/* Función que me permite ir a la pregunta seleccionada al clicar en cualquiera de los enlaces del grid de Preguntas en
* la mitad derecha del navegador (en la barra de navegación lateral) al repasar un test finalizado.
*
* */
async function navegarAPreguntaAlRepasarElTest(sessionId, questionNumber, event) {
    event.preventDefault();

    // Esto redirige al usuario a la pregunta seleccionada en la vista de repasar_test_finalizado()
    // Esto NO debería estar hard-coded. OPTIMIZAR DESPUES.
    window.location.href = `/tests/repasar-test/${sessionId}/pregunta/${questionNumber}/`;

}



