from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Double, PrimaryKeyConstraint
from datetime import timedelta

Base = declarative_base()

class DiceRecording():
    device_uuid = None
    device_recording_id = None
    dice_face = None
    starttime = None
    endtime = None

class Dice(Base):
    __tablename__ = 'dice'

    diceid = Column(Integer, primary_key=True)
    uuid = Column(String)
    name = Column(String)
    faces = Column(Integer)

class DiceFace(Base):
    __tablename__ = 'diceface'

    dicefaceid = Column(Integer, primary_key=True)
    dice = Column(Integer)
    facenumber = Column(Integer)

class TaskType(Base):
    __tablename__ = 'tasktype'

    tasktypeid = Column(Integer, primary_key=True)
    name = Column(String)

class Tasks(Base):
    __tablename__ = 'tasks'

    taskid = Column(Integer, primary_key=True)
    tasktype = Column(Integer)
    organisation = Column(Integer)
    name = Column(String)    

class Organisation(Base):
    __tablename__ = 'organisation'

    organisationid = Column(Integer, primary_key=True)
    name = Column(String)

class User(Base):
    __tablename__ = 'user'

    userid = Column(Integer, primary_key=True)
    organisation = Column(Integer)
    name = Column(String)

class UserDice(Base):
    __tablename__ = 'userdice'

    userdiceid = Column(Integer, primary_key=True)
    user = Column(Integer)
    dice = Column(Integer)

class DiceFaceTask(Base):
    __tablename__ = 'dicefacetask'

    dicefacetaskid = Column(Integer, primary_key=True)
    diceface = Column(Integer)
    task = Column(Integer)

class APIKey(Base):
    __tablename__ = 'apikey'

    apikeyid = Column(Integer, primary_key=True)
    apikey = Column(String)
    user = Column(Integer)

class Recording(Base):
    __tablename__ = 'recording'

    recordingid = Column(Integer, primary_key=True)
    dice = Column(Integer)
    task = Column(Integer)
    user = Column(Integer)
    starttime = Column(DateTime)
    endtime = Column(DateTime)

    def __init__(self, dice:Dice, task:Tasks, user:User, diceRecording:DiceRecording):

        self.dice = dice.diceid
        self.task = task.taskid
        self.user = user.userid
        self.starttime = diceRecording.starttime
        self.endtime = diceRecording.endtime
    
    def __repr__(self):
        return "<Recording(dice='{}', task='{}', User={}, starttime={}, endtime={})>"\
                .format(self.dice, self.task, self.user, self.starttime, self.endtime)

class vw_taskspend(Base):
    __tablename__ = 'vw_taskspend'

    taskid = Column(Integer, primary_key=True)
    tasktype = Column(String)
    organisation = Column(String)
    name = Column(String)
    spend = Column(Double)
    spendtime = None

    def spend_time_pretty(self):
        if (self.spend is None): 
            return
            
        self.spendtime = str(timedelta(seconds=self.spend))

class vw_assignedtasks(Base):
    __tablename__ = 'vw_assignedtasks'
    __table_args__ = (
        PrimaryKeyConstraint('diceid', 'dicefaceid'),
    )

    userdiceid = Column(Integer)
    diceid = Column(Integer)
    uuid = Column(String)
    name = Column(String)
    faces = Column(Integer)
    userid = Column(Integer)
    username = Column(String)
    organisationid = Column(Integer)
    organisation = Column(String)
    dicefaceid = Column(Integer)
    facenumber = Column(Integer)
    taskid = Column(Integer)
    taskname = Column(String)
    tasktype = Column(String)
