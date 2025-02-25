# Documentación del Bot de Certificados

## Descripción
Este bot automatiza la extracción de información de correos electrónicos y la actualización de una base de datos con los datos extraídos. Específicamente, busca correos con el asunto "Certificados", extrae los códigos CTG y enlaces asociados, y los actualiza en una base de datos MySQL a través de una conexión SSH segura.

## Instalación y Configuración

### Requisitos Previos
- Python 3.7 o superior
- Un servidor SSH con acceso a la base de datos
- Un correo electrónico IMAP (por ejemplo, Gmail)
- Dependencias de Python:
  ```sh
  pip install pymysql sshtunnel imapclient email dotenv
  ```

### Variables de Entorno
Crea un archivo `.env` en el directorio raíz del proyecto con el siguiente contenido:
```env
# Configuración IMAP
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
CORREO=tu_correo@gmail.com
PASSWORD_APLICATION=tu_password_aplicacion

# Configuración SSH
SSH_HOST=98.82.46.106
SSH_PORT=22
SSH_USER=bitnami
SSH_KEY_FILE=C://Users//padil//Documents//Claves//ERPDYNNAMO.pem

# Configuración de base de datos
DB_USER=root
DB_PASSWORD=root
DB_NAME=bilbao
DB_PORT=3306
```

## Uso
1. Asegúrate de que las dependencias estén instaladas.
2. Configura las variables de entorno en el archivo `.env`.
3. Ejecuta el bot con el siguiente comando:
   ```sh
   python main.py
   ```

## Funcionalidad

### Conexión al Correo IMAP
Se establece una conexión IMAP con Gmail utilizando credenciales seguras almacenadas en variables de entorno.

### Obtención de Correos
El bot busca en la bandeja de entrada mensajes no leídos con el asunto "Certificados".

### Extracción de Información
Del cuerpo del correo, se extraen códigos CTG y enlaces utilizando expresiones regulares.

### Actualización de Base de Datos
A través de un túnel SSH, se conecta a la base de datos y actualiza la tabla `cartas_porte` con la información extraída.

## Código Principal
```python
import logging
import time
import re
import pymysql
import imaplib
import email
from email.header import decode_header
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración del registro de eventos
logging.basicConfig(level=logging.INFO)

# Obtener configuración desde .env
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT"))
CORREO = os.getenv("CORREO")
PASSWORD_APLICATION = os.getenv("PASSWORD_APLICATION")

SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT"))
SSH_USER = os.getenv("SSH_USER")
SSH_KEY_FILE = os.getenv("SSH_KEY_FILE")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT"))

# Funciones de conexión y extracción de datos
def conectar_email():
    """Conectar al servidor IMAP."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(CORREO, PASSWORD_APLICATION)
    return mail

def obtener_correos_certificados(mail):
    """Obtener correos con 'Certificados' en el asunto."""
    mail.select("inbox")
    status, mensajes = mail.search(None, '(UNSEEN SUBJECT "Certificados")')
    return mensajes[0].split() if status == "OK" else []

def extraer_ctg_y_link(cuerpo):
    """Extraer CTG y LINK del cuerpo del mensaje."""
    patron = r"CTG:\s*(\d+)\s*<([^>]+)>"
    return [{"CTG": int(ctg), "LINK": link} for ctg, link in re.findall(patron, cuerpo)]

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
            with connection.cursor() as cursor:
                for item in data:
                    consulta_sql = "UPDATE cartas_porte SET link_cert = %s WHERE carta_porte = %s;"
                    cursor.execute(consulta_sql, (item["LINK"], item["CTG"]))
                connection.commit()
            connection.close()
            logging.info("Base de datos actualizada.")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    mail = conectar_email()
    correos = obtener_correos_certificados(mail)
    if correos:
        data = [extraer_ctg_y_link(obtener_cuerpo(mail.fetch(num, "(RFC822)")[1][0][1])) for num in correos]
        actualizar_cartas_porte(data)
    else:
        logging.info("No hay correos nuevos.")
```

## Conclusión
Este bot proporciona una solución automatizada para gestionar la recepción de certificados por correo y su actualización en una base de datos remota mediante un túnel SSH. Su configuración basada en variables de entorno facilita su despliegue en distintos entornos.

# build
 ´´´bash
 pip install pyinstaller
´´´
instala la dependencia para generar el exe, y luego 

´´´bash
  pyinstaller --onefile  main.py
´´´

# Configuración de Variables de Entorno en Linux y Windows

## Linux: Establecer Variables de Entorno

### *1. Editar el Archivo de Configuración*
Para establecer variables de entorno en Linux, edita el archivo de configuración adecuado.

- *Para un usuario en particular*, edita .bashrc:
  bash
  nano ~/.bashrc
  
- *Para todos los usuarios*, edita /etc/environment:
  bash
  sudo nano /etc/environment
  

### *2. Agregar las Variables*
Si usas .bashrc o .bash_profile, agrega al final:
bash
export IMAP_PORT="993"
export IMAP_SERVER="imap.gmail.com"
export CORREO="bilbao.dynnamo@gmail.com"
export PASSWORD_APLICATION="qhoqogoxzrnelzpu"
export SSH_HOST="98.82.46.106"
export SSH_PORT="22"
export SSH_USER="bitnami"
export DB_USER="root"
export DB_PASSWORD="root"
export DB_NAME="bilbao"
export DB_PORT="3306"
export SSH_KEY_FILE="/home/usuario/claves/erpdynnamo.pem"

(Sustituye /home/usuario/claves/erpdynnamo.pem con la ruta correcta).

Si usas /etc/environment, agrega las variables en el mismo formato pero **sin export**:
bash
IMAP_PORT="993"
IMAP_SERVER="imap.gmail.com"
CORREO="bilbao.dynnamo@gmail.com"
PASSWORD_APLICATION="qhoqogoxzrnelzpu"
SSH_HOST="98.82.46.106"
SSH_PORT="22"
SSH_USER="bitnami"
DB_USER="root"
DB_PASSWORD="root"
DB_NAME="bilbao"
DB_PORT="3306"
SSH_KEY_FILE="/home/usuario/claves/erpdynnamo.pem"


### *3. Guardar y Cerrar el Archivo*
En nano, presiona:
- CTRL + X para salir.
- Y y Enter para guardar los cambios.

### *4. Aplicar los Cambios*
Si editaste .bashrc, ejecuta:
bash
source ~/.bashrc

Si editaste /etc/environment, reinicia la sesión o ejecuta:
bash
sudo su


### *5. Verificar que las Variables Están Configuradas*
Ejecuta:
bash
echo $SSH_KEY_FILE

Si muestra la ruta correcta, la configuración fue exitosa. 🚀

---

## Windows: Establecer Variables de Entorno

En Windows, usa PowerShell para configurar variables de entorno de manera permanente.

Ejecuta los siguientes comandos en una terminal de *PowerShell con privilegios de administrador*:

powershell
[System.Environment]::SetEnvironmentVariable("IMAP_PORT", "993", "Machine")
[System.Environment]::SetEnvironmentVariable("IMAP_SERVER", "imap.gmail.com", "Machine")
[System.Environment]::SetEnvironmentVariable("CORREO", "bilbao.dynnamo@gmail.com", "Machine")
[System.Environment]::SetEnvironmentVariable("PASSWORD_APLICATION", "qhoqogoxzrnelzpu", "Machine")
[System.Environment]::SetEnvironmentVariable("SSH_HOST", "98.82.46.106", "Machine")
[System.Environment]::SetEnvironmentVariable("SSH_PORT", "22", "Machine")
[System.Environment]::SetEnvironmentVariable("SSH_USER", "bitnami", "Machine")
[System.Environment]::SetEnvironmentVariable("DB_USER", "root", "Machine")
[System.Environment]::SetEnvironmentVariable("DB_PASSWORD", "root", "Machine")
[System.Environment]::SetEnvironmentVariable("DB_NAME", "bilbao", "Machine")
[System.Environment]::SetEnvironmentVariable("DB_PORT", "3306", "Machine")
[System.Environment]::SetEnvironmentVariable("SSH_KEY_FILE", "C:\Users\bpadilla\Documents\claves\erpdynnamo.pem", "Machine")


### *Verificar las Variables de Entorno en Windows*
Para comprobar que se configuraron correctamente, usa:
powershell
echo $env:SSH_KEY_FILE

Si devuelve la ruta esperada, la configuración fue exitosa. ✅

---
