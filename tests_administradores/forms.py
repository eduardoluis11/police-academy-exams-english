from django import forms

# Esto me deja importar ModelForm, el cual me deja crear formularios basados en mis modelos de Django
from django.forms import ModelForm

# Esto importa mis modelos
from .models import PreguntaDelTest, Test

# Esto me deja crear Formsets
from django.forms import modelformset_factory, inlineformset_factory


""" Formularios de Django para la app de tests para administradores.

# Form for File Upload
Create a form to handle the Excel file upload.

Why: Validates file type and size before processing, enhancing security and usability.

Best Practices: Limits file size to prevent abuse and restricts to .xlsx for consistency.

"""


class SubirExcelConTestsFormulario(forms.Form):
    excel_file = forms.FileField(
        label='Sube un Archivo de Excel',
        help_text='Solo se aceptan archivos del tipo .xlsx',
        widget=forms.FileInput(attrs={'accept': '.xlsx'})
    )

    # Esto valida el archivo subido para que el usuario no suba malware
    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']

        # Solo se pueden subir archivos Excel del tipo xlsx
        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError("Only .xlsx files are allowed.")

        # Limitar el tamaño del archivo a 5MB
        if file.size > 5 * 1024 * 1024:  # 5MB limit
            raise forms.ValidationError("File size must be under 5MB.")
        return file


""" Campo para Introducir el Nombre del Test.

Lo sacare del modelo de Test usando la biblioteca de ModelForm de Django.

También meteré el año del Test para que el administrador pueda escribirlo. Si el administrador quiere meter exámenes 
viejos (ej: del 2022) de manera manual, creo que el administrador debe poder hacerlo.
"""


class NombreDelTestFormulario(forms.ModelForm):

    # Esto coge los campos del modelo de Test(), y los mete en este formulario
    class Meta:
        model = Test
        fields = ['nombre_del_test', 'year']    # Aqui le digo que solo quiero el campo "nombre del test" y el año

        # Optional: Add widgets, Bootstrap styles, labels, or help_text
        widgets = {
            'nombre_del_test': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }


""" Formulario para Crear un Nuevo Test Manualmente sin Subir un Archivo de Excel.

Necesito poner casi todos los campos del modelo de Preguntas del Test, y necesito el campo "nombre del test" del
modelo de Test.

You can use Django's ModelForm to automatically create a form based on your model. This is more efficient than creating 
a regular Form with manual fields.

This ModelForm automatically:  
- Creates form fields based on your model fields
- Inherits validation from model field definitions
- Handles model instance creation/updates

Cuando uso el ModelForm, debo usar "forms.ModelForm" en lugar de "forms.Form".

El nombre del test quiero que el usuario lo escriba en un campo de texto tipo CharField. No quiero que el usuario lo 
seleccione de una lista desplegable de la lista de tests existentes.

Ahora que lo pienso:  solo hay 4 posibles respuestas para todos los examenes: a, b, c, y d. Entonces, en el formulario 
de crear un nuevo test, voy a crear una lista de python y un dropdown menu para que, para escribir la respuesta, solo 
tengas que escoger entre 4 letras desde un dropdown menu. Asi, te evitaras un monton de errores, y la web app sera mas 
facil de usar.

Key changes:
1) Added OPCIONES_RESPUESTA list with the four possible answers.
2) Created a custom ChoiceField for respuesta_correcta.
3) Removed respuesta_correcta from the widgets dictionary since it's now defined separately.

Al crear un test, cuando seleccionas la respuesta correcta, solo puedes seleccionar la respuesta correcta desde un 
dropdown menu.
"""


class CrearTestSinExcelFormulario(forms.ModelForm):

    # Opciones para el menu desplegable para el campo "respuesta correcta"
    OPCIONES_RESPUESTA = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    # Override the respuesta_correcta field
    respuesta_correcta = forms.ChoiceField(
        choices=OPCIONES_RESPUESTA,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Esto mete los Campos del modelo de PreguntaDelTest() a este formulario
    class Meta:
        model = PreguntaDelTest
        fields = ['tema', 'normativa', 'pregunta',
                  'opcion_a', 'opcion_b', 'opcion_c', 'opcion_d',
                  'respuesta_correcta', 'justificacion']

        # Optional: Add widgets, labels, or help_text.
        # Con esto, puedo agrega la clase de form-control de Bootstrap a los campos del formulario
        widgets = {
            'tema': forms.NumberInput(attrs={'class': 'form-control'}),
            'normativa': forms.TextInput(attrs={'class': 'form-control'}),
            'pregunta': forms.Textarea(attrs={'class': 'form-control'}),
            'opcion_a': forms.Textarea(attrs={'class': 'form-control'}),
            'opcion_b': forms.Textarea(attrs={'class': 'form-control'}),
            'opcion_c': forms.Textarea(attrs={'class': 'form-control'}),
            'opcion_d': forms.Textarea(attrs={'class': 'form-control'}),

            # La respuesta correcta la elimine de aqui y la defini como un ChoiceField arriba
            # 'respuesta_correcta': forms.TextInput(attrs={'class': 'form-control'}),
            'justificacion': forms.Textarea(attrs={'class': 'form-control'})
        }


""" Formset para Crear Varias Preguntas de un Test Manualmente sin Subir un Archivo de Excel.

I want to create a formset for my CrearTestSinExcelFormulario django form. That way, the user will be able to assign 
multiple questions to the same isntance of the Test model. Give me an algorithm on how to create the formset in my 
forms.py, then tell me how to add it in my django view for creating new exams. Then, tell me how to render the formset 
into my template, and put a javascript button to be able to add new questions with a new formset. 

El campo "extra" me agrega preguntas adicionales a mi formset. Yo quiero que mi formset empiece con una sola pregunta,
por lo que dejaré el "extra" como "0".

Now, in my "crear nuevo test" template, I have an input to delete formsets with the ID "id="id_preguntas-0-DELETE"". However, I never wrote such code in the HTML of my template. Where does that "DELETE" input come from? From the "can_delete=True" attribute from my formset from my forms.py file?


Yes, that's correct. The `can_delete=True` parameter in your formset automatically adds a `DELETE` checkbox field to each form in the formset. 

When you use `{{ form.as_p }}` in your template, Django automatically renders all fields, including this hidden `DELETE` checkbox. The naming convention follows Django's formset pattern:

- `id_preguntas`: Your formset prefix
- `0`: The form index
- `DELETE`: The delete field name

This is part of Django's built-in formset functionality. When a form is submitted with this checkbox checked, Django's formset processing will mark that instance for deletion when you call `formset.save()`.

In your view, you're already handling these deletions with:

```python
# Handle deleted forms
for obj in formset.deleted_objects:
    obj.delete()
```

You can control the visibility and styling of this delete checkbox by explicitly rendering it in your template or by customizing it with CSS.
"""


# Create a formset for multiple questions
CrearPreguntaDelTestFormSet = modelformset_factory(
    PreguntaDelTest,
    form=CrearTestSinExcelFormulario,   # The form class used for each form in the formset.
    extra=0,    # Start with 0 extra forms
    can_delete=True,    # Esto genera la Casilla "eliminar" de mis formsets
    min_num=1,  # Ensures at least one form is required.
    validate_min=True   # Validates that the minimum number of forms is met.
)


""" Formulario para el Buscador para buscar una pregunta en específico de algún test.

## Algorithm Overview
View: Create a view that handles the search request and queries the database for matching questions.

Form: Use a simple form to capture the search query from the front-end.

Query: Search the PreguntasDelTest model by matching the query against the question text and the related test name.

Template: Display a search bar and render the results in a list or table.

Security: Restrict access to admins only.

Best Practices: Add pagination for large result sets, provide feedback, and handle edge cases (e.g., no results).

We’ll create a simple form to capture the search query.

Why: A form ensures proper validation and rendering of the search bar.

Best Practice: The required=False allows empty searches (which can show all questions), and the placeholder improves UX.
"""


class BuscadorDePreguntasFormulario(forms.Form):
    consulta = forms.CharField(
        label='Buscar pregunta',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Introduce una pregunta o el nombre de un test'})
    )
