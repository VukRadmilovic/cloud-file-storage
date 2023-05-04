import boto3

def lambda_handler(event, context):
    file_type = event['type']
    file_size = event['size']
    file_name = event['name']

    supported_file_types = ["audio/aac", "application/x-abiword", "image/avif", "video/x-msvideo", "image/bmp", "application/x-cdf",
    "text/css","text/csv","application/msword","application/vnd.openxmlformats-officedocument.wordprocessingml.document","image/gif","text/html",
    "image/vnd.microsoft.icon","image/jpeg","application/json","audio/midi","audio/x-midi","audio/mpeg","video/mp4","video/mpeg",
    "application/vnd.oasis.opendocument.presentation","application/vnd.oasis.opendocument.spreadsheet","application/vnd.oasis.opendocument.text",
    "audio/ogg","video/ogg","audio/opus","application/ogg","image/png","application/pdf","application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation","application/rtf","image/svg+xml","image/tiff","video/mp2t","text/plain",
    "audio/wav","audio/x-wav","audio/webm","video/webm","image/webp","application/vnd.ms-excel","application/xhtml+xml",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","application/xml","text/xml"]

    if(file_type not in supported_file_types):
        raise Exception("Bad request: File type is not supported!")

    if(file_size > 52428800):
        raise Exception("Bad request: File too large!")

    session_id = event['session_id']

    dynamodb = boto3.resource('dynamodb')
    sessions_table = dynamodb.Table('sessions')
    users_table = dynamodb.Table('najbolja-tabela-ikada')

    session_response = sessions_table.get_item(Key={'session_id': session_id})

    if 'Item' not in session_response:
        raise Exception("Bad request: session invalid.")

    username = session_response['Item']["username"]
    
    s3 = boto3.resource('s3')
    bucket_name = 'najbolji-bucket-ikada'
    
    bucket = s3.Bucket(bucket_name)
    object_keys = [obj.key for obj in bucket.objects.all()]
    path = 'user_data/' + username + '/' + file_name
    
    if path in object_keys:
        raise Exception("Bad request: file with the same name already exists")
    
    return generate_presigned_post(path, 3600)


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
