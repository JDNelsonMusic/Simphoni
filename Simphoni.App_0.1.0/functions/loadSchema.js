// functions/loadSchema.js
const functions = require('firebase-functions');
const { db } = require('./firebaseAdmin');

exports.loadSchema = functions.https.onCall(async (data, context) => {
  const userId = context.auth.uid;
  if (!userId) {
    throw new functions.https.HttpsError(
      "unauthenticated",
      "User must be authenticated."
    );
  }

  try {
    const schemaDoc = await db
      .collection("users")
      .doc(userId)
      .collection("instruct-schemas")
      .doc("default")
      .get();
    if (!schemaDoc.exists) {
      return { schema: [] };
    }
    return { schema: schemaDoc.data().schema };
  } catch (error) {
    console.error("Error loading schema:", error);
    throw new functions.https.HttpsError(
      "unknown",
      "Failed to load schema."
    );
  }
});
