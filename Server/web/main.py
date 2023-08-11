# pylint: disable=broad-exception-caught, unused-argument, missing-module-docstring, missing-function-docstring, wildcard-import, unused-wildcard-import
from datetime import datetime
import json
from types import SimpleNamespace
from pprint import PrettyPrinter

## Note: sqlalchemy is installed by running "pip install psycopg2-binary"
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import *
from models import *
from flask import Flask, render_template, request, Response, make_response

app = Flask(__name__)
pp = PrettyPrinter(indent=4)
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def recreate_database():
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

# Web Routes Start
@app.context_processor
def inject_now():
    return {'year': datetime.utcnow().year}

@app.route('/')
def index():
    return render_template('index.html', tasks=get_efforts(), dicetasks=get_dice_face_tasks())

@app.route('/dice')
def dice():
    return render_template('dice.html', dice=get_dice())

@app.route('/tasks')
def tasks():
    return render_template('tasks.html', tasks=get_tasks(), tasktypes=get_tasktypes())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/dice', methods=['GET', 'POST'])
@app.route('/api/dice/<dice_id>', methods=['GET'])
def api_dice(dice_id = None):
    """ API Method: Create or Get a Dice"""
    if request.method == 'GET':
        if dice_id is None:
            js_list = []
            for dice in get_dice():
                js_list.append(dice.to_dict())

            return make_response({ "dice" : js_list })

        else:
            # Return specific dice by its ID
            with session_scope() as db:
                this_dice = db.query(Dice).filter(Dice.diceid == dice_id).first()

                dice_faces = []
                for face in db.query(vw_assignedtasks).filter(
                        vw_assignedtasks.diceid == dice_id
                    ).order_by(vw_assignedtasks.facenumber).all():
                    dice_faces.append(face.to_dict())

                db.close()
                return make_response({ "dice" : this_dice.to_dict(), "faces" : dice_faces })

    elif request.method == 'POST' and request.mimetype == 'multipart/form-data':
        # TODO Error Handling
        new_dice = Dice(request.form['dice-uuid'], request.form['nickname'], request.form['faces'])

        try:
            with session_scope() as db:
                # Check dice does not already exist
                if db.query(Dice).filter(Dice.uuid == new_dice.uuid).count() > 0:
                    return Response('Duplicate UUID', 409)
                
                # Create New Dice
                db.add(new_dice)
                new_dice:Dice = db.query(Dice).filter(Dice.uuid == new_dice.uuid).first()

                # Create Dice Faces
                for facenumber in range(0, int(new_dice.faces)):
                    new_face:DiceFace = DiceFace(new_dice, facenumber + 1)
                    db.add(new_face)

                # Assign Dice to Default User
                user_dice:UserDice = UserDice(1, new_dice)
                db.add(user_dice)

                return Response(new_dice.to_json(), 200)

        except Exception as exception:
            print("Hit Exception: %r" % exception)
            return Response('Server Error', 503)
    
    return Response(405) # Not Allowed

@app.route('/api/tasks/available/<dice_id>', methods=['GET'])
def api_tasks_available(dice_id = None):
    if dice_id is None:
        return Response(400)
    
    # Get Tasks not arleady assigned to this dice
    with session_scope() as db:
        assigned_tasks = db.query(vw_assignedtasks.taskid).filter(
            vw_assignedtasks.diceid == dice_id,
            vw_assignedtasks.taskid.is_not(None)
        ).all()

        _tasks = []
        for task in db.query(Tasks).filter(Tasks.taskid.not_in([i[0] for i in assigned_tasks])).all():
            _tasks.append(task.to_dict())

        return make_response({ "tasks" : _tasks })

@app.route('/api/tasks', methods=['GET'])
def api_tasks():
    if request.method == 'GET':
        js_list = []
        for _tasks in get_tasks():
            js_list.append(_tasks.to_dict())

        return make_response({ "tasks" : js_list })
    
    return Response("Method Not Allowed", 405)

@app.route('/api/tasks/assign', methods=['POST'])
def api_tasks_assign():
    """ API Method: Assign Task To Dice Face"""
    pp.pprint(request)

    if request.method == 'POST' and request.mimetype == 'multipart/form-data':
        diceface:DiceFace = get_dice_face(request.form['diceid'], request.form['facenumber'])
        task:Tasks = get_task(request.form['taskid'])

        if diceface is None:
            return Response('Dice Face Not Found', 404)
        
        if task is None:
            return Response('Task Not Found', 404)

        #try:
        with session_scope() as db:
            # TODO Check this task isn't assigned to another face on this dice
            # return Response('Duplicate Task Assignment', 409)

            # Check there isn't a task assigned to this face already
            dicefacecheck = db.query(DiceFaceTask).filter(DiceFaceTask.diceface == diceface.dicefaceid)
            if dicefacecheck.count() > 0:
                for dfc in dicefacecheck.all(): # Remove existing assignment
                    db.delete(dfc)

            # Create Assignment   
            assignment = DiceFaceTask(diceface, task)             
            db.add(assignment)

            return Response(assignment.to_json(), 200)

        # except Exception as exception:
        #     print("Hit Exception: %r" % exception)
        #     return Response('Server Error', 503)

@app.route('/api/tasks/add', methods=['POST'])
def api_tasks_add():
    if request.method == 'POST' and request.mimetype == 'multipart/form-data':
        # TODO Error Handling
        new_task = Tasks(request.form['addTaskType'], request.form['addTaskOrganisation'], request.form['addTaskName'])

        try:
            with session_scope() as db:
                # Check Task does not already exist
                if db.query(Tasks).filter(Tasks.name == new_task.name, Tasks.organisation == new_task.organisation).count() > 0:
                    return Response('Duplicate Task within Organisation', 409)
                
                # Create New Task
                db.add(new_task)
                new_task:Tasks = db.query(Tasks).filter(
                    Tasks.name == new_task.name, 
                    Tasks.organisation == new_task.organisation, 
                    Tasks.tasktype == new_task.tasktype
                ).first()

                return Response(new_task.to_json(), 200)

        except Exception as exception:
            print("Hit Exception: %r" % exception)
            return Response('Server Error', 503)
    
    return Response(405) # Not Allowed

@app.route('/api/tasks/spend/<task_id>', methods=['GET'])
def api_tasks_spend(task_id):
    if task_id is None:
        return Response(400)
    
    with session_scope() as db:
        task_spend_report = db.query(vw_taskspendreport).filter(
                vw_taskspendreport.taskid == task_id
            ).order_by(
                vw_taskspendreport.starttime
            ).all()

        report = []
        for recording in task_spend_report:
            report.append(recording.to_dict())

        return make_response({
            "task_spend_report" : report, 
            "task" : get_task(task_id).to_dict()
        })

@app.route('/api/tasktypes', methods=['GET'])
def api_tasktypes():
    if request.method == 'GET':
        js_list = []
        for tasktype in get_tasktypes():
            js_list.append(tasktype.to_dict())

        return make_response({ "tasktypes" : js_list })

    return Response("Method Not Allowed", 405)

@app.route('/api/tasktypes/add', methods=['POST'])
def api_tasktypes_add():
    if request.method == 'POST' and request.mimetype == 'multipart/form-data':
        # TODO Error Handling
        new_task_type = TaskType(request.form['addTaskTypeName'])

        try:
            with session_scope() as db:
                # Check Task Type does not already exist
                if db.query(TaskType).filter(TaskType.name == new_task_type.name).count() > 0:
                    return Response('Duplicate Task Type', 409)
                
                # Create New Task Type
                db.add(new_task_type)
                new_task_type:TaskType = db.query(TaskType).filter(TaskType.name == new_task_type.name).first()

                return Response(new_task_type.to_json(), 200)

        except Exception as exception:
            print("Hit Exception: %r" % exception)
            return Response('Server Error', 503)
    
    return Response(405) # Not Allowed

@app.route('/api/organisation', methods=['GET'])
def api_organisation():
    if request.method == 'GET':
        js_list = []
        for organisations in get_organisations():
            js_list.append(organisations.to_dict())

        return make_response({ "organisation" : js_list })

    return Response("Method Not Allowed", 405)

@app.route('/api/recording', methods=['GET', 'POST'])
def api_recording():
    """ API Method: Start/End or Get a recording"""
    if request.method == 'GET':
        return 'Get recording'

    elif request.method == 'POST' and request.mimetype == 'application/json':
        dice_recording:DiceRecording = json.loads(request.json, object_hook=lambda d: SimpleNamespace(**d))
        return create_recording(dice_recording)

    return Response(405) # Not Allowed
# Web Routes End

# Controller Start
def get_dice():
    with session_scope() as db:
        _dice = db.query(Dice).order_by(Dice.uuid).all()
        db.close()
        return _dice

def get_tasks():
    with session_scope() as db:
        _tasks = db.query(vw_tasks).order_by(vw_tasks.taskname).all()
        db.close()
        return _tasks

def get_tasktypes():
    with session_scope() as db:
        tasktypes = db.query(TaskType).order_by(TaskType.name).all()
        db.close()
        return tasktypes

def get_organisations():
    with session_scope() as db:
        organisations = db.query(Organisation).order_by(Organisation.name).all()
        db.close()
        return organisations

def get_efforts():
    with session_scope() as db:
        efforts = db.query(vw_taskspend).all()
        for effort in efforts:
            effort.spend_time_pretty()
        db.close()
        return efforts

def get_dice_face_tasks():
    with session_scope() as db:
        dft = db.query(vw_assignedtasks).filter(vw_assignedtasks.taskid.isnot(None)).order_by(vw_assignedtasks.diceid)
        db.close()
        return dft
    
def get_dice_face(dice_id, face_number):
    with session_scope() as db:
        df = db.query(DiceFace).filter(DiceFace.dice == dice_id, DiceFace.facenumber == face_number).first()
        db.close()
        return df
    
def get_task(task_id):
    with session_scope() as db:
        task = db.query(Tasks).filter(Tasks.taskid == task_id).first()
        db.close()
        return task
        
def create_recording(dice_recording:DiceRecording):
    """ Create A Dice Recording, consume dice_recording"""
    with session_scope() as db:
        # Get Dice
        _dice:Dice = db.query(Dice).filter_by(uuid = dice_recording.device_uuid).first()
        if (_dice is None):
            return Response("Dice could not be found", 404)
        
        # Get Dice Face
        face:DiceFace = db.query(DiceFace).filter_by(dice = _dice.diceid, facenumber = dice_recording.dice_face).first()
        if (face is None):
            return Response("Dice Face could not be found", 404)
        
        # Get task assigned to this face
        face_task:DiceFaceTask = db.query(DiceFaceTask).filter_by(diceface = face.dicefaceid).first()
        if (face_task is None):
            return Response("No Task Assigned To This Face", 404)
        
        task:Tasks = db.query(Tasks).filter_by(taskid = face_task.task).first()
        if (task is None):
            return Response("Task assigned but could not be found", 404)
        
        # Get User
        user_dice:UserDice = db.query(UserDice).filter_by(dice = _dice.diceid).first()
        if (user_dice is None):
            user:User = None
        else:
            user:User = db.query(User).filter_by(userid = user_dice.user).first()

        # Create our recording entry
        try:
            recording = Recording(_dice, task, user, dice_recording)
            db.add(recording)

        except Exception as ex:
            print(ex)
            return Response("Error during recording creation", 503)
        
        # All good!
        return Response(None, 200)

# Controller End

if __name__ == "__main__":
    #recreate_database()
    pass
