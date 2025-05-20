from django import forms

""" Formulario con el Campo del Nombre de Usuario y el Email para Registrarse.

Solo le pediré al usuario su email de su cuenta de wordpress. No le pedire el numero de su pedido, ya que puedo revisar
todos los pedidos de ese usuario usand ola AP de WP Swings, y revisare si tiene alguna suscripcion activa. De ser así, le
dejare´al usuario registrarse a la web app.

Here’s an updated version of your RegistrarseFormulario class in forms.py that adds two new fields: one for a password and another for 
confirming that password. I’ll include labels, placeholders, and basic validation to ensure the passwords match.

New Fields:
password: A CharField with a PasswordInput widget to hide the input (shows asterisks or dots). It has a label “Contraseña” and a placeholder 
“Contraseña”.

confirm_password: Another CharField with a PasswordInput widget, labeled “Confirmar Contraseña” and with a placeholder “Confirma tu contraseña”.

Validation:
I added a clean() method to the form to check if the password and confirm_password fields match. If they don’t, it raises a ValidationError with 
a Spanish error message: “Las contraseñas no coinciden. Por favor, inténtalo de nuevo.”

This validation ensures users enter matching passwords before the form is processed.

Attributes:
Both password fields use max_length=128 (a common length for password fields, though you can adjust it based on your needs).

The PasswordInput widget ensures the input is masked for security.

Despues dividiré el formulario de Registrarse en 2 formularios: uno para el email de wordpress, y otro solo para las contraseñas. 
Luego, pondré un mensaje diciendo “pon tu email de Wistarr aqui”, y renderizo con Jinja el formulario del email. Despues, pondré 
un mensaje diciendo “create una nueva contraseña que sea distinta a la de Wistarr”, y luego renderizaré el formulario que solo 
tendra la contraseña y el campo de confirmar la contraseña.
	
Sino, es que la gente pensará que tienen que poner su contraseña de Wordpress. O pueden pensar que pueden poner un email cualquiera 
para poder crearse su cuenta.

"""


class EmailParaRegistrarseFormulario(forms.Form):

    # Username field
    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',  # Bootstrap class for input styling
        }))

    # Email
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'form-control',  # Bootstrap class for input styling
        }))

    # numero_del_pedido = forms.CharField(label='Número del Pedido', max_length=255,
    # widget=forms.TextInput(attrs={'placeholder': 'Número del Pedido'}))


""" Formulario on el Campo de la Contraseña para Registrarse.

Este formulario solo tendrá el campo de la Contraseñay y el campo para Confirmar la Contraseña.
"""


class ContraseñaParaRegistrarseFormulario(forms.Form):
    password = forms.CharField(
        label='Contraseña',
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-control',  # Bootstrap class for input styling
        })
    )
    confirmar_password = forms.CharField(
        label='Confirmar Contraseña',
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirma tu contraseña',
            'class': 'form-control',  # Bootstrap class for input styling
        })
    )

    def clean(self):
        """
        Validate that the password and confirmar_password fields match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password and confirmar_password and password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden. Por favor, inténtalo de nuevo.")

        return cleaned_data


""" Formulario para Iniciar Sesion. 

Solo le pediré al usuario el email, y su contraseña de su cuenta de la web app de Django para que puedan iniciar sesión.

Creo que modificaré la forma de loguearte para que sea nombre de usuario en lugar de email, ya que AbstractUser te 
deja loguearte con nombre de usuario por defecto, NO por email. E igual, que como te autentiques no es lo importante 
en mi portfolio. Lo importante es la función de tomar los tests en sí.
"""


class IniciarSesionFormulario(forms.Form):

    # Username Field.
    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',  # Bootstrap class for input styling
        }))

    # email = forms.EmailField(
    #     label='Email',
    #     max_length=254,
    #     widget=forms.EmailInput(attrs={
    #         'placeholder': 'Email',
    #         'class': 'form-control',  # Bootstrap class for input styling
    #     }))

    password = forms.CharField(
        label='Contraseña',
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-control',  # Bootstrap class for input styling
        }))
