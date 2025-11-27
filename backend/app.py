from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"Message: Hello FastAPI is working"}

@app.get("/health")
def health():
    return {"ok" : True}

@app.get("/stacks")
def list_stacks():
    stacks = [
        {
            "id": "fastapi-postgres-docker",
            "label": "FastAPI + Postgres + Docker",
            "description": "Backend-only stack with REST API, Postgres, Docker Compose.",
        },
        {
            "id": "express-mongo-docker",
            "label": "Express + Mongo + Docker",
            "description": "Node/Express API with MongoDB and Docker Compose.",
        },
        {
            "id": "react-spa",
            "label": "React SPA",
            "description": "Client-side React app with Vite.",
        },
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