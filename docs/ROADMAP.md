# Project Engram - Roadmap

> **Vision**: Local, persistent memory for AI development workflows.

---

## Completed Phases

### Phase 1: Core Foundation ✅
*Basic ingestion + MCP server*

- [x] PDF document support
- [x] Text file support (.txt, .md, .rst)
- [x] Recursive folder scanning
- [x] Local embeddings (sentence-transformers)
- [x] FAISS vector storage
- [x] MCP Server with `query_memory` tool
- [x] Semantic search (meaning-based)

### Phase 2: Omni-Reader ✅
*OCR + multi-format support*

- [x] OCR for scanned PDFs (Tesseract)
- [x] Image file support (.png, .jpg, .jpeg)
- [x] Mixed PDF handling (text + scanned pages)
- [x] Source type metadata tracking
- [x] Code file support (.py, .js, .ts, .go, etc.)
- [x] Config file support (.json, .yaml, .toml)

### Phase 3: Ghost File Watcher ✅
*Background auto-indexing*

- [x] Background file watcher (watchdog)
- [x] Smart ignore list (node_modules, .git, cache)
- [x] Auto-rebuild on file changes
- [x] Debounce (2 seconds)

### Phase 4: Crash-Proof Indexing ✅
*Incremental updates + recovery*

- [x] Process files in batches (100 at a time)
- [x] Save progress after EVERY batch
- [x] Resume from where it stopped
- [x] Only re-process new/changed files
- [x] File registry tracking (hash + timestamp)

### Phase 5: GPU Acceleration ✅
*5-10x faster embeddings*

- [x] Auto-detect best device (CUDA/MPS/CPU)
- [x] Apple Silicon (MPS) support
- [x] NVIDIA GPU (CUDA) support
- [x] Graceful fallback to CPU
- [x] GPU support in ingest.py, ghost.py, server.py

### Phase 6: Developer Experience ✅
*CLI + easy setup*

- [x] `engram` CLI command
- [x] `engram init` - Index folders
- [x] `engram query` - Search from terminal
- [x] `engram watch` - Start Ghost
- [x] `engram status` - Show index stats
- [x] `engram setup` - Auto-configure MCP
- [x] One-liner installer script
- [x] setup.py for pip install

### Phase 7: Smart Temporal Memory ✅
*The killer feature - time-aware search*

- [x] Git integration (engram/git_utils.py)
- [x] Parse git log for recent commits
- [x] Extract commit messages and diffs
- [x] Link files to commits
- [x] `query_recent` MCP tool - time-aware search
- [x] `whats_changed` MCP tool - activity summary
- [x] `explain_file` MCP tool - file history

---

## Current Phase

### Phase 8: Launch Prep 🟡
*Demo + soft launch*

- [ ] Record 60-second setup demo GIF
- [ ] Record Temporal Memory demo GIF
- [ ] Update README with GIFs
- [ ] Write HN skeptic answers
- [ ] Draft r/LocalLLaMA post
- [ ] Draft Twitter thread
- [ ] Soft launch on Reddit

---

## Future Phases

### Phase 9: Architecture Insight
*Screenshot-worthy feature*

**Priority**: HIGH (next killer feature)

- [ ] `explain_architecture` MCP tool
- [ ] Auto-detect project structure
- [ ] Identify domains/modules
- [ ] Count files and lines per area
- [ ] Show key dependencies
- [ ] Generate human-readable summary

Example output:
```
"This is a Next.js app with 3 main domains:

📁 Authentication (src/auth/)
   - JWT-based with refresh tokens
   - 4 files, 847 lines

📁 API Layer (src/api/)
   - REST endpoints with Prisma ORM
   - 12 files, 2,340 lines
..."
```

### Phase 10: Desktop App
*Pro tier differentiator*

**Priority**: MEDIUM (after launch traction)

- [ ] Menu bar app (macOS)
- [ ] System tray (Windows)
- [ ] Quick search hotkey (Cmd+Shift+E)
- [ ] Drag & drop indexing
- [ ] Status indicator
- [ ] Built with Tauri or Electron

### Phase 11: Hybrid Search
*Semantic + keyword search*

**Priority**: MEDIUM

- [ ] BM25 keyword retriever
- [ ] Ensemble retriever (50/50 blend)
- [ ] Exact match boosting
- [ ] Better for function names, IDs, specific terms

### Phase 12: Smarter Chunking
*Better search quality*

**Priority**: MEDIUM

- [ ] Code-aware chunking (respect function boundaries)
- [ ] Markdown structure awareness
- [ ] Semantic chunking (split by meaning)
- [ ] Language-specific splitters

### Phase 13: Multiple Cartridges
*Manage multiple projects*

**Priority**: LOW

- [ ] `engram list` - List all cartridges
- [ ] `engram switch <name>` - Switch active cartridge
- [ ] `engram merge` - Merge cartridges
- [ ] Cross-cartridge search

### Phase 14: Team Features
*Shared knowledge bases*

**Priority**: LOW (need individual traction first)

- [ ] Shared cartridges
- [ ] Access control
- [ ] Sync across devices
- [ ] Admin dashboard

### Phase 15: Additional Formats
*More file types*

**Priority**: LOW

- [ ] .docx (Word)
- [ ] .xlsx (Excel)
- [ ] .pptx (PowerPoint)
- [ ] .epub (eBooks)
- [ ] Audio transcription (Whisper)
- [ ] Video transcription

---

## Phase Priority Matrix

| Phase | Name | Priority | Effort | Status |
|-------|------|----------|--------|--------|
| 1-7 | Foundation → Temporal Memory | - | - | ✅ Done |
| 8 | Launch Prep | HIGH | Low | 🟡 Current |
| 9 | Architecture Insight | HIGH | Medium | ⬜ Next |
| 10 | Desktop App | MEDIUM | High | ⬜ Planned |
| 11 | Hybrid Search | MEDIUM | Medium | ⬜ Planned |
| 12 | Smarter Chunking | MEDIUM | Medium | ⬜ Planned |
| 13 | Multiple Cartridges | LOW | Medium | ⬜ Backlog |
| 14 | Team Features | LOW | High | ⬜ Backlog |
| 15 | Additional Formats | LOW | Medium | ⬜ Backlog |

---

## Strategic Timeline

### Now → Month 6: Dominate Dev Memory
- ✅ Ship CLI + Temporal Memory
- 🟡 Launch on Reddit/HN/Twitter
- ⬜ Get 1,000+ users
- ⬜ Collect feedback
- ⬜ Hit $1-3K MRR

### Month 6-12: Solidify Position
- ⬜ Ship desktop app (Pro tier)
- ⬜ Add Architecture Insight
- ⬜ Product Hunt launch
- ⬜ Hit $5-10K MRR

### Year 2+: Expand to Agent Ecosystem
- ⬜ Plugin system
- ⬜ Team features
- ⬜ Integrations beyond IDEs
- ⬜ Position as "memory infrastructure"

---

## How to Track Progress

**For this project, we use:**

1. **SPRINT.md** - Current 2-week sprint tasks
2. **ROADMAP.md** - This file, high-level phases
3. **GitHub Issues** - Bug reports and feature requests
4. **GitHub Projects** - Kanban board (optional)

**Quick status check:**
```bash
# See what's done
grep -E "^\- \[x\]" docs/ROADMAP.md | wc -l

# See what's pending
grep -E "^\- \[ \]" docs/ROADMAP.md | wc -l
```

---

*Last Updated: February 2026*
