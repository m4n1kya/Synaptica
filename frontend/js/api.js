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

    async request(endpoint, options = {}, token = null) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            
            const headers = { ...options.headers };
            if (!(options.body instanceof FormData)) {
                headers['Content-Type'] = 'application/json';
            }
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(url, {
                ...options,
                headers
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
    async getDocuments(token = null) {
        return this.request('/api/documents', {}, token);
    },

    async getDocument(docId, token = null) {
        return this.request(`/api/documents/${docId}`, {}, token);
    },

    async deleteDocument(docId, token = null) {
        return this.request(`/api/documents/${docId}`, { method: 'DELETE' }, token);
    },

    async uploadPdf(file, token = null) {
        const formData = new FormData();
        formData.append('file', file);
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const response = await fetch(`${this.baseUrl}/api/upload`, {
            method: 'POST',
            body: formData,
            headers
        });
        if (!response.ok) throw new Error('Upload failed');
        return response.json();
    },

    // Facts
    async getFacts(params = {}, token = null) {
        const query = new URLSearchParams();
        if (params.category) query.set('category', params.category);
        if (params.doc_id) query.set('doc_id', params.doc_id);
        if (params.min_confidence) query.set('min_confidence', params.min_confidence);
        if (params.dataset) query.set('dataset', params.dataset);
        const qs = query.toString();
        return this.request(`/api/facts${qs ? '?' + qs : ''}`, {}, token);
    },

    async getFact(factId, token = null) {
        return this.request(`/api/facts/${factId}`, {}, token);
    },

    async getCategories(token = null) {
        return this.request('/api/categories', {}, token);
    },

    // Relationships
    async getRelationships(relType = null, token = null) {
        const qs = relType ? `?rel_type=${relType}` : '';
        return this.request(`/api/relationships${qs}`, {}, token);
    },

    async getRelationshipStats(token = null) {
        return this.request('/api/relationships/stats', {}, token);
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
