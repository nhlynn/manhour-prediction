# MHES - Man Hour Estimation System

A Flask-based system to help Infrastructure Engineers estimate man-hours by searching imported Excel knowledge files using AI semantic search, assembling results on an editable Preview screen, and exporting a formatted estimate.

No relational database is used — knowledge files, embeddings, metadata, and temporary Preview backups are all persisted on the local filesystem. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/DATABASE.md](docs/DATABASE.md) for details.

## Installation

### Prerequisites

- Python 3.11+
- Ollama (with Qwen 2.5 3B model) — optional; the client library is included but not yet wired into the chatbot (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md))

### Windows Setup Commands

```cmd
REM 1. Navigate to project directory
cd D:\Infa\infra_manhour_estimation\MHES

REM 2. Create virtual environment
python -m venv venv

REM 3. Activate virtual environment
venv\Scripts\activate

REM 4. Install packages
pip install -r requirements.txt

REM 5. Run Flask development server
python app.py

REM 6. Verify installation - open browser
start http://localhost:5000
```

### Ollama Setup

```cmd
REM Install Ollama from https://ollama.com
REM Pull the Qwen 2.5 3B model
ollama pull qwen2.5:3b
```

## Running the Server

```cmd
REM Development
set FLASK_ENV=development
python app.py

REM Production (using waitress)
waitress-serve --host=0.0.0.0 --port=5000 app:create_app()
```

## How It Works

1. **Upload** — `.xlsx` knowledge files (Category → Task → Activity man-hour breakdowns) are uploaded and stored in `kb_knowledge/`.
2. **Embed** — each file is parsed into a nested Category/Task/Activity structure, converted to text chunks, embedded with Sentence Transformers, and indexed with FAISS (`embeddings/`).
3. **Search** — the chatbot matches a query against known category/task/activity names first (including partial/word-level matches), then falls back to FAISS semantic search scoped to a single source file, returning grouped results with computed totals.
4. **Preview** — matched results are assembled on an editable Preview screen (add/edit/delete categories, tasks, and activities; live totals).
5. **Export** — the Preview estimate is exported to a formatted `.xlsx` workbook (`exports/`). If it contains any Category, Task, or Activity Detail not already in the knowledge base, that data is also automatically added to `kb_knowledge/` and embedded, so it becomes searchable going forward.
6. **Temporary Data** — in-progress Preview data is automatically backed up server-side (`temp_data/`) when starting a new chatbot session or closing the browser, and can be restored or discarded from the Temporary Data page. Backups older than a configurable retention period (default 7 days) are purged automatically on a daily schedule.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for component diagrams and request flows, and [docs/DATABASE.md](docs/DATABASE.md) for the filesystem-based data schema (tables, columns, relationships).

## Folder Structure

| Folder | Description |
|---|---|
| `kb_knowledge/` | Stored knowledge base files (processed Excel data) |
| `embeddings/` | FAISS vector index, mapping JSON, and embedding metadata |
| `temp_data/` | Server-side backups of in-progress Preview data (auto-purged on a schedule) |
| `uploads/` | Temporary storage for uploaded Excel files |
| `exports/` | Generated export files for download |
| `logs/` | Application log files |
| `templates/` | Jinja2 HTML templates |
| `static/` | CSS, JavaScript, and image assets |
| `routes/` | Flask Blueprint route handlers |
| `services/` | Business logic service classes (Excel I/O, parsing, embeddings, search) |
| `scheduler/` | APScheduler integration and the Temporary Data store/cleanup logic |
| `utils/` | Utility functions and helpers |
| `models/` | Reserved for future ML model artifacts (currently empty) |
| `docs/` | Architecture and database documentation |

## Tech Stack

- **Backend:** Flask, Jinja2, Bootstrap 5
- **Data:** Pandas, OpenPyXL
- **AI:** Sentence Transformers, FAISS, Ollama (Qwen 2.5 3B, not yet connected)
- **Scheduling:** APScheduler (in-process background jobs)
- **Storage:** Local filesystem (no database)

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system overview, application architecture, frontend/backend breakdown, AI chatbot flow, and the scheduler/Temporary Data subsystem (with Mermaid diagrams)
- [docs/DATABASE.md](docs/DATABASE.md) — filesystem-based data stores, schema, and relationships
