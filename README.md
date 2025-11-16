# Illusion — Transparent AI Audits for Company Data Practices

Illusion is a multi-agent auditing system that makes **company privacy, data-collection, and data-usage policies transparent**.

Given a company name or URL, Illusion:

* Finds official privacy / terms / cookie / data-usage documents
* Reads and extracts the relevant clauses
* Scores **data-collection, sharing, tracking, and transparency risk**
* Provides **user protection advice** and **citations**
* Exposes **execution traces, reasoning steps, latency, and token usage**
* Uses **caching** so repeated queries do not consume extra LLM credits

---

## Project Overview

Online privacy policies are long, scattered across obscure links, and written for lawyers—not users. This makes it hard for people to understand how their data is collected, shared, tracked, and retained.

Illusion automates this analysis. A search agent finds official policies, an extraction agent pulls out only the relevant data-practice sections, and a summary agent synthesizes a structured report with risk ratings, transparency scores, and concrete advice on how users can protect themselves.

Illusion is also a **glass-box** system: we log our tools, reasoning steps, runtime, token usage, and associated costs, so users can see exactly how the model reached its conclusions.

---

## Architecture at a Glance

* **Frontend** (Node.js + React + Vite + TypeScript)

  * Landing page with company search bar and microphone input
  * Visual components for:

    * Transparency score
    * Risk ratings
    * Summary of key findings
    * User protection advice
    * Model transparency (tokens, latency, tools used)
    * Sources and citations

* **Backend** (FastAPI)

  * `/[company_or_url]` endpoint that orchestrates the full pipeline
  * **search_agent** → finds official policy URLs via Valyu / web search
  * **extract_agent** → fetches pages and extracts only data-practice text
  * **summary_agent** → produces final structured JSON:

    * overview, key findings, ratings
    * risks, user protection advice
    * sources used and reasoning

* **Tracing & Cost Awareness**

  * Strands + MLflow tracing for:

    * per-span token usage
    * estimated API cost
    * full tool call trace and reasoning

* **Caching**

  * Responses cached by company / URL
  * Repeat queries return instantly without consuming additional LLM or search credits

---

## Requirements

* **Python** 3.10+
* **Node.js** 18+
* **npm**
* Ability to create a Python virtual environment (`venv`)

---

## Environment Variables

Create a `.env` file in `app/backend/` with:

```env
GEMINI_API_KEY=<your-gemini-api-key>
VALYU_API_KEY=<your-valyu-api-key>
TEAM_ID=<your-team-id>
API_TOKEN=<your-api-token>
API_ENDPOINT=<your-api-endpoint>  # e.g. https://api.valyu.ai/...
```

You may also include any additional API or tracing configuration variables as needed.

---

## Setup

### 1. Clone repository & create virtual environment

```bash
# Clone repo
git clone <your-repo-url>
cd <your-repo-name>

# Create and activate virtual environment
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows PowerShell
# .\venv\Scripts\Activate
```

### 2. Install backend dependencies (FastAPI, Strands, etc.)

```bash
# From repo root, with venv activated
pip install -r requirements.txt
```

### 3. Install frontend dependencies (React / Vite)

```bash
cd app/frontend
npm install
```

### 4. Configure .env for backend

Create `app/backend/.env`:

```env
GEMINI_API_KEY=...
VALYU_API_KEY=...
TEAM_ID=...
API_TOKEN=...
API_ENDPOINT=...
```

These keys are required for:

* Calling Gemini (LLM)
* Calling Valyu search / API
* Running the multi-agent pipeline without errors

---

## How to Run

### Start the backend (FastAPI)

From the **repo root** (where `app/` lives):

```bash
# Ensure venv is activated
uvicorn app.backend.main:app --reload
```

Backend will run on:

```text
http://127.0.0.1:8000
```

### Start the frontend (React + Vite)

Open another terminal and navigate to the frontend directory:

```bash
cd app/frontend
npm run dev
```

Frontend will run on:

```text
http://localhost:5173
```

### Quick test

With both servers running:

1. Open `http://127.0.0.1:8800/` in your browser.
2. Type a company name or URL (e.g. `OpenAI`, `Meta`, `https://anthropic.com`).
3. Click the arrow button (or use the microphone).
4. Wait for Illusion to:

   * show a loading / “thinking” animation
   * then display:

     * transparency score
     * risk ratings
     * summary of data practices
     * user protection advice
     * sources and citations
     * model transparency (tokens, latency, tools used)

---

## API Shape (Backend Response)

For a successful audit, the backend returns a JSON object of the form:

```json
{
  "status": "success",
  "query": "...",
  "search_result": { },
  "extraction_result": { },
  "final_summary": {
    "summary": {
      "overview": "...",
      "key_findings": ["..."],
      "ratings": {
        "data_collection_risk": 3,
        "data_sharing_risk": 2,
        "tracking_risk": 3,
        "transparency_score": 4
      },
      "reasoning": [ ],
      "user_protection_advice": [ ],
      "final_recommendation": "...",
      "sources_used": [ ]
    }
  },
  "timing": {
    "estimated_total_ms": 123456,
    "token_usage": {
      "input_tokens": 1234,
      "output_tokens": 567,
      "total_tokens": 1801
    },
    "token_usage_detailed": [ ]
  },
  "trace": {
    "tools_used": ["search_agent", "extract_agent", "summary_agent"],
    "steps": [
      {
        "step_index": 0,
        "action": "Call search_agent to resolve company and find policy URLs",
        "tool": "search_agent",
        "tool_input": "company_or_url=...",
        "tool_output_used": "full search_agent JSON",
        "reasoning": "..."
      }
    ]
  },
  "error_message": null
}
```

The frontend consumes this object to render scores, summaries, and transparency metadata.

---

## Track-Specific Requirements

### Track A — Agent Iron Man

**Goal:** Demonstrate performance, robustness, and error handling.

* **Performance metrics (latency, cost, tokens)**

  * `timing.estimated_total_ms` — total end-to-end runtime
  * `timing.token_usage` — aggregate input / output / total tokens
  * `timing.token_usage_detailed` — per-span breakdown with estimated USD cost

* **Error handling**

  * Each stage (search, extract, summarize) is wrapped in `try/except`:

    * If `search_agent` fails → returns `status: "error"`, includes any partial result and error message
    * If `extract_agent` fails → no summary is attempted; error is surfaced
    * If `summary_agent` fails → search & extraction results are preserved and exposed
  * The frontend displays friendly error messages if the backend returns `status: "error"`.

* **Baseline comparison**

  * Manual baseline: users must open multiple pages, skim dense legal text, and try to judge data practices themselves.
  * Illusion: one query → automated search, extraction, scoring, and explanation with sources and recommendations.

### Track B — Agent Glass Box

**Goal:** Show how the agent thinks and why it made its decisions.

* **Execution traces included**

  * `trace.tools_used` shows exactly which agents were called and in what order.
  * `trace.steps[]` provides:

    * which tool was called
    * what input was passed
    * which part of the output was used
    * a short reasoning explanation for each step

* **Visualization / documentation of reasoning**

  * The frontend’s **Model Transparency** component displays:

    * token usage
    * elapsed time
    * tools used in this run
    * natural-language “thoughts” (from `trace.steps[].reasoning`)

* **Failure analysis**

  * On failure (e.g., 403 on a policy URL, timeouts, malformed pages), the backend:

    * sets `status: "error"`
    * populates `error_message` with a human-readable cause
    * includes any partial `search_result` / `extraction_result` for debugging
  * This lets users inspect *why* the system could not complete an audit.

---

## Caching & Cost Awareness

To keep the system efficient and affordable:

* A caching layer stores the **full master JSON** keyed by normalized company name / URL.
* If a user queries the same company again:

  * the backend returns the cached result instantly
  * no new LLM or search calls are made
  * token usage and cost do **not** increase

This design supports interactive exploration while respecting API rate limits and credit budgets.
