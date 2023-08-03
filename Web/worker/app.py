from config import *
from models import *
from consumer import Consumer
from web import *

from pprint import PrettyPrinter
from multiprocessing import Process

## Note: sqlalchemy is installed by running "pip install psycopg2-binary"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

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

"""
Callback for incoming MQ messages
"""
def mq_callback(ch, method, properties, body):
    print(" Received a message!")

    # Convert XML Message into Dice Recording object
    try:
        diceRecording = DiceRecording(body.decode()) 
    except Exception as e:
        print("Failed to parse XML message! %r" % e)
        return

    # Handle Recording    
    with session_scope() as sesh:

        # Get Dice ID from Dice UID
        dice:Dice = sesh.query(Dice).filter_by(UUID = diceRecording.deviceUID).first()
        if (dice == None):
            print("Dice could not be found!")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        print("Dice: %r" % dice) # We have a dice match!

        # Get Dice Face
        diceFace:DiceFace = sesh.query(DiceFace).filter_by(Dice = dice.DiceID, FaceNumber = diceRecording.diceFace).first()
        if (diceFace == None):
            print("Dice Face could not be found!")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        print("Dice Face: %r" % diceFace) # We have a dice face match!

        # Get task assigned to this face
        diceFaceTask:DiceFaceTask = sesh.query(DiceFaceTask).filter_by(DiceFace = diceFace.DiceFaceID).first()
        if (diceFaceTask == None):
            print("No task assigned to this face")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        task:Tasks = sesh.query(Tasks).filter_by(TaskID = diceFaceTask.Task).first()
        if (task == None):
            print("Task assigned but could not be found")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        print("Task Found! %r" % task)

        # Get User
        userDice:UserDice = sesh.query(UserDice).filter_by(Dice = dice.DiceID).first()
        if (userDice == None):
            print("No user assigned to dice")
            user:User = None
        else:
            user:User = sesh.query(User).filter_by(UserID = userDice.User).first()

        # Create our recording entry
        recording = Recording(dice, task, user, diceRecording)
        pp.pprint(recording)
        sesh.add(recording)

        # All Done, Ack the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

class WebServer():
    def run(self):
        webapp.run(debug=WEB_DEBUG, host='0.0.0.0', port=WEB_PORT)

if __name__ == "__main__":
    recreate_database()

    subscriber_list = []
    subscriber_list.append(WebServer())
    subscriber_list.append(Consumer(mq_callback))

    # execute
    process_list = []
    for sub in subscriber_list:
        process = Process(target=sub.run)
        process.start()
        process_list.append(process)

    # wait for finish
    for process in process_list:
        process.join()