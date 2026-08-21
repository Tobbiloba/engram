# Engram - Project Status

> **Last Updated**: March 2026

## What is Engram?

**Engram** is an open-source AI memory system that enables AI assistants (Claude, Cursor) to understand and remember your entire codebase. It's a local-first, persistent memory layer that connects via the Model Context Protocol (MCP).

**Problem**: AI assistants forget context after 5 minutes
**Solution**: Engram creates a searchable "memory cartridge" of your code

### Key Features
- **Semantic Search**: Ask "how does authentication work?" and get relevant code
- **Temporal Memory**: Know what changed recently (killer feature)
- **Local-First**: Your code never leaves your machine
- **GPU Accelerated**: Fast indexing on Apple Silicon (MPS) or NVIDIA (CUDA)
- **AST-Aware**: Understands code structure, not just text

---

## Current State

### Version: 0.2.0 (PyPI: `engram-dev`)

### Completion Status

| Phase | Name | Status |
|-------|------|--------|
| 1 | Core Foundation | Done |
| 2 | Omni-Reader (OCR + formats) | Done |
| 3 | Ghost File Watcher | Done |
| 4 | Crash-Proof Indexing | Done |
| 5 | GPU Acceleration | Done |
| 6 | Developer Experience (CLI) | Done |
| 7 | Smart Temporal Memory | Done |
| 8 | Launch Prep | In Progress |
| 9 | Architecture Insight | Planned |
| 10+ | Desktop App, Hybrid Search, etc. | Backlog |

**7 of 15 phases complete** - Core product is fully functional

---

## Project Structure

```
engram/
├── engram/                     # Python package (3,100+ LOC)
│   ├── __init__.py            # v0.2.0
│   ├── cli.py                 # CLI interface (Click)
│   ├── ingest.py              # File processor
│   ├── server.py              # MCP server (4 tools)
│   ├── ghost.py               # Background file watcher
│   ├── ast_chunker.py         # AST-aware code parsing
│   ├── temporal.py            # Time-aware search
│   └── git_utils.py           # Git integration
│
├── website/                    # Next.js landing page
│   ├── app/                   # Next.js app router
│   ├── package.json           # React 19, Tailwind 4
│   └── ...
│
├── docs/                       # Documentation
│   ├── ROADMAP.md             # 15-phase plan
│   ├── PLAN.md                # Business strategy
│   └── SPRINT.md              # Current sprint
│
├── tests/                      # Test suite (minimal)
│   └── test_basic.py          # 3 basic tests
│
├── scripts/
│   └── install.sh             # One-liner installer
│
├── setup.py                    # PyPI package config
├── requirements.txt            # Python dependencies
├── CLAUDE.md                   # Claude Code rules
├── README.md                   # Main documentation
└── LICENSE                     # MIT
```

---

## Technology Stack

### Backend (Python 3.9+)
| Component | Technology |
|-----------|------------|
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS (CPU) |
| ML Framework | PyTorch 2.0+ |
| Doc Processing | LangChain ecosystem |
| PDF | pypdf |
| OCR | pytesseract (optional) |
| MCP | mcp>=1.0.0 |
| CLI | Click |
| File Watching | watchdog |

### Frontend (Website)
| Component | Technology |
|-----------|------------|
| Framework | Next.js 16 |
| UI | React 19 |
| Styling | Tailwind CSS 4 |
| Animation | Framer Motion, GSAP |

### Hardware Support
- Apple Silicon: MPS acceleration
- NVIDIA: CUDA acceleration
- Fallback: CPU

---

## MCP Tools Exposed

The server exposes 4 tools to AI clients:

| Tool | Purpose |
|------|---------|
| `query_memory` | Semantic search across indexed files |
| `query_recent` | Search recently modified files |
| `whats_changed` | Get recent changes with git context |
| `explain_file` | Get detailed explanation of a specific file |

---

## Installation & Usage

### Quick Install
```bash
pip install engram-dev
```

### Commands
```bash
engram init ~/project       # Index a project
engram query "how does X"   # Search memory
engram watch               # Start file watcher
engram status              # Check system status
engram setup               # Configure MCP for Claude/Cursor
```

### MCP Configuration
After running `engram setup`, Claude Desktop will have access to your codebase memory.

---

## What's Working

- Full CLI with all commands
- PDF, text, code, image (OCR) processing
- GPU-accelerated embeddings (5-10x faster)
- Incremental indexing with crash recovery
- Background file watching with auto-rebuild
- AST-aware chunking for Python/JS/TS
- Git integration for temporal context
- MCP server with 4 tools
- PyPI package published

---

## What's Not Done Yet

- Demo GIFs for README
- Architecture Insight tool
- Desktop app (menu bar)
- Hybrid search (semantic + keyword)
- Team features
- Comprehensive test coverage
- CONTRIBUTING.md

---

## Files Removed (Cleanup)

These legacy files were removed as they were duplicates of the package modules:
- `/ghost.py` (duplicate of `engram/ghost.py`)
- `/ingest.py` (duplicate of `engram/ingest.py`)
- `/server.py` (duplicate of `engram/server.py`)
- `/__pycache__/` (build artifact)

---

## Development Setup

```bash
# Clone
git clone https://github.com/Tobbiloba/engram.git
cd engram

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev,ocr]"

# Run tests
pytest tests/

# Run CLI
engram --help
```

---

## Metrics

| Metric | Value |
|--------|-------|
| Python LOC | ~3,100 |
| Modules | 7 |
| MCP Tools | 4 |
| Supported File Types | 30+ |
| Test Coverage | Minimal (3 tests) |
| PyPI Version | 0.2.0 |

---

## Next Steps (Priority Order)

1. **Record demo GIFs** - Show setup and temporal memory in action
2. **Launch on Reddit/HN** - Get first 1,000 users
3. **Architecture Insight tool** - Next killer feature
4. **Improve test coverage** - Integration tests for core flows
5. **Desktop app** - Menu bar app for Pro tier

---

## Links

- **PyPI**: https://pypi.org/project/engram-dev/
- **GitHub**: https://github.com/Tobbiloba/engram
- **License**: MIT
