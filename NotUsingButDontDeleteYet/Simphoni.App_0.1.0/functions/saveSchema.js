// functions/saveSchema.js
const functions = require('firebase-functions');
const { db } = require('./firebaseAdmin');

exports.saveSchema = functions.https.onCall(async (data, context) => {
  const userId = context.auth.uid;
  const { schema } = data;

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
      .collection("instruct-schemas")
      .doc("default")
      .set({ schema }, { merge: true });
    return { success: true };
  } catch (error) {
    console.error("Error saving schema:", error);
    throw new functions.https.HttpsError(
      "unknown",
      "Failed to save schema."
    );
  }
});
