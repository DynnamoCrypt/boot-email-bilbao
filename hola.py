from sshtunnel import SSHTunnelForwarder
import pymysql
import logging

# Configuración del registro de eventos para SSHTunnelForwarder
logging.basicConfig(level=logging.INFO)

# Parámetros SSH
SSH_HOST = "98.82.46.106"
SSH_PORT = 22
SSH_USER = "bitnami"
SSH_KEY_FILE = "C://Users//padil//Documents//Claves//ERPDYNNAMO.pem"

# Parámetros de conexión a la base de datos
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "bilbao"
DB_PORT = 3306

try:
    # Establecer el túnel SSH
    with SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_pkey=SSH_KEY_FILE,
        remote_bind_address=("127.0.0.1", DB_PORT),
        local_bind_address=("127.0.0.1", 3307)  # Puerto local específico
    ) as tunnel:
        logging.info(f"Túnel SSH activo en el puerto local: {tunnel.local_bind_port}")

        # Conectar a la base de datos a través del túnel SSH
        connection = pymysql.connect(
            host="127.0.0.1",
            port=tunnel.local_bind_port,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset="utf8mb4",  # Uso de utf8mb4 para mejor compatibilidad
            cursorclass=pymysql.cursors.DictCursor  # Resultados como diccionarios
        )

        try:
            with connection.cursor() as cursor:
                # Ejecutar una consulta de prueba
                cursor.execute("SELECT VERSION();")
                version = cursor.fetchone()
                logging.info(f"Versión de MySQL: {version['VERSION()']}")
        finally:
            connection.close()
            logging.info("Conexión a la base de datos finalizada.")

except Exception as e:
    logging.error(f"Se produjo un error: {e}")
