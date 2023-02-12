#!/usr/bin/python3
import sys
sys.path.append('/home/yashprime/.local/lib/python3.10/site-packages')
#################################  Configuration ##################################
import boto3
import os
from botocore.config import Config
from botocore.exceptions import ClientError
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



#############################  Code to check stack's presence #####################
def getStacksThatExist(regions):
    stacks_to_create = {}
    stacks_to_update = {}
    for region in regions:
        region_name = region["Region"]
        if region_name=="ap-south-1":
            client = mu_client
        elif region_name=="eu-west-1":
            client = ir_client
        else:
            client = sl_client
       
        stack_prefix = region["stackprefix"]
        stacks = region["Stacks"]
        stacks_to_create[region_name]=[]
        stacks_to_update[region_name]=[]
        
        # Check stack if exists / not 
        for stack in stacks:
            name = stack["stackname"]
            path = stack["template"]
            try:
                response = client.describe_stacks(
                    StackName=name
                )
                if response["Stacks"][0]["StackStatus"] ==  "REVIEW_IN_PROGRESS":
                    stackexists = False
                else:
                    stackexists =  True
            except ClientError:
                stackexists = False

            if (stackexists):
                stacks_to_update[region_name].append(stack)
            else:
                stacks_to_create[region_name].append(stack)
                print(name +  " stack does not exist (will be created)")

    return stacks_to_create,stacks_to_update
#############################  Code to check stack's presence #####################