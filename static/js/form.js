// ---- CONSTANTS ----

const applicationform = document.querySelector("#application")

const error_server = "Bei der Kommunikation mit dem Server ist ein Fehler aufgetreten."
const error_requires_reload = "Beim Auswerten des Formulars ist ein Fehler aufgetreten.\nBitte laden Sie diese Seite neu."
const message_success = "Ihr Antrag ist bei uns eingegangen.\nIhre Vorgangsnummer lautet {{ID}}."


// ---- FUNCTIONS ----

/**
 * Sends a POST request containing data entered into a form.
 * If the response is in JSON format, returns it as an Object.
 * 
 * @param {Element} form 
 * @param {string} url 
 * @returns {Promise.<Object,undefined>}
 */
async function sendData(form, url) {
	const formData = new FormData(form);
	try{
		const response = await fetch(url, {method: "POST", body: formData, });
		if (!response.ok) {
			throw new Error(`Response status: ${response.status}`);
		}const data = await response.json();
		return data;
	} catch (error) {
		console.error("Failed to fetch data:", error.message);
		return;
	}
}

/**
 * Submit the form to the server API and
 * inform the user of the result.
 * 
 * @returns {undefined}
 */
async function submitApplication() {
	const result = await sendData(applicationform, '/api/submit');
	if (!result) {
		window.alert(error_server);
		return;
	}
	if (result.status.toLowerCase() === 'ok') {
		window.alert(message_success.replace("{{ID}}", result.id));
	} else {
		// Show received error messages on corresponding form field
		try {
			let focused = false
			for (let key in result.errors) {
				if (key == 'csrf_token') throw new Error('Invalid CSRF token');

				const field = document.querySelector(`#${key}`);
				field.setCustomValidity(result.errors[key][0]);
				if (!focused) {
					field.focus();
					focused = true;
				}
				field.addEventListener('change', function clicked(){
					field.setCustomValidity('');
					field.removeEventListener('change', clicked);
				});
			}
		} catch (error) {
			console.error("Failed to set custom validity for", key);
			window.alert(error_requires_reload);
		}
	}
}


// ---- MAIN ----

applicationform.addEventListener("submit", (event) => {
	event.preventDefault();
	submitApplication();
});