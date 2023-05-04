import boto3

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
        
def lambda_handler(event, context):
    file_name = event['file_name']
    username = event['username']
    
    item = {
        "partial_path": username + "/" + file_name
    }
    
    for key, value in event.items():
        if key in ['file_name', 'username']:
            continue
        
        if isfloat(value):
            item[key] = str(value)
        else:
            item[key] = value
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('metadata')
    table.put_item(Item=item)

    return "Success"
