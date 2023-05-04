import boto3

def lambda_handler(event, context):
    file_name = event['file_name']
    username = event['username']
    
    item = {
        "partial_path": username + "/" + file_name
    }
    
    for key, value in event.items():
        if key in ['file_name', 'username']:
            continue
        
        item[key] = value
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('metadata')
    table.put_item(Item=item)

    return "Success"
