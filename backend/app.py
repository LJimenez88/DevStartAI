from fastapi import FastAPI
from pydantic import BaseModel #used to autogenerate schemas
from typing import List

app = FastAPI()

class Stack(BaseModel):#class for the /stacks API
    id:str
    label:str
    description:str

@app.get("/")
def home():
    return {"Message: Hello FastAPI is working"}

@app.get("/health")
def health():
    return {"ok" : True}

@app.get("/stacks")
def list_stacks():
    stacks = [
        Stack(
            id="fastapi-postgres-docker",
            label="FastAPI + Postgres + Docker",
            description="Backend-only stack with REST API, Postgres, Docker Compose.",
        ),
        Stack(
            id="express-mongo-docker",
            label="Express + Mongo + Docker",
            description="Node/Express API with Mongo and Docker Compose.",
        ),
        Stack(
            id="react-spa",
            label="React SPA",
            description="Client-side React app with Vite.",
        ),
    ]
    return stacks






if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )