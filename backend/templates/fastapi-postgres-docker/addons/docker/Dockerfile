FROM python:3.13-slim

WORKDIR /app

# Install system deps (if you later need Postgres client libs, add them here)
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Uvicorn with hot reload disabled (this is for running the generated app)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
