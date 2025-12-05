import json
import boto3
import uuid
from decimal import Decimal

def lambda_handler(event, context):
    # Parse incoming JSON data
    try:
        data = json.loads(event['body'])
    except (KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'body': json.dumps("Bad request. Please provide valid JSON data in the body.")
        }

    # Convert numeric fields to Decimal
    numeric_fields = ['location_id', 'price', 'qty']
    for field in numeric_fields:
        if field not in data:
            return {
                'statusCode': 400,
                'body': json.dumps(f"Missing required field: {field}")
            }
        try:
            # Use Decimal for all numeric types
            data[field] = Decimal(str(data[field]))
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps(f"Field {field} must be numeric.")
            }

    # Generate a unique ID if not provided
    unique_id = data.get('id', str(uuid.uuid4()))

    # Connect to DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')

    # Insert item into DynamoDB
    try:
        table.put_item(
            Item={
                'id': unique_id,
                'location_id': data['location_id'],
                'description': data['description'],
                'name': data['name'],
                'price': data['price'],
                'qty': data['qty'],
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps(f"Item with ID {unique_id} added successfully.")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error adding item: {str(e)}")
        }
