"""
URL configuration for oposiciones_wordpress project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

""" Esto me permite usar las URLs de las distintas apps que instalaré en el proyecto de django.

To implement a password reset functionality in your Django web app where the reset link is printed to Django’s console (instead 
of being sent via email) for testing purposes, you can use Django’s built-in password reset views and forms. Django provides a 
robust password reset system out of the box, and you can customize it to output the reset link to the console by overriding the 
email-sending behavior. Here’s a step-by-step guide to implement this:

Steps to Implement Password Reset Functionality
1. Ensure Required Dependencies and Settings
Make sure your Django project has the necessary settings and apps enabled:
Installed Apps:
Ensure django.contrib.auth and django.contrib.messages are in your INSTALLED_APPS in settings_NO_USAR.py (they are included by default 
in new Django projects):

URL Configuration:
Ensure your project’s urls.py includes the auth URLs for password reset. If not, add them:

Templates:

Django expects templates for password reset forms. You’ll need to create these in your templates directory (e.g., 
templates/registration/). I’ll provide basic templates below.
Session and Messages:
Ensure you have django.contrib.messages configured for flash messages, as shown in previous responses.
2. Customize Email Sending to Print to Console
By default, Django sends password reset links via email using the EMAIL_BACKEND setting. For testing purposes, you can 
override this behavior to print the reset link to the console instead of sending an email. To do this, you’ll create a 
custom email backend that logs the email content (including the reset link) to the console.
Create a Custom Email Backend:
Create a new file email_backends.py in your app (e.g., yourapp/email_backends.py):

Update settings_NO_USAR.py:

Configure Django to use your custom email backend instead of the default email backend:
python
EMAIL_BACKEND = 'yourapp.email_backends.ConsoleEmailBackend'
This tells Django to use ConsoleEmailBackend for sending emails, which will log the email (including the reset link) to the 
console instead of sending it via email.

Enable Logging to Console:
Ensure your settings_NO_USAR.py has logging configured to output to the console. Add or update the LOGGING setting:

This ensures that logger.info() calls in ConsoleEmailBackend print to the console.
3. Create Password Reset Templates
Django looks for specific templates in templates/registration/ for password reset. Create these files in your 
templates/registration/ directory: password_reset_form.html (Form for users to request a password reset):


4. Add a Password Reset Link to Your Templates
Update your iniciar_sesion.html or home.html to include a link to the password reset page (password_reset). For 
example, add this to iniciar_sesion.html below the form:
html
<p>¿Olvidaste tu contraseña? <a href="{% url 'password_reset' %}">Restablecer contraseña</a></p>
5. Test the Password Reset Flow
Run your Django development server (python manage.py runserver).
Visit http://localhost:8000/password_reset/ in your browser.
Enter a registered email address (e.g., one from your Django users, created via registration).
Check the console output (in your terminal where the server is running) for the reset link. It will look 
something like:

Copy the reset link from the console, visit it in your browser, set a new password, and confirm the reset.
6. Ensure User Model Compatibility
Since you’re using Django’s default User model, the password reset views will work out of the box. If you had a 
custom user model, you’d need to ensure it has the required fields (email, is_active, etc.) and configure 
AUTH_USER_MODEL in settings_NO_USAR.py.

Additional Notes

Console Output Only for Testing: This setup is for development and testing. For production, you’d switch back 
to an actual email backend (e.g., EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend') and configure 
SMTP settings or use a service like SendGrid or Amazon SES.

Security: Ensure your settings_NO_USAR.py includes SESSION_COOKIE_SECURE = True and CSRF_COOKIE_SECURE = True for HTTPS, 
and use SESSION_COOKIE_HTTPONLY = True to enhance security.

Customizations: You can customize the email subject, body, or reset link behavior by overriding PasswordResetView 
or its templates. For example, modify password_reset_email.html (if needed) to change the email content, but since 
you’re using the console, the current setup prints the default message.

Error Handling: The templates include flash messages for errors (e.g., invalid email), styled with .custom-message 
as in your previous responses.

Performance: For testing, this is fine, but in production, consider rate limiting password reset requests to prevent abuse.

If you need to refine the templates, add custom logic (e.g., subscription checks before resetting), or switch to a 
production email setup later, let me know, and I’ll assist!

Los archivos de Excel con los Tests y el resto de archivos de la carpeta “media” NO SE DEBEN METER EN UNA CARPETA 
“media” EN LA WEB APP DE DJANGO. SE DEBEN METER EN OTRO SERVIDOR (como en un bucket de amazon AWS) PARA EVITAR QUE LO 
HACKEEN. Por eso es que solo se debe usar la carpeta “media” si tengo el debug mode activado.
"""

from django.contrib import admin
from django.urls import path, include

# Esto me deja usar los enlaces para que los usuarios puedan resetear sus contraseñas.
from django.contrib.auth import views as auth_views

# Esto me permite acceder a los archivos multimedia de la carpeta "media" en el modo de desarrollo
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Estas 2 URLs me enviaran a las vistas de las URLs de la app de "autenticacion".

    # # Esta URL me envía a la pagina de inicio de "/autenticacion"
    # path('autenticacion/', include('autenticacion.urls')),

    # Esto envia al usuario a la pagina de inicio de la app de autenticacion
    path('', include('autenticacion.urls')),  

    # Esto incluye todas las URLs de la app de tests de administradores
    path('tests-administradores/', include('tests_administradores.urls')),

    # Esto incluye todas las URLs de la app de Tests de Clientes
    path('tests/', include('tests_clientes.urls')),

    # Enlaces para que el usuario pueda resetear su contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


]

# Esto me deja acceder a los archivos de la carpeta "media" en el modo de desarrollo (debug mode activado)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

