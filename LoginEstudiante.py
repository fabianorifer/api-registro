import boto3
import hashlib
import uuid
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event,context):
    email=event['body']['email']
    password=event['body']['password']
    hashed_password=hash_password(password)

    dynamodb=boto3.resource('dynamodb')
    tabla_estudiantes=dynamodb.Table('tabla_estudiantes')
    #response=tabla_estudiantes.get_item(
    #    Key={
    #        'email':email
    #    }
    #)
    response = tabla_estudiantes.query(
        IndexName='email-index',  # Nombre del GSI
        KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
    )
    #if 'Item' not in response:
    #    return {
    #        'statusCode':403,
    #        'body': 'Usuario no existe'
    #    }
    if 'Items' not in response or len(response['Items']) == 0:
        return {
            'statusCode': 403,
            'body': 'Usuario no existe'
        }
    else:
        estudiante=response['Items'][0]
        hashed_password_db=estudiante['datos_estudiante']['password']
        if hashed_password==hashed_password_db:
            token=str(uuid.uuid4())
            fecha_hora_exp=datetime.now()+timedelta(minutes=240)
            registro={
                'token':token,
                'expires':fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S')
            }
            tabla_tokens_acceso=dynamodb.Table('tabla_tokens_acceso')
            dynamodbResponse=tabla_tokens_acceso.put_item(Item=registro)
        else:
            return {
                'statusCode': 403,
                'body': 'Password incorrecto'
            }

    return {
        'statusCode': 200,
        'token': token
    }