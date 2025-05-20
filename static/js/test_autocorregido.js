/* Script de JavaScript para el Template de Tomar Tests cuando el test esta siendo autocorregido. */

/* Función para navegar a la pregunta seleccionada de la barra de navegación lateral del grid de preguntas para los
* tests de autocorrección.
* */
/* Función para que, al clicar en cualquiera de los enlaces del grid de Preguntas en la mitad derecha del
* navegador (en la barra de navegación lateral), se guarde la respuesta de la pregunta actual del test.
*
* Eso se hace enviando un POST request.
*
* Here's what I want: in this template, I have a form on the left side of the browser, and I have a series of
* links on a grid on the right side of the browser. Well, the links work just fine. My issue is that, whenever
* I click on the "a" tag in the selected snippet, I want to send a POST request. That is because the selected
* answer of the current page in my form on the left side of the browser will be saved on my database if I make
* any kind of POST request from this template. Could you modify my current code so that, if users click on the
* link of the "a" tag on the selected snippet, that a POST request should be sent?
*
* You'll have to modify the code to send a POST request when clicking the links.
*
* Key changes made:
*      Changed the <a> tags to use an onclick handler instead of href
*      Created a navigateToQuestion() function that:
*         Prevents the default link behavior
*         Adds an action field to identify the navigation type
*         Kept the same styling and conditional classes
*      This way, when users click on a question number:
*         They'll be redirected to the selected question
*
* You'll need to handle the goto action in your view to make sure it processes the saved answer before
* redirecting.
*
* This way, you'll send the selected answer when clicking on question links on the sidebar.
*
* I used a template literal to construct the URL properly when redirecting the user to the correct question if
* they click on the sidebar, ensuring the session ID and question number are placed in their correct
* positions without affecting each other.
*
* Guardo el tiempo restante del temporizador sin salirme del test para que, cuando me cambie de una pregunta
* a otra al clicar en una pregunta en la barra de navegación lateral, no se me pierda el tiempo restante del
* temporizador, ni se me reinicie el temporizador desde el principio.
*
* Esto solo se usa si clico los enlaces en el grid de preguntas en la barra de navegación lateral a la derecha
* de la pantalla. Esto NO se ejecuta cuando clico los botones "Siguiente" o "Anterior", o al menos solo guarda
* el tiempo restante del temporizador y la respuesta, PERO no me redirige a la página de la pregunta si clicas en
* los botones "Siguiente" o "Anterior".
* */
async function navegarAPreguntaDelGridDeLaBarraLateralAutocorregido(sessionId, questionNumber, event) {
    event.preventDefault();

    // Get base URL from data attribute and replace placeholder values
    const urlElement = document.getElementById('test-urls');
    const baseUrl = urlElement.dataset.testUrl
                             .replace('999999', sessionId)
                             .replace('/1/', `/${questionNumber}/`);

    // Guardo el tiempo restante del temporizador sin salirme del test.
    await saveTimeOnly();

    // Redirect to the selected question
    window.location.href = baseUrl;
}


/* Función para que, a penas clique en una de las respuestas de la pregunta, se me guarde la respuesta seleccionada
* en la base de datos, y ya no pueda cambiar mi respuesta. Es decir, que a penas yo clique en una de las respuestas,
* se me desactivarán todas las 3 o 4 respuestas de la pregunta, y no podré cambiar mi respuesta.
*
* También me mostrará un mensaje de feedback (correcto o incorrecto) en la parte inferior de la pregunta.
*
* // Function to handle immediate answer submission and feedback.
    // Only proceed if this is an autocorrect exam.
*
*
*
*
* Here's a solution to handle immediate answer submission and disabling radio buttons when a selection is made in autocorrect mode:


To implement this, you'll need to:

1. Add data attribute to your template body tag:


2. Update your answer container in the template:


3. Add some CSS for feedback:


This solution:
- Only activates for autocorrect exams
- Immediately disables radio buttons when an answer is selected
- Sends the answer to the backend
- Shows immediate feedback with correct/incorrect status
- Displays the justification if available
- Handles errors gracefully
- Uses Bootstrap alert classes for feedback styling

The user experience will be:
1. User sees question with enabled radio buttons
2. User selects an answer
3. All radio buttons become disabled immediately
4. Feedback appears showing if answer was correct
5. Shows justification for the answer
6. User can move to next question but cannot change current answer

Remember that this needs to work with your Django view that handles the AJAX request (the one in the `tomar_test_autocorregido` view we discussed earlier).
*
* No le estoy asignando la función a los radio buttons con un onClick, sino que, a penas se carga la página del
* template, ya se le asigna la función a los radio buttons. Si me meto en el inspector del navegador, no me va a salir
* esta función en ninguna parte. Lo que pasa es que, a penas se carga el template de tomar el test, esta función se
* va a ejecutar inmediatamente. Lo que hará serña escuchar si le hago click a cualquiera de los 3 o 4 botones radio.
* De ser así, se guarda la respuesta en el modelo de RespuestaDelUsuario para la pregunta actual.
*
* Now, I want to modify autocorrected exams show the right answer and its justification when the user selects an answer.
* Instead of showing the right answer for an autocorrected exam as I'm doing right now, I want to show the right answer
* in the exact same way as it id displayed if a user is viewing their results. That is, I want to show what the "if
* viewing_results" snippets show, but ONLY after the user answers the currently selected question. That is, I only want
* to display the HTML code from the "if viewing_results" snippets if a user clicks on any of the 4 radio buttons during
* an autocorrected exam.
*
* I had to modify your JavaScript function to remove the custom feedback div and rely on the template's feedback. To do
* this, I had to reload the page once the user selects an answer. This maintains consistent styling across both
* the autocorrected test and the review page for the test.
*
* You need to update your test_autocorregido.js file to handle the button elements instead of radio buttons. Here's the solution:

The key changes are:

Created a new handleAutocorrectAnswerForButtons function that:

Takes the letter directly instead of extracting it from an event object
Disables all answer buttons immediately
Submits the selected answer to the backend
Saves the time and reloads the page to show the correct/incorrect styling
Modified the selectAnswer function to:

Update the hidden input value
Provide visual feedback by changing button colors
Call the new handleAutocorrectAnswerForButtons function
Removed the old event listeners that were attached to radio buttons since they're no longer needed (the buttons have onclick="selectAnswer('{{ option_letter }}')" in the HTML)

This implementation maintains the same behavior as your original autocorrected exams but works with button elements instead of radio buttons.
* */
async function handleAutocorrectAnswer(letter) {

    // // DEBUGGEO: Esto imprime un mensaje cuando clico en una de las 4 opciones. NO FUNCIONA.
    // console.log('Clicado en una de las respuestas de la pregunta');

    // DEBUGGEO: Esto imprime un mensaje cuando clico en una de las 4 opciones. SE EJECUTA CORRECTAMENTE.
    console.log('Handling autocorrect for letter:', letter);

    // const selectedRadio = event.target;
    // const selectedAnswer = selectedRadio.value;
    // const allRadios = document.querySelectorAll('input[name="selected_answer"]');

    // Disable all buttons immediately for better UX
    const allButtons = document.querySelectorAll('.answer-btn');
    allButtons.forEach(button => {
        button.disabled = true;
    });

    // // Disable all radio buttons immediately
    // allRadios.forEach(radio => {

    //     // // DEBUGGEO: Esto imprime un mensaje cuando clico en una de las 4 opciones. SE EJECUTA CORRECTAMENTE.
    //     // console.log('Se debería ejecutar la función que desactiva los radio buttons');

    //     radio.disabled = true;
    //     // radio.setAttribute('disabled', 'disabled');  // Esto no es necesario
    // });

    // Prepare form data
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
    // formData.append('selected_answer', selectedAnswer);
    formData.append('selected_answer', letter);
    formData.append('action', 'answer');

    try {
        // Send answer to backend
        const response = await fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Guardo el tiempo restante del temporizador antes de refrescar la página
        await saveTimeOnly();

        // Refresca la página para que se muestre si la respuesta es correcta con los estilos de Repasar el Test
        window.location.reload();

        // // Handle the response
        // // Tengo que saber que se está enviando aquí, porque no puedo extraer el campo "es correcto" del registro de
        // // RespuestaDelUsuario().
        // const data = await response.json();
        //
        // // // DEBUGGEO: Imprimir el JSON que me devuelve el servidor.
        // // console.log(data);
        //
        // // Apply visual feedback.
        // // Esto agarra el div que contiene las opciones de respuesta, los cuales tienen la clase "options".
        // const answerContainer = document.querySelector('.options');
        // const feedbackDiv = document.createElement('div');
        //
        // // Si el usuario respondió correctamente, la variable de JSON tendrá el campo "es_correcto" en true
        // if (data.es_correcto) {
        //
        //     // Esto imprime un mensaje de confirmación que dice que la respuesta es correcta
        //     feedbackDiv.className = 'alert alert-success mt-3';
        //     feedbackDiv.textContent = '¡Correcto! ';
        // } else {
        //
        //     // Esto imprime un mensaje de error que dice que la respuesta es incorrecta
        //     feedbackDiv.className = 'alert alert-danger mt-3';
        //     feedbackDiv.textContent = `Incorrecto. La respuesta correcta es: ${data.correct_answer}. `;
        // }
        //
        // // Esto agrega la justificación a la respuesta al lado de la respuesta
        // if (data.justificacion) {
        //     feedbackDiv.textContent += `Justificación: ${data.justificacion}`;
        // }
        //
        // // Esto me muestra si la respuesta es correcta o no. EDITAR PARA USAR LOS ESTILOS DE CUANDO REPASO EL TEST.
        // answerContainer.appendChild(feedbackDiv);

    } catch (error) {
        console.error('Error:', error);

        // Re-enable buttons if there was an error
        allButtons.forEach(button => {
            button.disabled = false;
        });

        // // Re-enable radio buttons if there was an error
        // allRadios.forEach(radio => {
        //     radio.disabled = false;
        // });
    }
}

/* After reviewing your code, I can see exactly why your exam only works properly with radio buttons. Here are the key
reasons:

1. Form Submission and Data Handling
The primary issue is that your form submission process is built around standard HTML form behavior with radio buttons:

This code specifically looks for a checked radio button to determine the selected answer. If you change to buttons,
there's no "checked" property to find.

2. Built-in State Management
Radio buttons with the same name attribute have built-in functionality that:

Ensures only one can be selected at a time
Maintains which option is selected (browser state)
Automatically includes the selected value in form submissions
Your code relies on this behavior throughout the application.

3. No JavaScript Fallback for Buttons
To use buttons instead of radio buttons, you would need JavaScript that:

Handles button clicks
Updates button appearance to show which is selected
Stores the selected value in a hidden form field
Ensures this value gets submitted with the form
This JavaScript isn't implemented in your code base.

4. Backend Expectations
Your Django views expect form data with a field named selected_answer, which automatically comes from radio buttons
but wouldn't come from button clicks without additional JavaScript.

Solution Options
If you want to use buttons instead of radio buttons, you'd need to:

Add a hidden input to store the selected answer:


Write JavaScript to update this hidden field when buttons are clicked:

Modify your buttons to call this function:

This would create a complete alternative to the radio button functionality, but requires significant changes to your
current code.
*
* The problem is in your selectAnswer() function. When you click a button, it correctly updates the hidden field, but
it's not changing the button appearance because:

It's looking for elements with the class .answer-btn but your buttons don't have this class
It's looking for a data-value attribute, but your buttons have a regular value attribute
There's no CSS style defined for the selected class it's trying to add
* GitHub Copilot
The Button Selection Color Issue
The problem is in your selectAnswer() function. When you click a button, it correctly updates the hidden field, but
it's not changing the button appearance because:

It's looking for elements with the class .answer-btn but your buttons don't have this class
It's looking for a data-value attribute, but your buttons have a regular value attribute
There's no CSS style defined for the selected class it's trying to add
Here's the fix for your test_sin_autocorreccion.js file:
This function:

Correctly selects all buttons with name="selected_answer"
Uses Bootstrap's btn-primary class (blue) to highlight the selected option
Makes sure all other buttons remain with the standard light gray appearance (btn-light)

 This is your new function for autocorrected exams

 * Looking at your code, the issue is that when a user clicks on an answer button in an autocorrected exam, it
 briefly turns blue (btn-primary) before the page reloads to show the correct colors (green or red).

Let's fix the selectAnswer function in test_autocorregido.js to avoid this unwanted blue color:

This simplified version does two key things:

Updates the hidden input field with the selected letter
Immediately triggers the handleAutocorrectAnswer function without changing any button colors first
Since the page will reload immediately anyway (in the handleAutocorrectAnswer function), there's no need to apply any
temporary color changes. When the page reloads, the server will have processed the answer and will render the buttons
with the correct styles:

Green (btn-success) for correct answers
Red (btn-danger) for incorrect answers
This approach provides a cleaner user experience without the brief flash of blue before showing the correct color.
* */
function selectAnswer(letter) {
    // Update hidden field
    document.getElementById('selected_answer').value = letter;

    // For autocorrected exams, don't change to blue - skip visual feedback
    // since the page will reload anyway with the correct colors
    

    // // Update button appearance
    // document.querySelectorAll('.answer-btn').forEach(btn => {

    //     if (btn.value === letter) {
    //         // Para un test Autocorregido, este botón se debe poner rojo o verde, pero NUNCA Azul
    //         btn.classList.remove('btn-light');
    //         btn.classList.add('btn-primary');
    //     } else {
    //         // Reset all other buttons to light gray
    //         btn.classList.remove('btn-primary');
    //         btn.classList.add('btn-light');
    //     }

    //     // if (btn.getAttribute('data-value') === letter) {
    //     //     btn.classList.add('selected');
    //     // } else {
    //     //     btn.classList.remove('selected');
    //     // }
    // });

    // Call the handleAutocorrectAnswer with the appropriate event object
    handleAutocorrectAnswer(letter);

    // // Save answer if needed
    // if (typeof saveAnswer === 'function') {
    //     handleAutocorrectAnswer();
    // }
}

// Remove the old event listeners that were attaching to radio buttons
// The DOMContentLoaded event listener below is no longer needed since
// we're using the onclick attribute directly on the buttons.
// // Add event listeners when the document loads
// document.addEventListener('DOMContentLoaded', () => {
//
//     const radioButtons = document.querySelectorAll('input[name="selected_answer"]');
//     radioButtons.forEach(radio => {
//         radio.addEventListener('change', handleAutocorrectAnswer);
//     });
//
// });