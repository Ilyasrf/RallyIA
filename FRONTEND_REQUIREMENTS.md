# Next Steps: Frontend & System Requirements

This document summarizes what has been built on the backend so far and outlines exactly what needs to be built on the frontend (and the main platform) to make the entire Igudar AI system fully functional.

## What We Have Built So Far (The AI Backend)

We have successfully built a **100% Local AI Microservice**. It is fully independent and exposes an API.

1. **Semantic Recommendation Engine (`POST /recommend`)**: Uses MiniLM and pgvector to take a user's quiz profile, convert it to a mathematical vector, and find the best-matching properties from the database based on meaning and hard constraints (capital, lock-in period).
2. **Context-Aware Chatbot (`POST /chat`)**: Uses a local generative AI model (Qwen 0.5B) combined with RAG (Retrieval-Augmented Generation). It reads a user's question, fetches relevant properties from the database, and answers the question accurately using that context.
3. **Database Architecture**: Configured a PostgreSQL database with the `pgvector` extension to handle rapid similarity searches.

---

## What Needs to be Built Next (The Frontend)

For users to actually interact with this AI, you need to build the frontend interfaces. Here is exactly what the frontend needs to handle:

### 1. The Investor Onboarding Quiz UI
You need to build a user interface for the 5-question quiz.
- **The UI:** A clean, step-by-step form asking the user about their:
  - Primary goal
  - Preferred lock-in period (years)
  - Risk tolerance
  - Initial investment capital
  - Experience level
- **The Integration:** When the user finishes the quiz, the frontend must collect these answers into a JSON object and make a `POST` request to `http://127.0.0.1:8000/recommend`.
- **The Result View:** The frontend must receive the response from the API and beautifully display the recommended properties, the risk summary, and the market analysis context.

### 2. The AI Chatbot Interface
You need to build a chat window where users can talk to the assistant.
- **The UI:** A standard chat interface (like WhatsApp or ChatGPT) with a message history view and an input box.
- **State Management:** The frontend is responsible for remembering the conversation history. It must keep an array of all previous messages in the current session.
- **The Integration:** Every time the user types a message, the frontend appends it to the history array and sends the entire array to `http://127.0.0.1:8000/chat`.
- **The Result View:** When the API returns a `reply`, the frontend adds it to the chat UI as an "assistant" message.

---

## What Needs to be Built on the Main Platform Backend

The AI Microservice currently searches a local `properties` table. However, it doesn't know when new properties are added to the main Igudar platform. 

### 1. Database Synchronization Strategy
To keep the AI up-to-date, the main platform's backend (where admins add new properties) must sync with the AI microservice's database.
- **When a property is created:** The main platform must trigger a process to:
  1. Take the new property's description.
  2. Send it to the MiniLM embedding model to get its 384-dimension vector.
  3. Insert the property details and the vector into the AI Microservice's `pgvector` database.
- **When a property is updated/deleted:** The main platform must update or remove the corresponding record in the AI database.

### 2. Mock Summaries Upgrade (Optional Future Step)
Currently, the `risk_summary` and `market_analysis_context` returned by the `/recommend` endpoint are generated using static text templates (mocked) to keep the recommendation endpoint extremely fast. In the future, you can hook these fields back up to the local generative LLM if you want dynamic, AI-written summaries.
