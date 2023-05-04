import boto3
import uuid

def generate_session_id():
    """Generates a unique session ID."""
    return str(uuid.uuid4())

def store_session_info(session_id, username):
    """Stores user session information in DynamoDB."""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('sessions')
    table.put_item(Item={'session_id': session_id, 'username': username})
    
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
        
    # Store session information in database or cache
    session_id = generate_session_id()  # Generate a unique session ID
    store_session_info(session_id, username)  # Store session information in database or cache
    
    # Return successful login response with session ID
    response_data = {
        "message": "Successful login",
        "session_id": session_id
    }
    
    return response_data
