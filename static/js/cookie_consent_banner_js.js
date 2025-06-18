/* Snippet del Banner de Consentimiento de Cookies.

This code was taken from Godson Thomas from:
https://github.com/Godsont/Cookie-Consent-Banner/blob/master/main.js .
*/
const cookieContainer = document.querySelector(".cookie-container");
const cookieButton = document.querySelector(".cookie-btn");

/* Esto se va a ejecutar si el usuario clica en "Acepto las Cookies" en el Banner de Cookies. */
cookieButton.addEventListener("click", () => {

  // Esto esconde el Banner de las Cookies despues de clicar en "Acepto Cookies"
  cookieContainer.classList.remove("active");

  // Esto agrega una cookie
  localStorage.setItem("cookieBannerDisplayed", "true");
});

setTimeout(() => {
  if (!localStorage.getItem("cookieBannerDisplayed")) {
    cookieContainer.classList.add("active");
  }
}, 2000);
/* Fin del snippet del Banner de Consentimiento de Cookies */