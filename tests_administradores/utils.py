import pandas as biblioteca_pandas
from django.core.exceptions import ValidationError

# Modelos que voy a importar
from .models import PreguntaDelTest, Test

# Usaré esto para agarrar el PATH o ruta de los archivos de Excel de la carpeta media
from django.conf import settings
import os

""" Script que escanea los archivos de Excel y guarda la información extraída en la base de datos, el
cual se ejecutará usando una vista de Django. No necesito usar el shell de Python para ejecutar este script.

Este script es lo que mete la información extraída del Excel a los modelos de Test() y PreguntaDelTest() en la base de 
datos.

Tengo que modificar este script, ya que ahora el nombre del test se asigna al modelo de PreguntaDelTest() al campo 
"nombre del test" como un Many To Many Field. 

Extract Data from the Excel File

Assuming your Excel file has headers matching the fields in your document (e.g., "Examen", "Tema", "Normativa", etc.), 
you can write a script to read the file and populate your database.

Notes:

Ensure your Excel column names match the ones in the document (Examen, Tema, etc.). If they differ, adjust the 
row['...'] keys accordingly.

Run this script after setting up your database and migrations (see below).

Run the script:
You can run the script standalone or integrate it into a Django management command. To run it standalone:
bash
python script.py

(Ensure your Django environment is loaded if running standalone—e.g., by running it in the Django shell: 
python manage.py shell and pasting the code.)

# Utility Function (Data Extraction Logic)
Move the Excel processing logic into a reusable function in a utils.py file.

Why: Separates logic from the view, improves testability, and centralizes error handling.

Best Practices: Uses full_clean() for model validation, handles exceptions gracefully, and provides detailed feedback.

Cada vez que subas un excel, subes un examen distinto.

Tal vez cree otro modelo que se llame “tests” o “nombres de los tests” , y solo guarde los nombres de los tests. Luego, 
metere esos nombres de tests como FK en el modelo de “preguntas de los tests”.

To ensure that the exam names are unique and to avoid inserting duplicate instances, you can modify the code to check 
if the Test instance already exists before creating a new one. If it exists, fetch the existing instance and use it. 

Problem 1: Incorrect assignment of ManyToMany field When working with ManyToMany fields, you can't directly assign 
values during model creation. Instead, you need to:  
    Create the model instance first
    Save it
    Add the relationship using add()

The key difference is that we:
    Remove the nombre_del_test from the initial creation
    Save the instance first
    Use add() to create the many-to-many relationship

Cuando se cree un test al importarlo de un excel, o después de crearlo manualmente, tengo que marcar ese test como “por 
año” en el campo “tipo”.

Los archivos Excel van a tener una columna adicional que se llama “Año”, que es el año del examen. Pues, de esa 
columna, tengo que sacar el año del examen y guardarlo en el modelo de Test().

I need to ensure that NULL values in the Excel file are properly handled and stored as NULL in the database, instead 
of as "nan" strings. To handle NULL values from Excel properly, you should add a check before assigning option D. So,
I will need to add the following changes:

1. Added a check using `biblioteca_pandas.isna()` to detect NaN values.
2. Set option D to `None` if the value is NaN, otherwise use the actual value.
3. Pass the checked value to the model.

Todo test creado al importar un excel será un test que todos los usuarios podrán ver. Es decir, que es un test que
no fue generado proceduralmente. Entonces, al crear la instancia del test, quiero que el campo "fue generado 
proceduralmente" sea falso.
"""


def import_exams_from_excel(file_path):
    """
    Extracts exam data from an Excel file and inserts it into the Test() and PreguntaDelTest() models.
    Returns a tuple: (success_count, error_messages).
    """
    success_count = 0
    error_messages = []

    try:
        # Read the Excel file
        datos_del_archivo_excel = biblioteca_pandas.read_excel(file_path)
        if datos_del_archivo_excel.empty:
            raise ValidationError("El archivo de Excel está vacío.")

        # Valida las columnas del archivo de Excel que esperas encontrar
        expected_columns = ['Examen', 'Tema', 'Normativa', 'Pregunta', 'A', 'B', 'C', 'D', 'Correcta', 'Justificación',
                            'Año']
        if not all(col in datos_del_archivo_excel.columns for col in expected_columns):
            missing = [col for col in expected_columns if col not in datos_del_archivo_excel.columns]
            raise ValidationError(f"Columnas que faltan en el archivo de Excel: {', '.join(missing)}")

        # Process each row
        for index, row in datos_del_archivo_excel.iterrows():
            try:

                # Esto crea una instancia del modelo de Test si el Test no existe, o lo coge si ya existe
                # Check if the Test instance already exists.
                test_instance, created = Test.objects.get_or_create(
                    nombre_del_test=row['Examen'],
                    tipo="año",  # Todo test importado de un Excel es un test por año, por lo que debo asignarle el tipo
                    year=row['Año'],  # Año del test
                    fue_generado_proceduralmente=False  # Indico que este es un test universal
                )

                # Check if option D is NaN or None and handle it accordingly
                opcion_d = None if biblioteca_pandas.isna(row['D']) else row['D']

                # test_instance = Test(nombre_del_test=row['Examen'])
                # test_instance.full_clean()  # Validate model fields
                # test_instance.save()

                # Esto mete los datos de las preguntas del test en el modelo de PreguntaDelTest
                # Create an instance of the PreguntaDelTest model using the test_instance as the name of the exam
                pregunta_del_test = PreguntaDelTest(
                    # nombre_del_test=test_instance,
                    tema=row['Tema'],
                    normativa=row['Normativa'],
                    pregunta=row['Pregunta'],
                    opcion_a=row['A'],
                    opcion_b=row['B'],
                    opcion_c=row['C'],
                    opcion_d=opcion_d,  # Use the checked value
                    # opcion_d=row['D'],
                    respuesta_correcta=row['Correcta'],
                    justificacion=row['Justificación'],
                    year=row['Año'],  # Año del test
                )
                pregunta_del_test.full_clean()  # Validate model fields
                pregunta_del_test.save()  # Esto guarda los cambios en la instancia de esta Pregunta Del Test

                # Después de guardar los cambios en la pregunta actual, se añade la pregunta al Test() usando add()
                pregunta_del_test.nombre_del_test.add(test_instance)

                success_count += 1
            except Exception as e:
                error_messages.append(f"Row {index + 2}: {str(e)}")  # +2 to match Excel row numbers
    except Exception as e:
        error_messages.append(f"No se pudo procesar el archivo: {str(e)}")

    return success_count, error_messages

# # Path to your Excel file.
# # Esto debe ser la URL a la carpeta "media" con los tests. Esta en la ruta
# # "media\archivos_con_modelos_de_tests".
# excel_file = os.path.join(settings.MEDIA_ROOT, 'archivos_con_modelos_de_tests', 'test-1.xlsx')
#
# # # DEBUGGEO. BORRAR. Esto me imprime el PATH que me está agarrando.
# # print("Esta es la ruta en la que estoy tratando de agarrar el archivo Excel" + excel_file)
#
# # excel_file = "path/to/your/exam_file.xlsx"
#
# # Read the Excel file
# df = pd.read_excel(excel_file)
#
# # Iterate over the rows and save to the database.
# """ Tengo que poner el nombre de cada campo del modelo de Test para asi meterle cada dato extraido del Excel
# al campo que le corresponde del modelo de Test en la base de datos.
#
# Por cada fila y columna de mi archivo de Excel, es decir, por cada campo de cada examen de mi archivo de Excel
# que estoy escaneando, voy a crear una instancia del modelo de Test() y le voy a meter los datos de cada campo de cada
# examen de mi archivo de Excel. Luego, voy a guardar los cambios hechos en la base de datos en el modelo de Test.
# """
# for index, row in df.iterrows():
#     test = Test(
#         nombre_del_test=row['Examen'],
#         tema=row['Tema'],
#         normativa=row['Normativa'],
#         pregunta=row['Pregunta'],
#         opcion_a=row['A'],
#         opcion_b=row['B'],
#         opcion_c=row['C'],
#         opcion_d=row['D'],
#         respuesta_correcta=row['Correcta'],
#         justificacion=row['Justificación']
#     )
#     test.save()
#
# ## DEBUGGEO. BORRAR.
# print("Data successfully imported into the database!")