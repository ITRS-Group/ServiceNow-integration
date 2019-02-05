import requests, base64, json, sys, argparse, os, time
import urllib3
import pysnow
from datetime import datetime
from argparse import RawTextHelpFormatter

#Uber ASCII Art
# For Supressing warnings
urllib3.disable_warnings()
Uber_Small_ASCII = (" - Geneos Integrations for ServiceNow - \n")

# Modify Environment variables
# https://docs.servicenow.com/bundle/london-it-service-management/page/product/incident-management/concept/c_IncidentManagementStateModel.html
Usage_Msg = ( Uber_Small_ASCII + \
"\n\tFor listing incidents of certain status from ServiceNow:\n\n" + \
"\t\t" + sys.argv[0] + " -s \"<status>\"\n")

# Arg Parser https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option https://docs.python.org/2/howto/argparse.html
parser = argparse.ArgumentParser( description=Usage_Msg , formatter_class=RawTextHelpFormatter)

# Typical operations for ServiceNow states
parser.add_argument( "-s", "--state", help = "List incidents by state.",  type=int)

# Operators for the state as well
parser.add_argument( "-so", "--over-state", help = "List incidents over a certain state.",  action="store_true")
parser.add_argument( "-su", "--under-state", help = "List incidents under a certain state.",  action="store_true")

# Other attributes
parser.add_argument( "-p", "--priority", help = "List incidents by a priority.",  type=int)
parser.add_argument( "-u", "--urgency", help = "List incidents by urgency.",  type=int)

# global args
args = parser.parse_args()

# Loads the environment variable as JSON structure
# We will use this later
Env_JSON = json.dumps(dict(**os.environ), sort_keys=True, indent=4)
EnvData = json.loads(Env_JSON)

# Some required settings
S_User = EnvData["SERVNOW_USER"]
S_Pass = EnvData["SERVNOW_PASS"]
S_Table = EnvData["SERVNOW_TABLE"]
S_Instance = EnvData["SERVNOW_INSTANCE"]
# S_Server = EnvData["SERVNOW_SERVER"]

# Setting the Proxy in script if necessary
if "https_proxy" in EnvData:

    # proxies
    ProxySess = requests.Session()
    ProxySess.proxies.update({'https' : EnvData["https_proxy"]})
    ProxySess.auth = requests.auth.HTTPBasicAuth(S_User, S_Pass)

    # Create ServiceNow client
    ServNow = pysnow.Client(instance=S_Instance, session=ProxySess)

elif "http_proxy" in EnvData:

    # proxies
    ProxySess = requests.Session()
    ProxySess.proxies.update({'http': EnvData["http_proxy"]})
    ProxySess.auth = requests.auth.HTTPBasicAuth(S_User, S_Pass)

    # Create ServiceNow client
    ServNow = pysnow.Client(instance=S_Instance, session=ProxySess)
else:
    ServNow = pysnow.Client(instance=S_Instance, user=S_User, password=S_Pass)

# API path for getting endpoints on resources
Inc_Res = ServNow.resource(api_path=S_Table)

def Query_incidents():

    # Grab current state
    if (args.state):
        Queried_Incidents = Inc_Res.get(query={'state' : (args.state) }).all()
    elif (args.priority):
        Queried_Incidents = Inc_Res.get(query={'priority' : (args.priority) }).all()
    elif (args.urgency):
        Queried_Incidents = Inc_Res.get(query={'urgency' : (args.urgency) }).all()
    else:
        Queried_Incidents = Inc_Res.get(query={'state' : 1 }).all()

    # Column Values
    print(
            "number," + \
            "sys_id," + \
            "priority," + \
            "urgency," + \
            "state," + \
            # "severity," + \
            "madeSLA," + \
            "sysCreatedBy," + \
            "sysCreatedOn," + \
            "sysUpdatedBy," + \
            "sysUpdateOn," + \
            "active," + \
            "shortDescription," + \
            "description," + \
            "location," + \
            "deliveryPlan," + \
            "sysTags," + \
            # "notify," + \
            # "childIncidents," + \
            "contactType" )

    for incident in Queried_Incidents:
        print(
            # json.dumps(incident, indent=2)
            # incident values
            incident["number"] + "," + \
            incident["sys_id"] + "," + \
            incident["priority"] + "," + \
            incident["urgency"] + "," + \
            incident["state"] + "," + \
            # incident["severity"] + "," + \
            incident["made_sla"] + "," + \
            incident["sys_created_by"] + "," + \
            incident["sys_created_on"] + "," + \
            incident["sys_updated_by"] + "," + \
            incident["sys_updated_on"] + "," + \
            incident["active"] + "," + \
            incident["short_description"].replace(",","\\,").replace("\n","") + "," + \
            incident["description"].replace(",","\\,").replace("\n","") + "," + \
            str(incident["location"]).replace(",","\\,").replace("\n","") + "," + \
            incident["delivery_plan"].replace(",","\\,").replace("\n","") + "," + \
            incident["sys_tags"].replace(",","\\,").replace("\n","") + "," + \
            # str(incident["notify"]) + "," + \
            # incident["child"] + "," + \
            incident["contact_type"]
            #incident.correlation_id,
            #incident.due_date,
            #incident.closed_by,
            #incident.close_notes,
            #incident.work_notes_list,
        )

def Query_changes():

    # Grab current state
    if (args.state):
        Queried_Incidents = Inc_Res.get(query={'state' : (args.state) }).all()
    elif (args.priority):
        Queried_Incidents = Inc_Res.get(query={'priority' : (args.priority) }).all()
    elif (args.urgency):
        Queried_Incidents = Inc_Res.get(query={'urgency' : (args.urgency) }).all()
    else:
        Queried_Incidents = Inc_Res.get(query={'state' : 1 }).all()

    # Column Values
    print(
            "number," + \
            "sys_id," + \
            "priority," + \
            "urgency," + \
            "state," + \
            "severity," + \
            "madeSLA," + \
            "sysCreatedBy," + \
            "sysCreatedOn," + \
            "sysUpdatedBy," + \
            "sysUpdateOn," + \
            "active," + \
            "shortDescription," + \
            "description," + \
            "location," + \
            "deliveryPlan," + \
            "sysTags," + \
            "notify," + \
            "childIncidents," + \
            "contactType" )

    for incident in Queried_Incidents:
        print(
            # json.dumps(incident, indent=2)
            # incident values
            incident["number"] + "," + \
            incident["sys_id"] + "," + \
            incident["priority"] + "," + \
            incident["urgency"] + "," + \
            incident["state"] + "," + \
            incident["severity"] + "," + \
            incident["made_sla"] + "," + \
            incident["sys_created_by"] + "," + \
            incident["sys_created_on"] + "," + \
            incident["sys_updated_by"] + "," + \
            incident["sys_updated_on"] + "," + \
            incident["active"] + "," + \
            incident["short_description"].replace(",","\\,").replace("\n","") + "," + \
            incident["description"].replace(",","\\,").replace("\n","") + "," + \
            str(incident["location"]).replace(",","\\,").replace("\n","") + "," + \
            incident["delivery_plan"].replace(",","\\,").replace("\n","") + "," + \
            incident["sys_tags"].replace(",","\\,").replace("\n","") + "," + \
            str(incident["notify"]) + "," + \
            incident["child_incidents"] + "," + \
            incident["contact_type"]
            #incident.correlation_id,
            #incident.due_date,
            #incident.closed_by,
            #incident.close_notes,
            #incident.work_notes_list,
        )

if __name__ == '__main__':
    # print("==== Begin Of Script ====")
    # if not (args.command):
    #     Action_Create_Update_Incident()
    # else:
    Query_incidents()
