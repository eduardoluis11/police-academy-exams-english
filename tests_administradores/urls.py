""" URLS de la app de Tests para Administradores. 

Aqui es donde los administradores podrán crear y gestionar los tests de oposiciones.

# URL Configuration
Add the view to your app’s URLs.

"""

from django.urls import path
from . import views

app_name = 'tests_administradores'

urlpatterns = [

    # Vista para Subir y Procesar archivos de Excel con Tests / Exámenes para escanearlos y así extraerles los datos
    path('subir-tests/', views.upload_and_import_exams, name='upload_and_import_exams'),

    # Vista para Crear un Nuevo Test Manualmente sin Subir un Archivo de Excel
    path('crear-nuevo-test/', views.crear_nuevo_test_sin_subir_un_archivo,
         name='crear_nuevo_test_sin_subir_un_archivo'),

    # Vista para Confirmar Si Quieres Eliminar un Test. Tengo que poner "test_id" si pongo "test_id" en el view
    path('confirmar-eliminar-test/<int:test_id>/', views.confirmar_eliminar_test, name='confirmar_eliminar_test'),

    # Vista para Eliminar un Test
    path('eliminar-test/<int:test_id>/', views.eliminar_test, name='eliminar_test'),

    # Vista para Editar un Test
    path('editar-test/<int:test_id>/', views.editar_test, name='editar_test'),

    # Vista para Buscar alguna pregunta en específico
    path('buscador-de-preguntas/', views.buscador_de_preguntas, name='buscador_de_preguntas'),

    # # Vista para Registrarse
    # path('registrarse/', registrarse, name='registrarse'),

    # # # Primera Vista para Registrarse. esto revisa si el email del usuario existe en Wordpress
    # # path('registrarse/revisar-email', registrarse, name='registrarse'),

    # # Pagina para iniciar sesión
    # path('iniciar-sesion/', iniciar_sesion, name='iniciar_sesion'),

    # # Página de Inicio / Home
    # path('', inicio, name='inicio'),

    # # Vista para Cerrar la Sesion
    # path('cerrar-sesion/', cerrar_sesion, name='cerrar_sesion'),
]