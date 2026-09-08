/**
 * Synaptica — Evidence Viewer
 * Renders relationship cards, case studies, and evidence comparisons.
 */
const EvidenceViewer = {
    relationships: [],
    cases: [],
    activeType: 'all',

    // ── Relationships View ──────────────────────────────────
    async renderRelationships() {
        const list = document.getElementById('relationships-list');
        if (list) {
            list.innerHTML = '<div style="text-align: center; padding: 60px;"><div class="loading-spinner" style="margin: 0 auto 16px;"></div><div style="color: var(--text-muted);">Waking up AI engine & loading Relationships...</div></div>';
        }

        try {
            this.relationships = await API.getRelationships();
        } catch (e) {
            console.error('Relationships load failed:', e);
            return;
        }

        this.setupRelTabs();
        this.renderRelList();
    },

    setupRelTabs() {
        const tabs = document.getElementById('rel-type-tabs');
        if (!tabs) return;
        tabs.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                tabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.activeType = btn.dataset.type;
                this.renderRelList();
            });
        });
    },

    renderRelList() {
        const container = document.getElementById('relationships-list');
        if (!container) return;

        let filtered = this.relationships;
        if (this.activeType !== 'all') {
            filtered = filtered.filter(r => r.relationship?.relationship_type === this.activeType);
        }

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"></div>
                    <h3>No relationships found</h3>
                    <p>Adjust your filter to see different relationship types.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = filtered.map((item, i) => {
            return this.renderRelationshipCard(item.relationship, item.fact_a, item.fact_b, i);
        }).join('');

        // Animate
        setTimeout(() => Animations.observeNewElements(), 100);
    },

    renderRelationshipCard(rel, factA, factB, index) {
        if (!rel || !factA || !factB) return '';

        const typeLabels = {
            'corroborates': { label: 'Corroboration', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>', badge: 'badge-corroborate' },
            'contradicts': { label: 'Contradiction', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>', badge: 'badge-contradict' },
            'contextual_difference': { label: 'Variation', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>', badge: 'badge-contextual' },
            'extraction_failure': { label: 'Processing Error', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>', badge: 'badge-failure' }
        };

        const typeInfo = typeLabels[rel.relationship_type] || typeLabels['contextual_difference'];
        const colorMap = {
            'corroborates': 'var(--color-corroborate)',
            'contradicts': 'var(--color-contradict)',
            'contextual_difference': 'var(--color-contextual)',
            'extraction_failure': 'var(--color-failure)'
        };
        const relColor = colorMap[rel.relationship_type] || 'var(--color-contextual)';

        return `
        <div class="relationship-card rel-type-${rel.relationship_type} reveal" style="margin-bottom: var(--space-6); animation-delay: ${index * 100}ms;">
            <div class="rel-header" style="align-items: flex-start; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
                <div style="width: 100%; display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="font-size: 1.75rem; font-weight: 700; letter-spacing: 0; text-transform: uppercase; margin: 0; color: ${relColor}; line-height: 1;">
                        ${typeInfo.label}
                    </h3>
                    <div class="text-xs text-muted" style="font-family: monospace; letter-spacing: 0.05em; opacity: 0.6;">CONFIDENCE ${Math.round(rel.confidence * 100)}%</div>
                </div>
            </div>

            <div class="facts-comparison">
                <div class="comparison-fact">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span class="badge badge-doc">${this.truncate(factA.source_doc_name || '', 30)}</span>
                        ${factA.page_numbers?.length ? `<span class="text-xs text-muted">p. ${factA.page_numbers.join(', ')}</span>` : ''}
                    </div>
                    ${factA.value ? `<div style="font-family: var(--font-mono); font-size: 1.3rem; font-weight: 700; color: var(--text-primary); margin: 6px 0;">${factA.value} ${factA.unit || ''}</div>` : ''}
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 8px;">${factA.statement}</p>
                    <div class="evidence-block">
                        "${factA.evidence_text}"
                        ${factA.context?.time_period ? `<span class="evidence-source">${factA.context.time_period} · ${factA.context.methodology || ''}</span>` : ''}
                    </div>
                </div>

                <div class="comparison-connector">
                    <div class="connector-line"></div>
                </div>

                <div class="comparison-fact">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span class="badge badge-doc">${this.truncate(factB.source_doc_name || '', 30)}</span>
                        ${factB.page_numbers?.length ? `<span class="text-xs text-muted">p. ${factB.page_numbers.join(', ')}</span>` : ''}
                    </div>
                    ${factB.value ? `<div style="font-family: var(--font-mono); font-size: 1.3rem; font-weight: 700; color: var(--text-primary); margin: 6px 0;">${factB.value} ${factB.unit || ''}</div>` : ''}
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 8px;">${factB.statement}</p>
                    <div class="evidence-block">
                        "${factB.evidence_text}"
                        ${factB.context?.time_period ? `<span class="evidence-source">${factB.context.time_period} · ${factB.context.methodology || ''}</span>` : ''}
                    </div>
                </div>
            </div>

            <div class="reasoning-box">
                <h5><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px; vertical-align:text-top;"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg> System Reasoning</h5>
                <p>${rel.explanation}</p>
                ${rel.reconciliation ? `<p style="margin-top: 8px; color: var(--color-contextual);"><strong>Reconciliation:</strong> ${rel.reconciliation}</p>` : ''}
            </div>
        </div>
        `;
    },

    // ── Cases View ──────────────────────────────────────────
    async renderCases() {
        const grid = document.getElementById('cases-grid');
        if (grid) {
            grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 60px;"><div class="loading-spinner" style="margin: 0 auto 16px;"></div><div style="color: var(--text-muted);">Waking up AI engine & loading Cases...</div></div>';
        }

        try {
            this.cases = await API.getCases();
        } catch (e) {
            console.error('Cases load failed:', e);
            return;
        }

        const container = document.getElementById('cases-grid');
        if (!container) return;

        const typeConfig = {
            'corroboration': { color: 'var(--color-corroborate)', bgColor: 'var(--color-corroborate-bg)', badgeClass: 'badge-corroborate', label: 'Case 1: Corroboration' },
            'contradiction': { color: 'var(--color-contradict)', bgColor: 'var(--color-contradict-bg)', badgeClass: 'badge-contradict', label: 'Case 2: Contradiction' },
            'contextual': { color: 'var(--color-contextual)', bgColor: 'var(--color-contextual-bg)', badgeClass: 'badge-contextual', label: 'Case 3: Variation' },
            'extraction_failure': { color: 'var(--color-failure)', bgColor: 'var(--color-failure-bg)', badgeClass: 'badge-failure', label: 'Case 4: Processing Error' }
        };

        container.innerHTML = this.cases.map((cs, i) => {
            const config = typeConfig[cs.case_type] || typeConfig['contextual'];
            return `
            <div class="case-card reveal" style="animation-delay: ${i * 100}ms; border: 1px solid var(--glass-border); border-left: 4px solid ${config.color}; border-radius: var(--radius-lg); background: var(--glass-bg); margin-bottom: var(--space-4); cursor: pointer; padding: var(--space-6); transition: transform 0.2s, box-shadow 0.2s;" onclick="EvidenceViewer.openCaseModal('${cs.id}')" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none'">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="font-size: 1.75rem; font-weight: 700; letter-spacing: 0; text-transform: uppercase; margin: 0 0 8px 0; color: ${config.color}; line-height: 1;">${config.label}</h3>
                        <h2 style="font-size: 1.4rem; font-weight: 500; margin: 0 0 16px 0; color: var(--text-primary); letter-spacing: -0.01em; line-height: 1.4;">${cs.title}</h2>
                        <p style="color: var(--text-secondary); margin: 0; line-height: 1.6; font-size: 0.95rem;">${cs.summary}</p>
                    </div>
                    <div style="color: var(--text-muted); opacity: 0.6; padding-left: 16px;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                    </div>
                </div>
            </div>
            `;
        }).join('');

        setTimeout(() => Animations.observeNewElements(), 100);
    },

    openCaseModal(caseId) {
        const cs = this.cases.find(c => c.id === caseId);
        if (!cs) return;

        /* Semantic colors - Blue Monochromatic Palette */
        const typeConfig = {
            'corroboration': { color: '#90CAF9', bgColor: 'rgba(144, 202, 249, 0.08)', border: 'rgba(144, 202, 249, 0.25)', label: 'Corroboration' },
            'contradiction': { color: '#2196F3', bgColor: 'rgba(33, 150, 243, 0.08)', border: 'rgba(33, 150, 243, 0.25)', label: 'Contradiction' },
            'contextual': { color: '#E3F2FD', bgColor: 'rgba(227, 242, 253, 0.08)', border: 'rgba(227, 242, 253, 0.25)', label: 'Variation' },
            'extraction_failure': { color: '#1565C0', bgColor: 'rgba(21, 101, 192, 0.2)', border: 'rgba(21, 101, 192, 0.5)', label: 'Processing Error' }
        };
        const config = typeConfig[cs.case_type] || typeConfig['contextual'];

        const existing = document.querySelector('.case-modal-overlay');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.className = 'case-modal-overlay';
        overlay.style.cssText = `position: fixed; inset: 0; background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); z-index: 1000; display: flex; justify-content: center; align-items: center; padding: 20px;`;

        const modal = document.createElement('div');
        modal.style.cssText = `background: var(--bg-primary); border: 1px solid var(--glass-border); border-top: 4px solid ${config.color}; border-radius: var(--radius-xl); width: 100%; max-width: 900px; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-xl); animation: scaleIn 0.2s var(--ease-out); position: relative;`;

        modal.innerHTML = `
            <button class="btn-close" style="position: absolute; top: 20px; right: 20px; background: transparent; border: none; color: var(--text-muted); font-size: 1.5rem; cursor: pointer; padding: 8px; line-height: 1;" onclick="this.closest('.case-modal-overlay').remove()">✕</button>
            <div style="padding: 40px;">
                <h3 style="font-size: 2rem; font-weight: 700; letter-spacing: 0; text-transform: uppercase; margin: 0 0 12px 0; color: ${config.color}; line-height: 1;">${config.label}</h3>
                <h2 style="font-size: 1.75rem; font-weight: 500; margin: 0 0 24px 0; color: var(--text-primary); letter-spacing: -0.02em; line-height: 1.3;">${cs.title}</h2>
                <p style="color: var(--text-secondary); margin-bottom: 40px; line-height: 1.7; font-size: 1.05rem;">${cs.summary}</p>

                ${cs.facts.length > 0 ? `
                <h4 style="margin-bottom: 20px; font-size: 1.1rem; color: var(--text-primary); border-bottom: 1px solid var(--glass-border); padding-bottom: 8px;">Extracted Facts</h4>
                <div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 40px;">
                    ${cs.facts.map(f => `
                        <div style="background: var(--bg-secondary); border: 1px solid var(--glass-border); border-radius: var(--radius-md); padding: 20px;">
                            <span class="badge badge-doc" style="margin-bottom: 12px; display: inline-block;">${f.source_doc_name || ''}</span>
                            ${f.value ? `<div style="font-family:var(--font-mono); font-size:1.3rem; font-weight:700; color:var(--text-primary); margin-bottom: 8px;">${f.value} ${f.unit || ''}</div>` : ''}
                            <p style="font-size:0.95rem; color:var(--text-secondary); margin-bottom: 12px;">${f.statement}</p>
                            <div class="evidence-block" style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 4px; font-size: 0.85rem; border-left: 2px solid var(--text-muted);">
                                <em>"${f.evidence_text}"</em>
                                ${f.context?.time_period ? `<div style="margin-top: 8px; color: var(--text-muted);">${f.context.time_period}</div>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
                ` : ''}

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: var(--radius-md); padding: 24px;">
                        <h5 style="margin: 0 0 16px 0; font-size: 0.9rem; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.1em; display: flex; align-items: center; gap: 8px;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg> 
                            Evidence Analysis
                        </h5>
                        <p style="margin: 0; color: var(--text-secondary); line-height: 1.6; font-size: 0.95rem;">${cs.evidence_analysis}</p>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: var(--radius-md); padding: 24px;">
                        <h5 style="margin: 0 0 16px 0; font-size: 0.9rem; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.1em; display: flex; align-items: center; gap: 8px;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect></svg> 
                            System Reasoning
                        </h5>
                        <p style="margin: 0; color: var(--text-secondary); line-height: 1.6; font-size: 0.95rem;">${cs.system_reasoning}</p>
                    </div>
                </div>
            </div>
        `;

        overlay.appendChild(modal);
        
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });

        document.body.appendChild(overlay);
    },

    truncate(str, len) {
        return str.length > len ? str.substring(0, len) + '…' : str;
    }
};
