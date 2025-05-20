""" Vistas para la app de tests para clientes.

We’ll create views to handle starting the exam, displaying questions, saving answers, and showing results.

## Why:
start_exam: Initiates a new session and redirects to the first question.

take_exam: Handles displaying questions, saving answers, and navigation.

exam_results: Calculates and displays the results.

exam_list: Shows available exams to start.

"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone

# Esto importa mis modelos de la app de tests para clientes
from .models import SesionDelTest, RespuestaDelUsuario, PreguntaGuardadaPorElUsuario

# Formularios de Django de esta app ("test_clientes")
from .forms import (ConfigurarTestSinIncluirPreguntasForm, ConfigurarNuevoTestAGenerarForm,
                    NumeroDePreguntasARealizarFormulario, ConfigureNewTestByTopicForm, ConfigureNewTestByRegulationForm)

# Esto importa mis modelos de la app de tests para administradores
from tests_administradores.models import PreguntaDelTest, Test

from django.contrib import messages
import json

from random import seed
from datetime import datetime

# Decorator para forzar al usuario a usar un POST request
from django.views.decorators.http import require_POST

# Me deja coger varios registros de un solo modelo al mismo tiempo (para agarrar múltiples temas de PreguntaDelTest)
from django.db.models import Q

# Create your views here.

""" Vistas para la app de tests para clientes.
"""

""" Vista para el Menú Principal o "Hub" de los Tests.

Desde aquí, los clientes podrán ver los distintos enlaces a las distintas funcionalidades de los tests. Esto incluye
las distintas listas de tests, y los resultados de los tests que el cliente ha tomado.
"""


@login_required(login_url='iniciar_sesion')
def menu_principal_tests(request):
    return render(request, 'tests_clientes/menu_principal_de_tests.html')


""" Vista con la Lista de Tests por Tema.

Cuando entre a esta vista me debe salir la lista de todos los tests, pero con un título que diga "tema 1", y ahí salen 
todos los tests del tema 1; luego otro título que diga "tema 2", y salgan todos los tests del tema 2, y así 
sucesivamente.

Es posible que reuse el template de esta vista para las vistas de los tests por años, y los tests por normativa, ya
que, de una u otra forma, todas estas 3 vistas mostrarán listas de tests de manera similar.

For tests that have "None" or NULL as a chapter or "tema", assign them the heading "Sin Tema" ("No chapter assigned 
to it"). Also, I would like to show the tests without a chapter at the bottom end of the exam list. So, knowing all of 
this, create a condition to check if the chapter ("tema") is None / NULL. And if it is, group them under a header 
called "Sin Tema" (or "No chapter".)

This code:
    Gets unique topics excluding None.
    Creates the dictionary with assigned topics first.
    Adds 'Sin Tema' as the last key.
    Groups tests with no topic under 'Sin Tema'.
    The template will display topics in order, with 'Sin Tema' at the end.

La cosa es que un mismo test por tema puede tener 2 o más temas. Entonces, no tiene sentido asignarle 1 tema a
un test por tema.

Lo que puedo hacer por los momentos es simple y llanamente crear 1 datatable gigante en la lista de tests por temas 
para que te salgan todos los tests que sean de tipo “por tema” y ya. No les pondría subtítulos. Y haría algo similar 
con los tests “por normativa”.

Dado a que todos estos tests van a ser proceduralmente generados por los usuarios, yo quiero que el unico que pueda
ver los tests por tema sea el usuario que genero proceduralmente ese test. Los demás usuarios NO deben ver los tests
generados por un usuario. Cada usuario solo podrá veer sus propios tests generados proceduralmente.

We need to modify the lista_de_tests_por_tema view to only show tests that the current user has interacted with. 

How This Works:
1) We use the built-in Django relationship traversal with sesiondeltest__usuario=request.user

    This follows the reverse relationship from Test → SesionDelTest → User
    It finds all tests that are linked to sessions owned by the current user

2) We keep the tipo='tema' filter to ensure we only get topic-type tests.

3) We add .distinct() to prevent duplicate tests in case the user has taken the same test multiple times.

This approach is efficient because:
    It uses a single database query rather than Python-level filtering
    It leverages Django's ORM to handle all the relationship traversal
    It automatically handles the case where users might have multiple sessions for the same test

Now your view will only show topic-based tests that the authenticated user has previously interacted with through a 
session.

Puse que cada test sea único con el distinct().
"""


@login_required(login_url='iniciar_sesion')
def lista_de_tests_por_tema(request):
    # Obtener todos los tests que sean del tipo "tema" del usuario autenticado.
    # Necesito obtener las sesiones del usuario autenticado para obtener los Tests generados por el usuario.
    tests = Test.objects.filter(
        tipo='tema',
        sesiondeltest__usuario=request.user  # Uso relación inversa para ver la Sesion() relacionada a este Test()
    ).distinct()

    # # Obtener todos los tests
    # tests = Test.objects.all()

    # # Obtener los temas únicos
    # temas_unicos = Test.objects.exclude(tema=None).values_list('tema', flat=True).distinct()

    # # Agrupar tests por tema
    # tests_por_tema = {}

    # # First, group tests with assigned topics
    # for tema in temas_unicos:
    #     tests_por_tema[tema] = []

    # # Then group tests without topic at the end
    # tests_por_tema['Sin Tema'] = []

    # # Assign tests to their groups
    # for test in tests:
    #     if test.tema is None:
    #         tests_por_tema['Sin Tema'].append(test)
    #     else:
    #         tests_por_tema[test.tema].append(test)

    #     # tema = test.tema
    #     # if tema not in tests_por_tema:
    #     #     tests_por_tema[tema] = []
    #     # tests_por_tema[tema].append(test)

    # # Crear un diccionario para almacenar los tests por tema
    # tests_por_tema = {tema: [] for tema in temas_unicos}
    # # Agrupar los tests por tema
    # for test in tests:
    #     tests_por_tema[test.tema].append(test)

    # Pasar el diccionario al contexto
    context = {
        'tests': tests
        # 'tests_por_tema': tests_por_tema
    }
    return render(request, 'tests_clientes/listas-de-tests/lista_de_tests_por_tema.html', context)


""" Vista con la Lista de Años para los Tests por Año.

Esto solo mostrará los años de los tests que sean de tipo "por año". El usuario tendrá que seleccionar un año, y luego 
se le mostrará una lista de todos los tests de ese año.

If there are exams or instances of the Test() model that are of type "por año", but who have the "year" field as 
"None", then insert "Sin Año" as one of the years in the annos_unicos variable. That way, I'll render a year called 
"Sin año" or "No year" if there are exams of type "by year", but that don't have a year assigned to them.
"""


@login_required(login_url='iniciar_sesion')
def lista_de_annos(request):
    # Obtener todos los tests que sean del tipo "Año"
    tests = Test.objects.filter(tipo='año')

    # Obtener los años únicos
    annos_unicos = list(Test.objects.exclude(year=None).values_list('year', flat=True).distinct())

    # Si hay tests de tipo "año" con year=None, agregar "sin-año" a la lista. Lo puse en formato URL para evitar bugs.
    if Test.objects.filter(tipo='año', year=None).exists():
        annos_unicos.append('sin-año')

    # # Crear un diccionario para almacenar los tests por año
    # tests_por_anno = {anno: [] for anno in annos_unicos}

    # # Agrupar los tests por año
    # for test in tests:
    #     if test.year is not None:
    #         tests_por_anno[test.year].append(test)

    # Pasar el diccionario al contexto
    context = {
        'annos_unicos': annos_unicos
        # 'tests_por_anno': tests_por_anno
    }
    return render(request, 'tests_clientes/lista_de_annos.html', context)


""" Vista de Lista de Tests por Año (Por Examen) del Año Seleccionado.

Aquí se van a renderizar todos los tests que tengan marcado "Año" en el campo de "Tipo" en el modelo de Test().

Todos los tests deberían renderizarse en un solo datatable. No debo crear distintos datatables, ni generar distintos
títulos por cada año. 

Modify my lista_de_tests_por_anno() view so that it first checks whatever is stored in the "year" parameter, which will 
get from the URL to this view. If the "year" variable is anything except "sin-año", make a query set to fetch all the 
tests from the Test() model that has "año" for its "tipo" field, and has year from the URL in the "year" field of the 
record of the Test() model. That way, I will fetch all of the exams for the specified year. Meanwhile, if the URL 
parameter is "sin-año", make a query set that fetches all the exams where the "tipo" field is "año", but which have 
"None" or NULL in their "año" field. This will fetch all the exams thar are of type "year", but which don't have a year 
assigned to it.

I'll modify the lista_de_tests_por_anno view to show universal tests (non-procedurally generated) to everyone, while 
only showing procedurally generated tests to the users who created them.

How This Works:
    Base filtering: First, we filter tests by type ('año') and the selected year.

    Universal tests: We get all tests that weren't procedurally generated (fue_generado_proceduralmente=False). These 
    are visible to all users.

    User-specific tests: We get all procedurally generated tests (fue_generado_proceduralmente=True) that are connected 
    to the current user through a session. This ensures users only see their own generated tests.

    Combining results: We combine both querysets using the | operator, which performs a SQL UNION to eliminate 
    duplicates.

    Rendering: We send the combined tests to the template with the selected year for context.

This approach ensures that:
    Everyone sees the universal (non-procedurally generated) tests
    Users only see their own procedurally generated tests
    No duplicates appear in the list

Los query sets con los tests universales y con los tests del usuario autenticado tiene que ser tener disctinct().
Es decir, no puede haber tests repetidos ni en los tests universales, ni en los tests generados proceduralmente.
De lo contrario, si uso el operador "|" para hacer una intersección SQL entre los 2, me va a dar un error de Django.
"""


@login_required(login_url='iniciar_sesion')
def lista_de_tests_por_anno(request):
    # Esto solo coge los tests que sean del tipo "Año", es decir, solo coge los tests por año
    tests = Test.objects.filter(tipo='año')

    # context = {
    #     'tests': tests
    # }
    # return render(request, 'tests_clientes/lista_de_tests_por_anno.html', context)

    # # Obtener todos los tests
    # tests = Test.objects.all()

    # Obtener los años únicos
    annos_unicos = Test.objects.exclude(year=None).values_list('year', flat=True).distinct()

    # Agrupar tests por año
    tests_por_anno = {}

    # First, group tests with assigned years
    for ano in annos_unicos:
        tests_por_anno[ano] = []

    # Then group tests without year at the end
    tests_por_anno['Sin Año'] = []

    # Assign tests to their groups
    for test in tests:
        if test.year is None:

            # Si el test no tiene Año, le pondré el título Sin Año
            tests_por_anno['Sin Año'].append(test)
        else:
            tests_por_anno[test.year].append(test)

    context = {
        'tests_por_anno': tests_por_anno
    }
    return render(request, 'tests_clientes/listas-de-tests/lista_de_tests_por_anno.html', context)

    # # Esto solo coge los tests que sean del tipo "Año", es decir, solo coge los tests por año
    # # Check if we're looking for tests without a year
    # if year == 'sin-año':
    #     base_tests = Test.objects.filter(tipo='año', year=None)
    # else:
    #     base_tests = Test.objects.filter(tipo='año', year=year)
    #
    # # Get universal tests (non-procedurally generated) - visible to everyone. There shouldn't be repeated entries.
    # universal_tests = base_tests.filter(fue_generado_proceduralmente=False).distinct()
    #
    # # Get user's own procedurally generated tests. There shouldn't be repeated entries.
    # user_tests = base_tests.filter(
    #     fue_generado_proceduralmente=True,
    #     sesiondeltest__usuario=request.user
    # ).distinct()
    #
    # # Combine the two querysets. Both need to be either distinct() or not.
    # tests = universal_tests | user_tests
    #
    # # tests = Test.objects.filter(tipo='año')
    #
    # # context = {
    # #     'tests': tests
    # # }
    # # return render(request, 'tests_clientes/lista_de_tests_por_anno.html', context)
    #
    # # # Obtener todos los tests
    # # tests = Test.objects.all()
    #
    # # # Obtener los años únicos
    # # annos_unicos = Test.objects.exclude(year=None).values_list('year', flat=True).distinct()
    # #
    # # # Agrupar tests por año
    # # tests_por_anno = {}
    # #
    # # # First, group tests with assigned years
    # # for ano in annos_unicos:
    # #     tests_por_anno[ano] = []
    # #
    # # # Then group tests without year at the end
    # # tests_por_anno['Sin Año'] = []
    #
    # # # Assign tests to their groups
    # # for test in tests:
    # #     if test.year is None:
    # #
    # #         # Si el test no tiene Año, le pondré el título Sin Año
    # #         tests_por_anno['Sin Año'].append(test)
    # #     else:
    # #         tests_por_anno[test.year].append(test)
    #
    # context = {
    #
    #     'tests': tests,  # Esto tiene todos los tests por año, tanto los generados por un usuario, como los universales
    #     'selected_year': year
    #     # 'tests_por_anno': tests_por_anno
    # }
    # return render(request, 'tests_clientes/lista_de_tests_por_anno.html', context)


""" Vista para la Lista de Tests agrupado por Normativa.

Esta vista será similar a las vistas de tests por tema y por año.

Dado a que un test por normativa puede tener varias normativas, voy a quitar el campo “normativa” del modelo de Test().

Entonces, lo que puedo hacer por los momentos es simple y llanamente crear 1 datatable gigante en la lista de tests por 
normativa para que te salgan todos los tests que sean de tipo “por normativa” y ya. No les pondría subtítulos.

Quiero que el usuario solo pueda ver sus propios test generados proceduralmente. Es decir, un usuario solo podra ver sus 
propios tests por normativa. Un usuario no puede verle los tests por normativa de otros usuarios.

Para ello, usaré una relación inversa entre el modelo de Sesion(), y el modelo de Test(). Ya que el modelo de Test()
no guarda el usuario que generó ese test, pero sí guarda el tipo de test de ese test, necesito llamar al modelo de 
Sesion(). Desde el modelo de Test(), obtendré el tipo de test, que en este caso, debe ser por normativa. Luego,
desde el modelo de Sesion(), obtendré el usuario que generó ese test. Dado a que las sesiones del modelo de Sesion()
están relacionados a sus respectivos tests del modelo de Test() por medio de una FK, tengo que hallar alguna relación
entre el modelo de Sesion() y el modelo de Test() para coger las sesiones del usuario autenticado que sean de un test
de tipo "normativa". Pues, para hallar al usuario que generó ese test a través del modelo de Sesión, usaré el snippet
"sesiondeltest__usuario".

Quiero que la lista de Tests por normativa sea única. Si un usuario toma 10 veces el mismo test por normativa, no
quiero que le salgan las 10 sesiones de ese mismo test en la lista de tests por normativa. Eso se puede hacer 
desde la lista de resultados. En la lista de resultados, puedo poner alguna opción que diga "volver a tomar el test"
o algo así. Pero aquí, usaré un distinct() para que cada test sea único.
"""


@login_required(login_url='iniciar_sesion')
def lista_de_tests_por_normativa(request):
    # Obtener todos los tests que sean del tipo "normativa"
    tests = Test.objects.filter(
        tipo='normativa',
        sesiondeltest__usuario=request.user  # Uso relación inversa para ver la Sesion() relacionada a este Test()
    ).distinct()

    # # Obtener todos los tests
    # tests = Test.objects.all()
    #
    # # Obtener las normativas únicas
    # normativas_unicas = Test.objects.exclude(normativa=None).values_list('normativa', flat=True).distinct()

    # # Agrupar tests por normativa
    # tests_por_normativa = {}
    #
    # # First, group tests with assigned topics
    # for normativa in normativas_unicas:
    #     tests_por_normativa[normativa] = []
    #
    # # Then group tests without topic at the end
    # tests_por_normativa['Sin Normativa'] = []
    #
    # # Assign tests to their groups
    # for test in tests:
    #     if test.normativa is None:
    #
    #         # Si el test no tiene Normativa, le pondré el título "Sin Normativa"
    #         tests_por_normativa['Sin Normativa'].append(test)
    #     else:
    #         tests_por_normativa[test.normativa].append(test)

    context = {
        # 'tests_por_normativa': tests_por_normativa
        'tests': tests
    }
    return render(request, 'tests_clientes/listas-de-tests/lista_de_tests_por_normativa.html', context)


""" Vista para la Configuración y Ajustes de un Test Predefinido.

I'll create a new view for clients to configure exam parameters before taking the test. This approach will give 
users much more control while providing a better user experience than an overly wide datatable.
Let's design a dedicated exam configuration page:

##Exam Configuration Page Approach

    First, we'll create a new view that shows a form for configuring exam parameters.
    Then add a template for this configuration page.
    Finally, update the iniciar_el_test view to accept these parameters.

I want to modify how questions are handled. As of right now, the user can see all the questions that come included for 
the currently selected test. That's just half of what I want to achieve with this view. What I want to make in this 
functionality is to let the user to either: 1) Use the questions that come by default in the currently selected test, 
or 2) let the user to add any other exam questions that are stored in my database from my PreguntaDelTest model. So, 
modify my view to let the user to either select the questions that come by default in the currently selected test, or, 
if they choose to, to let them add any other exam questions from my database.

Key changes made:  
    Added default_questions to get questions specific to this test.
    Added all_available_questions to get all questions from database.
    Grouped questions by test name for better organization.
    Added question_mode parameter to distinguish between default and custom selection.
    Modified session creation to handle custom question selection.

Si el usuario selecciona "Customizado / Personalizado" en el límite de tiempo, entonces el usuario podrá poner su 
propio tiempo para el temporizador, y eso es lo que se meterá en "limite de tiempo" en SesionDelTest. de lo contrario,
se meterá el tiempo que el usuario seleccionó en el formulario.

If a user selects custom questions to customize their test, delete the "session.preguntas_seleccionadas" line of code. 
Instead, just use an algorithm like this, which is in spanish: "Al clicar en “comenzar test” con preguntas customizadas, 
que se me cree una nueva instancia de “Test”. Luego, yo le debo asignar esas preguntas seleccionadas a esa nueva 
instancia de Test. Luego, debo poder tomar ese test. El test se puede llamar “test customizado del USUARIO - 
(fecha y hora)” ". That is, in this "if" statement, create a new isntance of the Test() model ("nombre del test"), 
give it a name that says "Test Customizado - Username - Time and date" to it. Then, add the selected questions to that 
newly created Test. Then, I guess jsut assign that exam / name of the test from the Test() model and those questions to 
the "tomar_test()" view.

Key changes:  
    Creates a new Test instance with a custom name including username and timestamp.
    Gets selected questions from database.
    Associates selected questions with the new test using the many-to-many relationship.
    Updates the session to use the new custom test.
This will allow users to:
    Create their own custom test.
    Have it named uniquely with their username and timestamp.
    Take the test with only their selected questions.


The line of code that gets whether the exam is autocorrected or not does this:
    1. Gets the value of the `autocorrect` field from the POST request using `request.POST.get('autocorrect')`
    2. Compares it with the string `'true'`
    3. Returns a boolean value (`True` or `False`)

Since your HTML form has a dropdown with these options:

When the form is submitted:
    - If the user selected "Sí", the value will be `'true'` and the comparison will return `True`
    - If the user selected "No", the value will be `'false'` and the comparison will return `False`

This boolean value is then used to set the `test_autocorregido` field in the `SesionDelTest` model.

Modifiqué el formulario de Configurar el Test para que sea un formulario de Django en lugar de ser un formulario
hard-coded en el template de esta vista.

To get the custom time limit, I will get the calculated total_seconds from cleaned_data if it exists (custom time 
selected), otherwise falls back to the selected time_limit choice. This ensures custom times are properly passed to 
the exam session.

Debo meter el tiempo límite customizado tanto en el tiempo límite como en el tiempo restante en el modelo de 
SesionDelTest() para que se me meta el tiempo customizado en el test. Lo que hago es que, si el usuario envió tiempo
customizado en el formulario, meteré el tiempo customizado en el tiempo límite. De lo contrario, meteré el tiempo 
predefinido que el usuario seleccionó en el menu desplegable del formulario. Esto es lo que hace la línea de código 
que dice "limite_de_tiempo=formulario.cleaned_data.get('custom_time_limit') or time_limit".

Dado a que el número de preguntas de un test por año es fijo, no tengo que usar una API. Puedo simple y llanamente 
usar una variable jinja desde el view de configuración del test, y renderizarlo en el template de ese examen por año.

Todos los tests pre-definidos van a tener su número de preguntas también predefinidos. Así que, en el view  de 
configurar un test predefinido, agarrare y contaré el número de preguntas, lo meteré en una variable de jinja, y lo 
enviare al template de configurar un test pre-definido.

I'll help you add a field to display the number of questions in the form. Since this is read-only information coming 
from the view, we can add a non-editable field to the form class.

The form field will be automatically rendered in your template since you're using `{{ formulario.as_p }}`. The field 
will be displayed as a read-only input showing the total number of questions for the selected test.

This approach:
1. Adds a non-editable field to display the question count
2. Uses form initial data to populate the field
3. Styles it to look like a read-only input
4. Maintains consistency with your existing form layout

To add the ability for users to have unlimited time when selecting "ilimitado" in the time options, we need to make 
several changes in the code. First, let's modify the configurar_test_predefinido view to handle the "ilimitado" option 
properly. Next, let's modify the tomar_test view to pass the unlimited time flag to the template. Finally, let's update 
the tomar_test.html template to conditionally display the timer. Update the JavaScript for the automatic submission when 
time runs out. You'll also need to modify the JavaScript that handles the timer to account for unlimited time. In the 
exam_timer.js file, you should add a check to only initialize the timer if it's not unlimited.

These changes will ensure that:

1) When a user selects "ilimitado" time, the value is properly stored in the session.
2) The timer is not displayed in the template for unlimited time exams.
3) A message indicating unlimited time is shown instead.
4) The JavaScript timer functionality is skipped for unlimited time exams.


I'll modify the selected view so that it can generate a new instance of the Test() model to create a new exam in a similar way that the 
configurar_nuevo_test_a_generar() creates new test. configurar_nuevo_test_a_generar() creates new instances of the Test() model to create new 
exams by "tema" and by "normativa" (by topic or by regulation). Well, the configurar_test_predefinido should generate a new instance of the 
Test() model, but the exam type will be by years. Also, unlike the configurar_nuevo_test_a_generar() view, the exams here should not have its 
questions to be randomly selected. Instead, while generating tests by year, the exam questions will always be in the same fixed order. The only 
difference is that, for instance, if an exam has 10 questions, but the user wants to only take 8 questions, the last 2 questions won't be 
rendered. But the 8 questions that the user will take will be the first 8 questions from the 10 questions from that selected exam by year. 
The questions won't be selected at random, unliek the questions from the configurar_nuevo_test_a_generar() view. So, add a snippet in my 
configurar_test_predefinido() that creates a new instance of the Test() model, where the "type" field should be "year", and where the 
questions won't be randomly selected.

Key Features Added
1) Test Generation Logic:
    Only creates a new test if the user wants fewer questions than available
    Takes the first N questions in original order (no randomization)
    Maintains the original test's year value

2) Intelligent Test Selection:
    Uses the original test if user wants all questions
    Creates a new custom test only when needed

3) User-specific Naming:
    Names tests with username and timestamp for easy identification
    Marks the test as procedurally generated

This implementation will allow users to take partial exams with the first N questions from the original test, maintaining the original order 
and keeping track of which questions were included.

If the number of exam questions that the user want a to do is bigger than the total number of available questions for 
the test, an error message will show up via the "messages" library from django telling the suer that the number of 
questions typed is bigger than the total number of questions available, and that he should type a number less or equal 
to the total number of available questions for the selected test.
"""


@login_required(login_url='iniciar_sesion')
def configurar_test_predefinido(request, test_id):
    """
    View for configuring test parameters before starting the exam.
    Allows users to set difficulty, time limit, and select specific questions.
    """
    # Get the test instance
    test = get_object_or_404(Test, id=test_id)

    # Esto agarra todas las preguntas de este test seleccionado
    preguntas_del_test_seleccionado = PreguntaDelTest.objects.filter(nombre_del_test=test_id).order_by('id')

    # Esto cuenta el número de preguntas disponibles en total del test seleccionado
    numero_de_preguntas = preguntas_del_test_seleccionado.count()

    # # Get all available questions from database
    # all_available_questions = PreguntaDelTest.objects.all().order_by('id')

    # all_available_questions = PreguntaDelTest.objects.all().order_by('nombre_del_test', 'id')

    # # Get all questions for this test for the question selection feature
    # all_questions = PreguntaDelTest.objects.filter(nombre_del_test=test_id).order_by('id')

    # # Group questions by test name for better organization
    # questions_by_test = {}
    #
    # for question in all_available_questions:
    #     test_name = question.nombre_del_test.nombre_del_test
    #     if test_name not in questions_by_test:
    #         questions_by_test[test_name] = []
    #     questions_by_test[test_name].append(question)

    # Si el usuario envía el formulario (para comenzar el Test)
    if request.method == 'POST':

        # Parte 1 del formulario
        formulario = ConfigurarTestSinIncluirPreguntasForm(request.POST)

        # Campo con el número de preguntas a realizar del formulario
        campo_numero_de_preguntas_a_realizar = NumeroDePreguntasARealizarFormulario(request.POST)

        # Validar / Sanitizar los formularios
        if formulario.is_valid() and campo_numero_de_preguntas_a_realizar.is_valid():

            # Check if unlimited time was selected
            time_choice = formulario.cleaned_data['time_limit']
            if time_choice == 'ilimitado':
                # Use None or a special value to indicate unlimited time
                time_limit = None
            else:
                # Esto agarra el tiempo que el usuario seleccionó en el formulario de manera validada
                # Convert to integer if not unlimited
                time_limit = int(time_choice)
                # time_limit = int(formulario.cleaned_data['time_limit'])

            # time_limit = int(request.POST.get('time_limit', 1800))  # Default 30 minutes

            # Dejare el custom time desactivado por los momentos
            # # Si el usuario selecciona un tiempo personalizado para el temporizador, necesito coger ese tiempo
            # if formulario.cleaned_data['custom_time']:
            #     custom_time = formulario.cleaned_data['custom_time']  # Validado

            # custom_time = request.POST.get('custom_time')

            # # Get number of questions requested by user
            # num_preguntas = formulario_parte_2.cleaned_data['numero_de_preguntas']

            # # Get random questions based on test type

            # # MODIFICAR para que NO me haga las preguntas de manera aleatoria, sino que las agarre por orden.

            # # TAL VEZ DESACTIVE ESTA LINEA, porque no la usare.
            # year = formulario_parte_2.cleaned_data['year']
            # preguntas_random = PreguntaDelTest.objects.filter(year=year).order_by('?')[:num_preguntas]

            # # Esto agrega cada pregunta al test a tomar. La manera que lo hace es agregando el test a cada pregunta.
            # for pregunta in preguntas_random:
            #     pregunta.nombre_del_test.add(nuevo_test)

            # Get number of questions requested by user
            numero_preguntas_solicitadas = campo_numero_de_preguntas_a_realizar.cleaned_data[
                'numero_de_preguntas_a_realizar']

            # Si el usuario escribió que quiere más preguntas que las que hay disponibles, mostrarle un error
            if numero_preguntas_solicitadas > numero_de_preguntas:
                messages.error(request,
                               f'El número de preguntas solicitadas ({numero_preguntas_solicitadas}) es mayor que el '
                               f'número de preguntas disponibles ({numero_de_preguntas}). Por favor, seleccione un '
                               f'número menor o igual a {numero_de_preguntas}.')

                # Redirect to the same page to show the error message.
                # El "name" de este view en el urls.py es "configurar_test", por lo que debo usar ese nombre.
                return redirect('tests_clientes:configurar_test', test_id=test.id)

            # Create a new Test instance only if user wants fewer than all questions
            if numero_preguntas_solicitadas < numero_de_preguntas:
                # Create timestamp for the test name
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')

                # Create new Test instance with procedurally generated name and type="año"
                nuevo_test = Test.objects.create(
                    nombre_del_test=f"Test por año de {request.user.username} - {timestamp}",
                    tipo='año',
                    year=test.year,  # Keep the same year as original test
                    fue_generado_proceduralmente=True,
                )

                # Get the first N questions from the original test in order (no randomization)
                preguntas_a_incluir = preguntas_del_test_seleccionado[:numero_preguntas_solicitadas]

                # Assign selected questions to the new Test
                for pregunta in preguntas_a_incluir:
                    pregunta.nombre_del_test.add(nuevo_test)

                # Use the new test for the session
                test_to_use = nuevo_test
            else:
                # If user wants all questions, use the original test
                test_to_use = test

            # Esto crea una nueva Sesión con los datos validados del formulario, y con valores correctos para el tiempo
            session = SesionDelTest.objects.create(
                usuario=request.user,
                nombre_del_test=test_to_use,
                # nivel_de_dificultad=difficulty,
                nivel_de_dificultad=formulario.cleaned_data['difficulty'],
                # Use custom time if provided, otherwise use selected time (which might be None for unlimited)
                limite_de_tiempo=formulario.cleaned_data.get('custom_time_limit') or time_limit,
                tiempo_restante=formulario.cleaned_data.get('custom_time_limit') or time_limit,
                # limite_de_tiempo=custom_time if time_limit == 'custom' else time_limit,
                # tiempo_restante=custom_time if time_limit == 'custom' else time_limit,

                # Agrega "True" o "False" para decir si el test es autocorregido
                test_autocorregido=formulario.cleaned_data['autocorrect'] == 'true'

                # test_autocorregido=autocorrect  # Agrega "True" o "False" para decir si el test es autocorregido

                # limite_de_tiempo=time_limit,
                # tiempo_restante=time_limit  # Initial remaining time equals the time limit
            )

            # # Get user-selected parameters
            # difficulty = request.POST.get('difficulty', '1')
            #

            # question_mode = request.POST.get('question_mode', 'default')  # 'default' or 'custom'
            #
            # # Handle question selection - get selected question IDs
            # selected_questions = request.POST.getlist('selected_questions')

            # # Check if user selected custom questions
            # use_custom_questions = request.POST.get('use_custom_questions') == 'on'

            # # Esto coge del formulario si el test es autocorregido o no, y lo compara con "True". True + True = True.
            # autocorrect = request.POST.get('autocorrect') == 'true'

            # # Save selected questions if using custom mode
            # # If using custom questions, save them to the session
            # # if use_custom_questions and selected_questions:
            # if question_mode == 'custom' and selected_questions:
            #
            #     # We need to add a ManyToMany field to SesionDelTest for custom questions
            #     # or create a separate model to store this information
            #     # session.preguntas_seleccionadas = ','.join(selected_questions)
            #
            #     # Crea un Timestamp para agregárselo al nombre del Test Customizado que el Cliente va a crear
            #     timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
            #
            #     # Crea una instancia del modelo de Test(), y le agrego un nombre customizado con el Timestamp
            #     custom_test = Test.objects.create(
            #         nombre_del_test=f"Test Customizado - {request.user.username} - {timestamp}"
            #     )
            #
            #     # Agrega las preguntas seleccionadas para el test customizado a la nueva instancia de Test()
            #     selected_questions = PreguntaDelTest.objects.filter(id__in=selected_questions)
            #     for question in selected_questions:
            #         question.nombre_del_test.add(custom_test)
            #
            #     # Introduce la nueva instancia de Test() en la nueva sesión creada para el Test customizado
            #     session.nombre_del_test = custom_test
            #
            #     # Guarda los cambios en la Nueva Sesion Creada
            #     session.save()

            # Redirijo al usuario a la 1era pregunta del Test para que lo tome
            # Esto redirige al cliente a la vista de Tomar el Test con Autocorrección (si lo quiere con autocorrección)
            if session.test_autocorregido:
                return redirect('tests_clientes:tomar_test_autocorregido', session_id=session.id, question_number=1)

            else:
                # Esto redirige al usuario a la vista de Tomar el Test sin autocorrección
                return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=1)

        else:  # Si el formulario no es válido, entonces le muestro un mensaje de error
            messages.error(request, f"Error al enviar el formulario")

            # error_messages = []
            # for field, errors in formulario.errors.items():
            #     error_messages.append(f"{field}: {', '.join(errors)}")
            #
            # messages.error(request, f"Error al enviar el formulario: {'; '.join(error_messages)}")

            # Esto renderiza la parte 1 del formulario
            formulario = ConfigurarTestSinIncluirPreguntasForm(request.POST)

            # Esto renderiza el campo con el número de preguntas
            campo_numero_de_preguntas_a_realizar = NumeroDePreguntasARealizarFormulario(request.POST)

    else:  # Esto renderiza el formulario si entras a esta página, es decir, si no envías el formulario

        # Renderiza el formulario con el campo del número de preguntas del test rellenado con el número de preguntas
        formulario = ConfigurarTestSinIncluirPreguntasForm(initial={
            # 'numero_de_preguntas': numero_de_preguntas
            'preguntas_disponibles': numero_de_preguntas  # Meto el Número de preguntas en el campo de preguntas
        })

        # Renderiza el campo para que el usuario escriba cuántas preguntas quiere hacer en el test
        campo_numero_de_preguntas_a_realizar = NumeroDePreguntasARealizarFormulario()

    # Prepare context for the form
    context = {
        'formulario': formulario,
        'campo_numero_de_preguntas_a_realizar': campo_numero_de_preguntas_a_realizar,
        'test': test,
        'numero_de_preguntas': numero_de_preguntas,  # Número de preguntas para este test
        # 'default_questions': default_questions,
        # 'all_available_questions': all_available_questions,
        # 'questions_by_test': questions_by_test,
        # 'all_questions': all_questions,
        # 'difficulty_levels': [
        #     {'value': '1', 'name': 'Errores No Restan'},
        #     {'value': '2', 'name': '4:1 (4 respuestas malas restan 1 buena)'},
        #     {'value': '3', 'name': '3:1 (3 respuestas malas restan 1 buena)'},
        #     {'value': '4', 'name': '2:1 (2 respuestas malas restan 1 buena)'},
        #     {'value': '5', 'name': '1:1 (1 respuesta mala resta 1 respuesta buena)'}
        # ],
        # 'time_options': [  # Time limit options in seconds
        #     {'value': 600, 'name': '10 minutos'},
        #     {'value': 1200, 'name': '20 minutos'},
        #     {'value': 1800, 'name': '30 minutos'},
        #     {'value': 2700, 'name': '45 minutos'},
        #     {'value': 3600, 'name': '1 hora'},
        #     {'value': 'custom', 'name': 'Personalizado'}  # Si quiero poner mi propio tiempo para el temporizador
        # ]
    }

    return render(request, 'tests_clientes/configurar_test.html', context)


""" Vista para Configurar un Test que Se Tiene Que Generar desde Cero.

Voy a introducir 2 formularios de Django en el view de Configurar un Nuevo Test a Generar: el formulario que ya 
creé para configurar un test predefinido, y otro formulario que va a permitir al cliente seleccionar unos nuevos 
campos, como por ejemplo, si el test es por tema, por año, o por normativa.

Ahora, para verificar que las preguntas se le asignen aleatoriamente a un test, primero tengo que hacer varias 
cosas:

1) Al generar el test, tengo que crearle un nombre genérico, y luego tengo que insertarlo en el modelo de Test(). Esto 
lo puedo hacer de manera similar de como yo generaba un nuevo test anteriormente.

2) Tengo que luego asignarle a ese test creado en el modelo de Test() el año, la normativa, o el tema, según 
corresponda.

3) Luego, tengo que agarrar el número de preguntas escrito por el usuario en el formulario para configurar un nuevo 
test.

4) Luego, tengo que agarrar el tema, o el año, o la normativa seleccionada por el usuario. Si selecciona “aleatorio”, 
seria un caso extra (que sea cualquier pregunta a lo random).

5) Luego, tengo que agarrar un montón de preguntas de manera aleatoria que pertenezcan a ese tema, o a ese año, o a 
esa normativa. ( El número de preguntas que debo agarrar es el que haya escrito el usuario.

5.1) Le agrego un seed para hacer que tenga más aleatoriedad? El seed se lo puedo agarrar agarrando el timestamp de 
la hora de inicio del examen. Con ese timestamp, creo el seed para determinar cuales preguntas agarrar).

6) Luego, gracias a un “for” loop y aprovechando el usar el many to many, le asignare las preguntas ya existentes a 
ese newly created test del modelo de Test().

7) Debo luego asignar el resto de cosas que debo asignar a los tests.

Before the Query set made within the "session" variable, I need to first create an instance of the Test() model to 
generate a new test. Then, that new instance must be inserted into the "nombre del test" field. And I need to generate 
a name for the newly created test for the test() model. So, add a generic name like "Test de USERNAME, TIMESTAMP", 
where USERNAME is the username of the logged in user, and TIMESTAMP is the timestamp when the user began the test. 
So, knowing all of this, create an instance of the Test() model with a generic name like I told you before the 
"session" variable query set.

Al generar el nuevo test, voy a meter el tipo de test en el modelo de Test() ("normativa", "año", o "tema").

Tengo que modificar este view para que, si el usuario selecciona que quiere tiempo ilimitado, entonces tendrá tiempo
ilimitado para hacer su test.

Por si acaso, prefiero modificar mi código que genera mis tests proceduralmente para que siempre se marque “true” en 
“fue generado proceduralmente” en Test(). Por defecto, ese campo siempre se marca como True al generarse un test.
Pero, para evitar posibles bugs, es mejor que me asegure de que el campo "fue generado proceduralmente" se marque como
"true". 

I want to implement a functionality that, if the user types that he wants to take more questions for an exam than the total available number of 
questions for that exam, I want to display them an error message telling them to select a lower number. However, as of right now, I'm taking the 
total number of all the questions stored in the database in the PreguntaDelTest() model. I don't want that. The user will first select if they 
want to take a test by "tema" or by "normativa". Afterwards, they will select the specific "tema" or "normativa" that they want (for instance, 
"tema 1", or "topic 1"). Then, my web app will fetch the total number of questions for the specific selected type of test for the specific topic 
or regulation that the user wants for that test. THAT's the number that I want. I don't want the total number of questions that are stored in 
the database. I want the total number of questions, for instance, for a "tema 1" exam, if the suer selects "tema 1" as their type of exam. 
Well, if the total number of questions, for instance, for "tema 1" is 10, and the user types "11", I want to show them an error message. So, 
implement this functionality.

What This Does
Topic-Specific Filtering: Instead of checking against all questions in the database, it filters based on the selected test type and specific 
selection (tema or normativa).

Custom Error Message: The error message now includes which specific topic or regulation was selected, making it clearer to the user.

Variable Message Text: Added a tipo_mensaje variable that describes the selection type in human-readable format for the error message.

Same Filtering Logic: Uses the same filtering logic that's used later when actually selecting questions, ensuring consistency.

This ensures users only see errors that are relevant to their specific selection, rather than a generic message about the total question count 
in the database.

Now, I want to overhaul for selecting the topic or "tema" when I want to make an exam by "tema" in the form that lets 
me generate a new exam from scratch. Right now, to make an exam by topic, I select a single topic from a dropdown 
menu. However, I want my users to select 1 or more topics for an exam. And, for the time being, I don't want to use 
formsets. Instead, I want to render all the 40 possible topics for an exam as a list of filters with checkboxes. In 
that list of filters or topics, users can click 1 or more boxes to select all the topics that they want for an exam. 
Depending on the selected topics, my view should select all the questions that belong to the topics selected in the 
list of topics, which the users will be able to check using checkboxes. This is the form that currently lets you 
select a topic from a dropdown menu. Look at my configurar_nuevo_test_a_generar() view from the attached views.py 
file. Give me a general algorithm on how to do this, since it will be hard. There are a ton of changes that should be 
made to my code to render the full list of 40 topics as a series of checkboxes, where suers can select 1 or mor topics 
for a single exam while configuring the settings for the exam that they want to take.
"""


@login_required(login_url='iniciar_sesion')
def configurar_nuevo_test_a_generar(request):
    """
    View for configuring test parameters for a newly generated exam.
    Le permite al usuario decidir si el test será por normativa, por año, o por tema, entre otros parámetros.
    """
    # # Get the test instance
    # test = get_object_or_404(Test, id=test_id)

    # # Get default questions for this test
    # default_questions = PreguntaDelTest.objects.filter(nombre_del_test=test_id).order_by('id')

    # Get all available questions from database
    all_available_questions = PreguntaDelTest.objects.all().order_by('id')

    # Si el usuario envía el formulario (para comenzar el Test)
    if request.method == 'POST':

        formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm(request.POST)

        # Esto contiene los nuevos campos que son específicos para esta vista de Configurar un Test
        formulario_parte_2 = ConfigurarNuevoTestAGenerarForm(request.POST)

        # Validar / Sanitizar el formulario. En caso de que sea válido:
        if formulario_parte_1.is_valid() and formulario_parte_2.is_valid():

            # Validar / Sanitizar el Formulario

            # Check if unlimited time was selected
            time_choice = formulario_parte_1.cleaned_data['time_limit']
            if time_choice == 'ilimitado':
                # Use None or a special value to indicate unlimited time
                time_limit = None
            else:
                # Convert to integer if not unlimited.
                # Esto agarra el tiempo que el usuario seleccionó en el formulario de manera validada.
                time_limit = int(time_choice)

            # # Esto agarra el tiempo que el usuario seleccionó en el formulario de manera validada
            # time_limit = int(formulario_parte_1.cleaned_data['time_limit'])

            # Get number of questions requested by user
            numero_de_preguntas = formulario_parte_2.cleaned_data['numero_de_preguntas']

            # Get the type of test and specific selection
            tipo_test = formulario_parte_2.cleaned_data['tipo_de_test']

            # Get filtered questions based on test type and specific selection.
            # # Replace the existing topic filtering with multi-topic support.
            if tipo_test == 'tema':

                temas_seleccionados = formulario_parte_2.cleaned_data['tema']
                # tema = formulario_parte_2.cleaned_data['tema']

                if not temas_seleccionados:
                    messages.error(request, 'Debes seleccionar al menos un tema.')
                    return redirect('tests_clientes:configurar_nuevo_test_a_generar')

                # Use Q objects to create OR conditions for multiple topics.
                # Usa objetos Q para crear condiciones "OR" para coger múltiples temas.

                query = Q()
                for tema in temas_seleccionados:
                    query |= Q(tema=tema)

                available_questions = PreguntaDelTest.objects.filter(query)

                # available_questions = PreguntaDelTest.objects.filter(tema=tema)

                # Create custom message showing selected topics
                temas_texto = ", ".join([f"Tema {t}" for t in temas_seleccionados])
                tipo_mensaje = f"temas '{temas_texto}'"

                # tipo_mensaje = f"tema '{tema}'"

            elif tipo_test == 'normativa':

                # Para coger múltiples normativas, usaré un snippet similar al que coge múltiples temas

                normativas_seleccionadas = formulario_parte_2.cleaned_data['normativa']

                if not normativas_seleccionadas:
                    messages.error(request, 'Debes seleccionar al menos una normativa.')
                    return redirect('tests_clientes:configurar_nuevo_test_a_generar')

                # Use Q objects to create OR conditions for multiple topics.
                # Usa objetos Q para crear condiciones "OR" para coger múltiples temas.

                query = Q()
                for normativa in normativas_seleccionadas:
                    query |= Q(normativa=normativa)

                available_questions = PreguntaDelTest.objects.filter(query)

                # Create custom message showing selected topics
                normativas_texto = ", ".join([f"Normativa {t}" for t in normativas_seleccionadas])
                tipo_mensaje = f"normativas '{normativas_texto}'"

                # normativa = formulario_parte_2.cleaned_data['normativa']
                # available_questions = PreguntaDelTest.objects.filter(normativa=normativa)
                # tipo_mensaje = f"normativa '{normativa}'"

            else:
                # Default case for other types
                available_questions = PreguntaDelTest.objects.all()
                tipo_mensaje = "seleccionado"

            # Count of available questions for the specific selection
            available_question_count = available_questions.count()

            # Si el número de preguntas escrito por el usuario es más que las disponibles
            if numero_de_preguntas > available_question_count:
                # Mostrar un mensaje de error
                messages.error(request,
                               f'El número de preguntas solicitadas ({numero_de_preguntas}) es mayor que el '
                               f'número de preguntas disponibles para el {tipo_mensaje} ({available_question_count}). '
                               f'Por favor, seleccione un número menor o igual a {available_question_count}.')

                # Vuelvo a renderizar el formulario con el error
                return redirect('tests_clientes:configurar_nuevo_test_a_generar')

            # Create timestamp for the test name
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')

            # Create new Test() instance with procedurally generated name, and the selected type
            nuevo_test = Test.objects.create(
                nombre_del_test=f"Test de {request.user.username} - {timestamp}",
                tipo=formulario_parte_2.cleaned_data['tipo_de_test'],  # Tipo de test que el usuario seleccionó
                fue_generado_proceduralmente=True,  # Test debe marcarse como que fue generado proceduralmente
            )

            # Para que las preguntas cogidas sean realmente aleatorias, le voy a agregar un seed
            seed(int(datetime.now().timestamp()))

            # Voy a volver a chequear si el test es por tema o por normativa para renderizar preguntas aleatorias
            tipo_test = formulario_parte_2.cleaned_data['tipo_de_test']
            if tipo_test == 'tema':  # Si el test es por tema

                # Como ahora agarro los temas de las preguntas usando "query", ya no necesito esto
                # tema = formulario_parte_2.cleaned_data['tema']

                # Use the same Q object for random question selection
                preguntas_random = PreguntaDelTest.objects.filter(query).order_by('?')[:numero_de_preguntas]

                # Ya no necesito esto
                # preguntas_random = PreguntaDelTest.objects.filter(tema=tema).order_by('?')[:numero_de_preguntas]

            # elif tipo_test == 'año':    # Si el test es por año

            #
            #     # MODIFICAR para que NO me haga las preguntas de manera aleatoria, sino que las agarre por orden.

            #     # TAL VEZ DESACTIVE ESTA LINEA, porque no la usare.
            #     year = formulario_parte_2.cleaned_data['year']
            #     preguntas_random = PreguntaDelTest.objects.filter(year=year).order_by('?')[:num_preguntas]

            elif tipo_test == 'normativa':  # Si el test es por normativa

                # Use the same Q object for random question selection.
                # Esto selecciona las preguntas seleccionadas por normativa, y agarra las preguntas de manera aleatoria.
                preguntas_random = PreguntaDelTest.objects.filter(query).order_by('?')[:numero_de_preguntas]

                # Como ahora cojo 1 o varias normativas, ya no necesito esto.
                # normativa = formulario_parte_2.cleaned_data['normativa']
                # preguntas_random = PreguntaDelTest.objects.filter(normativa=normativa).order_by('?')[:numero_de_preguntas]

            else:
                # Si en un futuro quiero meter un test 100% aleatorio, sin tomar en cuenta tema o normativa,
                # Esto coge todas las preguntas de la base de datos de manera aleatoria.
                preguntas_random = PreguntaDelTest.objects.all().order_by('?')[:numero_de_preguntas]

            # Esto agrega cada pregunta al test a tomar. La manera que lo hace es agregando el test a cada pregunta.
            for pregunta in preguntas_random:
                pregunta.nombre_del_test.add(nuevo_test)

            # Esto crea una nueva Sesión con los datos validados del formulario
            session = SesionDelTest.objects.create(
                usuario=request.user,
                nombre_del_test=nuevo_test,  # INSTANCIA DE UN TEST EXISTENTE
                nivel_de_dificultad=formulario_parte_1.cleaned_data['difficulty'],
                limite_de_tiempo=formulario_parte_1.cleaned_data.get('custom_time_limit') or time_limit,
                tiempo_restante=formulario_parte_1.cleaned_data.get('custom_time_limit') or time_limit,

                # Agrega "True" o "False" para decir si el test es autocorregido
                test_autocorregido=formulario_parte_1.cleaned_data['autocorrect'] == 'true'
            )

            # Redirijo al usuario a la 1era pregunta del Test para que lo tome
            # Esto redirige al cliente a la vista de Tomar el Test con Autocorrección (si lo quiere con autocorrección)
            if session.test_autocorregido:
                return redirect('tests_clientes:tomar_test_autocorregido', session_id=session.id, question_number=1)

            else:
                # Esto redirige al usuario a la vista de Tomar el Test sin autocorrección
                return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=1)

        else:  # Si el formulario no es válido, entonces le muestro un mensaje de error
            messages.error(request, f"Error al enviar el formulario")

            # Esto renderiza los formularios con los errores
            formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm(request.POST)
            formulario_parte_2 = ConfigurarNuevoTestAGenerarForm(request.POST)

    else:  # Esto renderiza los formularios si entras a esta página, es decir, si no envías el formulario
        formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm()
        formulario_parte_2 = ConfigurarNuevoTestAGenerarForm()

    # Prepare context for the form
    context = {
        'formulario_parte_1': formulario_parte_1,
        'formulario_parte_2': formulario_parte_2,
        # 'test': test,
        # 'default_questions': default_questions,
    }

    return render(request, 'tests_clientes/configurar_nuevo_test_a_generar.html', context)


""" Vista para Configurar un Nuevo Test por Tema.

Esto será similar a la vista de Generar un nuevo test desde cero, pero será solo para generar un test por tema.

Pondré algún boolean o algo para decir si el test es por normativa o por tema. Para evitar bugs, puedo poner un boolean 
que diga “es un test por tema”, y enviarlo por Jinja. Si es “true”, solo renderizo las casillas por tema. De lo 
contrario, renderizo las casillas por normativa.

"""


@login_required(login_url='iniciar_sesion')
def configure_new_test_by_topic(request):

    # Get all available questions from database
    all_available_questions = PreguntaDelTest.objects.all().order_by('id')

    # Boolean that tells me if the test is by topic. For this view, it will be set to "true"
    is_test_by_topic = True

    # Si el usuario envía el formulario (para comenzar el Test)
    if request.method == 'POST':

        formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm(request.POST)

        # Esto contiene los nuevos campos que son específicos para esta vista de Configurar un Test
        formulario_parte_2 = ConfigureNewTestByTopicForm(request.POST)

        # Validar / Sanitizar el formulario. En caso de que sea válido:
        if formulario_parte_1.is_valid() and formulario_parte_2.is_valid():

            # Validar / Sanitizar el Formulario

            # Check if unlimited time was selected
            time_choice = formulario_parte_1.cleaned_data['time_limit']
            if time_choice == 'ilimitado':
                # Use None or a special value to indicate unlimited time
                time_limit = None
            else:
                # Convert to integer if not unlimited.
                # Esto agarra el tiempo que el usuario seleccionó en el formulario de manera validada.
                time_limit = int(time_choice)

            # # Esto agarra el tiempo que el usuario seleccionó en el formulario de manera validada
            # time_limit = int(formulario_parte_1.cleaned_data['time_limit'])

            # Get number of questions requested by user
            numero_de_preguntas = formulario_parte_2.cleaned_data['numero_de_preguntas']

            # The type of exam will "by topic", since this view is only for exams by topic
            tipo_test = "tema"

            # Get filtered questions based on test type and specific selection.
            # # Replace the existing topic filtering with multi-topic support.

            temas_seleccionados = formulario_parte_2.cleaned_data['tema']
            # tema = formulario_parte_2.cleaned_data['tema']

            if not temas_seleccionados: # If you don't select any topic

                # Shows an error message, and reloads the current page / template with the form
                messages.error(request, 'Debes seleccionar al menos un tema.')
                return redirect('tests_clientes:configure_new_test_by_topic')

            # Use Q objects to create OR conditions for multiple topics.
            # Usa objetos Q para crear condiciones "OR" para coger múltiples temas.

            query = Q()
            for tema in temas_seleccionados:
                query |= Q(tema=tema)

            available_questions = PreguntaDelTest.objects.filter(query)

            # available_questions = PreguntaDelTest.objects.filter(tema=tema)

            # Create custom message showing selected topics
            temas_texto = ", ".join([f"Tema {t}" for t in temas_seleccionados])
            tipo_mensaje = f"temas '{temas_texto}'"

            # Count of available questions for the specific selection
            available_question_count = available_questions.count()

            # Si el número de preguntas escrito por el usuario es mayor que las disponibles
            if numero_de_preguntas > available_question_count:
                # Mostrar un mensaje de error
                messages.error(request,
                               f'El número de preguntas solicitadas ({numero_de_preguntas}) es mayor que el '
                               f'número de preguntas disponibles para el {tipo_mensaje} ({available_question_count}). '
                               f'Por favor, seleccione un número menor o igual a {available_question_count}.')

                # Vuelvo a renderizar el formulario con el error
                return redirect('tests_clientes:configure_new_test_by_topic')

            # Create timestamp for the test name
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')

            # Create new Test() instance with procedurally generated name, and of type "topic"
            nuevo_test = Test.objects.create(
                nombre_del_test=f"Test de {request.user.username} - {timestamp}",
                tipo="tema",  # The exam type will be "by topic"
                fue_generado_proceduralmente=True,  # Test debe marcarse como que fue generado proceduralmente
            )

            # Para que las preguntas cogidas sean realmente aleatorias, le voy a agregar un seed
            seed(int(datetime.now().timestamp()))

            # This will sort the questions in a random order
            # Use the same Q object for random question selection (with the selected topics from the form)
            preguntas_random = PreguntaDelTest.objects.filter(query).order_by('?')[:numero_de_preguntas]

            # Esto agrega cada pregunta al test a tomar. La manera que lo hace es agregando el test a cada pregunta.
            for pregunta in preguntas_random:
                pregunta.nombre_del_test.add(nuevo_test)

            # Esto crea una nueva Sesión con los datos validados del formulario
            session = SesionDelTest.objects.create(
                usuario=request.user,
                nombre_del_test=nuevo_test,  # INSTANCIA DE UN TEST EXISTENTE
                nivel_de_dificultad=formulario_parte_1.cleaned_data['difficulty'],
                limite_de_tiempo=formulario_parte_1.cleaned_data.get('custom_time_limit') or time_limit,
                tiempo_restante=formulario_parte_1.cleaned_data.get('custom_time_limit') or time_limit,
                # Agrega "True" o "False" para decir si el test es autocorregido
                test_autocorregido=formulario_parte_1.cleaned_data['autocorrect'] == 'true'
            )

            # Redirijo al usuario a la 1era pregunta del Test para que lo tome.
            # Esto redirige al cliente a la vista de Tomar el Test con Autocorrección (si lo quiere con autocorrección)
            if session.test_autocorregido:
                return redirect('tests_clientes:tomar_test_autocorregido', session_id=session.id, question_number=1)

            else:
                # Esto redirige al usuario a la vista de Tomar el Test sin autocorrección
                return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=1)

        else:  # Si el formulario no es válido, entonces le muestro un mensaje de error
            messages.error(request, f"Error al enviar el formulario")

            # Esto renderiza los formularios con los errores
            formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm(request.POST)
            formulario_parte_2 = ConfigureNewTestByTopicForm(request.POST)

    else:  # Esto renderiza los formularios si entras a esta página, es decir, si no has enviado el formulario
        formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm()
        formulario_parte_2 = ConfigureNewTestByTopicForm()

    # Prepare context for the form
    context = {
        'formulario_parte_1': formulario_parte_1,
        'formulario_parte_2': formulario_parte_2,
        'is_test_by_topic': is_test_by_topic,  # Booleano que dice si el test es por tema
        # 'test': test,
        # 'default_questions': default_questions,
    }

    return render(request, 'tests_clientes/configurar_test_por_tema_o_normativa.html', context)


""" Vista para Configurar un Nuevo Test por Normativa.

Esto será similar a la vista de Generar un nuevo test desde cero, pero será solo para generar un test por Normativa.

Pondré algún boolean o algo para decir si el test es por normativa o por tema. Para evitar bugs, puedo poner un boolean 
que diga “es un test por tema”, y enviarlo por Jinja. En este caso, debe ser "false", ya que este no será un test
por tema.


BOOKMARK.
"""


@login_required(login_url='iniciar_sesion')
def configure_new_test_by_regulation(request):

    # Get all available questions from database
    all_available_questions = PreguntaDelTest.objects.all().order_by('id')

    # Boolean that tells me if the test is by topic. For this view, it will be set to "false".
    is_test_by_topic = False

    # Si el usuario envía el formulario (para comenzar el Test)
    if request.method == 'POST':

        formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm(request.POST)

        # Esto contiene los nuevos campos que son específicos para esta vista de Configurar un Test
        formulario_parte_2 = ConfigureNewTestByTopicForm(request.POST)

        # Validar / Sanitizar el formulario. En caso de que sea válido:
        if formulario_parte_1.is_valid() and formulario_parte_2.is_valid():

            # Validar / Sanitizar el Formulario

            # Check if unlimited time was selected
            time_choice = formulario_parte_1.cleaned_data['time_limit']
            if time_choice == 'ilimitado':
                # Use None or a special value to indicate unlimited time
                time_limit = None
            else:
                # Convert to integer if not unlimited.
                # Esto agarra el tiempo que el usuario seleccionó en el formulario de manera validada.
                time_limit = int(time_choice)

            # # Esto agarra el tiempo que el usuario seleccionó en el formulario de manera validada
            # time_limit = int(formulario_parte_1.cleaned_data['time_limit'])

            # Get number of questions requested by user
            numero_de_preguntas = formulario_parte_2.cleaned_data['numero_de_preguntas']

            # The type of exam will "by topic", since this view is only for exams by topic
            tipo_test = "tema"

            # Get filtered questions based on test type and specific selection.
            # # Replace the existing topic filtering with multi-topic support.

            temas_seleccionados = formulario_parte_2.cleaned_data['tema']
            # tema = formulario_parte_2.cleaned_data['tema']

            if not temas_seleccionados: # If you don't select any topic

                # Shows an error message, and reloads the current page / template with the form
                messages.error(request, 'Debes seleccionar al menos un tema.')
                return redirect('tests_clientes:configure_new_test_by_topic')

            # Use Q objects to create OR conditions for multiple topics.
            # Usa objetos Q para crear condiciones "OR" para coger múltiples temas.

            query = Q()
            for tema in temas_seleccionados:
                query |= Q(tema=tema)

            available_questions = PreguntaDelTest.objects.filter(query)

            # available_questions = PreguntaDelTest.objects.filter(tema=tema)

            # Create custom message showing selected topics
            temas_texto = ", ".join([f"Tema {t}" for t in temas_seleccionados])
            tipo_mensaje = f"temas '{temas_texto}'"

            # Count of available questions for the specific selection
            available_question_count = available_questions.count()

            # Si el número de preguntas escrito por el usuario es mayor que las disponibles
            if numero_de_preguntas > available_question_count:
                # Mostrar un mensaje de error
                messages.error(request,
                               f'El número de preguntas solicitadas ({numero_de_preguntas}) es mayor que el '
                               f'número de preguntas disponibles para el {tipo_mensaje} ({available_question_count}). '
                               f'Por favor, seleccione un número menor o igual a {available_question_count}.')

                # Vuelvo a renderizar el formulario con el error
                return redirect('tests_clientes:configure_new_test_by_topic')

            # Create timestamp for the test name
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')

            # Create new Test() instance with procedurally generated name, and of type "topic"
            nuevo_test = Test.objects.create(
                nombre_del_test=f"Test de {request.user.username} - {timestamp}",
                tipo="tema",  # The exam type will be "by topic"
                fue_generado_proceduralmente=True,  # Test debe marcarse como que fue generado proceduralmente
            )

            # Para que las preguntas cogidas sean realmente aleatorias, le voy a agregar un seed
            seed(int(datetime.now().timestamp()))

            # This will sort the questions in a random order
            # Use the same Q object for random question selection (with the selected topics from the form)
            preguntas_random = PreguntaDelTest.objects.filter(query).order_by('?')[:numero_de_preguntas]

            # Esto agrega cada pregunta al test a tomar. La manera que lo hace es agregando el test a cada pregunta.
            for pregunta in preguntas_random:
                pregunta.nombre_del_test.add(nuevo_test)

            # Esto crea una nueva Sesión con los datos validados del formulario
            session = SesionDelTest.objects.create(
                usuario=request.user,
                nombre_del_test=nuevo_test,  # INSTANCIA DE UN TEST EXISTENTE
                nivel_de_dificultad=formulario_parte_1.cleaned_data['difficulty'],
                limite_de_tiempo=formulario_parte_1.cleaned_data.get('custom_time_limit') or time_limit,
                tiempo_restante=formulario_parte_1.cleaned_data.get('custom_time_limit') or time_limit,
                # Agrega "True" o "False" para decir si el test es autocorregido
                test_autocorregido=formulario_parte_1.cleaned_data['autocorrect'] == 'true'
            )

            # Redirijo al usuario a la 1era pregunta del Test para que lo tome.
            # Esto redirige al cliente a la vista de Tomar el Test con Autocorrección (si lo quiere con autocorrección)
            if session.test_autocorregido:
                return redirect('tests_clientes:tomar_test_autocorregido', session_id=session.id, question_number=1)

            else:
                # Esto redirige al usuario a la vista de Tomar el Test sin autocorrección
                return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=1)

        else:  # Si el formulario no es válido, entonces le muestro un mensaje de error
            messages.error(request, f"Error al enviar el formulario")

            # Esto renderiza los formularios con los errores
            formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm(request.POST)
            formulario_parte_2 = ConfigureNewTestByTopicForm(request.POST)

    else:  # Esto renderiza los formularios si entras a esta página, es decir, si no has enviado el formulario
        formulario_parte_1 = ConfigurarTestSinIncluirPreguntasForm()
        formulario_parte_2 = ConfigureNewTestByTopicForm()

    # Prepare context for the form
    context = {
        'formulario_parte_1': formulario_parte_1,
        'formulario_parte_2': formulario_parte_2,
        'is_test_by_topic': is_test_by_topic,  # Booleano que dice si el test es por tema
        # 'test': test,
        # 'default_questions': default_questions,
    }

    return render(request, 'tests_clientes/configurar_test_por_tema_o_normativa.html', context)


""" Vista para Iniciar el Test.

El usuario NUNCA vera una pagina para esta vista. Esta vista solo va a redirigir al usuario a la vista de Tomar el Test
con el test que el cliente seleccionó para que el cliente pueda tomar el test.

Esta vista es como un checkpoint o un "guardia en la entrada de una discoteca" el cual crea una nueva sesión por
cada vez que el usuario tome el examen. Es decir, si el usuario interrumpe el test cuando todavía tenía tiempo, y 
luego vuelve a tomar el test, el usuario podrá continuar el test desde donde lo dejó, y con el tiempo que le quedaba.

Ademas, si el usuario toma varias veces el mismo test, en cada sesión puedo guardar cual fue la puntuación del usuario
en cada test (ej: saco 5 en el 1er intento, saco 7 en el 2do intento, etc).

Tengo que modificar esta vista para que el usuario pueda tomar varias veces el mismo test. Por los momentos, 
si el cliente ya ha tomado el test una vez, no podrá tomarlo de nuevo. Si el cliente intenta tomar el test de nuevo,
le saldrán los resultados de la primera vez que tomó el test.

I'll modify the iniciar_el_test view to allow users to take the exam multiple times. The key change is removing the 
check for cliente_entrego_este_test and always creating a new session.

Key changes:  
1) Removed the filter check for existing sessions.
2) Always create a new session when starting the test.
3) Each session will track its own answers and results independently.
Now users can take the test multiple times, and each attempt will be stored as a separate session in the database.

Now, modify the selected snippet from my template so that the list of tests looks like a datatable. Also, users can no 
longer take the test by clicking on the test name. Instead, you will have to render 2 new columns: one to choose the 
difficulty level of the exam, and another for starting the exam. The difficulty level could be a dropdown menu with 5 
difficulty levels. Then, if the user clicks on the button to start taking the exam, you need to put the difficulty 
level as an additional parameter to the "iniciar_el_test()" view. Also, I'll have to modify my iniciar_el_test() 
view and the URL from urls.py for that view so that it accepts the difficulty level as an additional parameter.

I want my users to be able to interrupt their exams, and if they click on that same exam, they'll be able to resume 
where they last left off. If they haven't submitted their exam, or if they haven't run out of time for that exam, users 
should be able to continue from where they last left off. The stuff you'll have to check to give me the 
functionality to be able to interrupt and continue an interrupted exam should be the iniciar_el_test() view, and my 
"SesionDelTest()" model. So please, tell me an algorithm to make it so that, if users abandon an incomplete exam, 
that users will be able to continue the exam from where they left off.
Here's how to modify the iniciar_el_test view to allow exam resumption:

1) Check for an existing incomplete session for this test
2) If found, verify the time hasn't expired
3) If time remains:
    - Find the last answered question
    - Redirect to that question number

4) If time expired:
    - Mark session as complete
    - Create a new session
5) If no incomplete session exists:
    - Create a new session as before

This allows users to:
    - Resume incomplete exams
    - Continue from their last answered question
    - Start fresh if previous session expired

Aquí es donde se guarda el tiempo para el cronómetro / temporizador del test. El tiempo se guarda en segundos.
Si quiero que el test sea más largo o más corto, debo modificarlo aquí.

Here, I attached a JS script that manages the timer of the exam, the views.py file with the backend of the exam (look 
at the tomar_test() and iniciar_test() views), and the template of taking the actual test. Well, i want a 
"save and exit" button in my template which will let users interrupt their exam so that they can continue with their 
test later of if they want. I'm already saving the answers given by the users each time that they click on "next" or 
"previous". What I want know is to be able to save the current time in tne timer so that, if users leave their exams, 
they will continue with the exact same amount of time that they previously had before exiting the exam, which will be 
executed when users click on the "save and exit" button that you'll need to generate. As of right now, I only check the 
timer on the backend in my views.py file. The problem with that is that the timer keeps going on even after exiting 
the exam, which I don't want. I only want the timer to run as long as the user is taking the exam. If users leave the 
exam, I want to store in my SesionDelTest model the time remaining from the timer on my front-end, so that the timer 
will resume from where it left off once users re-take the exam. I don't want the timer to keep running on on the 
backend after users interrupt their exam. Given all of these parameters, give me an algorithm on how to implemet this 
"save and exit" functionality, where the timer will be interrupted when users click on the "save and exit" button, and 
it will continue from where it left off after users resume their exam.

This implementation:  
    Stores remaining time in the database
    Stops the timer when user exits
    Resumes from stored time when user returns
    Preserves all existing answers
    Uses AJAX to save time without form submission

This view now redirects to the configuration page instead of starting the test directly.

If a user comes from the lista_de_tests() view, that the user will always be redirected to a new session. Otherwise, 
the user could be redirected to either an existing session, or a new session. The goal is to ensure that:

    If a user comes from the lista_de_tests() view, they are always redirected to a new session (i.e., a new 
    SesionDelTest instance is created, even if an incomplete session exists).

    If a user comes from any other view (e.g., lista_de_tests_incompletos()), the existing logic applies: they can 
    either resume an incomplete session (if one exists and hasn’t expired) or start a new session.

The query parameter approach is more robust but requires updating the links in your templates.

"""


@login_required(login_url='iniciar_sesion')
def iniciar_el_test(request, nombre_del_test):
    # # DEBUGGEO. Esto me imprime el nombre del test que el cliente seleccionó
    # print("Nombre del Test: ", nombre_del_test)

    # # DEBUGGEO. Esto me imprime el nivel de dificultad que el cliente seleccionó
    # print("Nivel de Dificultad: ", difficulty)

    # Esto coge la instancia del modelo de Test que tenga el nombre del test que el cliente seleccionó
    instancia_del_nombre_del_test = get_object_or_404(Test, id=nombre_del_test)

    # Check if the request includes a 'new_session' query parameter in the URL (ie: "?new_session=true").
    # Con esto, puedo chequear si el usuario vino de la vista de lista_de_tests() o no.
    force_new_session = request.GET.get('new_session') == 'true'

    # Si el usuario viene de la vista de lista_de_tests(), entonces siempre se creará una nueva sesión.
    # If forcing a new session, redirect to configure a new test
    if force_new_session:
        return redirect('tests_clientes:configurar_test', test_id=nombre_del_test)

    # Revisa si el usuario tiene un test incompleto para el test seleccionado
    existing_session = SesionDelTest.objects.filter(
        usuario=request.user,
        nombre_del_test=instancia_del_nombre_del_test,
        cliente_entrego_este_test=False,  # Si el cliente no ha entregado el test, entonces no ha terminado
        hora_del_fin_del_test__isnull=True  # Si el test no tiene la hora de finalización, entonces no ha terminado
    ).first()

    # Si el usuario autenticado tiene un test incompleto, entonces puede continuar desde donde lo dejó.
    # Esto no se va a cumplir para algunos de mis tests, ya que son sesiones existentes, pero que tienen NULL el tiempo
    # restante.
    # if existing_session and existing_session.tiempo_restante:

    # Solo revisaré si ya existe una sesion para este test para este usuario que tenga no haya sido entregado ni tenga
    # hora de finalización
    if existing_session:

        # Esto coge la última pregunta respondida para así iniciar desde la última pregunta sin responder
        # Get the last answered question number
        last_answer = RespuestaDelUsuario.objects.filter(
            sesion=existing_session
        ).order_by('-pregunta__id').first()

        # If there's a last answer, resume from that question, otherwise start from question 1
        question_number = 1
        if last_answer:
            questions = PreguntaDelTest.objects.filter(
                nombre_del_test=nombre_del_test
            ).order_by('id')

            # Busca el índice de la última pregunta respondida por el usuario
            for index, question in enumerate(questions, 1):
                if question.id == last_answer.pregunta.id:
                    question_number = index
                    break

        # Use saved remaining time instead of calculating from start time
        return redirect('tests_clientes:tomar_test',
                        session_id=existing_session.id,
                        question_number=question_number)

    # Esto era lo que me dejaba continuar el test desde donde lo dejé usando un cronometro desde el servidor /
    # backend. Sin embargo, no me funcionó.
    # TAL VEZ REACTIVE ESTO DESPUES.
    # if existing_session:
    #     # Check if time hasn't expired
    #     time_elapsed = (timezone.now() - existing_session.hora_de_inicio).total_seconds()
    #     time_remaining = existing_session.limite_de_tiempo - time_elapsed
    #
    #     if time_remaining > 0:
    #         # Get the last answered question number
    #         last_answer = RespuestaDelUsuario.objects.filter(
    #             sesion=existing_session
    #         ).order_by('-pregunta__id').first()
    #
    #         # If there's a last answer, resume from that question, otherwise start from question 1
    #         question_number = 1
    #         if last_answer:
    #             questions = PreguntaDelTest.objects.filter(
    #                 nombre_del_test=nombre_del_test
    #             ).order_by('id')
    #
    #             # Busca el índice de la última pregunta respondida por el usuario
    #             for index, question in enumerate(questions, 1):
    #                 if question.id == last_answer.pregunta.id:
    #                     question_number = index
    #                     break
    #
    #         # Esto rediriige al cliente a la vista de tomar el test, y va a la última pregunta que respondió
    #         return redirect('tests_clientes:tomar_test',
    #                         session_id=existing_session.id,
    #                         question_number=question_number)
    #     else:
    #         # Si se venció el tiempo para hacer el test, entonces marco el test como completo y creo uno nuevo
    #         existing_session.cliente_entrego_este_test = True
    #         existing_session.hora_del_fin_del_test = timezone.now()
    #         existing_session.save()

    # Si el usuario autenticado no tiene ningún test incompleto para este test, entonces puede tomar un nuevo test.

    # Esto redirige al usuario a la vista de Ajustes del test, en donde el cliente podrá seleccionar la dificultad
    return redirect('tests_clientes:configurar_test', test_id=nombre_del_test)

    # # Coge las preguntas para el test del modelo de PreguntaDelTest
    # questions = PreguntaDelTest.objects.filter(nombre_del_test=nombre_del_test)
    # if not questions.exists():
    #     messages.error(request, "No existen preguntas para este test.")
    #     return redirect('tests_clientes:lista_de_tests')
    #
    # # Ver si el cliente ya había entregado anteriormente este test.
    # # Si el cliente ya había entregado este test, entonces no se le permite tomarlo de nuevo.
    # # Si dejo cliente_entrego_este_test=False, entonces el cliente solo puede ver el resultado de su test al
    # # intentar tomarlo de nuevo. Mientras tanto, si dejo cliente_entrego_este_test=True, entonces al cliente le va
    # # a salir un mensaje de error 404 diciendo que no se encuentra una sesión con ese ID.
    #
    # # Crearé una sesión nueva cada vez que un cliente tome un test. Así, podrá tomar el test cuantas veces quiera.
    # session = SesionDelTest.objects.create(
    #     usuario=request.user,
    #     nombre_del_test=instancia_del_nombre_del_test,
    #     limite_de_tiempo=60,  # 1 minutos
    #     # limite_de_tiempo=1800,  # 30 minutos
    #     nivel_de_dificultad=difficulty  # Nivel de Dificultad del Test
    # )
    #
    # # session = SesionDelTest.objects.filter(
    # #     usuario=request.user,
    # #     nombre_del_test=instancia_del_nombre_del_test,
    # #     cliente_entrego_este_test=False     # Dejarlo en False por los momentos
    # # ).first()
    #
    # # if not session:
    # #     session = SesionDelTest.objects.create(
    # #         usuario=request.user,
    # #         nombre_del_test=instancia_del_nombre_del_test,
    # #         limite_de_tiempo=1800  # 30 minutos
    # #     )
    #
    # # Redirigir a la primera pregunta
    # return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=1)


""" Vista para que el cliente Haga el Test.

Ahora, para los clientes, creame un algoritmo para hacer que los usuarios puedan tomar un examen de seleccion simple 
como el que muestro en la captura de pantalla que te estoy adjuntando en este mensaje. Es decir, dame un algoritmo 
para crear una funcionalidad para mis clientes en mi web app de django para que puedan ir a las distintas preguntas de 
un examen, seleccionar una de las 3 o 4 preguntas, que tengan que hacer clic en solo una de las opciones. Luego, los 
usuarios deben poder enviar todas sus respuestas. Al final, la web app le dira cuantas preguntas tuvieron buenas, 
cuantas malas, y la puntuacion total, y si aprobaron o no. Y deben tener tiempo limitado. Si se acaba el tiempo, no 
podrán responder mas preguntas. Entonces, dame un algoritmo general para poder implantar esta funcionalidad en mi web 
app. Las preguntas del examen debe venir de los examenes que estan en mi modelo de Test().

Let’s design a complete algorithm and provide code snippets to implement a timed, single-selection exam functionality 
in your Django web app, similar to the one shown in the screenshot. The functionality will allow users to take an 
exam, select one answer per question, submit their responses, and get a score with pass/fail status, all within a 
time limit. Questions will be pulled from your Test model, and we’ll ensure best practices for a commercial web app.
Functionality Requirements
Based on your screenshot and description, here’s what we need:
Exam Interface:
Display one question at a time with 4 options (A, B, C, D).
Users can select only one option per question.
Navigation buttons: “Anterior” (Previous) and “Siguiente” (Next) to move between questions.
A “Finalizar” (Finish) button to submit the exam.
Timer:
A countdown timer (e.g., 4 minutes as shown in the screenshot).
If time runs out, the exam auto-submits, and users can no longer answer.
Submission & Scoring:
After submission (manual or auto), calculate:
Number of correct answers.
Number of incorrect answers.
Total score (e.g., 1 point per correct answer).
Pass/fail status (e.g., pass if score ≥ 70%).
Display results to the user.
Data Source:
Questions come from the Test model, filtered by exam name (e.g., “Granada 2023”).
User Experience:
Visual feedback (e.g., selected answer highlighted).
Progress indicator (e.g., question 1 of 5).
Responsive design for a clean UI.
Algorithm Overview
Models: Extend the Test model with an ExamSession model to track user answers and progress.
Views: Create views for starting the exam, displaying questions, handling answers, and showing results.
Frontend: Use JavaScript for the timer and dynamic interaction (e.g., selecting answers).
Templates: Render the exam interface and results page.
Logic:
Fetch questions from the Test model.
Track user answers and time remaining.
Submit answers and calculate scores.
1. Models
We need a model to track user sessions and answers.

Why:
ExamSession: Tracks each user’s exam attempt, including start/end time and score.
UserAnswer: Stores each answer, linking it to a question and session.
is_correct: Automatically calculated when saving an answer.
Run migrations after adding these models:

2. Views
We’ll create views to handle starting the exam, displaying questions, saving answers, and showing results.

Why:
start_exam: Initiates a new session and redirects to the first question.
take_exam: Handles displaying questions, saving answers, and navigation.
exam_results: Calculates and displays the results.
exam_list: Shows available exams to start.
3. URLs
Add the views to your URL configuration.

4. Templates
Exam List Template



Take Exam Template


Results Template

5. JavaScript for Timer
Add JavaScript to handle the countdown timer and auto-submit when time runs out.

Why: Automatically submits the form when time runs out and updates the timer display every second.
Run python manage.py collectstatic to ensure static files are collected.
6. Styling (Optional)
Add some basic CSS for a clean UI.


7. Best Practices for Commercial Use
Security:
All views are @login_required to ensure only authenticated users can access exams.
Validate question_number and session_id to prevent tampering.
User Experience:
Clear feedback with messages.
Progress tracking (e.g., “Question 1 of 5”).
Timer visibility and auto-submit on timeout.
Scalability:
Use pagination or lazy loading if exams have many questions.
Consider Celery for background tasks (e.g., calculating scores for large exams).
Logging:
Log exam starts, completions, and scores for auditing.
Testing:
Test edge cases (e.g., time running out, invalid submissions).
How It Works
User logs in and visits /tests/exams/ to see available exams.
They start an exam (e.g., /tests/exam/Granada 2023/start/).
They’re redirected to the first question with a timer.
They select an answer, navigate through questions, and submit when done or when time runs out.
Results are shown with a breakdown of correct/incorrect answers, score, and pass/fail status.
Next Steps
Test the functionality with a small set of questions.
Add more styling to match the screenshot’s design (e.g., green/red highlights for answers).
Consider adding a “Resume Exam” feature if users leave mid-exam.
Let me know if you’d like to dive deeper into any part (e.g., styling, additional features, or testing)!

===

This view handles the exam-taking process and has several key functions:

1. Initial Setup:
- Gets the exam session for the current user and verifies it hasn't been submitted yet using:

- Retrieves all questions for this test in order and counts them:

2. Validation Checks:
- Ensures the question number is valid
- Checks if the time limit has expired, and if so, marks the test as completed and redirects to results:


3. Answer Management:
- Gets or creates an answer record for the current question:

4. Form Processing:
- Handles POST requests for:
  - Saving answers when the user selects an option (A, B, C, or D)
  - Navigation between questions (next/previous)
  - Finishing the exam
- Note: There's a commented issue about the answer saving functionality needing JavaScript integration

5. Context Preparation:
- Prepares all necessary data for the template, including:
  - Current question and answer
  - Navigation information (current question number, total questions)
  - Time remaining
  - Session information

The view acts as a central controller for the exam-taking process, managing both the data storage and user interface 
flow.

In your code, questions are loaded one at a time, not in a loop.

Las preguntas del test son enviadas al template SIN USAR un "for" loop. Simplemente estoy creando varias páginas
dentro del mismo template, en donde el cada página representa una sola pregunta. Es decir, si hay 10 preguntas, 
entonces habrá 10 páginas en el template que usa esta misma vista, y cada página mostrará una sola pregunta. 
Básicamente, estoy creando paginación para las preguntas del test dentro de mi template, en donde cada pagina
de la paginación muestra 1 sola pregunta del test.

Necesito crear una cuadrícula en donde se van a mostrar enlaces a cada una de las preguntas, apra que el cliente 
pueda saltarse a cualquiera de las preguntas del test. Es decir, el cliente no tiene que estar limitado a solo ir de
manera secuancial a la pregunta anterior o siguiente al hacer clic en "siguiente" o "anterior". Puedo editar mi view 
para agarrar todas las preguntas de ese test, y enviarlo como una variable de jinja a mi template. 
Luego, usando un “for” loop de toda la vida, puedo renderizar cada una de esas preguntas en mi side navbar. No quiero 
renderizar el nombre de cada pregunta, ni la ID de cada pregunta. Lo que puedo es tomar el numero total de preguntas de 
ese test, y decir con un contador que, por cada pregunta in preguntas, que renderice un numero, y que le agregue un 1 
al contador. Asi, puedo renderizar en el grid todas las preguntas de un test, en donde cada pregunta tiene su respetivo 
numero, NO su ID (ejemplo, “1, 2, 3…” en lugar de “25, 30, 27, …”)

Igual, ya estoy enviando el numero total de preguntas con una variable de jinja en el view de iniciar_test(). Solo me 
falta enviar la variable con todas las preguntas de ese test via jinja a mi template de tomar_test.html.

To be able to save the selected answer from the currently selected question whenever you clic on any link of the 
question grid on the sidebar, you'll have to add a new condition in your view's POST handler.

This solution:
    Prevents default link behavior
    Gets the currently selected answer
    Sends it via POST before navigation
    Handles the save in your view
    Redirects to the selected question

This solution:
    Prevents default link behavior
    Gets the currently selected answer
    Sends it via POST before navigation
    Handles the save in your view
    Redirects to the selected question

Simplifiqué el snippet con los "if" statements de la variable "action" usando un match / case, para que así sea más 
fácil de leer.

We need to modify the tomar_test view to handle custom questions.

Quiero que las preguntas respondidas en el test se coloreen de verde, por lo que creé una nueva variable que almacena
las preguntas respondidas por el cliente. Lo que hago es buscar todas las respuestas del usuario autenticado para
el test seleccionado que está tomando. Luego, le asignare un número empezando por el "1" hasta el último número de
preguntas que tiene el test. Luego, enviaré esa respuesta respondida con ese número a mi template con una variable
de Jinja. Lo de numerar cada pregunta empezando por el "1" es porque cada pregunta tiene su propia ID
(por ejemplo, "48" o "50"). Pero no quiero que se muestren los numeros "48" o "50". Lo que quiero es que la primera
pregunta del test comience desde el "1", la segunda pregunta se marque como un "2", etc.

Quiero que, al tomar el test, que solo se guarden las respuestas y solo se creen registros en el modelo de
RespuestaDelUsuario cuando el cliente seleccione una de las respuestas. No se deben crear registros vacíos 
ni se deben introducir respuestas vacías en el campo de respuesta seleccionada de ese modelo. Pero ya cree una variable
Jinja que envía las respuestas seleccionadas siempre que entres al template de Tomar el Test. Por lo tanto, 
debo darle un valor por defecto a esa variable Jinja. Pero del resto, para guardar las respuestas seleccionadas 
por el usuario, las cuales tomaré con un fetch() usando una función de JavaScript, tengo que esperar hasta que el
usuario haga un POST request. De esta manera, lograré lo siguiente:
    Records are only created when users actually submit an answer
    No empty records are created when just viewing questions
    Existing answers can still be retrieved for display

Para evadir el bug que hacía que en el primer milisegundo del temporizador se mostrara todo el tiempo en segundos
en lugar de minutos, formatee desde aquí en el template el tiempo en minutos y segundos.

**Problem 1: No validation for empty tests**
The view needs to check if the test has any questions before allowing access. Add a check at the beginning of the view 
and redirect back with an error message if no questions are found.

This change will:
1. Check if any questions exist for the test
2. Display an error message if none found
3. Redirect back to the configuration page
4. Prevent the infinite redirect loop

This validation should be added before any other question-related operations to fail fast and provide clear feedback 
to users.

If option D (the 4th option) of a question is NULL or None, I don't want to show the 4th option to the user. That is, if 
the fourth option is NULL, I want the user to only select among 3 options for that question, not 4. So, you'll need to 
look at the selected view, and my "disposición de opciones de cada pregunta del test" template to figure out how to not 
to render the 4th option if the 4th option is NULL. Option D is already optional in the PreguntaDelTest() model.

To only render 3 options if there's no 4th option, I added a boolean flag to indicate if option D exists. It only 
renders the option markup if it's A, B, C or if it's D and exists. It maintains all existing functionality for valid 
options. It handles validation correctly since option D is already optional in your model.
"""


@login_required(login_url='iniciar_sesion')
def tomar_test(request, session_id, question_number):
    # Esto crea una sesión para que el cliente tome el test. Así, sabremos cuánto tiempo le queda al cliente para
    # terminar el test, y se puede registrar cuando empezó y cuando terminó el test.
    # Gets the exam session for the current user and verifies it hasn't been submitted yet.
    session = get_object_or_404(SesionDelTest, id=session_id, usuario=request.user, cliente_entrego_este_test=False)

    # Esto evitar un monton de bugs que ocurrían si intentas tomar un test sin preguntas
    if not PreguntaDelTest.objects.filter(nombre_del_test=session.nombre_del_test).exists():
        # Si no hay preguntas para este test, entonces le muestro un mensaje de error al cliente
        messages.error(request, "Este test no tiene preguntas asignadas.")

        # Redirijo al cliente a la vista de configurar un nuevo test a generar
        return redirect('tests_clientes:configurar_nuevo_test_a_generar')

    # Esto formatea el tiempo en minutos y segundos al iniciar el temporizador
    def format_time(seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:02d}"

    # Check if time is unlimited (boolean)
    tiempo_ilimitado = session.limite_de_tiempo is None

    # Solo voy a ponerle el formato correcto al tiempo restante si el tiempo no es ilimitado.
    # Si la sesion del test tiene un tiempo restante, entonces se inicia el cronómetro desde ese tiempo restante.
    if not tiempo_ilimitado and session.tiempo_restante is not None:
        inicio_temporizador = format_time(session.tiempo_restante)
    elif not tiempo_ilimitado:

        # Si la sesión del test no tiene un tiempo restante, entonces se inicia el cronómetro desde el principio
        # Esto inicia el temporizador desde el principio.
        # Esto lo voy a modificar después para que el cliente pueda decidir cuanto tiempo quiere.
        # Tomaré el límite de tiempo del modelo de SesionDelTest
        inicio_temporizador = format_time(session.limite_de_tiempo)
    else:
        inicio_temporizador = None

    # # Si la sesion del test tiene un tiempo restante, entonces se inicia el cronómetro desde ese tiempo restante
    # if session.tiempo_restante is not None:
    #
    #     inicio_temporizador = session.tiempo_restante
    #     # time_remaining = session.tiempo_restante
    #
    # # Si la sesión del test no tiene un tiempo restante, entonces se inicia el cronómetro desde el principio
    # else:
    #     # Esto inicia el temporizador desde el principio.
    #     # Esto lo voy a modificar después para que el cliente pueda decidir cuanto tiempo quiere.
    #     # Tomaré el límite de tiempo del modelo de SesionDelTest
    #     inicio_temporizador = session.limite_de_tiempo  # 30 minutos
    #
    #     # inicio_temporizador = 60  # 1 minuto

    # # Check if there are custom questions for this session.
    # # Esto llama a la función get_custom_question_ids() del modelo de SesionDelTest para agarrar las preguntas
    # # seleccionadas por el cliente para un test customizado.
    # custom_question_ids = session.get_custom_question_ids()
    #
    # # Retrieve questions - either custom selection or all questions
    # if custom_question_ids:
    #     questions = PreguntaDelTest.objects.filter(
    #         nombre_del_test=session.nombre_del_test,
    #         id__in=custom_question_ids
    #     ).order_by('id')

    # Esto coge todas las preguntas si el usuario no seleccionó preguntas para un test customizado
    # else:

    # Retrieves all questions for this test in order
    questions = PreguntaDelTest.objects.filter(
        nombre_del_test=session.nombre_del_test
    ).order_by('id')

    # Esto no lo necesito. Si no había tiempo restante guardado en la sesión, iniciaré el temporizador desde el inicio
    #     time_elapsed = (timezone.now() - session.hora_de_inicio).total_seconds()
    #     time_remaining = max(0, session.limite_de_tiempo - int(time_elapsed))

    # # Retrieves all questions for this test in order
    # questions = PreguntaDelTest.objects.filter(nombre_del_test=session.nombre_del_test).order_by('id')

    # Número total de preguntas de este test
    total_questions = questions.count()

    # Validate question number. Ensures the question number is valid.
    # La variable "question_number" es el 3er parámetro que se pasa en la URL (ver los 3 parámetros de este view.)
    if question_number < 1 or question_number > total_questions:
        messages.error(request, "Invalid question number.")
        return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=1)

    # Otro cronometro del backend. Esto no lo necesito, porque tomare el tiempo del front-end y de SesionDelTest
    # # Check if time is up.
    # # Esto chequea server-side si aun queda tiempo. Si se acaba el tiempo, entonces se marca el test como completado
    # time_elapsed = (timezone.now() - session.hora_de_inicio).total_seconds()
    # time_remaining = max(0, session.limite_de_tiempo - int(time_elapsed))
    #
    # # Checks if the time limit has expired, and if so, marks the test as completed and redirects to results.
    # if time_remaining <= 0:
    #     session.cliente_entrego_este_test = True
    #     session.hora_del_fin_del_test = timezone.now()
    #     session.save()
    #     return redirect('tests_clientes:resultados_del_test', session_id=session.id)

    # Get the current question
    pregunta = questions[question_number - 1]  # Gets a single question based on the index

    # Dado que siempre debo tener algo almacenado en esta variable, usaré un filter() para darle un valor sin crear un
    # nuevo registro en el modelo de RespuestaDelUsuario.
    # Get or create the user’s answer for the current question.
    # GET Request only - doesn't create anything if it doesn't exist.
    user_answer = RespuestaDelUsuario.objects.filter(
        sesion=session,
        pregunta=pregunta
    ).first()  # Returns None if no answer exists

    # user_answer, created = RespuestaDelUsuario.objects.filter(
    #     sesion=session,
    #     pregunta=pregunta,
    #     # defaults={'respuesta_seleccionada': ''}
    #     # # BUG: no puedo tomar el testo si pongo "None" aqui
    #     # defaults={'respuesta_seleccionada': None}
    # )

    # Si el usuario hace un POST request en el template de tomar_test.html
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_answer = request.POST.get('selected_answer')

        # Saving answers when the user selects an option (A, B, C, or D).
        # Esto debería llamar a una API para agarrar mi respuesta del front-end usando JS, y luego lo enviaría aquí
        # en mi back-edn para agarrar la respuesta seleccionada del usuario y guardarla en mi modelo de
        # RespuestaDelUsuario. SIN EMBARGO, no hay ningún "save_answer" ni en el template ni en exam_timer.js. Por
        # lo tanto, este snippet jamas se ejecutara. Esa es la razon por la que nunca se guarda la respuesta
        # seleccionada del usuario en mi modelo de RespuestaDelUsuario cuando el cliente toma el test.
        # if action == 'save_answer' and selected_answer in ['A', 'B', 'C', 'D']:
        #     user_answer.respuesta_seleccionada = selected_answer
        #     user_answer.save()

        # Save the answer if one was selected
        if selected_answer in ['A', 'B', 'C', 'D']:
            # Esto crea o actualica un registro en el modelo de RespuestaDelUsuario SOLO si el cliente selecciona una
            # respuesta
            user_answer, created = RespuestaDelUsuario.objects.get_or_create(
                sesion=session,
                pregunta=pregunta,
                defaults={'respuesta_seleccionada': selected_answer}
            )

            # Si el registro no existe, entonces crea la respuesta seleccionada
            if not created:
                user_answer.respuesta_seleccionada = selected_answer
                user_answer.save()

        # Navigation between questions (next/previous)
        # Navigation and action handling using match/case
        match action:
            case 'next' if question_number < total_questions:
                return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=question_number + 1)

            case 'previous' if question_number > 1:
                return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=question_number - 1)

            # Esto me permite guardar la respuesta seleccionada en caso de que cliques los enlaces en la barra lateral
            case 'goto':
                # The answer is already saved above
                # The redirect will happen client-side
                return JsonResponse({'status': 'success'})

            # Si el usuario termina el test o se le acaba el tiempo
            case 'finish':
                # Actualizo los Datos de la Sesion en SesionDelTest
                session.cliente_entrego_este_test = True
                session.hora_del_fin_del_test = timezone.now()
                session.save()
                # Redirijo a la vista de resultados
                return redirect('tests_clientes:resultados_del_test', session_id=session.id)

        # if action == 'next' and question_number < total_questions:
        #     return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=question_number + 1)
        # elif action == 'previous' and question_number > 1:
        #     return redirect('tests_clientes:tomar_test', session_id=session.id, question_number=question_number - 1)
        #
        # # Esto me permite guardar la respuesta seleccionada en caso de que cliques los enlaces en la barra lateral
        # elif action == 'goto':
        #     # The answer is already saved above
        #     # The redirect will happen client-side
        #     return JsonResponse({'status': 'success'})
        #
        # # Si el usuario termina el test o se le acaba el tiempo
        # elif action == 'finish':
        #     # Actualizo los Datos de la Sesion en SesionDelTest
        #     session.cliente_entrego_este_test = True
        #     session.hora_del_fin_del_test = timezone.now()
        #     session.save()
        #
        #     # Redirijo a la vista de resultados
        #     return redirect('tests_clientes:resultados_del_test', session_id=session.id)

    # Get all answered questions for this session
    answered_questions = list(RespuestaDelUsuario.objects.filter(
        sesion=session,
        respuesta_seleccionada__isnull=False  # Only get questions with actual answers
    ).values_list('pregunta__id', flat=True))

    # Convert question IDs to 1-based question numbers
    answered_question_numbers = []
    for index, question in enumerate(questions, 1):
        if question.id in answered_questions:
            answered_question_numbers.append(index)

    # Add this before the context dictionary.
    # Check if current question is bookmarked by the user.
    pregunta_esta_guardada = PreguntaGuardadaPorElUsuario.objects.filter(
        usuario=request.user,
        pregunta=pregunta,
        test=session.nombre_del_test
    ).exists()

    # Prepares all necessary data for the template
    context = {
        'session': session,
        'question': pregunta,  # Sends just one question to the template using Jinja
        'question_number': question_number,
        'total_questions': total_questions,  # Número total de preguntas de este test
        'user_answer': user_answer,
        # 'inicio_temporizador': format_time(inicio_temporizador),  # Esto inicia el cronómetro desde 0 en minutos
        'inicio_temporizador': inicio_temporizador,  # Esto inicia el cronómetro desde 0 en minutos
        # 'inicio_temporizador': inicio_temporizador,  # Esto inicia el cronómetro desde 0
        # 'time_remaining': time_remaining,   # Esto inicia el cronómetro desde 0
        'questions': questions,  # Todas las instancias de las preguntas de este test
        'answered_questions': answered_question_numbers,  # Preguntas que ya han sido respondidas
        'has_option_d': bool(pregunta.opcion_d),  # Will be True if Option D exists and is not NULL / empty
        'pregunta_esta_guardada': pregunta_esta_guardada,  # Esto revisa si la pregunta está guardada por el usuario
        'tiempo_ilimitado': tiempo_ilimitado,  # Este booleano me dice si el tiempo es ilimitado o no
    }

    # Render the exam template
    return render(request, 'tests_clientes/tomar_test.html', context)


""" Vista de Resultados del Test.

Esto debe tomar las respuestas del Usuario de RespuestasDelUsuario, y calcular cuantas preguntas tuvieron buenas,
cuantas preguntas tuvieron malas, y la puntuación total. Luego, debe mostrarle al cliente si aprobó o no el test.

Now, create me a match / case with 5 conditions. In it, take the difficulty level of the exam from the SesionDelTest 
model (which is in session.nivel_de_dificultad). Then, depending on the difficulty, the score will be calculate 
differently. In the easiest difficulty (difficulty=1), leave the default calculation for the score. However, in the 
higher difficulties (from "2" to "5"), you will have to calculate the score differently. If the difficulty is "2", 4 
wrong answers will eliminate 1 correct answer. Meanwhile, for difficulty "3", 3 wrong answers will eliminate 1 right 
answer. And so on and so forth until you reach the 5th difficulty, in which 1 wrong answer eliminates 1 right answer. 
Considering all this, create the 5 conditions using a match / case statement in which you calculate the final exam 
score depending on the difficulty level chosen by the user.

This code:
1) Uses Python's match/case syntax
2) Calculates penalties based on difficulty level
3) Uses integer division // to calculate eliminated answers
4) Uses max(0, ...) to prevent negative scores
5) Has a default case for safety.

Now, I want to print the difficulty level in my template. So, from this view, within the match / case, create a new 
variable which will store the name of the difficulty level. Here are the names for each difficulty level (i.e.: 
Difficulty "1" is called "Errores no restan"). Well, take these names, and create a new variable in my 
resultados_del_test view to store the name of that difficulty level in that variable. Then, in the match case, change 
the name of the difficulty depending on whether the difficulty is "1", "2", "3", etc. Then, send the name of that 
difficulty level via jinja to my template.

En la variable con el numero total de preguntas debo meter todas las preguntas del test. Esto lo saco agarrando el 
test seleccionado, y todas las preguntas del test que estaban asignadas a ese test en específico.

What I want is to select the exam that the user took and submitted (from the Test() model), count the number of 
questions assigned to that exam (from the PreguntaDelTest() model, which should have the selected test assigned to it 
via a many to many field), and then store it into this variable.

I want to differentiate between wrong answers and empty answers. I need to differentiate between and incorrect answer 
with an empty answer, since I will later only penalize the user if they answer wrongly. I won't penalize their exam 
score if they leave an answer empty. 

To do this, I will:
    1) Correctly counts wrong answers by ensuring they have a selected answer.
    2) Calculates empty answers by subtracting correct and wrong answers from total.
    3) Separates empty answers from wrong answers for penalty calculations.

Esta vista mostrará el resultado con la nota total, pero NO mostrará cuales preguntas estaban buenas y cuales estaban
malas. Eso lo mostraré en la vista para repasar el test. 

Quiero que los resultados se muestren en en escala de 0 a 10, no en porcentaje. Es decir, quiero que la nota máxima sea 
10.

Necesito enviar también el número de preguntas que el cliente dejó en blanco.
"""


@login_required(login_url='iniciar_sesion')
def resultados_del_test(request, session_id):
    # Esto coge la sesión del test del modelo de SesionDelTest
    session = get_object_or_404(SesionDelTest, id=session_id, usuario=request.user)

    # Luego, debo coger las respuestas que dió este cliente de RespuestasDelUsuario() para este test
    respuestas_del_usuario = RespuestaDelUsuario.objects.filter(sesion=session)

    # answers = session.answers.all()

    # Calcula los Resultados

    # Numero total de preguntas (es un integer)
    # Get total questions from PreguntaDelTest for this test
    numero_total_de_preguntas = PreguntaDelTest.objects.filter(
        nombre_del_test=session.nombre_del_test
    ).count()

    # numero_total_de_preguntas = respuestas_del_usuario.count()

    # Numero de respuestas que el cliente respondió correctamente
    respuestas_correctas = respuestas_del_usuario.filter(es_correcto=True).count()

    # Número de respuestas incorrectas (respondidas, pero incorrectas)
    respuestas_incorrectas = respuestas_del_usuario.filter(
        es_correcto=False,
        respuesta_seleccionada__isnull=False  # Ensure answer is not empty
    ).count()

    # Número total de respuestas vacías (no respondidas)
    respuestas_vacias = numero_total_de_preguntas - (respuestas_correctas + respuestas_incorrectas)

    # respuestas_incorrectas = numero_total_de_preguntas - respuestas_correctas

    # Esta variable guarda el nombre de la dificultad del test. Aquí la inicializo.
    nombre_de_dificultad = ""

    # Hay 5 niveles de dificultad. Dependiendo de la dificultad, la puntuación será diferente.
    # Calculate adjusted correct answers based on difficulty level.
    # Dependiendo de la dificultad, le pondré el nombre que le corresponde a la dificultad.
    match session.nivel_de_dificultad:
        case "1":
            # Easiest: wrong answers don't affect score
            nombre_de_dificultad = "Errores No Restan"
            score = (respuestas_correctas / numero_total_de_preguntas) * 10 if numero_total_de_preguntas > 0 else 0

        case "2":
            # 4:1 penalty: every 4 wrong answers eliminate 1 correct answer
            nombre_de_dificultad = "4:1 (4 respuestas malas restan 1 buena)"
            respuestas_eliminadas = respuestas_incorrectas // 4
            respuestas_correctas_ajustadas = max(0, respuestas_correctas - respuestas_eliminadas)
            score = (respuestas_correctas_ajustadas / numero_total_de_preguntas) * 10

        case "3":
            # 3:1 penalty: every 3 wrong answers eliminate 1 correct answer
            nombre_de_dificultad = "3:1 (3 respuestas malas restan 1 buena)"
            respuestas_eliminadas = respuestas_incorrectas // 3
            respuestas_correctas_ajustadas = max(0, respuestas_correctas - respuestas_eliminadas)
            score = (respuestas_correctas_ajustadas / numero_total_de_preguntas) * 10

        case "4":
            # 2:1 penalty: every 2 wrong answers eliminate 1 correct answer
            nombre_de_dificultad = "2:1 (2 respuestas malas restan 1 buena)"
            respuestas_eliminadas = respuestas_incorrectas // 2
            respuestas_correctas_ajustadas = max(0, respuestas_correctas - respuestas_eliminadas)
            score = (respuestas_correctas_ajustadas / numero_total_de_preguntas) * 10

        case "5":
            # 1:1 penalty: each wrong answer eliminates 1 correct answer
            nombre_de_dificultad = "1:1 (1 respuesta mala resta 1 respuesta buena)"
            respuestas_correctas_ajustadas = max(0, respuestas_correctas - respuestas_incorrectas)
            score = (respuestas_correctas_ajustadas / numero_total_de_preguntas) * 10

        case _:
            # Default case: use easiest scoring method
            nombre_de_dificultad = "Errores No Restan"
            score = (respuestas_correctas / numero_total_de_preguntas) * 10 if numero_total_de_preguntas > 0 else 0

    # # Dificultad 1 (la más fácil): Las respuestas incorrectas no te restan ninguna correcta
    # score = (respuestas_correctas / numero_total_de_preguntas) * 100 if numero_total_de_preguntas > 0 else 0
    #
    # # Dificultad 2: Caso 4:1: Cuatro respuestas incorrectas restan una correcta
    #
    #
    # # Dificultad 3: Caso 3:1: Tres respuestas incorrectas restan una correcta
    #
    # # Dificultad 4: Caso 2:1: Dos respuestas incorrectas restan una correcta
    #
    # # Dificultad 5 (la más difícil): Caso 1:1: Una respuesta incorrecta resta una correcta

    passed = score >= 5  # El cliente necesita un 50% para aprobar el test

    # Esto guarda la puntuación en el modelo de SesionDelTest
    session.puntuacion = score

    # Esto termina de guardar los cambios en el modelo de SesionDelTest
    session.save()

    context = {
        'session': session,
        'total_questions': numero_total_de_preguntas,
        'correct_answers': respuestas_correctas,
        'incorrect_answers': respuestas_incorrectas,
        'score': score,
        'passed': passed,
        'respuestas_del_usuario': respuestas_del_usuario,
        'nombre_de_dificultad': nombre_de_dificultad,  # Nombre de la dificultad
        'respuestas_vacias': respuestas_vacias,  # Número de Respuestas vacías
    }
    return render(request, 'tests_clientes/resultados_del_test.html', context)


""" Vista para la Lista de Tests.

Aquí, tanto los administradores como los clientes podrán ver todos los tests que están disponibles para tomar.

O ELIMINAR ESTA VISTA PARA LOS CLIENTES MAS TARDE, O MODIFICARLA PARA QUE 1 usuario no pueda ver los tests generados proceduralmente por
otro usuario.

Decidí que solo los administradores pueden entrar aquí para ver todos los tests de toda la base de datos. Modificaré
esta vista para que solo los administradores puedan entrar en él. Los clientes no podrán entrar aquí. Si entran
aquí, les mostraré un mensaje de error.
"""


@login_required(login_url='iniciar_sesion')
def lista_de_tests(request):
    # Si el usuario que entra aquí no es un administrador, mostrarle un mensaje de error.
    if not request.user.is_superuser:
        # print("USTED NO DEBE ESTAR AQUI. El usuario no es un administrador.")

        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('tests_clientes:menu_principal_tests')

    # print("Esto se ejecuta en el view de lista de tests.")

    # Si el usuario es un administrador, podrá ver esta página.
    # Lista de todos los Tests como instancias
    nombres_de_los_tests = Test.objects.all().distinct()
    # nombres_de_los_tests = Test.objects.values_list('nombre_del_test', flat=True).distinct()
    return render(request, 'tests_clientes/listas-de-tests/lista_de_tests.html', {
        'nombres_de_los_tests': nombres_de_los_tests
    })


# """ Vista con la Lista de Tests Por Año (Por Examen).
#
# Solo se van a renderizar aquí los tests que tengan marcado "Año" en el campo de "Tipo" del modelo de Test().
# """
#
#
# @login_required(login_url='iniciar_sesion')
# def lista_de_tests(request):
#     # Lista de todos los Tests como instancias
#     nombres_de_los_tests = Test.objects.all().distinct()
#     # nombres_de_los_tests = Test.objects.values_list('nombre_del_test', flat=True).distinct()
#     return render(request, 'tests_clientes/lista_de_tests.html', {
#         'nombres_de_los_tests': nombres_de_los_tests
#     })


""" Vista para la Lista de los Resultados de los Tests pasados de un Cliente.

Aquí, el cliente podrá ver los resultados de los tests que ha tomado en el pasado.

Esto se le genera al cliente, y solo puede verlo el cliente que genero proceduralmente sus tests. Esto NO podrá
verlo otros usuarios. Cada usuario solo podra ver sus propios resultados aquí.
"""


@login_required(login_url='iniciar_sesion')
def lista_de_resultados_de_tests_pasados(request):
    # Lista de todos los Tests como instancias del usuario autenticado
    sesiones = SesionDelTest.objects.filter(usuario=request.user).order_by('-hora_de_inicio')
    return render(request, 'tests_clientes/lista_de_resultados_de_tests_pasados.html', {
        'sesiones': sesiones
    })


""" Vista con la Lista de Tests Incompletos de un Cliente.

Aquí saldrá la lista de todos los Tests incompletos que el cliente ha interrumpido, para que así los pueda continuar y
terminar.

Solo necesito coger todos los tests del cliente actual, pero que no estén marcados como entregados, y que tengan 
vacío el campo de la hora de finalización. Luego, los muestro en una tabla en mi template.

I want to render the number of the last answered question in the lista_de_tests_icnompletos() view to send it as a 
jinja variable to my lista_de_tests_interrumpidos template. So, get the last answered question from all of these 
interrupted sessions, and send them as a jinja variable to my "lista de tests incompletos" template. If there isn't 
any answered question in one of the sessions, make the question number "1" by default.

This modification:
    Gets the last answered question for each session
    Determines its 1-based index number
    Defaults to 1 if no questions were answered
    Sends both session and question number to the template
    Updates the template to use the correct question number in the URL
"""


@login_required(login_url='iniciar_sesion')
def lista_de_tests_incompletos(request):
    # Lista de todas las Sesiones con todos los Tests incompletos del usuario autenticado
    sesiones_con_tests_incompletos = SesionDelTest.objects.filter(usuario=request.user, cliente_entrego_este_test=False,
                                                                  hora_del_fin_del_test__isnull=True).order_by(
        '-hora_de_inicio')

    # Create a list to store sessions with their last answered question numbers
    sesiones_con_ultima_pregunta = []

    for sesion in sesiones_con_tests_incompletos:
        # Get the last answered question for this session
        ultima_respuesta = RespuestaDelUsuario.objects.filter(
            sesion=sesion,
            respuesta_seleccionada__isnull=False  # Only get questions with answers
        ).order_by('-pregunta__id').first()

        # Get all questions for this test to determine the question number
        preguntas = PreguntaDelTest.objects.filter(nombre_del_test=sesion.nombre_del_test).order_by('id')

        # Find the question number (1-based index)
        if ultima_respuesta:
            for index, pregunta in enumerate(preguntas, 1):
                if pregunta.id == ultima_respuesta.pregunta.id:
                    numero_ultima_pregunta = index
                    break
        else:
            numero_ultima_pregunta = 1  # Default to first question if none answered

        # A la variable con cada sesión, le agregarñe la última pregunta respondida y otros parámetros
        sesiones_con_ultima_pregunta.append({
            'sesion': sesion,
            'ultima_pregunta': numero_ultima_pregunta
        })

    # Esto renderiza el template con los tests interrumpidos
    return render(request, 'tests_clientes/listas-de-tests/lista_de_tests_interrumpidos.html', {
        'sesiones_con_tests_incompletos': sesiones_con_ultima_pregunta  # Metere las sesiones con la ultima pregunta
        # 'sesiones_con_tests_incompletos': sesiones_con_tests_incompletos
    })


""" Vista de la API para guardar el Tiempo Restante de un Test Incompleto al Guardar y Salir del Test.

Cuando el usuario clique en "Guardar y Salir" en la vista de tomar el test, se le guardará el tiempo restante que le
quedaba al usuario para terminar el test en el modelo de SesionDelTest.

El usuario solo podrá aceder a esta API con un POST request.
"""


@require_POST
@login_required
def save_time(request):
    # Esto coge el JSON que se envía desde el front-end
    data = json.loads(request.body)

    # Esto coge el ID de la Sesión del Test seleccionado del JSON enviado desde el fetch() en el front-end
    session_id = data.get('session_id')

    # Esto coge el tiempo restante del JSON enviado desde el fetch() en el front-end
    remaining_time = data.get('remaining_time')

    # Esto coge la el Test Incompleto del modelo de SesionDelTest con un get()
    session = get_object_or_404(SesionDelTest,
                                id=session_id,
                                usuario=request.user)

    # Esto guarda el tiempo restante en el campo de tiempo restante de la Sesion del Test seleccionado
    session.tiempo_restante = remaining_time

    # Esto guarda los cambios en el Test seleccionado de SessionDelTest
    session.save()

    return JsonResponse({'status': 'success'})


""" Vista para Repasar un Test Terminado.

Esta vista mostrará todas las preguntas del test, y mostrará cuales preguntas estaban buenas y cuales estaban malas.

Se usará código muy similar al de la vista de tomar_test(), pero con algunas modificaciones para mostrar las
respuestas correctas e incorrectas, y no tendrá el temporizador activado.

Esto también te permite ir a la pregunta siguiente y anterior al clicar en "siguiente" y "anterior", sin la necesidad
de tener que agregarles uan función de JavaScript a esos 2 botones.

This code retrieves a single question from the `preguntas_del_test` queryset using index-based access. Here's what it 
does specifically:

The line `pregunta = preguntas_del_test[question_number - 1]` gets a single question based on the `question_number` 
parameter passed to the view. Since Python uses zero-based indexing but the question numbers in the URL start from 1, 
it subtracts 1 from `question_number` to get the correct array index.

For example:
- If `question_number` is 1, it accesses index 0 (`question_number - 1 = 0`)
- If `question_number` is 5, it accesses index 4 (`question_number - 1 = 4`)

The snippet that gives numbers to answered questions creates a list of question numbers that have been answered by the 
user in a completed test. Here's how it works:

The code starts by creating an empty list `answered_question_numbers`. Then, it iterates through all test questions 
using `enumerate(preguntas_del_test, 1)`, which provides both the index (starting at 1) and the question object.

For each question, it checks if the question's ID exists in `preguntas_respondidas` (a list of answered question IDs) 
using `if q.id in preguntas_respondidas`. If found, it adds the 1-based index number to `answered_question_numbers`.

For example:
- If questions 1, 3, and 5 were answered, the list would contain `[1, 3, 5]`
- If no questions were answered, the list would remain empty `[]`
- If all questions were answered, the list would contain all numbers from 1 to the total number of questions

This list is later used in the template to highlight or mark which questions have been answered when reviewing the 
completed test.

Si quiero marcar una respuesta como correcta o incorrecta, crearé 2 booleanos: una que me dice si la respuesta
es correcta, y otra que me dice si es incorrecta. Si ambos booleanos son falsos, la respuesta se considerará vacía.
Mientras tanto, si uno de los booleanos es verdadero, la respuesta se considerará como respondida. Si el booleano
de la respuesta correcta es verdadero, la respuesta se considerará correcta. Si el booleano de la respuesta incorrecta
es verdadero, la respuesta se considerará incorrecta. Luego, enviaré ese booleano en una variable Jinja a mi template.

Pues, si el booleano de la respuesta correcta en mi template es verdadero, marcaré la respuesta como correcta. Mientras 
tanto, si el booleano de la respuesta incorrecta es verdadero, marcaré la respuesta como incorrecta. Si los booleanos 
son falsos, no renderizaré nada. Solo renderizaré algo en el template si alguno de los booleanos de las respuestas
correctas o incorrectas es "True".

Each record of the RespuestaDelUsuario() already stores if the user gave a correct answer to a question or not. The 
"es_correcto" field from the RespuestaDelUsuario() model is a boolean that automatically turns to "True" if the answer 
given by the user is the same as the real answer for the question. Otherwise, it turns to "False". So, I don't need to 
compare the questions between the PreguntaDelTest() model and the RespuestaDelUsuario() to see if the questions was 
correct or not in the repasar_test_finalizado() view. What I need to compare is the "es_correcto" field for the 
RespuestaDelUsuario with the question from the PreguntaDelTest() model. So, in my repasar_test_finalizado, I will use 
the most efficient way to send all the answered questions with the correct answer from the RespuestaDelUsuario as a 
jinja variable to my tomar_test template.

Para hacer que en el grid de preguntas en la mitad derecha del navegador las preguntas respondidas correctamente se
vean verdes, las incorrectas se vean rojas, y las vacías se vean en blanco, cree 4 nuevos "arrays" o listas. En
las primeras 2 listas, metí todas las preguntas del test, y todas las respuestas del usuario para la sesión actual.
Luego, en las últimas 2 listas, metí todas las preguntas que fueron respondidas correctamente, y todas las preguntas
que fueron respondidas incorrectamente. Luego, voy a enviar al template las 2 últimas listas como variables Jinja.
Es decir, voy a enviar las listas con la lista de preguntas respondidas correctamente, y la lista de preguntas
respondidas incorrectamente. En estas 2 últimas listas o "arrays" voy a insertar el número del índice de cada
pregunta respondida. Es decir, si hay 10 preguntas, voy a meter los números "1", "2", "3", etc, por cada pregunta.
Pues, si las preguntas "1", "2", y "3" fueron respondidas correctamente, entonces, cuando las renderice en el template,
revisaré si los números "1", "2", y "3" están en la lista de preguntas respondidas correctamente. De ser así,
les asignaré una clase CSS que las ponga en verde. Mientras tanto, si las preguntas "4", "5", y "6" fueron
respondidas incorrectamente, entonces, cuando las renderice en el template, revisaré si los números "4", "5", y "6"
están en la lista de preguntas respondidas incorrectamente. De ser así, les asignaré una clase CSS que las ponga
en rojo. Finalmente, si las preguntas "7", "8", "9" y "10" no fueron respondidas, entonces, cuando las renderice en el
template, no les asignaré ninguna clase CSS, y así quedarán en blanco. 

Now, if I'm reviewing a test in the repasar_test() view, and there's a bookmarked question in there in my database, the 
question doesn't show up as bookmarked. So, edit my repasar_test() view so that, if the current question has been 
bookmarked in the PreguntasGuardadasPorElUsuario() model, the template should show somehow that that current question is 
bookmarked (for instance, by rendering the "pregunta guardada" button).

To fix the above issue, I will:
1. Checks if the current question is bookmarked by the user
2. Uses `exists()` for efficiency since we only need to know if the record exists
3. Passes the bookmarked state to the template through the context
4. Allows the template to render the correct button state based on `pregunta_esta_guardada`.

Currently you're only showing the letter of the correct answer without the full text content. Let's modify the 
repasar_test_finalizado() view to include the complete answer text. Modify the view to get the full text of the 
correct answer. You will Get the correct answer letter from the question model. Then, Use a conditional to find the 
corresponding full text. Add both to the context. Finally, update the template to display both the letter and full text.

"""


@login_required(login_url='iniciar_sesion')
def repasar_test_finalizado(request, session_id, question_number):
    # Esto coge la sesión del test del modelo de SesionDelTest
    session = get_object_or_404(
        SesionDelTest,
        id=session_id,
        usuario=request.user,
        cliente_entrego_este_test=True  # Changed from False to True
    )

    # Coge todas las preguntas del Test de la sesión seleccionada
    preguntas_del_test = PreguntaDelTest.objects.filter(
        nombre_del_test=session.nombre_del_test
    ).order_by('id')

    # Esto cuenta el número total de preguntas de este test
    numero_total_de_preguntas = preguntas_del_test.count()

    # Esto redirige al usuario a la 1era pregunta si intenta ir antes de la 1era pregunta o después de la última
    if question_number < 1 or question_number > numero_total_de_preguntas:
        return redirect('tests_clientes:repasar_test_finalizado', session_id=session.id, question_number=1)

    # # Luego, debo coger las respuestas que dió este cliente de RespuestasDelUsuario() para este test
    # respuestas_del_usuario = RespuestaDelUsuario.objects.filter(sesion=session)

    # Dado que Python empieza a contar desde el 0, esto, por ejemplo, toma la pregunta 1, y la convierte en "0"
    pregunta_en_formato_python = preguntas_del_test[question_number - 1]

    # Esto no cogerá las respuestas vacías, solo una sola respuesta correcta o incorrectas (la primera del filter())
    respuesta_del_usuario = RespuestaDelUsuario.objects.filter(
        sesion=session,
        pregunta=pregunta_en_formato_python
    ).first()

    # Quiero saber si la respuesta es correcta, incorrecta, o si estaba vacía.

    # Esto inicializa las variables de las respuestas correctas e incorrectas
    pregunta_seleccionada_es_correcta = False
    pregunta_seleccionada_es_incorrecta = False

    # Esto solo se ejecutará si la pregunta actual está respondida
    if respuesta_del_usuario and respuesta_del_usuario.respuesta_seleccionada:

        # Si el campo "es correcto" es "True" de este registro de RespuestaDelUsuario(), se marca como correcta
        if respuesta_del_usuario.es_correcto:
            pregunta_seleccionada_es_correcta = True

        else:
            # Si el campo "es correcto" es "False" de este registro de RespuestaDelUsuario(), se marca como incorrecta
            pregunta_seleccionada_es_incorrecta = True

        # if respuesta_del_usuario.respuesta_seleccionada == pregunta_en_formato_python.respuesta_correcta:
        #     pregunta_seleccionada_es_correcta = True

        # elif respuesta_del_usuario.respuesta_seleccionada != pregunta_en_formato_python.respuesta_correcta:
        #     pregunta_seleccionada_es_incorrecta = True

    # Solo se permiten GET requests en esta vista, NO POST requests
    if request.method == 'POST':
        # Esto imprime un mensaje de error si haces POST requests
        return HttpResponseForbidden("No se pueden modificar las respuestas de un examen completado")

    # Esto coge las preguntas que fueron respondidas por el usuario (para diferenciarlas de las vacías)
    preguntas_respondidas = list(RespuestaDelUsuario.objects.filter(
        sesion=session,
        respuesta_seleccionada__isnull=False
    ).values_list('pregunta__id', flat=True))

    # Esto crea un "array" que me dice cuales de las preguntas del test fueron respondidas.
    # Esto me ayuda para saber cuales preguntas fueron respondidas, y cuales quedaron sin respuesta.
    numero_de_las_preguntas_respondidas = []
    for index, q in enumerate(preguntas_del_test, 1):
        if q.id in preguntas_respondidas:
            numero_de_las_preguntas_respondidas.append(index)

    # Esta lista coge todas las preguntas respondidas correctamente por el usuario
    respuestas_correctas = list(RespuestaDelUsuario.objects.filter(
        sesion=session,
        es_correcto=True
    ).values_list('pregunta__id', flat=True))

    # Lista que coge todas las preguntas respondidas incorrectamente por el usuario
    respuestas_incorrectas = list(RespuestaDelUsuario.objects.filter(
        sesion=session,
        es_correcto=False
    ).values_list('pregunta__id', flat=True))

    # Estos 2 arrays almacenarán el número de cada pregunta (empezando desde el 1), y si son correctas o incorrectas
    preguntas_correctas = []
    preguntas_incorrectas = []

    # Este bucle me marca cada pregunta respondida como correcta o incorrecta. Esto lo usaré en el grid de preguntas
    for index, q in enumerate(preguntas_del_test, 1):

        # Si el número de la pregunta fue respondido correctamente, se añade all array de preguntas correctas
        if q.id in respuestas_correctas:
            preguntas_correctas.append(index)

        elif q.id in respuestas_incorrectas:

            # Si el número de la pregunta fue respondido incorrectamente, se añade all array de preguntas incorrectas
            preguntas_incorrectas.append(index)

    # # DEBUGGEO: esto me dice si la pregunta actual es correcta o incorrecta (diciendome cual variable es "True")
    # print(f"Correcta: {pregunta_seleccionada_es_correcta}")
    # print(f"Incorrecta: {pregunta_seleccionada_es_incorrecta}")

    # # Esto convierte la respuesta correcta en mayúsculas
    # respuesta_correcta = pregunta_en_formato_python.respuesta_correcta.upper()

    # Add this before the context dictionary.
    # Check if current question is bookmarked by the user.
    pregunta_esta_guardada = PreguntaGuardadaPorElUsuario.objects.filter(
        usuario=request.user,
        pregunta=pregunta_en_formato_python,
        test=session.nombre_del_test
    ).exists()

    # Get the correct answer letter (A, B, C, or D)
    respuesta_correcta = pregunta_en_formato_python.respuesta_correcta.upper()

    # Get the full text of the correct answer based on the letter.
    texto_respuesta_correcta = ""

    # Get the full text of the correct answer based on the letter
    match respuesta_correcta:
        case 'A':
            texto_respuesta_correcta = pregunta_en_formato_python.opcion_a
        case 'B':
            texto_respuesta_correcta = pregunta_en_formato_python.opcion_b
        case 'C':
            texto_respuesta_correcta = pregunta_en_formato_python.opcion_c
        case 'D':
            texto_respuesta_correcta = pregunta_en_formato_python.opcion_d if pregunta_en_formato_python.opcion_d else ""
        case _:
            texto_respuesta_correcta = ""

    # # OPTIMIZAR DESPUES.
    # if respuesta_correcta == 'A':
    #     texto_respuesta_correcta = pregunta_en_formato_python.opcion_a
    # elif respuesta_correcta == 'B':
    #     texto_respuesta_correcta = pregunta_en_formato_python.opcion_b
    # elif respuesta_correcta == 'C':
    #     texto_respuesta_correcta = pregunta_en_formato_python.opcion_c
    # elif respuesta_correcta == 'D' and pregunta_en_formato_python.opcion_d:
    #     texto_respuesta_correcta = pregunta_en_formato_python.opcion_d

    # 9. Add result-specific context
    context = {
        'session': session,
        'question': pregunta_en_formato_python,
        'question_number': question_number,
        'total_questions': numero_total_de_preguntas,
        'user_answer': respuesta_del_usuario,  # Respuesta del usuario para la pregunta seleccionada
        'questions': preguntas_del_test,
        'answered_questions': numero_de_las_preguntas_respondidas,
        # Esto almacena las respuestas correctas
        'pregunta_seleccionada_es_correcta': pregunta_seleccionada_es_correcta,
        # Esto almacena las respuestas incorrectas
        'pregunta_seleccionada_es_incorrecta': pregunta_seleccionada_es_incorrecta,
        'respuesta_correcta': pregunta_en_formato_python.respuesta_correcta.upper(),  # Respuesta en mayúsculas
        'texto_respuesta_correcta': texto_respuesta_correcta,  # The full text of the correct answer
        'viewing_results': True,  # Flag to modify template behavior
        'preguntas_correctas': preguntas_correctas,  # Esto me dira si la pregunta del grid fue respondida correctamente
        'preguntas_incorrectas': preguntas_incorrectas,  # Esto me dira si la pregunta del grid es incorrecta
        'has_option_d': bool(pregunta_en_formato_python.opcion_d),  # Will be True if option_d exists and is not empty
        'pregunta_esta_guardada': pregunta_esta_guardada,  # Esto revisa si el Usuario Guardo esta pregunta

    }

    # Reusaré el template de Tomar el Test, pero sin el temporizador y con las respuestas marcadas para repasar
    return render(request, 'tests_clientes/tomar_test.html', context)


""" Vista para tomar un Test Autocorregido.

Here's the `tomar_test_autocorregido()` view that handles immediate answer feedback.

Key differences from the original view:
1. Verifies `autocorrect=True` in session
2. Adds AJAX handling for immediate answer feedback
3. Returns correct/incorrect status and explanation
4. Sets `autocorrect=True` in context
5. Uses same template but with autocorrect mode

To implement this, you'll need to:
1. Add the `autocorrect` field to your `SesionDelTest` model
2. Update your URLs to include the new view
3. Add JavaScript to handle the answer selection and feedback
4. Update the template to show immediate feedback

Tendré que agregar notación en Jinja para reusar los estilos de repasar el test para el Test Autocorregido.

Tengo una idea: re-usaré el for loop que creaba los arrays que almacenaba las preguntas correctas e incorrectas de 
repasar el test, pero para el view del test autocorregido.

Para ver si la respuesta es correcta o incorrecta al devolverme a preguntas anteriores, puedo simple y llanamente 
re-usar el codigo y los estilos de repasar el test. Así, habría consistencia entre lo que muestro al repasar el test, 
y lo que muestro en el test de autocorrección. Creo que sería más fácil mostrar todo lo de “repasar test” cuando el 
usuario clique en una de las respuestas, y dejarlo permanentemente durante el test autocorregido. Y una vez más, así 
los estilos serían consistentes con lo que puse en “repasar test”, por lo que el diseño de la web app estaría mejor.

To add random questions to the newly created test:

1. Use the number of questions from the form
2. Set a random seed using the current timestamp
3. Filter questions based on the selected test type (tema/año/normativa)
4. Use `order_by('?')` for random selection
5. Limit to the requested number of questions
6. Assign the random questions to the new test using the many-to-many relationship

Agregue el snippet para que, si por accidente el usuario toma un test sin preguntas, no le salga el error que hace
que la pagina se redirija indefinidamente, ni salgan el monton de mensajes flash rojos diciendo "invalid question
number".

Currently you're only showing the letter of the correct answer without the full text content. Let's modify the 
repasar_test_finalizado() view to include the complete answer text. Modify the view to get the full text of the 
correct answer. You will Get the correct answer letter from the question model. Then, Use a conditional to find the 
corresponding full text. Add both to the context. Finally, update the template to display both the letter and full text.

Necesito enviar la letra con la respuesta correcta al template para que se me renderize la respuesta correcta junto
con la incorrecta cuando el usuario responda incorrectamente.
"""


@login_required(login_url='iniciar_sesion')
def tomar_test_autocorregido(request, session_id, question_number):
    # Get session with autocorrect verification
    session = get_object_or_404(
        SesionDelTest,
        id=session_id,
        usuario=request.user,
        cliente_entrego_este_test=False,
        test_autocorregido=True  # Ensure this is an autocorrect session
    )

    # Esto evitar un monton de bugs que ocurrían si intentas tomar un test sin preguntas
    if not PreguntaDelTest.objects.filter(nombre_del_test=session.nombre_del_test).exists():
        # Si no hay preguntas para este test, entonces le muestro un mensaje de error al cliente
        messages.error(request, "Este test no tiene preguntas asignadas.")

        # Redirijo al cliente a la vista de configurar un nuevo test a generar
        return redirect('tests_clientes:configurar_nuevo_test_a_generar')

    # Timer logic remains the same
    if session.tiempo_restante is not None:
        inicio_temporizador = session.tiempo_restante
    else:
        inicio_temporizador = session.limite_de_tiempo

    # Get questions
    questions = PreguntaDelTest.objects.filter(
        nombre_del_test=session.nombre_del_test
    ).order_by('id')

    total_questions = questions.count()

    # Validate question number
    if question_number < 1 or question_number > total_questions:
        messages.error(request, "Invalid question number.")
        return redirect('tests_clientes:tomar_test_autocorregido', session_id=session.id, question_number=1)

    # Get current question
    pregunta = questions[question_number - 1]

    # Handle AJAX POST request for answer submission
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        selected_answer = request.POST.get('selected_answer')

        if selected_answer in ['A', 'B', 'C', 'D']:
            # Save the answer
            user_answer, created = RespuestaDelUsuario.objects.get_or_create(
                sesion=session,
                pregunta=pregunta,
                defaults={'respuesta_seleccionada': selected_answer}
            )

            if not created:
                user_answer.respuesta_seleccionada = selected_answer
                user_answer.save()

            # Este es el booleano que me dice si la respuesta seleccionada es correcta o incorrecta.
            # Le insertaré el si la respuesta es correcta o no del campo "es_correcto" de RespuestaDelUsuario().
            # is_correct = (selected_answer == pregunta.respuesta_correcta)
            es_correcto_campo_de_json = user_answer.es_correcto

            # Esto crea el JSON que se le enviará al front-end del Template de Tomar el Test
            return JsonResponse({
                'status': 'success',
                'es_correcto': es_correcto_campo_de_json,  # Booleano que me dice si la respuesta es correcta o no
                'correct_answer': pregunta.respuesta_correcta,
                'justificacion': pregunta.justificacion
            })

    # Handle regular POST requests for navigation
    elif request.method == 'POST':
        action = request.POST.get('action')

        match action:
            case 'next' if question_number < total_questions:
                return redirect('tests_clientes:tomar_test_autocorregido',
                                session_id=session.id,
                                question_number=question_number + 1)

            case 'previous' if question_number > 1:
                return redirect('tests_clientes:tomar_test_autocorregido',
                                session_id=session.id,
                                question_number=question_number - 1)

            case 'finish':
                session.cliente_entrego_este_test = True
                session.hora_del_fin_del_test = timezone.now()
                session.save()
                return redirect('tests_clientes:resultados_del_test', session_id=session.id)

    # Get user's current answer and answered questions
    user_answer = RespuestaDelUsuario.objects.filter(
        sesion=session,
        pregunta=pregunta
    ).first()

    answered_questions = list(RespuestaDelUsuario.objects.filter(
        sesion=session,
        respuesta_seleccionada__isnull=False
    ).values_list('pregunta__id', flat=True))

    answered_question_numbers = [
        i for i, q in enumerate(questions, 1)
        if q.id in answered_questions
    ]

    # Esto coge las preguntas que fueron respondidas por el usuario (para diferenciarlas de las vacías)
    preguntas_respondidas = list(RespuestaDelUsuario.objects.filter(
        sesion=session,
        respuesta_seleccionada__isnull=False
    ).values_list('pregunta__id', flat=True))

    # Esto crea un "array" que me dice cuales de las preguntas del test fueron respondidas.
    # Esto me ayuda para saber cuales preguntas fueron respondidas, y cuales quedaron sin respuesta.
    numero_de_las_preguntas_respondidas = []
    for index, q in enumerate(questions, 1):
        if q.id in preguntas_respondidas:
            numero_de_las_preguntas_respondidas.append(index)

    # Esta lista coge todas las preguntas respondidas correctamente por el usuario
    respuestas_correctas = list(RespuestaDelUsuario.objects.filter(
        sesion=session,
        es_correcto=True
    ).values_list('pregunta__id', flat=True))

    # Lista que coge todas las preguntas respondidas incorrectamente por el usuario
    respuestas_incorrectas = list(RespuestaDelUsuario.objects.filter(
        sesion=session,
        es_correcto=False
    ).values_list('pregunta__id', flat=True))

    # Estos 2 arrays almacenarán el número de cada pregunta (empezando desde el 1), y si son correctas o incorrectas
    preguntas_correctas = []
    preguntas_incorrectas = []

    # Este bucle me marca cada pregunta respondida como correcta o incorrecta. Esto lo usaré en el grid de preguntas
    for index, q in enumerate(questions, 1):

        # Si el número de la pregunta fue respondido correctamente, se añade all array de preguntas correctas
        if q.id in respuestas_correctas:
            preguntas_correctas.append(index)

        elif q.id in respuestas_incorrectas:

            # Si el número de la pregunta fue respondido incorrectamente, se añade all array de preguntas incorrectas
            preguntas_incorrectas.append(index)

    # Snippet para mostrar si la respuesta es correcta o incorrecta como que si estuvieras repasando el test
    # Esto inicializa las variables que dice si la respuesta de la pregunta seleccionada es correcta o incorrecta
    pregunta_seleccionada_es_correcta = False
    pregunta_seleccionada_es_incorrecta = False

    # Esto solo se ejecutará si la pregunta actual está respondida
    if user_answer and user_answer.respuesta_seleccionada:

        # Si el campo "es correcto" es "True" de este registro de RespuestaDelUsuario(), se marca como correcta
        if user_answer.es_correcto:
            pregunta_seleccionada_es_correcta = True

        else:
            # Si el campo "es correcto" es "False" de este registro de RespuestaDelUsuario(), se marca como incorrecta
            pregunta_seleccionada_es_incorrecta = True

            # Fin del snippet para mostrar si la respuesta es correcta como que si estuvieras repasando el test

    # Esto arregla el formato del temporizador a minutos y segundos en lugar de solo segundos
    def format_time(seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:02d}"

    # Add this before the context dictionary.
    # Check if current question is bookmarked by the user.
    pregunta_esta_guardada = PreguntaGuardadaPorElUsuario.objects.filter(
        usuario=request.user,
        pregunta=pregunta,
        test=session.nombre_del_test
    ).exists()

    # Get the correct answer letter (A, B, C, or D)
    respuesta_correcta = pregunta.respuesta_correcta.upper()

    # Get the full text of the correct answer based on the letter.
    texto_respuesta_correcta = ""

    # Get the full text of the correct answer based on the letter
    match respuesta_correcta:
        case 'A':
            texto_respuesta_correcta = pregunta.opcion_a
        case 'B':
            texto_respuesta_correcta = pregunta.opcion_b
        case 'C':
            texto_respuesta_correcta = pregunta.opcion_c
        case 'D':
            texto_respuesta_correcta = pregunta.opcion_d if pregunta.opcion_d else ""
        case _:
            texto_respuesta_correcta = ""

    # # OPTIMIZAR DESPUES.
    # if respuesta_correcta == 'A':
    #     texto_respuesta_correcta = pregunta.opcion_a
    # elif respuesta_correcta == 'B':
    #     texto_respuesta_correcta = pregunta.opcion_b
    # elif respuesta_correcta == 'C':
    #     texto_respuesta_correcta = pregunta.opcion_c
    # elif respuesta_correcta == 'D' and pregunta.opcion_d:
    #     texto_respuesta_correcta = pregunta.opcion_d

    context = {
        'session': session,
        'question': pregunta,
        'question_number': question_number,
        'total_questions': total_questions,
        'user_answer': user_answer,
        'inicio_temporizador': format_time(inicio_temporizador),
        'questions': questions,
        'answered_questions': answered_question_numbers,
        'autocorreccion': True,  # Template flag for autocorrect mode
        'preguntas_correctas': preguntas_correctas,  # Esto es para que la respuesta correcta se ponga verde en el grid
        'preguntas_incorrectas': preguntas_incorrectas,  # Para que la respuesta incorrecta se ponga roja en el grid
        'pregunta_seleccionada_es_correcta': pregunta_seleccionada_es_correcta,  # Esto renderiza respuesta correcta
        'pregunta_seleccionada_es_incorrecta': pregunta_seleccionada_es_incorrecta,  # Si respuesta es errónea
        'texto_respuesta_correcta': texto_respuesta_correcta,  # The full text of the correct answer
        'has_option_d': bool(pregunta.opcion_d),  # Will be True if option_d exists and is not empty
        'pregunta_esta_guardada': pregunta_esta_guardada,  # Esto revisa si el Usuario Guardo esta pregunta
        # Respuesta correcta que se mostrará si respondo incorrectamente
        'respuesta_correcta': pregunta.respuesta_correcta.upper(),

    }

    return render(request, 'tests_clientes/tomar_test.html', context)


""" API para Obtener el Número de Preguntas de un Tema, una Normativa, o un Año de un Test.

Haré lo de como mostrarle al cliente el número total de preguntas disponible para ese tema, o para esa normativa, o 
para ese año. TENDRE que usar un fetch() call con JS y el back-end de django. Cuando el usuario seleccione “tema”, 
y se seleccione automáticamente el tema 1, automáticamente me diga cuantas preguntas tiene ese tema seleccionado 
(o esa normativa, o ese año). Puedo poner un onChange() event listener en el dropdown menu en donde yo seleccione o el 
año, o la normativa, o el tema específico.

Haré que una función de JavaScript en el template de "configurar_nuevo_test_a_generar.html" haga un fetch() a esta API
cuando el usuario seleccione un tema, normativa, o año. Luego, la API le devolverá el número de preguntas que hay
para ese tema, normativa, o año. 

Here's the refactored code using Python's `match/case` structure.

The changes:
1. Replaced if/elif/else with match/case syntax
2. Used `case _` as the default case
3. Maintained the same logic within each case
4. Kept the query filtering logic intact

Lo modifiqué para que pueda coger varios temas y varias normativas en lugar de solo 1.

Where does 'temas' come from?
This is a naming mismatch between your backend and frontend:

In your form: The field is named tema (singular)
In your API call: You're looking for temas (plural)
In your JavaScript: When building the fetch request, it's using:

    selectedTopics.forEach(topic => {
      params.append('temas', topic);  // <-- Using 'temas' (plural)
    });

"""


def get_question_count(request):
    tipo_test = request.GET.get('tipo_test')

    match tipo_test:

        # Si el tipo de test es "tema", entonces se filtra por tema
        case 'tema':

            # Cogeré 1 o más temas
            temas = request.GET.getlist('temas')
            if temas:
                from django.db.models import Q
                query = Q()
                for tema in temas:
                    query |= Q(tema=tema)
                count = PreguntaDelTest.objects.filter(query).count()
            else:
                count = 0

            # Probablemente REACTIVE esto después si no funciona lo que intento hacer.
            # tema = request.GET.get('tema')
            # count = PreguntaDelTest.objects.filter(tema=tema).count()

        case 'año':
            year = request.GET.get('year')
            count = PreguntaDelTest.objects.filter(year=year).count()

        case 'normativa':

            # Para coger 1 o más normativas, usaré un snippet similar a como cojo los temas
            normativas = request.GET.getlist('normativas')
            if normativas:
                from django.db.models import Q
                query = Q()

                for normativa in normativas:
                    query |= Q(normativa=normativa)
                count = PreguntaDelTest.objects.filter(query).count()
            else:
                count = 0

            # normativa = request.GET.get('normativa')
            # count = PreguntaDelTest.objects.filter(normativa=normativa).count()

        case _:  # handles 'sin especificar' and any other case
            count = PreguntaDelTest.objects.all().count()

    # # USAR UN SWITCH / CASE AQUI DESPUES
    # if tipo_test == 'tema':
    #     tema = request.GET.get('tema')
    #     count = PreguntaDelTest.objects.filter(tema=tema).count()
    # elif tipo_test == 'año':
    #     year = request.GET.get('year')
    #     count = PreguntaDelTest.objects.filter(year=year).count()
    # elif tipo_test == 'normativa':
    #     normativa = request.GET.get('normativa')
    #     count = PreguntaDelTest.objects.filter(normativa=normativa).count()
    # else: # handles 'aleatorio'
    #     count = PreguntaDelTest.objects.all().count()

    return JsonResponse({'count': count})


""" Vista para que el Usuario pueda Ver las Preguntas que haya Guardado.

Necesito buscar también el test al que pertenece esa pregunta que guardó el usuario. Pero eso ya se almacena en el
modelo de PreguntaGuardadaPorElUsuario().

Solo el usuario que haya guardado las preguntas podra veer sus propias preguntas guardadas.
"""


@login_required(login_url='iniciar_sesion')
def ver_preguntas_guardadas(request):
    # Esto coge todas las preguntas guardadas por el usuario autenticado
    preguntas_guardadas = PreguntaGuardadaPorElUsuario.objects.filter(usuario=request.user)

    # Esto renderiza el template con las preguntas guardadas por el usuario autenticado
    return render(request, 'tests_clientes/preguntas_guardadas/ver_preguntas_guardadas.html', {
        'preguntas_guardadas': preguntas_guardadas
    })


""" Vista para que el usuario pueda ver de manera detallada ls Pregunta Guardada seleccionada.

Si el usuario esta viendo su lista de preguntas guardadas, y clica en una de las preguntas guardadas, entonces se le
redirigirá a esta vista. Aquí podrá ver la pregunta guardada, y la respuesta correcta de esa pregunta.

Solo mostrare el test del modelo de Test() de ese test, mostraré esa pregunta en específico, junto con la respuesta 
correcta, la justificacion, etc. Es decir, solo crearé un view para mostrar todos los datos de esa pregunta del modelo 
de PreguntasDelTest(). Lo único adicional que pondré es el nombre del test al que le pertenece esa pregunta.
"""


@login_required(login_url='iniciar_sesion')
def ver_detalles_de_pregunta_guardada_seleccionada(request, pregunta_guardada_id):
    # Esto coge la pregunta guardada por el usuario autenticado
    instancia_de_pregunta_guardada = get_object_or_404(
        PreguntaGuardadaPorElUsuario, id=pregunta_guardada_id, usuario=request.user
    )

    # Esto coge la pregunta del test del modelo de PreguntaDelTest() que le pertenece a esa pregunta guardada
    instancia_de_pregunta_del_test = get_object_or_404(PreguntaDelTest, id=instancia_de_pregunta_guardada.pregunta.id)

    # Esto renderiza el template con la pregunta guardada por el usuario autenticado
    return render(request, 'tests_clientes/preguntas_guardadas/ver_detalles_de_pregunta_guardada.html',
                  {
                      'instancia_de_pregunta_guardada': instancia_de_pregunta_guardada,
                      'instancia_de_pregunta_del_test': instancia_de_pregunta_del_test
                  })


""" Vista con la API para que el Usuario pueda Guardar una Pregunta en el modelo de PreguntaGuardadaPorElUsuario().

El usuario llamará a esta API desde el front-end cuando clique en el botón de "Guardar Pregunta" o el icono del 
marcador en la página para repasar el test.

This implementation:
1. Adds a "Save Question" button to the results view
2. Creates an AJAX endpoint to handle saving questions
3. Prevents duplicate saves for the same question
4. Provides visual feedback when a question is saved
5. Handles errors appropriately
6. Uses CSRF protection for the POST request

The button will be disabled and show "Pregunta Guardada" after successfully saving the question. If there's an error 
(like trying to save a duplicate), it will show an alert with the error message.

"""


@require_POST
@login_required
def guardar_pregunta(request):
    try:
        data = json.loads(request.body)
        pregunta_id = data.get('pregunta_id')
        test_id = data.get('test_id')
        session_id = data.get('session_id')

        # Esto me asegura en el back-end que no se me vuelvan a guardar preguntas que ya estaban guardadas.
        # Check if question is already saved by this user
        if PreguntaGuardadaPorElUsuario.objects.filter(
                usuario=request.user,
                pregunta_id=pregunta_id,
                test_id=test_id,
                sesion_id=session_id  # También meteré la ID de la sesión del test
        ).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Ya has guardado esta pregunta'
            })

        # Get the question and test instances
        pregunta = get_object_or_404(PreguntaDelTest, id=pregunta_id)
        test = get_object_or_404(Test, id=test_id)

        # También voy a agarrar la sesión del test
        sesion = get_object_or_404(SesionDelTest, id=session_id)

        # Create new saved question record
        PreguntaGuardadaPorElUsuario.objects.create(
            usuario=request.user,
            pregunta=pregunta,
            test=test,
            sesion=sesion  # Guardar la sesión del test
        )

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


""" Vista con la API para que el Usuario pueda Eliminar una Pregunta del modelo de PreguntaGuardadaPorElUsuario(),
para que así pueda eliminar una pregunta guardada que ya no le interese.
"""


@require_POST
@login_required
def eliminar_pregunta_guardada(request):
    try:
        data = json.loads(request.body)
        pregunta_id = data.get('pregunta_id')
        test_id = data.get('test_id')

        # Find and delete the saved question
        PreguntaGuardadaPorElUsuario.objects.filter(
            usuario=request.user,
            pregunta_id=pregunta_id,
            test_id=test_id
        ).delete()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
