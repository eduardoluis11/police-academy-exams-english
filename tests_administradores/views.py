from django.shortcuts import render, get_object_or_404, redirect

from .models import Test, PreguntaDelTest

# tests_administradores/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# Esto importa mis formularios de la app de tests para administradores
from .forms import (SubirExcelConTestsFormulario, CrearTestSinExcelFormulario, NombreDelTestFormulario,
                    CrearPreguntaDelTestFormSet, BuscadorDePreguntasFormulario
                    )

from .utils import import_exams_from_excel
import os

# Esto lo necesito para poder hacer búsquedas en una barra de busqueda
from django.db.models import Q

# Esto lo necesito para poder hacer paginación
from django.core.paginator import Paginator

""" Vistas para la app de tests para administradores.

Por recomendación de Grok y por ciberseguridad, dejare los 2 decorators para los views de los administradores: el 
login required para revisar si el usuario esta logueado, y el lambda para verificar que el usuario logueado sea un 
administrador. Debería ser “user.is_superuser” creo. Pero is staff creo que tambien funciona (un empleado que no sea 
superusuario). 
"""

""" View with Upload and Processing Logic

Create a view that handles the upload and triggers the data import.

Why:
@login_required and @user_passes_test: Restricts access to authenticated admins.

FileSystemStorage: Saves the file securely in media/exams/.

messages: Provides user-friendly feedback.

File deletion: Removes the file after processing to avoid leaving sensitive data on the server.

Best Practices: CSRF protection (automatic with Django forms), error handling, and cleanup.

"""

# Create your views here.


""" Vista para Subir y Procesar archivos de Excel con Tests / Exámenes para escanearlos y así extraerles los datos
de cada test y meterlos a la base de datos.

Para meter los datos extraídos del Excel a los modelos de Test() y PreguntaDelTest() en la base de datos, necesito
un script que haga eso. Este script se encuentra en utils.py, el cual está en la misma carpeta que este view.

# View with Upload and Processing Logic

This is a view that handles the upload and triggers the data import.



Certainly! The line `@user_passes_test(lambda u: u.is_staff, login_url='login')` is a decorator in Django that ensures 
only users who pass a specific test can access the associated view. Let me break it down for you:

1. **`@user_passes_test`**:
   - This is a built-in Django decorator that takes a test function as its first argument. The test function should 
   accept a user object and return `True` if the user passes the test, or `False` otherwise.

2. **`lambda u: u.is_staff`**:
   - The test function here is written as a lambda (anonymous function). It checks the value of the `is_staff` 
   attribute on the user object (`u`).
   - `u.is_staff` is a boolean attribute of the Django `User` model. It is typically used to indicate whether a user 
   has staff-level privileges (e.g., an administrator or similar role).
   - If the user is a staff member (`is_staff == True`), they pass the test. Otherwise, they don't.

3. **`login_url='login'`**:
   - If a user fails the test (e.g., they are not a staff member), they are redirected to the `login` view (identified 
   by its URL name `'login'`).
   - This ensures that unauthorized users are not given access to the view.

### Practical Example:
In this case, the decorator ensures that:
- The user must be logged in (`@login_required`) *and*
- The user must have the `is_staff` attribute set to `True`.

If either condition is not met:
- If the user is not logged in, they are first redirected to the login page due to `@login_required`.
- If the user is logged in but not a staff member, they are also redirected to the login page (`login_url='login'`).

### Why It's Used:
This line effectively restricts the view `upload_and_import_exams` so that only admin or staff users (those with the 
`is_staff` flag) can access it. It is a common security measure to ensure certain views or actions are limited to 
privileged users.

Let me know if you'd like further clarification or additional examples!

## Why:
@login_required and @user_passes_test: Restricts access to authenticated admins.

FileSystemStorage: Saves the file securely in media/exams/.

messages: Provides user-friendly feedback.

File deletion: Removes the file after processing to avoid leaving sensitive data on the server.

Best Practices: CSRF protection (automatic with Django forms), error handling, and cleanup.

Por los momentos, se suben los archivos a una carpeta llamada "exams", la cual está dentro de la carpeta "media",
y luego se borran los archivos excel después de extraerles los datos. Por los momentos, se borra el archivo subido
despues de extraerle los datos por motivos de ciberseguridad.

Si el usuario autenticado no es un administrador, y se intenta meter a esta vista, será redirigido al formulario para
iniciar sesión. Esto es para evitar que los clientes intenten hackear la página para subir archivos excel, y así
no puedan robarse los tests.

You can redirect users to the Django admin login page. Here's how to modify the decorator:

This will redirect unauthenticated users to the Django admin login page at /admin/login/.  Note that:  
The leading slash is important
We need to specify the full path to the login page
This assumes you have the Django admin site enabled in your urls.py and settings_NO_USAR.py
This is often used when you want to restrict access to admin-only views since the admin login page has additional 
security features built in.
"""


@login_required(login_url='/admin/login/')
# Esto revisa si el usuario autenticado es un administrador
@user_passes_test(lambda usuario: usuario.is_staff, login_url='/admin/login/')
def upload_and_import_exams(request):
    if request.method == 'POST':
        form = SubirExcelConTestsFormulario(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']

            # Save the file to media/exams/.
            # Lo modifiqué para que se guarden los archivos en media/archivos_con_modelos_de_tests
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'archivos_con_modelos_de_tests'))
            filename = fs.save(excel_file.name, excel_file)
            file_path = fs.path(filename)

            # Esto llama al script de utils.py para meter los datos del Excel a Test() y a PreguntaDelTest()
            success_count, error_messages = import_exams_from_excel(file_path)

            # Esto crea los mensajes flash de error y de confirmación usando "messages"
            if success_count > 0:
                messages.success(request, f"Se importaron exitosamente {success_count} preguntas.")
                # messages.success(request, f"Successfully imported {success_count} exam questions.")
            if error_messages:  # Si hay errores
                for error in error_messages:
                    messages.error(request, error)
            else:   # Si no hay errores
                messages.info(request, "No se encontraron errores durante la importación.")
                # messages.info(request, "No errors encountered during import.")

            # Optionally, delete the file after processing for security
            if os.path.exists(file_path):
                os.remove(file_path)

    else:
        form = SubirExcelConTestsFormulario()

    return render(request, 'tests_administradores/subir_archivos_con_tests.html', {
        'form': form
    }
                  )


""" Vista para Crear un Nuevo Test Sin Usar un Archivo de Excel.

Aqui, mostraré un formulario para que el administrador pueda crear un nuevo test y sus respectivas preguntas 
manualmente.

I want to create a formset for my CrearTestSinExcelFormulario django form. That way, the user will be able to assign 
multiple questions to the same isntance of the Test model. Give me an algorithm on how to create the formset in my 
forms.py, then tell me how to add it in my django view for creating new exams. Then, tell me how to render the formset 
into my template, and put a javascript button to be able to add new questions with a new formset. 

I did this to implement my formsets for the exam's questions:
    
1) Uses Django's modelformset_factory for proper form handling
2) Includes form validation for both the test name and questions
3) Implements dynamic form addition with JavaScript
4) Maintains proper form indexing
5) Includes error handling and success messages
6) Uses Bootstrap classes for styling
7) Follows Django's best practices for formsets
8) Provides a clean user interface for adding/removing questions

Agregué un add() al momento de agregar la instancia del Test() en el campo "nombre del test" en la instancia
de la pregunta del test de PreguntaDelTest. Esto es porque ahora el campo "nombre del test" es un ManyToManyField(),
por lo que es un poco más complicado agregarle el nombre del test a la pregunta del test.

Cuando se cree manualmente, tengo que marcar ese test como “por año” en el campo “tipo”.

También meteré el año del Test para que el administrador pueda escribirlo. Si el administrador quiere meter exámenes 
viejos (ej: del 2022) de manera manual, creo que el administrador debe poder hacerlo.

BOOKMARK:
Tengo que hacer que el nuevo test creado se marque que no fue generado proceduralmente. Así, este test será universal,
y cualquier cliente podrá tomar este test. Esto tengo que hacerlo también en la vista para importar un Test desde un
archivo Excel.
"""


@login_required(login_url='/admin/login/')
@user_passes_test(lambda usuario: usuario.is_staff, login_url='/admin/login/')
def crear_nuevo_test_sin_subir_un_archivo(request):
    # Esto valida el formulario y lo guarda en la base de datos
    if request.method == 'POST':

        # Creo una instancia de los 2 formularios
        campo_nombre_del_test = NombreDelTestFormulario(request.POST)
        # resto_del_formulario = CrearTestSinExcelFormulario(request.POST)
        formset = CrearPreguntaDelTestFormSet(request.POST, prefix='preguntas')

        # Si los 2 formularios son válidos
        if campo_nombre_del_test.is_valid() and formset.is_valid():
            # if resto_del_formulario.is_valid() and campo_nombre_del_test.is_valid():

            # Esto crea una nueva instancia del modelo de Test con su nombre, año, y de tipo "por año"
            nuevo_nombre_del_test = Test(
                nombre_del_test=campo_nombre_del_test.cleaned_data['nombre_del_test'],
                tipo="año",  # Todo test creado manualmente es un test por año, por lo que debo asignarle "año"
                year=campo_nombre_del_test.cleaned_data['year'],    # Año del test (e.g., "2023")
                fue_generado_proceduralmente=False,  # Esto marca el test como no generado proceduralmente (universal)
            )

            # Esto guarda el nuevo test en la base de datos en el modelo de Test
            nuevo_nombre_del_test.save()

            # Esto crea una nueva instancia del modelo de PreguntaDelTest con el resto de los campos del formulario
            # Save each question

            # Esto coge todos los campos del formset de las preguntas del test del formulario de mi template
            instances = formset.save(commit=False)

            # Esto crea una nueva instancia del modelo de PreguntaDelTest por cada formset de mi formulario.
            # No hay necesidad de especificar cad campo del modelo de PreguntaDelTest porque ya se especificaron en el
            # formset de CrearPreguntaDelTestFormSet.
            for instance in instances:

                # instance.nombre_del_test = nuevo_nombre_del_test

                # Esto guarda la instancia de la pregunta de la iteración actual en el modelo de PreguntaDelTest
                instance.save()

                # Esto actualiza la pregunta actual con el nombre del test que se acaba de crear usando add()
                instance.nombre_del_test.add(nuevo_nombre_del_test)

            # Handle deleted forms
            for obj in formset.deleted_objects:
                obj.delete()

            # pregunta_del_test = PreguntaDelTest(
            #     nombre_del_test=nuevo_nombre_del_test,
            #     tema=resto_del_formulario.cleaned_data['tema'],
            #     normativa=resto_del_formulario.cleaned_data['normativa'],
            #     pregunta=resto_del_formulario.cleaned_data['pregunta'],
            #     opcion_a=resto_del_formulario.cleaned_data['opcion_a'],
            #     opcion_b=resto_del_formulario.cleaned_data['opcion_b'],
            #     opcion_c=resto_del_formulario.cleaned_data['opcion_c'],
            #     opcion_d=resto_del_formulario.cleaned_data['opcion_d'],
            #     respuesta_correcta=resto_del_formulario.cleaned_data['respuesta_correcta'],
            #     justificacion=resto_del_formulario.cleaned_data['justificacion']
            #     )

            # # Esto guarda las nuevas preguntas del nuevo test en la base de datos en PreguntaDelTest()
            # pregunta_del_test.save()

            # Muestra un mensaje de confirmación
            messages.success(request, "El test fue creado correctamente.")

            # Esto redirige al usuario a la lista de tests
            return redirect('tests_clientes:lista_de_tests')

        # Si los 2 formularios no son válidos
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")

            # # Errores del resto del formulario si el formulario no es válido
            # for field, errors in resto_del_formulario.errors.items():
            #     for error in errors:
            #         # Esto mostrara cada uno de los errores del formulario como mensaje flash de error
            #         messages.error(request, f"Error en {resto_del_formulario[field].label}: {error}")

    # Esto crea los formularios para la página
    campo_nombre_del_test = NombreDelTestFormulario()
    formset = CrearPreguntaDelTestFormSet(prefix='preguntas', queryset=PreguntaDelTest.objects.none())

    # resto_del_formulario = CrearTestSinExcelFormulario()

    # Esto renderiza la página con el formulario para Crear un nuevo test
    return render(request, 'tests_administradores/crear_nuevo_test_sin_archivo.html', {
        'campo_nombre_del_test': campo_nombre_del_test,
        'formset': formset,
        # 'resto_del_formulario': resto_del_formulario
    })


""" Vista para Editar un Test.

Primero, tengo que coger la ID del test que quiero editar de la URL. La ID la voy a tener cuando clico en el enlace
"Editar" al lado del Test que quiero editar.

Luego, usando esa ID, debo buscar el test deseado del modelo de Test.

Después, debo coger todas las preguntas del test seleccionado, por lo que tendré que acceder al modelo de 
PreguntaDelTest.

Luego, si un test tiene varias preguntas (y todos los van a tener), tendre renderizar con formsets cada pregunta.

Si le quiero quitar preguntas a un test, tendré que agregar la funcionalidad de eliminar preguntas en el formset.
Esto lo debería hacer en la vista de para Crear Tests sin usar Archivos Excel.
"""


@login_required(login_url='/admin/login/')
@user_passes_test(lambda usuario: usuario.is_staff, login_url='/admin/login/')
def editar_test(request, test_id):
    # Esto coge el test seleccionado que el usuario quiere editar con un get()
    test = get_object_or_404(Test, pk=test_id)

    # Esto valida el formulario y lo guarda en la base de datos
    if request.method == 'POST':

        # Creo una instancia de los 2 formularios
        campo_nombre_del_test = NombreDelTestFormulario(request.POST, instance=test)
        formset = CrearPreguntaDelTestFormSet(request.POST,
                                              prefix='preguntas',
                                              queryset=PreguntaDelTest.objects.filter(nombre_del_test=test))

        # Si los 2 formularios son válidos
        if campo_nombre_del_test.is_valid() and formset.is_valid():

            # Esto guarda el nuevo test en la base de datos en el modelo de Test
            nuevo_nombre_del_test = campo_nombre_del_test.save()

            # Esto coge todos los campos del formset de las preguntas del test del formulario de mi template
            instances = formset.save(commit=False)

            # Esto crea una nueva instancia del modelo de PreguntaDelTest por cada formset de mi formulario.
            # No hay necesidad de especificar cad campo del modelo de PreguntaDelTest porque ya se especificaron en el
            # formset de CrearPreguntaDelTestFormSet.
            for instance in instances:
                instance.nombre_del_test = nuevo_nombre_del_test
                instance.save()

            # Handle deleted forms
            for obj in formset.deleted_objects:
                obj.delete()

            # Muestra un mensaje de confirmación
            messages.success(request, "El test fue editado correctamente.")

            # Esto redirige al usuario a la lista de tests
            return redirect('tests_clientes:lista_de_tests')

        # Si los 2 formularios no son válidos
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")

    # Esto crea los formularios para la página
    campo_nombre_del_test = NombreDelTestFormulario(instance=test)
    formset = CrearPreguntaDelTestFormSet(prefix='preguntas',
                                          queryset=PreguntaDelTest.objects.filter(nombre_del_test=test))

    # Esto renderiza la página con el formulario para Crear un nuevo test
    return render(request, 'tests_administradores/editar_test.html', {
        'campo_nombre_del_test': campo_nombre_del_test,
        'formset': formset,
        'test': test
    })


""" Vista para Confirmar que quieres Eliminar un Test.

Si el usuario clica en el enlace para eliminar un test, se le mostrará una página de confirmación para asegurarse
de que realmente quiere eliminar el test.

Si realmente quiere eliminar el test, entonces se le redirigirá a la vista de Eliminar Test para terminar de 
eliminar el test.
"""


@login_required(login_url='/admin/login/')
@user_passes_test(lambda usuario: usuario.is_staff, login_url='/admin/login/')
def confirmar_eliminar_test(request, test_id):
    # Esto coge el test seleccionado que el usuario quiere eliminar con un get()
    test = get_object_or_404(Test, pk=test_id)

    # Esto renderiza el template con la página de confirmación de eliminar el test
    return render(request, 'tests_administradores/confirmar_eliminar_test.html', {'test': test})


""" Vista para Eliminar un Test.

Me aseguraré de que el usuario autenticado sea un administrador antes de permitirle eliminar un test.

El usuario tiene que venir desde la vista de Confirmar Eliminar Test para poder eliminar el test.
"""


@login_required(login_url='/admin/login/')
@user_passes_test(lambda usuario: usuario.is_staff, login_url='/admin/login/')
def eliminar_test(request, test_id):
    # Esto coge el test que el usuario quiere eliminar con un get()
    test = get_object_or_404(Test, pk=test_id)

    # Esto elimina el test seleccionado del modelo de Test
    test.delete()

    # Esto le muestra al usuario un mensaje de confirmacion
    messages.success(request, f"El test '{test.nombre_del_test}' fue eliminado correctamente.")

    # Esto redirige al usuario a la lista de tests
    return redirect('tests_clientes:lista_de_tests')


""" Vista de Buscador de Preguntas para buscar una pregunta en específico de todos los tests.

## Algorithm Overview
View: Create a view that handles the search request and queries the database for matching questions.

Form: Use a simple form to capture the search query from the front-end.

Query: Search the PreguntasDelTest model by matching the query against the question text and the related test name.

Template: Display a search bar and render the results in a list or table.

Security: Restrict access to admins only.

Best Practices: Add pagination for large result sets, provide feedback, and handle edge cases (e.g., no results).

## Create the Search View

We’ll create a view that:

Accepts the search query.

Queries PreguntasDelTest for matching questions.

Filters results to ensure only admins can access the page.

How It Works:
@login_required and @user_passes_test: Ensures only authenticated admins can access the view.

Q objects: Allows searching across multiple fields (question and test__name) with a single query.

icontains: Case-insensitive search for partial matches.

Paginator: Limits the number of results per page, improving performance for large datasets.

Best Practice: Pagination prevents overwhelming the user with too many results, and Q objects make the search flexible.

Quiero buscar el texto escrito en la barra de búsqueda en para cualquier registro que esté tanto en el modelo
de PreguntaDelTest como en el modelo de Test. Es decir, quiero saber si el texto escrito es el nombre 
de un test, o es una pregunta, u es una justificacion, o es una de las opciones, etc.

I'll modify the query to search across all relevant fields in the PreguntaDelTest model. Here's how to chain multiple 
Q objects with the OR operator (|).

This will search for the query string in all fields of the PreguntaDelTest model. The | operator means OR, so it will 
return any question that matches the search term in any of these fields.  Note that for the foreign key field 
nombre_del_test, we use double underscores to search in its nombre_del_test field.
"""


@login_required(login_url='/admin/login/')
@user_passes_test(lambda usuario: usuario.is_staff, login_url='/admin/login/')
def buscador_de_preguntas(request):
    # Esto crea el formulario para buscar preguntas. Si coge los datos, lo hace usando un GET request.
    form = BuscadorDePreguntasFormulario(request.GET or None)

    # Esto coge todas las preguntas registradas en el modelo de PreguntaDelTest
    preguntas = PreguntaDelTest.objects.all()

    if form.is_valid():  # Si el formulario es válido al enviar el formulario

        # Esto coge el texto escrito en el formulario por el usuario
        consulta = form.cleaned_data.get('consulta')

        # Si el usuario escribió algo en el formulario al enviarlo
        if consulta:

            # Esto busca si existe alguna pregunta que contenga le texto escrito en la barra de búsqueda.
            # Buscare si el campo "pregunta" del modelo PreguntaDelTest contiene el texto escrito del buscador.
            preguntas = preguntas.filter(
                Q(nombre_del_test__nombre_del_test__icontains=consulta) |  # Busca en el nombre del test de Test()
                Q(tema__icontains=consulta) |   # Esto busca si el tema contiene el texto escrito de PreguntaDelTest
                Q(normativa__icontains=consulta) |
                Q(pregunta__icontains=consulta) |   # Esto busca si la pregunta contiene el texto escrito
                Q(opcion_a__icontains=consulta) |
                Q(opcion_b__icontains=consulta) |
                Q(opcion_c__icontains=consulta) |
                Q(opcion_d__icontains=consulta) |
                Q(respuesta_correcta__icontains=consulta) |
                Q(justificacion__icontains=consulta)    # Esto busca si la justificación contiene el texto escrito
            )

            # preguntas = preguntas.filter(
            #     Q(pregunta__icontains=consulta | Q(justificacion__icontains=consulta))
            # )

            # questions = questions.filter(
            #     Q(question__icontains=consulta) | Q(test__name__icontains=consulta)
            # )

    # else:  # Si el formulario es inválido
    #     messages.error(request, "Por favor, corrija los errores en el formulario.")

    # Add pagination (e.g., 10 questions per page)
    paginator = Paginator(preguntas, 10)  # Show 10 questions per page
    page_number = request.GET.get('page')

    # This will return the current page object
    page_object = paginator.get_page(page_number)
    # Fin del snippet con la paginación

    context = {
        'form': form,
        'page_object': page_object,

        # Esto renderiza los resultados de la búsqueda solo si el usuario ha hecho una búsqueda
        'consulta': consulta if form.is_valid() else '',
    }
    return render(request, 'tests_administradores/buscador_de_preguntas.html', context)
