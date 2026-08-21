# Claude Code Rules for Engram

## Project Overview
Engram is an open-source AI memory system that enables AI assistants (Claude, Cursor) to understand and remember entire codebases. It's a local-first, persistent memory layer using the Model Context Protocol (MCP).

## Architecture

```
Files → AST Chunks → Embeddings → FAISS Index → MCP Server → AI
```

### Core Modules (in `engram/`)
- `cli.py` - Command-line interface (Click framework)
- `ingest.py` - File processor, handles PDF/text/code/images
- `server.py` - MCP server exposing 4 tools to AI clients
- `ghost.py` - Background file watcher with incremental updates
- `ast_chunker.py` - AST-aware code parsing (Python/JS/TS)
- `temporal.py` - Time-aware search with git integration
- `git_utils.py` - Git commit parsing and diff extraction

### Tech Stack
- **Python 3.9+** with type hints
- **ML**: sentence-transformers (all-MiniLM-L6-v2), torch, FAISS
- **Document Processing**: langchain ecosystem, pypdf, pytesseract
- **MCP**: mcp>=1.0.0 for AI tool protocol
- **CLI**: Click framework
- **File Watching**: watchdog

## Code Style Guidelines

### Python
- Use type hints for all function parameters and return values
- Docstrings for all public functions (Google style)
- Keep functions focused and under 50 lines when possible
- Use `get_best_device()` pattern for GPU detection (MPS/CUDA/CPU)
- Log to stderr in server code to keep stdout clean for MCP protocol

### Error Handling
- Graceful fallbacks for missing OCR (pytesseract)
- File encoding fallback: UTF-8 → Latin-1
- Never crash on single file failures during batch processing
- Save progress after each batch (crash recovery)

### Naming Conventions
- Modules: snake_case (`ast_chunker.py`)
- Classes: PascalCase (`FileRegistry`, `IncrementalBuilder`)
- Functions: snake_case (`get_best_device`, `needs_processing`)
- Constants: UPPER_SNAKE (`BATCH_SIZE`, `DEVICE`)

## Testing
- Tests in `tests/` directory
- Run: `python -m pytest tests/`
- Minimal coverage currently - prioritize integration tests

## Package Structure
```
engram/
├── __init__.py          # Version and package metadata
├── cli.py               # Entry point: python -m engram.cli
├── ingest.py            # Core indexing logic
├── server.py            # MCP server
├── ghost.py             # File watcher daemon
├── ast_chunker.py       # Code-aware chunking
├── temporal.py          # Time-based search
└── git_utils.py         # Git integration
```

## Key Commands
```bash
# Development
pip install -e .                    # Install in development mode
python -m engram.cli --help         # Run CLI
python -m pytest tests/             # Run tests

# Usage
engram init ~/project               # Index a project
engram query "how does auth work"   # Search memory
engram watch                        # Start file watcher
engram status                       # Check system status
engram setup                        # Configure MCP for Claude/Cursor
```

## Important Patterns

### GPU Detection (use this pattern everywhere)
```python
def get_best_device() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"
```

### MCP Server Tools
The server exposes these tools to AI clients:
1. `query_memory` - Semantic search across indexed files
2. `query_recent` - Search recently modified files
3. `whats_changed` - Get recent changes with git context
4. `explain_file` - Get detailed explanation of a specific file

### Incremental Indexing
- Process files in batches of 100
- Save FAISS index + registry after EACH batch
- Registry tracks file hashes for change detection
- Enables resumable indexing after interruption

## Do Not
- Commit `*_engram/` folders (indexed data)
- Commit `.env` files
- Modify the MCP protocol format without testing with Claude Desktop
- Use synchronous I/O in the file watcher (use threading)

## Website
The `website/` directory contains a Next.js landing page. It's separate from the core Python package and has its own package.json dependencies.
