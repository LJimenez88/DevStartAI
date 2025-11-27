from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()


# ---------- Models ----------

class ScaffoldRequest(BaseModel):
    projectName: str = Field(..., min_length=1, max_length=100)
    stackId: str
    includeDocker: bool = True
    includeAuth: bool = False
    includeCI: bool = False


class ScaffoldResponse(BaseModel):
    message: str
    projectName: str
    stackId: str
    downloadUrl: Optional[str] = None


class Stack(BaseModel):  # class for the /stacks API
    id: str
    label: str
    description: str


# ---------- Data ----------

AVAILABLE_STACKS: List[Stack] = [
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


# ---------- Routes ----------

@app.get("/")
def home():
    return {"message": "Hello FastAPI is working"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/stacks", response_model=List[Stack])
def list_stacks():
    return AVAILABLE_STACKS


@app.post("/scaffold", response_model=ScaffoldResponse)
def scaffold_project(body: ScaffoldRequest):
    # 1) Validate the stackId
    valid_stack_ids = [stack.id for stack in AVAILABLE_STACKS]
    if body.stackId not in valid_stack_ids:
        raise HTTPException(status_code=400, detail="Invalid stackId")

    # 2) For now, we don't actually create folders or zip.
    fake_zip_name = f"{body.projectName}-dummy.zip"
    fake_download_url = f"http://localhost:8000/download/{fake_zip_name}"

    return ScaffoldResponse(
        message="Scaffold request received (no files generated yet).",
        projectName=body.projectName,
        stackId=body.stackId,
        downloadUrl=fake_download_url,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
