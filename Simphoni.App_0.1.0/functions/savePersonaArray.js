// functions/savePersonaArray.js
const functions = require('firebase-functions');
const { db } = require('./firebaseAdmin');

exports.savePersonaArray = functions.https.onCall(async (data, context) => {
  const userId = context.auth.uid;
  const { personaArray } = data;

  if (!userId) {
    throw new functions.https.HttpsError(
      "unauthenticated",
      "User must be authenticated."
    );
  }

  try {
    await db
      .collection("users")
      .doc(userId)
      .collection("persona-arrays")
      .doc("default")
      .set({ personaArray }, { merge: true });
    return { success: true };
  } catch (error) {
    console.error("Error saving persona array:", error);
    throw new functions.https.HttpsError(
      "unknown",
      "Failed to save persona array."
    );
  }
});
