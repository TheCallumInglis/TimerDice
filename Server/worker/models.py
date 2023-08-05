import xmltodict

class DiceRecording:
    """Given an XML recording, convert to object"""
    device_uuid = None
    device_recording_id = None
    dice_face = None
    starttime = None
    endtime = None

    def __init__(self, xml_recording):
        obj = xmltodict.parse(xml_recording)['root'] # XML to JSON

        # Assign elements to object
        self.device_uuid = obj['deviceUID']
        self.device_recording_id = obj['recordingID']
        self.dice_face = obj['face']

        if "start" in obj:
            self.starttime = obj['start']

        if "end" in obj:
            self.endtime = obj['end']