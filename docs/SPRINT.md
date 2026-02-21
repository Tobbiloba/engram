# Engram - 2 Week Sprint

> **Goal**: Ship CLI + Smart Temporal Memory + Launch on Reddit/HN

---

## Week 1: Perfect DX (Days 1-7)

### Day 1-2: Project Setup + Installer
- [x] Create GitHub repo
- [x] Add .gitignore
- [x] Add LICENSE (MIT)
- [x] Create proper package structure
- [ ] Create `setup.py` for pip install
- [ ] Create `scripts/install.sh` (one-liner installer)
- [ ] Test installer on clean system

### Day 3-4: CLI Wrapper
- [ ] Create `engram/cli.py`
- [ ] `engram init` - Index current/specified folder
- [ ] `engram query "..."` - Search from terminal
- [ ] `engram watch` - Start Ghost
- [ ] `engram status` - Show index stats
- [ ] `engram setup` - Auto-configure MCP

### Day 5-7: Auto MCP Setup
- [ ] Detect Cursor installation
- [ ] Detect Claude Desktop installation
- [ ] Auto-generate MCP config
- [ ] Show clear success message
- [ ] Test on fresh Cursor install
- [ ] Test on fresh Claude Desktop install

---

## Week 2: Smart Temporal Memory (Days 8-14)

### Day 8-9: Git Integration
- [ ] Create `engram/git_utils.py`
- [ ] Parse `git log` for recent commits
- [ ] Extract commit messages
- [ ] Get file diffs per commit
- [ ] Link files to commits

### Day 10-11: query_recent Tool
- [ ] Create `engram/temporal.py`
- [ ] Combine semantic search + time filtering
- [ ] Include git commit context in results
- [ ] Show related files
- [ ] Add to MCP server

### Day 12-13: whats_changed Tool
- [ ] Summary of recent activity
- [ ] Group by feature/area
- [ ] Human-readable output
- [ ] Add to MCP server

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
| 1 | | Project setup | 🟡 In Progress |
| 2 | | Installer | ⬜ Not Started |
| 3 | | CLI init/query | ⬜ Not Started |
| 4 | | CLI watch/status/setup | ⬜ Not Started |
| 5 | | MCP auto-config | ⬜ Not Started |
| 6 | | MCP testing | ⬜ Not Started |
| 7 | | Buffer/polish | ⬜ Not Started |
| 8 | | Git integration | ⬜ Not Started |
| 9 | | Git integration | ⬜ Not Started |
| 10 | | query_recent | ⬜ Not Started |
| 11 | | query_recent | ⬜ Not Started |
| 12 | | whats_changed | ⬜ Not Started |
| 13 | | whats_changed | ⬜ Not Started |
| 14 | | Demo + README | ⬜ Not Started |

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
```

---

## Notes

- Ship ugly, refine after feedback
- Don't over-polish before launch
- Get to 100 users before optimizing
