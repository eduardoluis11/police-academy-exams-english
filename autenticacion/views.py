from django.shortcuts import render, redirect

from django.conf import settings  # Import settings to get the AbstractUser model

from django.contrib.auth import get_user_model  # This should get my AbstractUser model from my base.py from my settings


# Esto importa todos los formularios
from .forms import EmailParaRegistrarseFormulario, ContraseñaParaRegistrarseFormulario, IniciarSesionFormulario

# This should get my AbstractUser model from my models.py file from my "autenticacion" app
from autenticacion.models import User

# Esto me permitirá hacer peticiones HTTP a la API de Wordpress y Woocommerce
import requests
from requests.auth import HTTPBasicAuth

# Esto me permitirá autenticar a los usuarios y cerrar sesión con mi custom backend de autenticacion
from django.contrib.auth import authenticate, login, logout

# Esto me permitirá coger las credenciales de Wordpress del archivo .env
import os

# Esto me muestra mensajes flash de confirmación y de error en los templates
from django.contrib import messages

# # Esto detecta errores de Validacion de Django, como el de un email repetido en la base de datos
# from django.core.exceptions import ValidationError

# Esto detecta errores de Validacion de Django, como el de si un email repetido en la base de datos
from django.db import IntegrityError

# from .backends import WooCommerceSubscriptionBackend  # Import your custom backend


""" URLS de la app de autenticacion."""

# Create your views here.

""" Vista para la página para Registrarse.

Para evitar confusiones, haré 2 templates para la funcionalidad para registrarse: una para pedirle al usuario su email 
de la web app de wordpress, y otra para que cree su nueva contraseña.

En la pagina de pedirle el email de wordpress, le dire “escribe tu email con el cual te registraste en Wistarr”. Si 
el email existe en wordpress (revisando con la Wordpress REST API), enviare al usuario a la siguiente pagina. De lo 
contrario, le diré a ese usuario que ese usuario no esta registrado en Wistarr.

Mientras tengo en la 2da pagina de registro, le diré al usuario que se cree una nueva contraseña. Esa es la que 
usara para usar la web app de django.

Le agregué el formulario de Django para Registrarse del forms.py.

To display an error message using Django's messages library when a user tries to sign up with an email that already exists in the database, you can catch the specific exception and use the messages.error function to show the error message. To handle the IntegrityError and display a user-friendly error message using Django's messages library, you can catch the IntegrityError exception and use messages.error to show the error message. Here's how you can modify your registrarse view to achieve this:

In this code, the IntegrityError exception is caught, and an appropriate error message is displayed using messages.error. This way, you avoid showing the yellow Django error message and instead show a user-friendly error message on the page.



I will call the Wordpress REST API so that, if the user inserts their email in my current form in my 
iniciar_sesion() view, the Wordpress REST API will be called for the example.com website to check if 
there's an user in that worpdress web app that has that email account. If the user exists, my django web 
app should display a message saying that the user exists; otherwise, it should say that it doesn't exist.

To implement the functionality where your Django web app calls the WordPress REST API to check if a user with a 
given email exists, you can follow this general algorithm:

Create a form submission handler in the iniciar_sesion view:

When the form is submitted, extract the email from the form data.
Make a request to the WordPress REST API to check if the user exists.
Display a message based on the response from the WordPress REST API.
Update the iniciar_sesion view to handle form submissions:

Use the requests library to make HTTP requests to the WordPress REST API.
Update the template to display messages:

Add a section in the template to display success or error messages.

Summary
Create a custom authentication backend to authenticate users based on their email and subscription ID.
Update the iniciar_sesion view to authenticate users using the custom authentication backend and log them in.
Update the Django settings to include the custom authentication backend.
Ensure you have a user model to store user information.
With this implementation, users will be able to log in to your Django web app using their email and subscription ID.

I modified the iniciar_sesion view to authenticate users using the custom authentication backend and log them in.

Usare los mensajes flash de error y confirmación de Django de la biblioteca de "messages".




To modify your custom authentication backend (WooCommerceSubscriptionBackend in backends.py) so that it assigns a password 
to the user during account creation, you’ll need to update the authenticate() method to accept the password from your 
RegistrarseFormulario and pass it to User.objects.create_user(). Since your form already includes password and 
confirmar_password fields with validation, we’ll ensure the backend uses the validated password (from password) when creating the user.
Here’s the modified version of your backends.py based on the document you provided and the RegistrarseFormulario you shared:

Explanation of Changes
Updated authenticate() Method:
I modified the authenticate() method to accept an additional password parameter (along with email).
I added a check if not email or not password: to ensure both are provided before proceeding.
When creating a user with User.objects.create_user(), I now pass the password parameter from the form, ensuring the user is 
created with a password. This password will be hashed securely by Django’s default password hasher (typically PBKDF2-SHA256).
Removed subscription_id:
Based on your document, you’ve decided to remove the subscription_id (formerly numero_del_pedido) and rely solely on checking for 
active subscriptions via the WP Swings API. The backend now focuses on verifying the email exists in WordPress and has at least 
one active subscription.
Maintained Error Handling:
The backend still returns {'error': 'El nombre de usuario o el correo electrónico ya existe en la base de datos.'} if the username 
or email already exists in Django’s database.
It returns None if the email doesn’t exist in WordPress or if there are no active subscriptions, allowing the view to show a generic 
error message.
Compatibility with RegistrarseFormulario:
The backend now assumes your RegistrarseFormulario validates the password and confirmar_password fields (ensuring they match) and 
passes the password to the backend. Your view will need to extract this password and pass it to authenticate().
Updating the registrarse View
You’ll need to update your registrarse view in views.py to pass the password to the authenticate() method. Here’s how you can modify 
it (assuming it’s based on your previous code).



Changes:
Added password = form.cleaned_data['password'] to extract the validated password from the form.
Passed password=password to backend.authenticate() alongside email.
Maintained the same error handling and message logic as before.
Notes
Password Security: Django’s create_user() method hashes the password securely, so you don’t need to worry about storing plain text. 
Users can later use this password to log in via your iniciar_sesion view (if you implement password-based login).
Form Validation: Ensure your RegistrarseFormulario’s clean() method validates that password and confirmar_password match, as shown 
in your form code. This prevents users from creating accounts with mismatched passwords.
Testing: Test the registration with:
A new email (to ensure a user is created with a password).
An existing email (to verify the “username or email already exists” error).
A non-existent email or expired subscription (to trigger the generic error).
Login Integration: If you want users to log in using their email and password (instead of email + subscription ID), update your 
iniciar_sesion view to use Django’s default authenticate() with email and password. You might need a custom backend or user model 
to support email-based login.
Let me know if you need help with the login view, testing, or any additional modifications!

Al registrarme, ya me sale el mensaje de confirmación, y me logueo como el usuario logueado
"""


def registrarse(request):
    # Variable con el mensaje que se mostrará en la página al enviar el formulario
    message = ''

    # Si el usuario envía el formulario
    if request.method == 'POST':

        # Esto crea una instancia del Formulario de Django con el Campo del Email
        emailForm = EmailParaRegistrarseFormulario(request.POST)

        # Esto crea una instancia del Formulario de Django con los 2 Campos de las Contraseñas
        passwordForm = ContraseñaParaRegistrarseFormulario(request.POST)

        # Si el formulario es válido (por razones de seguridad)
        if emailForm.is_valid() and passwordForm.is_valid():

            # This gets the username from the form
            username = emailForm.cleaned_data['username']

            # Esto coge el email del formulario
            email = emailForm.cleaned_data['email']

            password = passwordForm.cleaned_data['password']  # Get the password from the form

            # Esto intentará crear a un usuario y registrarlo
            try:
                # # Authenticate the user using the custom backend.
                # # Enviaré tanto el email como la contraseña a mi backend customizado de autenticacion.
                # user = authenticate(request, email=email, password=password)

                # This creates the new user in the database
                # new_user = settings.AUTH_USER_MODEL.objects.create_user(username, email, password)
                # User = get_user_model()
                new_user = User.objects.create_user(username, email, password)
                new_user.save()

                # This will log in the newly created user
                login(request, new_user)

                # This will render a success flash message
                messages.success(request, 'Te has registrado exitosamente.')

                # This will redirect the logged user to the home page
                return redirect('inicio')

                # # This will redirect the logged user to the home page
                # return HttpResponseRedirect(reverse("index"))

                # # Si el email del usuario es correcto
                # if user is not None:
                #
                #     login(request, user)  # Esto permite al usuario iniciar sesión
                #     return redirect('inicio')  # Redirige al usuario a la pagina de Inicio
                #
                #     # # Si el usuario esta repetido, mostrarle un mensaje de error
                #     # if user is 'usuario ya existe':
                #     #     messages.error(request, 'Ese correo electrónico ya existe en la base de datos de
                #     este sitio web. Por favor, usa otro email que hayas registrado en Wistarr.')
                #
                #     # else:
                #     # # User successfully authenticated and can be logged in
                #     # user = result
                #
                #     # Pondre un try/except por si me sale el ValueError que dice que el usuario este repetido
                #     # try:
                #
                #     # except ValueError:
                #     #     messages.error(request, 'Ese correo electrónico ya existe en la base de datos de
                #     este sitio web. Por favor, usa otro email que hayas registrado en Wistarr.')

                # else:  # Si el usuario no existe o tiene una suscripcion caducada, se le muestra un mensaje de error
                #     messages.error(request,
                #                    "Ese email no existe en Wistarr, o tu suscripción no está activa. Por f
                #                    avor, verifica que hayas escrito correctamente tu email y revisa el estado de
                #                    tu suscripción, o contacta al administrador para más información.")

                # message = 'Ese email no existe en Wistarr, o tu suscripción no está activa.'
                # message += '<br>Por favor, verifica que hayas escrito correctamente tu email y revisa el estado
                # de tu suscripción, o contacta al administrador para más información.'

            # Si el email ya existe en la base de datos de Django y ya esa cuenta esta creada, mostrar un mensaje de
            # error.

            # Esto evita que se cree el mismo usuario 2 veces en Django.
            # This will print an error if the user types a username that was taken by someone else.
            except IntegrityError:

                # Si el email ya existe, mostrar un mensaje de error
                messages.error(request,
                               'Error: Ese correo electrónico o nombre de usuario ya existe en la base de datos de este sitio web. Por favor, usa otro email que hayas registrado en Wistarr.'
                               )

                # except ValidationError as e:

            # # Get WordPress credentials from environment variables
            # wordpress_username = os.environ.get('WORDPRESS_USERNAME')
            # wordpress_app_password = os.environ.get('WORDPRESS_APP_PASSWORD')

            # # Get the URL of the WordPress website uploaded in the hosting server from environment variables
            # wordpress_base_url = os.environ.get('WORDPRESS_BASE_URL')

            # # Consumer Secret de la API de WP Swings de Woocommerce
            # wp_swings_consumer_secret = os.environ.get('WP_SWINGS_SUBSCRIPTIONS_CONSUMER_SECRET')

            # # Esto revisa si el email escrito existe en la web app de Wordpress llamando a una API
            # response = requests.get(
            #     f'{wordpress_base_url}/wp-json/wp/v2/users?search={email}',
            #     auth=HTTPBasicAuth(wordpress_username, wordpress_app_password)
            # )

            # # Esto revisa si se pudo acceder correctamente a la Wordpress REST API
            # if response.status_code == 200:
            #     users = response.json()
            #     if users:

            #         # Extract the username of the first user in the response from the API call
            #         username = users[0]['name']

            #         # Esto concatena el nombre de usuario del usuario extraido de la llamada a la API
            #         message = f'El usuario existe.\n Nombre de usuario: {username}\n'

            #         # Make a request to the WP Swings API to get subscription data
            #         wp_swings_response = requests.get(
            #             f'{wordpress_base_url}/wp-json/wsp-route/v1/wsp-view-subscription?consumer_secret={wp_swings_consumer_secret}'
            #         )

            #         # Si pudiste conectarte correctamente a la API de WP Swings
            #         if wp_swings_response.status_code == 200:

            #             # Esto extrae los datos de todas las suscripciones de la respuesta de la API de WP Swings
            #             wp_swings_data = wp_swings_response.json()

            #             # Check if there's a subscription with the specified parent_order_id and username
            #             suscripcion_encontrada = False

            #             # Esto revisa todas las suscripciones, y ve si hay alguna que tenga el numero de pedido y usuario especificado.
            #             # Todas las Suscripciones se guarda en el campo "data" de todo el JSON extraido.
            #             for suscripcion in wp_swings_data["data"]:

            #                 # # DEBUGGEO: esto imprime cada entrada del JSON extraido de la API de WP Swings
            #                 # message += f'\nDatos de suscripción: {entry}'

            #                 # Si se encuentra una suscripción que cumpla con esos 2 requisitos, se imprimen los datos de esa suscripcion
            #                 if suscripcion['parent_order_id'] == numero_del_pedido and suscripcion['user_name'].lower() == username.lower():
            #                     message += f'<br>Datos de suscripción: {suscripcion}'
            #                     suscripcion_encontrada = True

            #                     # Esto revisa si la suscripcion está activa, pendiente o caducada

            #                     if suscripcion['status'] == 'active':   # Si está activa, puedes iniciar sesión
            #                         message += '<br>Tu suscripción está activa. Iniciarás sesión en un momento.'

            #                     # Si la suscripción está pendiente o caducada, no podrás iniciar sesión
            #                     elif suscripcion['status'] == 'pending':
            #                         message += '<br>Lo sentimos, pero tu suscripción está marcada como "pendiente". No puedes iniciar sesión. Contacta al administrador para más información.'
            #                     else:
            #                         message += '<br>Lo sentimos, pero tu suscripción ha caducado. No puedes iniciar sesión. Contacta al administrador para más información.'
            #                     # Fin del snippet que revisa el estado de la suscripción

            #                     # Esto termina de iterar el bucle for que itera las suscripciones
            #                     break

            #             if not suscripcion_encontrada: # Si no encuentra la suscripcion con esos datos, se imprime un mensaje de error
            #                 message += '<br>El número de pedido no existe o no coincide con el nombre de usuario.'

            #             # # Esto concatena los datos de todas las suscripciones a la variable de mensaje
            #             # message += f'\nDatos de suscripción: {wp_swings_data}'

            #         else:   # Esto muestra un mensaje de error si no se pudo acceder a la API de WP Swings

            #             # Esto concatena un mensaje de error a la variable de mensaje
            #             message += '<br>Error al conectar con la API de WP Swings.'

            #     else:
            #         message = 'El usuario no existe.'

            # else:   # Esto muestra un mensaje de error si no se pudo acceder a la API de Wordpress
            #     message = 'Error al conectar con la API de WordPress.'

        else:
            # If the form is invalid, show a generic form error message
            messages.error(request, 'Por favor, corrige los errores en el formulario.')

    else:  # Esto renderiza el formulario si no se ha enviado el formulario
        # Esto crea una instancia del Formulario con el Email para Registrarse
        emailForm = EmailParaRegistrarseFormulario()

        # Esto crea una instancia del Formulario con las Contraseñas para Registrarse
        passwordForm = ContraseñaParaRegistrarseFormulario()

    # Esto siempre renderiza la pagina de Inicio de Sesion con el formulario de Inicio de Sesion
    return render(request, 'autenticacion/registrarse.html', {
        'emailForm': emailForm,
        'passwordForm': passwordForm,
        'message': message,
    })


""" Vista que renderiza la pagina de Inicio de Sesion.

Le agregué el formulario de Django de Inicio de Sesión del forms.py.

I will call the Wordpress REST API so that, if the user inserts their email in my current form in my 
iniciar_sesion() view, the Wordpress REST API will be called for the example.com website to check if 
there's an user in that worpdress web app that has that email account. If the user exists, my django web 
app should display a message saying that the user exists; otherwise, it should say that it doesn't exist.

To implement the functionality where your Django web app calls the WordPress REST API to check if a user with a 
given email exists, you can follow this general algorithm:

Create a form submission handler in the iniciar_sesion view:

When the form is submitted, extract the email from the form data.
Make a request to the WordPress REST API to check if the user exists.
Display a message based on the response from the WordPress REST API.
Update the iniciar_sesion view to handle form submissions:

Use the requests library to make HTTP requests to the WordPress REST API.
Update the template to display messages:

Add a section in the template to display success or error messages.

To implement login functionality in your Django web app where users provide their email and password, and you verify both their 
Django credentials and their active subscription status via the WP Swings API, you have two main options: modify your backends.py 
to include this logic in a custom authentication backend, or handle it directly in a view in views.py. Let’s evaluate both 
approaches and recommend the best one for your use case.



Para evitar problemas y futuros bugs, pondré el snippet que chequea si tienes una cuenta en django y si tienes 
una suscripción activa directamente en el view de iniciar_sesion(). NO creare un nuevo backend para evitar problemas.

Handle Login Logic Directly in views.py
If you prefer not to create a new backend and want to keep all login logic in the view, you can implement the same functionality 
in the iniciar_sesion view without modifying backends.py. This approach duplicates some logic but keeps WooCommerceSubscriptionBackend 
unchanged.

Steps:
Update iniciar_sesion View in views.py:
Use the standalone login logic from my previous response (Option 2). Here’s the relevant code (unchanged from before):

Keep backends.py Unchanged:
Leave WooCommerceSubscriptionBackend exactly as it is in your document for registration.

The error you're encountering, ValueError: You have multiple authentication backends configured and therefore must provide the 
backendargument or set thebackend attribute on the user, occurs because Django requires you to explicitly specify which authentication 
backend to use when logging in a user if you have multiple backends configured in AUTHENTICATION_BACKENDS. This is a safeguard to prevent 
ambiguity when multiple backends could potentially authenticate a user.

Since you want to log the user in using Django’s default ModelBackend (instead of your custom WooCommerceSubscriptionBackend or WooCommerceLoginBackend), 
you need to explicitly specify the backend when calling login().

Explanation of Changes
Explicit Backend Specification:
I added backend='django.contrib.auth.backends.ModelBackend' to you login() call. This tells Django to use only the default ModelBackend for authentication
 and session management, bypassing your custom backends (WooCommerceSubscriptionBackend).

This ensures Django doesn’t try to use your custom backends, which could attempt to create users or check subscriptions in unintended ways.

Subscription Check After Authentication:
Since you want to verify an active subscription before allowing login (even with correct Django credentials), I added logic after authenticate() 
fails to check the WP Swings API. If the user exists in Django but authentication fails (e.g., due to no active subscription), the view checks the 
subscription status manually.

This keeps the subscription check in the view (as you requested) but ensures the login uses ModelBackend for basic email/password authentication.

Error Handling:
The generic error message (“Tu email no existe en Wistarr, o tu suscripción ha caducado…”) is used for all failure cases, maintaining security by not
 revealing specific reasons (e.g., wrong password vs. expired subscription).

No Changes to Backends:
Your WooCommerceSubscriptionBackend remains unchanged, ensuring it’s only used for registration (e.g., when called from registrarse).

I will use the “authenticate” function to check if a username and its respective password exist inside the database 
(source: https://docs.djangoproject.com/en/dev/topics/auth/default/ ). 

BOOKMARK.
MODIFICAR: NO DEBO LOGUEARME A WORDPRESS PARA LOGUEARME.
"""


def iniciar_sesion(request):
    # Variable con el mensaje que se mostrará en la página al enviar el formulario
    message = ''

    # Si el usuario envía el formulario
    if request.method == 'POST':

        # Esto crea una instancia del Formulario de Django
        form = IniciarSesionFormulario(request.POST)

        # Si el formulario es válido (por razones de seguridad)
        if form.is_valid():

            username = form.cleaned_data['username']  # Esto coge el nombre de usuario del formulario
            password = form.cleaned_data['password']  # Esto coge la contraseña del formulario

            # email = form.cleaned_data['email']  # Esto coge el email del formulario

            # Verify Django credentials
            try:

                # This will check if the username and password exist in the database
                check_user = authenticate(request, username=username, password=password)

                # If the user exists, they will be logged in
                if check_user is not None:
                    login(request, check_user)

                    # This will redirect the logged user to the home page
                    return redirect('inicio')
                else:
                    # If the user doesn't exist, show an error message
                    messages.error(request, 'You typed an incorrect username and/or password.')

                # # Intento buscar al usuario usando su email en la base de datos de Django
                # user = User.objects.get(email=email)
                #
                # if user.check_password(password):
                #     # Step 2: Check WordPress and subscription status
                #     wordpress_username = os.environ.get('WORDPRESS_USERNAME')
                #     wordpress_app_password = os.environ.get('WORDPRESS_APP_PASSWORD')
                #     wordpress_base_url = os.environ.get('WORDPRESS_BASE_URL')
                #     wp_swings_consumer_secret = os.environ.get('WP_SWINGS_SUBSCRIPTIONS_CONSUMER_SECRET')
                #
                #     response = requests.get(
                #         f'{wordpress_base_url}/wp-json/wp/v2/users?search={email}',
                #         auth=HTTPBasicAuth(wordpress_username, wordpress_app_password)
                #     )
                #
                #     if response.status_code == 200:
                #         users = response.json()
                #         if users:
                #             username = users[0]['name']
                #
                #             wp_swings_response = requests.get(
                #                 f'{wordpress_base_url}/wp-json/wsp-route/v1/wsp-view-subscription?consumer_secret={wp_swings_consumer_secret}'
                #             )
                #
                #             if wp_swings_response.status_code == 200:
                #                 wp_swings_data = wp_swings_response.json()
                #
                #                 has_active_subscription = False
                #                 for subscription in wp_swings_data["data"]:
                #                     if (subscription['user_name'].lower() == username.lower() and
                #                             subscription['status'] == 'active'):
                #                         has_active_subscription = True
                #                         break
                #
                #                 if has_active_subscription:
                #
                #                     # Esto hará que el usuario inice sesión. Usaré el backend por defecto de Django para autenticarme.
                #                     # Si no especifico el backend que voy a usar, me saldrá un error de Django.
                #                     login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                #
                #                     messages.success(request, '¡Inicio de sesión exitoso!')
                #                     return redirect('inicio')
                #                 else:
                #                     messages.error(request,
                #                                    'Tu email y/o contraseña son incorrectos, o tu suscripción ha caducado.')
                #             else:
                #                 messages.error(request,
                #                                'Hubo un error al verificar tu suscripción. Por favor, inténtalo de nuevo más tarde.')
                #         else:
                #             messages.error(request,
                #                            'Tu email y/o contraseña son incorrectos, o tu suscripción ha caducado.')
                #     else:
                #         messages.error(request,
                #                        'Hubo un error al verificar tus credenciales. Por favor, inténtalo de nuevo más tarde.')
                # else:
                #     messages.error(request, 'Tu email y/o contraseña son incorrectos, o tu suscripción ha caducado.')

                # # Authenticate the user using the custom backend
                # user = authenticate(request, email=email, password=password)

                # # Si el usuario y el número de pedido son correctos
                # if user is not None:

                #     login(request, user)    # Esto permite al usuario iniciar sesión
                #     return redirect('inicio')  # Redirige al usuario a la pagina de Inicio
                # else:   # Si el usuario no existe, se le muestra un mensaje de error
                #     message = 'Nombre de usuario o contraseña incorrectos, o tu suscripción puede estar caducada'

            except User.DoesNotExist:   # If the user doesn't exist

                messages.error(request, 'You typed an incorrect username and/or password.')

        else:   # If the form is invalid,
            # Show a generic form error message
            messages.error(request, 'Por favor, corrige los errores en el formulario.')

    else:  # Esto renderiza el formulario si no se ha enviado
        # Esto crea una instancia del Formulario de Django de  Inicio de Sesion
        form = IniciarSesionFormulario()

    # Esto siempre renderiza la pagina de Inicio de Sesion con el formulario de Inicio de Sesion
    return render(request, 'autenticacion/iniciar_sesion.html', {
        'form': form,
        'message': message,
    })


""" Vista para Cerrar la Sesión del usuario autenticado.
"""


def cerrar_sesion(request):
    # Logs out the current user and redirects to the homepage or login page.
    logout(request)

    return redirect('inicio')  # Redirect to the homepage (or 'iniciar_sesion' if preferred)


""" Vista que renderiza la pagina de Inicio / Home.
"""


def inicio(request):
    return render(request, 'autenticacion/inicio.html')
