import boto3
import random
import string
from faker import Faker
from datetime import date

fake = Faker()

# Configuración
TENANT_IDS = ["UTEC", "UPC", "UNI"]
NUM_ENTRIES = 11000
DYNAMODB_REGION = "us-east-1"

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=DYNAMODB_REGION)


def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


def convert_date_to_string(date_obj):
    return date_obj.isoformat()  # Convertimos la fecha a formato "YYYY-MM-DD"


def generate_estudiantes(table):
    estudiantes = []
    for _ in range(NUM_ENTRIES):
        tenant_id = random.choice(TENANT_IDS)
        c_estudiante = str(random.randint(100000, 999999))
        nombres = fake.first_name()
        apellidos = fake.last_name()
        email = f"{nombres.lower()}.{apellidos.lower()}@{tenant_id.lower()}.edu.pe"
        edad = random.randint(18, 25)
        password = generate_random_password()

        item = {
            "tenant_id": tenant_id,
            "c_estudiante": c_estudiante,
            "datos_estudiante": {
                "nombres": nombres,
                "apellidos": apellidos,
                "edad": edad,
                "password": password,
            },
            "email": email,
        }
        estudiantes.append(item)
        table.put_item(Item=item)
    return estudiantes


def generate_programas(table):
    programas = []
    for _ in range(NUM_ENTRIES):
        tenant_id = random.choice(TENANT_IDS)
        c_programa = f"{random.randint(2023, 2030)}#USA#MIAMI#{random.randint(10000, 99999)}"
        datos_programa = {
            "name": fake.job(),
            "empresa": fake.company(),
            "descripcion": fake.text(max_nb_chars=200),
            "direccion_alojamiento": fake.address(),
            "capacity": random.randint(1, 20),
            "monto": random.randint(200, 500),
            "start_date": convert_date_to_string(fake.date_this_year()),
            "end_date": convert_date_to_string(fake.date_this_year()),
        }
        item = {
            "tenant_id": tenant_id,
            "c_programa": c_programa,
            "datos_programa": datos_programa,
        }
        programas.append(item)
        table.put_item(Item=item)
    return programas


def generate_inscripciones(table, estudiantes, programas):
    for _ in range(NUM_ENTRIES):
        estudiante = random.choice(estudiantes)
        programa = random.choice(programas)

        item = {
            "tenant_id#c_estudiante": f"{estudiante['tenant_id']}#{estudiante['c_estudiante']}",
            "c_programa": programa["c_programa"],
            "datos_inscripcion": {
                "estado": random.choice(["Pendiente", "Aprobado", "Rechazado"]),
                "monto": programa["datos_programa"]["monto"],
            },
            "tenant_id#c_programa": f"{programa['tenant_id']}#{programa['c_programa']}"
        }
        table.put_item(Item=item)


def generate_descuentos(table, estudiantes):
    for _ in range(NUM_ENTRIES):
        estudiante = random.choice(estudiantes)
        tenant_id = estudiante["tenant_id"]
        c_estudiante = estudiante["c_estudiante"]
        descuento_value = random.randint(1, 50)  # Generar el valor del descuento
        c_descuento = f"{descuento_value}p"

        item = {
            "tenant_id#c_estudiante": f"{tenant_id}#{c_estudiante}",
            "c_descuento": c_descuento,
            "datos_descuento": {
                "descuento": descuento_value,  # Aseguramos que el valor coincida con c_descuento
                "stock": random.randint(1, 5),
            },
            "tenant_id#c_descuento": f"{tenant_id}#{c_descuento}",
        }
        table.put_item(Item=item)


def generate_boletas(table, estudiantes, programas):
    for _ in range(NUM_ENTRIES):
        estudiante = random.choice(estudiantes)
        programa = random.choice(programas)

        item = {
            "tenant_id": estudiante["tenant_id"],
            "c_estudiante#c_programa": f"{estudiante['c_estudiante']}#{programa['c_programa']}",
            "datos_boleta": {
                "empresa_bancaria": fake.company(),
                "fecha_pago": convert_date_to_string(fake.date_this_year()),
                "hora_pago": fake.time(),
                "monto": programa["datos_programa"]["monto"],
            },
        }
        table.put_item(Item=item)


def generate_encuestas(table, estudiantes, programas):
    for _ in range(NUM_ENTRIES):
        estudiante = random.choice(estudiantes)
        programa = random.choice(programas)

        item = {
            "tenant_id#c_programa": f"{programa['tenant_id']}#{programa['c_programa']}",
            "tipo#c_estudiante": f"experiencia#{estudiante['c_estudiante']}",
            "c_programa#c_estudiante": f"{programa['c_programa']}#{estudiante['c_estudiante']}",
            "descripcion": fake.text(max_nb_chars=300),
            "tenant_id#c_estudiante": f"{estudiante['tenant_id']}#{estudiante['c_estudiante']}",
            "tenant_id#tipo": f"{programa['tenant_id']}#experiencia",
            "tipo#c_programa": f"experiencia#{programa['c_programa']}",
        }
        table.put_item(Item=item)


def main():
    # Crear 11,000 registros para cada tabla
    estudiantes_table = dynamodb.Table("tabla_estudiantes")
    programas_table = dynamodb.Table("tabla_programas")
    inscripciones_table = dynamodb.Table("tabla_inscripciones")
    descuentos_table = dynamodb.Table("tabla_descuentos")
    boletas_table = dynamodb.Table("tabla_boletas")
    encuestas_table = dynamodb.Table("tabla_encuestas")

    print("Generando estudiantes...")
    estudiantes = generate_estudiantes(estudiantes_table)

    print("Generando programas...")
    programas = generate_programas(programas_table)

    print("Generando inscripciones...")
    generate_inscripciones(inscripciones_table, estudiantes, programas)

    print("Generando descuentos...")
    generate_descuentos(descuentos_table, estudiantes)

    print("Generando boletas...")
    generate_boletas(boletas_table, estudiantes, programas)

    print("Generando encuestas...")
    generate_encuestas(encuestas_table, estudiantes, programas)

    print("Datos fake generados correctamente.")


if __name__ == "__main__":
    main()