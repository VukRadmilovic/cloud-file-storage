import json
import boto3
from dateutil import parser

supported_file_types = ["audio/aac", "audio/mp3", "application/x-abiword", "image/avif", "video/x-msvideo", "image/bmp", "application/x-cdf",
"text/css","text/csv","application/msword","application/vnd.openxmlformats-officedocument.wordprocessingml.document","image/gif","text/html",
"image/vnd.microsoft.icon","image/jpeg","application/json","audio/midi","audio/x-midi","audio/mpeg","video/mp4","video/mpeg",
"application/vnd.oasis.opendocument.presentation","application/vnd.oasis.opendocument.spreadsheet","application/vnd.oasis.opendocument.text",
"audio/ogg","video/ogg","audio/opus","application/ogg","image/png","application/pdf","application/vnd.ms-powerpoint",
"application/vnd.openxmlformats-officedocument.presentationml.presentation","application/rtf","image/svg+xml","image/tiff","video/mp2t","text/plain",
"audio/wav","audio/x-wav","audio/webm","video/webm","image/webp","application/vnd.ms-excel","application/xhtml+xml",
"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","application/xml","text/xml", "image/jpg", "txt", "ppt", "pptx", "doc", "docx"]

def generate_presigned_post(object_key, expires_in):
    s3 = boto3.client('s3')
    bucket_name = 'najbolji-bucket-ikada'

    try:
        response = s3.generate_presigned_post(
            Bucket=bucket_name,
            Key=object_key,
            ExpiresIn=expires_in)
    except:
        raise
    return response

def generate_presigned_put(object_key, expires_in):
    s3 = boto3.client('s3')
    bucket_name = 'najbolji-bucket-ikada'
    try:
        response = s3.generate_presigned_url(
            ClientMethod = 'put_object',
            ExpiresIn = expires_in, 
            Params = {'Bucket': bucket_name, 'Key': object_key})
    except:
        raise
    return response

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def s3_trigger(event, context):
    dynamodb = boto3.client('dynamodb')

    event_type = event['Records'][0]['eventName']

    if event_type == "ObjectCreated:Post":
        file_key = str(event['Records'][0]['s3']['object']['key']).replace("+", " ")

        dynamodb.update_item(
            TableName='s-metadata',
            Key={
                'partial_path': {'S': file_key}
            },
            UpdateExpression='SET valid = :value',
            ExpressionAttributeValues={
                ':value': {'S': 'yes'}
            }
        )

        email = dynamodb.get_item(TableName='users',Key = {'username': {'S': file_key.split('/')[0]}})
        email = email['Item']['email']['S']
        ses_client = boto3.client('ses')
        ses_client.send_email(
            Source='2001vuk@gmail.com',
            Destination={
                'ToAddresses': [email],
            },
            Message={
                'Subject': {
                    'Data': 'Actions completed',
                    'Charset': 'utf-8'
                },
                'Body': {
                    'Text': {
                        'Data': """You have successfully uploaded a file.\nFile: {file}""".format(file=file_key.split('/')[-1]),
                        'Charset': 'utf-8'
                    }
                }
            }
        )
    elif event_type == "ObjectCreated:Put":
        try:
            s3_object_key = str(event['Records'][0]['s3']['object']['key']).replace("+", " ")
            dynamodb_table_name = 's-metadata'

            source_key = s3_object_key + '2DUP2'
            source_entry = dynamodb.get_item(
                TableName=dynamodb_table_name,
                Key={
                    'partial_path': {'S': source_key}
                }
            )

            if 'Item' not in source_entry:
                raise Exception(f"Source entry '{source_key}' not found in DynamoDB.")

            destination_item = source_entry['Item']
            destination_item['partial_path'] = {'S': s3_object_key}

            dynamodb.delete_item(
                TableName=dynamodb_table_name,
                Key={
                    'partial_path': {'S': source_key}
                }
            )

            dynamodb.put_item(
                TableName=dynamodb_table_name,
                Item=destination_item
            )

            email = dynamodb.get_item(TableName='users',Key = {'username': {'S': file_key.split('/')[0]}})
            email = email['Item']['email']['S']
            ses_client = boto3.client('ses')
            ses_client.send_email(
                Source='2001vuk@gmail.com',
                Destination={
                    'ToAddresses': [email],
                },
                Message={
                    'Subject': {
                        'Data': 'Actions completed',
                        'Charset': 'utf-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': """You have successfully modified a file.\nFile: {file}""".format(file=file_key.split('/')[-1]),
                            'Charset': 'utf-8'
                        }
                    }
                }
            )
        except Exception as e:
            print('Error:', e)
            return {
                'statusCode': 500,
                'body': 'Error occurred'
            }

def generate_presigned_get(object_key, expiration=3600):
    s3 = boto3.client('s3')
    try:
        response = s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': "najbolji-bucket-ikada",
                                                            'Key': object_key},
                                                    ExpiresIn=expiration)
    except:
        return None

    return response

def download_file(event, context):
    username = event['query']['username']
    file_path = event['query']['file_path']
    
    owner_username = file_path.split('/')[0]
    if username != owner_username:
        return 'Bad request: Cannot download files that are not your own!'
    
    return generate_presigned_get(file_path)

def generate_s3_url(event, context):
    name = event['file_name']
    type = event['type']
    size = int(event['size'])
    creation_date = event['creation_date']
    last_modification_date = event['last_modification_date']
    username = event['username']

    if(type not in supported_file_types):
        raise Exception("Bad request: File type is not supported!")

    if(size > 52428800):
        raise Exception("Bad request: File too large!")

    s3 = boto3.resource('s3')
    bucket_name = 'najbolji-bucket-ikada'
    
    bucket = s3.Bucket(bucket_name)
    object_keys = [obj.key for obj in bucket.objects.all()]
    path = username + '/' + name
    
    if path in object_keys:
        raise Exception("Bad request: file with the same name already exists!")
    
    item = {
        "partial_path" : username + "/" + name,
        "file_name" : str(name),
        "type" : str(type),
        "size" : str(size),
        "creation_date" : str(creation_date),
        "last_modification_date" : str(last_modification_date),
        "valid" : "no"
    }

    for key, value in event.items():
        if key in ['file_name', 'username', 'type', 'size', 'creation_date', 'last_modification_date']:
            continue

        if isfloat(value):
            item[key] = str(value)
        else:
            item[key] = value

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('s-metadata')
    table.put_item(Item=item)
    return generate_presigned_post(path, 3600)

def get_user_shared_data(event, context):
    username = event['query']['username']
    final_list = []
    items = []
    s3client = boto3.client('s3')
    s3bucket = boto3.resource('s3')
    my_bucket = s3bucket.Bucket('najbolji-bucket-ikada')
    key = {"partial_path": {"S" : ""} }
    
    dynamodbc = boto3.client('dynamodb')

    email = dynamodbc.get_item(TableName='users',Key = {'username': {'S': username}})
    email = email['Item']['email']['S']

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('shared')
    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Key('partial_path').begins_with("")
    )

    table = dynamodb.Table('s-metadata')
    for tempItem in response['Items']:
        if(tempItem['sharedTo'] != email):
            continue
        temp = table.get_item(Key={'partial_path': tempItem['partial_path']})
        tempItem = temp['Item']
        for object_summary in my_bucket.objects.filter(Prefix=tempItem['partial_path']):
            tokens = object_summary.key.split('.')
            extension = tokens[len(tokens) - 1]
            typeArr = [x for x in supported_file_types if extension in x]
            type = ""
            if(len(typeArr) == 0):
                type = "FOLDER"
                final_list.append({
                "file":object_summary.key,
                "type":type,
                "date_created":None,
                "url":""
                })
                
            else:
                type = typeArr[0].split("/")[0].upper()
            if type != "FOLDER":
                key['partial_path']["S"] = object_summary.key
        
                item = dynamodbc.get_item(TableName='s-metadata', Key=key)['Item']
                date_created_str = item['creation_date']['S']
                try:
                    valid = item['valid']['S']
                    if valid == 'no':
                        continue
                except:
                    pass
        
                date_created = parser.isoparse(date_created_str)
                path = username + "/" + object_summary.key
                url = s3client.generate_presigned_url(ClientMethod = 'get_object', Params = { 'Bucket': 'najbolji-bucket-ikada', 'Key': object_summary.key })
        
                items.append( {
                    "file":object_summary.key,
                    "type":type,
                    "date_created":date_created,
                    "url":url
                })

    items.sort(key=lambda x: x['date_created'], reverse=True)
    for item in items:
        item['date_created'] = item['date_created'].strftime("%Y-%m-%d %H:%M:")
    final_list = final_list + items
    return json.dumps(final_list)

def get_user_data(event, context):
    username = event['query']['username']
    album = event['query']['album']
    items = []
    s3client = boto3.client('s3')
    s3bucket = boto3.resource('s3')
    my_bucket = s3bucket.Bucket('najbolji-bucket-ikada')
    
    dynamodb = boto3.client('dynamodb')
    key = {"partial_path": {"S" : ""} }

    prefix = username + "/"
    if(album != '0'):
        prefix += album + "/"
    final_list = []
    correct_tokens = len(prefix.split('/'))
    for object_summary in my_bucket.objects.filter(Prefix=prefix):
        check = object_summary.key.split('/')
        if((len(check) == correct_tokens + 1 and check[-1] != '') or (len(check) > correct_tokens + 1) or len(check) < correct_tokens or (len(check) == correct_tokens and check[-1] == '')):
            continue
        tokens = object_summary.key.split('.')
        extension = tokens[len(tokens) - 1]
        typeArr = [x for x in supported_file_types if extension in x]
        type = ""
        if(len(typeArr) == 0):
            type = "FOLDER"
            final_list.append({
            "file":object_summary.key,
            "type":type,
            "date_created":None,
            "url":""
            })
            
        else:
            type = typeArr[0].split("/")[0].upper()
        if type != "FOLDER":
            key['partial_path']["S"] = object_summary.key
    
            item = dynamodb.get_item(TableName='s-metadata', Key=key)['Item']
            date_created_str = item['creation_date']['S']
            try:
                valid = item['valid']['S']
                if valid == 'no':
                    continue
            except:
                pass
    
            date_created = parser.isoparse(date_created_str)
            path = username + "/" + object_summary.key
            url = s3client.generate_presigned_url(ClientMethod = 'get_object', Params = { 'Bucket': 'najbolji-bucket-ikada', 'Key': object_summary.key })
    
            items.append( {
                "file":object_summary.key,
                "type":type,
                "date_created":date_created,
                "url":url
            })
    items.sort(key=lambda x: x['date_created'], reverse=True)
    for item in items:
        item['date_created'] = item['date_created'].strftime("%Y-%m-%d %H:%M:")
    final_list = final_list + items
    return json.dumps(final_list)

def get_file_metadata(event, context):
    file_path = event['query']['file_path']
    username = event['query']['username']
    owner_username = file_path.split('/')[0]
    if username != owner_username:
        return {
                'statusCode': 400,
                'body': json.dumps('Bad request: Cannot view files that are not your own!')
                }
    dynamodb = boto3.client('dynamodb')
    key = {"partial_path": {"S" : file_path} }
    file_info = dynamodb.get_item(TableName='s-metadata', Key=key)
    if file_info.get("Item") is None:
        return {
                'statusCode': 404,
                'body': json.dumps('Not found: The file does not exist!')
                }
    file_info = file_info['Item']
    item = {}
    for key, value in file_info.items():
        item[key] = value['S']
    return json.dumps(item)

def modify_metadata(event,context):
    dynamodb = boto3.client('dynamodb')
    username = event['username']
    
    file_path = event['partial_path']
    key = {"partial_path": {"S" : file_path} }
    
    file_name = event['file_name']
    file_type = event['type']
    
    if username != file_path.split("/")[0]:
        raise Exception("Bad request: You are not the file's owner!")
            
    response = dynamodb.get_item(TableName='s-metadata', Key=key)
    
    if 'Item' in response:
        real_file_name = response['Item']['file_name']['S']
        if real_file_name != file_name:
            raise Exception('Bad request: File name does not match!')
        
        real_file_type = response['Item']['type']['S']
        if real_file_type != file_type:
            raise Exception('Bad request: File type does not match!')
        item = {}

        for key, value in event.items():
            if key == 'username':
                continue
            item[key] = {'S' : value}
        dynamodb.put_item(TableName='s-metadata', Item=item)
        email = dynamodb.get_item(TableName='users',Key = {'username': {'S': username}})
        email = email['Item']['email']['S']
        ses_client = boto3.client('ses')
        ses_client.send_email(
            Source='2001vuk@gmail.com',
            Destination={
                'ToAddresses': [email],
            },
            Message={
                'Subject': {
                    'Data': 'Actions completed',
                    'Charset': 'utf-8'
                },
                'Body': {
                    'Text': {
                        'Data': """You have successfully modified a file.\nFile: {file}""".format(file=file_path.split('/')[-1]),
                        'Charset': 'utf-8'
                    }
                }
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully modified the file!')
        }
        
    else:
        raise Exception('Not found: The file does not exist!')
    
def full_modify_item(event, context):
    dynamodb = boto3.client('dynamodb')
    file_name = event['file_name']
    file_path = event['partial_path']
    key = {"partial_path": {"S" : file_path} }
    file_type = event['type']
    file_size = int(event['size'])
    username = event['username']

    if(file_type not in supported_file_types):
        raise Exception("Bad request: File type is not supported!")

    if(file_size > 52428800):
        raise Exception("Bad request: File too large!")
        
    if username != file_path.split("/")[0]:
        raise Exception("Bad request: You are not the file's owner!")
            
    response = dynamodb.get_item(TableName='s-metadata', Key=key)
    
    if 'Item' in response:
        real_file_name = response['Item']['file_name']['S']
        if real_file_name != file_name:
            raise Exception('Bad request: File name does not match!')
        
        real_file_type = response['Item']['type']['S']
        if real_file_type != file_type:
            raise Exception('Bad request: File type does not match!')
        item = {}

        for key, value in event.items():
            if key == 'username':
                continue
            item[key] = {'S' : value}
        item['partial_path']['S'] += '2DUP2'
        dynamodb.put_item(TableName='s-metadata', Item=item)
        return generate_presigned_put(file_path, 3600)
    else:
        raise Exception('Not found: The file does not exist!')
    
def delete_item(event, context):
    username = event['query']['username']
    file_path = event['query']['file_path']
    
    owner_username = file_path.split('/')[0]
    if username != owner_username:
        return {
                'statusCode': 400,
                'body': json.dumps('Bad request: Cannot view files that are not your own!')
                }
                
    dynamodb = boto3.client('dynamodb')
    key = {"partial_path": {"S" : file_path}}
    s3 = boto3.client('s3')
    bucket_name = 'najbolji-bucket-ikada'
    file_info = dynamodb.get_item(TableName='s-metadata', Key=key)
    if file_info.get("Item") is None:
        return {
                'statusCode': 404,
                'body': json.dumps('Not found: The file does not exist!')
                }
    s3.delete_object(Bucket=bucket_name, Key=file_path)
    dynamodb.delete_item(TableName='s-metadata', Key=key)
    email = dynamodb.get_item(TableName='users',Key = {'username': {'S': username}})
    email = email['Item']['email']['S']
    ses_client = boto3.client('ses')
    ses_client.send_email(
        Source='2001vuk@gmail.com',
        Destination={
            'ToAddresses': [email],
        },
        Message={
            'Subject': {
                'Data': 'Actions completed',
                'Charset': 'utf-8'
            },
            'Body': {
                'Text': {
                    'Data': """You have successfully deleted a file.\nFile: {file}""".format(file=file_path.split('/')[-1]),
                    'Charset': 'utf-8'
                }
            }
        }
    )
    return {
        'statusCode': 200,
        'body': json.dumps('File successfully deleted!')
    }

def add_user_trigger(event, context):
    username = event['userName']
    email = event['request']['userAttributes']['email']
    dynamodb = boto3.resource('dynamodb')
    item = {
        "username" : username,
        "email": email
    }
    table = dynamodb.Table('users')
    table.put_item(Item=item)
    return event

def create_album(event, context):
    username = event['query']['username']
    file_path = event['query']['file_path']
    
    owner_username = file_path.split('/')[0]
    if username != owner_username:
        return 'Bad request: Cannot create albums inside albums which are not yours!'

    s3 = boto3.client('s3')
    return s3.put_object(Bucket="najbolji-bucket-ikada", Key=file_path + "/")

def delete_album(event, context):
    username = event['query']['username']
    file_path = event['query']['file_path']
    
    owner_username = file_path.split('/')[0]
    if username != owner_username:
        return 'Bad request: Cannot delete albums which are not your own!'
    
    if file_path == owner_username + "/":
        return 'Bad request: Cannot delete root album!'
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('najbolji-bucket-ikada')
    bucket.objects.filter(Prefix=file_path).delete()
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('s-metadata')

    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Key('partial_path').begins_with(file_path)
    )

    with table.batch_writer() as batch:
        for item in response['Items']:
            batch.delete_item(Key={'partial_path': item['partial_path']})

def family_album_function(event, context):
    user = event['query']['user']
    family = event['query']['family']

    ses_client = boto3.client('ses')
    ses_client.send_email(
            Source='2001vuk@gmail.com',
            Destination={
                'ToAddresses': [family],
            },
            Message={
                'Subject': {
                    'Data': 'Actions completed',
                    'Charset': 'utf-8'
                },
                'Body': {
                    'Text': {
                        'Data': """You have successfully been added as family member""".format(),
                        'Charset': 'utf-8'
                    }
                }
            }
        )
    #dynamodb = boto3.client('dynamodb')
    #familyItem = {
    #            "parent": user,
    #            "child": family,
    #        }
    #dynamodb.put_item(
    #            TableName="family",
    #            Item = familyItem
    #        )

    dynamodb = boto3.resource('dynamodb')
    tableMeta = dynamodb.Table('s-metadata')
    response = tableMeta.scan(
        FilterExpression=boto3.dynamodb.conditions.Key('partial_path').begins_with(user)
    )

    table = dynamodb.Table('shared')
    with table.batch_writer() as batch:
        for item in response['Items']:
            tempItem = {
                "sharedTo": family,
                "sharedFrom": user,
                "partial_path": item['partial_path']
            }
            batch.put_item(Item=tempItem)
    return {
        'statusCode': 200,
        'body': json.dumps('Family successfully created!')
    }


def share_album_function(event, context):
    sharedFrom = event['query']['sharedFrom']
    file_path = event['query']['file_path']
    sharedTo = event['query']['sharedTo']
    
    owner_username = file_path.split('/')[0]
    if sharedFrom != owner_username:
        return 'Bad request: Cannot share albums which are not your own!'

    dynamodb = boto3.resource('dynamodb')
    tableMeta = dynamodb.Table('s-metadata')
    response = tableMeta.scan(
        FilterExpression=boto3.dynamodb.conditions.Key('partial_path').begins_with(file_path)
    )
    
    table = dynamodb.Table('shared')
    with table.batch_writer() as batch:
        #tempItem = {
        #        "sharedTo": sharedTo,
        #        "sharedFrom": sharedFrom,
        #        "partial_path": file_path
        #    }
        #batch.put_item(Item=tempItem)
        for item in response['Items']:
            tempItem = {
                "sharedTo": sharedTo,
                "sharedFrom": sharedFrom,
                "partial_path": item['partial_path']
            }
            batch.put_item(Item=tempItem)
    return {
        'statusCode': 200,
        'body': json.dumps('File successfully shared!')
    }

def stop_share_album_function(event, context):
    sharedFrom = event['query']['sharedFrom']
    file_path = event['query']['file_path']
    sharedTo = event['query']['sharedTo']

    owner_username = file_path.split('/')[0]
    if sharedFrom != owner_username:
        return 'Bad request: Cannot delete albums which are not your own!'
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('s-metadata')

    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Key('partial_path').begins_with(file_path)
    )

    table = dynamodb.Table('shared')
    with table.batch_writer() as batch:
        for item in response['Items']:
            batch.delete_item(Key={'partial_path': item['partial_path']})
        batch.delete_item(Key={'partial_path': file_path})

    return {
        'statusCode': 200,
        'body': json.dumps('File successfully stoped sharing!')
    }

def copy_file(event, context):
    username = event['query']['username']
    source_path = event['query']['source_path']
    destination_path = event['query']['destination_path']
    
    owner_username1 = source_path.split('/')[0]
    owner_username2 = destination_path.split('/')[0]
    if username != owner_username1 or username != owner_username2:
        return 'Bad request: Cannot copy files which are not your own or to foreign folders!'

    copy(source_path, destination_path)

    dynamodb = boto3.client('dynamodb')
    email = dynamodb.get_item(TableName='users',Key = {'username': {'S': source_path.split('/')[0]}})
    email = email['Item']['email']['S']
    ses_client = boto3.client('ses')
    ses_client.send_email(
        Source='2001vuk@gmail.com',
        Destination={
            'ToAddresses': [email],
        },
        Message={
            'Subject': {
                'Data': 'Actions completed',
                'Charset': 'utf-8'
            },
            'Body': {
                'Text': {
                    'Data': """You have successfully copied a file.\nFile: {file}""".format(file=source_path.split('/')[-1]),
                    'Charset': 'utf-8'
                }
            }
        }
    )

def copy(source_path, destination_path, delete=False):
    s3 = boto3.resource('s3')
    copy_source = {
        'Bucket': 'najbolji-bucket-ikada',
        'Key': source_path
        }
    bucket = s3.Bucket('najbolji-bucket-ikada')
    bucket.copy(copy_source, destination_path)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('s-metadata')

    response = table.get_item(Key={'partial_path': source_path})
    item = response['Item']
    
    new_item = {**item, 'partial_path': destination_path}
    table.put_item(Item=new_item)

    if delete:
        s3 = boto3.client('s3')
        dynamodb = boto3.client('dynamodb')

        s3.delete_object(Bucket = 'najbolji-bucket-ikada', Key = source_path)
        dynamodb.delete_item(
                TableName='s-metadata',
                Key={
                    'partial_path': {'S': source_path}
                }
            )

def move_file(event, context):
    username = event['query']['username']
    source_path = event['query']['source_path']
    destination_path = event['query']['destination_path']
    
    owner_username1 = source_path.split('/')[0]
    owner_username2 = destination_path.split('/')[0]
    if username != owner_username1 or username != owner_username2:
        return 'Bad request: Cannot move files which are not your own or to foreign folders!'

    copy(source_path, destination_path, True)

    dynamodb = boto3.client('dynamodb')
    email = dynamodb.get_item(TableName='users',Key = {'username': {'S': source_path.split('/')[0]}})
    email = email['Item']['email']['S']
    ses_client = boto3.client('ses')
    ses_client.send_email(
        Source='2001vuk@gmail.com',
        Destination={
            'ToAddresses': [email],
        },
        Message={
            'Subject': {
                'Data': 'Actions completed',
                'Charset': 'utf-8'
            },
            'Body': {
                'Text': {
                    'Data': """You have successfully moved a file.\nFile: {file}""".format(file=source_path.split('/')[-1]),
                    'Charset': 'utf-8'
                }
            }
        }
    )
