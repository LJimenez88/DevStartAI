# {{PROJECT_NAME}}

This project was generated using DevStart AI.

## How to run (without Docker)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
