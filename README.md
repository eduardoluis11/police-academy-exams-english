# police-academy-exams-english

This is my Django web app, translated into English, that lets you practice entrance exams for a police academy. It's a project for my portfolio. Made by Eduardo Salinas.

## Author

Eduardo Salinas

## Usage Instructions

1. Create a virtual environment. There are several ways to do this. I use mkvirtualenv on Windows. To install mkvirtualenv on Windows, follow these steps:

### Installing mkvirtualenv on Windows

I) **Install Python and pip**:

* Make sure you have Python installed on your machine. You can download it from [python.org](https://www.python.org/).
* During installation, check the box that says “Add Python to PATH.”
* Once installed, verify that Python and pip are working by running in the console:
```bash
  python --version
  pip --version
  ```
  

II) **Install `virtualenvwrapper-win`**:

- mkvirtualenv is part of virtualenvwrapper, but on Windows you need to install a version adapted for Windows called virtualenvwrapper-win.
- Run the following command in the terminal to install it:
```bash
    pip install virtualenvwrapper-win
```

III) **Set up the `WORKON_HOME` environment variable (optional)**:

- By default, virtual environments are stored in %USERPROFILE%\Envs. If you want to change this location:

  - Go to “Advanced system settings” > “Environment Variables.”
  - Create a new environment variable named WORKON_HOME and set the path where you want to store your virtual environments.

---

### Activating and using mkvirtualenv

I) **Create a virtual environment**:

- Use the mkvirtualenv command to create a new virtual environment. For example:
```bash
    mkvirtualenv my_env
```

II) **Activate a virtual environment**:

- To activate an existing virtual environment, use:
```bash
    workon my_env
```
  

III) **Deactivate the virtual environment**:

-When you're done working, deactivate the virtual environment with:
```bash
    deactivate
```

---

2. Install the project dependencies. To do this, first activate your virtual environment, then run the following command in the console:
```bash
pip install -r requirements.txt
```

---

3. If you're going to use a MySQL database, insert your database credentials into the .env file. Delete my MySQL credentials from that file and insert yours instead.

If you just want to run quick tests, you can use the default SQLite database and skip this step.

4. Migrate the database. Run the following command in the console:

```bash
python manage.py migrate
```

5. Create a superuser. To do this, run:

```bash
python manage.py createsuperuser
```

6. Run the server. Execute:
```bash
python manage.py runserver
```

7. Open your browser and go to `localhost:8000`. There you will see the web app.

8. To access the Django admin panel, go to `localhost:8000/admin` and log in with the superuser credentials you created in step 5.

---

## Legal

### Use of Generative AI Models

Generative AI models such as LLMs were used to help write parts of the code in this web app.

As far as we know, all generated code is original. However, there is a small risk that some generated snippets may resemble existing open-source code that could be under copyright.

If you believe any code infringes on your copyright, please contact us at the following email, and we will take the necessary action:
[wistarrcompany@gmail.com](mailto:wistarrcompany@gmail.com)

For a full list of the generative AIs used, see the file `credits.txt`.

## Credits and External Sources

See the file `credits.txt` for a full list of third-party resources and sources used in this project.


### Third-Party Software Notice for canvas-confetti

This project uses the following third-party software:

Library Name: canvas-confetti 

License Type: ISC License 

Copyright Notice:

Copyright (c) 2020, Kiril Vatev

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.


