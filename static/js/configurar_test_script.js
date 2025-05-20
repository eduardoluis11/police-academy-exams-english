/* Función para mostrar u ocultar las casillas para modificar los minutos y segundos si el usuario elige que quiere
* customizar el tiempo de su test en el template para Configurar un test.
*
* You'll need to add JavaScript to your template to show/hide the custom time fields based on the time_limit
* selection.
*
* The custom time fields will be hidden by default and only shown when the user selects the "Personalizado" option.
*
* Quité el campo de segundos, y solo dejé el de minutos.
* */

document.addEventListener('DOMContentLoaded', function() {
    const timeSelect = document.querySelector('[name="time_limit"]');
    // {#const customMinutes = document.querySelector('[name="custom_minutes"]');#}
    // {#const customSeconds = document.querySelector('[name="custom_seconds"]');#}

    // Esto hace aparecer y desaparecer los inputs y labels de los minutos y segundos customizados
    const customMinutes = document.querySelector('[name="custom_minutes"]').parentNode;
    // const customSeconds = document.querySelector('[name="custom_seconds"]').parentNode;

    function toggleCustomTimeFields() {
        const isCustom = timeSelect.value === '0';
        customMinutes.style.display = isCustom ? 'block' : 'none';
        // customSeconds.style.display = isCustom ? 'block' : 'none';
    }

    timeSelect.addEventListener('change', toggleCustomTimeFields);
    toggleCustomTimeFields();
});


// {#/* Función que muestra u oculta las preguntas personalizadas al cambiar el modo de selección de preguntas. #}
// {#*#}
// {#* Con esta función, o puedes usar las preguntas que vienen por defecto en el test seleccionado, o puedes#}
// {#* seleccionar cualquier pregunta de la base de datos para incluirla en el testt. Así, el usuario podrá#}
// {#* crear su propio test de manera customizada.#}
// {#* #}
// {#* ## JavaScript to toggle question selection visibility#}
// {#*#}
// {#* This implementation:#}
// {#*    Shows default questions first.#}
// {#*    Allows switching between default and custom selection.#}
// {#*    Groups custom questions by test name.#}
// {#*    Handles both modes in the view.#}
// {#*    Saves selected questions to the session.#}
// {#* */#}
// {#document.addEventListener('DOMContentLoaded', function() {#}
// {#    const defaultSection = document.getElementById('defaultQuestionsSection');#}
// {#    const customSection = document.getElementById('customQuestionsSection');#}
// {#    const modeInputs = document.querySelectorAll('input[name="question_mode"]');#}
// {##}
// {#    modeInputs.forEach(input => {#}
// {#        input.addEventListener('change', function() {#}
// {#            if (this.value === 'default') {#}
// {#                defaultSection.style.display = 'block';#}
// {#                customSection.style.display = 'none';#}
// {#            } else {#}
// {#                defaultSection.style.display = 'none';#}
// {#                customSection.style.display = 'block';#}
// {#            }#}
// {#        });#}
// {#    });#}
// {# });#}







// {#document.addEventListener('DOMContentLoaded', function() {#}
// {#    const useCustomCheckbox = document.getElementById('useCustomQuestions');#}
// {#    const questionSelection = document.getElementById('questionSelection');#}
// {#    const selectAllBtn = document.getElementById('selectAll');#}
// {#    const deselectAllBtn = document.getElementById('deselectAll');#}
// {#    const checkboxes = document.querySelectorAll('.question-checkbox');#}
// {##}
// {#    // Toggle question selection visibility#}
// {#    useCustomCheckbox.addEventListener('change', function() {#}
// {#        questionSelection.style.display = this.checked ? 'block' : 'none';#}
// {#    });#}
// {##}
// {#    // Select all questions#}
// {#    selectAllBtn.addEventListener('click', function() {#}
// {#        checkboxes.forEach(checkbox => checkbox.checked = true);#}
// {#    });#}
// {##}
// {#    // Deselect all questions#}
// {#    deselectAllBtn.addEventListener('click', function() {#}
// {#        checkboxes.forEach(checkbox => checkbox.checked = false);#}
// {#    });#}
// {# });#}