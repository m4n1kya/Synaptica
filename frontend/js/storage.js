/**
 * Synaptica - Data Access Layer
 * Manages hybrid storage: Local IndexedDB for unauthenticated users,
 * Cloud Backend (Firestore) for authenticated users.
 */

// Simple IndexedDB Wrapper
const DB_NAME = 'synaptica_local';
const DB_VERSION = 1;

const initDB = () => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('documents')) db.createObjectStore('documents', { keyPath: 'id' });
            if (!db.objectStoreNames.contains('facts')) db.createObjectStore('facts', { keyPath: 'id' });
            if (!db.objectStoreNames.contains('relationships')) db.createObjectStore('relationships', { keyPath: 'id' });
        };
    });
};

const getLocal = async (storeName) => {
    const db = await initDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
};

const putLocal = async (storeName, data) => {
    const db = await initDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const request = store.put(data);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
};

const deleteLocal = async (storeName, id) => {
    const db = await initDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const request = store.delete(id);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
};

// Main StorageManager
window.StorageManager = {
    async getToken() {
        if (window.FirebaseAuth && window.FirebaseAuth.auth.currentUser) {
            return await window.FirebaseAuth.auth.currentUser.getIdToken();
        }
        return null;
    },

    async getDocuments() {
        const token = await this.getToken();
        if (token) return await API.getDocuments(token);
        return await getLocal('documents');
    },

    async deleteDocument(docId) {
        const token = await this.getToken();
        if (token) {
            return await API.deleteDocument(docId, token);
        } else {
            await deleteLocal('documents', docId);
            // Cleanup local facts
            const facts = await getLocal('facts');
            for (let f of facts) {
                if (f.source_doc_id === docId) await deleteLocal('facts', f.id);
            }
            return { status: 'success' };
        }
    },

    async getFacts(category = null, doc_id = null) {
        const token = await this.getToken();
        if (token) return await API.getFacts(category, doc_id, token);
        
        let facts = await getLocal('facts');
        if (category) facts = facts.filter(f => f.category === category);
        if (doc_id) facts = facts.filter(f => f.source_doc_id === doc_id);
        return facts;
    },

    async getRelationships() {
        const token = await this.getToken();
        if (token) return await API.getRelationships(token);
        
        const rels = await getLocal('relationships');
        const facts = await getLocal('facts');
        const enriched = rels.map(rel => {
            return {
                relationship: rel,
                fact_a: facts.find(f => f.id === rel.fact_a_id) || null,
                fact_b: facts.find(f => f.id === rel.fact_b_id) || null
            }
        });
        return enriched;
    },

    async getCategories() {
        const token = await this.getToken();
        if (token) return await API.getCategories(token);

        const facts = await getLocal('facts');
        const catMap = {};
        facts.forEach(f => {
            catMap[f.category] = (catMap[f.category] || 0) + 1;
        });
        return Object.entries(catMap)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count);
    },

    async getStats() {
        const token = await this.getToken();
        if (token) return await API.getStats(token);
        
        return {
            documents: (await getLocal('documents')).length,
            facts: (await getLocal('facts')).length,
            relationships: (await getLocal('relationships')).length,
            cases: 0
        };
    },
    
    async getCases() {
        return [];
    },

    async uploadPdf(file) {
        const token = await this.getToken();
        const res = await API.uploadPdf(file, token);
        
        // If unauthenticated, save the returned data locally
        if (!token && res.document) {
            await putLocal('documents', res.document);
            for (let f of res.facts) await putLocal('facts', f);
            for (let r of res.relationships) await putLocal('relationships', r);
        }
        return res;
    }
};
