import os

# Configuración del correo y servidor IMAP
CORREO = os.getenv('EMAIL_USER', 'padillabrian830@gmail.com')  # Deja el valor predeterminado si no está configurada la variable de entorno
CONTRASEÑA = os.getenv('EMAIL_PASS', 'syimwnjersxgxlmu')  # Lo mismo con la contraseña
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')  # Por defecto se usa Gmail
IMAP_PORT = int(os.getenv('IMAP_PORT', 993))  # Puerto IMAP por defecto (puede cambiar según el servidor)
URL_ENDPOINT= os.getenv('URL_ENDPOINT', 'https://bilbao.dynnamo.com/bilbao/?action=sync-certificados-camara')