// ---- CONSTANTS ----

const DeleteLinks = document.getElementsByClassName('delete');

const message_confirm = 'Soll * wirklich gelöscht werden?'
const error_server = "Bei der Kommunikation mit dem Server ist ein Fehler aufgetreten."
const fallback_element = 'der Eintrag'

// ---- FUNCTIONS ----

/**
 * Sends a POST request to the specified URL and returns the response.
 * 
 * @param {string} url
 * @returns {Promise.<Object,undefined>}
 */
async function call(url, body = '') {
	try {
		const response = await fetch(url, {method: "POST", body: body});
		if (!response.ok) {
			throw new Error(`Response status: ${response.status}`);
		}const data = await response.json();
		return data;
	} catch(error) {
		console.error("Failed to fetch data:", error.message);
		return;
	}
}

/**
 * Send a POST request to the specified URL.
 * If this API call fails, show an appropriate error message;
 * finally, return whether the API call was successful.
 * 
 * @param {string} url
 * @returns {Promise.<boolean>}
 */
async function executeApiCall(url, body = '') {
	const result = await call(url, body);
	if (!result) {
		window.alert(error_server);
		return false;
	}

	if (!(result.status.toLowerCase() === 'ok')) {
		windows.alert(result.error);
		return false;
	}
	return true;
}

/**
 * Show a message box to confirm that an object should be deleted.
 * Upon confirmation, sends a POST request to the URL specified.
 * If this API call succeeds, navigate to the destination URL
 * or reload the page if undefined.
 * 
 * @param {string} description
 * @param {string} url
 * @param {string|undefined} destination
 * 
 */
function confirmDeletion(description, url, destination = undefined) {
	const message = message_confirm.replace('*', description || fallback_element);
	if (!confirm(message)) {
		return;
	}

	executeApiCall(url).then((status) => {
		if (!status){
			return;
		}
		if (destination) {
			window.location.href = destination;
		} else {
			location.reload();
		}
	});
}

// ---- MAIN ----

for (let element of DeleteLinks) {
	element.addEventListener('click', (event) => {
		event.preventDefault();
		confirmDeletion(element.dataset.description, element.href, element.dataset.returnhref);
	});
}
