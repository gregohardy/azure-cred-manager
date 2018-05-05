# azure-cred-manager
A tool to manage your subscription through the Azure CLI.

Its not rocket science, but I found the whole process of finding out your creds when you
created an application as mildy terrible in Azure. Having to discover your tennant id through 
the URI of the console was unpleasant (I know this will/has changed)

This tool enables you to track and create these for your account. Hopefully its simple and easy to use.

It tracks and manages your Applications and Service Principals, and makes creating and 
maintaining them simple. Its easy to lose track of what your currently SP struture looks like.
You can remove old or unused SP's.

At present it is setup in the install step to use brew, ergo its OSX at present for the install
step, but if you dont mind installing the Azure CLI, this tool is for you on any linux that supports
the Azure CLI and python3.

## Installation

```
virtualenv .
source bin/activate
pip3 install -r requirements.txt
```

## Usage

    ```
    ./manageAzure.py

    This will display the basic help :

    usage: manage (sub-commands ...) [options ...] {arguments ...}

    Build and manage your Microsoft Azure credentials

    commands:

      create
        Create Azure Application/Service Principal and add a role for this subscription

      delete
        Delete Azure Application/Service Principal and add a role for this subscription

      list
        List azure elements [sp|app]

      login
        Set the Azure Subscription to use and login to the Azure CLI

      show
        Show current credentials

    optional arguments:
      -h, --help            show this help message and exit
      --debug               toggle debug output
      --quiet               suppress all output
      -n APP_NAME, --name APP_NAME
                            the name of the Azure application to create
      -p PASSWORD, --password PASSWORD
                            the client secret or password for the application to
                            create
      -b BASENAME, --basename BASENAME
                            the basename for the URI and identifier for the app to
                            create
    ```
## First Steps

### Authenticate through the Azure CLI

    ```
    ./manageAzure.py login
    ```

This step will show you how to login to the Azure CLI. You will have to open a browser and confirm with the code
that is displayed in this step. This is Azure specific and not part of this module. You should only have to log
in once. Thankfully.

### Creating a Service Principal

This will generate a set of credentials you can use for this application/ServicePrincipal with the ARM SDK through the Azure CLI.

    ```
    ./manageAzure.py create -n app name -b sp base name -p password for the application
    ```

Example :

    ```
    ./manageAzure.py create -n testapp1 -b testapp -p 4321mypass!
    Creating an application for [testapplication1]
    Creating a service principal for [testapplication1]
    Creating a role assignment for [testapplication1]
    Created role [Contributor] for application [testapplication1]
    Now saving the credentials
    ```

The password is for the application, NOT your azure login. DO NOT use that. The passwords are not protected.

### Show credentials

To show your credentials, listed by application name for use with the Azure SDK :

    ```
    ./manageAzure.py show
    ```

Example:

    ```
    ./manageAzure.py show
    INFO: Show your current credentials

    Your current Azure Credentials:
    APP :  basegregapp
    export AZURE_SUBSCRIPTION_ID=xxxx
    export AZURE_TENANT_ID=xxxx
    export AZURE_CLIENT_ID=xxxx
    export AZURE_CLIENT_SECRET=xxxx
    ```

### Deleting

To delete an Application/ServicePrincipal/Role.

    ```
    ./manageAzure.py delete -n <application name>
    ```

Example:

    ```
    ./manageAzure.py delete -n testapplication1
    INFO: Deleting creds for this subscription
    Removing role assignment for [d23cf3eb-a5d2-4627-ab2a-94aaa17cbc8d]
    Removing service principal for [d23cf3eb-a5d2-4627-ab2a-94aaa17cbc8d]
    info:    Executing command ad sp delete
    info:    Deleting service principal d23cf3eb-a5d2-4627-ab2a-94aaa17cbc8d
    info:    ad sp delete command OK

    Deleting application [testapplication1] credentials
    ```

### List Service Principals/Applications

The manager can show you your current Application or Service Principals for the current user, or display
all of the elements for this subscri:

    ```
    ./manageAzure.py list
    usage: manage (sub-commands ...) [options ...] {arguments ...}

    List azure elements [sp|app]

    commands:

      apps
        Show applications

      sps
        Show service principals

    optional arguments:
      -h, --help  show this help message and exit
      --debug     toggle debug output
      --quiet     suppress all output
      --all       show all
    ```

Example:

    ```
    ./manageAzure.py list sps -all
    ```

Displays all Service Principals for this subscription.

    ```
    ./manageAzure.py list sps
    ```

Displays only this User's Service principals
