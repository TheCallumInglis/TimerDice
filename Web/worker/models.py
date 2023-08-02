from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, DateTime
import xmltodict

Base = declarative_base()

class Recording(Base):
    __tablename__ = 'Recording'

    recordingid = Column(Integer, primary_key=True)
    dice = Column(Integer)
    task = Column(Integer)
    User = Column(Integer)
    starttime = Column(DateTime)
    endtime = Column(DateTime)

    def __init__(self, xmlRecording):
        jsonRecording = xmltodict.parse(xmlRecording)['root'] # XML to JSON

        self.dice = 1 #jsonRecording['deviceUID']
        self.recordingid = jsonRecording['recordingID']
        self.face = jsonRecording['face']
        self.starttime = jsonRecording['start']
        self.endtime = jsonRecording['end']
    
    def __repr__(self):
        return "<Recording(dice='{}', task='{}', User={}, starttime={}, endtime={})>"\
                .format(self.dice, self.task, self.User, self.starttime, self.endtime)