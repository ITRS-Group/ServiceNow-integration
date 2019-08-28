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
"\n\tExample for resolving an incident in ServiceNow:\n\n" + \
"\t\t" + sys.argv[0] + " -r \"UniqueID\"\n" + \
"\n\tExample for a new incident in ServiceNow: \n\n" + \
"\t\t" + sys.argv[0] + " -n \"UniqueID\"\n")

# Arg Parser https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option https://docs.python.org/2/howto/argparse.html
parser = argparse.ArgumentParser( description=Usage_Msg , formatter_class=RawTextHelpFormatter)

# Software -> Category
# Internal Application -> SubCatergory
# Azure -> Configuration # ATTRIBUTE
# Grab KBA

# Typical operations for ServiceNow states
parser.add_argument( "-n", "--new", help = "Incident is logged but not yet triaged.",  action="store_true")
parser.add_argument( "-r", "--resolve", help = "Resolves targeted Incident",  action="store_true")
parser.add_argument( "-c", "--close", help = "Closes targeted Incident",  action="store_true")
parser.add_argument( "-u", "--update", help = "Update incident data",  action="store_true")
parser.add_argument( "-q", "--query", help = "Query Incident.",  action="store_true")
parser.add_argument( "-act", "--action", help = "Incident is not yet triaged.",  action="store_true")

# parser.add_argument( "-c", "--close", help = "Close an incident.",  action="store_true")
parser.add_argument( "-inp", "--in-progress", help = "Incident is assigned and is being investigated.",  action="store_true")
parser.add_argument( "-oh", "--on-hold", help = "Put incident on-hold.",  action="store_true")
parser.add_argument( "-nt", "--notes", help = "Notes to apply to the Incident ticket",  type=str)
parser.add_argument( "-im", "--impact", help = "Impact the Incident ticket",  type=int)
parser.add_argument( "-ur", "--urgency", help = "Urgency of the Incident ticket",  type=int)

# querying tickets by unique identifier
parser.add_argument( "-si", "--SysId", help = "Notes to apply to the Incident ticket",  type=str)
parser.add_argument( "-tn", "--TicketNum", help = "Notes to apply to the Incident ticket",  type=str)

# assign
parser.add_argument( "-ato", "--assign", help = "Assign the Incident ticket to someone",  type=str)
parser.add_argument( "-cby", "--created", help = "Incident ticket's creator or the user reasonable for",  type=str)

# Whether or not to run it as a command, and what data you like to pass through
parser.add_argument( "-cmd", "--command", help = "Run the integration as a command (instead of on an action)", action="store_true")
parser.add_argument( "-gw", "--gateway", help = "Name of the Gateway",  type=str)
parser.add_argument( "-np", "--netprobe", help = "Name of the NetProbe",  type=str)
parser.add_argument( "-me", "--entity", help = "Name of the Managed Entity",  type=str)
parser.add_argument( "-spr", "--sampler", help = "Name of the Sampler",  type=str)
parser.add_argument( "-dv", "--dataview", help = "Name of the Dataview",  type=str)
parser.add_argument( "-rn", "--rowname", help = "RowName of the targeted cell",  type=str)
parser.add_argument( "-col", "--column", help = "ColumnName of the targeted cell",  type=str)
parser.add_argument( "-val", "--value", help = "Value of the targeted cell",  type=str)

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

def Query_Incident():

    # Set the payload
    Find_Incident = {}

    # Ticket Number
    if (args.TicketNum):
        Find_Incident["number"] = (args.TicketNum)
    else:
        print("Sys Id or Ticket Number is needed.")

    Get_Ticket = Inc_Res.get(query=Find_Incident).one()

    print("==== Incident JSON Start ====")
    print(json.dumps(Get_Ticket, indent=2))
    print("==== Incident JSON End ====")
    #
    # for key in res_rec.keys():
    #     print(key + "," + res_rec[key])
    print("==== End Of Script ====")

def Command_Create_Incident():

    # Create empty json Payload
    Geneos_Payload = {}

    # Create placeholder
    # Row information
    Column = ""
    RowName = ""
    Value = ""

    # ===== Other Feature
    KBA = ""
    ATTRIBUTE_A = ""
    ATTRIBUTE_B = ""
    ATTRIBUTE_C = ""

    print("==== Building Payloads and Message ====")
    Geneos_info = ""
    if (args.gateway):
        Geneos_info += "Gateway = " + (args.gateway) + "\n"
    if (args.netprobe):
        Geneos_info += "Probe = " + (args.netprobe) + "\n"
    if (args.entity):
        Geneos_info += "Entity = " + (args.entity) + "\n"
    if (args.sampler):
        Geneos_info += "Sampler = " + (args.sampler) + "\n"
    if (args.dataview):
        Geneos_info += "Dataview = " + (args.dataview) + "\n"
    if (args.rowname):
        Geneos_info += "Rowname = " + (args.rowname) + "\n"
        RowName = (args.rowname)
    if (args.column):
        Geneos_info += "Column = " + (args.column) + "\n"
        Column = (args.column)
    ######################################################
    if (args.value):
        Geneos_info += "Value = " + (args.value) + "\n"
        Value = (args.value)
    if (args.notes):
        NOTES=(args.notes)
        # Geneos_Payload["notes"] = (args.notes)
    print("==== START Geneos Payload ====")
    print("Geneos Information: " + "\n" + Geneos_info  )
    print("==== END Geneos Payload ====")

    # Set the payload
    New_Incident = {
        "short_description" : "Change created by Geneos " + Column + " is " + Value + " on " + RowName + ".",
        "category" : "Software", # Because we're a software company.
        "subcategory" : "Operating System",
        "description" : Geneos_info + "\n\n" + NOTES,
        "comments" : NOTES,
        "location" : "Americas",
        "assigned_to" : "",
        "assignment_group" : "Software",
        "cmdb_ci": "GCP"
         # "cmdb_ci": {11
         #  "value": "AZURE"
         #  }
         #    # "Gateway = " +
            # "u_dataset_item" : My_XPath
    }

    if (args.urgency):
            # URGENCY=(args.urgency)
            New_Incident["urgency"] = (args.urgency)
    if (args.impact):
            # IMPACT=(args.impact)
            New_Incident["impact"] = (args.impact)


    print("==== START Incident Payload for ServiceNow ====")

    # print(json.dumps(New_Incident, indent=2))

    print("==== END Incident Payload for ServiceNow ====")

    result = Inc_Res.create(payload=New_Incident)
    
    print("==== Response ====")
    # print(result)
    res_rec = result.one()
    ticket_n = res_rec['number']
    print("==== Incident Result JSON ====")
    # print(json.dumps(res_rec, indent=2))
    #
    # for key in res_rec.keys():
    #     print(key + "," + res_rec[key])
    
    # Mark ticket opener as caller
    opened_by_id = res_rec['opened_by']['value']
    update = {'caller_id': opened_by_id}
    Inc_Res.update(query={'number': ticket_n}, payload=update)
    
    print("==== End Of Script ====")

def Command_Update_Incident():

    # Create empty json Payload
    Geneos_Payload = {}
    Find_Incident = {}

    # Create placeholder
    # Row information
    Column = ""
    RowName = ""
    Value = ""

    # ===== Other Feature
    KBA = ""
    ATTRIBUTE_A = ""
    ATTRIBUTE_B = ""
    ATTRIBUTE_C = ""

    # Ticket Number
    if (args.TicketNum):
        Find_Incident["number"] = (args.TicketNum)
    else:
        print("Sys Id or Ticket Number is needed.")

    print("==== Building Payloads and Message ====")
    Geneos_info = ""
    if (args.gateway):
        Geneos_info += "Gateway = " + (args.gateway) + ".\n"
    if (args.netprobe):
        Geneos_info += "Probe = " + (args.netprobe) + ".\n"
    if (args.entity):
        Geneos_info += "Entity = " + (args.entity) + ".\n"
    if (args.sampler):
        Geneos_info += "Sampler = " + (args.sampler) + ".\n"
    if (args.dataview):
        Geneos_info += "Dataview = " + (args.dataview) + ".\n"
    if (args.rowname):
        Geneos_info += "Rowname = " + (args.rowname) + ".\n"
        RowName = (args.rowname)
    if (args.column):
        Geneos_info += "Column = " + (args.column) + ".\n"
        Column = (args.column)
    ######################################################
    if (args.value):
        Geneos_info += "Value = " + (args.value) + ".\n"
        Value = (args.value)
    if (args.notes):
        NOTES=(args.notes)
        # Geneos_Payload["notes"] = (args.notes)



    print("==== START Geneos Payload ====")

    print(" Geneos Information: " + "\n" + Geneos_info  )

    print("==== END Geneos Payload ====")

    print("==== START Query Payload ====")

    print(json.dumps(Geneos_Payload, indent=2))

    print("==== END Query Payload ====")

    # Set the payload
    # Set the payload
    New_Incident = {
        "short_description" : "Change updated by Geneos " + Column + " is " + Value + " on " + RowName + ".",
        "category" : "Software", # Because we're a software company.
        "subcategory" : "Operating System",
        "description" : Geneos_info + "\n\n" + NOTES,
        "comments" : NOTES,
        "location" : "Americas",
        "assigned_to" : "",
        "assignment_group" : "Software"
            # "Gateway = " +
            # "u_dataset_item" : My_XPath
    }

    if (args.urgency):
        # URGENCY=(args.urgency)
        New_Incident["urgency"] = (args.urgency)

    if (args.impact):
        # IMPACT=(args.impact)
        New_Incident["impact"] = (args.impact)

    print("==== START Incident Payload for ServiceNow ====")

    print(json.dumps(New_Incident, indent=2))

    print("==== END Incident Payload for ServiceNow ====")

    # result = Inc_Res.create(payload=New_Incident)
    result = Inc_Res.update(query=Find_Incident, payload=New_Incident)

    print("==== Response ====")
    print(result)
    res_rec = result.one()
    print("==== Incident Result JSON ====")
    print(json.dumps(res_rec, indent=2))
    #
    # for key in res_rec.keys():
    #     print(key + "," + res_rec[key])

    print("==== End Of Script ====")

def Command_Close_Incident():
    desired_state = 3
    if args.TicketNum != None:
        ticket_n = args.TicketNum
    else:
        print("Ticket Number not supplied. Exiting.")
        sys.exit(1)
        
    try:
        update = {'state': desired_state}
        updated_record = Inc_Res.update(query={'number': ticket_n}, payload=update)
        updated_state = int(updated_record.one()['state'])
        if desired_state != updated_state:
            print("Completed but failed changing ticket state to desired value.")
        else:
            print("Ticket %s marked Closed." % ticket_n)
    except pysnow.exceptions.NoResults:
        print("Failed to find incident with ref: %s" % ticket_n)
    
def Command_Resolve_Incident():
    desired_state = 6
    if args.TicketNum != None:
        ticket_n = args.TicketNum
    else:
        print("Ticket Number not supplied. Exiting.")
        sys.exit(1)
        
    try:
        update = {'state': desired_state}
        updated_record = Inc_Res.update(query={'number': ticket_n}, payload=update)
        updated_state = int(updated_record.one()['state'])
        if desired_state != updated_state:
            print("Completed but failed changing ticket state to desired value.")
        else:
            print("Ticket %s marked Resolved." % ticket_n)
    except pysnow.exceptions.NoResults:
        print("Failed to find incident with ref: %s" % ticket_n)
    
     
    
def Action_Create_Update_Incident():

    GATEWAY=EnvData["_GATEWAY"]
    PROBE=EnvData["_PROBE"]
    MANAGED_ENTITY=EnvData["_MANAGED_ENTITY"]
    SAMPLER=EnvData["_SAMPLER"]
    TYPE=EnvData["_TYPE"]
    DATAVIEW=EnvData["_DATAVIEW"]
    ROWNAME=EnvData["_ROWNAME"]
    COLUMN=EnvData["_COLUMN"]
    # VALUE=EnvData["_VALUE"]

    My_XPath = GATEWAY + "\\" + \
        PROBE + "\\" + \
        MANAGED_ENTITY + "\\" + \
        SAMPLER + "\\" + \
        TYPE + "\\" + \
        DATAVIEW + "\\" + \
        ROWNAME + "\\" + \
        COLUMN

        #description for the ticket created from the variables
        #description="
        #Alert details:\n
        #Gateway: ${gateway}\n
        #Probe: ${probe}\n
        #Managed Entity: ${me}\n
        #Sampler: ${sampler}\n
        #Row: ${rowname}\n
        #Column: ${column}\n
        #Value: ${value}\n
        #Notes: ${notes} # this should be another user input

    # Query for incidents with state 1
    response = Inc_Res.get(query={'u_dataset_item': My_XPath })

    # Iterate over the result and print out `sys_id` of the matching records.
    for record in response.all():
        print(json.dumps(record, indent=2))

            # If it's one record and you're confident
            # print(json.dumps(response.one_or_none(), indent=2))

            # Set the payload
    New_Incident = {
        "short_description" : "Geneos Gateway: " + EnvData["_GATEWAY"] + " created Incident",
        "description" : "Geneos Integration Test: " + EnvData["_GATEWAY"]
            # "u_dataset_item" : My_XPath
    }

    # Create a new incident record
    result = Inc_Res.create(payload=New_Incident)
    print("==== End Of Script ====")

if __name__ == '__main__':
    print("==== Begin Of Script ====")
    # if not (args.command):
    #     Action_Create_Update_Incident()
    # else:
    # Command_Create_Incident()
    #
    if args.new:
        Command_Create_Incident()
    elif args.update:
        Command_Update_Incident()
    elif args.resolve:
        Command_Resolve_Incident()
    elif args.close:
        Command_Close_Incident()
    elif args.query:
        Query_Incident()
    else:
        print("Unsuported Options")
