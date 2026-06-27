from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import markdown
import sqlite3
import os
import base64
import html

# Remap built-in Swagger/ReDoc UIs to /api/* so /docs and /redoc stay free
app = FastAPI(docs_url="/api/docs", redoc_url="/api/redoc")

DB_PATH = "content.db"


# ── DB Setup ─────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                format TEXT NOT NULL CHECK(format IN ('markdown', 'html'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    # Try static/index.html first, then root index.html
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    elif os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return {"message": "Maktaba API running. Place index.html in static/ or root."}


# ── Blog routes (read-only) ───────────────────────────────────────────────────

@app.get("/blogs")
def list_blogs():
    with get_db() as conn:
        rows = conn.execute("SELECT name, format FROM blogs").fetchall()
    return {"blogs": [dict(r) for r in rows]}


@app.get("/blog/{name:path}")   # ← allows slashes in blog names
def get_blog(name: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT content, format FROM blogs WHERE name = ?", (name,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Blog not found")
    content = row["content"]
    if row["format"] == "markdown":
        content = markdown.markdown(content)
    elif row["format"] == "html":
        content = html.unescape(content)
    return {"name": name, "content": content, "format": row["format"]}


@app.delete("/blog/{name:path}")
def delete_blog(name: str):
    with get_db() as conn:
        result = conn.execute("DELETE FROM blogs WHERE name = ?", (name,))
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog deleted", "name": name}


# ── File routes (read-only) ───────────────────────────────────────────────────

@app.get("/files")
def list_files():
    with get_db() as conn:
        rows = conn.execute("SELECT name FROM files").fetchall()
    return {"files": [r["name"] for r in rows]}


@app.get("/file/{name:path}")   # ← allows slashes in file names
def get_file(name: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT content FROM files WHERE name = ?", (name,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="File not found")
    # Decode base64 content (as stored by blogs.py)
    raw = row["content"]
    try:
        decoded = base64.b64decode(raw)
        # Try to decode as UTF-8; if it fails, return the base64 string
        try:
            content = decoded.decode('utf-8')
        except UnicodeDecodeError:
            # Binary file – return base64 string (the frontend can display it)
            content = raw
    except Exception:
        content = raw
    return {"name": name, "content": content}


@app.delete("/file/{name:path}")
def delete_file(name: str):
    with get_db() as conn:
        result = conn.execute("DELETE FROM files WHERE name = ?", (name,))
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted", "name": name}


# ── Markdown doc routes ───────────────────────────────────────────────────────

def _render_md_file(path: str, label: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"{label} file not found")
    with open(path, "r", encoding="utf-8") as f:
        return {"content": markdown.markdown(f.read())}

@app.get("/docs")
def readme():
    return _render_md_file("README.md", "README")

@app.get("/redoc")
def changelog():
    return _render_md_file("CHANGELOG.md", "Changelog")


# ── Static files (must be last) ───────────────────────────────────────────────

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")