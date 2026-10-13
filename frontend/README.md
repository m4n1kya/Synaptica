# Synaptica — Frontend Client

A zero-dependency, high-performance web client built with **Vanilla JavaScript (ES6+)**, **HTML5**, **CSS3**, **GSAP**, and **WebGL (OGL)**.

## Architecture & Design Philosophy

Synaptica intentionally avoids heavy SPA frameworks to achieve instant load times, zero build-step static deployment on Vercel's edge CDN, and fine-grained control over WebGL shaders and timeline animations.

### Module Structure

```text
frontend/
├── index.html              # Single-page application shell & view containers
├── demo.json               # Pre-computed static dataset for instant unauthenticated load
├── css/
│   ├── design-system.css   # Design tokens, typography, color palette, utilities
│   ├── layout.css          # Grid systems, navigation, responsive shells
│   ├── components.css      # Cards, badges, tables, modals, toast notifications
│   ├── hero.css            # Hero typography & viewport layout
│   └── animations.css      # Keyframes and transition utilities
└── js/
    ├── app.js              # Hash-based router, view lifecycle, auth controller
    ├── api.js              # REST API client with automatic Bearer token injection
    ├── storage.js          # Hybrid storage layer (Cloud Firestore + local IndexedDB + static demo)
    ├── PatternWaves.js     # Interactive WebGL2 shader surface (OGL)
    ├── animations.js       # GSAP timelines, counter animations, toast manager
    ├── upload.js           # Drag-and-drop PDF ingestion & real-time progress ticker
    ├── matrix-view.js      # Cross-document Source × Category pivot matrix
    ├── facts-panel.js      # Filterable atomic fact cards with source citations
    ├── evidence-viewer.js  # Side-by-side relationship & reconciliation inspector
    ├── graph-view.js       # Interactive HTML5 Canvas force-directed knowledge graph
    ├── analytics-view.js   # Chart.js distribution & confidence telemetry
    └── firebase-init.js    # Firebase Authentication initialization
```
