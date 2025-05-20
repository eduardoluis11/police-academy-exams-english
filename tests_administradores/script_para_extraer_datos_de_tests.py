import pandas as pd
from tests_administradores.models import Test  # Replace 'your_app' with your app name

# Usaré esto para agarrar el PATH o ruta de los archivos de Excel de la carpeta media
from django.conf import settings
import os

""" CREO QUE ESTE ARCHIVO NO SE ESTÁ USANDO, NI TAMPOCO SE DEBE USAR. SOLO SE DEBE USAR el utils.py para importar
los Excels.
"""

# Script que escanea los archivos de Excel y guarda la información extraída en la base de datos.

""" Extract Data from the Excel File

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
"""

# Path to your Excel file.
# Esto debe ser la URL a la carpeta "media" con los tests. Esta en la ruta
# "media\archivos_con_modelos_de_tests".
excel_file = os.path.join(settings.MEDIA_ROOT, 'archivos_con_modelos_de_tests', 'test-1.xlsx')

# # DEBUGGEO. BORRAR. Esto me imprime el PATH que me está agarrando.
# print("Esta es la ruta en la que estoy tratando de agarrar el archivo Excel" + excel_file)

# excel_file = "path/to/your/exam_file.xlsx"

# Read the Excel file
df = pd.read_excel(excel_file)

# Iterate over the rows and save to the database.
""" Tengo que poner el nombre de cada campo del modelo de Test para asi meterle cada dato extraido del Excel
al campo que le corresponde del modelo de Test en la base de datos.

Por cada fila y columna de mi archivo de Excel, es decir, por cada campo de cada examen de mi archivo de Excel
que estoy escaneando, voy a crear una instancia del modelo de Test() y le voy a meter los datos de cada campo de cada 
examen de mi archivo de Excel. Luego, voy a guardar los cambios hechos en la base de datos en el modelo de Test.
"""
for index, row in df.iterrows():
    test = Test(
        nombre_del_test=row['Examen'],
        tema=row['Tema'],
        normativa=row['Normativa'],
        pregunta=row['Pregunta'],
        opcion_a=row['A'],
        opcion_b=row['B'],
        opcion_c=row['C'],
        opcion_d=row['D'],
        respuesta_correcta=row['Correcta'],
        justificacion=row['Justificación']
    )
    test.save()

# ## DEBUGGEO. BORRAR.
# print("Data successfully imported into the database!")

