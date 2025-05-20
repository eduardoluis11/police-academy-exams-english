from django.db import models

# This will access my base.py file with my settings
from django.conf import settings  # Import settings


from tests_administradores.models import PreguntaDelTest  # Modelo de Test de tests para administradores

# Create your models here.

from django.contrib.auth.models import User
from django.utils import timezone

""" Modelos de la app de tests para clientes.

We need a model to track user sessions and answers.

## Why:

Run migrations after adding these models.
"""

# Esto me importa el modelo de Test de la app de tests para administradores

""" Modelo para las Sesiones de los Tests de cada cliente.

Esto almacena cada intento de un test del usuario. Esto incluye la hora de inicio, la hora de finalización, 
la dificultad, y la puntuación que sacó en ese intento en ese test.

ExamSession: Tracks each user’s exam attempt, including start/end time and score.

Dejame modificarle el __str__ al panel de admin de django al modelo de Sesion del Test para que salga la ID de la 
Sesion, para asi poder diferenciar cada sesión.

Dado a que el usuario puede seleccionar después la dificultad que quiera, puedo poner el nivel de dificultad en cada 
sesión. Por lo tanto, tendré que modificar el modelo de Sesion del Test para incluir un campo que almacene la 
dificultad. 

Sobre el nivel de dificultad de los test, hay 5 modos que el usuario puede elegir antes de empezar:

Ordenados de más restrictivo a menos restrictivo:
- 1:1. 1 respuesta mal resta 1 respuesta bien (más difícil)
- 2:1. 2 respuestas mal restan 1 bien
- 3:1. 3 respuestas mal restan 1 bien
- 4:1. 4 respuestas mal restan 1 bien
- Errores no restan (más fácil)

Agregué un nuevo campo que almacena cuanto tiempo le queda al cliente para terminar el test. Esto es para que, si el 
cliente interrumpe el test, pueda volver a tomarlo y se le quede guardado en el cronómetro cuanto tiempo le queda.
Es decir, si le quedaban 10 minutos para terminar el test, y lo interrumpió, cuando vuelva a tomar el test, le quedará
guardado que le quedan 10 minutos para terminar el test.

Si el límite de tiempo es infinito o ilimitado, dejaré el campo de tiempo restante como "null".
"""


class SesionDelTest(models.Model):

    # I will call my AbstractUser model, which I nicknamed "User", from my "autenticacion" app
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)     # Nombre del usuario que está tomando el test
    hora_de_inicio = models.DateTimeField(auto_now_add=True)    # Hora de inicio del test
    hora_del_fin_del_test = models.DateTimeField(null=True, blank=True)     # Hora de finalización del test

    # Time limit in seconds (e.g., 1800 minutes)
    limite_de_tiempo = models.IntegerField(default=1800, null=True, blank=True)

    # Nombre del Test del cliente. Se debe tomar como FK del modelo de Test de la app de Tests
    nombre_del_test = models.ForeignKey('tests_administradores.Test', on_delete=models.CASCADE)

    # Nivel de dificultad del test que seleccionó el cliente
    nivel_de_dificultad = models.CharField(max_length=50, default='Errores no restan puntos')

    # Puntuación que sacó el cliente en el test en el intento actual
    puntuacion = models.FloatField(null=True, blank=True)

    # Esto me dice si el cliente ya tomó y terminó el test o no. Si es "False", el cliente puede seguir tomando el test.
    cliente_entrego_este_test = models.BooleanField(default=False)

    # Esto me guarda el tiempo en segundos de cuanto tiempo le queda al cliente para terminar el test (OPCIONAL)
    tiempo_restante = models.IntegerField(null=True, blank=True)

    # Esto me dice si el test es de autocorrección o no. Si es "True", el test es de autocorrección.
    test_autocorregido = models.BooleanField(default=False)

    # # ESTO NO LO VOY A USAR
    # # New field for custom questions
    # preguntas_seleccionadas = models.TextField(null=True, blank=True)
    # # Format: comma-separated question IDs, e.g., "1,4,7,10"
    #
    # def get_custom_question_ids(self):
    #     """Helper method to get list of custom question IDs if any"""
    #     if not self.preguntas_seleccionadas:
    #         return None
    #     return [int(id) for id in self.preguntas_seleccionadas.split(',')]

    # Esto me renderiza el ID de la Sesión, el nombre del usuario y el nombre del test
    def __str__(self):
        return f"ID de Sesión: {self.id} - {self.usuario.username} - {self.nombre_del_test}"


""" Modelo para las Respuestas Enviadas por los clientes para cada pregunta en los Tests.

UserAnswer: Stores each answer, linking it to a question and session.

is_correct: Automatically calculated when saving an answer.

Lo que quiero saber es el nombre del examen, el nombre de usuario del cliente, la pregunta, y la respuesta seleccionada. 
Al principio de todo eso, puedo poner la ID. Tal vez también necesite la sesión.
 
E igual, si el usuario cambia su respuesta, debo borrar la respuesta 
anterior, y poner la respuesta nueva a esa pregunta.

Now, for this model, could you modify this function so that, when comparing the selected answer with the actual answer 
in the "respuesta_seleccionada" field, can you make sure it's case-insensitive? Right now, all of the answers in my 
template have upper case letters as values. However, I sometimes write the answers in the actual exam with lower case 
letters. This leads to a bug in which, if I chose "A" as the answer, but I typed in the database that the actual answer 
was "a", it will be marked as wrong. 

Here's the modified save method that makes the answer comparison case-insensitive. This uses the upper() method to 
convert both strings to uppercase before comparison. You could also use lower() - either way will work as long as 
both strings are converted to the same case. 
"""


class RespuestaDelUsuario(models.Model):

    # Esto me almacena la pregunta que respondió el cliente en el examen
    pregunta = models.ForeignKey(PreguntaDelTest, on_delete=models.CASCADE)

    # Sesion del Test. Aqui obtengo datos como el nombre del usuario que está tomando el test, el nombre del test
    sesion = models.ForeignKey(SesionDelTest, on_delete=models.CASCADE, related_name='answers')

    # Esto almacena la respuesta del cliente es correcta o no. Ver en "def save()" para más detalles.
    es_correcto = models.BooleanField(default=False)

    # Esto almacena la respuesta seleccionada por el cliente
    respuesta_seleccionada = models.CharField(max_length=1)  # e.g., "A", "B", "C", "D"

    # Esto compara la respuesta seleccionada por el cliente con la respuesta correcta de la pregunta
    def save(self, *args, **kwargs):

        # Si la respuesta seleccionada es correcta, entonces se marca la respuesta como correcta ("True").
        # Convert both answers to uppercase (or lowercase) before comparing.
        self.es_correcto = (self.respuesta_seleccionada.upper() == self.pregunta.respuesta_correcta.upper())

        # self.es_correcto = (self.respuesta_seleccionada == self.pregunta.respuesta_correcta)

        # Esto guarda si la respuesta seleccionada es correcta o no
        super().save(*args, **kwargs)

    # Esto me debe imprimir el nombre de usuario, la ID de la pregunta, y la respuesta seleccionada
    def __str__(self):
        return f"{self.sesion.usuario} - ID de Pregunta: {self.pregunta.id} - Respuesta Seleccionada: {self.respuesta_seleccionada}"


""" Modelo de Preguntas Guardadas por el Usuario.

Aquí es donde se van a almacenar las preguntas que el cliente decida guardar de sus tests para consultar más tarde.

Almacenará mínimo 2 campos: la instancia de la pregunta de la PreguntaDelTest(), y la instancia del usuario que guardó 
esa pregunta. 

Dado que tengo que guardar de que examen vino esa pregunta, y dado a que muchos exámenes pueden tener la misma pregunta 
(por ejemplo, si es por tema o por normativa), entonces, necesito datos adicionales sobre la pregunta guardada por el 
usuario (en este caso, quiero saber el test al que pertenece esa pregunta). Entonces, no debo usar un many to many 
relationship. En su lugar, tengo que crear un nuevo modelo.

Entonces, necesito almacenar mínimo 3 campos: el usuario al que le pertenece la pregunta guardada, la pregunta en sí,
y el test al que pertenece esa pregunta.

Por si acaso, mejor guardo también la sesión de donde agarré esa pregunta. Modificaré el modelo de PreguntasGuardadas() 
para guardar también la sesión.
"""


class PreguntaGuardadaPorElUsuario(models.Model):
    # Esto me almacena la pregunta que guardó el cliente
    pregunta = models.ForeignKey(PreguntaDelTest, on_delete=models.CASCADE)

    # Esto me almacena el usuario que guardó la pregunta.
    # I will call my AbstractUser model, which is in in my base.py file, under the variable AUTH USER MODEL.
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Esto me almacena el test al que pertenece la pregunta
    test = models.ForeignKey('tests_administradores.Test', on_delete=models.CASCADE)

    # Esto me almacena la sesión del test en la que el cliente guardó la pregunta
    sesion = models.ForeignKey(SesionDelTest, on_delete=models.CASCADE, null=True, blank=True)

    # Esto me imprime el nombre de usuario, la ID de la pregunta, y el nombre del test
    def __str__(self):
        return f"{self.usuario.username} - ID de Pregunta: {self.pregunta.id} - Test: {self.test.nombre_del_test}"
