# This file contains the WSGI configuration required to serve up your
# web application at http://eduardopythonportfolio10.eu.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#

# +++++++++++ GENERAL DEBUGGING TIPS +++++++++++
# getting imports and sys.path right can be fiddly!
# We've tried to collect some general tips here:
# https://help.pythonanywhere.com/pages/DebuggingImportError


# +++++++++++ HELLO WORLD +++++++++++
# A little pure-wsgi hello world we've cooked up, just
# to prove everything works.  You should delete this
# code to get your own working.


# HELLO_WORLD = """<html>
# <head>
#     <title>PythonAnywhere hosted web application</title>
# </head>
# <body>
# <h1>Hello, World!</h1>
# <p>
#     This is the default welcome page for a
#     <a href="https://eu.pythonanywhere.com/">PythonAnywhere</a>
#     hosted web application.
# </p>
# <p>
#     Find out more about how to configure your own web application
#     by visiting the <a href="https://eu.pythonanywhere.com/web_app_setup/">web app setup</a> page
# </p>
# </body>
# </html>"""
#
#
# def application(environ, start_response):
#     if environ.get('PATH_INFO') == '/':
#         status = '200 OK'
#         content = HELLO_WORLD
#     else:
#         status = '404 NOT FOUND'
#         content = 'Page not found.'
#     response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(content)))]
#     start_response(status, response_headers)
#     yield content.encode('utf8')


# Below are templates for Django and Flask.  You should update the file
# appropriately for the web framework you're using, and then
# click the 'Reload /yourdomain.com/' button on the 'Web' tab to make your site
# live.

# +++++++++++ VIRTUALENV +++++++++++
# If you want to use a virtualenv, set its path on the web app setup tab.
# Then come back here and import your application object as per the
# instructions below


# +++++++++++ CUSTOM WSGI +++++++++++
# If you have a WSGI file that you want to serve using PythonAnywhere, perhaps
# in your home directory under version control, then use something like this:
#
#import sys
#
#path = '/home/eduardopythonportfolio10/path/to/my/app
#if path not in sys.path:
#    sys.path.append(path)
#
#from my_wsgi_file import application  # noqa


# +++++++++++ DJANGO +++++++++++
# To use your own django app use code like this:
import os
import sys

""" Estas líneas me permiten agarrar las credenciales como el Secret Key del .env para agarrar las variables de entorno.

En mi caso, debo poner “project_folder = os.path.expanduser('~/foxwolf20.eu.pythonanywhere.com')” (o el equivalente) en 
el archivo WSGI.
"""

from dotenv import load_dotenv
project_folder = os.path.expanduser('~/eduardopythonportfolio10.eu.pythonanywhere.com')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# Add your project directory to the sys.path
settings_path = '/home/eduardopythonportfolio10/eduardopythonportfolio10.eu.pythonanywhere.com'
sys.path.insert(0, settings_path)

## assuming your django settings file is at '/home/eduardopythonportfolio10/mysite/mysite/settings.py'
## and your manage.py is is at '/home/eduardopythonportfolio10/mysite/manage.py'
#path = '/home/eduardopythonportfolio10/mysite'
#if path not in sys.path:
#    sys.path.append(path)

# Set environment variable to tell django where your settings.py is
os.environ['DJANGO_SETTINGS_MODULE'] = 'policeAcademyExams.settings.production'

## then:
# Set the 'application' variable to the Django wsgi app
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()



# +++++++++++ FLASK +++++++++++
# Flask works like any other WSGI-compatible framework, we just need
# to import the application.  Often Flask apps are called "app" so we
# may need to rename it during the import:
#
#
#import sys
#
## The "/home/eduardopythonportfolio10" below specifies your home
## directory -- the rest should be the directory you uploaded your Flask
## code to underneath the home directory.  So if you just ran
## "git clone git@github.com/myusername/myproject.git"
## ...or uploaded files to the directory "myproject", then you should
## specify "/home/eduardopythonportfolio10/myproject"
#path = '/home/eduardopythonportfolio10/path/to/flask_app_directory'
#if path not in sys.path:
#    sys.path.append(path)
#
#from main_flask_app_file import app as application  # noqa
#
# NB -- many Flask guides suggest you use a file called run.py; that's
# not necessary on PythonAnywhere.  And you should make sure your code
# does *not* invoke the flask development server with app.run(), as it
# will prevent your wsgi file from working.
