import { ref, set, get, child } from 'firebase/database';
import { database } from './firebaseConfig';

export const writeData = async (path: string, data: any) => {
  try {
    await set(ref(database, path), data);
    return true;
  } catch (error) {
    console.error('Error writing data:', error);
    return false;
  }
};

export const readData = async (path: string) => {
  try {
    const snapshot = await get(child(ref(database), path));
    if (snapshot.exists()) {
      return snapshot.val();
    }
    return null;
  } catch (error) {
    console.error('Error reading data:', error);
    return null;
  }
};

export const testFirebaseConnection = async () => {
  const testData = {
    message: "Test connection",
    timestamp: new Date().toISOString()
  };

  try {
    // Write test data
    const writeResult = await writeData('test/connection', testData);
    if (!writeResult) {
      console.error('Failed to write test data');
      return false;
    }

    // Read test data
    const readResult = await readData('test/connection');
    if (!readResult) {
      console.error('Failed to read test data');
      return false;
    }

    console.log('Firebase connection test successful!', readResult);
    return true;
  } catch (error) {
    console.error('Firebase connection test failed:', error);
    return false;
  }
};
