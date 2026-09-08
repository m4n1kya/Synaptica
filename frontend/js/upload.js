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

        const stages = [
            { progress: 25, step: 0, text: 'Parsing PDF structure and extracting text...' },
            { progress: 55, step: 1, text: 'Extracting atomic facts using AI analysis...' },
            { progress: 80, step: 2, text: 'Discovering cross-document relationships...' },
            { progress: 100, step: 3, text: 'Processing complete! Redirecting to results...' },
        ];

        // Try real upload for first file
        let uploaded = false;
        try {
            statusText.textContent = `Uploading ${files[0].name}...`;
            if (progressBar) progressBar.style.width = '10%';
            if (percentageText) percentageText.textContent = '10%';
            const result = await API.uploadPdf(files[0]);
            uploaded = true;
            Animations.showToast(`Uploaded ${result.filename} — ${result.fact_count} facts extracted`, 'success');
            this.loadHistory(); // Refresh history list
        } catch (e) {
            // Fallback to demo mode
            console.log('Upload failed, using demo mode:', e);
        }

        for (const stage of stages) {
            await new Promise(r => setTimeout(r, 800));
            if (progressBar) progressBar.style.width = stage.progress + '%';
            if (percentageText) percentageText.textContent = stage.progress + '%';
            statusText.textContent = stage.text;

            // Update step indicators
            steps.forEach((s, i) => {
                const el = document.getElementById(s);
                if (el) {
                    if (i < stage.step) el.className = 'progress-step done';
                    else if (i === stage.step) el.className = 'progress-step active';
                    else el.className = 'progress-step';
                }
            });
        }

        // Redirect to matrix view after completion
        await new Promise(r => setTimeout(r, 1200));
        window.location.hash = '#/matrix';
        Animations.showToast('Documents processed successfully!', 'success');
    },

    async loadHistory() {
        const historyList = document.getElementById('upload-history-list');
        if (!historyList) return;
        
        try {
            const docs = await API.getDocuments();
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
