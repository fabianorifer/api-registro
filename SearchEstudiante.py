"""
import boto3
import json

# Inicializar cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')

# Nombre de la tabla
TABLE_NAME = "tabla_estudiantes"


def lambda_handler(event, context):



    try:

        # Inicio - Proteger el Lambda
        token = event['headers']['Authorization']
        lambda_client = boto3.client('lambda')
        payload_string = '{ "token": "' + token + '" }'
        invoke_response = lambda_client.invoke(
            FunctionName="ValidarTokenEstudiante",
            InvocationType='RequestResponse',
            Payload=payload_string
        )
        response = json.loads(invoke_response['Payload'].read())
        print(response)
        if response['statusCode'] == 403:
            return {
                'statusCode': 403,
                'status': 'Forbidden - Acceso no autorizado'
            }
        # Fin - Proteger el Lambda

        # Extraer el email del body
        email = event['body']['email']

        if not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "El campo 'email' es requerido"})
            }

        # Obtener referencia a la tabla
        table = dynamodb.Table(TABLE_NAME)

        # Buscar el estudiante usando el índice global secundario
        response = table.query(
            IndexName="email-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )

        # Verificar si se encontró el estudiante
        items = response.get('Items', [])
        if not items:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "Estudiante no encontrado"})
            }

        # Retornar el estudiante encontrado
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Estudiante encontrado", "data": items[0]})
        }

    except Exception as e:
        # Manejar errores
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error interno del servidor", "error": str(e)})
        }
"""



"""
import boto3

def lambda_handler(event, context):
    # Entrada (json)
    email = event['body']['tenant_id']
    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('tabla_estudiantes')
    response = table.get_item(
        Key={
            'email': email,
        }
    )
    # Salida (json)
    return {
        'statusCode': 200,
        'response': response
    }
"""


import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    try:

        # Inicio - Proteger el Lambda
        token = event['headers']['Authorization']
        lambda_client = boto3.client('lambda')
        payload_string = '{ "token": "' + token + '" }'
        invoke_response = lambda_client.invoke(
            FunctionName="ValidarTokenEstudiante",
            InvocationType='RequestResponse',
            Payload=payload_string
        )
        response = json.loads(invoke_response['Payload'].read())
        print(response)
        if response['statusCode'] == 403:
            return {
                'statusCode': 403,
                'status': 'Forbidden - Acceso no autorizado'
            }
        # Fin - Proteger el Lambda

        # Extraer el email del body
        email=event['body']['email']
        print(email)

        if not email:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'status': 'error',
                    'message': 'El campo "email" es requerido.',
                })
            }

        # Conexión a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('tabla_estudiantes')

        # Consultar el GSI usando el email como clave
        response = table.query(
            IndexName='email-index',  # Nombre del índice
            KeyConditionExpression=Key('email').eq(email)  # Condición de búsqueda
        )

        # Verificar si se encontraron resultados
        items = response.get('Items', [])
        print(items)
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'status': 'error',
                    'message': 'Estudiante no encontrado.'
                })
            }

        # Retornar el estudiante encontrado
        return {
            'statusCode': 200,
            'body': items[0]
        }

    except Exception as e:
        # Manejo de errores
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': 'Error interno del servidor.',
                'error': str(e)
            })
        }