import json
import os
import requests
from pprint import PrettyPrinter

from models import Tasks, Recording, ExternalTaskConfig
from ExternalTask import ExternalTask

pp = PrettyPrinter(indent=4)

# https://docs.gitlab.com/ee/api/
class GitLab(ExternalTask):
    _timeout = 10
    _api_version = "v4"

    def __init__(self, instance_domain, project, pat):
        self.api_auth = {'PRIVATE-TOKEN' : pat}
        self.api_url = f"https://{instance_domain}/api/{self._api_version}/projects/{project}"

    def GetWorkItem(self, work_item_id):
        request = requests.get(
            f"{self.api_url}/issues/{work_item_id}",
            headers=self.api_auth,
            timeout=self._timeout,
        )

        if request.status_code != 200:
            print(f"Failed to fetch Gitlab Issue... {request.status_code}")
            return None
        
        return request.json()
    
    def AddTimeSpent(self, work_item_id, spend, summary = None):
        """Add time spent to an issue
        @param spend Spend time in hours
        @param summary Text summary of effort
        @returns Issue
        """
        request = requests.post(
            f"{self.api_url}/issues/{work_item_id}/add_spent_time?duration={spend}h&summary={summary}",
            headers=self.api_auth,
            timeout=self._timeout,
        )

        if request.status_code != 201:
            print(f"Failed to add effort spend to GitLab Issue... {request.status_code} \n{request.url}")
            return None
        
        return request.json()

    def UpdateEffort(self, task: Tasks, recording: Recording):
        if task.external_task_id is None:
            return # TODO Raise Exception
        
        # Get Item, make sure it exists, but do we really need to?
        work_item = self.GetWorkItem(task.external_task_id)

        if (work_item is None):
            raise Exception("Work Item Not Found") # TODO Be Specific
        
        # Add Effort
        issue = self.AddTimeSpent(task.external_task_id, recording.getDuration("hours"), "Timer Dice Effort")
        return issue
    
    def GetExternalTasks(self) -> list[ExternalTaskConfig]:
        request = requests.get(
            f"{self.api_url}/issues",
            headers=self.api_auth,
            timeout=self._timeout,
        )

        if request.status_code != 200:
            print(f"Failed to fetch Gitlab Issues... {request.status_code}")
            return None
        
        response = request.json()

        tasks = []
        for task in response:
            tasks.append(ExternalTaskConfig(task['iid'], task['title']))

        return json.dumps([obj.__dict__ for obj in tasks])

    def SampleJsonConfig(self):
        return '{"type":"GitLab","config":{"instance_domain":"","project":"","api_PAT":""}}'
