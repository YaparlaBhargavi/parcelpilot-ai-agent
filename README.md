# 🚚 ParcelPilot AI Support Agent

> AI-powered internal support intelligence for logistics operations.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![FAISS](https://img.shields.io/badge/Vector%20DB-FAISS-green)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🌐 Live Demo

**Hosted Application:**  
https://parcelpilot-ai-agent-1.streamlit.app/

**GitHub Repository:**  
https://github.com/YaparlaBhargavi/parcelpilot-ai-agent

---

## 📖 About the Project

ParcelPilot is an AI-powered internal support assistant designed for logistics teams.

It helps support teams quickly:

- 📄 Search company documents
- 📊 Look up orders, tickets, and customer accounts
- 🧠 Answer complex questions using multiple sources
- ⚡ Escalate issues with human confirmation
- 🔍 Investigate recurring operational issues

The main goal is to reduce the time support teams spend searching for information and help them make more consistent, evidence-based decisions.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 💬 AI Support Assistant | Ask questions using natural language |
| 📄 Document Search | Search policies, SOPs, product guides, and agreements |
| 📊 Data Lookup | Retrieve order, ticket, and account information |
| 🧠 Multi-Step Reasoning | Combine information from multiple sources |
| ⚡ Actions | Prepare escalations with human confirmation |
| 🔍 Issue Investigation | Investigate recurring operational problems |
| ⚖️ Source Priority | Resolve conflicting information using source reliability |
| 📈 Confidence | Provide confidence based on available evidence |
| 🔐 Security | Keep secrets and environment variables outside the repository |

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    │   Natural Language  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   ParcelPilot AI    │
                    │       Agent         │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │  Document   │  │ Structured  │  │   Action    │
       │   Search    │  │    Data     │  │    Tool     │
       └──────┬──────┘  └──────┬──────┘  └─────────────┘
              │                │
              ▼                ▼
       ┌─────────────┐  ┌─────────────┐
       │    FAISS    │  │ Excel / DB  │
       │ Vector Store│  │    Data     │
       └──────┬──────┘  └──────┬──────┘
              │                │
              └────────┬───────┘
                       ▼
              ┌─────────────────┐
              │ Evidence +      │
              │ Source Priority │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Final Answer    │
              └─────────────────┘

## 🛠️ Technology Stack

- Python
- Streamlit
- LangChain
- OpenAI
- Hugging Face
- FAISS
- Pandas
- PyPDF

---

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/YaparlaBhargavi/parcelpilot-ai-agent.git
cd parcelpilot-ai-agent

2. Install dependencies
pip install -r requirements.txt
3. Add environment variables

Create a .env file:

OPENAI_API_KEY=your_api_key
4. Create the vector store
python ingest_documents.py
5. Run the application
streamlit run app.py

Open:

http://localhost:8501
💬 Example Queries
Document Search
What is the cancellation policy?
What are the SLA response times?
Data Lookup
Look up order ORD-1001
Look up ticket TKT-501
Reasoning
Can Northstar cancel this order without a fee?
What service credit applies to LumenWorks?
Actions
Escalate order ORD-1001
🎯 Challenges

The main challenges were:

Combining PDF documents with structured data
Handling conflicting information between different documents
Building reliable document search using RAG
Managing Python package compatibility
Deploying the application successfully on Streamlit Cloud
🚀 Future Improvements
Better issue detection
Real ticketing-system integration
More analytics
Automatic ticket classification
Better user feedback and evaluation
📊 Success Metric

The main metric I would track is average support resolution time.

The goal is to reduce the time support agents spend searching for information while maintaining reliable answers.

🤖 AI Tool Usage

I used AI coding assistants to help with:

Code generation
Debugging
Dependency troubleshooting
RAG implementation
Streamlit deployment
Documentation

I reviewed and tested the generated code before using it in the final project.

🌐 Live Demo

Streamlit App:
https://parcelpilot-ai-agent-1.streamlit.app/

GitHub:
https://github.com/YaparlaBhargavi/parcelpilot-ai-agent

👩‍💻 Author

Yaparla Bhargavi

GitHub:
https://github.com/YaparlaBhargavi/parcelpilot-ai-agent
