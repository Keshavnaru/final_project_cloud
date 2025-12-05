import boto3
import json
from boto3.dynamodb.conditions import Attr
from decimal import Decimal
 
def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj
 
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')
 
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }
    try:
        location_id = int(event['pathParameters']['id'])
    except:
        return {
            'statusCode': 400,
            'body': json.dumps("Path parameter 'id' must be a number")
        }
 
    try:
        response = table.scan(
            FilterExpression=Attr('location_id').eq(location_id)
        )
 
        items = response.get('Items', [])
        items = convert_decimals(items)
 
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
 
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
 
