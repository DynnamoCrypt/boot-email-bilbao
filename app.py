import imaplib
import email
from email.header import decode_header
import time
import logging
import re
import requests
from config import CORREO, CONTRASEÑA, IMAP_SERVER, IMAP_PORT,URL_ENDPOINT

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

# Conectar al servidor IMAP
def conectar_email():
    # Conectar al servidor IMAP usando SSL
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(CORREO, CONTRASEÑA)
    return mail

# Función para obtener los correos no leídos con la palabra "Certificados" en el asunto
def obtener_correos_certificados(mail):
    # Seleccionar la bandeja de entrada
    mail.select("inbox")
    
    # Buscar correos no leídos con "Certificados" en el asunto
    status, mensajes = mail.search(None, '(UNSEEN SUBJECT "Certificados")')
    if status == "OK":
        return mensajes[0].split()
    return []

# Función para extraer CTG y LINK de un cuerpo de mensaje
def extraer_ctg_y_link(cuerpo):
    # Expresión regular para extraer CTG y LINK
    patron = r"CTG:\s*(\d+)\s*<([^>]+)>"
    
    # Buscar todas las coincidencias
    coincidencias = re.findall(patron, cuerpo)
    
    resultados = []
    for ctg, link in coincidencias:
        # Crear un diccionario con CTG y LINK
        resultados.append({
            "CTG": ctg,
            "LINK": link
        })
    return resultados

# Función para obtener el cuerpo del mensaje (texto plano o HTML)
def obtener_cuerpo(mensaje):
    # Si el correo tiene múltiples partes, buscar el cuerpo adecuado
    if mensaje.is_multipart():
        for parte in mensaje.walk():
            # Obtener el tipo de contenido
            tipo_contenido = parte.get_content_type()
            contenido_transferencia = parte.get("Content-Disposition")
            
            # Verificar que contenido_transferencia no sea None antes de comprobar
            if tipo_contenido == "text/plain" and (contenido_transferencia is None or "attachment" not in contenido_transferencia):
                return parte.get_payload(decode=True).decode("utf-8", errors="ignore")
            elif tipo_contenido == "text/html" and (contenido_transferencia is None or "attachment" not in contenido_transferencia):
                return parte.get_payload(decode=True).decode("utf-8", errors="ignore")
    else:
        # Si no tiene múltiples partes, es un solo cuerpo (puede ser texto plano o HTML)
        return mensaje.get_payload(decode=True).decode("utf-8", errors="ignore")

    return ""

# Función para leer los correos
def leer_correos(mail, ids_correos):
    resultados_finales = []  # Array para almacenar los objetos con CTG y LINK

    for num in ids_correos:
        # Obtener el correo por su ID
        status, data = mail.fetch(num, "(RFC822)")
        if status == "OK":
            for respuesta in data:
                if isinstance(respuesta, tuple):
                    # Analizar el correo
                    mensaje = email.message_from_bytes(respuesta[1])
                    
                    # Decodificar el asunto
                    asunto, encoding = decode_header(mensaje["Subject"])[0]
                    if isinstance(asunto, bytes):
                        asunto = asunto.decode(encoding if encoding else "utf-8")
                    
                    # Decodificar el remitente
                    remitente, encoding = decode_header(mensaje.get("From"))[0]
                    if isinstance(remitente, bytes):
                        remitente = remitente.decode(encoding if encoding else "utf-8")
                    
                    # Obtener el cuerpo del mensaje
                    cuerpo = obtener_cuerpo(mensaje)
                    
                    # Extraer CTG y LINK del cuerpo
                    resultados = extraer_ctg_y_link(cuerpo)
                    
                    # Agregar los resultados a la lista final
                    resultados_finales.extend(resultados)
    
    # Devolver los resultados acumulados
    return resultados_finales

# Función para enviar los resultados a un endpoint
def enviar_a_endpoint(resultados):
    url = URL_ENDPOINT  # Reemplaza con tu URL del endpoint
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=resultados, headers=headers)
    
    if response.status_code == 200:
        logging.info("Datos enviados correctamente al endpoint.")
    else:
        logging.error(f"Error al enviar datos al endpoint: {response.status_code}")

# Función para ejecutar el bot
def ejecutar_bot():
    while True:
        mail = conectar_email()
        correos_certificados = obtener_correos_certificados(mail)
        
        if correos_certificados:
            resultados = leer_correos(mail, correos_certificados)
            
            if resultados:
                # Enviar los resultados al endpoint
                enviar_a_endpoint(resultados)
            else:
                logging.info("No se encontraron CTGs y LINKS.")
        else:
            logging.info("No hay correos nuevos con 'Certificados' en el asunto.")

        # Esperar 60 segundos antes de verificar nuevamente
        time.sleep(60)

if __name__ == "__main__":
    ejecutar_bot()

 
"""

import imaplib
import email
from email.header import decode_header
import logging
import re
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from config import CORREO, CONTRASEÑA, IMAP_SERVER, IMAP_PORT

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

# Conectar al servidor IMAP
def conectar_email():
    # Conectar al servidor IMAP usando SSL
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(CORREO, CONTRASEÑA)
    return mail

# Función para obtener los correos no leídos con la palabra "Certificados" en el asunto
def obtener_correos_certificados(mail):
    # Seleccionar la bandeja de entrada
    mail.select("inbox")
    
    # Buscar correos no leídos con "Certificados" en el asunto
    status, mensajes = mail.search(None, '(UNSEEN SUBJECT "Certificados")')
    if status == "OK":
        return mensajes[0].split()
    return []

# Función para extraer CTG y LINK de un cuerpo de mensaje
def extraer_ctg_y_link(cuerpo):
    # Expresión regular para extraer CTG y LINK
    patron = r"CTG:\s*(\d+)\s*<([^>]+)>"
    
    # Buscar todas las coincidencias
    coincidencias = re.findall(patron, cuerpo)
    
    resultados = []
    for ctg, link in coincidencias:
        # Crear un diccionario con CTG y LINK
        resultados.append({
            "CTG": ctg,
            "LINK": link
        })
    return resultados

# Función para obtener el cuerpo del mensaje (texto plano o HTML)
def obtener_cuerpo(mensaje):
    # Si el correo tiene múltiples partes, buscar el cuerpo adecuado
    if mensaje.is_multipart():
        for parte in mensaje.walk():
            # Obtener el tipo de contenido
            tipo_contenido = parte.get_content_type()
            contenido_transferencia = parte.get("Content-Disposition")
            
            # Verificar que contenido_transferencia no sea None antes de comprobar
            if tipo_contenido == "text/plain" and (contenido_transferencia is None or "attachment" not in contenido_transferencia):
                return parte.get_payload(decode=True).decode("utf-8", errors="ignore")
            elif tipo_contenido == "text/html" and (contenido_transferencia is None or "attachment" not in contenido_transferencia):
                return parte.get_payload(decode=True).decode("utf-8", errors="ignore")
    else:
        # Si no tiene múltiples partes, es un solo cuerpo (puede ser texto plano o HTML)
        return mensaje.get_payload(decode=True).decode("utf-8", errors="ignore")

    return ""

# Función para leer los correos
def leer_correos(mail, ids_correos):
    resultados_finales = []  # Array para almacenar los objetos con CTG y LINK

    for num in ids_correos:
        # Obtener el correo por su ID
        status, data = mail.fetch(num, "(RFC822)")
        if status == "OK":
            for respuesta in data:
                if isinstance(respuesta, tuple):
                    # Analizar el correo
                    mensaje = email.message_from_bytes(respuesta[1])
                    
                    # Decodificar el asunto
                    asunto, encoding = decode_header(mensaje["Subject"])[0]
                    if isinstance(asunto, bytes):
                        asunto = asunto.decode(encoding if encoding else "utf-8")
                    
                    # Decodificar el remitente
                    remitente, encoding = decode_header(mensaje.get("From"))[0]
                    if isinstance(remitente, bytes):
                        remitente = remitente.decode(encoding if encoding else "utf-8")
                    
                    # Obtener el cuerpo del mensaje
                    cuerpo = obtener_cuerpo(mensaje)
                    
                    # Extraer CTG y LINK del cuerpo
                    resultados = extraer_ctg_y_link(cuerpo)
                    
                    # Agregar los resultados a la lista final
                    resultados_finales.extend(resultados)
    
    # Devolver los resultados acumulados
    return resultados_finales

# Función para enviar los resultados a un endpoint
def enviar_a_endpoint(resultados):
    url = "https://tuenpoint.com/api"  # Reemplaza con tu URL del endpoint
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=resultados, headers=headers)
    
    if response.status_code == 200:
        logging.info("Datos enviados correctamente al endpoint.")
    else:
        logging.error(f"Error al enviar datos al endpoint: {response.status_code}")

# Función principal para ejecutar el bot
def ejecutar_bot():
    mail = conectar_email()
    correos_certificados = obtener_correos_certificados(mail)
    
    if correos_certificados:
        resultados = leer_correos(mail, correos_certificados)
        
        if resultados:
            # Enviar los resultados al endpoint
            enviar_a_endpoint(resultados)
        else:
            logging.info("No se encontraron CTGs y LINKS.")
    else:
        logging.info("No hay correos nuevos con 'Certificados' en el asunto.")

# Configurar el programador para ejecutar el bot a las 19:00 todos los días
def configurar_programacion():
    scheduler = BlockingScheduler()
    # Programar la tarea a las 19:00 todos los días
    scheduler.add_job(ejecutar_bot, 'cron', hour=19, minute=0)
    logging.info("El bot está programado para ejecutarse todos los días a las 19:00.")
    scheduler.start()

# Ejecutar el programador
if __name__ == "__main__":
    configurar_programacion()


"""