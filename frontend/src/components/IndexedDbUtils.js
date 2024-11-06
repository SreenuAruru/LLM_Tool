import { openDB } from 'idb';

const DB_NAME = 'myApp';
const DB_VERSION = 1;
const STORE_NAME = 'vectorStore';

export async function openDatabase() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME);
      }
    },
  });
}

export async function saveStoreId(storeId) {
  try {
    const db = await openDatabase();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    await store.put(storeId, 'storeId');
    await tx.done;
  } catch (error) {
    console.error('Error saving store ID:', error);
    throw error;
  }
}

export async function getStoreId() {
  try {
    const db = await openDatabase();
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    return await store.get('storeId');
  } catch (error) {
    console.error('Error getting store ID:', error);
    throw error;
  }
}

export async function clearStoreId() {
  try {
    const db = await openDatabase();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    await store.delete('storeId');
    await tx.done;
  } catch (error) {
    console.error('Error clearing store ID:', error);
    throw error;
  }
}
