import boto3
import json

def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamo_client = boto3.client('dynamodb')
    table_name = 'Inventory'

    # Validate path parameters
    if 'pathParameters' not in event or not event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing path parameters")
        }

    path_params = event['pathParameters']

    # Prepare key based on table schema
    # ----- Adjust this depending on your table -----
    if 'id' in path_params and 'location_id' in path_params:
        # Composite key: location_id (Number) + id (String)
        key = {
            'location_id': {'N': str(path_params['location_id'])},
            'id': {'S': path_params['id']}
        }
        key_desc = f"id={path_params['id']} & location_id={path_params['location_id']}"
    elif 'id' in path_params:
        # Single partition key: id (String)
        key = {'id': {'S': path_params['id']}}
        key_desc = f"id={path_params['id']}"
    elif 'location_id' in path_params:
        # Single partition key: location_id (Number)
        key = {'location_id': {'N': str(path_params['location_id'])}}
        key_desc = f"location_id={path_params['location_id']}"
    else:
        return {
            'statusCode': 400,
            'body': json.dumps("Required path parameter not provided")
        }

    # Attempt to delete the item
    try:
        dynamo_client.delete_item(TableName=table_name, Key=key)
        return {
            'statusCode': 200,
            'body': json.dumps(f"Item with {key_desc} deleted successfully.")
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error deleting item: {str(e)}")
        }
