/**
 * Synaptica — Matrix View
 * Hebbia-inspired document × category grid for cross-referencing facts.
 */
const MatrixView = {
    facts: [],
    documents: [],
    activeDataset: 'all',

    async render() {
        const table = document.getElementById('matrix-table');
        if (table) {
            table.innerHTML = '<tbody><tr><td colspan="5" class="text-center" style="padding: 60px;"><div class="loading-spinner" style="margin: 0 auto 16px;"></div><div style="color: var(--text-muted);">Waking up AI engine & loading Knowledge Matrix...</div></td></tr></tbody>';
        }

        try {
            this.facts = await API.getFacts();
            this.documents = await API.getDocuments();
        } catch (e) {
            console.error('Matrix data load failed:', e);
            return;
        }

        this.setupTabs();
        this.buildMatrix();
    },

    setupTabs() {
        const tabContainer = document.getElementById('matrix-dataset-tabs');
        if (!tabContainer) return;
        tabContainer.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                tabContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.activeDataset = btn.dataset.dataset;
                this.buildMatrix();
            });
        });
    },

    buildMatrix() {
        const table = document.getElementById('matrix-table');
        if (!table) return;

        // Filter by dataset
        let docs = this.documents;
        let facts = this.facts;
        if (this.activeDataset !== 'all') {
            docs = docs.filter(d => d.dataset === this.activeDataset);
            const docIds = new Set(docs.map(d => d.id));
            facts = facts.filter(f => docIds.has(f.source_doc_id));
        }

        // Get unique categories
        const categories = [...new Set(facts.map(f => f.category))].sort();

        // Build facts lookup: doc_id -> category -> facts[]
        const lookup = {};
        facts.forEach(f => {
            if (!lookup[f.source_doc_id]) lookup[f.source_doc_id] = {};
            if (!lookup[f.source_doc_id][f.category]) lookup[f.source_doc_id][f.category] = [];
            lookup[f.source_doc_id][f.category].push(f);
        });

        // Build HTML
        let html = '<thead><tr><th class="doc-cell">Document</th>';
        categories.forEach(cat => {
            html += `<th>${cat}</th>`;
        });
        html += '</tr></thead><tbody>';

        docs.forEach(doc => {
            html += `<tr>`;
            html += `<td class="doc-cell">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1.2rem;"></span>
                    <div style="flex:1;">
                        <div style="font-size: 0.8rem; font-weight: 600;">${doc.original_filename || doc.filename}</div>
                        <div style="font-size: 0.7rem; color: var(--text-muted);">${doc.fact_count} facts · ${doc.page_count} pages</div>
                    </div>
                    <button class="btn-remove-doc" onclick="MatrixView.deleteDocument('${doc.id}')" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; padding: 4px; border-radius: 4px; transition: color 0.2s;" onmouseover="this.style.color='var(--color-contradict)'" onmouseout="this.style.color='var(--text-muted)'" title="Remove Document">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                    </button>
                </div>
            </td>`;

            categories.forEach(cat => {
                const cellFacts = (lookup[doc.id] && lookup[doc.id][cat]) || [];
                if (cellFacts.length === 0) {
                    html += `<td><span class="text-muted" style="font-size:0.75rem;">—</span></td>`;
                } else {
                    const topFact = cellFacts[0];
                    const displayValue = topFact.value
                        ? `${topFact.value}${topFact.unit ? ' ' + topFact.unit : ''}`
                        : '';
                    html += `<td>
                        <div class="matrix-cell-content" data-factid="${topFact.id}" style="cursor:pointer;" onclick="MatrixView.showFactDetail('${topFact.id}')">
                            ${displayValue ? `<div class="matrix-cell-value">${displayValue}</div>` : ''}
                            <div class="matrix-cell-count">${cellFacts.length} fact${cellFacts.length > 1 ? 's' : ''}</div>
                        </div>
                    </td>`;
                }
            });

            html += '</tr>';
        });

        html += '</tbody>';
        table.innerHTML = html;
    },

    showFactDetail(factId) {
        const fact = this.facts.find(f => f.id === factId);
        if (!fact) return;

        // Create a mini tooltip/modal showing fact details
        const existing = document.querySelector('.matrix-detail-popup');
        if (existing) existing.remove();

        const popup = document.createElement('div');
        popup.className = 'matrix-detail-popup';
        popup.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: var(--bg-secondary); border: 1px solid var(--glass-border);
            border-radius: var(--radius-xl); padding: 2rem; max-width: 500px; width: 90%;
            z-index: 1000; box-shadow: var(--shadow-xl);
            animation: scaleIn 0.2s var(--ease-out);
        `;

        const confClass = fact.confidence >= 0.9 ? 'confidence-high' : fact.confidence >= 0.7 ? 'confidence-medium' : 'confidence-low';

        popup.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 1rem;">
                <span class="badge badge-category">${fact.category}</span>
                <button onclick="this.closest('.matrix-detail-popup').remove(); document.querySelector('.matrix-backdrop')?.remove();" class="btn-icon" style="font-size: 1rem;">✕</button>
            </div>
            ${fact.value ? `<div class="fact-value">${fact.value} ${fact.unit || ''}</div>` : ''}
            <p style="color: var(--text-primary); font-size: 0.95rem; margin: 0.75rem 0;">${fact.statement}</p>
            <div class="evidence-block">
                "${fact.evidence_text}"
                <span class="evidence-source">${fact.source_doc_name} · Page${fact.page_numbers?.length > 1 ? 's' : ''} ${fact.page_numbers?.join(', ') || '?'}</span>
            </div>
            <div style="margin-top: 1rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; color: var(--text-muted); margin-bottom: 4px;">
                    <span>Confidence</span>
                    <span>${Math.round(fact.confidence * 100)}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill ${confClass}" style="width: ${fact.confidence * 100}%"></div>
                </div>
            </div>
            ${fact.context ? `
                <div style="margin-top: 1rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
                    ${fact.context.time_period ? `<span class="badge badge-doc">${fact.context.time_period}</span>` : ''}
                    ${fact.context.scope ? `<span class="badge badge-doc">🎯 ${fact.context.scope}</span>` : ''}
                </div>
            ` : ''}
        `;

        // Backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'matrix-backdrop';
        backdrop.style.cssText = `
            position: fixed; inset: 0; background: rgba(0,0,0,0.6);
            z-index: 999; backdrop-filter: blur(4px);
        `;
        backdrop.addEventListener('click', () => {
            popup.remove();
            backdrop.remove();
        });

        document.body.appendChild(backdrop);
        document.body.appendChild(popup);
    },

    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to remove this document and all its extracted facts from the knowledge base?')) return;
        
        try {
            await API.deleteDocument(docId);
            if (window.Animations) Animations.showToast('Document removed successfully', 'success');
            // Re-render
            this.render();
            // Optional: update global stats in app.js
            if (window.App && App.updateGlobalStats) App.updateGlobalStats();
        } catch (e) {
            if (window.Animations) Animations.showToast('Failed to remove document', 'error');
            console.error(e);
        }
    }
};
