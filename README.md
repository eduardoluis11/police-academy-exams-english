# police-academy-exams-english

This is my Django web app, translated into English, that lets you practice entrance exams for a police academy. It's a project for my portfolio. Made by Eduardo Salinas.

## Author

Eduardo Salinas

## TODO

I need to translate the rest of the text of this README file into English.

## Instrucciones de uso

1) Crea un entorno virtual. Hay varias formas de hacer esto. Yo uso mkvirtualenv en Windows. Para instalar mkvirtualenv en Windows, sigue estos pasos:

### Instalación de `mkvirtualenv` en Windows
I) **Instalar Python y pip**:
   - Asegúrate de tener Python instalado en tu máquina. Puedes descargarlo desde [python.org](https://www.python.org/).
   - Durante la instalación, marca la casilla "Add Python to PATH".
   - Una vez instalado, verifica que Python y pip están funcionando ejecutando en la consola:
     ```bash
     python --version
     pip --version
     ```

II) **Instalar `virtualenvwrapper-win`**:
   - `mkvirtualenv` es parte de `virtualenvwrapper`, pero en Windows necesitas instalar una versión adaptada llamada `virtualenvwrapper-win`.
   - Ejecuta el siguiente comando en la terminal para instalarlo:
     ```bash
     pip install virtualenvwrapper-win
     ```

III) **Configurar la variable de entorno `WORKON_HOME` (opcional)**:
   - Por defecto, los entornos virtuales se almacenan en `%USERPROFILE%\Envs`. Si deseas cambiar esta ubicación:
     - Ve a "Configuración avanzada del sistema" > "Variables de entorno".
     - Crea una nueva variable de entorno llamada `WORKON_HOME` y establece la ruta donde deseas almacenar los entornos virtuales.

---

### Activar y usar `mkvirtualenv`
I) **Crear un entorno virtual**:
   - Usa el comando `mkvirtualenv` para crear un nuevo entorno virtual. Por ejemplo:
     ```bash
     mkvirtualenv mi_entorno
     ```

II) **Activar un entorno virtual**:
   - Para activar un entorno virtual existente, usa el comando:
     ```bash
     workon mi_entorno
     ```

III) **Desactivar el entorno virtual**:
   - Cuando termines de trabajar, desactiva el entorno virtual con:
     ```bash
     deactivate
     ```
---

2) Instala las dependencias del proyecto. Para hacer esto, primero activa tu entorno virtual, y después ejecuta el siguiente comando en la consola:
```bash
pip install -r requirements.txt
```

---

3) Si vas a usar la base de datos de MySQL, inserta las credenciales de tu base de datos en el archivo .env. Elimina mis credenciales de MySQL de mi archivo .env, e inserta las credenciales de tu base de datos.

Mientras tanto, si quieres hacer pruebas rápidas, puedes usar la base de datos SQLite que viene por defecto, e ignora este paso.

4) Migra la base de datos. Para hacer esto, ejecuta el siguiente comando en la consola:
```bash
python manage.py migrate
``` 

5) Crea un superusuario. Para hacer esto, ejecuta el siguiente comando en la consola:
```bash
python manage.py createsuperuser
```

6) Corre el servidor. Para hacer esto, ejecuta el siguiente comando en la consola:
```bash
python manage.py runserver
```

7) Abre tu navegador y ve a la dirección `localhost:8000`. Ahí podrás ver la web app.

8) Para ir al panel de administración de Django, debes ir a la dirección `localhost:8000/admin` y autenticarte con las credenciales del superusuario que creaste en el paso 5.

## Legal

### Uso de Inteligencias Artificiales Generativas

Se usaron inteligencias artificiales generativas tipo LLM para generar y crear parte del código de esta web app.

Hasta donde sabemos, todo el código que ha sido generado es original, pero hay un pequeño riesgo de que algún snippet de código generado sea similar a otro snippet de código existente de un repositorio de código abierto que pueda tener copyright.. 

Si crees que se ha generado código que infringe tus derechos de autor, por favor contacta con nosotros en el siguiente email, y tomaremos las medidas necesarias:
wistarrcompany@gmail.com

Para ver la lista completa de las inteligencias artificiales generativas usadas, ver el archivo `credits.txt`.

## Créditos y fuentes usadas

Ver el archivo `credits.txt` para ver todas las fuentes de todos los recursos usados por terceros en este proyecto.

### Third-Party Software Notice for canvas-confetti

This project uses the following third-party software:

Library Name: canvas-confetti 

License Type: ISC License 

Copyright Notice:

Copyright (c) 2020, Kiril Vatev

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.


