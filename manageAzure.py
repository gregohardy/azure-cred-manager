#!/usr/local/bin/python3

from azure.credentials import azure_cli_installed, azure_login, azure_set_account, azure_get_apps
from azure.credentials import azure_get_subscription_id, save_config, load_config, azure_delete_cred_elements
from azure.credentials import create_cred_elements, azure_show_service_principals, azure_show_apps
from azure.credentials import azure_get_service_principals
from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from osagent.core import OSAgent
from pprint import pprint


class ListController(CementBaseController):
    class Meta:
        label = 'list'
        description = 'List azure elements [sp|app]'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--all'],  dict(action='store_true', help='show all')),
        ]

    @expose(hide=True, aliases=['help'])
    def default(self):
        self.app.args.print_help()

    @expose(help="Show service principals")
    def sps(self):
        if self.app.pargs.all:
            self.app.log.info("Show All Service Principals for the account")
            os_agent = OSAgent()
            pprint(azure_get_service_principals(os_agent), indent=4)
        else:
            self.app.log.info("Show Service Principals for this user")
            os_agent = OSAgent()
            pprint(azure_show_service_principals(os_agent), indent=4)

    @expose(help="Show applications")
    def apps(self):
        if self.app.pargs.all:
            self.app.log.info("Show All Applications for the Account")
            os_agent = OSAgent()
            pprint(azure_get_apps(os_agent), indent=4)
        else:
            self.app.log.info("Show Applications owned by this User")
            os_agent = OSAgent()
            pprint(azure_show_apps(os_agent), indent=4)


class AzureCredController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'Build and manage your Microsoft Azure credentials'
        arguments = [(['-n', '--name'], dict(action='store', dest='app_name',
                                             help='the name of the Azure application to create')),
                     (['-p', '--password'], dict(action='store', dest='password',
                                                 help='the client secret or password for the application to create ')),
                     (['-b', '--basename'], dict(action='store', dest='basename',
                                                 help='the basename for the URI and identifier for the app to create'))
        ]

    @expose(hide=True, aliases=['help'])
    def default(self):
        self.app.args.print_help()

    @expose(help="Show current credentials")
    def show(self):
        self.app.log.info("Show your current credentials")
        os_agent = OSAgent()
        creds = load_config(os_agent)
        if not creds:
            print("Creds have not been created for this subscription. Please run the create step")
        else:
            print("\nYour current Azure Credentials:")
            pprint(creds, indent=4)

    @expose(help="Create Azure Application/Service Principal and add a role for this subscription")
    def create(self):
        self.app.log.info("Creating creds for this subscription")
        os_agent = OSAgent()

        if not app.pargs.app_name or not app.pargs.password or not app.pargs.basename:
            print("-n|--app_name <name> -p|--password -b|basename are mandatory for a create")
        else:
            creds = create_cred_elements(os_agent,
                                         app.pargs.app_name,
                                         app.pargs.basename,
                                         azure_get_subscription_id(os_agent),
                                         app.pargs.password)
            print("Now saving the credentials")
            orig = load_config(os_agent)
            creds.update(orig)
            save_config(creds, os_agent)

    @expose(help="Delete Azure Application/Service Principal and add a role for this subscription")
    def delete(self):
        self.app.log.info("Deleting creds for this subscription")
        os_agent = OSAgent()

        if not app.pargs.app_name:
            print("-n|--app_name <name> must be specified for delete")
        else:
            azure_delete_cred_elements(os_agent, app.pargs.app_name)

    @expose(help="Install or Update the Azure CLI")
    def install(self):
        self.app.log.info("Installing the azure CLI")
        os_agent = OSAgent()
        azure_cli_installed(os_agent)

    @expose(help="Set the Azure Subscription to use and login to the Azure CLI")
    def login(self):
        os_agent = OSAgent()
        self.app.log.info("Verify the User has logged into the Azure CLI")
        azure_login(os_agent)
        self.app.log.info("Setting the Azure Subscription ID")
        subscription_id = azure_set_account(os_agent)


class AzureManagementApp(CementApp):
    class Meta:
        label = 'manage'
        base_controller = AzureCredController
        extensions = ['colorlog']
        log_handler = 'colorlog'
        handlers = [
            AzureCredController,
            ListController,
        ]

with AzureManagementApp() as app:
    app.run()
