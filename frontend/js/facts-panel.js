/**
 * Synaptica — Facts Panel
 * Searchable, filterable fact explorer with category chips and confidence bars.
 */
const FactsPanel = {
    facts: [],
    categories: [],
    activeCategory: 'all',
    searchQuery: '',

    async render() {
        const grid = document.getElementById('facts-grid');
        if (grid) {
            grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 60px;"><div class="loading-spinner" style="margin: 0 auto 16px;"></div><div style="color: var(--text-muted);">Waking up AI engine & loading Extracted Facts...</div></div>';
        }

        try {
            this.facts = await API.getFacts();
            this.categories = await API.getCategories();
        } catch (e) {
            console.error('Facts load failed:', e);
            return;
        }

        this.setupFilters();
        this.setupSearch();
        this.renderFacts();
    },

    setupFilters() {
        const container = document.getElementById('facts-filters');
        if (!container) return;

        let html = '<button class="filter-chip active" data-category="all">All (${this.facts.length})</button>';
        html = `<button class="filter-chip active" data-category="all">All (${this.facts.length})</button>`;
        this.categories.forEach(cat => {
            html += `<button class="filter-chip" data-category="${cat.name}">${cat.name} (${cat.count})</button>`;
        });
        container.innerHTML = html;

        container.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                container.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                this.activeCategory = chip.dataset.category;
                this.renderFacts();
            });
        });
    },

    setupSearch() {
        const search = document.getElementById('facts-search');
        if (!search) return;
        let timeout;
        search.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.searchQuery = e.target.value.toLowerCase();
                this.renderFacts();
            }, 200);
        });
    },

    getFilteredFacts() {
        let filtered = this.facts;
        if (this.activeCategory !== 'all') {
            filtered = filtered.filter(f => f.category === this.activeCategory);
        }
        if (this.searchQuery) {
            filtered = filtered.filter(f =>
                f.statement.toLowerCase().includes(this.searchQuery) ||
                f.category.toLowerCase().includes(this.searchQuery) ||
                (f.evidence_text && f.evidence_text.toLowerCase().includes(this.searchQuery)) ||
                (f.source_doc_name && f.source_doc_name.toLowerCase().includes(this.searchQuery))
            );
        }
        return filtered;
    },

    renderFacts() {
        const grid = document.getElementById('facts-grid');
        if (!grid) return;

        const filtered = this.getFilteredFacts();

        if (filtered.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <div class="empty-icon"></div>
                    <h3>No facts found</h3>
                    <p>Try adjusting your filters or search query.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = filtered.map((fact, i) => {
            const confPercent = Math.round(fact.confidence * 100);
            const confClass = fact.confidence >= 0.9 ? 'confidence-high'
                : fact.confidence >= 0.7 ? 'confidence-medium' : 'confidence-low';

            return `
                <div class="fact-card" data-stagger style="animation-delay: ${i * 40}ms;" onclick="FactsPanel.showDetail('${fact.id}')">
                    <div class="fact-header">
                        <span class="badge badge-category">${fact.category}</span>
                        <span class="text-xs text-muted font-mono">${confPercent}%</span>
                    </div>
                    ${fact.value ? `<div class="fact-value">${fact.value}<span style="font-size: 0.6em; color: var(--text-muted); margin-left: 4px;">${fact.unit || ''}</span></div>` : ''}
                    <p class="fact-statement">${fact.statement}</p>
                    <div style="margin-top: var(--space-3);">
                        <div class="confidence-bar">
                            <div class="confidence-fill ${confClass}" style="width: ${confPercent}%"></div>
                        </div>
                    </div>
                    <div class="fact-meta">
                        <span>${this.truncate(fact.source_doc_name || '', 25)}</span>
                        ${fact.page_numbers?.length ? `<span>p. ${fact.page_numbers.join(', ')}</span>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        // Animate entry
        setTimeout(() => {
            grid.querySelectorAll('[data-stagger]').forEach((el, i) => {
                setTimeout(() => el.classList.add('entered'), i * 40);
            });
        }, 50);
    },

    showDetail(factId) {
        // Reuse the matrix popup style
        MatrixView.facts = this.facts;
        MatrixView.showFactDetail(factId);
    },

    truncate(str, len) {
        return str.length > len ? str.substring(0, len) + '…' : str;
    }
};
