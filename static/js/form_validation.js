// ---- CONSTANTS ----

const questionFileMarker = 'file_'

const personalFields = document.getElementById('personaldata').getElementsByTagName('input');
const questionFields = document.getElementById('questions').getElementsByTagName('input');
const complianceFields = document.getElementById('compliance').getElementsByTagName('input');


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
		target.setCustomValidity('Bitte fülle dieses Feld aus.');
	} else if (target.type == 'email' && target.validity.typeMismatch) {
		target.setCustomValidity('Bitte gib eine Email-Adresse ein.');
	} else if (target.validity.patternMismatch) {
		target.setCustomValidity('Bitte gib einen gültigen Wert ein.');
	} else if (target.minLength > -1 && (target.maxLength == target.minLength) && (target.value.length != target.minLength)) {
		target.setCustomValidity('Bitte gib genau '+target.minLength+' Zeichen ein.');
	} else if (target.minLength > -1 && target.value.length < target.minLength) {
		target.setCustomValidity('Bitte gib mindestens '+target.minLength+' Zeichen ein.');
	} else if (target.maxLength > -1 && target.value.length > target.maxLength) {
		target.setCustomValidity('Bitte gib höchstens '+target.maxLength+' Zeichen ein.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Zahleneingabefeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird 
 */
function validateNumber(target) {
	if (target.validity.valueMissing || target.validity.badInput) {
		target.setCustomValidity('Bitte gib hier eine Zahl ein.');
	} else if (target.validity.rangeUnderflow) {
		if (target.min == 0) {
			target.setCustomValidity('Bitte gib hier eine Zahl ein, die nicht negativ ist.');
		} else {
			target.setCustomValidity('Bitte gib hier eine Zahl ein, die nicht kleiner als '+target.min+' ist.');
		}
	} else 	if (target.validity.rangeOverflow) {
		target.setCustomValidity('Bitte gib hier eine Zahl ein, die nicht größer als '+target.max+' ist.');
	} else if (target.validity.stepMismatch) {
		if (!target.step || target.step == 1) {
			target.setCustomValidity('Bitte gib hier nur ganze Zahlen ein.');
		} else {
			target.setCustomValidity('Bitte gib hier nur durch '+target.step+' teilbahre Zahlen ein.');
		}
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Kontrollkästchenfeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird 
 */
function validateCheckbox(target) {
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte stimme zu.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Optionsfeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird 
 */
function validateRadio(target) {
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte triff eine Auswahl.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Uploadfeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird 
 */
function validateFile(target) {
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte lade für jedes Ja einen Beleg hoch.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft alle Felder, die zu einer Frage gehören.
 * Setzt außerdem das Uploadfeld auf Benötigt oder Optional, abhängig
 * davon, welches Optionsfeld ausgewählt ist.
 * 
 * @param {string} name 
 */
function processQuestion(name) {
	const options = document.querySelectorAll('input[name="'+name+'"]');
	const file = document.getElementById(questionFileMarker+name);
	const selected = document.querySelector('input[name="'+name+'"]:checked')

	for (let i = 0; i < options.length; i++) {
		validateRadio(options[i]);
	}
	file.required = (selected && selected.value && selected.value != "0");
	validateFile(file);
}


// ---- MAIN ----

function start() {
	for (let i = 0; i < personalFields.length; i++) {
		if (personalFields[i].type == 'text' || personalFields[i].type == 'email') {
			validateText(personalFields[i]);
			personalFields[i].addEventListener('change',function(){
				validateText(this);
			});
		} else if (personalFields[i].type == 'number') {
			validateNumber(personalFields[i]);
			personalFields[i].addEventListener('change',function(){
				validateNumber(this);
			});
		}
	}

	for (let i = 0; i < questionFields.length; i++) {
		if (questionFields[i].type == 'radio') {
			if (questionFields[i].id.endsWith('-0')) {
				processQuestion(questionFields[i].name);
			}
			questionFields[i].addEventListener('input',function(){
				processQuestion(this.name);
			});
		} else if (questionFields[i].type == 'file') {
			validateFile(questionFields[i]);
			questionFields[i].addEventListener('input',function(){
				validateFile(this);
			});
		}
	}

	for (let i = 0; i < complianceFields.length; i++) {
		if (complianceFields[i].type == 'checkbox') {
			validateCheckbox(complianceFields[i]);
			complianceFields[i].addEventListener('change',function(){
				validateCheckbox(this);
			});
		}
	}
}

window.addEventListener('pageshow', start);