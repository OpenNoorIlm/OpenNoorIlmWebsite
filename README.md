# OpenNoorIlm — مكتبة النور

> A self-hosted Islamic knowledge blog platform. Blogs are written offline via a desktop editor and served read-only through a FastAPI backend.

---

## Project structure

```
OpenNoorIlm/
├── main.py          # FastAPI server (read-only API)
├── blogs.py         # PyQt5 desktop blog editor (writes to DB) — not in git
├── content.db       # SQLite database (auto-created) — not in git
├── README.md        # This file
├── CHANGELOG.md     # Version history
└── static/
    └── index.html   # Islamic-modern frontend UI
```

---

## Requirements

```
fastapi
uvicorn
markdown
pyqt5
```

Install all at once:

```bash
pip install fastapi uvicorn markdown pyqt5
```

---

## Running the server

```bash
uvicorn main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

Swagger API docs are at [http://localhost:8000/api/docs](http://localhost:8000/api/docs).

---

## Writing blogs

Open the desktop editor:

```bash
python blogs.py
```

- Write your post in the editor (Markdown or HTML)
- Give it a filename/slug e.g. `my-first-post.md`
- Click **Save to DB** — it goes straight into `content.db`
- The server picks it up instantly, no restart needed

### Importing existing files

Single file:
```bash
python blogs.py import my-post.md
python blogs.py import article.html
```

Entire folder:
```bash
python blogs.py import ./posts/
```

All `.md` and `.html` files in the folder are imported in one shot.

---

## API endpoints

### Blogs

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/blogs` | List all blog posts |
| `GET` | `/blog/{name}` | Get a single post (markdown rendered to HTML) |
| `DELETE` | `/blog/{name}` | Delete a post |

### Files

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/files` | List all files |
| `GET` | `/file/{name}` | Get file content |
| `DELETE` | `/file/{name}` | Delete a file |

### Docs

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/readme` | This README rendered as HTML |
| `GET` | `/changelog` | Changelog rendered as HTML |
| `GET` | `/api/docs` | Swagger UI |
| `GET` | `/api/redoc` | ReDoc UI |

> **Note:** There are no `POST` or `PUT` routes on the server. Content can only be created or edited through `blogs.py`.

---

## Design philosophy

- The **server is read-only**. It cannot create or modify content.
- The **desktop editor** (`blogs.py`) is the only way to write blogs. It talks directly to the SQLite database, bypassing the server entirely.
- `blogs.py` is excluded from git (see `.gitignore`) — it stays on your local machine only.
- This keeps the public-facing API safe — no one can inject content through HTTP.

---

## License

MIT — free to use, modify, and distribute.
