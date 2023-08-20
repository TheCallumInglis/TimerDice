from datetime import timedelta, datetime
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, UUID, Integer, String, DateTime, Double, PrimaryKeyConstraint, Interval
from sqlalchemy_serializer import SerializerMixin

Base = declarative_base()

class DiceRecording():
    device_uuid = None
    device_recording_id = None
    dice_face = None
    starttime = None
    endtime = None

class CustomSerializerMixin(SerializerMixin):
    serialize_types = (
        (UUID, lambda x: String),
    )

class Dice(Base, CustomSerializerMixin):
    __tablename__ = 'dice'

    serialize_only = ('diceid', 'uuid', 'name', 'faces')

    diceid = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    faces = Column(Integer, nullable=False)

    def __init__(self, uuid, name, faces):
        self.uuid = uuid
        self.name = name
        self.faces = faces

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class DiceFace(Base, CustomSerializerMixin):
    __tablename__ = 'diceface'

    dicefaceid = Column(Integer, primary_key=True)
    dice = Column(Integer)
    facenumber = Column(Integer)

    def __init__(self, dice:Dice, facenumber:int):
        self.dice = dice.diceid
        self.facenumber = facenumber

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class TaskType(Base, CustomSerializerMixin):
    __tablename__ = 'tasktype'

    tasktypeid = Column(Integer, primary_key=True)
    name = Column(String)
    jsonconfig = Column(String)

    def __init__(self, name, config = None):
        self.name = name
        if config is not None:
            self.jsonconfig = json.dumps(json.loads(config)) 

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)
    
    def get_redacted(self):
        redacted_dict = self.to_dict()
        del redacted_dict['jsonconfig'] # Remove jsonconfig as this may contain API keys
        redacted_dict['hasexternalconfig'] = self.jsonconfig != None and len(self.jsonconfig) > 0 
        return redacted_dict

class Tasks(Base, CustomSerializerMixin):
    __tablename__ = 'tasks'

    taskid = Column(Integer, primary_key=True)
    tasktype = Column(Integer)
    organisation = Column(Integer)
    name = Column(String)
    external_task_id = Column(String)

    def __init__(self, tasktype:int, organisation: int, name:String, external_task_id:String = None):
        self.tasktype = tasktype
        self.organisation = organisation
        self.name = name
        self.external_task_id = external_task_id

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class Organisation(Base, CustomSerializerMixin):
    __tablename__ = 'organisation'

    organisationid = Column(Integer, primary_key=True)
    name = Column(String)

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class User(Base, CustomSerializerMixin):
    __tablename__ = 'user'

    userid = Column(Integer, primary_key=True)
    organisation = Column(Integer)
    name = Column(String)

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class UserDice(Base, CustomSerializerMixin):
    __tablename__ = 'userdice'

    userdiceid = Column(Integer, primary_key=True)
    user = Column(Integer)
    dice = Column(Integer)

    def __init__(self, user_id:int, dice:Dice):
        self.user = user_id
        self.dice = dice.diceid

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class DiceFaceTask(Base, CustomSerializerMixin):
    __tablename__ = 'dicefacetask'

    dicefacetaskid = Column(Integer, primary_key=True)
    diceface = Column(Integer)
    task = Column(Integer)

    def __init__(self, diceface:DiceFace, task:Tasks):
        self.diceface = diceface.dicefaceid
        self.task = task.taskid

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class Integration(Base, CustomSerializerMixin):
    __tablename__ = 'integration'

    integrationid = Column(Integer, primary_key=True)
    integration = Column(String)
    presetjson = Column(String)

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class APIKey(Base, CustomSerializerMixin):
    __tablename__ = 'apikey'

    apikeyid = Column(Integer, primary_key=True)
    apikey = Column(String)
    user = Column(Integer)

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class Recording(Base, CustomSerializerMixin):
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

    def getDurationInHours(self) -> float:
        strptime_format = '%Y-%m-%dT%H:%M:%S'
        duration = (datetime.strptime(self.endtime, strptime_format) - 
                    datetime.strptime(self.starttime, strptime_format)) / timedelta(hours=1)
        return duration
    
    def __repr__(self):
        return "<Recording(dice='{}', task='{}', User={}, starttime={}, endtime={})>"\
                .format(self.dice, self.task, self.user, self.starttime, self.endtime)
    
    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class vw_taskspend(Base, CustomSerializerMixin):
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

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class vw_assignedtasks(Base, CustomSerializerMixin):
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

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)

class vw_tasks(Base, CustomSerializerMixin):
    __tablename__ ='vw_tasks'

    taskid = Column(Integer, primary_key=True, unique=True)
    taskname = Column(String)
    tasktypeid = Column(Integer)
    tasktype = Column(String)
    external_task_id = Column(String)
    organisationid = Column(Integer)
    organisation = Column(String)

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)
    
class vw_taskspendreport(Base, CustomSerializerMixin):
    __tablename__ = 'vw_taskspendreport'

    recordingid = Column(Integer, primary_key=True)
    starttime = Column(DateTime)
    endtime = Column(DateTime)

    diceid = Column(Integer)
    diceuuid = Column(String)
    dicename = Column(String)

    taskid = Column(Integer)
    taskname = Column(String)

    tasktypeid = Column(Integer)
    tasktype = Column(String)

    userid = Column(Integer)
    username = Column(String)

    spend = Column(Double)
    spendtime = Column(String)

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, sort_keys=True)