# TaskCircuit – Your Task Manager

TaskCircuit is a minimalist, iOS-inspired task manager where users log in using a unique 6-digit key, prioritize their tasks, and track daily history with smooth, native-like animations.

## Table of Contents
- Features
- Screenshots
- Tech Stack
- Getting Started
- Project Structure
- Usage
- Roadmap
- License

## Features
- 🔐 Unique 6-digit key login with weak-pattern detection (no 000000, 123456, etc.).
- ✅ Today-focused dashboard showing only today's tasks by default.
- ⭐ Task priorities (Low / Medium / High) with visual emphasis for important work.
- 📅 Date-based history to review past days and see what was completed.
- ⏭️ Schedule tomorrow and future tasks that automatically appear on the right day.
- 🌗 Manual CSS with light/dark theme toggle.
- 🧑‍💻 User profile to view/update key-related settings and theme preferences.


## Tech Stack
- Backend: Django
- Database: SQLite/PostgreSQL
- Frontend: HTML, manual CSS (no UI frameworks), and Javascript
- Auth: Django auth + custom 6-digit key mapping (Python)

## Getting Started

### Prerequisites
- Python 3.x
- pip

### Installation
```bash
git clone https://github.com/Prajwalg9/taskcircuit-task-manager.git
cd taskcircuit-task-manager
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
