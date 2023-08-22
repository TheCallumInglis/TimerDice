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

from ExternalTask import ExternalTask
from AzureDevops import AzureDevops
from GitLab import GitLab

app = Flask(__name__)
pp = PrettyPrinter(indent=4)
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

# TODO  Assign colours to faces (Hex preferred)
# TODO  Record on-device recording ID in recording record.
#       Use this for for the dice to check if a recording has been sucesflly saved, and if so, delete local recording file
# TODO  Handle un-assigned task recordings
# TODO  Show "In Progress" Tasks
# TODO  Handle task recordings with no end date
# TODO  Allow manual recording of effort through API

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
    return render_template('tasks.html', tasks=get_tasks(), tasktypes=get_tasktypes(), integrations=get_integrations())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/dice', methods=['GET'])
def api_dice():
    js_list = []
    for dice in get_dice():
        js_list.append(dice.to_dict())

    return make_response({ "dice" : js_list })

@app.route('/api/dice/<dice_id>', methods=['GET'])
def api_dice_getbyid(dice_id):
    if dice_id is None:
        return Response("Expecting diceid, none given", 400)

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

@app.route('/api/dice', methods=['POST'])
def api_dice_add():
    if request.mimetype != 'multipart/form-data':
        return Response("Invalid Application-Type. Expecting 'multipart/form-data'.", 406)
    
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

@app.route('/api/tasks', methods=['POST'])
def api_tasks_add():
    if request.method == 'POST' and request.mimetype == 'multipart/form-data':
        # TODO Error Handling
        new_task = Tasks(
            request.form['addTaskType'], 
            request.form['addTaskOrganisation'], 
            request.form['addTaskName'], 
            (request.form['addTaskExternalID'] if 'addTaskExternalID' in request.form else None)
        )

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

@app.route('/api/tasks', methods=['DELETE'])
def api_tasks_delete():
    if request.mimetype != 'application/json':
        return Response("Invalid Application-Type. Expecting 'application/json'.", 406)
    
    content = request.json

    if "diceid" not in content or "facenumber" not in content:
        return Response("Bad Request. Expecting diceid and facenumber to be set.", 400)
    
    # Find Dice Face
    dice_face = get_dice_face(content["diceid"], content["facenumber"])
    if dice_face is None:
        return Response("Dice Face not found", 404)
    
    # Find Dice-Face Task Assignment
    dice_face_task:DiceFaceTask = get_dice_face_task(dice_face)
    if dice_face_task is None:
        return Response("No Task Assigned To Dice Face", 404)
    
    # Remove Dice Face Task Assignment
    try:
        with session_scope() as db:
            db.query(DiceFaceTask).filter(DiceFaceTask.dicefacetaskid == dice_face_task.dicefacetaskid).delete()
            db.commit()
            db.close()

            return Response("Task Removed", 200)
    
    except Exception as e:
        return Response("Failed to Delete Task Assignment", 500)

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

@app.route('/api/tasktypes/<tasktype_id>', methods=['GET'])
def api_tasktype(tasktype_id):
    return make_response({ "tasktype" : get_tasktype(tasktype_id).get_redacted() })

@app.route('/api/tasktypes/<tasktype_id>/extended', methods=['GET'])
def api_tasktype_extended(tasktype_id):
    return make_response({ "tasktype" : get_tasktype(tasktype_id).to_dict() })

@app.route('/api/tasktypes', methods=['GET'])
def api_tasktypes():
    if request.method == 'GET':
        js_list = []
        for tasktype in get_tasktypes():
            js_list.append(tasktype.to_dict())

        return make_response({ "tasktypes" : js_list })

    return Response("Method Not Allowed", 405)

@app.route('/api/tasktypes', methods=['POST'])
def api_tasktypes_add():
    if request.method == 'POST' and request.mimetype == 'multipart/form-data':
        # TODO Error Handling
        new_task_type = TaskType(
            request.form['addTaskTypeName'], 
            (request.form['addTaskTypeJsonConfig'] if 'addTaskTypeJsonConfig' in request.form and len(request.form['addTaskTypeJsonConfig']) > 0 else None)
        )

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

@app.route('/api/integrations/<integration_id>', methods=['GET'])
def api_integrations(integration_id):
    return make_response({ "integration" : get_integration(integration_id).to_dict() })

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

def get_integration(integration_id):
    with session_scope() as db:
        integation = db.query(Integration).filter(Integration.integrationid == integration_id).first()
        db.close()
        return integation

def get_integrations():
    with session_scope() as db:
        integrations = db.query(Integration).order_by(Integration.integration).all()
        db.close()
        return integrations

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

def get_dice_face_task(diceface:DiceFace) -> DiceFaceTask:
    with session_scope() as db:
        dft = db.query(DiceFaceTask).filter(DiceFaceTask.diceface == diceface.dicefaceid).first()
        db.close()
        return dft

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

def get_tasktype(tasktype_id):
    with session_scope() as db:
        tasktype = db.query(TaskType).filter(TaskType.tasktypeid == tasktype_id).first()
        db.close()
        return tasktype

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
        
        # Push through to external task handler
        try:
            external_task_handler(get_tasktype(task.tasktype), recording)

        except Exception as ex:
            print("Failed to push to external task handler: ")
            print(ex)
        
        # All good!
        return Response(None, 200)

def external_task_handler(tasktype:TaskType, recording:Recording):
    if tasktype.jsonconfig is None or tasktype.jsonconfig == "null":
        raise Exception("No Action for Task Type")
    
    json_config = json.loads(tasktype.jsonconfig)
    print(f"External Task Handler for type: {json_config['type']}")

    # Find External Task Handler
    match json_config["type"]:
        case "AzureDevOps":
            external_task:ExternalTask = AzureDevops(
                json_config['config']['organisation'],
                json_config['config']['project'],
                json_config['config']['api_PAT'],
                json_config['config']['api_version'],
                json_config['config']['effort_units']
            )

        case "GitLab":
            external_task:ExternalTask = GitLab(
                json_config['config']['instance_domain'],
                json_config['config']['project'],
                json_config['config']['api_PAT']
            )

        case _:
            print(f"External Task Handler Not Defined! Given: {json_config['type']}")
            return
    
    # Push Through an update
    external_task.UpdateEffort(get_task(recording.task), recording)
# Controller End

if __name__ == "__main__":
    #recreate_database()
    pass
