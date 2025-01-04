import { initializeApp } from 'firebase/app';
import { getDatabase } from 'firebase/database';

const firebaseConfig = {
  databaseURL: "https://plagiamvision-default-rtdb.firebaseio.com/",
  // Add other Firebase config options if needed (apiKey, authDomain, etc.)
};

const app = initializeApp(firebaseConfig);
export const database = getDatabase(app);
