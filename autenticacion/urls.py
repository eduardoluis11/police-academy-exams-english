""" URLS de la app de autenticacion. 

Aqui es donde los usuarios podran autenticarse, y posiblemente hasta registrarse.
"""

from django.urls import path
from .views import iniciar_sesion, inicio, cerrar_sesion, registrarse

urlpatterns = [

    # Vista para Registrarse
    path('sign-up/', registrarse, name='registrarse'),

    # # Primera Vista para Registrarse. esto revisa si el email del usuario existe en Wordpress
    # path('registrarse/revisar-email', registrarse, name='registrarse'),

    # Pagina para iniciar sesión
    path('login/', iniciar_sesion, name='iniciar_sesion'),

    # Página de Inicio / Home
    path('', inicio, name='inicio'),

    # Vista para Cerrar la Sesion
    path('logout/', cerrar_sesion, name='cerrar_sesion'),
]
