from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
import requests
from requests.auth import HTTPBasicAuth
import os

""" Backend de Autenticacion por Email.

Ya el número del pedido no lo necesito. Puedo simplemente usar la API de WP Swings para revisar si el usuario
seleccionado tiene alguna suscripcion activa. Si la tiene, podrá registrarse en la web app de Django. De lo contrario, 
le mostraré un mensaje de error.

Pondré un mensaje de error genérico que diga “tu email no existe o tu suscripción ha caducado. Por favor, verifica que 
hayas escrito correctamente tu email y revisa el estado de tu suscripción, o contacta al administrador para más 
información.” Así, un hacker no sabrá si escribió un email erróneo o si la suscripción de ese cliente está caducada. 
Así, el hacker no sabrá cuáles emails están registrados en Wistarr, y cuales no. Esto mejora la seguridad de la web 
app.

To modify the authentication backend so that it only creates a user and displays an error if the username or email already 
exists in the Django database, you can update the authenticate method to check for existing users and raise an error if they 
already exist.

To implement an authentication system in your Django web app that allows users to log in using their email and 
subscription ID (without a password), you can follow this general algorithm:

General Algorithm
Create a custom authentication backend:

Implement a custom authentication backend that authenticates users based on their email and subscription ID.
Update the iniciar_sesion view:

Modify the view to authenticate users using the custom authentication backend.
Log in the user if authentication is successful.
Update the Django settings:

Add the custom authentication backend to the AUTHENTICATION_BACKENDS setting.
Create a user model or use the existing one:

Ensure you have a user model to store user information.

Create a custom authentication backend
Create a new file backends.py in your autenticacion app and implement the custom authentication backend.

Step 2: Update the iniciar_sesion view
Modify the iniciar_sesion view to authenticate users using the custom authentication backend and log them in:

Step 3: Update the Django settings
Add the custom authentication backend to the AUTHENTICATION_BACKENDS setting in your settings_NO_USAR.py file


GitHub Copilot
To implement an authentication system in your Django web app that allows users to log in using their email and subscription ID (without a password), you can follow this general algorithm:

General Algorithm
Create a custom authentication backend:

Implement a custom authentication backend that authenticates users based on their email and subscription ID.
Update the iniciar_sesion view:

Modify the view to authenticate users using the custom authentication backend.
Log in the user if authentication is successful.
Update the Django settings:

Add the custom authentication backend to the AUTHENTICATION_BACKENDS setting.
Create a user model or use the existing one:

Ensure you have a user model to store user information.
Step-by-Step Implementation
Step 1: Create a custom authentication backend
Create a new file backends.py in your autenticacion app and implement the custom authentication backend:

Step 2: Update the iniciar_sesion view
Modify the iniciar_sesion view to authenticate users using the custom authentication backend and log them in:

Step 3: Update the Django settings
Add the custom authentication backend to the AUTHENTICATION_BACKENDS setting in your settings_NO_USAR.py file:

Step 4: Create a user model or use the existing one
Ensure you have a user model to store user information. You can use Django's default User model or create a custom user model if needed.


To call the WordPress REST API using Basic Authentication with your WordPress username and app password, you 
need to include the credentials in the request headers. You can use the requests library to make the HTTP 
request with Basic Authentication.

Yes, it is possible to hide the URL in an environment variable for security purposes. You can store the URL in your 
.env file and then retrieve it in your Django view.

Then, from the fetched user that was gotten from the wordpress REST API, find the username of the user whose email was 
fetched from the "response = requests.get( f'{wordpress_base_url}/wp-json/wp/v2/users?search={email}'" API call. Then, 
concatenate the username of the fetched user to the "el usuario existe" message. To do this, you'll have to

    1) Extract the username from the API response by accessing the username field of the first user in the response.
    2) Concatenate the username to the message to display the username along with the "El usuario existe" message.

Then, I'll get the consumer secret from WP Swings from my environment variables, and, if the consumer exists, list all the 
JSON data obtained from that API call. The API URL Endpoint that you will have to call is 
"example.com/wp-json/wsp-route/v1/wsp-view-subscription?consumer_secret=API_KEY_de_WP_Swings_Sin_Comillas".

To get the consumer secret from WP Swings from your environment variables and list all the JSON data obtained from the API 
call if the consumer exists, you can follow these steps:

1) Store the WP Swings consumer secret in an environment variable.
2) Update the iniciar_sesion view to include the consumer secret in the API call.
3) List all the JSON data obtained from the API call.

Now, I made a new "if" statement within the selected "if" statement. In it, check that in there's an entry in the extracted 
JSON data that has the "parent_order_id" field equal to the number typed by the user from the "numero_del_pedido" form field; 
and check that the username from the "user_name" field from that entry from that JSON response is equal to the lower caps 
version of the user's username that I extracted earlier. If it is, print that entry from the WP Swings JSON response. Otherwise, 
print an error message saying that that order number doesn't exist.

To add the new if statement within the selected if statement, you need to check if there is an entry in the extracted JSON data 
that has the parent_order_id field equal to the number typed by the user from the numero_del_pedido form field, and check that 
the username from the user_name field from that entry is equal to the lowercased version of the user's username extracted earlier. 
If both conditions are met, print that entry from the WP Swings JSON response. Otherwise, print an error message saying that the 
order number doesn't exist.

Now, within the "if" statement that fetches the subscription of the current user, look up the "status" field of the "suscripcion" 
variable in this "for" loop. if the status is equal to "active", concatenate in the "message" variable a string that says 
"Tu suscripción está activa. Iniciarás sesión en un momento." Meanwhile, if the "status" says "pending", concatenate the message 
"Lo sentimos, pero tu suscripción esta marcada como 'pendiente'. No puedes iniciar sesión. Contacta al administrador para más 
información." Finally, if the status is "expired" or anything else, print the message "Lo sentimos, pero tu suscripción ha 
caducado. No puedes iniciar sesión. Contacta al administrador para más información."

To implement the requested functionality, you need to update the if statement within the for loop to check the status field of 
the suscripcion variable. Based on the value of the status field, concatenate the appropriate message to the message variable.

With this implementation, users will be able to log in to your Django web app using their email and subscription ID.




To modify your custom authentication backend (WooCommerceSubscriptionBackend in backends.py) so that it assigns a password to the user during account creation, 
you’ll need to update the authenticate() method to accept the password from your RegistrarseFormulario and pass it to User.objects.create_user(). Since your 
form already includes password and confirmar_password fields with validation, we’ll ensure the backend uses the validated password (from password) when creating the user.

Here’s the modified version of your backends.py based on the document you provided and the RegistrarseFormulario you shared:

Explanation of Changes
Updated authenticate() Method:
I modified the authenticate() method to accept an additional password parameter (along with email).
I added a check if not email or not password: to ensure both are provided before proceeding.
When creating a user with User.objects.create_user(), I now pass the password parameter from the form, ensuring the user is created with a password. This password will 
be hashed securely by Django’s default password hasher (typically PBKDF2-SHA256).
Removed subscription_id:
Based on your document, you’ve decided to remove the subscription_id (formerly numero_del_pedido) and rely solely on checking for 
active subscriptions via the WP Swings API. The backend now focuses on verifying the email exists in WordPress and has at least one active subscription.
Maintained Error Handling:
The backend still returns {'error': 'El nombre de usuario o el correo electrónico ya existe en la base de datos.'} if the username or 
email already exists in Django’s database.
It returns None if the email doesn’t exist in WordPress or if there are no active subscriptions, allowing the view to show a generic 
error message.
Compatibility with RegistrarseFormulario:
The backend now assumes your RegistrarseFormulario validates the password and confirmar_password fields (ensuring they match) and passes the password 
to the backend. Your view will need to extract this password and pass it to authenticate().
Updating the registrarse View
You’ll need to update your registrarse view in views.py to pass the password to the authenticate() method. Here’s how you can modify it (assuming 
it’s based on your previous code):

Changes:
Added password = form.cleaned_data['password'] to extract the validated password from the form.
Passed password=password to backend.authenticate() alongside email.
Maintained the same error handling and message logic as before.
Notes
Password Security: Django’s create_user() method hashes the password securely, so you don’t need to worry about storing plain text. Users 
can later use this password to log in via your iniciar_sesion view (if you implement password-based login).
Form Validation: Ensure your RegistrarseFormulario’s clean() method validates that password and confirmar_password match, as shown in your form 
code. This prevents users from creating accounts with mismatched passwords.
Testing: Test the registration with:
A new email (to ensure a user is created with a password).
An existing email (to verify the “username or email already exists” error).
A non-existent email or expired subscription (to trigger the generic error).
Login Integration: If you want users to log in using their email and password (instead of email + subscription ID), update your iniciar_sesion 
view to use Django’s default authenticate() with email and password. You might need a custom backend or user model to support email-based login.
Let me know if you need help with the login view, testing, or any additional modifications!
"""

class WooCommerceSubscriptionBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        # Get WordPress credentials from environment variables
        wordpress_username = os.environ.get('WORDPRESS_USERNAME')
        wordpress_app_password = os.environ.get('WORDPRESS_APP_PASSWORD')

        # Get the URL of the WordPress website uploaded in the hosting server from environment variables
        wordpress_base_url = os.environ.get('WORDPRESS_BASE_URL')

        # Consumer Secret de la API de WP Swings de Woocommerce
        wp_swings_consumer_secret = os.environ.get('WP_SWINGS_SUBSCRIPTIONS_CONSUMER_SECRET')

        # Check if email and password are provided
        if not email or not password:
            return None

        # Esto revisa si el email escrito existe en la web app de Wordpress llamando a una API.
        # Cogeré las credenciales del usuario administrador de WordPress para poder ver la lista de usuarios de la 
        # web app de Wordpress usando "auth=HTTPBasicAuth".
        response = requests.get(
            f'{wordpress_base_url}/wp-json/wp/v2/users?search={email}',
            auth=HTTPBasicAuth(wordpress_username, wordpress_app_password)
        )

        # Esto revisa si se pudo acceder correctamente a la Wordpress REST API
        if response.status_code == 200:
            users = response.json()
            if users:

                # Extract the username of the first user in the response from the API call
                username = users[0]['name']
                # Make a request to the WP Swings API to get subscription data
                wp_swings_response = requests.get(
                    f'{wordpress_base_url}/wp-json/wsp-route/v1/wsp-view-subscription?consumer_secret={wp_swings_consumer_secret}'
                )

                # Si pudiste conectarte correctamente a la API de WP Swings
                if wp_swings_response.status_code == 200:

                    # Esto extrae los datos de todas las suscripciones de la respuesta de la API de WP Swings
                    wp_swings_data = wp_swings_response.json()

                    # Esto revisa todas las suscripciones, y ve si hay alguna que tenga el usuario especificado, y que está activa.
                    # Todas las Suscripciones se guarda en el campo "data" de todo el JSON extraido.
                    for suscripcion in wp_swings_data["data"]:

                        # # DEBUGGEO: esto se me deberia imprimir 4 veces porque tengo 4 suscipciones.
                        # # SOLO SE ESTA IMPRIMIENDO UNA SOLA VEZ.
                        # print("Esto se debe imprimir una vez por cada suscripcion existente.")

                        # # DEBUGGEO: quiero imprimir todos los datos de la suscripcion para ver cual suscripcion se esta agarrando.
                        # print(suscripcion)

                        # Revisaré todas las suscripciones del usuario seleccionado para ver si tiene alguna activa

                        # Si se encuentra una suscripción que cumpla con los 2 requisitos anteriormente seleccionados
                        if suscripcion['user_name'].lower() == username.lower() and suscripcion['status'] == 'active':

                            # # DEBUGGEO. Esto se me debería imprimir, porque mi usuario si tiene una suscripcion activa.
                            # # NO SE ESTA IMPRIMIENDO.
                            # print("El usuario tiene una suscripcion activa.")

                            # # Check if the user already exists in Django
                            # if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():

                            #     # # Si ya existe el usuario en Django, se lanza un error
                            #     # return 'usuario ya existe'
                            
                            #     # return {'error': 'Ese correo electrónico ya existe en la base de datos de este sitio web. Por favor, usa otro email que hayas registrado en Wistarr.'}


                            #     raise ValueError("El nombre de usuario o el correo electrónico ya existe en la base de datos.")
                            
                            # Se crea al usuario en Django. Le asignaré la contraseña que escribió el usuario en el formulario.
                            user = User.objects.create_user(username=username, email=email, password=password)

                            # user, created = User.objects.get_or_create(username=username, email=email)

                            # Esto devuelve / envía al usuario al view de registrarse()
                            return user

        #                     # if suscripcion['parent_order_id'] == subscription_id and suscripcion['user_name'].lower() == username.lower():

        #                     # # DEBUGGEO: Esto me permite ver si al menos detectó que el usuario y el numero de pedido escritos existen en wordpress
        #                     # print("La suscripcion existe para el usuario seleccionado")

        #                     # Check the status of the subscription

        #                     # # Si la suscripción está activa, se crea el usuario en Django
        #                     # if suscripcion['status'] == 'active':

        #                     #     # # DEBUGGEO: Esto me permite ver si al menos detectó que la suscripcion esta activa
        #                     #     # print("La suscripcion esta activa. Puedes crearte tu usuario y/o loguearte.")

        #                     #     # Get or create the user in Django
        #                     #     user, created = User.objects.get_or_create(username=username, email=email)
        #                     #     return user
                            
        #                 # Si la suscripción no está activa (caducada o pendiente), o si el usuario no existe, se devuelve None
        #                 else:

        #                     # # DEBUGGEO: Esto me indica que el usuario no puede loguearse porque la suscripcion esta caducada
        #                     # print("Lo sentimos, pero tu suscripción está caducada. No puedes loguearte.")
        #                     return None
        
        # Si el email no existe, o el usuario no tiene una suscripcion activa, se devuelve "None" para mostrar 
        # un mensaje de error.
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None