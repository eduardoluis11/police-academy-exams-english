from django.test import TestCase, Client

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import reverse
import os

from tests_administradores.models import Test, PreguntaDelTest

import pandas as biblioteca_pandas

# Create your archivos_con_modelos_de_tests here.

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

# Esto importa mis modelos
from tests_administradores.models import Test, PreguntaDelTest

from tests_administradores.forms import NombreDelTestFormulario, CrearPreguntaDelTestFormSet
from django.contrib.messages import get_messages


""" Test para probar la vista de crear un nuevo test sin subir un archivo Excel para administradores.

I'll create a comprehensive Django unit test for the `crear_nuevo_test_sin_subir_un_archivo()` view. I'll create an 
artifact with the test case that covers various scenarios.


I've created a comprehensive unit test suite for the `crear_nuevo_test_sin_subir_un_archivo()` view with the following 
test cases:

1. `test_crear_nuevo_test_view_staff_access()`: Verifies that staff users can access the view.
2. `test_crear_nuevo_test_view_non_staff_access()`: Ensures non-staff users are redirected.
3. `test_crear_nuevo_test_successful_creation()`: Tests successful test and question creation.
4. `test_crear_nuevo_test_invalid_form()`: Checks form validation and prevents invalid test creation.

The test suite covers several key scenarios:
- Access control
- Successful test creation with multiple questions
- Form validation
- Redirection after successful creation
- Verifying model instances are created correctly

A few important notes:
- Make sure to replace `'tests_administradores:crear_nuevo_test_sin_subir_un_archivo'` and 
`'tests_clientes:lista_de_tests'` with your actual URL names.
- Ensure you have the necessary imports for your models and forms.
- You might need to adjust the test data to match your exact model fields.

To run these tests, you would typically use the Django test runner:
```bash
python manage.py test tests_administradores.tests
```

The key changes are:
    Using capital letters for respuesta_correcta choices.
    Toda instancia de "Tema" tiene que estar como un integer, no como una cadena.
"""


class CrearNuevoTestViewTestCase(TestCase):
    def setUp(self):
        # Create a staff user for testing
        self.staff_user = User.objects.create_user(
            username='admin_test',
            password='testpassword123',
            is_staff=True
        )

        # Create a non-staff user to test access restrictions
        self.non_staff_user = User.objects.create_user(
            username='regular_user',
            password='testpassword123',
            is_staff=False
        )

        # Client for making requests
        self.client = Client()

    def test_crear_nuevo_test_view_staff_access(self):
        """
        Test that only staff users can access the view
        """
        # Log in as staff user
        self.client.login(username='admin_test', password='testpassword123')

        # Get the view
        response = self.client.get(reverse('tests_administradores:crear_nuevo_test_sin_subir_un_archivo'))

        # Assert staff user can access the view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tests_administradores/crear_nuevo_test_sin_archivo.html')

    # Funciona
    def test_crear_nuevo_test_view_non_staff_access(self):
        """
        Test that non-staff users cannot access the view
        """
        # Log in as non-staff user
        self.client.login(username='regular_user', password='testpassword123')

        # Get the view
        response = self.client.get(reverse('tests_administradores:crear_nuevo_test_sin_subir_un_archivo'))

        # Assert non-staff user is redirected to admin login
        self.assertRedirects(response, '/admin/login/?next=/tests-administradores/crear-nuevo-test/')
        # Corregiré esto, ya que no quiero que me redirija al login de admin, sino que me redirija al login de la app
        # self.assertRedirects(response, '/admin/login/')

    # Este test por fin me funciona. Esto me crea un nuevo test con multiples preguntas.
    def test_crear_nuevo_test_successful_creation(self):
        """
        Test successful creation of a new test with multiple questions
        """
        # Log in as staff user
        self.client.login(username='admin_test', password='testpassword123')

        # Prepare test data
        form_data = {
            'nombre_del_test': 'Test de Prueba',

            # Formset data for questions
            'preguntas-TOTAL_FORMS': 2,
            'preguntas-INITIAL_FORMS': '0',
            'preguntas-MIN_NUM_FORMS': '0',
            'preguntas-MAX_NUM_FORMS': '1000',

            # First question
            # El Tema debe ser un integer, no un string
            'preguntas-0-tema': 1,
            'preguntas-0-normativa': 'Normativa 1',
            'preguntas-0-pregunta': '¿Pregunta de prueba 1?',
            'preguntas-0-opcion_a': 'Opción A 1',
            'preguntas-0-opcion_b': 'Opción B 1',
            'preguntas-0-opcion_c': 'Opción C 1',
            'preguntas-0-opcion_d': 'Opción D 1',
            'preguntas-0-respuesta_correcta': 'A', # Tiene que ser una letra mayúscula
            'preguntas-0-justificacion': 'Justificación 1',

            # Second question
            # El Tema debe ser un integer, no un string
            'preguntas-1-tema': 2,
            'preguntas-1-normativa': 'Normativa 2',
            'preguntas-1-pregunta': '¿Pregunta de prueba 2?',
            'preguntas-1-opcion_a': 'Opción A 2',
            'preguntas-1-opcion_b': 'Opción B 2',
            'preguntas-1-opcion_c': 'Opción C 2',
            'preguntas-1-opcion_d': 'Opción D 2',
            'preguntas-1-respuesta_correcta': 'B',  # Tiene que ser una letra mayúscula
            'preguntas-1-justificacion': 'Justificación 2',
        }

        # Submit the form
        response = self.client.post(
            reverse('tests_administradores:crear_nuevo_test_sin_subir_un_archivo'),
            data=form_data
        )

        # # Print out any form errors
        # if response.status_code == 200:
        #     # If the response is 200, it means the form didn't validate
        #     # So let's print out the form errors
        #     print("Form Errors:", response.context['campo_nombre_del_test'].errors)
        #     print("Formset Errors:", response.context['formset'].errors)
        #
        # # Print response content for additional debugging
        # print("Response Status Code:", response.status_code)
        # print("Response Content:", response.content.decode('utf-8'))

        # Check redirect after successful creation
        self.assertRedirects(response, reverse('tests_clientes:lista_de_tests'))

        # Verify test was created
        test = Test.objects.get(nombre_del_test='Test de Prueba')
        self.assertIsNotNone(test)

        # Verify questions were created
        preguntas = PreguntaDelTest.objects.filter(nombre_del_test=test)
        self.assertEqual(preguntas.count(), 2)

        # Check specific question details
        primera_pregunta = preguntas.first()

        # Los temas son integers, no strings. Por lo tanto, puse "1" en lugar de "Tema 1"
        self.assertEqual(primera_pregunta.tema, 1)
        self.assertEqual(primera_pregunta.pregunta, '¿Pregunta de prueba 1?')

    def test_crear_nuevo_test_invalid_form(self):
        """
        Test form validation prevents test creation with invalid data
        """
        # Log in as staff user
        self.client.login(username='admin_test', password='testpassword123')

        # Prepare invalid test data (missing required fields)
        form_data = {
            'nombre_del_test': '',  # Empty test name

            'preguntas-TOTAL_FORMS': '1',
            'preguntas-INITIAL_FORMS': '0',
            'preguntas-MIN_NUM_FORMS': '0',
            'preguntas-MAX_NUM_FORMS': '1000',

            'preguntas-0-tema': '',  # Missing required fields
        }

        # Submit the form
        response = self.client.post(
            reverse('tests_administradores:crear_nuevo_test_sin_subir_un_archivo'),
            data=form_data
        )

        # Check that the form is not valid and no redirect occurs
        self.assertEqual(response.status_code, 200)

        # Check for error messages
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Por favor, corrija los errores' in str(msg) for msg in messages))

        # Verify no test was created
        self.assertEqual(Test.objects.count(), 0)
        self.assertEqual(PreguntaDelTest.objects.count(), 0)


""" Test para probar la vista de subir archivos Excel para crear un nuevo Test / Examen.

Esto me dice si el view de tests_administradores:upload_and_import_exams() funciona correctamente.

Generate me a test for the upload_and_import_exams() view. This view asks the user to upload an excel file. Then, 
from that excel file, it extracts data as a string, and then inserts it into 2 models. It first uploads the excel file 
into my media folder, and then, after extracting all the data as a string, it deletes that excel from my media folder. 
Well, knowing all that, create a unit test for this view to check that it works properly.

The issue is with the test method names. Currently, the test runner doesn't recognize them because they don't start with `test_`. Here's the fix:

**Problem 1: Test methods not recognized**
The method names need to start with `test_` for Django's test runner to find them.

To run the tests:
```bash
python manage.py test tests_administradores.tests
```

Es decir, cada uno de los "def" debe empezar con el nombre "test_" para que Django los reconozca como tests (ej:
"def test_normal_user_cannot_access_upload_page(self):")
"""


class UploadAndImportExamsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.url = reverse('tests_administradores:upload_and_import_exams')
        self.excel_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"  # Minimal valid Excel file bytes

    # Esto funciona.
    def test_normal_user_cannot_access_upload_page(self):
        normal_user = User.objects.create_user(username='user', password='userpass123')
        self.client.login(username='user', password='userpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    # Esto funciona.
    def test_admin_can_access_upload_page(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tests_administradores/subir_archivos_con_tests.html')

    # Esto me genera un "FAIL".
    # def test_valid_excel_file_uploads_successfully(self):
    #     self.client.login(username='admin', password='adminpass123')
    #     excel_file = SimpleUploadedFile("test.xlsx", self.excel_content)
    #
    #     response = self.client.post(self.url, {'excel_file': excel_file})
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Successfully imported")

    # Esto me genera un "ERROR".
    def test_valid_excel_file_uploads_successfully(self):
        self.client.login(username='admin', password='adminpass123')

        # Create valid Excel file content with required columns
        excel_data = {
            'Examen': ['Test 1'],
            'Tema': ['Topic 1'],
            'Normativa': ['Law 1'],
            'Pregunta': ['Question 1?'],
            'A': ['Option A'],
            'B': ['Option B'],
            'C': ['Option C'],
            'D': ['Option D'],
            'Correcta': ['A'],
            'Justificación': ['Because A is correct']
        }
        excel_file = biblioteca_pandas.DataFrame(excel_data)

        # Save DataFrame to temporary file and read bytes
        excel_file.to_excel('test.xlsx', index=False)
        with open('test.xlsx', 'rb') as file:
            buffer = file.read()
        os.remove('test.xlsx')  # Clean up temporary file

        # # Save DataFrame to bytes buffer
        # from io import BytesIO
        # buffer = BytesIO()
        # with biblioteca_pandas.ExcelWriter(buffer, engine='openpyxl') as writer:
        #     excel_file.to_excel(writer, index=False)

        # Create uploaded file
        excel_file = SimpleUploadedFile(
            "test.xlsx",
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response = self.client.post(self.url, {'excel_file': excel_file})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Test.objects.filter(nombre_del_test='Test 1').exists())
        self.assertTrue(PreguntaDelTest.objects.filter(pregunta='Question 1?').exists())
        pregunta = PreguntaDelTest.objects.get(pregunta='Question 1?')
        self.assertEqual(list(pregunta.nombre_del_test.values_list('nombre_del_test', flat=True)), ['Test 1'])

    # # Esto me genera un "FAIL".
    # def test_valid_excel_file_uploads_successfully(self):
    #     self.client.login(username='admin', password='adminpass123')
    #     # Create a proper Excel file content
    #     excel_content = b'PK\x03\x04\x14\x00\x08\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # Valid Excel file bytes
    #     excel_file = SimpleUploadedFile("test.xlsx", excel_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #     response = self.client.post(self.url, {'excel_file': excel_file})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotContains(response, "Failed to process file")

    # Instead of assertFormError, check for error message in response content.
    # Esto me genera un "FAIL".
    def test_invalid_file_type_returns_error(self):
        self.client.login(username='admin', password='adminpass123')
        txt_file = SimpleUploadedFile("test.txt", b"some text content")
        response = self.client.post(self.url, {'excel_file': txt_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Failed to process file")

    # Esto me generar un "ERROR" en el test. No se si eso sea mejor o peor que un "FAIL".
    # def test_invalid_file_type_returns_error(self):
    #     self.client.login(username='admin', password='adminpass123')
    #     txt_file = SimpleUploadedFile("test.txt", b"some text content")
    #
    #     response = self.client.post(self.url, {'excel_file': txt_file})
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFormError(response, 'form', 'excel_file', 'File must be an Excel file')

    # Esto funciona.
    def test_uploaded_file_is_deleted_after_processing(self):
        self.client.login(username='admin', password='adminpass123')
        excel_file = SimpleUploadedFile("test.xlsx", self.excel_content)

        self.client.post(self.url, {'excel_file': excel_file})

        file_path = os.path.join('media', 'archivos_con_modelos_de_tests', 'test.xlsx')
        self.assertFalse(os.path.exists(file_path))