import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env si existe
load_dotenv()

# Configuración del correo y servidor IMAP
CORREO = os.getenv('EMAIL_USER')  
CONTRASEÑA = os.getenv('EMAIL_PASS')  
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')  
IMAP_PORT = int(os.getenv('IMAP_PORT', 993))  
URL_ENDPOINT = os.getenv('URL_ENDPOINT', 'https://bilbao.dynnamo.com/bilbao/?action=sync-certificados-camara')

# Configuración de la base de datos
DATABASE_CONFIG = {
    "driver": os.getenv("DB_DRIVER", "mysql"),
    "user": os.getenv("DB_USER", "root"),
    "pass": os.getenv("DB_PASS", "root"),
    "host": os.getenv("DB_HOST", "98.82.46.106"),
    "db": os.getenv("DB_NAME", "bilbao"),
    "charset": os.getenv("DB_CHARSET", "utf8"),
    "collate": os.getenv("DB_COLLATE", "utf8_general_ci"),
    "default": os.getenv("DB_DEFAULT", "true").lower() == "true",
    "debug": os.getenv("DB_DEBUG", "false").lower() == "true"
}
