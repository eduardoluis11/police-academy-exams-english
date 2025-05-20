/* Script de JavaScript para los Tests Sin Autocorrección.
*
* */

/* Función que me guarda la respuesta seleccionada de la pregunta actual del test.
*
* Esto lo voy a llamar cuando el usuario haga clic en los botones "Anterior" o "Siguiente", o cuando el usuario
* clique en los enlaces a las preguntas en la barra de navegación lateral, lo cual haré desde la función
* navigateToQuestion().
*
* Esta función hace un POST request usando un fetch() call para llamar a una API en una de mis vistas de Django.
*
* Esto es lo que hace esta función:
*     Creates a dynamic form.
*     Adds the CSRF token.
*     Adds the currently selected answer if any.
*     Submits the form as POST.
*     The current answer will be saved (if selected).
*     A POST request will be sent.
*
* Refactoricé esta función para que solo guarde la respuesta seleccionada si la respuesta es diferente de null o
* None. Es decir, primero revisa si la respuesta es "A", "B", "C", o "D", y si lo es, entonces guarda la
* respuesta. Si no, no hace nada.
* */
async function saveAnswer() {
  const selectedAnswer = document.querySelector('input[name="selected_answer"]:checked');

  if (selectedAnswer && ['A', 'B', 'C', 'D'].includes(selectedAnswer.value)) {

      const formData = new FormData();
      formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
      formData.append('selected_answer', selectedAnswer.value);

      // {#if (selectedAnswer) {#}
      // {#    formData.append('selected_answer', selectedAnswer.value);#}
      // {# }#}

      formData.append('action', 'goto');

      // Esto hace un POST request usando fetch() para llamar a una API en una de mis vistas de Django
      await fetch(window.location.href, {
          method: 'POST',
          body: formData,
          credentials: 'same-origin'
      });
  }
}

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
* Esto solo se usa si clico los enlaces en el grid de pregutas en la barra de navegación lateral a la derecha
* de la pantalla. Esto NO se ejecuta cuando clico los botones "Siguiente" o "Anterior", o al menos solo guarda
* el tiempo restante del temporizador y la respuesta, PERO no me redirige a la página de la pregunta si clicas en
* los botones "Siguiente" o "Anterior".
*
*
*
* In JavaScript files, you cannot directly use Django/Jinja template tags since they are processed server-side.
* Instead, Add a data attribute to your HTML that contains the base URL.
*
* De manera resumida, quiero anotar la URL de la vista de tomar_test() usando Jinja, pero para la pregunta seleccionada
* del grid de preguntas en la barra de navegación lateral. Sin embargo, eso no lo puedo hacer en un script de
* JavaScript. Entonces, tendré que usar otro método. En mi caso, lo que hice fue crear un div invisible que
* contenta la URL de la vista de tomar_test() usando Jinja: Luego, en esta función de JavaScript, lo que hice fue
* coger la URL de ese div invisible y usarla para redirigir al usuario a la pregunta seleccionada del grid de
* preguntas en la barra de navegación lateral.
* */
async function navegarAPreguntaDelGridDeLaBarraLateral(sessionId, questionNumber, event) {
    event.preventDefault();

    // {#try {#}
    // {#    await Promise.all([saveTimeOnly(), saveAnswer()]);#}
    // {#    window.location.href = `/tests/test/sesion/${sessionId}/pregunta/${questionNumber}/`;#}
    // {# } catch (error) {#}
    // {#    console.error('Error during navigation:', error);#}
    // {# }#}

    // Esto coge el div invisible con la URL de la vista de tomar_test() que usa la notación de Jinja
    const urlElement = document.getElementById('test-urls');

    // Esto reemplaza los valores temporales de la sesión y el número de pregunta en la URL a los valores que debo usar
    const baseUrl = urlElement.dataset.testUrl
                             .replace('999999', sessionId)
                             .replace('/1/', `/${questionNumber}/`);


    // Guardo el tiempo restante del temporizador sin salirme del test.
    await saveTimeOnly();

    // Esto guarda la respuesta seleccionada de la pregunta actual del test en el modelo de RespuestaDelUsuario
    await saveAnswer();

    // Redirige al usuario a la pregunta seleccionada del grid de preguntas en la barra de navegación lateral
    window.location.href = baseUrl;
    // window.location.href = `{% url 'tests_clientes:tomar_test' ${sessionId} ${questionNumber} %}`;  // NO USAR
    // window.location.href = `/tests/test/sesion/${sessionId}/pregunta/${questionNumber}/`;

    // {#// Get the selected answer if any#}
    // {#const selectedAnswer = document.querySelector('input[name="selected_answer"]:checked');#}
    // {##}
    // {##}
    // {##}
    // {#// Create form data#}
    // {#const formData = new FormData();#}
    // {#formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);#}
    // {#if (selectedAnswer) {#}
    // {#    formData.append('selected_answer', selectedAnswer.value);#}
    // {# }#}
    // {#formData.append('action', 'goto');#}
    // {##}
    // {#// Submit using fetch#}
    // {#await fetch(window.location.href, {#}
    // {#    method: 'POST',#}
    // {#    body: formData,#}
    // {#    credentials: 'same-origin'#}
    // {# }).then(() => {#}
    // {#    // After saving, redirect to the selected question#}
    // {#    // After saving, redirect to the selected question with proper URL structure#}
    // {#    window.location.href = `/tests/test/sesion/${sessionId}/pregunta/${questionNumber}/`;#}
    // {#    #}
    //     {#window.location.href = `{% url 'tests_clientes:tomar_test' session_id=session.id question_number=1 %}`#}
    //     {#    .replace('1', questionNumber);#}
    // {# });#}

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
* The problem is in your selectAnswer() function. When you click a button, it correctly updates the hidden field, but it's not changing the button appearance because:

It's looking for elements with the class .answer-btn but your buttons don't have this class
It's looking for a data-value attribute, but your buttons have a regular value attribute
There's no CSS style defined for the selected class it's trying to add
* GitHub Copilot
The Button Selection Color Issue
The problem is in your selectAnswer() function. When you click a button, it correctly updates the hidden field, but it's not changing the button appearance because:

It's looking for elements with the class .answer-btn but your buttons don't have this class
It's looking for a data-value attribute, but your buttons have a regular value attribute
There's no CSS style defined for the selected class it's trying to add
Here's the fix for your test_sin_autocorreccion.js file:
This function:

Correctly selects all buttons with name="selected_answer"
Uses Bootstrap's btn-primary class (blue) to highlight the selected option
Makes sure all other buttons remain with the standard light gray appearance (btn-light) 
* */
function selectAnswer(letter) {
    // Update hidden field
    document.getElementById('selected_answer').value = letter;
    
    // Update button appearance
    document.querySelectorAll('.answer-btn').forEach(btn => {

        if (btn.value === letter) {
            // Change clicked button to blue
            btn.classList.remove('btn-light');
            btn.classList.add('btn-primary');
        } else {
            // Reset all other buttons to light gray
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-light');
        }

        // if (btn.getAttribute('data-value') === letter) {
        //     btn.classList.add('selected');
        // } else {
        //     btn.classList.remove('selected');
        // }
    });
    
    // Save answer if needed
    if (typeof saveAnswer === 'function') {
        saveAnswer();
    }
}