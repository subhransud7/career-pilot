# 🧭 Career Pilot

### 🚀 AI-Powered Job Hunting Command Center

Career Pilot is a local-first, multi-agent job automation system that aggregates hiring posts, analyzes them using configurable LLM agents (OpenAI / Gemini), routes tasks intelligently with fallback logic, and provides a fast review dashboard for semi-automated outreach.

It transforms job hunting from a chaotic process into a structured, data-driven pipeline.

---

## ✨ Features

- 🔎 Aggregate fresh job posts (custom keywords + date filters)
- 🧠 Multi-LLM orchestration (OpenAI + Gemini)
- 🔄 System-level and task-level agent routing
- ⚡ Automatic fallback if primary LLM fails
- 📊 Intelligent scoring & filtering
- 🗂 Lead lifecycle state management
- 👀 Minimal, fast dashboard UI (Bootstrap + HTMX)
- ✉️ Personalized email draft generation
- 💬 LinkedIn DM draft generation (manual safe sending)
- 📈 Agent performance tracking
- 🔁 Duplicate prevention
- 📤 Optional export to Google Sheets
- 💾 Persistent SQLite memory layer
- 🧵 Parallel processing for faster aggregation

---

## 🏗 Architecture Overview

Career Pilot is built with:

- **FastAPI** backend
- **SQLite** persistent storage
- **Multi-agent orchestration layer**
- **Provider-agnostic LLM wrapper**
- **Task router with fallback logic**
- **Concurrent task execution**
- **Bootstrap + HTMX minimal UI**

