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
