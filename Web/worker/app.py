from config import DATABASE_URI
from models import Base, Dice, DiceFace, TaskType, Tasks, Organisation, User, UserDice, DiceFaceTask, DiceRecording, Recording, APIKey
from consumer import Consumer

import pprint

## Note: sqlalchemy is installed by running "pip install psycopg2-binary"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

pp = pprint.PrettyPrinter(indent=4)
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

        # TODO Get User
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


    # recording = Recording(body.decode())
    # pp.pprint(recording)

    # with session_scope() as sesh:
    #     try:
    #         sesh.add(recording)
    #         ch.basic_ack(delivery_tag=method.delivery_tag)

    #     except Exception as e:
    #         print('that didnt work %r' % (e))



if __name__ == "__main__":
    recreate_database()

    consumer = Consumer(mq_callback)
    