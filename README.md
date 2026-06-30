# Interview Gym

> AI-powered platform to prepare for technical interviews — practice Q&A sessions and get your code reviewed automatically by submitting a GitHub link.

**Bachelor's thesis project** · FastAPI · React · Gemini API · ChatGPT API

---

## Features

### Interview Simulation
Practice answering technical interview questions in a realistic Q&A format. The AI acts as an interviewer, asks follow-up questions, and evaluates your answers in real time.

### Automated Code Review via GitHub Link
Paste a link to any GitHub repository and get:
- An automatically generated set of technical tasks based on the codebase
- AI-powered code review and evaluation of your solutions
- Feedback on code quality, logic, and structure

### Dual AI Integration
- **Google Gemini** — used for interview question generation and answer evaluation
- **OpenAI ChatGPT** — used for code analysis and task generation from GitHub repos

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React |
| AI | Google Gemini API, OpenAI API |
| Database | PostgreSQL |
| ORM | SQLAlchemy, Alembic |
| Cache / Queue | Redis, Celery |
| DevOps | Docker |

---

## 🗂 Project Structure

```
interview-gym/          ← Backend (this repo)
interview-gym-frontend/ ← Frontend (React)
```

Frontend repo: [azazzillo/interview-gym-frontend](https://github.com/azazzillo/interview-gym-frontend)

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- OpenAI API key
- Google Gemini API key

### Run with Docker

```bash
git clone https://github.com/azazzillo/interview-gym.git
cd interview-gym
cp .env.example .env
# Fill in your API keys in .env
docker-compose up --build
```

## 🎓 About

This project was developed as a **bachelor's thesis** at Karaganda Technical University (2026). The goal was to build a practical AI-powered tool that helps developers prepare for technical interviews by combining conversational AI with automated code analysis.

---
