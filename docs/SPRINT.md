# Engram - 2 Week Sprint

> **Goal**: Ship CLI + Smart Temporal Memory + Launch on Reddit/HN

---

## Week 1: Perfect DX (Days 1-7)

### Day 1-2: Project Setup + Installer
- [x] Create GitHub repo
- [x] Add .gitignore
- [x] Add LICENSE (MIT)
- [x] Create proper package structure
- [x] Create `setup.py` for pip install
- [x] Create `scripts/install.sh` (one-liner installer)
- [ ] Test installer on clean system

### Day 3-4: CLI Wrapper
- [x] Create `engram/cli.py`
- [x] `engram init` - Index current/specified folder
- [x] `engram query "..."` - Search from terminal
- [x] `engram watch` - Start Ghost
- [x] `engram status` - Show index stats
- [x] `engram setup` - Auto-configure MCP

### Day 5-7: Auto MCP Setup
- [x] Detect Cursor installation
- [x] Detect Claude Desktop installation
- [x] Auto-generate MCP config
- [x] Show clear success message
- [ ] Test on fresh Cursor install
- [ ] Test on fresh Claude Desktop install

---

## Week 2: Smart Temporal Memory (Days 8-14)

### Day 8-9: Git Integration
- [x] Create `engram/git_utils.py`
- [x] Parse `git log` for recent commits
- [x] Extract commit messages
- [x] Get file diffs per commit
- [x] Link files to commits

### Day 10-11: query_recent Tool
- [x] Create `engram/temporal.py`
- [x] Combine semantic search + time filtering
- [x] Include git commit context in results
- [x] Show related files
- [x] Add to MCP server

### Day 12-13: whats_changed Tool
- [x] Summary of recent activity
- [x] Group by feature/area
- [x] Human-readable output
- [x] Add to MCP server

### Day 14: Polish + Demo
- [ ] Record 60-second setup GIF
- [ ] Record Temporal Memory demo GIF
- [ ] Update README with GIFs
- [ ] Write launch post drafts

---

## Week 3: Soft Launch

### Launch Prep
- [ ] Final README polish
- [ ] HN skeptic answers ready
- [ ] r/LocalLLaMA post drafted
- [ ] Twitter thread drafted
- [ ] Landing page (optional)

### Launch
- [ ] Post on r/LocalLLaMA
- [ ] Post on r/cursor
- [ ] Post on Twitter/X
- [ ] Submit to Hacker News (Show HN)

### Post-Launch
- [ ] Monitor comments
- [ ] Respond to issues
- [ ] Collect feedback
- [ ] Prioritize fixes

---

## Progress Tracker

| Day | Date | Focus | Status |
|-----|------|-------|--------|
| 1 | Feb 21 | Project setup | ✅ Complete |
| 2 | Feb 21 | CLI + Installer | ✅ Complete |
| 3-4 | Feb 21 | CLI commands | ✅ Complete |
| 5-7 | Feb 21 | MCP auto-config | ✅ Complete |
| 8-9 | Feb 21 | Git integration | ✅ Complete |
| 10-11 | Feb 21 | query_recent | ✅ Complete |
| 12-13 | Feb 21 | whats_changed | ✅ Complete |
| 14 | | Demo + README | ⬜ Not Started |

---

## What's Done (Day 1)

**Shipped in one session:**

1. **GitHub Repo**: https://github.com/Tobbiloba/engram
2. **CLI** (`engram` command):
   - `engram init` - Index folders
   - `engram query` - Search from terminal
   - `engram watch` - Background watcher
   - `engram status` - Show stats
   - `engram setup` - Auto-configure MCP
3. **Smart Temporal Memory**:
   - `query_recent` - Time-aware search
   - `whats_changed` - Git activity summary
   - `explain_file` - File history
4. **Git Integration**: Full commit history parsing

---

## Remaining Tasks

1. [ ] Record demo GIFs
2. [ ] Polish README with GIFs
3. [ ] Write launch posts
4. [ ] Soft launch

---

## Quick Commands

```bash
# Development
cd /Users/MAC/Documents/projects/Startups/engram
source venv/bin/activate

# Test CLI locally
pip install -e .
engram --help

# Run tests
pytest tests/

# Check current index
engram status

# Test temporal memory
python -c "from engram.git_utils import get_activity_summary; print(get_activity_summary('.', 7))"
```

---

## Notes

- Ship ugly, refine after feedback
- Don't over-polish before launch
- Get to 100 users before optimizing
- **We crushed Week 1 + Week 2 in one day!**
