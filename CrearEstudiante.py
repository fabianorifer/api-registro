import boto3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event,context):
    try:
        tenant_id=event['body']['tenant_id']
        c_estudiante=event['body']['c_estudiante']
        email=event['body']['email']
        datos_estudiante=event['body']['datos_estudiante']
        password=datos_estudiante['password']

        if(email and password):
            hashed_password=hash_password(password)
            datos_estudiante['password']=hashed_password
            dynamodb=boto3.resource('dynamodb')
            tabla_estudiantes=dynamodb.Table('tabla_estudiantes')
            tabla_estudiantes.put_item(
                Item={
                    'tenant_id':tenant_id,
                    'c_estudiante':c_estudiante,
                    'datos_estudiante':datos_estudiante
                }
            )
            mensaje={
                'message':'User registered successfully',
                'c_estudiante':c_estudiante
            }
            return {
                'statusCode':200,
                'body':mensaje
            }
        else:
            mensaje={
                'error':'Invalid request body: missing email or password'
            }
            return {
                'statusCode':400,
                'body':mensaje
            }
    except Exception as e:
        print("Exception:", str(e))
        mensaje={
            'error': str(e)
        }
        return {
            'statusCode': 500,
            'body': mensaje

        }


