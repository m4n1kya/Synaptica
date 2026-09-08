/**
 * Synaptica — Graph View
 * Force-directed graph visualization of facts and their relationships using Canvas.
 */
const GraphView = {
    canvas: null,
    ctx: null,
    facts: [],
    relationships: [],
    nodes: [],
    edges: [],
    width: 0,
    height: 0,
    animationId: null,
    isDragging: false,
    dragNode: null,
    hoverNode: null,
    mousePos: { x: 0, y: 0 },
    transform: { x: 0, y: 0, scale: 1 },

    async render() {
        const container = document.getElementById('graph-container');
        if (container) {
            container.innerHTML = '<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%;"><div class="loading-spinner" style="margin: 0 auto 16px;"></div><div style="color: var(--text-muted);">Waking up AI engine & building Graph...</div></div>';
        }

        try {
            this.facts = await API.getFacts();
            this.relationships = await API.getRelationships();
        } catch (e) {
            console.error('Graph data load failed:', e);
            return;
        }

        this.initCanvas();
        this.buildGraph();
        this.setupInteractions();
        this.startSimulation();
    },

    initCanvas() {
        this.canvas = document.getElementById('knowledge-graph-canvas');
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        const container = this.canvas.parentElement;
        
        const resize = () => {
            const rect = container.getBoundingClientRect();
            this.width = rect.width;
            this.height = rect.height;
            // Handle high DPI displays
            const dpr = window.devicePixelRatio || 1;
            this.canvas.width = this.width * dpr;
            this.canvas.height = this.height * dpr;
            this.ctx.scale(dpr, dpr);
            
            // Initial transform to center graph
            this.transform.x = this.width / 2;
            this.transform.y = this.height / 2;
        };

        window.addEventListener('resize', resize);
        resize();
    },

    buildGraph() {
        // Build nodes (facts that have relationships, plus a few isolated ones for context)
        const connectedFactIds = new Set();
        this.relationships.forEach(r => {
            connectedFactIds.add(r.fact_a_id);
            connectedFactIds.add(r.fact_b_id);
        });

        // Filter facts to mostly those with connections to keep graph clean
        const graphFacts = this.facts.filter(f => connectedFactIds.has(f.id)).slice(0, 50);

        this.nodes = graphFacts.map(fact => ({
            id: fact.id,
            fact: fact,
            x: (Math.random() - 0.5) * this.width,
            y: (Math.random() - 0.5) * this.height,
            vx: 0,
            vy: 0,
            radius: 8 + (fact.confidence * 4),
            color: this.getCategoryColor(fact.category)
        }));

        const nodeMap = new Map(this.nodes.map(n => [n.id, n]));

        // Build edges
        this.edges = [];
        this.relationships.forEach(rel => {
            const source = nodeMap.get(rel.fact_a_id);
            const target = nodeMap.get(rel.fact_b_id);
            if (source && target) {
                this.edges.push({
                    source: source,
                    target: target,
                    type: rel.relationship?.relationship_type || rel.relationship_type,
                    confidence: rel.relationship?.confidence || rel.confidence || 0.8
                });
            }
        });
    },

    getCategoryColor(category) {
        const colors = {
            'GDP Growth': '#3b82f6',
            'Inflation': '#ef4444',
            'Fiscal Policy': '#8b5cf6',
            'Trade': '#10b981',
            'Employment': '#f59e0b',
            'Financial Sector': '#06b6d4',
            'Corporate Information': '#6366f1',
            'Operations': '#8b5cf6',
            'Financials': '#10b981'
        };
        return colors[category] || '#94a3b8';
    },

    getEdgeColor(type) {
        const colors = {
            'corroborates': 'rgba(144, 202, 249, 0.7)',
            'contradicts': 'rgba(33, 150, 243, 0.7)',
            'contextual_difference': 'rgba(227, 242, 253, 0.7)',
            'extraction_failure': 'rgba(21, 101, 192, 0.7)'
        };
        return colors[type] || 'rgba(148, 163, 184, 0.4)';
    },

    startSimulation() {
        if (this.animationId) cancelAnimationFrame(this.animationId);

        const tick = () => {
            this.simulateForces();
            this.draw();
            this.animationId = requestAnimationFrame(tick);
        };
        tick();
    },

    simulateForces() {
        const ALPHA = 0.05; // Cooling factor
        const REPULSION = 1500;
        const SPRING_LENGTH = 100;
        const SPRING_STRENGTH = 0.02;

        // Apply repulsion
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const node1 = this.nodes[i];
                const node2 = this.nodes[j];
                const dx = node2.x - node1.x;
                const dy = node2.y - node1.y;
                let dist = Math.sqrt(dx * dx + dy * dy) || 1;
                
                if (dist < 300) {
                    const force = REPULSION / (dist * dist);
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    
                    node1.vx -= fx;
                    node1.vy -= fy;
                    node2.vx += fx;
                    node2.vy += fy;
                }
            }
        }

        // Apply attraction (edges)
        this.edges.forEach(edge => {
            const dx = edge.target.x - edge.source.x;
            const dy = edge.target.y - edge.source.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            
            const force = (dist - SPRING_LENGTH) * SPRING_STRENGTH * edge.confidence;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            
            edge.source.vx += fx;
            edge.source.vy += fy;
            edge.target.vx -= fx;
            edge.target.vy -= fy;
        });

        // Apply center gravity
        this.nodes.forEach(node => {
            node.vx -= node.x * 0.005;
            node.vy -= node.y * 0.005;
        });

        // Update positions with friction
        this.nodes.forEach(node => {
            if (node === this.dragNode) return;
            node.vx *= 0.85; // friction
            node.vy *= 0.85;
            node.x += node.vx * ALPHA;
            node.y += node.vy * ALPHA;
        });
    },

    draw() {
        if (!this.ctx) return;
        
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.ctx.save();
        
        // Apply transform (pan/zoom)
        this.ctx.translate(this.transform.x, this.transform.y);
        this.ctx.scale(this.transform.scale, this.transform.scale);

        // Draw edges
        this.edges.forEach(edge => {
            this.ctx.beginPath();
            this.ctx.moveTo(edge.source.x, edge.source.y);
            this.ctx.lineTo(edge.target.x, edge.target.y);
            this.ctx.strokeStyle = this.getEdgeColor(edge.type);
            this.ctx.lineWidth = edge.confidence * 2;
            
            // Highlight connected edges if hovering a node
            if (this.hoverNode && (edge.source === this.hoverNode || edge.target === this.hoverNode)) {
                this.ctx.lineWidth = 3;
                this.ctx.globalAlpha = 1;
            } else if (this.hoverNode) {
                this.ctx.globalAlpha = 0.2;
            } else {
                this.ctx.globalAlpha = 1;
            }
            
            this.ctx.stroke();
        });

        // Draw nodes
        this.nodes.forEach(node => {
            const isHovered = node === this.hoverNode;
            
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius * (isHovered ? 1.5 : 1), 0, Math.PI * 2);
            
            if (this.hoverNode && !isHovered && !this.isConnected(node, this.hoverNode)) {
                this.ctx.globalAlpha = 0.2;
            } else {
                this.ctx.globalAlpha = 1;
            }
            
            this.ctx.fillStyle = node.color;
            this.ctx.fill();
            
            // Node stroke
            this.ctx.lineWidth = isHovered ? 3 : 1;
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.stroke();

            // Label for hovered or connected nodes
            if (isHovered || (this.transform.scale > 1.5 && this.ctx.globalAlpha > 0.5)) {
                this.ctx.font = '10px Inter';
                this.ctx.fillStyle = '#ffffff';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(
                    this.truncate(node.fact.statement, 20), 
                    node.x, 
                    node.y + node.radius + 15
                );
            }
        });

        this.ctx.restore();
    },

    isConnected(nodeA, nodeB) {
        return this.edges.some(e => 
            (e.source === nodeA && e.target === nodeB) || 
            (e.source === nodeB && e.target === nodeA)
        );
    },

    setupInteractions() {
        if (!this.canvas) return;

        let lastMousePos = { x: 0, y: 0 };
        let isPanning = false;

        const getMousePos = (e) => {
            const rect = this.canvas.getBoundingClientRect();
            return {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
        };

        const getTransformedPos = (pos) => {
            return {
                x: (pos.x - this.transform.x) / this.transform.scale,
                y: (pos.y - this.transform.y) / this.transform.scale
            };
        };

        // Hover & Tooltip
        const tooltip = document.getElementById('graph-tooltip');
        
        this.canvas.addEventListener('mousemove', (e) => {
            this.mousePos = getMousePos(e);
            const tPos = getTransformedPos(this.mousePos);

            if (this.isDragging && this.dragNode) {
                this.dragNode.x = tPos.x;
                this.dragNode.y = tPos.y;
                return;
            }

            if (isPanning) {
                this.transform.x += this.mousePos.x - lastMousePos.x;
                this.transform.y += this.mousePos.y - lastMousePos.y;
                lastMousePos = this.mousePos;
                return;
            }

            // Find hovered node
            let found = null;
            for (let i = this.nodes.length - 1; i >= 0; i--) {
                const node = this.nodes[i];
                const dx = tPos.x - node.x;
                const dy = tPos.y - node.y;
                if (dx * dx + dy * dy < (node.radius * 2) * (node.radius * 2)) {
                    found = node;
                    break;
                }
            }

            this.hoverNode = found;
            this.canvas.style.cursor = found ? 'pointer' : (isPanning ? 'grabbing' : 'grab');

            // Show tooltip
            if (found && tooltip) {
                tooltip.style.display = 'block';
                tooltip.style.left = (this.mousePos.x + 15) + 'px';
                tooltip.style.top = (this.mousePos.y + 15) + 'px';
                tooltip.innerHTML = `
                    <div style="font-weight:600; margin-bottom:4px;">${found.fact.category}</div>
                    <div style="color:var(--text-secondary); margin-bottom:4px;">${this.truncate(found.fact.statement, 60)}</div>
                    <div style="color:var(--text-muted); font-size:0.85em;">${found.fact.source_doc_name}</div>
                `;
            } else if (tooltip) {
                tooltip.style.display = 'none';
            }
        });

        // Dragging & Panning
        this.canvas.addEventListener('mousedown', (e) => {
            this.mousePos = getMousePos(e);
            lastMousePos = this.mousePos;
            
            if (this.hoverNode) {
                this.isDragging = true;
                this.dragNode = this.hoverNode;
                // Zero out velocity when dragging
                this.dragNode.vx = 0;
                this.dragNode.vy = 0;
            } else {
                isPanning = true;
                this.canvas.style.cursor = 'grabbing';
            }
        });

        window.addEventListener('mouseup', () => {
            this.isDragging = false;
            this.dragNode = null;
            isPanning = false;
            if (this.canvas) this.canvas.style.cursor = this.hoverNode ? 'pointer' : 'grab';
        });

        // Zooming
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomSensitivity = 0.001;
            const delta = -e.deltaY * zoomSensitivity;
            const newScale = Math.max(0.2, Math.min(4, this.transform.scale * Math.exp(delta)));
            
            // Zoom centered on mouse
            const pos = getMousePos(e);
            this.transform.x = pos.x - (pos.x - this.transform.x) * (newScale / this.transform.scale);
            this.transform.y = pos.y - (pos.y - this.transform.y) * (newScale / this.transform.scale);
            this.transform.scale = newScale;
        });
    },

    truncate(str, len) {
        if (!str) return '';
        return str.length > len ? str.substring(0, len) + '…' : str;
    },

    stop() {
        if (this.animationId) cancelAnimationFrame(this.animationId);
    }
};
