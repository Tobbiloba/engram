# Engram

**Local, persistent memory for AI development workflows.**

Your AI assistant finally remembers your entire codebase.

---

## The Problem

- Cursor forgets your codebase after 5 minutes
- Claude loses context mid-conversation
- Copilot suggests code that conflicts with your architecture
- You keep re-explaining the same things

## The Solution

Engram creates a **persistent memory layer** that any AI can access via MCP.

```bash
# Index your project
engram init ~/my-project

# Configure Claude/Cursor
engram setup

# Done. Your AI now remembers everything.
```

---

## Features

- **Local-first** — Your code never leaves your machine
- **GPU accelerated** — Fast indexing with MPS (Mac) or CUDA
- **MCP native** — Works with Claude Desktop, Cursor, and any MCP client
- **Incremental updates** — Only re-indexes what changed
- **Crash-proof** — Saves progress, resumes if interrupted
- **Portable** — Copy your "memory cartridge" anywhere

### Supported Files

| Type | Extensions |
|------|------------|
| Code | `.py` `.js` `.ts` `.tsx` `.go` `.rs` `.java` `.rb` `.php` `.swift` `.c` `.cpp` |
| Docs | `.pdf` `.txt` `.md` `.rst` |
| Config | `.json` `.yaml` `.yml` `.toml` |
| Images | `.png` `.jpg` `.jpeg` (OCR) |

---

## Quick Start

### Install

```bash
# Clone and setup
git clone https://github.com/Tobbiloba/engram.git
cd engram
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Or one-liner (coming soon):
```bash
curl -sSL https://engram.dev/install | bash
```

### Index Your Project

```bash
# Index current folder
engram init

# Index specific folder
engram init ~/projects/my-app

# Custom output name
engram init ~/projects/my-app -o my_brain
```

### Configure MCP

```bash
engram setup
```

This auto-detects Claude Desktop and Cursor, and configures them.

### Query From Terminal

```bash
engram query "how does authentication work"
```

### Watch for Changes

```bash
engram watch ~/projects/my-app
```

Runs in background, auto-updates index when files change.

---

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Files     │────▶│   Chunks    │────▶│  Vectors    │────▶│   FAISS     │
│  Code/Docs  │     │ 1000 chars  │     │ 384 dims    │     │   Index     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     AI      │◀────│   Results   │◀────│  Semantic   │◀────│ MCP Server  │
│   Claude    │     │  Top 5      │     │   Search    │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **Index** — Engram scans your files and creates chunks
2. **Embed** — Each chunk becomes a 384-dimension vector (local model, no API)
3. **Store** — Vectors saved to FAISS index (fast similarity search)
4. **Query** — MCP server exposes `query_memory` tool to AI assistants
5. **Search** — AI asks questions, gets relevant code/docs back

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `engram init [folder]` | Index a folder |
| `engram query "..."` | Search from terminal |
| `engram watch [folder]` | Start background watcher |
| `engram status` | Show index stats |
| `engram setup` | Auto-configure MCP |

---

## Manual MCP Configuration

If `engram setup` doesn't work, add manually:

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "engram": {
      "command": "/path/to/engram/venv/bin/python",
      "args": ["/path/to/engram/server.py", "/path/to/your_engram"]
    }
  }
}
```

### Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "engram": {
      "command": "/path/to/engram/venv/bin/python",
      "args": ["/path/to/engram/server.py", "/path/to/your_engram"]
    }
  }
}
```

---

## Requirements

- Python 3.9+
- ~2GB disk space (for model + index)
- For OCR: `brew install tesseract poppler`

---

## Tech Stack

- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (runs locally)
- **Vector Store**: FAISS
- **GPU**: MPS (Apple Silicon) / CUDA (NVIDIA) / CPU fallback
- **Protocol**: MCP (Model Context Protocol)

---

## Roadmap

- [x] Local vector indexing
- [x] MCP server
- [x] GPU acceleration
- [x] Incremental updates
- [x] Background watcher
- [ ] Temporal memory (what changed recently?)
- [ ] Git-aware context
- [ ] Architecture insights
- [ ] Desktop app

See [ROADMAP.md](ROADMAP.md) for details.

---

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — Use freely, modify freely, share freely.

---

**Built for developers who are tired of re-explaining their codebase.**
