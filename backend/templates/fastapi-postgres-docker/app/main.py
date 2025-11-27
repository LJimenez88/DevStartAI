from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello from your generated FastAPI-Postgress-Docker project!"}
