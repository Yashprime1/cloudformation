#!/usr/bin/python3

#################################  Configuration ##################################
import subprocess
subprocess.call("apt-get update", shell=True)
subprocess.call("apt-get install python3-pip", shell=True)
subprocess.call("pip3 install boto3", shell=True)
subprocess.call("pip3 install python-dotenv", shell=True)
subprocess.call("pip3 install prettytable", shell=True)

import json
import sys
import boto3
from botocore.config import Config
import check_stack_exists 
import create_stack_changeset
import os 
from dotenv import load_dotenv
load_dotenv()

mu_config = Config(
    region_name = 'ap-south-1',
    retries = dict(
        max_attempts = 100
    )
)
sl_config = Config(
    region_name = 'ap-northeast-2',
    retries = dict(
        max_attempts = 100
    )
)
ir_config = Config(
    region_name = 'eu-west-1',
    retries = dict(
        max_attempts = 100
    )
)


mu_client = boto3.client('cloudformation',
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"] ,
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    config=mu_config)

sl_client = boto3.client('cloudformation',
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"] ,
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    config=sl_config)   

ir_client = boto3.client('cloudformation',
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"] ,
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    config=ir_config)        
# #################################  Configuration ##################################



# #############################  Code to get stack's changeset #####################
def findIfAnyChanges(changeset_ids):
    for changesetid in changeset_ids:
        if changesetid["ChangeSetStatus"]=="AVAILABLE":
            global changeset_present
            changeset_present = True

def deploymentStatus(stackName,client):
    response = client.describe_stacks(
        StackName=stackName,
    )
    return response["Stacks"][0]["StackStatus"]


if sys.argv[1].lower() == 'true':
    regions = json.load(open(os.getcwd()+"/prod.manifest.json", "r", encoding="utf-8"))
    print("########################### Changeset for stacks #######################")
    stacks_regionwise_create,stacks_regionwise_update=check_stack_exists.getStacksThatExist(regions)
    with open(os.getcwd()+'/scripts/stacks_changeset.json') as f:
        changeset_ids = json.load(f)
else:
    regions = json.load(open(os.getcwd()+"/prod.manifest.json", "r", encoding="utf-8"))
    print("########################### Changeset for stacks #######################")
    stacks_regionwise_create,stacks_regionwise_update=check_stack_exists.getStacksThatExist(regions)
    changeset_ids=[]
    changeset_ids.extend(create_stack_changeset.getStackChangeSet(stacks_regionwise_create,"CREATE"))
    changeset_ids.extend(create_stack_changeset.getStackChangeSet(stacks_regionwise_update,"UPDATE"))
    

changeset_present = False 
findIfAnyChanges((changeset_ids))

def deployChanges(changeset_ids):
    for changesetid in changeset_ids:
        if changesetid["StackRegion"]=="ap-south-1":
            client = mu_client
        elif changesetid["StackRegion"]=="eu-west-1":
            client = ir_client
        else:
            client = sl_client
        
        if changesetid["ChangeSetStatus"]=="AVAILABLE":
            print("########################### Deploying Chnages for stacks #######################")
            print("Deploying Stack : "+changesetid["StackName"])
            try:
                response = client.execute_change_set(
                    ChangeSetName=changesetid["ChangeSetId"],
                    DisableRollback=False
                )
            except Exception as e:
                print("ERROR : "+str(e))
                print(changesetid["StackName"]+ " could not be deployed")
            finally:
                print("Deploying in progress for stack : "+changesetid["StackName"])
                while(True):
                    status=deploymentStatus(changesetid["StackName"],client)
                    if 'COMPLETE'in status:
                        print("Deploying completed for stack : "+changesetid["StackName"]+" successfully with status : " + status)
                        break
                    if 'FAILED'in status:
                        print("Deploying completed for stack : "+changesetid["StackName"]+" but did not succeed with status : "+status)
                        break
                    


if sys.argv[1].lower() == 'true':
    print("Deploying")
    deployChanges((changeset_ids))
else:
    with open(os.getcwd()+'/scripts/stacks_changeset.json', "w") as final:
        json.dump(changeset_ids, final)

if not changeset_present:
    print("No change sets on any stack")
#############################  Code to check stack's presence #####################