# AI Due Diligence Copilot

A Django + Postgres (pgvector) RAG platform that ingests company filings,
financial statements, investor presentations, and market reports, then
generates **source-backed** risk assessments, growth opportunities, and
executive summaries — plus an ad-hoc Q&A interface, all grounded with
citations back to the exact document and page they came from.

Built by Jackson Ochieng Ayagah ([@ayagah](https://github.com/ayagah)).

## Why this project

Due diligence today means an analyst manually reading hundreds of pages of
filings to answer "what are the risks here?" This project automates the
first pass: upload the source documents, and get a structured report in
seconds, where every claim is traceable to a specific page in a specific
document — not a hallucinated summary.

## How it works (architecture)

```
Upload (PDF/TXT) 
   -> Text extraction (pypdf, per-page)
   -> Token-aware chunking with overlap (tiktoken)
   -> Embedding (OpenAI text-embedding-3-small)
   -> Stored in Postgres as a pgvector column (HNSW index, cosine distance)

Query ("generate report" or ad-hoc question)
   -> Query embedded -> top-k similarity search in pgvector
   -> Retrieved chunks + question assembled into a grounded prompt
   -> LLM (gpt-4o-mini) call in JSON mode -> structured report
   -> Each risk/opportunity/answer is linked back to its source chunk(s)
      as a Citation row
```

### Apps
- **accounts** — custom user model (`AUTH_USER_MODEL`), JWT auth (register/login/refresh)
- **documents** — `Document` + `DocumentChunk` models, the ingestion pipeline
  (`extraction.py`, `chunking.py`, `embeddings.py`, `vectorstore.py`), upload
  form, and document list/detail views
- **analysis** — `DueDiligenceSession`, `AnalysisReport`, `Citation`,
  `Question` models, the RAG orchestration (`rag_pipeline.py`,
  `prompts.py`, `llm_client.py`), and the session dashboard/report UI

### Why these design choices
- **pgvector over a separate vector DB**: one database to manage, one set of
  credentials, and Django's ORM can do the similarity search directly via
  `CosineDistance` — no extra infrastructure to deploy or pay for.
- **Token-based chunking with overlap**: keeps each chunk inside the
  embedding model's effective context and prevents a sentence/number being
  cut in half at a chunk boundary, which would otherwise hurt retrieval
  quality on financial figures.
- **JSON-mode LLM calls**: the report generator forces the model to return a
  strict schema (`executive_summary`, `risk_assessment[]`,
  `growth_opportunities[]`, each with `source_chunk_ids`), which is what
  makes automatic citation linking possible — without it you'd have a
  paragraph of prose with no way to verify it.
- **Citations as their own model**: rather than embedding source info as text
  in the report, each citation is a real foreign key to a `DocumentChunk`,
  so the UI can always link back to the original page.

## Tech stack

- Django 5 + Django REST Framework
- PostgreSQL + [pgvector](https://github.com/pgvector/pgvector)
- OpenAI API (`text-embedding-3-small`, `gpt-4o-mini`)
- JWT auth (`djangorestframework-simplejwt`)
- Bootstrap 5 + django-crispy-forms for the demo UI
- Render-ready (`render.yaml`, `build.sh`, WhiteNoise for static files)

## Local setup

1. **Install Postgres with the pgvector extension.**
   - macOS: `brew install postgresql pgvector`
   - Ubuntu: `sudo apt install postgresql postgresql-contrib` then build/install
     pgvector per [its README](https://github.com/pgvector/pgvector#installation)
   - Or use Docker: `docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector:pg16`

2. **Create the database:**
   ```bash
   createdb due_diligence_copilot
   ```

3. **Clone and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # then edit .env and set OPENAI_API_KEY and DATABASE_URL
   ```

5. **Run migrations** (this also enables the `vector` extension automatically
   via the first migration):
   ```bash
   python manage.py migrate
   ```
   If your Postgres user lacks permission to create extensions, run this
   once manually as a superuser before migrating:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

6. **Create a superuser and run the server:**
   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   ```

7. Visit `http://127.0.0.1:8000/documents/upload/` to upload a filing,
   then `http://127.0.0.1:8000/` to create a session and generate a report.
   Admin panel: `http://127.0.0.1:8000/admin/`.

> First run will download a small tokenizer file used by `tiktoken` — make
> sure the machine has internet access on first use (it caches after that).

## REST API

All endpoints below require a JWT (`Authorization: Bearer <token>`), obtained via:

```bash
POST /api/auth/register/   {"username", "email", "password"}
POST /api/auth/login/      {"username", "password"} -> {"access", "refresh"}
```

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/documents/` | POST | Upload a document (multipart form: `company_name`, `title`, `document_type`, `file`) |
| `/api/documents/` | GET | List your documents |
| `/api/documents/{id}/process/` | POST | Run extraction + chunking + embedding |
| `/api/analysis/sessions/` | POST | Create a session: `{"company_name", "documents": [id, ...]}` |
| `/api/analysis/sessions/{id}/generate_report/` | POST | Run full RAG report generation |
| `/api/analysis/sessions/{id}/ask/` | POST | Ask an ad-hoc question: `{"question": "..."}` |

Example flow with `curl`:
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -d "username=jack&password=yourpassword" | python -c "import sys,json;print(json.load(sys.stdin)['access'])")

curl -X POST http://127.0.0.1:8000/api/documents/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "company_name=Safaricom PLC" -F "title=FY2025 Annual Report" \
  -F "document_type=filing" -F "file=@/path/to/report.pdf"

curl -X POST http://127.0.0.1:8000/api/documents/1/process/ -H "Authorization: Bearer $TOKEN"

curl -X POST http://127.0.0.1:8000/api/analysis/sessions/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"company_name": "Safaricom PLC", "documents": [1]}'

curl -X POST http://127.0.0.1:8000/api/analysis/sessions/1/generate_report/ \
  -H "Authorization: Bearer $TOKEN"
```

## Deploying to Render

1. Push this repo to GitHub.
2. In Render, click **New > Blueprint** and point it at the repo —
   `render.yaml` already defines the web service and a free Postgres
   database with pgvector support.
3. After the first deploy, go to the service's **Environment** tab and set
   `OPENAI_API_KEY` (this is intentionally left out of `render.yaml` so your
   key never ends up in git history).
4. Render's managed Postgres supports the `vector` extension; the first
   migration enables it automatically.

## Roadmap / extensions worth mentioning on your resume

- Move ingestion (`index_document`) to a Celery task + Redis so large filings
  don't block the request/response cycle.
- Add a re-ranking step (e.g. Cohere rerank or a cross-encoder) after the
  initial pgvector retrieval to improve precision on long, similar-sounding
  financial disclosures.
- Add OCR (e.g. via `unstructured` or `pytesseract`) for scanned filings that
  have no extractable text layer.
- Multi-tenant support: scope sessions to an "Organization" model so teams
  can collaborate on the same due-diligence engagement.

## Suggested resume / portfolio description

> **AI Due Diligence Copilot** — A Django + PostgreSQL (pgvector) RAG
> platform that ingests company filings, financial statements, investor
> presentations, and market reports, and generates source-backed risk
> assessments, growth-opportunity analyses, and executive summaries in
> seconds. Implements a full retrieval pipeline (token-aware chunking,
> OpenAI embeddings, HNSW cosine-similarity search) with citation tracking
> linking every generated claim back to its source document and page.
> Exposes a JWT-authenticated REST API and a server-rendered demo UI;
> deployable to Render with a single Blueprint.
