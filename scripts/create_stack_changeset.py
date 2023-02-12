#!/usr/bin/python3

#################################  Configuration ##################################
import subprocess
subprocess.call("pip3 install boto3", shell=True)
subprocess.call("pip3 install python-dotenv", shell=True)
subprocess.call("pip3 install prettytable", shell=True)

import json
import boto3
from random import randint
from botocore.config import Config
from prettytable import PrettyTable
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
#################################  Configuration ##################################



#############################  Code to get stack's changeset #####################

def getStackChangeSet(stacks_regionwise,type):
    changesetids = []
    for region,stacks in stacks_regionwise.items():
        if region=="ap-south-1":
            client = mu_client
        elif region=="eu-west-1":
            client = ir_client
        else:
            client = sl_client
        for stack in stacks:
            name = stack["stackname"]
            path = stack["template"]
            parameters =  stack["parameters"]
            parameters.append({})
            parameters = parameters[:-1]
            print(os.getcwd()+"/"+path)
            with open(os.getcwd()+"/"+path) as template_file:
                template_data = json.load(template_file)
            changeset = client.create_change_set(
                StackName=name,
                TemplateBody=json.dumps(template_data),
                Parameters=parameters,
                ChangeSetType=type,
                ChangeSetName=name+str(randint(0, 1000000)),
            )
            table = PrettyTable(["Action","Logical ID","Resource Type","Replacement"])
            if changeset["Id"]:
                while True:
                    chnagesdescribed = client.describe_change_set(
                        ChangeSetName=changeset["Id"]
                    )
                    if chnagesdescribed["Status"]=="CREATE_COMPLETE" and chnagesdescribed["ExecutionStatus"]=="AVAILABLE":
                        break
                    if chnagesdescribed["ExecutionStatus"]=="OBSOLETE" or chnagesdescribed["Status"]=="FAILED":
                        break
    
                changesetids.append({"StackName":name,"ChangeSetId":changeset["Id"],"ChangeSetStatus":chnagesdescribed["ExecutionStatus"],"StackRegion":region})
                for change in (chnagesdescribed["Changes"]):
                    change = change["ResourceChange"]
                    if "Replacement" in change:
                        table.add_row([change["Action"],change["LogicalResourceId"],change["ResourceType"],change["Replacement"]])
                    else:
                        table.add_row([change["Action"],change["LogicalResourceId"],change["ResourceType"],""])
                if len(chnagesdescribed["Changes"])!=0:
                    print("**************************"+name+"******************************")
                    print(table)
    return changesetids
                        

#############################  Code to check stack's presence #####################