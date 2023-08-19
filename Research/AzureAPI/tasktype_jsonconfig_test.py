import json

azure = {
    "type" : "AzureDevops",
    "config" : {
        "organisation" : "4oh4ltd",
        "project" : "sandbox",
        "api_version" : "7.0",
        "api_PAT" : "",
    }
}

print(json.dumps(azure))