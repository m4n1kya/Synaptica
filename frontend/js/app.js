/**
 * Synaptica — Main Application Logic
 * Handles routing, initialization, and global state.
 */

const Auth = {
    openModal(mode) {
        const modal = document.getElementById('auth-modal');
        if (!modal) return;
        this.switchMode(mode);
        modal.classList.add('active');
    },
    
    closeModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) modal.classList.remove('active');
    },
    
    switchMode(mode) {
        const title = document.getElementById('auth-title');
        const switchText = document.getElementById('auth-switch-text');
        const submitBtn = document.getElementById('auth-submit-btn');
        
        if (mode === 'signup') {
            title.innerText = 'Sign up for Synaptica';
            submitBtn.innerText = 'Create Account';
            switchText.innerHTML = 'Already have an account? <a href="#" onclick="Auth.switchMode(\'signin\')">Log in</a>';
        } else {
            title.innerText = 'Log in to Synaptica';
            submitBtn.innerText = 'Continue';
            switchText.innerHTML = 'Logging in for the first time? <a href="#" onclick="Auth.switchMode(\'signup\')">Sign up</a>';
        }
    }
};

/**
 * Synaptica — Main Application Controller
 * Handles routing, state management, and initialization.
 */
const App = {
    zoomLevel: 90,

    async init() {
        // Initialize global zoom
        this.initZoom();

        // Initialize global animations
        Animations.init();

        // Initialize Views
        window.analyticsView = new AnalyticsView();

        // Initialize Upload Manager
        UploadManager.init();

        // Setup Routing
        this.setupRouter();
        
        // Handle initial route
        this.handleRoute();

        // Load Global Stats
        this.updateGlobalStats();
    },

    initZoom() {
        this.applyZoom();
    },
    
    applyZoom() {
        // Remove legacy zoom if it exists
        document.body.style.zoom = '';
        
        // Use root font-size scaling so it elegantly scales REM-based UI
        // without breaking VW/VH layout of the cinematic hero screen.
        document.documentElement.style.fontSize = `${this.zoomLevel}%`;
        
        // Re-trigger scroll observer to ensure elements are rendered correctly
        if (window.Animations && window.Animations.observeNewElements) {
            setTimeout(() => window.Animations.observeNewElements(), 100);
        }
    },

    setupRouter() {
        window.addEventListener('hashchange', () => this.handleRoute());
        
        // Setup navbar links
        document.querySelectorAll('.nav-item').forEach(link => {
            link.addEventListener('click', (e) => {
                // Let the hashchange handle it, but update active state immediately for snappiness
                document.querySelectorAll('.nav-item').forEach(l => l.classList.remove('active'));
                e.currentTarget.classList.add('active');
            });
        });
    },

    handleRoute() {
        const hash = window.location.hash || '#/';
        const viewName = hash === '#/' ? 'landing' : hash.replace('#/', '');
        
        this.switchView(viewName);
    },

    switchView(viewName) {
        // Stop animations from previous views
        if (viewName !== 'landing') Animations.stopHeroAnimation();
        if (viewName !== 'graph') GraphView.stop();

        // Hide all views
        document.querySelectorAll('.view-container').forEach(view => {
            view.classList.remove('active');
        });

        // Update Nav
        document.querySelectorAll('.nav-item').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.view === viewName) {
                link.classList.add('active');
            }
        });

        // Show requested view
        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            targetView.classList.add('active');
            
            // Trigger specific view logic
            switch (viewName) {
                case 'landing':
                    Animations.initHeroCanvas();
                    Animations.animateCounters();
                    break;
                case 'matrix':
                    MatrixView.render();
                    break;
                case 'facts':
                    FactsPanel.render();
                    break;
                case 'relationships':
                    EvidenceViewer.renderRelationships();
                    break;
                case 'cases':
                    EvidenceViewer.renderCases();
                    break;
                case 'analytics':
                    if (window.analyticsView) window.analyticsView.init(API);
                    break;
                default:
                    break;
            }
            
            // Trigger scroll reveal for new view elements
            setTimeout(() => Animations.observeNewElements(), 100);
            window.scrollTo(0, 0);
        } else {
            console.error(`View not found: ${viewName}`);
            // Fallback to landing
            document.getElementById('landing-view').classList.add('active');
            Animations.initHeroCanvas();
        }
    },

    async updateGlobalStats() {
        try {
            const stats = await API.getStats();
            
            const factsEl = document.getElementById('stat-facts');
            const relsEl = document.getElementById('stat-relationships');
            const docsEl = document.getElementById('stat-documents');
            
            if (factsEl) factsEl.setAttribute('data-target', stats.total_facts);
            if (relsEl) relsEl.setAttribute('data-target', stats.total_relationships);
            if (docsEl) docsEl.setAttribute('data-target', stats.total_documents);
            
            // Only animate if we're on the landing page
            if (window.location.hash === '' || window.location.hash === '#/') {
                Animations.animateCounters();
            }
        } catch (e) {
            console.error("Failed to load global stats:", e);
        }
    }
};

// Start application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    API.wakeUpBackend(); // Wake up the Render backend in the background
    App.init();
});
