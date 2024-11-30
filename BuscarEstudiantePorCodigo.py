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

        # Extraer tenant_id y c_estudiante del body
        tenant_id = event['body']['tenant_id']
        c_estudiante = event['body']['c_estudiante']

        print(f"tenant_id: {tenant_id}, c_estudiante: {c_estudiante}")

        # Validar que ambos campos estén presentes
        if not tenant_id or not c_estudiante:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'status': 'error',
                    'message': 'Los campos "tenant_id" y "c_estudiante" son requeridos.',
                })
            }

        # Conexión a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('tabla_estudiantes')

        # Consultar DynamoDB con la clave primaria (tenant_id y c_estudiante)
        response = table.get_item(
            Key={
                'tenant_id': tenant_id,
                'c_estudiante': c_estudiante
            }
        )

        # Verificar si se encontró un resultado
        item = response.get('Item')
        print(item)
        if not item:
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
            'body': item
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