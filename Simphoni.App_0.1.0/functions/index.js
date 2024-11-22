// functions/index.js
const functions = require('firebase-functions');
const loadSchema = require('./loadSchema').loadSchema;
const saveSchema = require('./saveSchema').saveSchema;
const loadPersonaArray = require('./loadPersonaArray').loadPersonaArray;
const savePersonaArray = require('./savePersonaArray').savePersonaArray;

// Export functions
exports.loadSchema = loadSchema;
exports.saveSchema = saveSchema;
exports.loadPersonaArray = loadPersonaArray;
exports.savePersonaArray = savePersonaArray;
