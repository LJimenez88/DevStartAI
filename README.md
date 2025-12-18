# DevStartAI

DevStartAI is a **template-based project scaffolding tool** that generates **ready-to-run backend starters** with optional databases and Docker support.

It provides a simple UI to choose a stack and configuration, then downloads a **fully working ZIP** you can immediately run locally or with Docker.

---

## Supported Stacks

### Backends
- FastAPI (Python)
- Express (Node.js)

### Databases (optional)
- PostgreSQL
- MySQL
- MongoDB
- SQLite *(intentionally disabled for now)*

---

## How It Works

1. You choose a stack and options in the UI
2. The backend copies a base template plus selected add-ons
3. A `.env` file is auto-generated based on your selections
4. The project is zipped and returned for download
5. You extract and run it locally (**Docker recommended**)

---

## Generated Project Features

Each generated project includes:

- A clean, minimal backend structure
- Example CRUD routes (`/items`)
- Optional database integration
- Optional Docker & Docker Compose setup
- Auto-generated environment variables
- Ready-to-run configuration (no manual setup required)

---

## Async vs Sync Design (FastAPI)

DevStartAI intentionally uses a **hybrid approach**:

- **PostgreSQL / MySQL**  
  Uses synchronous SQLAlchemy (simple, stable, beginner-friendly)

- **MongoDB**  
  Uses async Motor (MongoDB’s native async driver)

FastAPI safely supports mixing `def` and `async def` routes, making this a **production-ready design choice**.

---

## Running Generated Projects

### With Docker (Recommended)

```bash
docker compose up --build

## Running Without Docker (Advanced)

You can also run generated projects locally without Docker, but this requires manual setup.

You will need to:
- Install project dependencies
- Install and run the selected database locally
- Configure environment variables correctly

Docker is strongly recommended to avoid environment and dependency issues.

---

## Environment Variables

Each generated project includes the following environment files:

- `.env`  
  Auto-generated and ready to use based on the selected stack and options.

- `.env.example`  
  A reference template showing all available configuration options.

Database values are generated automatically depending on:
- Selected database engine
- Docker vs local execution mode

---

## Project Structure (Generated)

Example FastAPI project:

```text
app/
├── main.py
├── db.py
├── routes_db_items.py
├── models.py
.env
.env.example
docker-compose.yml
Dockerfile
README.md
requirements.txt

