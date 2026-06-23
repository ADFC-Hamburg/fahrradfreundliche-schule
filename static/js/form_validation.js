// ---- CONSTANTS ----

const personalFields = document.getElementById('personaldata').getElementsByTagName('input');
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


// ---- MAIN ----

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

for (let i = 0; i < complianceFields.length; i++) {
	if (complianceFields[i].type == 'checkbox') {
		validateCheckbox(complianceFields[i]);
		complianceFields[i].addEventListener('change',function(){
			validateCheckbox(this);
		});
	}
}
