# Synaptica

Synaptica is an AI-powered fact knowledge layer designed to transform scattered documentary evidence into connected, actionable intelligence. By processing unstructured data (such as financial reports, legal contracts, and macroeconomic surveys), Synaptica extracts atomic assertions, links related entities, and highlights discrepancies across a corpus of documents.

## Core Capabilities

*   **Knowledge Matrix**: A centralized dashboard that provides an overview of all processed documents, their extracted schemas, and the specific facts identified within them.
*   **Fact Extraction**: Automated identification of individual data points, complete with source context, confidence scores, and precise document attribution.
*   **Relationships and Conflicts**: Cross-document analysis that automatically identifies how facts across different documents corroborate or contradict each other.
*   **Resolved Cases**: AI-generated syntheses of conflicting or corroborating evidence, allowing analysts to quickly resolve data variations.
*   **Analytics and Visualization**: Interactive charting (including Area, Donut, and Bar charts) and data aggregation for high-level intelligence reporting.

## Technology Stack

### Frontend
*   **Architecture**: Vanilla HTML5, CSS3, and JavaScript (ES6+).
*   **Design System**: Custom CSS variables, glassmorphism UI principles, and fully responsive layouts.
*   **Visualization**: Chart.js for data analytics.
*   **Animation**: GSAP (GreenSock Animation Platform) for high-performance UI transitions and state changes.

### Backend
*   **Framework**: FastAPI (Python 3).
*   **Data Processing**: Extensible Python modules for PDF parsing, text extraction, and entity linking.
*   **Storage**: In-memory knowledge store (designed for extensibility to vector databases).

## Installation and Setup

### Prerequisites
*   Python 3.9 or higher
*   Node.js and npm (optional, for local development servers)

### Backend Setup
1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Start the FastAPI server:
    ```bash
    python main.py
    ```
    The backend API will run by default on `http://localhost:8000`.

### Frontend Setup
The frontend is built with vanilla web technologies and can be served using any static file server.

1.  Navigate to the project root directory:
    ```bash
    cd frontend
    ```
2.  Serve the application (using Python's built-in HTTP server as an example):
    ```bash
    python -m http.server 8080
    ```
3.  Access the application in your web browser at `http://localhost:8080`.

## Architecture Overview

Synaptica operates on a dual-layer architecture. The Python-based backend handles the heavy lifting of document ingestion, NLP processing, and relationship mapping. It exposes a clean REST API that the lightweight vanilla JavaScript frontend consumes. 

The frontend implements a custom single-page application (SPA) router, efficiently managing state across the Knowledge Matrix, Facts Panel, Evidence Viewer, and Analytics Dashboard without relying on heavy frameworks.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or modification is strictly prohibited.
