# Demo GIF Script

Record with: **CleanShot X**, **Kap**, or **Gifox** (Mac)

---

## Demo 1: Setup (30 seconds)

**What to show:**

```bash
# Terminal - clean, dark theme
cd ~/my-project

# 1. Index project (5 sec)
engram init
# Show: "Indexing... 47 files... Created!"

# 2. Configure MCP (3 sec)
engram setup
# Show: "✓ Claude Desktop configured"
# Show: "✓ Cursor configured"

# 3. Check status (2 sec)
engram status
# Show: index stats
```

**End card:** "Setup complete in 60 seconds"

---

## Demo 2: Temporal Memory (30 seconds)

**What to show:**

```bash
# In Claude Desktop or Cursor

User: "What changed in authentication this week?"

# AI uses query_recent tool
# Show the response with:
# - Recent commits
# - Files changed
# - Commit messages

User: "Explain the auth.ts file"

# AI uses explain_file tool
# Show commit history
```

**End card:** "Your AI finally remembers"

---

## Demo 3: Quick Search (15 seconds)

**What to show:**

```bash
# Terminal
engram query "how does login work"

# Show: 3-5 results with file names
# Show: Content snippets
```

---

## Recording Tips

1. **Clean terminal** - Clear history, use nice prompt
2. **Large font** - 18px minimum
3. **Dark theme** - Looks better in GIF
4. **Slow typing** - Or use a typing simulator
5. **Pause on results** - Let viewer read
6. **720p or 1080p** - Optimize for web
7. **Under 10MB** - Loads fast on GitHub

---

## Tools

- **Recording**: CleanShot X, Kap, Gifox, ScreenFlow
- **Editing**: Gifski (compress), EZGIF (online)
- **Typing sim**: `pv` command or carbon.now.sh for code

---

## Where to Put

1. `website/public/demo.gif` - For landing page
2. `README.md` - Embed directly
3. GitHub releases - Link to

---

## Example README Embed

```markdown
## Quick Start

![Engram Demo](website/public/demo.gif)

```bash
engram init ~/my-project
engram setup
# Done! Ask Claude about your code.
```
```
