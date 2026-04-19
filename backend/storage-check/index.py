import json
import os
import boto3
from botocore.exceptions import ClientError


def handler(event: dict, context) -> dict:
    """Проверяет подключение к S3 хранилищу и возвращает статистику бакета."""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400'}, 'body': ''}

    s3 = boto3.client(
        's3',
        endpoint_url='https://bucket.poehali.dev',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    )

    response = s3.list_objects_v2(Bucket='files')
    objects = response.get('Contents', [])
    count = len(objects)
    total_size = sum(obj['Size'] for obj in objects)

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
        'body': json.dumps({
            'bucket': 'files',
            'object_count': count,
            'total_size_bytes': total_size,
            'total_size_kb': round(total_size / 1024, 2),
        }),
    }
