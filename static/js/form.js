// ---- CONSTANTS ----

const applicationform = document.querySelector("#application")

const error_server = "Bei der Kommunikation mit dem Server ist ein Fehler aufgetreten."
const error_requires_reload = "Beim Auswerten des Formulars ist ein Fehler aufgetreten.\nBitte laden Sie diese Seite neu."
const error_too_many_requests = "Von Ihrer IP-Adresse sind zu viele Anfragen eingegangen. Bitte versuchen Sie es später erneut."
const message_success = "Ihr Antrag ist bei uns eingegangen."
const message_mail = "Wir senden Ihnen eine Empfangsbestätigung per Email."


// ---- FUNCTIONS ----

/**
 * Sends a POST request containing data entered into a form.
 * If the response is in JSON format, returns it as an Object.
 * 
 * @param {Element} form 
 * @param {string} url 
 * @returns {Promise.<Object,Error>}
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
		return error;
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
	// Handle returned Javascript errors
	if (!Object.hasOwn(result, 'status')) {
		if (result.message == 'Response status: 429') {
			window.alert(error_too_many_requests);
		} else {
			window.alert(error_server);
		}
		return;
	}

	if (result.status.toLowerCase() === 'ok') {
		// Show confirmation of a successful submission
		let message = message_success;
		if (result.sending_mail == true) {
			message = message + '\n' + message_mail;
		}
		window.alert(message);
	} else {
		// Show received error messages on corresponding form field
		try {
			for (let key in result.errors) {
				if (key == 'csrf_token') throw new Error('Invalid CSRF token');

				try {
					const field = document.querySelector(`input[name="${key}"]`);
					field.setCustomValidity(result.errors[key][0]);
				} catch (error) {
					throw new Error('Failed to set custom validity for '+key);
				}
				document.querySelector('input:invalid').focus();
			}
		} catch (error) {
			console.error(error);
			window.alert(error_requires_reload);
		}
	}
}


// ---- MAIN ----

applicationform.addEventListener("submit", (event) => {
	event.preventDefault();
	submitApplication();
});