import json
import os
import requests

# https://learn.microsoft.com/en-us/rest/api/azure/devops/
class AzureDevops():
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
            return False

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
            return False

        return request.json()

    class WorkItemFieldUpdate():
        """Ref https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/update?view=azure-devops-rest-7.0&tabs=HTTP#jsonpatchdocument"""

        def __init__(self, op, field, value):
            self.op = op
            self.path = f"/fields/{field}"
            self.value = value

# Get the show on the road
ORGANISATION = "4oh4ltd"
PROJECT = "Sandbox"
API_VER = "7.0"

# Get PAT
temp_pat = os.environ.get('AZURE_API_PAT')
if temp_pat is None:
    API_PAT = input("AZURE_API_PAT Not Set. Please Enter Your Personal Access Token Now: ")
else:
    API_PAT = temp_pat

devops = AzureDevops(ORGANISATION, PROJECT, API_PAT, API_VER)

# Get an item
work_item = devops.get_work_item(13)
current_effort = work_item['fields']['Microsoft.VSTS.Scheduling.Effort']

print(f"Item: {work_item['fields']['System.Title']}")
print(f"Current Effort: {current_effort} (hrs)")

# List of fields to update
field_updates = [
    AzureDevops.WorkItemFieldUpdate(
        "add", 
        "Microsoft.VSTS.Scheduling.Effort", 
        current_effort + 1 # + 1 hour to effort
    )
]
updated_item = devops.update_work_item(13, field_updates)
print(f"Updated Effort: {updated_item['fields']['Microsoft.VSTS.Scheduling.Effort']} (hrs)")
