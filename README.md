# Igudar AI Microservice

**AI-powered investment intelligence for fractional real estate in Morocco.**

Igudar makes real estate accessible to Moroccans with limited capital. This repo contains the standalone AI microservice that powers personalized property recommendations, risk assessment, ROI predictions, and a context-aware chatbot — all running 100% locally with no external API calls.

---

## Why Local-First?

The platform handles sensitive financial and KYC data. External LLM APIs (OpenAI, etc.) are off the table. Every model runs on your own hardware — embeddings, generation, everything.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Igudar Main Platform                    │
│                   (Next.js / Django)                     │
└───────────────────────┬─────────────────────────────────┘
                        │  HTTP POST /recommend
                        │  HTTP POST /chat
                        ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI AI Microservice (Python)            │
│                                                         │
│  ┌──────────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Recommendation│  │ Chatbot  │  │ Risk & ROI Engine │  │
│  │  Engine       │  │  (RAG)   │  │                   │  │
│  └──────┬───────┘  └────┬─────┘  └────────┬──────────┘  │
│         │               │                  │             │
│  ┌──────┴───────────────┴──────────────────┴──────────┐  │
│  │            shared/embedding_service.py              │  │
│  │           (all-MiniLM-L6-v2, 384-dim)              │  │
│  └───────────────────────┬────────────────────────────┘  │
│                          │                               │
│  ┌───────────────────────┴────────────────────────────┐  │
│  │         PostgreSQL + pgvector (vector DB)           │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Features

| Feature | Endpoint | What it does |
|---------|----------|-------------|
| **Semantic Recommendation** | `POST /recommend` | Takes a 5-question investor quiz profile, converts it to a vector, and finds the top 3 matching properties using hybrid search (SQL filters + cosine similarity). |
| **RAG Chatbot** | `POST /chat` | Retrieval-Augmented Generation — retrieves real property data from the DB, then generates grounded answers using a local LLM (Qwen 2.5 0.5B). No hallucinated properties. |
| **Risk Assessment** | Built into `/recommend` | Multi-factor risk scoring: base risk, lock-in penalty, yield factor, user alignment, and experience modifier. Returns a 0–100 score with a human-readable breakdown. |
| **ROI Prediction** | Built into `/recommend` | Projects annual and total returns in MAD, factoring in base yield, location appreciation (Casablanca, Marrakech, Tangier, etc.), risk premium, and property type. |
| **Health Check** | `GET /health` | Simple liveness probe. |

## Tech Stack

- **Framework:** FastAPI
- **Embeddings:** `all-MiniLM-L6-v2` (Sentence-Transformers, 384-dim, ~80MB, CPU-only)
- **Vector DB:** PostgreSQL + pgvector
- **Chat LLM:** Qwen 2.5 0.5B Instruct (runs locally on CPU, lazy-loaded on first `/chat`)
- **ORM:** SQLAlchemy
- **Validation:** Pydantic v2

## Quick Start

```bash
cd ai_microservice

python -m venv venv
source venv/bin/activate

# Install CPU-only torch (~250MB instead of 5GB)
pip install torch --index-url https://download.pytorch.org/whl/cpu

pip install -r requirements.txt

# Set up the database
psql -U postgres -c "CREATE DATABASE igudar_ai;"
psql -U postgres -d igudar_ai -f scripts/init_db.sql

# Configure environment
cp .env.example .env

# Run
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Swagger docs at `http://127.0.0.1:8000/docs`.

## API Reference

### `POST /recommend`

```json
// Request
{
  "goal": "Capital appreciation and passive income",
  "lock_in_years": 5,
  "risk_tolerance": "Moderate",
  "capital": 5000.00,
  "experience": "Beginner"
}

// Response
{
  "recommendations": [
    {
      "id": 12,
      "title": "Downtown Commercial Plaza",
      "description": "High-yield commercial fractional real estate...",
      "min_investment": 1000.0,
      "lock_in_years": 3,
      "risk_rating": "Medium",
      "risk_assessment": {
        "overall_score": 42.5,
        "risk_level": "Medium",
        "user_alignment": "Well-aligned",
        "explanation": "..."
      },
      "roi_prediction": {
        "annual_return_pct": 8.5,
        "total_return_mad": 2125.0,
        "explanation": "..."
      }
    }
  ],
  "risk_summary": "Based on your Moderate risk tolerance...",
  "market_analysis_context": "The Moroccan real estate market..."
}
```

### `POST /chat`

```json
// Request
{
  "messages": [
    { "role": "user", "content": "Any commercial properties under 5000?" }
  ]
}

// Response
{
  "reply": "Yes! Based on our current inventory, the Downtown Commercial Plaza..."
}
```

## Investor Quiz (5 Questions)

The recommendation engine is driven by a 5-question onboarding quiz:

1. **Primary goal** — passive income, capital appreciation, etc.
2. **Lock-in period** — how long the investor can commit capital
3. **Risk tolerance** — Low / Medium / High
4. **Initial capital** — hard filter before vector search
5. **Experience level** — Beginner / Intermediate / Advanced / Expert

## Project Structure

```
ai_microservice/
├── main.py                    # FastAPI app entry point
├── shared/
│   ├── database.py            # SQLAlchemy models, pgvector Property table
│   └── embedding_service.py   # MiniLM embedding (singleton, lazy-loaded)
├── recommendation/
│   ├── router.py              # POST /recommend
│   └── schemas.py             # QuizRequest, RecommendationResponse
├── chatbot/
│   ├── router.py              # POST /chat
│   ├── schemas.py             # ChatRequest, ChatResponse
│   └── service.py             # Qwen 2.5 LLM wrapper (lazy-loaded)
├── risk_assessment/
│   ├── router.py
│   ├── engine.py              # Multi-factor risk scoring
│   └── schemas.py
├── roi_prediction/
│   ├── router.py
│   ├── engine.py              # ROI projection engine
│   └── schemas.py
├── scripts/
│   ├── init_db.sql            # pgvector schema + IVFFlat index
│   └── init_db.py             # DB initialization script
├── requirements.txt
└── .env.example
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/igudar_ai` | PostgreSQL connection string |
| `CHAT_MODEL_NAME` | `Qwen/Qwen2.5-0.5B-Instruct` | Local LLM for chatbot |
| `CHAT_MAX_TOKENS` | `250` | Max tokens for chat responses |

## Notes

- **First `/chat` request is slow** — Qwen downloads (~1GB) and loads into memory. Subsequent requests are fast.
- **Risk & ROI summaries are template-based** for speed. Can be upgraded to use the local LLM for dynamic generation.
- **Database sync** — the main Igudar platform must push new properties (with embeddings) to this microservice's PostgreSQL database when inventory changes.

## License

Proprietary — Igudar
