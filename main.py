import logging
import time
import re
import pymysql
import imaplib
import email
from email.header import decode_header
from sshtunnel import SSHTunnelForwarder
from config import CORREO, PASSWORD_APLICATION

# Configuración del registro de eventos
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

def conectar_email():
    """Conectar al servidor IMAP usando SSL."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(CORREO, PASSWORD_APLICATION)
    return mail

def obtener_correos_certificados(mail):
    """Obtener correos no leídos con 'Certificados' en el asunto."""
    mail.select("inbox")
    status, mensajes = mail.search(None, '(UNSEEN SUBJECT "Certificados")')
    # logging.info(f"Estado de la búsqueda: {status}")
    if status == "OK":
        # logging.info(f"Mensajes encontrados: {mensajes[0]}")
        # status, carpetas = mail.list()
        # logging.info(f"Carpetas disponibles: {carpetas}")
        return mensajes[0].split() if mensajes[0] else []
    else:
        logging.info("No se encontraron mensajes.")
        return []

def obtener_cuerpo(mensaje):
    """Obtener el cuerpo del mensaje (texto plano o HTML)."""
    if mensaje.is_multipart():
        for parte in mensaje.walk():
            tipo_contenido = parte.get_content_type()
            contenido_transferencia = parte.get("Content-Disposition")
            if tipo_contenido in ["text/plain", "text/html"] and (contenido_transferencia is None or "attachment" not in contenido_transferencia):
                return parte.get_payload(decode=True).decode("utf-8", errors="ignore")
    return mensaje.get_payload(decode=True).decode("utf-8", errors="ignore")

def extraer_ctg_y_link(cuerpo):
    """Extraer CTG y LINK del cuerpo del mensaje."""
    patron = r"CTG:\s*(\d+)\s*<([^>]+)>"
    return [{"CTG": int(ctg), "LINK": link} for ctg, link in re.findall(patron, cuerpo)]

def leer_correos(mail, ids_correos):
    """Leer correos y extraer CTG y LINK."""
    resultados_finales = []
    for num in ids_correos:
        status, data = mail.fetch(num, "(RFC822)")
        if status == "OK":
            for respuesta in data:
                if isinstance(respuesta, tuple):
                    mensaje = email.message_from_bytes(respuesta[1])
                    cuerpo = obtener_cuerpo(mensaje)
                    resultados_finales.extend(extraer_ctg_y_link(cuerpo))
    return resultados_finales

def ejecutar_bot():
    """Ejecutar el bot para obtener CTG y LINK de los correos nuevos."""
    while True:
        mail = conectar_email()
        correos_certificados = obtener_correos_certificados(mail)
        if correos_certificados:
            resultados = leer_correos(mail, correos_certificados)
            if resultados:
                return resultados
            logging.info("No se encontraron CTGs y LINKS.")
        else:
            logging.info("No hay correos nuevos con 'Certificados' en el asunto.")
        time.sleep(60)

def actualizar_cartas_porte(data):
    """Actualizar la base de datos con los CTG y LINK extraídos."""
    try:
        with SSHTunnelForwarder(
            (SSH_HOST, SSH_PORT),
            ssh_username=SSH_USER,
            ssh_pkey=SSH_KEY_FILE,
            remote_bind_address=("127.0.0.1", DB_PORT),
            local_bind_address=("127.0.0.1", 3307)
        ) as tunnel:
            logging.info(f"Túnel SSH activo en el puerto local: {tunnel.local_bind_port}")
            connection = pymysql.connect(
                host="127.0.0.1",
                port=tunnel.local_bind_port,
                user=DB_USER,
                password=DB_PASSWORD,
                db=DB_NAME,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            try:
                with connection.cursor() as cursor:
                    for item in data:
                        consulta_sql = "UPDATE cartas_porte SET link_cert = %s WHERE carta_porte = %s;"
                        valores = (item["LINK"], item["CTG"])
                        cursor.execute(consulta_sql, valores)
                    connection.commit()
                    logging.info("Todas las consultas se ejecutaron con éxito.")
            finally:
                connection.close()
                logging.info("Conexión a la base de datos cerrada.")
    except Exception as e:
        logging.error(f"Se produjo un error: {e}")

if __name__ == "__main__":
    data = ejecutar_bot()
    if data:
        actualizar_cartas_porte(data)
    else:
        logging.info("No se encontraron resultados para actualizar.")
