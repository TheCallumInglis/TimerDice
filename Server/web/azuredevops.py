import json
import os
import requests

from models import Tasks, Recording
from ExternalTask import ExternalTask

# https://learn.microsoft.com/en-us/rest/api/azure/devops/
class AzureDevops(ExternalTask):
    _timeout = 10

    def __init__(self, organisation, project, pat, api_version) -> None:
        self.organisation = organisation
        self.project = project

        self.api_auth = ('', pat)
        self.api_version = api_version
        self.api_url = f"https://dev.azure.com/{self.organisation}/{self.project}/_apis"

    def get_work_item(self, work_item_id):
        request = requests.get(
            f"{self.api_url}/wit/workitems/{work_item_id}?api-version={self.api_version}", 
            auth=self.api_auth,
            timeout=self._timeout
        )

        if request.status_code != 200:
            print(f"He's dead jim... {request.status_code}")
            return None

        return request.json()
    
    def update_work_item(self, work_item_id, updates):
        request = requests.patch(
            f"{self.api_url}/wit/workitems/{work_item_id}?api-version={self.api_version}",
            json.dumps([ob.__dict__ for ob in updates]),
            headers={"Content-Type" : "application/json-patch+json"},
            auth=self.api_auth,
            timeout=self._timeout
        )

        if request.status_code != 200:
            print(f"He's dead jim... {request.status_code}")
            return None

        return request.json()
    
    def UpdateEffort(self, task: Tasks, recording: Recording):
        if task.external_task_id is None:
            return # TODO Raise Exception
        
        work_item = self.get_work_item(task.external_task_id)

        if (work_item is None):
            raise Exception("Work Item Not Found") # TODO Be Specific
        
        if "Microsoft.VSTS.Scheduling.Effort" not in work_item["fields"]:
            current_effort = 0
        else:
            current_effort = work_item['fields']['Microsoft.VSTS.Scheduling.Effort']

        print(f"Item: {work_item['fields']['System.Title']}")
        print(f"Current Effort: {current_effort} (hrs)")

        print(f"Effort To Add {recording.getDurationInHours()}")

        field_updates = [
            AzureDevops.WorkItemFieldUpdate(
                "add", 
                "Microsoft.VSTS.Scheduling.Effort", 
                current_effort + recording.getDurationInHours()
            )
        ]

        updated_item = self.update_work_item(task.external_task_id, field_updates)
        print(f"Updated Effort: {updated_item['fields']['Microsoft.VSTS.Scheduling.Effort']} (hrs)")
        
        return updated_item
    
    def SampleJsonConfig(self):
        return '{ "type" : "AzureDevOps", "config" : { "organisation" : "", "project" : "", "api_version" : "7.0", "api_PAT" : ""}}'

    class WorkItemFieldUpdate():
        """Ref https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/update?view=azure-devops-rest-7.0&tabs=HTTP#jsonpatchdocument"""

        def __init__(self, op, field, value):
            self.op = op
            self.path = f"/fields/{field}"
            self.value = value
