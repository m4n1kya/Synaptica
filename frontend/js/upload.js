/**
 * Synaptica — Upload Manager
 * Drag-and-drop file upload with progress simulation.
 */
const UploadManager = {
    init() {
        this.loadHistory();
        
        this.setupDropzone('dropzone', 'file-input', 'browse-btn');
        this.setupDropzone('dropzone-home', 'file-input-home', 'browse-btn-home');
    },

    setupDropzone(dropzoneId, inputId, btnId) {
        const dropzone = document.getElementById(dropzoneId);
        const fileInput = document.getElementById(inputId);
        const browseBtn = document.getElementById(btnId);

        if (!dropzone) return;

        // Click to browse
        browseBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput?.click();
        });
        dropzone.addEventListener('click', () => fileInput?.click());

        // File input change
        fileInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                // If this is the home dropzone, switch to upload tab automatically
                if (dropzoneId === 'dropzone-home') {
                    window.location.hash = '#/upload';
                }
                this.handleFiles(Array.from(e.target.files));
            }
        });

        // Drag and drop
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf'));
            if (files.length > 0) {
                if (dropzoneId === 'dropzone-home') {
                    window.location.hash = '#/upload';
                }
                this.handleFiles(files);
            }
        });
    },

    queuedFiles: [],

    handleFiles(files) {
        this.queuedFiles = [...this.queuedFiles, ...files];
        this.renderQueue();
    },

    renderQueue() {
        const fileList = document.getElementById('upload-file-list');
        const progressSection = document.getElementById('upload-progress-section');

        if (this.queuedFiles.length === 0) {
            fileList.style.display = 'none';
            return;
        }

        fileList.style.display = 'block';
        fileList.innerHTML = `
            ${this.queuedFiles.map((f, index) => `
                <div class="file-item animate-fade-in" style="display:flex; justify-content:space-between; align-items:center; background: var(--bg-secondary); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--glass-border); margin-bottom: 8px;">
                    <div style="display:flex; align-items:center; gap: 12px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--text-muted);"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                        <div class="file-info">
                            <div class="file-name" style="font-weight: 500; font-size: 0.95rem;">${f.name}</div>
                            <div class="file-status text-muted text-xs" style="margin-top:2px;">${(f.size / 1024 / 1024).toFixed(1)} MB</div>
                        </div>
                    </div>
                    <button class="btn-remove-file" data-index="${index}" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; padding: 4px; transition: color 0.2s;">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                    </button>
                </div>
            `).join('')}
            <div style="margin-top: var(--space-4); text-align: right;">
                <button class="btn btn-primary" id="btn-start-processing">Process Files</button>
            </div>
        `;

        document.querySelectorAll('.btn-remove-file').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.currentTarget.dataset.index);
                this.queuedFiles.splice(index, 1);
                this.renderQueue();
            });
            btn.addEventListener('mouseover', (e) => e.currentTarget.style.color = 'var(--color-contradict)');
            btn.addEventListener('mouseout', (e) => e.currentTarget.style.color = 'var(--text-muted)');
        });

        document.getElementById('btn-start-processing').addEventListener('click', () => {
            progressSection.style.display = 'block';
            document.getElementById('btn-start-processing').style.display = 'none';
            document.querySelectorAll('.btn-remove-file').forEach(b => b.style.display = 'none');
            this.simulateProcessing(this.queuedFiles);
        });
    },

    async simulateProcessing(files) {
        const progressBar = document.getElementById('upload-progress-fill');
        const statusText = document.getElementById('upload-status-text');
        const percentageText = document.getElementById('upload-percentage');
        const steps = ['step-parse', 'step-extract', 'step-link', 'step-done'];

        const setProgress = (pct, stepIdx, text) => {
            if (progressBar) progressBar.style.width = pct + '%';
            if (percentageText) percentageText.textContent = pct + '%';
            if (statusText) statusText.textContent = text;
            steps.forEach((s, i) => {
                const el = document.getElementById(s);
                if (el) {
                    if (i < stepIdx) el.className = 'progress-step done';
                    else if (i === stepIdx) el.className = 'progress-step active';
                    else el.className = 'progress-step';
                }
            });
        };

        // Stage 1: Start upload
        setProgress(5, 0, `Uploading ${files[0].name} to server...`);

        // Animate progress while real upload runs concurrently
        const uploadPromise = StorageManager.uploadPdf(files[0]);

        // Fake progress ticker that advances during real upload
        const ticker = [
            { delay: 1500,  pct: 15, step: 0, text: 'Parsing PDF structure and extracting text...' },
            { delay: 4000,  pct: 30, step: 1, text: 'Sending to AI for fact extraction...' },
            { delay: 8000,  pct: 45, step: 1, text: 'Extracting atomic facts using Gemini AI...' },
            { delay: 20000, pct: 60, step: 1, text: 'Processing document chunks...' },
            { delay: 40000, pct: 72, step: 2, text: 'Discovering cross-document relationships...' },
            { delay: 60000, pct: 82, step: 2, text: 'Almost done — finalising knowledge graph...' },
            { delay: 80000, pct: 90, step: 2, text: 'Applying API rate-limit backoff (if needed)...' },
            { delay: 95000, pct: 96, step: 2, text: 'Waiting for final response from server...' },
        ];

        let done = false;
        uploadPromise.finally(() => { done = true; });

        for (const t of ticker) {
            await new Promise(r => setTimeout(r, t.delay - (ticker.indexOf(t) > 0 ? ticker[ticker.indexOf(t)-1].delay : 0)));
            if (done) break;
            setProgress(t.pct, t.step, t.text);
        }

        // Await the real result
        let result;
        try {
            result = await uploadPromise;
        } catch (e) {
            console.error('Upload failed:', e);
            Animations.showToast('Upload failed: ' + e.message, 'error');
            if (statusText) statusText.textContent = 'Upload Failed.';
            if (progressBar) progressBar.style.backgroundColor = 'var(--color-contradict)';
            return;
        }

        // Complete!
        setProgress(100, 3, 'Processing complete!');
        this.loadHistory();

        const factCount = result.fact_count || result.facts?.length || 0;
        if (factCount === 0) {
            Animations.showToast(`Uploaded — but 0 facts extracted. Try a text-based PDF.`, 'error');
        } else {
            Animations.showToast(`✓ ${result.filename || files[0].name} — ${factCount} facts extracted!`, 'success');
        }

        await new Promise(r => setTimeout(r, 1200));
        window.location.hash = '#/matrix';
        setTimeout(() => {
            if (window.MatrixView) MatrixView.render();
        }, 200);
        // Reset queue

        this.queuedFiles = [];
        this.renderQueue();
    },

    async loadHistory() {
        const historyList = document.getElementById('upload-history-list');
        if (!historyList) return;
        
        try {
            const docs = await StorageManager.getDocuments();
            if (!docs || docs.length === 0) {
                historyList.innerHTML = '<div class="text-center text-muted" style="padding: var(--space-6);">No documents uploaded yet.</div>';
                return;
            }
            
            historyList.innerHTML = docs.map(doc => `
                <div class="glass-card" style="display:flex; justify-content:space-between; align-items:center; padding: var(--space-3) var(--space-4);">
                    <div style="display:flex; align-items:center; gap: var(--space-3);">
                        <div style="color: var(--primary);">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        </div>
                        <div>
                            <div style="font-weight: 500;">${doc.filename}</div>
                            <div class="text-muted text-xs">Added: ${new Date(doc.upload_time).toLocaleDateString()} &middot; Facts: ${doc.fact_count}</div>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            historyList.innerHTML = '<div class="text-center text-muted" style="padding: var(--space-6); color: var(--color-contradict);">Failed to load history.</div>';
        }
    }
};
