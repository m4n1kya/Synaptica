import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { 
    getAuth, 
    signInWithPopup, 
    GoogleAuthProvider,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    onAuthStateChanged,
    signOut
} from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyCSOhcOKT8kkxKkuz2NSXXl21eB-K0F2FU",
    authDomain: "synaptica-m4n1kya.firebaseapp.com",
    projectId: "synaptica-m4n1kya",
    storageBucket: "synaptica-m4n1kya.firebasestorage.app",
    messagingSenderId: "551871768995",
    appId: "1:551871768995:web:a5c36ccb526ecc3ae35216",
    measurementId: "G-8D27TBN4EW"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

window.FirebaseAuth = {
    auth,
    googleProvider,
    signInWithPopup,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    onAuthStateChanged,
    signOut
};
