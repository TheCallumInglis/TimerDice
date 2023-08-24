import json
import os
import requests

from models import Tasks, Recording, ExternalTaskConfig
from ExternalTask import ExternalTask

# https://learn.microsoft.com/en-us/rest/api/azure/devops/
class AzureDevops(ExternalTask):
    _timeout = 10

    def __init__(self, organisation, project, pat, api_version, effort_units) -> None:
        self.organisation = organisation
        self.project = project

        self.api_auth = ('', pat)
        self.api_version = api_version
        self.api_url = f"https://dev.azure.com/{self.organisation}/{self.project}/_apis"
        self.effort_units = effort_units

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
            print(f"Error Updating Work Item {request.status_code}")
            return None

        return request.json()
    
    def add_comment(self, work_item_id, comment):
        # https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/comments/add-work-item-comment?view=azure-devops-rest-7.1&tabs=HTTP
        request = requests.post(
            f"{self.api_url}/wit/workitems/{work_item_id}/comments?format=markdown&api-version={self.api_version}",
            data = json.dumps({ "text" : comment}),
            headers={"Content-Type" : "application/json"},
            auth=self.api_auth,
            timeout=self._timeout
        )

        if request.status_code != 200:
            print(f"Error Adding Comment to Work Item! \nURL: {request.url} \nStatus Code: {request.status_code} \nData: {request.request.body} \nResponse: {request.text}")
            return None

        return request.json()
    
    def UpdateEffort(self, task: Tasks, recording: Recording):
        if task.external_task_id is None:
            return # TODO Raise Exception
        
        work_item = self.get_work_item(task.external_task_id)

        if (work_item is None):
            raise Exception("Work Item Not Found") # TODO Be Specific
        
        # Current Effort
        if "Microsoft.VSTS.Scheduling.Effort" not in work_item["fields"]:
            current_effort = 0
        else:
            current_effort = work_item['fields']['Microsoft.VSTS.Scheduling.Effort']

        # Effort to add
        effort_to_add = recording.getDuration(self.effort_units)

        logs = []
        logs.append( "# :game_die: Timer Dice Effort Report :game_die:")
        logs.append(f"Item: {work_item['fields']['System.Title']}")
        logs.append( " ")
        logs.append( "## Before Changes")
        logs.append(f"Current Effort: `{current_effort} {self.effort_units}`")
        logs.append(f"Effort To Add: `{effort_to_add} {self.effort_units}`")
        logs.append( " ")
        logs.append( "## Effort Information")
        logs.append(f"Start Time: `{recording.starttime}`")
        logs.append(f"End Time: `{recording.endtime}`")
        logs.append(f"Duration: `{recording.getDelta()}`")

        field_updates = [
            AzureDevops.WorkItemFieldUpdate(
                "add", 
                "Microsoft.VSTS.Scheduling.Effort", 
                current_effort + effort_to_add
            )
        ]

        # Push Through Update
        updated_item = self.update_work_item(task.external_task_id, field_updates)
        logs.append( " ")
        logs.append( "## Update Information")
        logs.append(f"New Effort: `{updated_item['fields']['Microsoft.VSTS.Scheduling.Effort']} {self.effort_units}`")

        print ("\n===========================")
        print('  \r\n'.join(logs)) # Temp
        print ("===========================\n")

        # Add comment to ask
        self.add_comment(task.external_task_id, '\r\n'.join(logs))
        
        return updated_item
    
    def GetExternalTasks(self) -> list[ExternalTaskConfig]:
        tasks = []
        return json.dumps([obj.__dict__ for obj in tasks])
    
    def GetExternalTaskByID(self, task_id) -> ExternalTaskConfig:
        work_item = self.get_work_item(task_id)

        if (work_item is None):
            return None
        
        return ExternalTaskConfig(work_item['id'], work_item['fields']['System.Title'])

    def SampleJsonConfig(self):
        return '{ "type" : "AzureDevOps", "config" : { "organisation" : "", "project" : "", "api_version" : "7.1-preview", "api_PAT" : "", "effort_units" : "hours"}}'

    class WorkItemFieldUpdate():
        """Ref https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/update?view=azure-devops-rest-7.0&tabs=HTTP#jsonpatchdocument"""

        def __init__(self, op, field, value):
            self.op = op
            self.path = f"/fields/{field}"
            self.value = value
