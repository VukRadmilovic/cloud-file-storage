import json
import boto3

def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    
    # Check if user exists and password is correct
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('najbolja-tabela-ikada')
    response = table.get_item(Key={'username': username})
    
    if 'Item' not in response:
        raise Exception("Bad request: user with this username does not exist.")
    
    if response['Item']['password'] != password:
        raise Exception("Bad request: incorrect password")
    
    return "Successful login"
