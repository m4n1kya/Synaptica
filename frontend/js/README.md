# Frontend Architecture

This frontend is built entirely using Vanilla JavaScript, HTML5, and CSS3. 
We specifically avoid heavyweight frameworks (like React or Vue) to ensure maximum performance, zero build-step deployments, and absolute control over DOM animations via GSAP.

## Structure
- `api.js`: Handles all communication with the FastAPI backend.
- `app.js`: Main entry point and global state manager.
- `animations.js`: Contains GSAP timelines and complex transitions.
- `matrix-view.js`: Renders the extracted facts matrix.
- `PatternWaves.js`: Background WebGL animation component.
