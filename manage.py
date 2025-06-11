#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

""" Modifiqué la variable DJANGO_SETTINGS_MODULE para que use el script de local.py en el entorno de desarrollo
en lugar de usar el settings_NO_USAR.py.

MODIFICAR otra vez cuando vaya a subir esto a Pythonanywhere o a AWS para que use el script de production.py.

I will modify the DJANGO_SETTINGS_MODULE variable to change the settings script for a production environment
instead of a development environment. I will do so to deploy it into PythonAnywhere.

I will later change it back to the local.py script to be able to use it in my local machine with a PostgreSQL 
database.
"""
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'policeAcademyExams.settings.local')
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'policeAcademyExams.settings.production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
