# 🔍AI-Powered Production-Grade GitHub Repository Intelligence System

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-purple.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-blue.svg)
![Deploy](https://img.shields.io/badge/Deployed-Render-black.svg)

A **full-stack AI SaaS system** built with **LangGraph, FastAPI, Streamlit, and PostgreSQL (Supabase)** that performs automated GitHub repository analysis using a multi-agent architecture.

The system combines **agentic AI reasoning + production-grade backend engineering + interactive chat UI**, similar in structure to modern AI SaaS platforms.

---

## 🌐 Live Deployment

This project is deployed using Render with separate frontend and backend services.

- **Frontend (Streamlit UI):**  
https://ai-github-intelligence-system-front-end.onrender.com

- **Backend (FastAPI):**  
 https://ai-github-intelligence-system.onrender.com

---

## ⚠️ Important: Backend Cold Start (Render Free Tier)

The backend is hosted on Render’s free tier, which means it may go to **sleep after periods of inactivity**.

When this happens:

- The first request may take **30–60 seconds** to respond
- You may see messages like:
  - “Server is starting or temporarily unavailable”
  - `502 Bad Gateway`
  - Request timeout errors

---

## 🔄 How to Wake the Backend

If the backend is asleep, simply  this URLs to wake it up:

 
- https://ai-github-intelligence-system.onrender.com 


Once accessed, the backend will start up and subsequent requests will be fast.

---

## 💡 Why This Happens

Render free services spin down after periods of inactivity to save resources. This is expected behavior and not a bug in the application.

---

## 🚀 Recommended Usage

For the best experience:

1. Open the **backend URL first** (to wake it up)
2. Then open the **frontend UI**
3. Use the application normally




## 🚀 System Architecture

```text
Frontend (Streamlit UI)
           ↓
FastAPI Backend (Auth + API Layer)
           ↓
LangGraph Multi-Agent System
           ↓
GitHub API + LLM (Ollama / Cloud Model)
           ↓
Supabase PostgreSQL (Persistent Storage)
           ↓
Render Deployment (Production Hosting)
```


---

## 🧠 Core Capabilities

This system automatically:

- Analyzes GitHub repositories
- Extracts README structure and metadata
- Evaluates documentation quality
- Generates structured AI feedback
- Maintains persistent user sessions
- Enables conversational interaction per repository

---

## ⚙️ Key Features

### 🤖 Multi-Agent AI System (LangGraph)
- Content Agent (summarization)
- Metadata Agent (tags & keywords)
- Structure Agent (documentation validation)
- Quality Agent (scoring engine)
- Reviewer Agent (final decision engine)
- LLM Agent (interactive Q&A assistant)

---

### 🌐 Full-Stack SaaS Features
- Secure authentication (JWT)
- Refresh token system
- User-specific session storage
- Persistent chat history (like ChatGPT)
- Multi-session sidebar navigation
- Repository analytics dashboard
- Real-time chat interface (Streamlit)

---

### ☁️ Production Deployment
- Backend: FastAPI (Render)
- Frontend: Streamlit (Render)
- Database: Supabase PostgreSQL
- Environment-based configuration (.env)
- CORS-secured API communication

---

## 🏗️ System Design (Engineering View)

### Multi-Agent Flow
```text
GitHub Repo URL
        ↓
Analyzer Agent (Fetch Data)
        ↓
Parallel Agent Execution
├── Content Agent
├── Metadata Agent
├── Structure Agent
└── Quality Agent
         ↓
Reviewer Agent (Aggregation)
         ↓
LLM Agent (User Interaction Layer)
         ↓
Persistent Storage (PostgreSQL)
```


---

## 🔐 Authentication System

- JWT-based login system
- Secure refresh token rotation
- Protected API routes
- User-scoped data isolation

---

## 💾 Database Architecture (Supabase)

Each user has isolated data:
users → sessions → messages → repository analysis results.


Supports:
- Persistent chat history
- Session recovery
- Multi-repository tracking per user

---

## 🔧 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/login` | User authentication |
| `/register` | User registration |
| `/refresh` | Refresh access token |
| `/analyze` | Run repo analysis pipeline |
| `/chat` | LLM interaction endpoint |
| `/sessions` | Fetch user sessions |
| `/session/{id}` | Load specific session |

---

## 🖥️ Frontend (Streamlit)

Features:
- Repository analysis dashboard
- Sidebar session management
- Real-time chat interaction
- Metrics visualization:
  - Stars ⭐
  - Forks 🍴
  - Quality score 📊
  - Confidence score 🧠

---

## 📦 Installation (Local Development)

### 1. Clone repository
```bash
git clone https://github.com/Electrobello1/AI-Powered Production-Grade GitHub Repository Intelligence System.git
cd AI-Powered Production-Grade GitHub Repository Intelligence System
```
###   2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```

###  4. Configure environment variables
```bash
DATABASE_URL=your_supabase_postgres_url
SECRET_KEY=your_jwt_secret
REFRESH_SECRET_KEY=your_refresh_secret
OLLAMA_API_Key=your_API_Key
```
 ### 5. Run backend
```bash
uvicorn main:app --reload
```
 ### 6.Run frontend
```bash
streamlit run app.py
```
### 📊 Example Output
```bash
{

  "title": "Flask Chatbot System",
  "summary": "A chatbot built using Flask and LLMs",
  "stars": 9,
  "forks": 6,
  "tags": ["flask", "chatbot", "api"],
  "quality_score": 3,
  "confidence": 0.87,
  "status": "pass"
}
```
🧪 System Workflow

```text
User Input (GitHub URL)
        ↓
FastAPI /analyze endpoint
        ↓
LangGraph Multi-Agent Pipeline
        ↓
Supabase Database Storage
        ↓
Streamlit UI Rendering
        ↓
Chat-Based Interaction Layer
```

## 🚀 Future Improvements

- Asynchronous background workers (Celery / Redis)  
- Vector database integration (RAG system)  
- Real-time streaming responses  
- Multi-user collaboration features  
- CI/CD pipeline (GitHub Actions)  
- Role-based access control (RBAC)  
- Analytics dashboard for repo ranking  

## 🛠️ Tech Stack

- Python 🐍  
- FastAPI ⚡  
- Streamlit 🎨  
- LangGraph 🧠  
- PostgreSQL (Supabase) 🗄️  
- JWT Authentication 🔐  
- Ollama / LLM APIs 🤖  
- Render Deployment ☁️  

## 👨‍💻 Author

Princewill Bello

## 📜 License

MIT License