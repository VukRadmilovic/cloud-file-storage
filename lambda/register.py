import json
import boto3
from http import HTTPStatus

def lambda_handler(event, context):
    name = event['name']
    surname = event['surname']
    birthdate = event['birthdate']
    username = event['username']
    email = event['email']
    password = event['password']
    
    # Check if the username is taken
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('najbolja-tabela-ikada')
    response = table.get_item(Key={'username': username})
    if 'Item' in response:
        raise Exception("Bad request: username already in use")
    
    # Create new user
    table.put_item(
        Item={
            'name': name,
            'surname': surname,
            'birthdate': birthdate,
            'username': username,
            'email': email,
            'password': password
        }
    )
    
    return "Successful registration!"