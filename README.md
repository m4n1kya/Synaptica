# Synaptica: AI-Powered Fact Knowledge Layer

Synaptica is an AI-powered fact knowledge layer designed to transform scattered documentary evidence into connected, actionable intelligence. Built for the Superjoin VIT 2026 Engineering Intern Hiring Assignment.

## Setup and Run Instructions

### Prerequisites
*   Python 3.9 or higher

### Local Setup
1.  **Clone the repository and enter the backend directory:**
    ```bash
    cd backend
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Start the server:**
    ```bash
    uvicorn main:app --reload
    ```
    *(The backend API and the frontend UI will run simultaneously at `http://localhost:8000`)*

### Live Deployment
The application is continuously deployed and can be viewed live at: **[Insert Your Render Link Here]**

## Approach

*   **Architecture**: Synaptica operates on a dual-layer architecture. A lightweight Python/FastAPI backend handles document ingestion, NLP processing, and relationship mapping. A vanilla HTML5/JS/CSS frontend (without heavy frameworks like React) consumes the REST API.
*   **AI Tools**: The system leverages **Google's Gemini 1.5 Flash API** to dynamically extract structured facts from uploaded PDFs, assign confidence scores, and perform cross-document pairwise comparisons to find corroborations or contradictions. 
*   **Trade-offs & Decisions**: I chose to use an in-memory knowledge store (using native Python data structures) rather than spinning up a complex Graph Database (like Neo4j). This keeps the prototype incredibly fast, simple to review, and easy to deploy for the assignment, while demonstrating the core relationship mapping logic effectively.

## The Four Required Cases

The UI features a dedicated **"Cases" tab** that highlights the four requested scenarios:
1.  **Corroboration**: GDP growth estimates aligning perfectly between the Economic Survey and RBI Annual Report.
2.  **Contradiction**: Diverging FY25 growth forecasts between the RBI and the IMF.
3.  **Contextual Difference**: Varying inflation rates explained by different time periods and methodologies (WPI vs CPI).
4.  **Extraction Failure**: A simulated OCR error on a complex table structure, with system reasoning on how to flag low-confidence parses for human review.

## Limitations and Next Steps

*   **What doesn't work yet**: The in-memory data store is volatile; all uploaded documents and extracted facts are lost when the server restarts. 
*   **What I would build next**: 
    1. Integrate a persistent vector database (like Pinecone or ChromaDB) to store embeddings of extracted facts.
    2. Implement semantic search allowing users to query the knowledge layer using natural language.
    3. Add a chunking strategy that supports processing massive PDFs (500+ pages) without hitting API rate limits.

## Additional Notes
*   A custom CSS design system utilizing glassmorphism and modern UI principles was built completely from scratch without Tailwind or Bootstrap to ensure a premium, highly responsive user experience.
*   The application gracefully falls back to a pre-populated "Demo Mode" if a Gemini API key is not provided in the environment variables, allowing reviewers to safely test the UI without needing credentials.
