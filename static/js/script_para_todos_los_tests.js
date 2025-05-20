/* Script de JavaScript para Todos los Tests, sean Autocorregidos o no.
*
* */

/* Función para guardar el tiempo restante del temporizador cuando el usuario haga clic en los botones
* "Siguiente" o "Anterior", o cuando el usuario clique en los enlaces a las preguntas en la barra de navegación
* lateral.
*
* Es muy similar a la función saveAndExit(), pero esta función solo guarda el tiempo restante del temporizador
* sin salirte ni interrumpirte el examen.
*
* These changes will:
*      Save the current time whenever navigation occurs
*      Continue with normal navigation after saving
*      Keep the timer running
*      Not redirect to the incomplete tests page
*      The timer state will be preserved in the database but the exam session will continue uninterrupted.
*
* Esto ahora cogerá el tiempo en minutos. Sin embargo, debo enviar el tiempo en segundos a la vista de
* save-time/ en mi backend para que se guarde en la base de datos. Entonces, tendré que convertir el tiempo
* de minutos a segundos antes de enviarlo a la vista de save-time/ en mi backend.
*
* Key changes:
*     Split time string into minutes and seconds using split(':').
*     Convert string values to numbers using map(Number).
*     Calculate total seconds using formula: (minutes * 60) + seconds.
*     Send total seconds to backend instead of time string.
* */
async function saveTimeOnly() {
  try {
      const sessionId = document.getElementById('session_id').value;

      // Esto coge la cadena con el tiempo en minutos y segundos
      const timeString = document.getElementById('time').textContent;

      // Convert "minutes:seconds" to total seconds
      const [minutes, seconds] = timeString.split(':').map(Number);
      const totalSeconds = (minutes * 60) + seconds;

      // {#const timeLeft = document.getElementById('time').textContent;#}

      await fetch('/tests/save-time/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: JSON.stringify({
              session_id: sessionId,
              remaining_time: totalSeconds, // Esto envía el tiempo en segundos en lugar de minutos
              // {#remaining_time: timeLeft#}
          })
      });
  } catch (error) {
      console.error('Error saving time:', error);
  }
}

/* Función para Guardar la Respuesta del Test y Salir sin guardar el tiempo restante.
*
* Usaré esta función para los tests con tiempo ilimitado. Esto me permitirá corregir un bug en el que yo no podía
* guardar y salir de un test que tuviera tiempo ilimitado.
*
* This approach keeps your code clean by:
*
*    Maintaining separate functions for timed vs. unlimited tests.
*    Avoiding unnecessary timer logic in unlimited time tests.
*    Providing a consistent user experience for saving progress.
* */
async function guardarYSalirDeTestTiempoIlimitado() {
    // Get the form and selected answer
    const form = document.getElementById('exam_form');
    const formData = new FormData(form);
    formData.append('action', 'goto');  // Using 'goto' as it already handles answer saving

    try {
        // Save the currently selected answer
        await fetch(window.location.href, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        });

        // Redirect to the incomplete tests page
        window.location.href = '/tests/tests-incompletos/';
    } catch (error) {
        console.error('Error saving answer:', error);
    }
}

