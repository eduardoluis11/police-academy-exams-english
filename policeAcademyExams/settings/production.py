import os
import random
import string
import dj_database_url

""" Script del settings de mi web app de Django que contiene la configuración para un entorno de producción.

Del settings_NO_USAR.py, este es el archivo que se encarga de ejecutar la web app en un entorno de producción.

Cuando suba esto a Pythonanywhere o a AWS, este es el script que se debe ejecutar al correr la web app, NO
el settings_NO_USAR.py ni el local.py.
"""

from .base import *

# Este script siempre será para producción, por lo que "DEBUG" siempre será "False"
DEBUG = False

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True
    )
}

SECRET_KEY = os.environ["SECRET_KEY"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

""" Ideally, these are the settings that I need to detect my static files from my S3 Bucket in Backblaze, so that my 
fly.io hosting server can detect my static files and stop giving me the "Internal Server Error".
"""
# import boto3
# from botocore.client import Config
# from storages.backends.s3boto3 import S3Boto3Storage
#
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# AWS_LOCATION = 'static'
#
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
# STATICFILES_STORAGE = 'mysite.settings.production.StaticStorage'
# STATIC_ROOT = 'static'
#
# class StaticStorage(S3Boto3Storage):
#     location = 'static'
#     default_acl = 'public-read'
#     file_overwrite = False

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# """ S3 Bucket settings for Backblaze.
#
# The warning message indicates that the AWS_S3_FILE_OVERWRITE setting is set to True. This can cause documents and other
# user-uploaded files to be silently overwritten or deleted. It is recommended to set this to False.
# """
# if "AWS_STORAGE_BUCKET_NAME" in os.environ:
#     AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
#     AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
#     AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
#     AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID")
#     AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
#
#     INSTALLED_APPS.append("storages")
#
#     STORAGES["default"]["BACKEND"] = "storages.backends.s3boto3.S3Boto3Storage"
#
#     AWS_S3_OBJECT_PARAMETERS = {
#         'CacheControl': 'max-age=86400',
#     }
#
#     # This is to prevent a warning message from appearing while deploying my web app to fly.io
#     AWS_S3_FILE_OVERWRITE = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
    },
}

# WAGTAIL_REDIRECTS_FILE_STORAGE = "cache"

try:
    from .local import *
except ImportError:
    pass
