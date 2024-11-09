// src/firebase.js
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';
import 'firebase/compat/firestore';
import 'firebase/compat/analytics';

// Your Firebase configuration object from the Firebase console
const firebaseConfig = {
  apiKey: "AIzaSyAhZ4Bxb3o21DCv4xQJ5N_LLU9SOpQy17o",
  authDomain: "simphony-b5d8d.firebaseapp.com",
  projectId: "simphony-b5d8d",
  storageBucket: "simphony-b5d8d.appspot.com", // Corrected storageBucket URL
  messagingSenderId: "763160142287",
  appId: "1:763160142287:web:98acc1a299428e201772ba",
  measurementId: "G-Z60JN6ZWS6"
};

// Initialize Firebase
if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
  // Initialize analytics if needed
  firebase.analytics();
}

// Export authentication and firestore instances
export const auth = firebase.auth();
export const firestore = firebase.firestore();

export default firebase;
