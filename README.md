
```markdown
# Explicación del Bot para Leer Correos Usando IMAP

Este bot está diseñado para conectarse a un servidor IMAP (como Gmail, Outlook, Yahoo, etc.) y revisar los correos no leídos. El bot obtiene el **remitente**, el **asunto** y el **cuerpo** de los correos no leídos, y los muestra en la consola. El proceso se repite cada 60 segundos.

## Flujo Detallado

### 1. **Configuración Inicial**
Las credenciales (correo y contraseña) y los parámetros del servidor IMAP (como el nombre del servidor y el puerto) se toman desde **variables de entorno** o desde un archivo de configuración (`config.py`). Estas configuraciones permiten que el bot se conecte a cualquier servidor IMAP sin modificar el código directamente.

### 2. **Conexión con el Servidor IMAP (`conectar_email`)**
El bot utiliza las credenciales y el servidor IMAP configurado para establecer una conexión segura con el servidor IMAP:

```python
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(CORREO, CONTRASEÑA)
```

El bot puede conectarse a cualquier servidor IMAP, como Gmail, Outlook, etc., simplemente cambiando las configuraciones en el archivo `config.py` o utilizando variables de entorno. Se usa el protocolo IMAP sobre SSL para asegurar la conexión.

### 3. **Obtener Correos No Leídos (`obtener_correos_no_leidos`)**
Una vez establecida la conexión, el bot selecciona la **bandeja de entrada** y busca los correos **no leídos** (con el filtro `UNSEEN`):

```python
status, mensajes = mail.search(None, 'UNSEEN')
```

Si se encuentran correos no leídos, el bot devuelve una lista con los **IDs** de esos correos. Estos IDs serán utilizados para obtener el contenido completo de los correos.

### 4. **Leer los Correos (`leer_correos`)**
El bot accede a cada correo no leído utilizando el método `mail.fetch()`. Luego decodifica el **remitente** y el **asunto** de los correos, y extrae el cuerpo del mensaje (ya sea en texto plano o HTML). El contenido del correo se obtiene de la siguiente manera:

```python
status, data = mail.fetch(num, "(RFC822)")
```

Aquí `num` es el ID del correo no leído y `(RFC822)` indica que se desea recuperar todo el contenido del correo en formato estándar.

### 5. **Obtener el Cuerpo del Correo (`obtener_cuerpo`)**
La función `obtener_cuerpo()` maneja la extracción del cuerpo del mensaje, considerando si el correo tiene múltiples partes (por ejemplo, texto plano y HTML). Si el correo tiene varias partes, el bot busca el contenido adecuado (sin adjuntos) y lo devuelve en formato de texto:

```python
if mensaje.is_multipart():
    for parte in mensaje.walk():
        tipo_contenido = parte.get_content_type()
        if tipo_contenido == "text/plain" and "attachment" not in parte.get("Content-Disposition"):
            return parte.get_payload(decode=True).decode("utf-8", errors="ignore")
```

### 6. **Mostrar los Detalles del Correo**
Una vez que el bot ha decodificado el **remitente**, el **asunto** y el **cuerpo** del correo, muestra esta información en la consola mediante el uso de `logging`:

```python
logging.info(f"Nuevo correo de: {remitente}")
logging.info(f"Asunto: {asunto}")
logging.info(f"Cuerpo del mensaje:\n{cuerpo}")
```

Este proceso proporciona un seguimiento claro y estructurado de los correos nuevos que se reciben.

### 7. **Ciclo Continuo**
El bot se ejecuta en un **bucle infinito**, revisando los correos cada 60 segundos. Si no hay correos nuevos, muestra un mensaje indicando que no hay correos no leídos:

```python
time.sleep(60)
```

Esto permite que el bot funcione de manera continua sin intervención manual.

### 8. **Manejo de Errores**
El bot está diseñado para manejar posibles errores, como la falla en la conexión al servidor IMAP. Si ocurre un error, el bot captura la excepción y espera 60 segundos antes de intentar nuevamente.

---

## **Configuración del Servidor IMAP y las Credenciales**

El código está diseñado para ser flexible con el servidor IMAP y las credenciales. Puedes usar cualquier servidor IMAP proporcionado por tu proveedor de correo (Gmail, Outlook, Yahoo, etc.) solo con actualizar las configuraciones adecuadas.

### **Parámetros de Configuración**:
- **Servidor IMAP**: El nombre del servidor IMAP de tu proveedor de correo (ej. `imap.gmail.com` para Gmail).
- **Puerto IMAP**: El puerto IMAP seguro (generalmente `993`).
- **Credenciales**: Tu correo electrónico y contraseña o token de acceso (si usas verificación en dos pasos).

### **Ejemplo de Configuración**

#### **Configuración con Gmail**:

Si deseas usar Gmail, modifica las variables en el archivo `config.py`:

#### `config.py`

```python
# Variables para Gmail
CORREO = "tucorreo@gmail.com"
CONTRASEÑA = "tucontraseñaapp"
IMAP_SERVER = "imap.gmail.com"  # Servidor IMAP de Gmail
IMAP_PORT = 993  # Puerto IMAP seguro
```

#### **Configuración con Variables de Entorno**

Si prefieres configurar las variables de entorno, usa los siguientes comandos en tu sistema:

#### En **Windows** (PowerShell):

```powershell
[System.Environment]::SetEnvironmentVariable("EMAIL_USER", "tucorreo@gmail.com", "User")
[System.Environment]::SetEnvironmentVariable("EMAIL_PASS", "tucontraseñaapp", "User")
[System.Environment]::SetEnvironmentVariable("IMAP_SERVER", "imap.gmail.com", "User")
[System.Environment]::SetEnvironmentVariable("IMAP_PORT", "993", "User")
```

#### En **Linux/macOS**:

```bash
export EMAIL_USER="tucorreo@gmail.com"
export EMAIL_PASS="tucontraseñaapp"
export IMAP_SERVER="imap.gmail.com"
export IMAP_PORT="993"
```

---

## **Resumen del Funcionamiento**

- **Configuración Flexible**: El bot se conecta a cualquier servidor IMAP configurado en el archivo `config.py` o en las variables de entorno.
- **Búsqueda de Correos No Leídos**: El bot busca los correos no leídos cada vez que se ejecuta.
- **Lectura de Correos**: El bot decodifica y muestra el **remitente**, **asunto** y **cuerpo** de los correos no leídos en la consola.
- **Ejecución Continua**: El bot revisa los correos cada 60 segundos y repite el proceso sin intervención manual.

### Servidores IMAP Comunes:
- **Gmail**: `imap.gmail.com`, puerto `993`
- **Outlook**: `outlook.office365.com`, puerto `993`
- **Yahoo**: `imap.mail.yahoo.com`, puerto `993`
- **Proveedores Personalizados**: `imap.dominio.com` (reemplaza con el servidor IMAP adecuado).

---

### **Consideraciones de Seguridad**

- **Contraseñas**: Si usas verificación en dos pasos, necesitarás generar una **contraseña de aplicación** para acceder al correo de forma segura.
- **Seguridad de las Credenciales**: Evita almacenar tus credenciales directamente en el código. Usa variables de entorno o un archivo de configuración que no se comparta públicamente.
```