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
    demoData: null,
    
    async getStaticDemoData() {
        if (!this.demoData) {
            try {
                const res = await fetch('/demo.json');
                this.demoData = await res.json();
            } catch(e) {
                console.error("Failed to load static demo data", e);
                this.demoData = { documents: [], facts: [], relationships: [], categories: [], stats: {documents:0, facts:0, relationships:0, cases:0}, cases: [] };
            }
        }
        return this.demoData;
    },

    async getToken() {
        if (window.FirebaseAuth && window.FirebaseAuth.auth.currentUser) {
            return await window.FirebaseAuth.auth.currentUser.getIdToken();
        }
        return null;
    },

    async getDocuments() {
        const token = await this.getToken();
        if (token) return await API.getDocuments(token);
        
        // Unauthenticated: Merge Static Demo Data + Local Data
        const demo = await this.getStaticDemoData();
        const demoDocs = JSON.parse(JSON.stringify(demo.documents));
        const localDocs = await getLocal('documents');
        demoDocs.forEach(d => d.isDemo = true);
        localDocs.forEach(d => d.isLocal = true);
        return [...demoDocs, ...localDocs];
    },

    async deleteDocument(docId) {
        const token = await this.getToken();
        if (token) {
            return await API.deleteDocument(docId, token);
        } else {
            await deleteLocal('documents', docId);
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
        
        // Unauthenticated: Merge Static Demo Data + Local Data
        const demo = await this.getStaticDemoData();
        let demoFacts = JSON.parse(JSON.stringify(demo.facts));
        if (category) demoFacts = demoFacts.filter(f => f.category === category);
        if (doc_id) demoFacts = demoFacts.filter(f => f.source_doc_id === doc_id);
        
        let localFacts = await getLocal('facts');
        if (category) localFacts = localFacts.filter(f => f.category === category);
        if (doc_id) localFacts = localFacts.filter(f => f.source_doc_id === doc_id);
        
        demoFacts.forEach(f => f.isDemo = true);
        return [...demoFacts, ...localFacts];
    },

    async getRelationships() {
        const token = await this.getToken();
        if (token) return await API.getRelationships(null, token);
        
        const demo = await this.getStaticDemoData();
        const demoRels = JSON.parse(JSON.stringify(demo.relationships));
        const demoFacts = demo.facts;
        
        // Enriched demo
        const enrichedDemo = demoRels.map(rel => {
            return {
                relationship: rel,
                fact_a: demoFacts.find(f => f.id === rel.fact_a_id) || null,
                fact_b: demoFacts.find(f => f.id === rel.fact_b_id) || null
            }
        });

        const localRels = await getLocal('relationships');
        const facts = await getLocal('facts');
        const enrichedLocal = localRels.map(rel => {
            return {
                relationship: rel,
                fact_a: facts.find(f => f.id === rel.fact_a_id) || null,
                fact_b: facts.find(f => f.id === rel.fact_b_id) || null
            }
        });
        return [...enrichedDemo, ...enrichedLocal];
    },

    async getCategories() {
        const token = await this.getToken();
        if (token) return await API.getCategories(token);

        const demo = await this.getStaticDemoData();
        const facts = await getLocal('facts');
        const catMap = {};
        
        demo.categories.forEach(c => catMap[c.name] = c.count);
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
        
        const demo = await this.getStaticDemoData();
        const localDocs = await getLocal('documents');
        const localFacts = await getLocal('facts');
        const localRels = await getLocal('relationships');
        
        return {
            documents: demo.stats.documents + localDocs.length,
            facts: demo.stats.facts + localFacts.length,
            relationships: demo.stats.relationships + localRels.length,
            cases: demo.stats.cases
        };
    },
    
    async getCases() {
        const token = await this.getToken();
        if (token) return await API.getCases(token);
        const demo = await this.getStaticDemoData();
        return demo.cases || [];
    },

    async uploadPdf(file) {
        const token = await this.getToken();
        const res = await API.uploadPdf(file, token);
        
        // If unauthenticated, save the returned data locally
        if (!token && res.document) {
            await putLocal('documents', res.document);
            if (res.facts) {
                for (let f of res.facts) await putLocal('facts', f);
            }
            if (res.relationships) {
                for (let r of res.relationships) await putLocal('relationships', r);
            }
        }
        
        // Always clear the demo data cache so new data shows on next render
        this.demoData = null;
        
        return res;
    }
};
