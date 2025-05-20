# Esto me importa todo el código del script base.py
from .base import *

""" Este es el archivo del settings_NO_USAR.py o settings que se ejecutará en un entorno de desarrollo.

En lugar de ejecutarse el settings_NO_USAR.py cuando ejecute la web app en mi entorno de desarrollo, se debe ejecutar 
este archivo.

Voy a importar todo del archivo base.py, y luego voy a sobreescribir las variables que necesito cambiar para mi entorno
de desarrollo.
"""

# Aquí se guarda la clave de Django en el archivo .env, es decir, en las
# variables de entorno (fuente: https://codinggear.blog/django-environment-variables/)
from dotenv import load_dotenv
import os

# Esto me corrige un bug que dice que "Necesitaba Autenticación para poder Enviar un Email"
import django.core.mail.backends.smtp

# Esto me ejecuta el dotenv para poder acceder a las variables de entorno
load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
# Como este es el local.py, que es para un entorno de desarrollo, "DEBUG" siempre será "True"
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

""" Aqui especifico la configuracion de la base de datos que se usará para el proyecto.

Estas son las credenciales para la base de datos que usaré en el entorno de desarrollo.
"""
DATABASES = {

    # Postgres Database's credentials
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    },


    # # Base de datos de MySQL
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.environ.get('MYSQL_NAME'),
    #     'USER': os.environ.get('MYSQL_USER'),
    #     'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
    #     'HOST': os.environ.get('MYSQL_HOST'),
    #     'PORT': os.environ.get('MYSQL_PORT'),
    # }

    # # Base de datos de de MySQLite. NO USAR.
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}

""" Backend del Email.

Esto envía emails a la consola en lugar de enviarlos usando una dirección de email real

Por los momentos, enviaré todos los emails desde Django a la consola.

Con esto, podré enviar los emails con el enlace para resetear la contraseña a la consola en lugar
de tener que configurar un email.)
"""
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# # Esto DEBO BORRARLO
# try:
#     from .local import *
# except ImportError:
#     pass
