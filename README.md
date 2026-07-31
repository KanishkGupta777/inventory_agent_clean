# Restaurant AI Agent - Clean Project

## Quick Start

### 1. Install Python dependencies
```powershell
uv pip install -r requirements.txt
```

### 2. Setup PostgreSQL database
Make sure PostgreSQL is running, then:
```powershell
uv run python scripts/migrate_csv_to_postgres.py
```

### 3. Edit `.env` with your credentials
- `GROQ_API_KEY` - your Groq API key
- `DATABASE_URL` - your PostgreSQL connection string

### 4. Start backend (Terminal 1)
```powershell
uv run uvicorn api:app --reload --port 8000
```

### 5. Start frontend (Terminal 2)
```powershell
cd frontend/a
$env:Path = "C:\Users\KanishkGupta\Desktop\node;$env:Path"
& "C:\Users\KanishkGupta\Desktop\node\npm.cmd" install
& "C:\Users\KanishkGupta\Desktop\node\npx.cmd" vite
```

### 6. Open in browser
**http://localhost:5173**

Login credentials:
- Admin: `admin` / `admin123`
- Manager: `manager1` / `pass123`

## Project Structure
```
inventory_agent/
├── api.py                          # FastAPI backend
├── .env                            # Environment variables
├── pyproject.toml                  # Python project config
├── requirements.txt                # Python dependencies
├── data/                           # CSV/TSV data files
├── scripts/
│   └── migrate_csv_to_postgres.py  # DB migration script
├── src/
│   ├── ceo_agent.py                # CEO orchestrator (1 LLM call)
│   ├── data_loader.py              # Database data loader
│   ├── db/
│   │   └── connection.py           # PostgreSQL connection
│   ├── operations/
│   │   └── operations_agent.py     # Operations analysis (1 LLM call)
│   ├── customer/
│   │   └── customer_agent.py       # Customer analysis (1 LLM call)
│   └── business/
│       └── business_agent.py       # Business analysis (1 LLM call)
└── frontend/a/                     # React + Vite frontend
    ├── src/
    ├── package.json
    └── vite.config.js
```

## Architecture
Only **4 LLM calls** per analysis (~20-30 seconds total):
1. Operations agent → analyzes inventory, kitchen, waste, packaging, staff
2. Customer agent → analyzes CRM, loyalty, feedback, churn, offers
3. Business agent → analyzes demand, weather, festivals, pricing, finance, marketing, suppliers
4. CEO agent → combines all 3 reports into executive summary