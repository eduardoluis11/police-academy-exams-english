from django import forms

from tests_administradores.models import Test, PreguntaDelTest

from django.core.exceptions import ValidationError

""" Formularios de Django para la app de Test de Clientes.
"""

""" Formulario para Configurar un Test Predefinido o Pre-Hecho.

Make sure to keep your JavaScript for showing/hiding the question sections based on the radio button selection. The 
form will now handle validation and cleaning of the data automatically, and it's more maintainable since the form logic 
is centralized in the forms.py file.  

The key differences are:  
    Form logic is now in a dedicated Django form class.
    Form validation is handled automatically.
    The view is simplified and uses form.cleaned_data.
    The template uses Django's form rendering.
    Field choices are defined once in the form class.

You'll need to adapt any custom JavaScript to work with the new form IDs, but the functionality should remain the same.

I'll add a custom time field that allows users to input their own time in minutes and seconds. We'll use a combination 
of two number fields for this purpose.

Changes made:  
1)Added Personalizado (0) option to TIME_CHOICES.

2) Added two new fields:
    custom_minutes: For minutes (0-180).
    custom_seconds: For seconds (0-59).
    
3) Added form validation in clean() method that:
    Checks if custom time is selected.
    Validates the minutes and seconds values.
    Calculates total seconds.
    Raises errors for invalid values.

You'll need to add JavaScript to your template to show/hide the custom time fields based on the time_limit selection. 

The clean() method stores the custom time in cleaned_data['total_seconds'].

I'll help you add a field to display the number of questions in the form. Since this is read-only information coming 
from the view, we can add a non-editable field to the form class.

Tuve que quitar los segundos del tiempo customizado, ya que no los voy a usar.

Agregaré una opción adicional para que el usuario tenga tiempo infinito para hacer el test.
"""


class ConfigurarTestSinIncluirPreguntasForm(forms.Form):
    # Difficulty level choices
    DIFFICULTY_CHOICES = [
        ('1', 'Errores No Restan'),
        ('2', '4:1 (4 respuestas malas restan 1 buena)'),
        ('3', '3:1 (3 respuestas malas restan 1 buena)'),
        ('4', '2:1 (2 respuestas malas restan 1 buena)'),
        ('5', '1:1 (1 respuesta mala resta 1 respuesta buena)'),
    ]

    # Time limit choices (in seconds)
    TIME_CHOICES = [
        (600, '10 minutos'),
        (1800, '30 minutos'),
        (3600, '1 hora'),
        (7200, '2 horas'),
        ('ilimitado', 'Tiempo Ilimitado'),  # Added unlimited time option
        (0, 'Customizado'),  # Added custom option

    ]

    # Form fields
    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        label='Nivel de Dificultad',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='El nivel de dificultad determina cómo se calculará tu puntuación final.'
    )

    # Límite de Tiempo. Esto es para que el cliente pueda elegir cuánto tiempo quiere tener para hacer el test.
    time_limit = forms.ChoiceField(
        choices=TIME_CHOICES,
        label='Tiempo Límite',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Selecciona cuánto tiempo tendrás para completar el test.'
    )

    # Si el cliente selecciona la opción "Customizado", entonces se le mostrarán los campos para que escriba el tiempo.
    # Minutos customizados para el test
    custom_minutes = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=180,
        label='Minutos',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minutos',
            # 'style': 'display: none;' # ELIMINAR, ya que el input ya se hace visible e invisible usando JS
        })
    )

    # # Segundos customizados para el test
    # custom_seconds = forms.IntegerField(
    #     required=False,
    #     min_value=0,
    #     max_value=59,
    #     label='Segundos',
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control',
    #         'placeholder': 'Segundos',
    #         # 'style': 'display: none;' # ELIMINAR, ya que el input ya se hace visible e invisible usando JS
    #     })
    # )

    autocorrect = forms.ChoiceField(
        choices=[('false', 'No'), ('true', 'Sí')],
        label='Autocorrección',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='¿Deseas que el test se autocorrija a penas selecciones una respuesta?'
    )

    # Campo que renderiza el número total de Preguntas Disponibles (solo lectura)
    # numero_de_preguntas = forms.IntegerField(
    preguntas_disponibles = forms.IntegerField(
        required=False,
        label='Preguntas Disponibles',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',  # Esto solo renderiza las preguntas disponibles, por lo que no se debe editar
            'style': 'background-color: #e9ecef;'  # Gray background to indicate read-only
        }),
        help_text='Número total de preguntas disponibles en este test.'
    )

    # Esto devuelve el tiempo customizado en minutos validado
    def clean(self):
        cleaned_data = super().clean()
        time_limit = cleaned_data.get('time_limit')

        if time_limit == '0':  # Custom time selected
            minutes = cleaned_data.get('custom_minutes', 0) or 0
            seconds = 0
            # seconds = cleaned_data.get('custom_seconds', 0) or 0

            if minutes == 0 and seconds == 0:
                raise forms.ValidationError('Debes especificar un tiempo personalizado válido')

            # if seconds >= 60:
            #     raise forms.ValidationError('Los segundos deben ser menores a 60')

            # Esto convierte el tiempo customizado de minutos y segundos a segundos totales, y lo envia al POST
            cleaned_data['custom_time_limit'] = (minutes * 60)

        return cleaned_data

    # question_mode = forms.ChoiceField(
    #     choices=[('default', 'Usar preguntas predeterminadas'),
    #              ('custom', 'Seleccionar preguntas personalizadas')],
    #     widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    #     initial='default',
    #     label='Modo de Selección de Preguntas'
    # )
    #
    # selected_questions = forms.MultipleChoiceField(
    #     required=False,
    #     widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    #     label='Preguntas Personalizadas'
    # )
    #
    # def __init__(self, *args, **kwargs):
    #     available_questions = kwargs.pop('available_questions', None)
    #     super(ConfigurarTestSinIncluirPreguntasForm, self).__init__(*args, **kwargs)
    #
    #     if available_questions:
    #         # Create choices from available questions
    #         self.fields['selected_questions'].choices = [
    #             (q.id, q.pregunta[:80] + '...' if len(q.pregunta) > 80 else q.pregunta)
    #             for q in available_questions
    #         ]


""" Formulario para Configurar un Nuevo Test que se va a Generar desde Cero.

Voy a introducir 2 formularios de Django en el view de Configurar un Nuevo Test a Generar: el formulario que ya 
creé para configurar un test predefinido, y otro formulario que va a permitir al cliente seleccionar unos nuevos 
campos, como por ejemplo, si el test es por tema, o por normativa. Los tests por año son todos pre-definidos,
por lo que NO se van a generar tests por año usando este formulario.

Puedo poner una opción adicional que me diga que quiero un test con preguntas completamente aleatorias, sin seleccionar
ni por tema, ni por normativa.

I'll help you add dynamic fields to the form based on the test type selection. Here's how to modify the form:

Now add this JavaScript to your template (configurar_nuevo_test_a_generar.html):

This solution:

1. Creates dropdown fields for tema, año, and normativa
2. Populates año and normativa choices dynamically from the Test model
3. Includes client-side validation
4. Uses JavaScript to show/hide fields based on the selected test type
5. Maintains Bootstrap styling and form control classes

The fields will:
- Show "Tema 1" through "Tema 40" for tema selection
- Show all unique years from the Test model for año selection
- Show all unique normativas from the Test model for normativa selection
- Hide irrelevant fields based on the selection
- Include proper validation on both client and server side

Remember to:
1. Update your view to handle these new form fields
2. Add corresponding fields to your model if needed
3. Test the form validation with different selections

Now, generate me an integer field in which the user will be able to type the number of questions that he wants for his 
exam. The field should be called "numero de preguntas". The user should be able to type any integer into that field, as 
long as it's less than or equal to the number of records of the PreguntaDelTest() field for that category. For 
instance, if the user chooses that he wants tests by year, and there are only 2 records of PreguntaDelTest matching 
that year, then there are only 2 exam questions for that year. Therefore, the user should not be able to type any 
integer higher than 2 in that specific case.

This modification:  
    Adds a new IntegerField for number of questions.
    Validates the number against available questions based on the test type.
    Shows an error if the user requests more questions than available.
    Uses different filters based on the selected test type.
    Handles the random case by checking against all questions.

The validation occurs after the test type and specific selection (tema/año/normativa) are validated, ensuring we check 
against the correct subset of questions.

I realized that I have a problem: that each time that I select an exam type ("year", "tema", or "normativa"), there 
will be a pre-selected topic ("tema 1"), or a pre-selected "normativa" ("Constitucion Española"), or a pre-selected 
year (e.g.: "2023"). Well, when that first instance of the first record of my PreguntaDelTest() is rendered on my 
template, if the user wants to select the first year that pops up (e.g: "2023"), nothing will be rendered in the div 
that will render the number of questions available for the year 2023. There's no way for my JS function to know which 
pre-selected option showed up when the user selects "year" in the dropdown menu for the exam type. So, to simplify 
things and prevent bugs in the future, I have an idea: once the user selects the exam type, for instance 
"exam by year", the "year" field will be NULL by default (e.g: "------"). That way, the user will be forced to click on 
the "year" dropdown menu to change the year. This will trigger the onChange() event listener for the "year" dropdown 
menu, and will execute the JS function that will call the API to render the number of questions for the selected year. 
The same goes for the topic or the "normativa" of the exam: they should be NULL or None by default ("e.g.: -----"). 
So, please tell me how to modify my django form so that the default options for the "tema", "year", and "normativa" 
fields are NULL or None or "------".

Here's how to modify your form fields to include a blank default option:

The changes:
1. Added a blank option `('', '------')` as the first choice for each field
2. In `__init__`, prepend the blank option before adding the database values
3. Added `data-url` and `onchange` attributes for the JavaScript function

This ensures that users must actively select an option to trigger the `onChange` event.

Le agregué el event listener con la función de JavaScript que se activa con el onChange() en los 3 campos de tipos de 
test (“seleccionar el año”, “seleccionar la normativa”, y “seleccionar el tema”).

El número de preguntas NO debe ser de solo lectura. Debes poder escribir manualmente el número de preguntas que quieres
en el campo de "numero de preguntas". 

Now, in my forms.py file, this snippet renders 40 topics or "temas". Well, I want to modify this so that the number of 
topics printed is equal to the number of topics which have at least 1 exam question assigned to them. I don't have 
questions for each of the 40 topics. My qeustions are stored in the PreguntaDelTest() model. Each question has a field 
called "tema" (topic). Well, in this django form, make a query set to fetch all of the questions from 
PreguntaDelTest(). Then, look at the values stored in their "tema" field. Look at all the distinct "temas" or topics 
that can be found within my exam questions. Then render those distinct topics here in this snippet for this django form.

To only render the topics or "temas" that have a question assigned to them:
    Dynamic Topic List: Instead of a hard-coded list of 40 topics, the form now queries the database to find only 
    topics that have actual questions
    
    Database Query: PreguntaDelTest.objects.values_list('tema', flat=True).distinct().order_by('tema') gets all unique 
    topic numbers from questions
    
    Filtering: if tema is not None ensures we don't include any null topic values
    
    Ordering: Topics are ordered numerically for a clean presentation

This approach ensures your form only shows relevant topics that users can actually select for their exams, making the 
interface more intuitive and efficient.
"""


class ConfigurarNuevoTestAGenerarForm(forms.Form):
    # Lista de Python con los Tipos de Test
    TIPO_DE_TEST = [
        ('', '------'),  # Add blank default option
        ('tema', 'Por Tema'),
        # ('año', 'Por Examen (Por Año)'),
        ('normativa', 'Por Normativa'),
        # ('aleatorio', 'Aleatorio'),
    ]

    # # Lista de los 40 temas
    # TEMAS = [(str(i), f'Tema {i}') for i in range(1, 41)]

    # Esto es para que el cliente seleccione el tipo de test que quiere generar
    tipo_de_test = forms.ChoiceField(
        choices=TIPO_DE_TEST,
        label='Tipo de Test',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'tipo_de_test'  # Added ID for JavaScript
        }),
        help_text='Selecciona el tipo de test que deseas generar.'
    )

    # Campo para seleccionar el tema (inicialmente oculto).
    # Replace the existing tema ChoiceField with a MultipleChoiceField.
    tema = forms.MultipleChoiceField(
        choices=[],  # Empty initially, will populate in __init__
        # choices=TEMAS,
        # choices=[('', '------')] + TEMAS,  # Add blank option as first choice
        label='Tema',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tema-checkbox',
            'data-url': '/tests/get-question-count/',
        }),

        # widget=forms.Select(attrs={
        #     'class': 'form-control tema-field',
        #     'onchange': 'updateQuestionCount(this)',
        #     'data-url': '/tests/get-question-count/',  # Esto lo necesita la función JS con la API
        #
        #     # 'style': 'display: none;'
        # }),
        required=False,
        help_text='Selecciona uno o más temas para tu examen'
    )

    # # Campo para seleccionar el año (inicialmente oculto)
    # year = forms.ChoiceField(
    #     # choices=[],  # Will be populated in __init__
    #     choices=[('', '------')],  # Start with blank option, rest populated in __init__
    #     label='Año del Examen',
    #     widget=forms.Select(attrs={
    #         'class': 'form-control year-field',
    #         'onchange': 'updateQuestionCount(this)',
    #         'data-url': '/tests/get-question-count/',  # Esto lo necesita la función JS con la API
    #         # 'style': 'display: none;'
    #     }),
    #     required=False
    # )

    # Campo para seleccionar la normativa (inicialmente oculto)
    # Replace the existing tema ChoiceField with a MultipleChoiceField.
    normativa = forms.MultipleChoiceField(
        choices=[],  # Empty initially, will populate in __init__
        label='Normativa',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'normativa-checkbox',
            'data-url': '/tests/get-question-count/',
        }),
        required=False,
        help_text='Selecciona una o más normativas para tu examen'
    )

    # normativa = forms.ChoiceField(
    #     # choices=[],  # Will be populated in __init__
    #     choices=[('', '------')],  # Start with blank option, rest populated in __init__
    #     label='Normativa',
    #     widget=forms.Select(attrs={
    #         'class': 'form-control normativa-field',
    #         'onchange': 'updateQuestionCount(this)',
    #         'data-url': '/tests/get-question-count/',  # Esto lo necesita la función JS con la API
    #         # 'style': 'display: none;'
    #     }),
    #     required=False
    # )

    # Campo para que el Usuario inserte cuantas Preguntas quiere para el test
    numero_de_preguntas = forms.IntegerField(
        label='Número de Preguntas',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de preguntas'
        }),
        help_text='Indica cuántas preguntas deseas que tenga el test'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # # Año.
        # # Get unique years from the PreguntaDelTest() model
        # years = PreguntaDelTest.objects.values_list('year', flat=True).distinct().order_by('-year')

        # # Necesito que los años sean integers, no strings.
        # # Add years after the blank option.
        # self.fields['year'].choices = [('', '------')] + [(int(year), int(year)) for year in years if year]
        # # self.fields['year'].choices = [(int(year), int(year)) for year in years if year]

        # Esto cogerá los temas de PreguntaDelTest(), y los meterá al campo de "tema" de este formulario.
        # Get distinct tema values from PreguntaDelTest that have questions
        temas_with_questions = PreguntaDelTest.objects.values_list('tema', flat=True).distinct().order_by('tema')

        # Convert to list of tuples for choices, filtering out None values
        tema_choices = [(str(tema), f'Tema {tema}') for tema in temas_with_questions if tema is not None]

        # Assign to field choices
        self.fields['tema'].choices = tema_choices
        # Fin del snippet que renderiza los temas para el campo de "tema"

        # Normativa.
        # Esto cogerá las normativas de PreguntaDelTest(), y las meterá al campo de "normativa" de este formulario.
        # Get distinct normativa values from PreguntaDelTest that have questions
        normativas_de_las_preguntas_de_la_base_de_datos = PreguntaDelTest.objects.values_list('normativa', flat=True).distinct().order_by('normativa')

        # Convert to list of tuples for choices, filtering out None values
        opciones_de_normativas = [(str(normativa), f'{normativa}') for normativa in normativas_de_las_preguntas_de_la_base_de_datos if normativa is not None]

        # Assign to field choices
        self.fields['normativa'].choices = opciones_de_normativas
        # Fin del snippet que renderiza los normativas para el campo de "normativa"

        # # Get unique normativas from the PreguntaDelTest() model
        # normativas = PreguntaDelTest.objects.values_list('normativa', flat=True).distinct().order_by('normativa')
        # # self.fields['normativa'].choices = [(norm, norm) for norm in normativas if norm]
        #
        # # Add normativas after the blank option
        # self.fields['normativa'].choices = [('', '------')] + [(norm, norm) for norm in normativas if norm]

    def clean(self):
        cleaned_data = super().clean()
        tipo_test = cleaned_data.get('tipo_de_test')
        numero_preguntas = cleaned_data.get('numero_de_preguntas')

        if not numero_preguntas:
            return cleaned_data

        # Validate required fields based on test type
        if tipo_test == 'tema' and not cleaned_data.get('tema'):
            raise forms.ValidationError('Debes seleccionar un tema.')
        # elif tipo_test == 'año' and not cleaned_data.get('year'):
        #     raise forms.ValidationError('Debes seleccionar un año.')
        elif tipo_test == 'normativa' and not cleaned_data.get('normativa'):
            raise forms.ValidationError('Debes seleccionar una normativa.')

        else:  # aleatorio
            available_questions = PreguntaDelTest.objects.all().count()

        if numero_preguntas > available_questions:
            raise ValidationError(
                f'Solo hay {available_questions} preguntas disponibles para esta selección. '
                f'Por favor, elige un número menor o igual.'
            )

        return cleaned_data


""" Formulario para Configurar un Nuevo Test por Tema que se va a Generar desde Cero.
"""


class ConfigureNewTestByTopicForm(forms.Form):

    # Campo para seleccionar el tema (inicialmente oculto).
    # Replace the existing tema ChoiceField with a MultipleChoiceField.
    tema = forms.MultipleChoiceField(
        choices=[],  # Empty initially, will populate in __init__
        label='Tema',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tema-checkbox',
            'data-url': '/tests/get-question-count/',
        }),

        # widget=forms.Select(attrs={
        #     'class': 'form-control tema-field',
        #     'onchange': 'updateQuestionCount(this)',
        #     'data-url': '/tests/get-question-count/',  # Esto lo necesita la función JS con la API
        #
        #     # 'style': 'display: none;'
        # }),
        required=False,
        help_text='Selecciona uno o más temas para tu examen'
    )

    # Campo para que el Usuario inserte cuantas Preguntas quiere para el test
    numero_de_preguntas = forms.IntegerField(
        label='Número de Preguntas',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de preguntas'
        }),
        help_text='Indica cuántas preguntas deseas que tenga el test'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Esto cogerá los temas de PreguntaDelTest(), y los meterá al campo de "tema" de este formulario.
        # Get distinct tema values from PreguntaDelTest that have questions
        temas_with_questions = PreguntaDelTest.objects.values_list('tema', flat=True).distinct().order_by('tema')

        # Convert to list of tuples for choices, filtering out None values
        tema_choices = [(str(tema), f'Tema {tema}') for tema in temas_with_questions if tema is not None]

        # Assign to field choices
        self.fields['tema'].choices = tema_choices
        # Fin del snippet que renderiza los temas para el campo de "tema"

    def clean(self):
        cleaned_data = super().clean()
        numero_preguntas = cleaned_data.get('numero_de_preguntas')

        if not numero_preguntas:
            return cleaned_data

        # Validate required fields based on test type
        # if tipo_test == 'tema' and not cleaned_data.get('tema'):
        if not cleaned_data.get('tema'):
            raise forms.ValidationError('Debes seleccionar un tema.')

        # else:  # aleatorio
        #     available_questions = PreguntaDelTest.objects.all().count()

        available_questions = PreguntaDelTest.objects.all().count()

        if numero_preguntas > available_questions:
            raise ValidationError(
                f'Solo hay {available_questions} preguntas disponibles para esta selección. '
                f'Por favor, elige un número menor o igual.'
            )

        return cleaned_data


""" Formulario para Configurar un Nuevo Test por Normativa.

Este formulario es muy similar al formulario para configurar un nuevo test por Tema.
"""


class ConfigureNewTestByRegulationForm(forms.Form):

    # Campo para seleccionar el tema (inicialmente oculto).
    # Replace the existing tema ChoiceField with a MultipleChoiceField.
    normativa = forms.MultipleChoiceField(
        choices=[],  # Empty initially, will populate in __init__
        label='Normativa',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'normativa-checkbox',
            'data-url': '/tests/get-question-count/',
        }),

        # widget=forms.Select(attrs={
        #     'class': 'form-control tema-field',
        #     'onchange': 'updateQuestionCount(this)',
        #     'data-url': '/tests/get-question-count/',  # Esto lo necesita la función JS con la API
        #
        #     # 'style': 'display: none;'
        # }),
        required=False,
        help_text='Selecciona una o más normativas para tu examen'
    )

    # Campo para que el Usuario inserte cuantas Preguntas quiere para el test
    numero_de_preguntas = forms.IntegerField(
        label='Número de Preguntas',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de preguntas'
        }),
        help_text='Indica cuántas preguntas deseas que tenga el test'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Esto cogerá las normativas de PreguntaDelTest(), y los meterá al campo de "normativa" de este formulario.
        # Get distinct regulation values from PreguntaDelTest that have questions
        regulations_with_questions = PreguntaDelTest.objects.values_list('normativa', flat=True).distinct().order_by('normativa')

        # Convert to list of tuples for choices, filtering out None values
        regulation_choices = [(str(normativa), f'Normativa {normativa}') for normativa in regulations_with_questions if normativa is not None]

        # Assign to field choices
        self.fields['normativa'].choices = regulation_choices
        # Fin del snippet que renderiza los temas para el campo de "tema"

    def clean(self):
        cleaned_data = super().clean()
        numero_preguntas = cleaned_data.get('numero_de_preguntas')

        if not numero_preguntas:
            return cleaned_data

        # Validate required fields based on test type
        # if tipo_test == 'tema' and not cleaned_data.get('tema'):
        if not cleaned_data.get('normativa'):
            raise forms.ValidationError('Debes seleccionar una normativa.')

        # else:  # aleatorio
        #     available_questions = PreguntaDelTest.objects.all().count()

        available_questions = PreguntaDelTest.objects.all().count()

        if numero_preguntas > available_questions:
            raise ValidationError(
                f'Solo hay {available_questions} preguntas disponibles para esta selección. '
                f'Por favor, elige un número menor o igual.'
            )

        return cleaned_data


""" Formulario de un solo campo para que el cliente pueda escribir el Numero de Preguntas que quiere tomar en el test.

En principio, solo usaré esto para configurar un test por Año. Luego, si me da tiempo, voy a optimizar la vista
para configurar un Test por Normativa o por Tema para que también use este formulario de 1 solo campo.
"""


class NumeroDePreguntasARealizarFormulario(forms.Form):
    # Esto es para que el cliente escriba el número de preguntas que quiere para el test
    numero_de_preguntas_a_realizar = forms.IntegerField(
        label='Número de Preguntas',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de preguntas'
        }),
        help_text='Indica cuántas preguntas deseas que tenga el test'
    )
