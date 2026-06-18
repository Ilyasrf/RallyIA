# Igudar AI Microservice — Technical Guide

> **What this is:** A complete explanation of the AI microservice architecture, the technologies used, why each one was chosen, and how to integrate it into the main Igudar platform.

---

## 1. Project Structure

```
ai_microservice/
├── main.py                          # Entry point — connects everything
│
├── shared/                          # Shared by BOTH features
│   ├── database.py                  # PostgreSQL + pgvector connection & Property model
│   └── embedding_service.py         # MiniLM text → vector conversion
│
├── recommendation/                  # Feature 1: Quiz-based property matching
│   ├── schemas.py                   # Data validation (QuizRequest, PropertyResponse...)
│   └── router.py                    # POST /recommend endpoint
│
├── chatbot/                         # Feature 2: RAG-powered local chatbot
│   ├── schemas.py                   # Data validation (ChatMessage, ChatRequest...)
│   ├── service.py                   # Local LLM wrapper (Qwen 0.5B)
│   └── router.py                    # POST /chat endpoint
│
├── requirements.txt                 # Python dependencies
└── venv/                            # Virtual environment
```

---

## 2. What We Use & Why

### all-MiniLM-L6-v2 (Embedding Model)

| | |
|---|---|
| **What it is** | A small (80MB) Sentence-Transformer model that converts any text into a list of 384 numbers (a "vector"). |
| **Why we use it** | It runs 100% locally, is extremely fast even on CPU, and captures the *meaning* of text — not just keywords. Two sentences with different words but the same meaning will produce similar vectors. |
| **Where it runs** | `shared/embedding_service.py` — loaded once at server startup, used by both features. |

**Example:**
```
"I want safe passive income"  →  [0.023, -0.145, 0.089, ..., 0.034]  (384 numbers)
"Low risk rental yield"       →  [0.021, -0.139, 0.091, ..., 0.031]  (very similar numbers!)
```

### pgvector (Vector Database)

| | |
|---|---|
| **What it is** | A PostgreSQL extension that lets you store and search vectors directly inside your database. |
| **Why we use it** | It solves the "cold start problem." we can't use traditional recommendation algorithms. Instead, we match users to properties based on the *meaning* of their profile vs the *meaning* of property descriptions. pgvector does this search in milliseconds. |
| **Where it runs** | `shared/database.py` — the `Property` table has an `embedding` column of 384 dimensions. |

### Qwen2.5-0.5B-Instruct (Chat LLM)

| | |
|---|---|
| **What it is** | A small (0.5 billion parameter) generative language model that can read context and write natural language responses. |
| **Why we use it** | External APIs like OpenAI are **strictly prohibited** due to KYC/financial data privacy. This model runs 100% locally on CPU. It's small enough to be fast, but smart enough to hold a conversation about the properties. |
| **Where it runs** | `chatbot/service.py` — lazy-loaded on the first chat request (not at startup, to keep the server fast). |

### FastAPI (Web Framework)

| | |
|---|---|
| **What it is** | A modern Python web framework for building APIs. |
| **Why we use it** | Auto-generates Swagger documentation at `/docs`, validates all request/response data automatically, and is one of the fastest Python frameworks. |

---

## 3. How It Works — Feature by Feature

### Feature 1: Recommendation System (Quiz → Properties)

This is the core intelligence. It takes the user's 5-question investor quiz and finds the best matching properties.

```
┌─────────────────────────────────────────────────────────────────┐
│                    POST /recommend                              │
│                                                                 │
│  Step 1: User submits quiz answers                              │
│          (goal, lock_in_years, risk_tolerance, capital,         │
│           experience)                                           │
│                                                                 │
│  Step 2: Build a "persona" sentence from the answers            │
│          "Investor seeking: passive income.                     │
│           Risk tolerance: low. Experience: beginner."           │
│                                                                 │
│  Step 3: MiniLM converts this sentence → 384-dim vector        │
│                                                                 │
│  Step 4: HYBRID SEARCH in PostgreSQL:                           │
│          a) SQL filter: capital >= min_investment                │
│             AND lock_in_years >= property lock_in                │
│          b) Vector similarity: rank remaining properties        │
│             by cosine distance to the user's vector             │
│          c) Return top 3                                        │
│                                                                 │
│  Step 5: Return recommendations + mocked summaries              │
└─────────────────────────────────────────────────────────────────┘
```

**Why hybrid search?** Pure vector search might return a 500,000 MAD property to someone with 1,000 MAD. The SQL filters eliminate impossible matches first, then vector similarity finds the *best* matches from what's left.

### Feature 2: RAG Chatbot (Question → Answer)

RAG = **Retrieval-Augmented Generation**. The chatbot doesn't hallucinate random answers. It first *retrieves* real property data from the database, then *generates* a response using only that data.

```
┌─────────────────────────────────────────────────────────────────┐
│                      POST /chat                                 │
│                                                                 │
│  Step 1: User asks: "Any commercial properties under 5000?"    │
│                                                                 │
│  Step 2: RETRIEVAL — MiniLM embeds the question → vector        │
│          pgvector finds the 2 most semantically similar         │
│          properties from the database                           │
│                                                                 │
│  Step 3: AUGMENTATION — Inject those properties into a          │
│          system prompt:                                         │
│          "You are Igudar's assistant. Here are the relevant     │
│           properties: [Downtown Plaza, 1000 MAD, Medium risk]"  │
│                                                                 │
│  Step 4: GENERATION — Qwen 0.5B reads the system prompt +      │
│          the user's question and writes a natural response      │
│                                                                 │
│  Step 5: Return the LLM's reply                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Why RAG?** Without it, the LLM would make up properties that don't exist. With RAG, every answer is grounded in real database data.

---

## 4. Running Locally

```bash
cd ai_microservice

# Activate virtual environment
source venv/bin/activate

# Install torch CPU-only (much smaller download, no GPU needed)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install everything else
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

---

## 5. API Reference

### POST /recommend — Get Property Recommendations

**Request:**
```json
{
  "goal": "Capital appreciation and passive income",
  "lock_in_years": 5,
  "risk_tolerance": "Moderate",
  "capital": 5000.00,
  "experience": "Beginner"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "id": 12,
      "title": "Downtown Commercial Plaza",
      "description": "High-yield commercial fractional real estate...",
      "min_investment": 1000.0,
      "lock_in_years": 3,
      "risk_rating": "Medium"
    }
  ],
  "risk_summary": "Based on your Moderate risk tolerance and Beginner experience...",
  "market_analysis_context": "The Moroccan real estate market currently shows strong demand..."
}
```

### POST /chat — Chat with the AI Assistant

**Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Do you have any commercial properties with low risk?"
    }
  ]
}
```

**Response:**
```json
{
  "reply": "Yes! Based on our current inventory, the Downtown Commercial Plaza..."
}
```

---

## 6. Notes for the Main Platform Developer

1. **Database Setup Required:** You need PostgreSQL with the `pgvector` extension enabled. Create the database `igudar_ai` and populate the `properties` table with property data and their vector embeddings.
2. **Mocked Summaries:** The `risk_summary` and `market_analysis_context` in `/recommend` are currently template strings, not AI-generated. They can be upgraded to use the local LLM later.
3. **Torch Installation:** Always install torch from the CPU index (`--index-url https://download.pytorch.org/whl/cpu`). The default PyPI torch includes NVIDIA CUDA drivers (532MB) which are unnecessary without a GPU.
4. **First Chat is Slow:** The Qwen chatbot model downloads (~1GB) and loads into memory on the first `/chat` request. Subsequent requests are fast.
5. **Environment Variable:** Set `DATABASE_URL` to override the default PostgreSQL connection string.
