# Changelog

All notable changes to OpenNoorIlm are documented here.

---

## [0.3.0] — Desktop editor

### Added
- `blogs.py` — PyQt5 desktop blog editor with Islamic-modern dark theme
- Markdown syntax highlighting in the editor (headings, bold, links, code, blockquotes)
- **Import file** button — pick any `.md` or `.html` file and insert it into the database
- **Import folder** button — batch-import all `.md`/`.html` files from a directory
- CLI import mode: `python blogs.py import file.md` or `python blogs.py import ./folder/`
- Live character count in the editor footer
- Unsaved-changes guard on close and when switching between posts
- Auto-save hint after 5 seconds of inactivity

### Changed
- Format field now stored explicitly as `markdown` or `html` — no more guessing from content
- Switching format (markdown ↔ html) no longer clears or rewrites the editor content

### Fixed
- `QRegExp` moved to `PyQt5.QtCore` import (was incorrectly in `QtGui`)
- `QSyntaxHighlighter` abstract class crash when switching to HTML mode — highlighter is now properly detached via `setDocument(None)` and set to `None` for HTML

---

## [0.2.0] — SQLite backend

### Added
- SQLite database (`content.db`) replaces filesystem for both blogs and files
- Full CRUD routes for blogs and files on the server

### Changed
- Markdown bug fixed: `markdown.Markdown.convert()` → `markdown.markdown()`
- Error responses now use FastAPI `HTTPException` with proper status codes instead of `{"error": "..."}` dicts
- Path traversal vulnerability removed — filenames no longer passed directly to `open()`

### Removed
- `POST /blog` and `PUT /blog` — server is now read-only; only `blogs.py` can create content
- `POST /file` and `PUT /file` — same reason

---

## [0.1.0] — Initial version

### Added
- FastAPI server with filesystem-based blog and file serving
- `GET /blog/{name}` — serve `.md` or `.html` files from `blogs/` directory
- `GET /blogs` — list all blog files
- `GET /files` — list all files
- `GET /file/{name}` — read a file from `files/` directory
- Static file serving from `static/`

### Known issues (fixed in 0.2.0)
- `markdown.Markdown.convert()` raises `TypeError` — incorrect API usage
- Dead `else` branch in blog format detection (unreachable code)
- No error handling if `blogs/` or `files/` directory is missing
- Path traversal risk via unsanitised filename in `open()`
