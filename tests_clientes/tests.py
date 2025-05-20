from django.contrib.auth.models import User
from django.test import TestCase, Client

from tests_administradores.models import Test, PreguntaDelTest
from tests_clientes.models import SesionDelTest, RespuestaDelUsuario

""" Unit Tests para la app de clientes.

When considering different difficulty levels for your unit tests, you should ensure that each difficulty level is 
tested to verify that the scoring logic is correctly applied. Here are some test cases you should consider:

1. **Difficulty Level 1: No Penalty for Wrong Answers**
   - Test with all correct answers.
   - Test with all wrong answers.
   - Test with a mix of correct and wrong answers.
   - Test with some unanswered questions.

2. **Difficulty Level 2: 4 Wrong Answers Eliminate 1 Correct Answer**
   - Test with all correct answers.
   - Test with all wrong answers.
   - Test with a mix of correct and wrong answers (e.g., 4 wrong answers should eliminate 1 correct answer).
   - Test with some unanswered questions.

3. **Difficulty Level 3: 3 Wrong Answers Eliminate 1 Correct Answer**
   - Test with all correct answers.
   - Test with all wrong answers.
   - Test with a mix of correct and wrong answers (e.g., 3 wrong answers should eliminate 1 correct answer).
   - Test with some unanswered questions.

4. **Difficulty Level 4: 2 Wrong Answers Eliminate 1 Correct Answer**
   - Test with all correct answers.
   - Test with all wrong answers.
   - Test with a mix of correct and wrong answers (e.g., 2 wrong answers should eliminate 1 correct answer).
   - Test with some unanswered questions.

5. **Difficulty Level 5: 1 Wrong Answer Eliminates 1 Correct Answer**
   - Test with all correct answers.
   - Test with all wrong answers.
   - Test with a mix of correct and wrong answers (e.g., 1 wrong answer should eliminate 1 correct answer).
   - Test with some unanswered questions.

Here is an example of how you might write a unit test for difficulty level 2:

You can create similar tests for other difficulty levels by adjusting the `nivel_de_dificultad` and the expected 
results accordingly.

Recuerda que tengo que poner "test_" antes de cada test para que el CLI / la consola lo reconozca como un test
al ejecutar "python manage.py test".
"""

# Create your archivos_con_modelos_de_tests here.

""" Unit Test para la Vista de Resultados de los Tests.

Let's make some unit tests to verify that I get normal behavior when an user takes an exam. Let's make first unit 
tests for when the user takes a test from case 1: when wrong answers don't penalize right answers. Create a super user 
to test the exam view, since super users can take exams, and creating regular users would be a bit tricky since they 
require to have an active subscription in a wordpress online store. So, give all this, make a unit test for when a 
super user takes an exam in the case 1 difficulty.

Now, I've added 7 more questions to my exam for my unit tests, so that now my exam has a total of 10 questions. So, 
update the selecte test (test cas 1 wrong answers don't penalize) so that it takes into account that there are a total 
of 10 questions for the exam, not of 3.

I also created a test for the difficulty at case 3: where 3 wrong answers penalize 1 correct answer.

Next, I made a test for when a user takes an exam with the 4th case of difficulty: when 2 wrong answers penalize 1 
correct answer. Remember that I have a total of 10 questions.

My difficulty levels only penalize questions as integers, not as floats. So, I won't get 1/3 of a good question if I 
answer 1 wrong answer in the 3:1 difficulty. I will either lose 1 good answer after 3 bad answers, or not lose any 
good answers at all. 

Finally, I also made a unit test for the case in which the user takes an exam in which 1 wrong answer eliminates 1 
correct answer.

Las notas ahora van a ser de 0 a 10, y no de 0 a 100. Así que voy a cambiar la puntuación para que sea de 0 a 10, y no 
de 0 a 100.
"""


class ResultadosTestsViewTestCase(TestCase):

    # Esto prepara los datos que se reusarán en los tests (como el usuario y las preguntas)
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@test.com'
        )
        self.client = Client()

        # Esto crea el Nombre del Test en Test()
        self.test = Test.objects.create(nombre_del_test='Test de Prueba')

        # superuser = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        # test = Test.objects.create(nombre_del_test='Diez Preguntas ARREGLADO')

        # Esto crea las preguntas
        # Create test questions
        # Primera pregunta
        self.pregunta1 = PreguntaDelTest.objects.create(
            tema=1,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 1',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='A',
            justificacion='Justificación de prueba'
        )

        # Le agrego el nombre del test de Test() a esta pregunta con un add()
        self.pregunta1.nombre_del_test.add(self.test)

        # Segunda pregunta
        self.pregunta2 = PreguntaDelTest.objects.create(
            tema=2,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 2',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='B',
            justificacion='Justificación de prueba'
        )
        self.pregunta2.nombre_del_test.add(self.test)

        # Tercera pregunta
        self.pregunta3 = PreguntaDelTest.objects.create(
            tema=3,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 3',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='C',
            justificacion='Justificación de prueba'
        )
        self.pregunta3.nombre_del_test.add(self.test)

        # Cuarta pregunta
        self.pregunta4 = PreguntaDelTest.objects.create(
            tema=1,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 4',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='A',
            justificacion='Justificación de prueba'
        )

        # Le agrego el nombre del test de Test() a esta pregunta con un add()
        self.pregunta4.nombre_del_test.add(self.test)

        # Quinta pregunta
        self.pregunta5 = PreguntaDelTest.objects.create(
            tema=2,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 5',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='B',
            justificacion='Justificación de prueba'
        )
        self.pregunta5.nombre_del_test.add(self.test)

        # Sexta pregunta
        self.pregunta6 = PreguntaDelTest.objects.create(
            tema=3,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 6',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='C',
            justificacion='Justificación de prueba'
        )
        self.pregunta6.nombre_del_test.add(self.test)

        # Séptima pregunta
        self.pregunta7 = PreguntaDelTest.objects.create(
            tema=1,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 7',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='A',
            justificacion='Justificación de prueba'
        )

        # Le agrego el nombre del test de Test() a esta pregunta con un add()
        self.pregunta7.nombre_del_test.add(self.test)

        # Octava pregunta
        self.pregunta8 = PreguntaDelTest.objects.create(
            tema=2,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 8',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='B',
            justificacion='Justificación de prueba'
        )
        self.pregunta8.nombre_del_test.add(self.test)

        # Novena pregunta
        self.pregunta9 = PreguntaDelTest.objects.create(
            tema=3,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 9',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='C',
            justificacion='Justificación de prueba'
        )
        self.pregunta9.nombre_del_test.add(self.test)

        # Décima pregunta
        self.pregunta10 = PreguntaDelTest.objects.create(
            tema=3,
            normativa='Test Normativa',
            pregunta='Pregunta de prueba 10',
            opcion_a='Opción A',
            opcion_b='Opción B',
            opcion_c='Opción C',
            opcion_d='Opción D',
            respuesta_correcta='D',
            justificacion='Justificación de prueba'
        )
        self.pregunta10.nombre_del_test.add(self.test)

    # Este test funciona. Chequea 7 preguntas buenas y 3 malas. Las malas no penaliza.
    def test_case1_wrong_answers_dont_penalize(self):
        # Esto crea la Sesion del Test para la dificultad en donde las respuestas incorrectas no penalizan
        sesion_caso_1 = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="1",
            cliente_entrego_este_test=True
        )

        # Create user answers - 7 correct, 3 wrong
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta6,
            respuesta_seleccionada='C',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta8,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta9,
            respuesta_seleccionada='C',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1,
            pregunta=self.pregunta10,
            respuesta_seleccionada='A',
            es_correcto=False
        )

        # RespuestaDelUsuario.objects.create(
        #     sesion=sesion_caso_1,
        #     pregunta=self.pregunta1,
        #     respuesta_seleccionada='A',
        #     es_correcto=True
        # )
        # RespuestaDelUsuario.objects.create(
        #     sesion=sesion_caso_1,
        #     pregunta=self.pregunta2,
        #     respuesta_seleccionada='B',
        #     es_correcto=True
        # )
        # RespuestaDelUsuario.objects.create(
        #     sesion=sesion_caso_1,
        #     pregunta=self.pregunta3,
        #     respuesta_seleccionada='D',
        #     es_correcto=False
        # )

        # Execute test view
        # Esto hace que el superusuario se autentique / loguee
        self.client.force_login(self.superuser)

        # Llamo a la URL con la vista que me muestra los resultados (resultados_del_test())
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_1.id}/resultados/')

        # Verify score calculation, when there are a total of 3 questions.
        # These assertions verify that your view is:
        #   Calculating scores correctly
        #   Tracking correct/incorrect answers accurately
        #   Displaying the right difficulty level name

        # # Checks if the score is correctly calculated: 2 correct answers out of 3 questions = 66.67%
        # self.assertEqual(response.context['score'], (2/3) * 100)

        # Verifica si la puntuación se calcula correctamente: 7 respuestas correctas de 10 preguntas = 70%
        self.assertEqual(response.context['score'], (7 / 10) * 10)

        # # Verifies that exactly 2 correct answers were counted
        # self.assertEqual(response.context['correct_answers'], 2)

        # Verifica que exactamente 7 respuestas correctas fueron contadas
        self.assertEqual(response.context['correct_answers'], 7)

        # # Verifies that exactly 1 incorrect answer was counted
        # self.assertEqual(response.context['incorrect_answers'], 1)

        # Verifica que exactamente 3 respuestas incorrectas fueron contadas
        self.assertEqual(response.context['incorrect_answers'], 3)

        # Confirms the difficulty level name is correct for difficulty level 1 (where wrong answers don't penalize)
        self.assertEqual(response.context['nombre_de_dificultad'], 'Errores No Restan')

    # Caso 4:1: Este test chequea 6 preguntas buenas y 4 malas. Las malas penalizan (me quita 1 buena).
    def test_case2_penalty_for_wrong_answers(self):
        # Esto crea la Sesion del Test para la dificultad 4:1 (caso 2)
        sesion_caso_2 = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="2",
            limite_de_tiempo=1800,
            # cliente_entrego_este_test=True
        )

        # 6 correct, 4 wrong (4 wrong answers eliminate 1 correct, so final score is 5 correct)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta6,
            respuesta_seleccionada='C',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta8,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta9,
            respuesta_seleccionada='A',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2,
            pregunta=self.pregunta10,
            respuesta_seleccionada='A',
            es_correcto=False
        )

        # Esto hace que el superusuario se autentique. Si no pongo esto, el "self.assertEqual" no funcionará.
        self.client.force_login(self.superuser)

        response = self.client.get(f'/tests/test/sesion/{sesion_caso_2.id}/resultados/')

        self.assertEqual(response.context['correct_answers'], 6)
        self.assertEqual(response.context['incorrect_answers'], 4)
        self.assertEqual(response.context['nombre_de_dificultad'], '4:1 (4 respuestas malas restan 1 buena)')
        self.assertEqual(response.context['score'], (5 / 10) * 10)  # 6 correct - 1 penalty (4 wrong) = 5 correct

        # RespuestaDelUsuario.objects.create(
        #     sesion=sesion_caso_2,
        #     pregunta=self.pregunta1,
        #     respuesta_seleccionada='A',
        #     es_correcto=True
        # )
        # RespuestaDelUsuario.objects.create(sesion=sesion_caso_2, pregunta=self.pregunta2, respuesta_seleccionada='C',
        #                                    es_correcto=False)
        # RespuestaDelUsuario.objects.create(sesion=sesion_caso_2, pregunta=self.pregunta3, respuesta_seleccionada='D',
        #                                    es_correcto=False)
        #
        # response = self.client.get(f'/tests/test/sesion/{sesion_caso_2.id}/resultados/')
        #
        # self.assertEqual(response.context['correct_answers'], 1)
        # self.assertEqual(response.context['incorrect_answers'], 2)
        # self.assertEqual(response.context['nombre_de_dificultad'], '4:1 (4 respuestas malas restan 1 buena)')
        # self.assertEqual(response.context['score'], (1 / 3) * 100)

    # Caso 3:1: este test chequea 7 preguntas buenas y 3 malas. Las malas penalizan (3 malas me quita 1 buena).
    def test_case3_three_wrongs_remove_one_correct(self):
        sesion_caso_3 = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="3",
            limite_de_tiempo=1800
        )

        # 7 correct, 3 wrong (3 wrong answers eliminate 1 correct, so final score is 6 correct)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta6,
            respuesta_seleccionada='C',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta8,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta9,
            respuesta_seleccionada='A',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3,
            pregunta=self.pregunta10,
            respuesta_seleccionada='D',
            es_correcto=True
        )

        self.client.force_login(self.superuser)
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_3.id}/resultados/')

        self.assertEqual(response.context['correct_answers'], 7)
        self.assertEqual(response.context['incorrect_answers'], 3)
        self.assertEqual(response.context['nombre_de_dificultad'], '3:1 (3 respuestas malas restan 1 buena)')
        self.assertEqual(response.context['score'], (6 / 10) * 10)  # 7 correct - 1 penalty (3 wrong) = 6 correct

    # Caso 2:1: este test chequea 7 preguntas buenas y 3 malas. Las malas penalizan (2 malas me quita 1 buena).
    def test_case4_two_wrongs_remove_one_correct(self):
        sesion_caso_4 = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="4",
            limite_de_tiempo=1800
        )

        # 7 correct, 3 wrong (4 wrong answers eliminate 2 correct, so final score is 5 correct)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta6,
            respuesta_seleccionada='C',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta8,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta9,
            respuesta_seleccionada='A',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4,
            pregunta=self.pregunta10,
            respuesta_seleccionada='D',
            es_correcto=True
        )

        self.client.force_login(self.superuser)
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_4.id}/resultados/')

        self.assertEqual(response.context['correct_answers'], 7)
        self.assertEqual(response.context['incorrect_answers'], 3)
        self.assertEqual(response.context['nombre_de_dificultad'], '2:1 (2 respuestas malas restan 1 buena)')

        # 7 correct - 1 penalty (from 2 wrong answers) = 6 correct
        self.assertEqual(response.context['score'], (6 / 10) * 10)

        # # 7 correct - 1.5 penalty (3 wrong / 2) = 5.5 correct
        # self.assertEqual(response.context['score'], (5.5/10) * 10)

    # Caso 1:1: este test chequea 7 preguntas buenas y 3 malas. Una mala me quita 1 buena.
    def test_case5_one_wrong_removes_one_correct(self):
        sesion_caso_5 = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="5",
            limite_de_tiempo=1800
        )

        # 7 correct, 3 wrong (3 wrong answers eliminate 3 correct, so final score is 4 correct)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta6,
            respuesta_seleccionada='C',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta8,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta9,
            respuesta_seleccionada='A',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5,
            pregunta=self.pregunta10,
            respuesta_seleccionada='D',
            es_correcto=True
        )

        self.client.force_login(self.superuser)
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_5.id}/resultados/')

        self.assertEqual(response.context['correct_answers'], 7)
        self.assertEqual(response.context['incorrect_answers'], 3)

        # Tuve que especificar el nombre correcto de la dificultad como un string como lo tengo en el modelo
        self.assertEqual(response.context['nombre_de_dificultad'], '1:1 (1 respuesta mala resta 1 respuesta buena)')
        self.assertEqual(response.context['score'], (4 / 10) * 10)  # 7 correct - 3 penalty (3 wrong) = 4 correct

    # Caso sin penalización, pero con algunas preguntas sin responder
    def test_case1_partial_answers_no_penalty(self):
        sesion_caso_1_parcial = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="1",
            cliente_entrego_este_test=True
        )

        # Only answering 7 questions (5 correct, 2 wrong, 3 unanswered)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1_parcial,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1_parcial,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1_parcial,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1_parcial,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1_parcial,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1_parcial,
            pregunta=self.pregunta6,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_1_parcial,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )

        self.client.force_login(self.superuser)
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_1_parcial.id}/resultados/')

        self.assertEqual(response.context['correct_answers'], 5)
        self.assertEqual(response.context['incorrect_answers'], 2)
        self.assertEqual(response.context['nombre_de_dificultad'], 'Errores No Restan')
        self.assertEqual(response.context['score'], (5 / 10) * 10)  # 5 correct out of total 10 questions = 50%

    # Caso 4:1, pero con algunas preguntas sin responder
    def test_case2_partial_answers_four_wrongs_one_correct_penalty(self):
        sesion_caso_2_parcial = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="2",
            limite_de_tiempo=1800
        )

        # Only answering 8 questions (4 correct, 4 wrong, 2 unanswered)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2_parcial,
            pregunta=self.pregunta1,
            respuesta_seleccionada='B',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2_parcial,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2_parcial,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2_parcial,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2_parcial,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2_parcial,
            pregunta=self.pregunta6,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2_parcial,
            pregunta=self.pregunta7,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_2_parcial,
            pregunta=self.pregunta8,
            respuesta_seleccionada='B',
            es_correcto=False
        )

        self.client.force_login(self.superuser)
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_2_parcial.id}/resultados/')

        # Solo deben haber 4 respuestas correctas
        self.assertEqual(response.context['correct_answers'], 4)

        # Deben haber 4 respuestas incorrectas
        self.assertEqual(response.context['incorrect_answers'], 4)
        self.assertEqual(response.context['nombre_de_dificultad'], '4:1 (4 respuestas malas restan 1 buena)')

        # 4 correct - 1 penalty (4 wrong) = 3 correct out of 10 total
        self.assertEqual(response.context['score'], (3/10) * 10)

    # Caso 3:1, pero con algunas preguntas sin responder
    def test_case3_partial_answers_three_wrongs_one_correct_penalty(self):
        sesion_caso_3_parcial = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="3",
            limite_de_tiempo=1800
        )

        # Only answering 8 questions (5 correct, 3 wrong, 2 unanswered)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3_parcial,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3_parcial,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3_parcial,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3_parcial,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3_parcial,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3_parcial,
            pregunta=self.pregunta6,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3_parcial,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_3_parcial,
            pregunta=self.pregunta8,
            respuesta_seleccionada='D',
            es_correcto=False
        )

        self.client.force_login(self.superuser)
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_3_parcial.id}/resultados/')

        self.assertEqual(response.context['correct_answers'], 5)
        self.assertEqual(response.context['incorrect_answers'], 3)
        self.assertEqual(response.context['nombre_de_dificultad'], '3:1 (3 respuestas malas restan 1 buena)')

        # 5 correct - 1 penalty (3 wrong) = 4 correct out of 10 total
        self.assertEqual(response.context['score'], (4/10) * 10)

    # Caso 2:1, pero con algunas preguntas sin responder
    def test_case4_partial_answers_two_wrongs_one_correct_penalty(self):
        sesion_caso_4_parcial = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="4",
            limite_de_tiempo=1800
        )

        # Only answering 8 questions (5 correct, 3 wrong, 2 unanswered)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4_parcial,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4_parcial,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4_parcial,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4_parcial,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4_parcial,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4_parcial,
            pregunta=self.pregunta6,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4_parcial,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_4_parcial,
            pregunta=self.pregunta8,
            respuesta_seleccionada='D',
            es_correcto=False
        )

        self.client.force_login(self.superuser)
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_4_parcial.id}/resultados/')

        self.assertEqual(response.context['correct_answers'], 5)
        self.assertEqual(response.context['incorrect_answers'], 3)
        self.assertEqual(response.context['nombre_de_dificultad'], '2:1 (2 respuestas malas restan 1 buena)')
        # 5 correct - 1 penalty (3 wrong) = 4 correct out of 10 total
        self.assertEqual(response.context['score'], (4/10) * 10)

    # Caso 1:1, pero con algunas preguntas sin responder
    def test_case5_partial_answers_one_wrong_one_correct_penalty(self):
        sesion_caso_5_parcial = SesionDelTest.objects.create(
            usuario=self.superuser,
            nombre_del_test=self.test,
            nivel_de_dificultad="5",
            limite_de_tiempo=1800
        )

        # Only answering 8 questions (5 correct, 2 wrong, 3 unanswered)
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5_parcial,
            pregunta=self.pregunta1,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5_parcial,
            pregunta=self.pregunta2,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5_parcial,
            pregunta=self.pregunta3,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5_parcial,
            pregunta=self.pregunta4,
            respuesta_seleccionada='A',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5_parcial,
            pregunta=self.pregunta5,
            respuesta_seleccionada='B',
            es_correcto=True
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5_parcial,
            pregunta=self.pregunta6,
            respuesta_seleccionada='D',
            es_correcto=False
        )
        RespuestaDelUsuario.objects.create(
            sesion=sesion_caso_5_parcial,
            pregunta=self.pregunta7,
            respuesta_seleccionada='A',
            es_correcto=True
        )

        self.client.force_login(self.superuser)
        response = self.client.get(f'/tests/test/sesion/{sesion_caso_5_parcial.id}/resultados/')

        self.assertEqual(response.context['correct_answers'], 5)
        self.assertEqual(response.context['incorrect_answers'], 2)
        self.assertEqual(response.context['nombre_de_dificultad'], '1:1 (1 respuesta mala resta 1 respuesta buena)')
        # 5 correct - 2 penalty (2 wrong) = 3 correct out of 10 total
        self.assertEqual(response.context['score'], (3/10) * 10)
