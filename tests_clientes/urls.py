""" URLS de la app de Tests para Clientes.

Aquí es donde los clientes podrán tomar sus tests.

# URL Configuration
Add the view to your app’s URLs.

"""

from django.urls import path
from . import views

app_name = 'tests_clientes'

urlpatterns = [

    # Vista para el Menú Principal de las distintas funcionalidades de los Tests
    path('', views.menu_principal_tests, name='menu_principal_tests'),

    # Vista para ver la Lista de Tests Disponibles para tomar
    path('lista-de-tests/', views.lista_de_tests, name='lista_de_tests'),

    # Vista para ver la Lista de Tests por Tema
    path('tests-por-tema/', views.lista_de_tests_por_tema, name='lista_de_tests_por_tema'),

    # Vista para ver la lista de todos los test que sean de tipo "por año" de todos los años.
    path('tests-por-año/', views.lista_de_tests_por_anno, name='lista_de_tests_por_anno'),

    # # Vista para ver la Lista de Años de los Tests por Año
    # path('tests-por-año/', views.lista_de_annos, name='lista_de_annos'),

    # # Vista para ver la Lista de Tests por Año del Año Seleccionado
    # path('tests-por-año/<str:year>', views.lista_de_tests_por_anno, name='lista_de_tests_por_anno'),

    # Vista para ver la Lista de Tests por Normativa
    path('tests-por-normativa/', views.lista_de_tests_por_normativa, name='lista_de_tests_por_normativa'),

    # Vista que crea una nueva sesión para el test seleccionado por el cliente. No pondré la dificultad aquí.
    path('iniciar/<str:nombre_del_test>', views.iniciar_el_test, name='iniciar_el_test'),
    # path('test/<str:nombre_del_test>/<int:difficulty>/iniciar/', views.iniciar_el_test, name='iniciar_el_test'),

    # Vista para Configurar los Ajustes del Test
    path('configurar/<int:test_id>/', views.configurar_test_predefinido, name='configurar_test'),

    # Vista para Configurar los Ajustes del Test Generado desde Cero
    path('configurar-nuevo-test-a-generar/', views.configurar_nuevo_test_a_generar,
         name='configurar_nuevo_test_a_generar'),

    # Vista para Configurar un Test por Tema desde Cero
    path('configurar-test-por-tema/', views.configure_new_test_by_topic, name='configure_new_test_by_topic'),

    # Vista con la API para obtener el número total de preguntas de un test por tipo de test
    path('get-question-count/', views.get_question_count, name='get_question_count'),

    # Vista para Tomar el Test SIN Autocorrección
    path('test/sesion/<int:session_id>/pregunta/<int:question_number>/', views.tomar_test, name='tomar_test'),

    # Vista para Tomar el Test CON Autocorrección
    path('sesion/<int:session_id>/pregunta/<int:question_number>/autocorreccion/',
         views.tomar_test_autocorregido, name='tomar_test_autocorregido'),

    # Vista para ver los Resultados del Test
    path('test/sesion/<int:session_id>/resultados/', views.resultados_del_test, name='resultados_del_test'),

    # Vista para que el Usuario pueda ver la lista de sus resultados de sus tests pasados
    path('lista-de-resultados/', views.lista_de_resultados_de_tests_pasados,
         name='lista_de_resultados_de_tests_pasados'),

    # Vista para que el Usuario pueda ver la Lista de sus tests interrumpidos
    path('tests-incompletos/', views.lista_de_tests_incompletos, name='lista_de_tests_incompletos'),

    # Vista para guardar el Tiempo Restante al Guardar y Salir de un Test
    path('save-time/', views.save_time, name='save_time'),

    # Vista para que el Usuario pueda Repasar el Test Seleccionado que haya finalizado
    path('repasar-test/<int:session_id>/pregunta/<int:question_number>/',
         views.repasar_test_finalizado,
         name='repasar_test_finalizado'),

    # Vista para que el Usuario pueda Ver las Preguntas que él haya Guardado
    path('ver-preguntas-guardadas/', views.ver_preguntas_guardadas, name='ver_preguntas_guardadas'),

    # Vista para que el Usuario pueda ver de manera detallada la Pregunta Guardada seleccionada
    path('ver-preguntas-guardadas/<int:pregunta_guardada_id>/',
         views.ver_detalles_de_pregunta_guardada_seleccionada,
         name='ver_detalles_de_pregunta_guardada_seleccionada'),

    # URL a la API para que el usuario pueda guardar una pregunta desde el front-end
    path('guardar-pregunta/', views.guardar_pregunta, name='guardar_pregunta'),

    # URL a la API para que el usuario pueda eliminar una pregunta guardada desde el front-end
    path('eliminar-pregunta-guardada/', views.eliminar_pregunta_guardada, name='eliminar_pregunta_guardada'),
]
