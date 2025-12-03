FROM python:3.13-slim

# Make Python output unbuffered (logs appear immediately)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (if you later need Postgres client libs, add them here)
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run the FastAPI app
# Assumes your generated project has app/main.py with `app = FastAPI(...)`
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
