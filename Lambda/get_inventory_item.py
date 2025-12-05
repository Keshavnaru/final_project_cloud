import boto3
import json
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

deserializer = TypeDeserializer()

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        if obj == obj.to_integral_value():
            return int(obj)
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    return obj

def deserialize_item(av_map):
    py_item = {k: deserializer.deserialize(v) for k, v in av_map.items()}
    return convert_decimal(py_item)

def lambda_handler(event, context):
    dynamo_client = boto3.client('dynamodb')
    table_name = 'Inventory'
    path_params = event.get('pathParameters')

    try:
        if path_params and 'id' in path_params and 'location_id' in path_params:
            # Composite key get
            key = {
                'location_id': {'N': str(path_params['location_id'])},
                'id': {'S': path_params['id']}
            }
            response = dynamo_client.get_item(TableName=table_name, Key=key)

            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'body': json.dumps(f"Item {path_params['id']} at location {path_params['location_id']} not found")
                }

            item = deserialize_item(response['Item'])

            return {
                'statusCode': 200,
                'body': json.dumps(item)
            }

        else:
            # Scan all items
            response = dynamo_client.scan(TableName=table_name)
            items = [deserialize_item(i) for i in response.get('Items', [])]

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
