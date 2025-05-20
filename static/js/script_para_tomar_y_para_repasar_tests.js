// /* Función que me muestra la justificación de la respuesta correcta al clicar en el botón "Justificación" de la
// * pregunta seleccionada al repasar un test finalizado.
// *
// * Si la justificación está oculta, la muestra, y si está visible, la oculta. Es un botón de toggle.
// *
// * ELIMINAR esta función, ya que la justificación siempre se mostrará al repasar un test finalizado. En el caso
// * de un test autocorregido, la justificación se mostrará al responder la pregunta.
// * */
// function toggleJustificacion() {
//     const justificacion = document.getElementById('justificacion');
//     if (justificacion.style.display === 'none') {
//         justificacion.style.display = 'block';
//     } else {
//         justificacion.style.display = 'none';
//     }
// }

/* Now, make it so that, if the user is viewing the results of their test, render a button that says "save question".
* When the user clicks on that button, create a javascript function that will make a fetch() call or use an axios call
* so that a new record is inserted into the PreguntaGuardadaPorElUsuario() model. The record inserted will include an
* instance of the user, an instance of the test that was taken from the test() model, and an instance of the current
* question from the PreguntaDelTest() model.
*
* Creates an AJAX endpoint to handle saving questions.
* Prevents duplicate saves for the same question.
*
* The button will be disabled and show "Pregunta Guardada" after successfully saving the question. If there's an error
* (like trying to save a duplicate), it will show an alert with the error message.
*
* Now, could you make the Javascript button to be a toggle, so that, if the user has saved a question, but clicks the
* button again, the question gets deleted from the PreguntaGuardadaPorElUsuario() model? So, if the user enters into a
* question, and clicks on the "save question" button, the question will be saved in the database. However, if the user
* clicks on that button again, the question will no longer be saved by the user. I guess you'll have to make an API
* fetch() call to the PreguntaGuardadaPorElUsuario() model to delete the question that was previously saved by the user
* from the model.
*
* This implementation:
* 1. Toggles between saved/unsaved states
* 2. Makes API calls to either save or delete the question
* 3. Updates the button appearance and text accordingly
* 4. Handles errors gracefully
* 5. Shows the correct initial state based on whether the question is already saved
*
* The button will now toggle between "Guardar Pregunta" and "Pregunta Guardada" states, saving or deleting the question
* from the database accordingly.
*
* Esta función SIEMPRE se debe ejecutar en la plantilla de tomar_test.html, ya sea que estés tomanto el test sin
* autocorrección, con autocorrección, o estés repasando el test.
*
* Make sure your JavaScript function updates the bookmark Font Awesome icon. Update your guardarPregunta function to
* toggle the icon's class instead of changing the button text.
*
* I'll fix the guardarPregunta function to work properly with the bookmark icon instead of relying on the button
* classes.
*
* This solution:
*
* 1) Uses the fas class to determine if a question is saved instead of btn-success
* 2) Correctly selects the bookmark icon element
* 3) Properly toggles the icon's appearance when the state changes
* 4) Calls the appropriate endpoint based on the current state
* */
async function guardarPregunta(preguntaId, testId, sessionId) {
    try {
        // Get CSRF token from cookie
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // const button = document.getElementById('botonGuardarPregunta');

        // Find the bookmark icon (the HTML element with the class 'bookmark-container' for the "i" element.)
        const icon = document.querySelector('.bookmark-container i');

        // const isSaved = button.classList.contains('btn-success');

        // Check if question is saved by looking for the solid bookmark class (fas)
        const isSaved = icon.classList.contains('fas');

        const endpoint = isSaved ? '/tests/eliminar-pregunta-guardada/' : '/tests/guardar-pregunta/';


        // Make POST request to save question.
        // Esto va a llamar a "guardar pregunta" o a "eliminar pregunta", segun sea el caso.
        // const response = await fetch('/tests/guardar-pregunta/', {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            // NECESITO GUARDAR LA ID DE LA SESION TAMBIEN DESPUES. BOOKMARK
            body: JSON.stringify({
                pregunta_id: preguntaId,    // ID of the question to save
                test_id: testId, // ID of the test
                session_id: sessionId, // ID of the session
            })
        });

        const data = await response.json();

        if (data.status === 'success') {

            // // Esto lo necesito para que el botón del icono del marcador cambie de color al clicarlo.
            // var icon = document.getElementById('botonGuardarPregunta');

            // Si la pregunta estaba guardada, la eliminamos de la base de datos
            if (isSaved) {

                // // Disable button and change text
                // const button = document.getElementById('botonGuardarPregunta');
                // button.disabled = true;

                // button.textContent = 'Guardar Pregunta';
                // button.classList.remove('btn-success');
                // button.classList.add('btn-info');

                // Change to unsaved state (outline bookmark)
                icon.className = 'far fa-bookmark fa-2x text-secondary';
                icon.style.color = '#6c757d';
                icon.title = 'Guardar pregunta';


            } else {

                // // Si la pregunta no estaba guardada, la guardamos en la base de datos
                // button.textContent = 'Pregunta Guardada';
                // button.classList.remove('btn-info');
                // button.classList.add('btn-success');

                // Si la pregunta no estaba guardada, la guardamos en la base de datos.
                // Change to saved state (solid bookmark)
                icon.className = 'fas fa-bookmark fa-3x text-primary';
                icon.style.color = '#0d6efd';
                icon.title = 'Pregunta guardada';
            }

        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al guardar la pregunta');
    }
}