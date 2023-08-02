from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, DateTime
import xmltodict

Base = declarative_base()

class Dice(Base):
    __tablename__ = 'Dice'

    DiceID = Column(Integer, primary_key=True)
    UUID = Column(String)
    Name = Column(String)
    Faces = Column(Integer)

class DiceFace(Base):
    __tablename__ = 'DiceFace'

    DiceFaceID = Column(Integer, primary_key=True)
    Dice = Column(Integer)
    FaceNumber = Column(Integer)

class TaskType(Base):
    __tablename__ = 'TaskType'

    TaskTypeID = Column(Integer, primary_key=True)
    Name = Column(String)

class Tasks(Base):
    __tablename__ = 'Tasks'

    TaskID = Column(Integer, primary_key=True)
    TaskType = Column(Integer)
    Organisation = Column(Integer)
    Name = Column(String)    

class Organisation(Base):
    __tablename__ = 'Organisation'

    OrganisationID = Column(Integer, primary_key=True)
    Name = Column(String)

class User(Base):
    __tablename__ = 'User'

    UserID = Column(Integer, primary_key=True)
    Organisation = Column(Integer)
    Name = Column(String)

class UserDice(Base):
    __tablename__ = 'UserDice'

    UserDiceID = Column(Integer, primary_key=True)
    User = Column(Integer)
    Dice = Column(Integer)

class DiceFaceTask(Base):
    __tablename__ = 'DiceFaceTask'

    DiceFaceTaskID = Column(Integer, primary_key=True)
    DiceFace = Column(Integer)
    Task = Column(Integer)

class APIKey(Base):
    __tablename__ = 'APIKey'

    APIKEYID = Column(Integer, primary_key=True)
    APIKEY = Column(String)
    USER = Column(Integer)

"""
    Given an XML recording, convert to object
"""
class DiceRecording():
    deviceUID = None
    deviceRecordingID = None
    diceFace = None
    startTime = None
    endTime = None

    def __init__(self, xmlRecording):
        try:
            jsonRecording = xmltodict.parse(xmlRecording)['root'] # XML to JSON
        except Exception as e:
            print("failed to parse XML Recording: %r" % e)
            return

        # Assign elements to object
        self.deviceUID = jsonRecording['deviceUID']
        self.deviceRecordingID = jsonRecording['recordingID']
        self.diceFace = jsonRecording['face']

        if "start" in jsonRecording:
            self.starttime = jsonRecording['start']

        if "end" in jsonRecording:
            self.endtime = jsonRecording['end']

"""
    Class: Recording
    Record the start/end time for a task recording
"""
class Recording(Base):
    __tablename__ = 'Recording'

    recordingid = Column(Integer, primary_key=True)
    dice = Column(Integer)
    task = Column(Integer)
    user = Column(Integer)
    starttime = Column(DateTime)
    endtime = Column(DateTime)

    def __init__(self, dice:Dice, task:Tasks, user:User, diceRecording:DiceRecording):

        self.dice = dice.DiceID
        self.task = task.TaskID
        self.user = user.UserID
        self.starttime = diceRecording.starttime
        self.endtime = diceRecording.endtime
    
    def __repr__(self):
        return "<Recording(dice='{}', task='{}', User={}, starttime={}, endtime={})>"\
                .format(self.dice, self.task, self.user, self.starttime, self.endtime)