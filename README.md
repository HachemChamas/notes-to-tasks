# notes-to-tasks

AI agent that turns meeting notes and group chats into assigned tasks on a shared board.

**Where the project is going:** a user pastes meeting notes or group chat
messages, an AI agent extracts tasks with owners and due dates, the user
approves them, and they appear on a shared task board.

**What exists right now:** the skeleton. A FastAPI backend with a `/health`
endpoint, a React page that calls it, and a Postgres database with a `users`
table.

---

## Project layout

```
notes-to-tasks/
├── .env.example          # every environment variable, with safe example values
├── docker-compose.yml    # runs Postgres in Docker
├── backend/              # Python API (FastAPI)
│   ├── app/
│   │   ├── main.py       # the API endpoints (/health, /users)
│   │   ├── config.py     # reads settings from .env
│   │   ├── database.py   # connection to Postgres
│   │   ├── models.py     # database tables as Python classes
│   │   └── schemas.py    # shape of the JSON the API returns
│   ├── alembic/          # database migrations
│   │   └── versions/0001_create_users_table.py
│   ├── tests/            # backend tests (pytest)
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
└── frontend/             # React app (Vite)
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── main.jsx      # starts React
        ├── App.jsx       # the page
        ├── api.js        # calls to the backend
        ├── App.css
        ├── App.test.jsx  # frontend test (Vitest)
        └── setupTests.js
```

## How the pieces talk to each other

```
Browser (React, port 5173)  --HTTP-->  Backend (FastAPI, port 8000)  --SQL-->  Postgres (Docker, port 5432)
```

---

## Running it locally, step by step

### 0. Install the tools (one time)

| Tool | Version | Check with |
| --- | --- | --- |
| [Git](https://git-scm.com/) | any recent | `git --version` |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | any recent | `docker compose version` |
| [Python](https://www.python.org/downloads/) | 3.11 or newer | `python3 --version` (Windows: `python --version`) |
| [Node.js](https://nodejs.org/) | 24 LTS | `node --version` |

Make sure Docker Desktop is **open and running** before step 2.

### 1. Get the code and create your `.env`

```bash
git clone https://github.com/HachemChamas/notes-to-tasks.git
cd notes-to-tasks
cp .env.example .env
```

(Windows PowerShell: `Copy-Item .env.example .env`)

Open `.env` and change `POSTGRES_PASSWORD`. Put the **same** password inside
`DATABASE_URL`. `.env` is ignored by Git, so it never gets committed.

### 2. Start Postgres

From the repo root:

```bash
docker compose up -d
docker compose ps        # STATUS should say "healthy" after a few seconds
```

### 3. Start the backend

Open a terminal in the `backend/` folder:

```bash
cd backend

# Create a virtual environment: a private folder of Python packages for this project.
python3 -m venv .venv

# Activate it (do this every time you open a new terminal):
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\Activate.ps1       # Windows PowerShell

# Install the packages
pip install -r requirements.txt

# Create the tables in the database (runs the migrations)
alembic upgrade head

# Start the API. --reload restarts it whenever you save a file.
uvicorn app.main:app --reload
```

Check it: open http://localhost:8000/health. You should see:

```json
{"status": "ok", "database": "ok"}
```

FastAPI also gives you interactive docs at http://localhost:8000/docs.

### 4. Start the frontend

Open a **second** terminal (keep the backend running) in the `frontend/` folder:

```bash
cd frontend
npm install       # first time only, downloads packages into node_modules/
npm run dev
```

### 5. Open the app

Go to http://localhost:5173. You should see **API: ok** and **Database: ok**.

### Stopping everything

- Backend and frontend: press `Ctrl+C` in their terminals.
- Postgres: `docker compose down` (your data is kept). Use `docker compose down -v` to also delete the data.

---

## Running the tests

The tests don't need Docker or a running backend. They use fake versions
of the database and the API.

```bash
# Backend (in backend/, with the virtual environment activated)
pytest

# Frontend (in frontend/)
npm test
```

Right now the backend prints `1 passed, 1 skipped`. The skipped test is one
of your TODOs (see below).

---

## Your TODOs

Each TODO has a comment block in the code explaining what to do, with hints.
Search the project for `TODO (` to find them.

| # | Where | What |
| --- | --- | --- |
| 1 | `backend/app/main.py` (`list_users`) | Make `GET /users` return every user from the database, oldest first. |
| 2 | `frontend/src/App.jsx` | Add a "Check again" button that re-runs the health check and is disabled while it runs. |
| 3 | `backend/tests/test_health.py` | Write the test for when the database is down: `/health` should say `"database": "unavailable"`. |

### Adding a test user (for TODO 1)

`GET /users` returns an empty list `[]` until there are users. To add one:

```bash
# Open a Postgres shell inside the container (from the repo root).
# Use the POSTGRES_USER and POSTGRES_DB values from your .env.
docker compose exec db psql -U notes -d notes_to_tasks
```

Then, at the `notes_to_tasks=#` prompt:

```sql
INSERT INTO users (email, name) VALUES ('ada@example.com', 'Ada');
SELECT * FROM users;
\q
```

---

## Database migrations, in short

A migration is a script that changes the database's tables. They live in
`backend/alembic/versions/`, and Alembic remembers which ones already ran.

```bash
alembic upgrade head                      # apply all new migrations
alembic downgrade -1                      # undo the last one
alembic revision -m "add tasks table"     # create a new, empty migration file
```

When you change `app/models.py`, write a migration that makes the same change.

---

## Troubleshooting

**`RuntimeError: DATABASE_URL is not set`**
You don't have a `.env` file in the repo root. Do step 1 again.

**`/health` says `"database": "unavailable"`**
Postgres isn't running, or `DATABASE_URL` doesn't match the `POSTGRES_*`
values in `.env`. Run `docker compose ps` and compare the two. The backend
terminal prints the exact error.

**`port is already allocated` / `address already in use` on 5432**
You probably have Postgres installed outside Docker. Set `POSTGRES_PORT=5433`
in `.env`, change the port in `DATABASE_URL` to `5433` too, then run
`docker compose up -d` again.

**Changed the password in `.env` but Postgres still uses the old one?**
Postgres only reads the password the very first time it creates its data.
Run `docker compose down -v` (this deletes the data) and then `docker compose up -d`.

**The page says "Could not reach the backend"**
The backend isn't running, or `VITE_API_URL` is wrong. After you change
`.env`, restart `npm run dev`; Vite only reads `.env` when it starts.

**The browser console shows a CORS error**
`FRONTEND_ORIGIN` in `.env` must exactly match the address in your browser's
address bar (for example `http://localhost:5173`). Restart the backend after
changing it.
