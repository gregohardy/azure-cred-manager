import os
import json
import sys
import pdb

from pprint import pprint

def azure_login(agent):
    try:
        agent.shell("az account show")
        print("Azure CLI login verified")
    except Exception as e:
        print("It appears that you are not logged into the azure cli...")
        print("Please login to the azure cli : azure login")
        print("You will need to follow the instructions, then restart this script")
        sys.exit(2)

def azure_set_account(agent):
    accs = agent.shell("az account list")
    print(accs)
    accounts = json.loads(accs)
    sub_id = None
    while not sub_id:
        input_id = input("Please paste the Subscription ID you are using : ")
        for account in accounts:
            if input_id in account['id']:
                sub_id = input_id

    print("Using subscription [{0}]".format(sub_id))
    agent.shell("az account set -s {0}".format(sub_id))
    return sub_id


def azure_create_app(agent,
                     name,
                     homepage, # "https://test.com"
                     identifier, # "https://test.com"
                     password):

    agent.shell("az ad app create --display-name {0} --homepage {1} --identifier-uris {2} --password {3}".format(name,
                                                                                            homepage,
                                                                                            identifier,
                                                                                            password))

def config_get_app_list(agent):
    user_apps = {}
    creds = load_config(agent)
    for app, cred in creds.items():
        user_apps[app] = cred['AZURE_CLIENT_ID']

    return user_apps

def azure_get_account(agent):
    try:
        return json.loads(agent.shell("az account show"))
    except:
        return None

def azure_get_user(agent):
    account = azure_get_account(agent)
    return account['user']['name']

def azure_get_subscription_id(agent):
    account = azure_get_account(agent)
    if account:
        return account['id']
    
    return None

def get_azure_config_file_name(agent):
    account = azure_get_account(agent)
    if account:
        return "az.{0}_{1}.conf".format(account['user']['name'], account['name'])
    return None

def save_config(creds_dict, agent):
    path = "{0}/.azure/".format(os.getenv("HOME"))
    filename = get_azure_config_file_name(agent)

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError as e:
            raise Exception("Failed to create the directory [{0}] to save credentials."
                            " Please either move it or alter the permissions")

    with open(path+filename, 'w') as f:
        f.write(json.dumps(creds_dict))
        f.flush()

def load_config(agent):
    path = "{0}/.azure/".format(os.getenv("HOME"))
    filename = get_azure_config_file_name(agent)

    if filename is None or not os.path.isfile(path+filename):
        return {}

    with open(path+filename, 'r') as f:
        data = f.read()

    return json.loads(data)

def azure_get_user_name(agent):
    account = azure_get_account(agent)
    return account['user']['name']

def azure_show_service_principals(agent):
    sps = []
    apps = config_get_app_list(agent)
    for app_name, id in apps.items():
        sps.append(json.loads(agent.shell("az ad sp show --id {0}".format(id))))
    return sps

def azure_show_apps(agent):
    applications = []
    apps = config_get_app_list(agent)
    for app_name, id in apps.items():
        applications.append(json.loads(agent.shell("az ad app show --id {0}".format(id))))
    return applications

def azure_get_service_principals(agent):
    return json.loads(agent.shell("az ad sp list"))

def azure_get_apps(agent):
    return json.loads(agent.shell("az ad app list"))

def azure_get_role_assignment(agent, object_id):
    try:
        return json.loads(
            agent.shell("az role assignment list --assignee {0}".format(object_id)))[0]
    except:
        return None

def azure_get_application(agent, key, value):
    for app in azure_get_apps(agent):
        if value in app[key]:
            return app

    return None

def azure_get_service_principal(agent, key, value):
    for sp in azure_get_service_principals(agent):
        if value in sp[key]:
            return sp

    return None

def azure_create_service_principal(agent, name):
    app = azure_get_application(agent, 'displayName', name)
    agent.shell("az ad sp create --id {0}".format(app['appId']))
    return azure_get_service_principal(agent, 'displayName', name)

def azure_delete_service_principal(agent, sp_id):
    print(agent.shell('az ad sp delete --id {0}'.format(sp_id)))


def azure_create_role_assignment(agent, assignee):
    try:
        agent.shell("az role assignment create --assignee {0} --role Contributor".format(assignee))
        return azure_get_role_assignment(agent, assignee)
    except Exception as e:
        print("Role assignment failed! ", e)

def azure_delete_role_assignment(agent, assignee):
    agent.shell("az role assignment delete --assignee {0}".format(assignee))

def create_cred_elements(agent, app_name, app_hostname, subscription_id, password):
    app = azure_get_application(agent, 'displayName', app_name)
    if not app:
        print("Creating an application for [{0}]".format(app_name))
        azure_create_app(agent,
                         app_name,
                         "https://{0}.com".format(app_hostname),
                         "https://{0}.com".format(app_hostname),
                         password)
    else:
        print("App exists : {0}".format(app['displayName']))

    sp = azure_get_service_principal(agent, 'displayName', app_name)
    if not sp:
        print("Creating a service principal for [{0}]".format(app_name))
        sp = azure_create_service_principal(agent, app_name)
    else:
        print("Service Principal exists : {0}".format(sp['displayName']))

    role = azure_get_role_assignment(agent, sp['objectId'])
    if not role:
        print("Creating a role assignment for [{0}]".format(app_name))
        role = azure_create_role_assignment(agent, sp['objectId'])
        print("Created role [{0}] for application [{1}]".format(role['roleDefinitionName'], app_name))
    else:
        print("Role exists : {0}".format(role['roleDefinitionName']))

    if 'Contributor' not in role['roleDefinitionName']:
        sys.exit("Error: The service principal role is not set to contributor [{0}]".format(role['roleDefinitionName']))

    return get_arm_creds(agent, app_name, subscription_id, password)

def azure_show_cred_elements(agent, app_name):
    sp = azure_get_service_principal(agent, 'displayName', app_name)
    print("")
    pprint(sp, indent=2) if sp else print("No service principal for [{0}]".format(app_name))
    print("")
    if sp:
        role = azure_get_role_assignment(agent, sp['objectId'])
        pprint(role, indent=2) if role else print("No role assignment for [{0}]".format(app_name))
        print("")


def get_arm_creds(agent, app_name, subscription_id, password):
    sp = azure_get_service_principal(agent, 'displayName', app_name)

    return {
        app_name: {
            'AZURE_SUBSCRIPTION_ID': subscription_id,
            'AZURE_TENANT_ID': sp['additionalProperties']['appOwnerTenantId'],
            'AZURE_CLIENT_ID': sp['appId'],
            'AZURE_CLIENT_SECRET': password
        }
    }

def azure_delete_cred_elements(agent, app_name):
    sp = azure_get_service_principal(agent, 'displayName', app_name)
    if sp:
        role = azure_get_role_assignment(agent, sp['objectId'])
        if role:
            pdb.set_trace()
            print("Removing role assignment for [{0}]".format(sp['objectId']))
            azure_delete_role_assignment(agent, sp['objectId'], role['roleDefinitionName'])
        print("Removing service principal for [{0}]".format(sp['objectId']))
        azure_delete_service_principal(agent, sp['objectId'])
    else:
        app = azure_get_application(agent, 'displayName', app_name)
        if app:
            print("Removing application due to missing service principal for [{0}]".format(app_name))
            agent.shell("az ad app delete --objectId {0}".format(app['objectId']))

    creds = load_config(agent)
    try:
        del creds[app_name]
        print("Deleting application [{0}] credentials".format(app_name))
        save_config(creds,agent)
    except KeyError as e:
        print("Application [{0}] has already been removed from your credentials".format(app_name))
