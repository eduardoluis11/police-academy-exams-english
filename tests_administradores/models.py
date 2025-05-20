from django.db import models

# Create your models here.

# Modelos de la app de Tests para Administradores

# Aqui es donde se almacenarán los tests y sus respectivas preguntas

""" Modelo para los Tests.

Aquí almacenaré los nombres de los tests. Por ejemplo, "Granada 2023".

Dado que los tests se deben poder agrupar por normativa, tema, y año, no me quedará de otra que agregarles campos de 
“año”, “tema”, y “normativa” a los registros del modelo de Tests().

Haré que los campos de “año”, “tema”, y “normativa” sean opcionales, ya que no se si todos los tests vayan a tener un
tema, o una normativa, o un año.

Tendré que agregar un nuevo campo a los Tests en el modelo de Test() para almacenar el tipo de examen (“por año”, 
“por normativa”, o “por tema”). Puedo poner un campo adicional que diga “Sin Especificar” por si acaso.

I'll add a list of choices and a field that uses those choices. This is a common Django pattern for enumerated values.

El campo “year” o "año" debe ser un “integer”, ya que ahí pondré el nombre del año (ej: "2023"). El nombre del test 
completo (ej: “Granada 2023”) lo pondré en “nombre del test”.

Dado a que un test por normativa puede tener varias normativas, voy a quitar el campo “normativa” del modelo de Test(). 
Y debo hacer algo similar con los tests de tipo “tema”: dado a que un test por tema puede tener preguntas de varios 
temas, le quitaré el campo “tema” al modelo de Test(). 

Puedo crear un campo llamado “test universal” para el modelo de Test(), y se lo asigno a los tests por año. Si el test 
es universal, tanto los administradores como todos los clientes podrán ver ese test por año (por ejemplo, “Granada 
2023”). Si el test no es universal, solo cogerás los tests generados proceduralmente por año de ese usuario en 
específico. O le puedo llamar “este test fue generado proceduralmente?” en vez de “test universal” para el modelo de 
Test(). Si no fue generado proceduralmente, es un test universal por año, y todo el mundo puede tomarlo. Pero, si fue 
generado proceduralmente (para ahorrarme tiempo, pondré que por defecto este boolean como “true”), solo el usuario 
logueado podra ver esos test por año, pero no podrá ver el de los demás.
"""


class Test(models.Model):

    # Define choices for the exam type as class variables
    # Nombres de las variables
    TIPO_NORMATIVA = 'normativa'
    TIPO_ANNO = 'año'
    TIPO_TEMA = 'tema'
    TIPO_SIN_ESPECIFICAR = 'sin especificar'
    # TIPO_ALEATORIO = 'aleatorio'

    # Opciones de los tipos de test como una lista de tuplas de Python
    TIPOS_DE_TEST = [
        (TIPO_NORMATIVA, 'Normativa'),
        (TIPO_ANNO, 'Año'),
        (TIPO_TEMA, 'Tema'),
        (TIPO_SIN_ESPECIFICAR, 'Sin especificar'),
        # (TIPO_ALEATORIO, 'Aleatorio'),
    ]

    nombre_del_test = models.CharField(max_length=255)  # Nombre del Test (ej.: "Granada 2023")

    # Tipo de Test ("año", "normativa", o "tema")
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_DE_TEST,
        default=TIPO_SIN_ESPECIFICAR  # Por defecto, a todos los tests se les pondrá "sin especificar"
    )

    # # Categorías por las que podré agrupar a los tests
    # tema = models.IntegerField(null=True, blank=True)           # Tema (e.g., 1, 2, 3, etc).
    # normativa = models.CharField(max_length=100, null=True, blank=True)  # Normativa (e.g., "Constitución Española").

    year = models.IntegerField(null=True, blank=True, verbose_name="Año")    # Año del test (e.g., 2023, 2024, etc).

    # Esto es para saber si el test fue generado proceduralmente o no
    fue_generado_proceduralmente = models.BooleanField(
        default=True, verbose_name="Este test fue generado proceduralmente?"
    )

    # year = models.CharField(max_length=255, null=True, blank=True, verbose_name="Año")    # Año (e.g., "2023")

    def __str__(self):
        return f"ID: {self.id} - {self.nombre_del_test}"

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Tests"


""" Modelo para las Preguntas para los Tests / Examenes.

ESTOS NO SON los nombres de los tests, ni los tests. SOLO SON las preguntas de los tests.

Aquí se guardan las preguntas, opciones, respuestas correctas y justificaciones de los archivos_con_modelos_de_tests / examenes.
Estos son los examenes vacíos.

I can see the exam data you provided in the document format. Based on that, I'll help you design a Django model and 
show you how to extract the fields from an Excel file. Since you mentioned having an Excel file, I'll assume it has 
a similar structure to the document you shared, with columns like "Examen", "Tema", "Normativa", "Pregunta", "A", 
"B", "C", "D", "Correcta", and "Justificación".

Modificaré el campo de “test” o “nombre de test” a many to many en el modelo de PreguntasDelTest, ya que una pregunta 
puede pertenecer a uno o muchos tests.

Y cambiaré el __str__ para quitar a cual test pertenece cada pregunta: asi, ya no me aparecera la palabra “none” en
el nombre del test para ese test.

I included the field "pregunta" in the str of this model, but only included a small slice of it. I didn't include the 
entire string with the question, because, otherwise, it would be too long. I only took the first 30 characters of the 
question followed by '...' (or the full question if shorter than 30 characters.)

El tema, el año, y la normativa de la pregunta serán opcionales. Así puede que tengas el año de la pregunta, pero no
el tema ni la normativa, o viceversa. 

Tengo que cambiar el campo de “año” de “integerField” a “CharField” (para poder meter “Granada 2023” como nombre del 
año).
"""


class PreguntaDelTest(models.Model):

    # Modifiqué el nombre del test para que tenga una relación de muchos a muchos con el modelo de Test
    nombre_del_test = models.ManyToManyField('tests_administradores.Test')

    # # Modifiqué el nombre del test para que sea tomado como FK del modelo de Test
    # nombre_del_test = models.ForeignKey('tests_administradores.Test', on_delete=models.CASCADE)

    # nombre_del_test = models.CharField(max_length=50)  # e.g., "Granada 2023"
    tema = models.IntegerField(null=True, blank=True)           # Tema. e.g., 1, 2, 3, etc. OPCIONAL.
    year = models.CharField(max_length=255, null=True, blank=True)  # Año (ej: "Granada 2023"). OPCIONAL.
    normativa = models.CharField(max_length=100, null=True, blank=True)  # Normativa. e.g., "Constitución Española".
    pregunta = models.TextField()           # The question text
    opcion_a = models.TextField()           # Option A
    opcion_b = models.TextField()           # Option B
    opcion_c = models.TextField()           # Option C
    opcion_d = models.TextField(blank=True, null=True)           # Opcion D. Esta es opcional
    respuesta_correcta = models.CharField(max_length=1)  # e.g., "A", "B", "C", or "D"
    justificacion = models.TextField()      # Explanation or legal reference

    # Esto me renderiza la ID y el tema de la pregunta, y una vista previa de la pregunta
    def __str__(self):
        question_preview = self.pregunta[:30] + '...' if len(self.pregunta) > 30 else self.pregunta
        return f"ID: {self.id} - Tema {self.tema} - {question_preview}"

    # Esto es lo que me causa el bug de que no puedo renderizar el modelo de PreguntaDelTest en el panel de admin
    # def __str__(self):
    #     return f"{self.nombre_del_test.nombre_del_test} - Pregunta {self.tema}"

    class Meta:
        verbose_name = "Pregunta Del Test"
        verbose_name_plural = "Preguntas de los Tests"


# """ Modelo para mostrar la relacion entre Test y PreguntaDelTest.
#
# I just want to show yet another table using admin.site.register(). But, in this case, I want to render the model that is created between the Test and the PreguntasDelTest model since I used a many to many relationship between those 2 models.
#
# To display the automatically created many-to-many intermediate table in the admin panel, you can use the through attribute. First, explicitly define the intermediate model in your models.py.
#
# This will add the many-to-many relationship table to your admin panel, showing the connections between tests and questions.
# """
#
#
# class TestPreguntaRelation(models.Model):
#     pregunta = models.ForeignKey(PreguntaDelTest, on_delete=models.CASCADE)
#     test = models.ForeignKey(Test, on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = 'tests_administradores_preguntadeltest_nombre_del_test'
#
#     def __str__(self):
#         return f"{self.test.nombre_del_test} - Pregunta {self.pregunta.id}"
