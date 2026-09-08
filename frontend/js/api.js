/**
 * Synaptica — API Client
 * Handles all communication with the FastAPI backend.
 */
const API = {
    // If hosted on localhost, use localhost. Otherwise, route all API calls to the Render backend.
    baseUrl: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') 
        ? window.location.origin 
        : 'https://synaptica-7ha3.onrender.com',

    async wakeUpBackend() {
        try {
            // Silently ping the backend to wake up the Render free tier instance
            fetch(`${this.baseUrl}/api/documents`).catch(() => {});
        } catch (e) {}
    },

    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            const response = await fetch(url, {
                headers: { 'Content-Type': 'application/json', ...options.headers },
                ...options
            });
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    },

    // Documents
    async getDocuments() {
        return this.request('/api/documents');
    },

    async getDocument(docId) {
        return this.request(`/api/documents/${docId}`);
    },

    async deleteDocument(docId) {
        return this.request(`/api/documents/${docId}`, { method: 'DELETE' });
    },

    async uploadPdf(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${this.baseUrl}/api/upload`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('Upload failed');
        return response.json();
    },

    // Facts
    async getFacts(params = {}) {
        const query = new URLSearchParams();
        if (params.category) query.set('category', params.category);
        if (params.doc_id) query.set('doc_id', params.doc_id);
        if (params.min_confidence) query.set('min_confidence', params.min_confidence);
        if (params.dataset) query.set('dataset', params.dataset);
        const qs = query.toString();
        return this.request(`/api/facts${qs ? '?' + qs : ''}`);
    },

    async getFact(factId) {
        return this.request(`/api/facts/${factId}`);
    },

    async getCategories() {
        return this.request('/api/categories');
    },

    // Relationships
    async getRelationships(relType = null) {
        const qs = relType ? `?rel_type=${relType}` : '';
        return this.request(`/api/relationships${qs}`);
    },

    async getRelationshipStats() {
        return this.request('/api/relationships/stats');
    },

    // Cases
    async getCases() {
        return this.request('/api/cases');
    },

    // Stats
    async getStats() {
        return this.request('/api/stats');
    },

    // Analysis
    async triggerAnalysis() {
        return this.request('/api/analyze', { method: 'POST' });
    },

    // Health
    async healthCheck() {
        return this.request('/api/health');
    }
};
