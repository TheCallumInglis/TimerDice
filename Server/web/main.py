# pylint: disable=broad-exception-caught, unused-argument, missing-module-docstring, missing-function-docstring, wildcard-import, unused-wildcard-import
import json
from types import SimpleNamespace
from pprint import PrettyPrinter

## Note: sqlalchemy is installed by running "pip install psycopg2-binary"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from config import *
from models import *
from flask import Flask, render_template, request, Response

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
@app.route('/')
def index():
    return render_template('index.html', tasks=get_efforts(), dicetasks=get_dice_face_tasks())

@app.route('/api/recording', methods=['GET', 'POST'])
def api_recording():
    """ API Method: Start/End or Get a recording"""
    if request.method == 'GET':
        return 'Get recording'

    elif request.method == 'POST' and request.mimetype == 'application/json':
        dice_recording:DiceRecording = json.loads(request.json, object_hook=lambda d: SimpleNamespace(**d))
        return create_recording(dice_recording)

    else:
        return Response(405) # Not Allowed
# Web Routes End

# Controller Start
def get_efforts():
    efforts = []

    with session_scope() as db:
        efforts = db.query(vw_taskspend).all()
        for effort in efforts:
            effort.spend_time_pretty()
        db.close()

    return efforts

def get_dice_face_tasks():
    dft = []

    with session_scope() as db:
        dft = db.query(vw_assignedtasks).filter(vw_assignedtasks.taskid.isnot(None)).order_by(vw_assignedtasks.diceid)
        db.close()

    return dft
        

def create_recording(dice_recording:DiceRecording):
    """ Create A Dice Recording, consume dice_recording"""
    with session_scope() as db:
        # TODO Replace With View!

        # Get Dice
        dice:Dice = db.query(Dice).filter_by(uuid = dice_recording.device_uuid).first()
        if (dice is None):
            return Response("Dice could not be found", 404)
        
        # Get Dice Face
        face:DiceFace = db.query(DiceFace).filter_by(dice = dice.diceid, facenumber = dice_recording.dice_face).first()
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
        user_dice:UserDice = db.query(UserDice).filter_by(dice = dice.diceid).first()
        if (user_dice is None):
            user:User = None
        else:
            user:User = db.query(User).filter_by(userid = user_dice.user).first()

        # Create our recording entry
        try:
            recording = Recording(dice, task, user, dice_recording)
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