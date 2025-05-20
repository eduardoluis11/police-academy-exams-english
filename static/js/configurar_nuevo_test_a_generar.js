/* Código JavaScript para el Template de Configurar un Nuevo Test a Generar.
* */

/* Esto muestra el campo para seleccionar el número del tema si seleccionas "tema" como tipo de test, el año
si seleccionas "año" como tipo de test, y la normativa si seleccionas "normativa" como tipo de test al Configurar
el Nuevo Test a Generar.

This script is used to toggle the visibility of fields in a form based on the selected test type.

Create a new case in this Javascript function for "aleatorio". If the case is "aleatorio", make the fetch() call to my
Django API that fetches the records of the PreguntaDelTest() model from the get_question() view. Then, render that
number of question within a div in my template, just like you're rendering the number of questions for the selected
"tema", or the selected "year", or the selected "normativa".

Here's how to modify the JavaScript code to handle the "aleatorio" case:
1. Add a new case for "aleatorio"
2. Make an API call with `tipo_test=aleatorio` when random is selected
3. Update the help text and max value for the number input
4. Use the same endpoint as other question types

The existing `get_question_count` view already handles the "aleatorio" case by returning the total count of all
questions.

Para arreglar el menú desplegable de normativa ahora que puse los temas como checkboxes:
    Uses multiple methods to find the form fields (to ensure they're found)
    Scans all p elements for text content that matches the labels
    Hides both tema and normativa fields on page load
    Shows only the relevant field when a test type is selected
    Includes robust event listeners for checkboxes and the normativa select
    Adds extensive console logging to track what's happening
    This should resolve both issues by correctly hiding fields and properly updating the question count.

Primero, voy a agarrar el div que contenga a los campos de "Tema", y el div que contenga al campo de "Normativa". Ambos
campos (ambos divs) estarán escondidos por defecto. Luego, cuando el usuario seleccione el tipo de test, se le debe
mostrar el campo de "Tema" o el campo de "Normativa" dependiendo del tipo de test que haya seleccionado.
* */
document.addEventListener('DOMContentLoaded', function() {
    const tipoTestSelect = document.getElementById('tipo_de_test');

    // Direct targeting of the form fields using their label text
    // const temaParent = document.querySelector('label:contains("Tema:")').closest('p');
    // const temaParent = document.querySelector('label[for="id_tema"]').closest('p');
    // const normativaParent = document.querySelector('label[for="id_normativa"]').closest('p');

    // Esto coge el div que contiene a todo el campo de "normativa" del Formulario de Configurar un Nuevo Test a Generar
    const normativaField = document.getElementById('normativa-container');

    // // Esto coge el campo de "tema" y lo guarda en la variable "temaField"
    // const temaField = document.querySelector('.tema-checkbox');

    // Esto coge el div que contiene el campo de "tema"
    const temaField = document.getElementById('tema-container');

    // I need to find the tema parent element somehow
    // let temaParent = null;

    // // Dejame ver si con esto puedo encontrar el elemento padre del campo de "tema". Esto agarra a "<form>".
    // const temaParent = document.querySelector('.tema-checkbox').parentNode;
    // const temaField = document.querySelector('.tema-checkbox').parentNode;

    // Find elements by their labels to be more reliable
    // const temaFieldset = document.getElementById('id_tema').closest('p');
    // const normativaFieldset = document.getElementById('id_normativa').closest('p');

    // console.log("Tema fieldset:", temaFieldset);
    // console.log("Normativa fieldset:", normativaFieldset);


    // Fix the first bug: using correct selectors to find the parent elements.
    // Find the form groups containing our fields.
    // const temaField = document.querySelector('.tema-checkbox').closest('.form-group');
    // const normativaField = document.querySelector('select.normativa-field').closest('.form-group');

    // Hide both fields initially
    // if (temaField) temaField.style.display = 'none';
    // if (normativaFieldset) normativaFieldset.style.display = 'none';
    // if (normativaField) normativaField.style.display = 'none';


    // const temaField = document.querySelector('.tema-field').parentNode;
    // const yearField = document.querySelector('.year-field').parentNode;

    // const normativaField = document.querySelector('.normativa-field').parentNode;

    // Fallback selectors if the above selectors don't work
    // if (!temaParent) {
    //     console.log("Trying alternate tema selector");
    //     const temaDiv = document.getElementById('id_tema');
    //     if (temaDiv) {
    //         temaParent = temaDiv.closest('p');
    //     }
    // }

    // if (!normativaField) {
    //     console.log("Trying alternate normativa selector");
    //     const normativaSelect = document.querySelector('.normativa-field');
    //     if (normativaSelect) {
    //         normativaField = normativaSelect.closest('p');
    //     }
    // }



    // Esto debe esconder la normativa al entrar a la página de Configurar un Nuevo Test a Generar
    normativaField.style.display = 'none';

    // Esto oculta el campo de "tema" al entrar a la página de Configurar un Nuevo Test a Generar
    temaField.style.display = 'none';

    // BUG: esto me termina ocultando TODO el formulario.
    // // Esto debe esconder el tema al entrar a la página de Configurar un Nuevo Test a Generar
    // temaParent.style.display = 'none';

    function toggleFields() {
        // Hide all fields first
        if (temaField) temaField.style.display = 'none';
        if (normativaField) normativaField.style.display = 'none';

        // temaField.style.display = 'none';
        // yearField.style.display = 'none';
        // normativaField.style.display = 'none';

        // Show relevant field based on selection
        switch(tipoTestSelect.value) {

            case 'tema':
                if (temaField) temaField.style.display = 'block';
                // temaField.style.display = 'block';
                break;

            // case 'año':
            //     yearField.style.display = 'block';
            //     break;

            case 'normativa':
                if (normativaField) normativaField.style.display = 'block';
                // normativaField.style.display = 'block';
                break;
            // case 'aleatorio':
            //     // Make API call to get total question count
            //     fetch(`${document.querySelector('.tema-field').getAttribute('data-url')}?tipo_test=aleatorio`)
            //         .then(response => response.json())
            //         .then(data => {
            //             const numPreguntasInput = document.getElementById('id_numero_de_preguntas');
            //             const helpText = numPreguntasInput.nextElementSibling;
            //             helpText.textContent = `Preguntas disponibles: ${data.count}`;
            //             numPreguntasInput.max = data.count;
            //         })
            //         .catch(error => console.error('Error:', error));
            //     break;
        }
    }

    // Initial state
    toggleFields();

    // Listen for changes
    tipoTestSelect.addEventListener('change', toggleFields);
});

/* Función para mostrar el número de Preguntas Disponibles según el Tipo de Test seleccionado.
*
* Es decir, si el usuario selecciona un tema, se le mostrarán el número preguntas disponibles para ese tema. Es decir,
* si el usuario selecciona "Tema 1", se le mostrará la cantidad total de preguntas disponibles para el tema 1. Mientras
* tanto, si selecciona una normativa o un año, se le mostrará el número total de preguntas disponibles para esa
* normativa o ese año.
*
* Esta función va a ser llamada cada vez que cambie tanto el menu desplegable que me permite seleccionar el tipo de test
* ("año", "normativa", o "tema"), como el menu desplegable que me permite seleccionar el tema, año o normativa. Es
* decir, si selecciono "por tema" como tipo de test, se me debe llamar a esta función. Adicionalmente, abro el menú
* desplegable, y selecciono el tema 2, se debe llamar a esta función. Entonces, tengo que poner 2 event listeners:
* uno para el menu desplegable que me permite seleccionar el tipo de test, y otro para el menu desplegable que me
* permite seleccionar el tema, año o normativa.
*
* Thanks. Now, in the "preguntas_disponibles" form field from my forms.py file from my
* ConfigurarTestSinPreguntasFormularios Form, I want to render the number that is obtained from the fetch() call that
* I'm selecting right now. As of right now, the total number of exam questions is being rendered outside the form
* field. And I want it to be rendered within the form field. So please, render the number obtained from this fetch()
* call into the form field described from my form from my forms.py file.
*
* The main change is adding the line numPreguntasInput.value = data.count; which will update the form field's value
* with the count received from the API. The count will now appear both in the form field and in the help text below it.
*
* Let's fix the bugs in your configurar_nuevo_test_a_generar.js:
*
* 1) Correcting the fetch URL and handling potential errors: The data-url attribute should be fetched from an actual
* input checkbox, and we need to ensure it's the correct API endpoint (/tests/get-question-count/).
*
* 2) Addressing the "function called 3 times" issue: This usually happens if event listeners are attached to more
* elements than intended or if they are attached multiple times. We'll refine the selector for attaching event
* listeners to be very specific to the input checkboxes.
*
* 3) Resolving the selectElement compile error: Since selectElement is not used in the current logic path, we'll
* remove it.
*
* Key changes and explanations:
*
* 1) selectElement Removed: The variable selectElement was removed from updateQuestionCount as it was unused in the
* active code path, resolving the compile error.
*
* 2) Specific Selector for data-url: Changed document.querySelector('.tema-checkbox') to
* document.querySelector('input[name="tema"].tema-checkbox[data-url]') to reliably get the data-url from an actual
* input checkbox that possesses this attribute. Added checks if urlElement or url is null.
*
* 3) Specific Selector for Iterating Checkboxes: Inside updateQuestionCount, when collecting selectedTopics, the selector
* is now document.querySelectorAll('input[name="tema"].tema-checkbox:checked').
*
* 4) Error Handling in Fetch: Added a check for !response.ok to catch HTTP errors (like 404) before trying to parse
* JSON. The error log now includes the problematic URL.
*
* 5) Event Listener Attachment (for "called 3 times" issue): The DOMContentLoaded block that attaches event listeners
* for
* updateQuestionCount should use a specific selector: document.querySelectorAll('input[name="tema"].tema-checkbox').
* This ensures the listener is attached only to the input type="checkbox" elements and not to any container div that
* might also have the .tema-checkbox class. This is crucial to prevent the function from being called multiple times.
* I've also included how you might attach updateQuestionCount to the tipo_de_test select and a potential normativa
* select, ensuring it's called when those change as well.
*
* Make sure your DOMContentLoaded where you attach these listeners is structured correctly (ideally, one main
* DOMContentLoaded for the script). The provided snippet focuses on the updateQuestionCount function and the specific
* listener attachment for the tema checkboxes.
* */
function updateQuestionCount(event) {

    // Get the target element (the checkbox or select that triggered the event)
    const selectElement = event.target || this;

    const tipoTest = document.getElementById('tipo_de_test').value;

    // const selectedValue = selectElement.value;
    // const url = selectElement.getAttribute('data-url');

    // Return if no test type is selected (blank option)
    if (!tipoTest) return;

    // // Create the query parameters based on test type
    // const params = new URLSearchParams();
    // params.append('tipo_test', tipoTest);

    if (tipoTest === 'tema') {
        // Get all checked checkboxes
        const selectedTopics = [];


        // document.querySelectorAll('.tema-checkbox:checked').forEach(checkbox => {
        //     selectedTopics.push(checkbox.value);
        // });

        // Be specific: select INPUT elements with name="tema" and class ".tema-checkbox" that are checked
        document.querySelectorAll('input[name="tema"].tema-checkbox:checked').forEach(checkbox => {
            selectedTopics.push(checkbox.value);
        });

        // Build the query parameters
        const params = new URLSearchParams();
        params.append('tipo_test', 'tema');

        // De aquí viene la variable "temas" que usé en el back-end para coger la lista de "temas" seleccionados
        selectedTopics.forEach(topic => {
            params.append('temas', topic);
        });

        // Get data-url from a reliable source: an INPUT checkbox that has the attribute.
        const urlElement = document.querySelector('input[name="tema"].tema-checkbox[data-url]');
        if (!urlElement) {
            console.error('Configuration error: Could not find data-url on any input[name="tema"].tema-checkbox.');
            // Update UI to show an error
            const numPreguntasInput = document.getElementById('id_preguntas_disponibles');
            if (numPreguntasInput) {
                numPreguntasInput.value = '';
                const helpText = numPreguntasInput.nextElementSibling;
                if (helpText) helpText.textContent = 'Error de configuración (URL no encontrada).';
            }
            return;
        }
        const url = urlElement.getAttribute('data-url'); // This should be '/tests/get-question-count/'


        // // Get data-url from any checkbox (they all have the same).
        // const url = document.querySelector('.tema-checkbox').getAttribute('data-url');

        // Make API call to get question count.
        fetch(`${url}?${params.toString()}`)
            .then(response => response.json())
            .then(data => {

                // // BORRAR. Esto me dice el número de preguntas disponibles agarradas de mi back-end para los temas
                // // seleccionados.
                // console.log(`Preguntas encontradas para los temas seleccionados: ${data.count}`);


                const numPreguntasInput = document.getElementById('id_preguntas_disponibles');
                numPreguntasInput.value = data.count;
                const helpText = numPreguntasInput.nextElementSibling;
                helpText.textContent = `Puedes escoger hasta un máximo de ${data.count} preguntas para este test.`;
            })
            .catch(error => console.error('Error:', error));
    } // Fin del API call para los temas elegidos

    // BOOKMARK
    else if (tipoTest === 'normativa') { // API call para las normativas elegidas. CORREGIR.

        // Esto coge todas las normativas que el usuario ha seleccionado
        const normativasSeleccionadas = [];

        // Be specific: select INPUT elements with name="Normativa" and class ".normativa-checkbox" that are checked
        document.querySelectorAll('input[name="normativa"].normativa-checkbox:checked').forEach(checkbox => {
            normativasSeleccionadas.push(checkbox.value);
        });

        // Build the query parameters
        const params = new URLSearchParams();
        params.append('tipo_test', 'normativa');

        // De aquí viene la variable "temas" que usé en el back-end para coger la lista de "temas" seleccionados
        normativasSeleccionadas.forEach(topic => {
            params.append('normativas', topic);
        });

        // Get data-url from a reliable source: an INPUT checkbox that has the attribute.
        const urlElement = document.querySelector('input[name="normativa"].normativa-checkbox[data-url]');
        if (!urlElement) {
            console.error('Configuration error: Could not find data-url on any input[name="normativa"].normativa-checkbox.');
            // Update UI to show an error
            const numPreguntasInput = document.getElementById('id_preguntas_disponibles');
            if (numPreguntasInput) {
                numPreguntasInput.value = '';
                const helpText = numPreguntasInput.nextElementSibling;
                if (helpText) helpText.textContent = 'Error de configuración (URL no encontrada).';
            }
            return;
        }
        const url = urlElement.getAttribute('data-url'); // Should be '/tests/get-question-count/'

        // Make API call to get question count.
        fetch(`${url}?${params.toString()}`)
            .then(response => response.json())
            .then(data => {

                // // BORRAR. Esto me dice el número de preguntas disponibles agarradas de mi back-end para los temas
                // // seleccionados.
                // console.log(`Preguntas encontradas para las Normativas seleccionadas: ${data.count}`);


                const numPreguntasInput = document.getElementById('id_preguntas_disponibles');
                numPreguntasInput.value = data.count;
                const helpText = numPreguntasInput.nextElementSibling;
                helpText.textContent = `Puedes escoger hasta un máximo de ${data.count} preguntas para este test.`;
            })
            .catch(error => console.error('Error:', error));
    }

    // REACTIVAR todo este bloque de codigo después si no me funciona lo de los checkboxes.
    // // Esto agrega el menú desplegable para que selecciones el tema, o la normativa
    // switch (tipoTest) {
    //
    //     // Si el test seleccionado es te tipo "tema":
    //     case 'tema':
    //         params.append('tema', selectedValue);
    //         break;
    //     // case 'año':
    //     //     params.append('year', selectedValue);
    //     //     break;
    //     case 'normativa':
    //         params.append('normativa', selectedValue);
    //         break;
    //     // case 'aleatorio':
    //     //     // No additional params needed for random questions
    //     //     break;
    // }
    //
    // // // USAR UN SWITCH / CASE AQUI DESPUES
    // // if (tipoTest === 'tema') {
    // //     // params.append('tema', document.querySelector('.tema-field').value);
    // //
    // //     params.append('tema', selectedValue);
    // // } else if (tipoTest === 'año') {
    // //     // params.append('year', document.querySelector('.year-field').value);
    // //
    // //     params.append('year', selectedValue);
    // // } else if (tipoTest === 'normativa') {
    // //     // params.append('normativa', document.querySelector('.normativa-field').value);
    // //
    // //     params.append('normativa', selectedValue);
    // // }
    //
    // // Make the fetch call.
    // /* Esto es lo que renderiza el número de preguntas disponibles, NO el campo de solo lectura del forms.py.
    // *
    // * Y la cosa es que quiero que el número de preguntas disponibles se meta en el campo de solo lectura del forms.py.
    // * */
    // fetch(`${url}?${params.toString()}`)
    //     .then(response => response.json())
    //     .then(data => {
    //         // Update the help text below the number input
    //         const numPreguntasInput = document.getElementById('id_preguntas_disponibles');
    //
    //         // esto mete en el campo de solo lectura el número de Preguntas Disponibles para el test seleccionado
    //         numPreguntasInput.value = data.count;
    //
    //         // Descripción del campo que renderiza el número máximo de preguntas que puedes insertar en el test.
    //         const helpText = numPreguntasInput.nextElementSibling;
    //         helpText.textContent = `Puedes escoger hasta un máximo de ${data.count} preguntas para este test.`;
    //
    //         // // Update max value of number input
    //         // numPreguntasInput.max = data.count;
    //     })
    //     .catch(error => console.error('Error:', error));



}

/* Esto le agrega el event listener a los checkboxes con los temas. Cuando el usuario clique en un tema, se le debe
* mostrar el número de preguntas disponibles para ese tema.
* */
document.addEventListener('DOMContentLoaded', function() {

    // Attach listeners specifically to the INPUT checkboxes for 'tema'
    const temaCheckboxes = document.querySelectorAll('input[name="tema"].tema-checkbox');
    temaCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateQuestionCount);
    });

    // Attach listeners specifically to the INPUT checkboxes for 'Normativa'
    const normativaCheckboxes = document.querySelectorAll('input[name="normativa"].normativa-checkbox');
    normativaCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateQuestionCount);
    });

    // // If you have a 'normativa' select that should also trigger this:
    // const normativaSelect = document.getElementById('id_normativa');
    // if (normativaSelect) {
    //     normativaSelect.addEventListener('change', updateQuestionCount);
    // }

    // const checkboxes = document.querySelectorAll('.tema-checkbox');
    // checkboxes.forEach(checkbox => {
    //     checkbox.addEventListener('change', updateQuestionCount);
    // });
});