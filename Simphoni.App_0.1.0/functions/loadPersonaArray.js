// functions/loadPersonaArray.js
const functions = require('firebase-functions');
const { db } = require('./firebaseAdmin');

exports.loadPersonaArray = functions.https.onCall(async (data, context) => {
  const userId = context.auth.uid;
  if (!userId) {
    throw new functions.https.HttpsError(
      "unauthenticated",
      "User must be authenticated."
    );
  }

  try {
    const personaArrayDoc = await db
      .collection("users")
      .doc(userId)
      .collection("persona-arrays")
      .doc("default")
      .get();
    if (!personaArrayDoc.exists) {
      return { personaArray: [] };
    }
    return { personaArray: personaArrayDoc.data().personaArray };
  } catch (error) {
    console.error("Error loading persona array:", error);
    throw new functions.https.HttpsError(
      "unknown",
      "Failed to load persona array."
    );
  }
});
