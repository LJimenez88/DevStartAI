from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import shutil

app = FastAPI()

# Base directory: backend/
BASE_DIR = Path(__file__).resolve().parent

# Where templates live: backend/templates/
TEMPLATES_DIR = BASE_DIR / "templates"

# Where generated projects will be created: backend/generated/
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)  # make sure it exists


# ---------- Models ----------
# -------------------------------------------------------------
# Request model for the /scaffold endpoint
# This describes the shape of the JSON the frontend must send.
#
# FastAPI will:
#   - Validate these fields automatically
#   - Convert the JSON body into a Python object (ScaffoldRequest)
#   - Reject requests that are missing fields or have the wrong types
# -------------------------------------------------------------
class ScaffoldRequest(BaseModel):
    # Name of the project folder the user wants to generate
    projectName: str = Field(..., min_length=1, max_length=100)

    # Which template stack to use (must match AVAILABLE_STACKS)
    stackId: str

    # Optional features the user can toggle in the UI
    includeDocker: bool = True
    includeAuth: bool = False
    includeCI: bool = False

# -------------------------------------------------------------
# Response model for /scaffold
# This describes what our API will return back to the frontend.
#
# FastAPI automatically:
#   - Converts this Python object into JSON
#   - Shows this model in the Swagger docs
#   - Ensures we only return the fields we define here
# -------------------------------------------------------------
class ScaffoldResponse(BaseModel):
    # Human-readable message (ex: "Project generated successfully")
    message: str

    # Echo back the projectName and stackId so the frontend can use them
    projectName: str
    stackId: str

    # URL where the generated ZIP file can be downloaded
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
    """
    Accepts a ScaffoldRequest with project configuration.
    - Validates the stackId
    - Copies the chosen template into backend/generated/
    - Replaces {{PROJECT_NAME}} in the README template
    """

    # 1) Validate stackId against AVAILABLE_STACKS
    valid_stack_ids = [stack.id for stack in AVAILABLE_STACKS]
    if body.stackId not in valid_stack_ids:
        raise HTTPException(status_code=400, detail="Invalid stackId")

    # 2) Build the path to the chosen template folder
    template_dir = TEMPLATES_DIR / body.stackId
    if not template_dir.exists() or not template_dir.is_dir():
        raise HTTPException(
            status_code=500,
            detail=f"Template folder not found for stackId='{body.stackId}'",
        )

    # 3) Build a unique folder name in generated/
    safe_name = body.projectName.replace(" ", "-").lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    generated_folder_name = f"{safe_name}-{timestamp}"
    target_dir = GENERATED_DIR / generated_folder_name

    try:
        # 4) Copy the entire template folder into generated/
        shutil.copytree(template_dir, target_dir)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to copy template: {e}",
        )

    # 5) Replace {{PROJECT_NAME}} in README_TEMPLATE.md inside the NEW folder
    readme_template = target_dir / "README_TEMPLATE.md"
    if readme_template.exists():
        try:
            content = readme_template.read_text(encoding="utf-8")
            content = content.replace("{{PROJECT_NAME}}", body.projectName)

            readme_output = target_dir / "README.md"
            readme_output.write_text(content, encoding="utf-8")

            # Delete the template version so only README.md remains
            readme_template.unlink()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process README template: {e}",
            )

    # 6) Still using a fake zip name for now
    fake_zip_name = f"{generated_folder_name}.zip"
    fake_download_url = f"http://localhost:8000/download/{fake_zip_name}"

    return ScaffoldResponse(
        message=f"Project folder created at {target_dir}",
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