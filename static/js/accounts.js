// ---- CONSTANTS ----

const accountform = document.getElementById('accountform');
const inputfields = accountform.getElementsByTagName('input');
const idfield = document.getElementById('target_id');
const passwordfield = document.getElementById('password');
const passwordconfirmfield = document.getElementById('confirm_password');

const error_requires_reload = "Beim Auswerten des Formulars ist ein Fehler aufgetreten.\nDie Seite wird nun neu geladen.";
const message_create_success = "Der Benutzeraccount wurde angelegt."
const message_changes_success = "Die Änderungen wurden gespeichert.";

const textfieldtypes = ['text', 'email', 'password'];

// ---- FUNCTIONS ----

/**
 * Überprüft ein Texteingabefeld und gibt gegebenenfalls
 * eine passende Fehlermeldung aus.
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird
 */
function validateText(target) {
	target.value = target.value.trim()
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte füllen Sie dieses Feld aus.');
	} else if (target.type == 'email' && target.validity.typeMismatch) {
		target.setCustomValidity('Bitte geben Sie eine Email-Adresse ein.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft, ob Passwortfeld und Bestätigungsfeld übereinstimmen.
 */
function validateConfirmPassword() {
	if (passwordfield.value != passwordconfirmfield.value) {
		passwordconfirmfield.setCustomValidity('Stimmt nicht mit dem Passwort überein.');
	} else {
		passwordconfirmfield.setCustomValidity('');
	}
}

async function sendAccountForm() {
	let url = '/api/users/add';
	if (idfield && idfield.value) {
		url = '/api/users/edit/' + idfield.value;
	}

	const result = await call(url, new FormData(accountform));
	if (!result) {
		window.alert(error_server);
	} else if (!(result.status.toLowerCase() === 'ok')) {
		// Show received error messages on corresponding form field
		try{
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
			console.error("Failed to fetch data:", error.message);
			window.alert(error_requires_reload);
			location.reload();
			return;
		}
	} else {
		if (idfield && idfield.value) {
			window.alert(message_changes_success);
		} else {
			window.alert(message_create_success);
		}
		location.reload();
	}
}

// ---- MAIN ----

function start() {
	accountform.addEventListener("submit", (event) => {
		event.preventDefault();
		sendAccountForm();
	});

	for (let i = 0; i < inputfields.length; i++) {
		if (textfieldtypes.includes(inputfields[i].type)) {
			validateText(inputfields[i]);
			inputfields[i].addEventListener('change',function(){
				validateText(this);
			});
		}
	}
	passwordfield.addEventListener('change', validateConfirmPassword);
	passwordconfirmfield.addEventListener('change', validateConfirmPassword);
}

window.addEventListener('pageshow', start);