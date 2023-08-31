from datetime import datetime
import json
import os
import requests
from requests.auth import HTTPBasicAuth
import time

from models import Tasks, Recording, ExternalTaskConfig
from ExternalTask import ExternalTask

# https://learn.microsoft.com/en-us/rest/api/azure/devops/
class Jira(ExternalTask):
    _timeout = 10
    _api_version = "3"

    def __init__(self, organisation, username, api_token) -> None:
        self.api_url = f"https://{organisation}.atlassian.net/rest/api/{self._api_version}"
        self.api_auth = HTTPBasicAuth(username, api_token)

    # Jira Format: "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
    def formatDate(self, date):
        return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').astimezone().strftime('%Y-%m-%dT%H:%M:%S.%f%z')

    def UpdateEffort(self, task: Tasks, recording: Recording):
        if task.external_task_id is None:
            return # TODO Raise Exception
        
        payload = json.dumps({
            "comment": {
                "content": [
                {
                    "content": [
                    {
                        "text": "Timer Dice Effort Tracking. Effort Duration: " + str(recording.getDuration('minutes')) + " minutes",
                        "type": "text"
                    }
                    ],
                    "type": "paragraph"
                }
                ],
                "type": "doc",
                "version": 1
            },
            "started": self.formatDate(recording.starttime),
            "timeSpentSeconds": max(recording.getDuration('seconds'), 60) # Jira expects at least 1 min of effort
        })
        
        request = requests.post(
            f"{self.api_url}/issue/{task.external_task_id}/worklog",
            data=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            auth=self.api_auth,
            timeout=self._timeout,
        )

        print(payload)
        print(f"{self.api_url}/issue/{task.external_task_id}/worklog")

        if request.status_code != 201:
            print(f"Failed to add effort spend to Jira Issue... {request.status_code} \n{request.url} \n{request.text}")
            return None
        
        return request.json()

    def GetExternalTasks(self) -> list[ExternalTaskConfig]:
        return []

    def GetExternalTaskByID(self, task_id) -> ExternalTaskConfig:
        return ExternalTaskConfig()

    def SampleJsonConfig(self):
        return json.dumps({
            "type" : "Jira",
            "config" : {
                "organisation" : "",
                "username" : "",
                "api_token" : ""
            }
        })
    