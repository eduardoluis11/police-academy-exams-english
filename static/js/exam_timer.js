/* This Javascript file handles two main functionalities for the exam interface
*
* 1) Countdown Timer.
* 2) Form Submission or Form Action Handler.
*
* The integration works like this:
*
* The template provides the initial time in the <span id="time"> element.
*
* Navigation buttons in the template call submitForm() with appropriate actions.
*
* When time expires or user clicks a button, the form submits with the corresponding action, which the view then
* processes.
* */


/* Función que me permite arreglar el formato del temporizador para que me muestre minutos y segundos en lugar de
* solo segundos.
*
* This will:
*   1) Convert seconds to minutes and seconds (e.g., 90 seconds → "1:30").
*   2) Pad single-digit seconds with a leading zero (e.g., "5:05" instead of "5:5").
*   3) Keep the backend value in seconds while showing a formatted time to users.
*   4) Update the display every second while maintaining the same functionality.
* */
function formatTime(seconds) {

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}


/* Temporizador de Javascript para el Test.
*
* Esto agrega la funcionalidad del cronómetro o temporizador a los tests.
*
* El temporizador se pone en segundos. Es decir, si quiero poner media hora al test, debo escribir "1800" en el timer.
*
* Now, modify my exam_time.js file so that, if the timer hits "0", that is, if time is up, execute the "Finalizar"
* button of my tomar_test.html template so that the button gets clicked automatically once the timer hits 0.
*
* To automatically trigger the "Finalizar" button when time runs out:
*    1) Added code to find the finish button using querySelector
*    2) Used button.click() to programmatically trigger the button click
*    3) Kept the interval at 1000ms (1 second) for smooth countdown
*    4) Maintained the same timer logic and display update
* This will automatically submit the form with action=finish when the timer reaches zero.
*
* I want the time to be formatted in minutes and seconds AT ALL TIMES, that is, even if the timerActive boolean is
* false. To do this, I will do the following changes:
*   1) Added initial time formatting right after getting the time value.
*   2) Kept the format update inside the interval for when the timer is active.
*
* Now the time will always be displayed in minutes:seconds format, even when the timer is inactive.
*
* Tuve que hacer unas modificaciones ya que, al iniciar el temporizador, lo estoy iniciando en minutos desde el backend.
* El problema es que, si hacía eso, el tiempo iniciaba, por ejemplo, en 10 minutos, por lo que JavaScript parecía
* estar convirtiendo eso en 10 segundos, por lo que los tests tenían menos tiempo de lo que les asigné. Por
* eso, tuve que, desde aquí, volver a convertir el tiempo de minutos a segundos, y luego otra vez de segundos a minutos.
* Así, el temporizador se inicia en 10 minutos en lugar de 10 segundos si selecciono 10 minutos para el temporizador
* al seleccionar el test.
*
* Voy a asegurarme de que el div con el ID de "timer" exista antes de ejecutar el JavaScript para hacer funcionar
* el temporizador. Así, si el tiempo para tomar el test es ilimitado, esto NO se ejecutará, ya que el ID de "timer"
* no existirá.
*
* I provided three layers of redundancy to ensure that the test is always submitted once the timer reaches zero:
*
*   It tries to click the button first.
*   If that fails, it directly submits the form with the 'finish' action.
*   As a last resort, it redirects to the completed tests page after a short delay.
*
* This should ensure the exam ends properly when the timer reaches zero, regardless of the exam type.
* */
document.addEventListener('DOMContentLoaded', function() {

    // Only initialize timer if it exists (not unlimited time)
    if (document.getElementById('timer')) {

        // When the page loads, it initializes a timer using the remaining time from the template
        // Esto coge el tiempo en sí del cronómetro en la página, y lo convierte en un integer
        // Parse formatted time string (e.g. "10:00") into total seconds
        const timeString = document.getElementById('time').innerText;
        const [minutes, seconds] = timeString.split(':').map(Number);

        // Convierto el tiempo de minutos a segundos
        let timeRemaining = (minutes * 60) + seconds;

        // let timeRemaining = parseInt(document.getElementById('time').innerText);
        // Esto coge el div que contiene el cronómetro
        const timerDisplay = document.getElementById('time');

        // Format initial time display in minutes and seconds, regardless of timer boolean state.
        // Vuelvo a convertir el tiempo de segundos a minutos
        timerDisplay.innerText = formatTime(timeRemaining);


        // Booleano que me dirá si el temporizador está activo o no. En principio, estará activado
        let timerActive = true;

        /* Countdown Timer.
         *
         * Every second, this:
         * 1) Decrements the timer.
         * 2) Updates the display.
         * 3) If time reaches zero, automatically submits the form with 'finish' action.
         *
         * */
        const timer = setInterval(function() {

            // Si el temporizador está activado
            if (timerActive) {

                // Esto quita un segundo al cronómetro cada segundo
                timeRemaining--;

                // Esto renderiza y refresca el temporizador en la página, y lo pone en minutos y segundos
                timerDisplay.innerText = formatTime(timeRemaining);

                // Si se acaba el tiempo del test
                if (timeRemaining <= 0) {
                    clearInterval(timer);

                    // Encuentra el botón de "Finalizar" y le hace clic automáticamente.
                    const finishButton = document.querySelector('button[value="finish"]');
                    if (finishButton) {
                        finishButton.click();
                    }

                    // As a backup, also submit the form directly
                    const examForm = document.getElementById('exam_form');
                    if (examForm) {
                        // Set the action to 'finish' before submitting
                        const actionInput = document.createElement('input');
                        actionInput.type = 'hidden';
                        actionInput.name = 'action';
                        actionInput.value = 'finish';
                        examForm.appendChild(actionInput);

                        // Submit the form
                        examForm.submit();
                    }

                    // If all else fails, redirect to results list's page
                    setTimeout(() => {
                        window.location.href = '/tests/lista-de-resultados';
                    }, 1000);

                    // document.getElementById('form_action').value = 'finish';
                    // document.getElementById('exam_form').submit();
                }
            }   // Fin del "if" que detecta si el temporizador está activado
         }, 1000);    // Número de milisegundos para el cronómetro. Esto refresca cada segundo el temporizador.
        // }, 60); // Numero de milisegundos para el cronómetro. Esto hace que el temporizador vaya muy rapido (0.6 s).
        // }, 1800);    // Numero de milisegundos para el cronómetro. El temporizador va muy lento con esto (1.8 s).

        /* Función para guardar el tiempo restante del temporizador, y luego salir del test. Esto usa fetch() para llamar
        * a una API en mi backend de Django.
        *
        * Now, modify my saveAndExit() JS function so that it also saves the currently selected answer for the current
        * question in my tomar_test.html template. My "Siguiente" and "Anterior" buttons already do that. My "goto" links
        * from my sidebar in my template already do that. So, just add that same functionality from those buttons and links
        * of being able to save the currently selected answer from the current answer to my saveAndExit() JS function.
        * Look at my tomar_test() view from my views.py file for reference on how to implement that.
        *
        * I'll modify the saveAndExit() function to save both the timer and the currently selected answer.
        *
        * Key changes made:
        *    Made the function async to properly handle multiple fetch requests
        *    Added form submission similar to your navigateToQuestion function
        *    Used the existing 'goto' action which already handles answer saving
        *    Added proper error handling
        *    Made sure the timer is saved after the answer is saved
        *    Maintained the redirect to the incomplete tests page
        *
        * This ensures both the current answer and remaining time are saved before redirecting.
        */
        window.saveAndExit = async function() {
            timerActive = false;
            clearInterval(timer);

            // // DEBUGGEO: Esto me muestra si algo se está metiendo en el input oculto de session_id y en timeRemaining.
            // // BUG: NO: Esto no se está ejecutando.
            // // BOOKMARK.
            // console.log("session ID: " + document.getElementById('session_id').value);
            // console.log("Time remaining: " + timeRemaining);

            // Get the form and selected answer
            const form = document.getElementById('exam_form');
            const formData = new FormData(form);
            formData.append('action', 'goto');  // Using 'goto' as it already handles answer saving

            // Usaré un try / catch para evitar errores
            try {

                // Primero, guarda la respuesta seleccionada de la pregunta actual en el modelo de RespuestaDelUsuario
                await fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin'
                });


                // Luego, guarda el tiempo restante del temporizador en el modelo de SesionDelTest
                // Esto llama a la vista de Django con la API para guardar el tiempo restante del temporizador
                await fetch('/tests/save-time/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        session_id: document.getElementById('session_id').value,
                        remaining_time: timeRemaining
                    })
                }).then(() => {

                    // // DEBUGGEO. Esto solo me muestra un "hola mundo" para que el then() se ejecute.
                    // console.log("Hola Mundo");

                    // Esto reenvía al usuario a la Lista de Tests Interrumpidos
                    window.location.href = '/tests/tests-incompletos/';  // Redirect to test list
                });
            } catch (error) {
            console.error('Error saving:', error);
            }
        };
    }   // Fin del "if" que detecta si el temporizador existe (si el tiempo no es ilimitado)
});

/* Form Action Handler.
*
* Provides a submitForm function that's called by the template's navigation buttons.
* Sets the hidden 'action' field value (previous/next/finish) before form submission.
*
* */
function submitForm(action) {
    document.getElementById('form_action').value = action;
    document.getElementById('exam_form').submit();
}