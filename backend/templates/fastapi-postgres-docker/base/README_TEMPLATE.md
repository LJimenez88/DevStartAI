# {{PROJECT_NAME}}

This project was generated using DevStart AI.

## How to run (without Docker)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

## Run with Docker

1. Copy env file

   ```bash
   cp .env.example .env

2. docker-compose up --build
