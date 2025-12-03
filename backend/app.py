from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv 
import shutil
import os

load_dotenv()

app = FastAPI()

# Allow frontend (Vite) to call this API from the browser
origins_env = os.getenv("ALLOWED_ORIGINS", "")
origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],   # allow all headers
)

# Base directory: backend/
BASE_DIR = Path(__file__).resolve().parent

# Where templates live: backend/templates/
TEMPLATES_DIR = BASE_DIR / "templates"

# Where generated projects will be created: backend/generated/
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)  # make sure it exists

GENERATED_ZIPS_DIR = BASE_DIR / "generated-zips"
GENERATED_ZIPS_DIR.mkdir(parents=True, exist_ok=True)


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
    includeDocker: bool = False
    includeAuth: bool = False
    includeCI: bool = False

    # Allowed values: "none", "postgres", "sqlite"
    dbEngine: str = "none"

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
        id="fastapi-postgres-docker", #reminder to fix the ID for later
        label="FastAPI API Starter",
        description="FastAPI starter with example routes and Postgres-ready config. Optional Addons.",
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
    - Optionally includes Docker/Auth/CI add-ons
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

    # NEW: base + addons layout
    base_dir = template_dir / "base"
    addons_dir = template_dir / "addons"

    # 3) Build a unique folder name in generated/
    safe_name = body.projectName.replace(" ", "-").lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    generated_folder_name = f"{safe_name}-{timestamp}"
    target_dir = GENERATED_DIR / generated_folder_name

    try:
        if base_dir.exists():
            # 4a) Copy only the base template
            shutil.copytree(base_dir, target_dir)

            # Helper to copy an addon folder into target_dir
            def copy_addon(name: str):
                src = addons_dir / name
                if not src.exists():
                    return
                for item in src.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(src)
                        dest = target_dir / rel_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest)

            # 4b) Conditionally add extras
            if body.includeDocker:
                copy_addon("docker")
            if body.includeAuth:
                copy_addon("auth")
            if body.includeCI:
                copy_addon("ci")

            #database engine add-ons
            if body.dbEngine == "postgres":
                copy_addon("db-postgres")
            elif body.dbEngine == "sqlite":
                copy_addon("db-sqlite")
            # If "none", do nothing.

        else:
            # Fallback for stacks that don't use base/addons yet
            shutil.copytree(template_dir, target_dir)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to copy template: {e}",
        )
    
    env_example = template_dir / ".env.example"
    if env_example.exists():
        try:
            shutil.copy2(env_example, target_dir / ".env.example")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to copy env file: {e}",
            )

    # 5) Replace {{PROJECT_NAME}} in README_TEMPLATE.md inside the NEW folder
    readme_template = target_dir / "README_TEMPLATE.md"
    if readme_template.exists():
        try:
            content = readme_template.read_text(encoding="utf-8")
            content = content.replace("{{PROJECT_NAME}}", body.projectName)

            readme_output = target_dir / "README.md"
            readme_output.write_text(content, encoding="utf-8")
            readme_template.unlink()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process README template: {e}",
            )

    # 6) Create a ZIP file from the generated folder
    try:
        zip_base_path = GENERATED_ZIPS_DIR / generated_folder_name
        shutil.make_archive(
            base_name=str(zip_base_path),
            format="zip",
            root_dir=target_dir,
        )
        zip_filename = f"{generated_folder_name}.zip"
        download_url = f"http://localhost:8000/download/{zip_filename}"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create zip archive: {e}",
        )

    # 7) Return response with REAL zip download URL
    return ScaffoldResponse(
        message=f"Project folder created and zipped at {zip_filename}",
        projectName=body.projectName,
        stackId=body.stackId,
        downloadUrl=download_url,
    )

@app.get("/download/{zip_name}")
def download_project(zip_name: str):
    """
    Serves a generated zip file from the generatedZips directory.
    Example: /download/my-app-20251127-044610.zip
    """
    zip_path = GENERATED_ZIPS_DIR / zip_name

    if not zip_path.exists() or not zip_path.is_file():
        raise HTTPException(status_code=404, detail="Zip file not found")

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_name,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )