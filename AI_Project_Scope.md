# Igudar: AI-Powered Investment Intelligence
## Project Overview & Technical Scope

This document outlines the architecture, scope, and technical constraints for developing the AI features of the Igudar platform. Igudar is a fractional real estate investment platform designed to comply with Moroccan financial regulations, simplifying real estate investment for Moroccans with low capital.

---

## 1. Core AI Features

The following modules are being developed to provide smart, secure, and personalized investment assistance:

### AI-Powered Investment Intelligence
Our advanced AI analyzes market trends, property performance, and your personal preferences to recommend the perfect investment opportunities.

### Market Analysis
Real-time analysis of Moroccan real estate market trends and opportunities.

### Risk Assessment
Comprehensive risk evaluation for each investment opportunity, balancing expected yields, lock-in periods, and market location.

### Personalized Matching
Tailored recommendations based on your investment profile and goals, gathered via a targeted 5-question investor onboarding quiz.

---

## 2. Technical Constraints & Limitations

Due to operational and security requirements, this project operates under strict development boundaries:

*   **Time Constraint:** The entire MVP (Minimum Viable Product) for the AI features must be completed within a strict **2-day development sprint**.
*   **Data Privacy & Security (Local AI):** Because the platform handles highly sensitive financial and KYC data, external cloud LLM APIs (like OpenAI) are strictly prohibited. All AI models (LLMs for reasoning and embedding models for search) must run **100% locally**.
*   **Codebase Isolation:** There is no direct access to the main Igudar platform repository to prevent security risks. 
*   **Microservice Architecture:** Because of the lack of main repository access, the AI engine is being built as a standalone API microservice. The main platform will communicate with this service via HTTP requests.
*   **Cold Start Problem:** Since the startup is new, there is no historical user behavior data for traditional machine learning recommendation algorithms. The solution relies on **Semantic Vector Search (pgvector)** matching the user's quiz profile directly to property descriptions.

---

## 3. Workflow & Integration

**How it works seamlessly with the main app:**
1. The main Igudar platform sends a `POST` request to the AI microservice containing the user's profile (generated from the 5-question quiz) and their available capital.
2. The AI microservice converts this profile into a vector embedding using a local Sentence-Transformer model.
3. A similarity search is executed in a local vector database to find the closest matching properties.
4. The microservice returns the recommended property IDs, a risk summary, and market analysis context back to the main platform.
