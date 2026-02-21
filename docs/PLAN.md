# Project Engram - Business Plan v3

> **One-liner**: "Local, persistent memory for AI development workflows."

---

## The Vision

**Phase 1**: Dominate dev memory use case (IDE users, codebases)
**Phase 2**: Expand to AI agent ecosystem

Don't dilute focus too early. 90% of initial traction comes from developers.

---

## Positioning

**Category**: Local, persistent memory for AI development workflows

**Not**: "Just a Cursor plugin" or "better RAG"
**Not**: Abstract "memory layer for AI agents" (too vague for launch)

**We are**: The local, private, hackable memory layer that makes your AI actually understand your codebase.

**Our wedge against big tech:**
- They'll be cloud-first → We're local
- They'll store your code → We don't
- They'll be opaque → We're transparent
- They'll be locked → We're hackable

**Lean into**: Privacy + Control + Ownership

---

## What We Have (Built)

| Feature | Status |
|---------|--------|
| Local Vector Database (FAISS) | ✅ |
| PDF/Text/Markdown/Code support | ✅ |
| OCR (scanned docs, images) | ✅ |
| MCP Server (Claude/Cursor) | ✅ |
| Semantic Search | ✅ |
| Background Watcher (Ghost) | ✅ |
| Incremental Updates | ✅ |
| Crash Recovery | ✅ |
| GPU Acceleration (MPS/CUDA) | ✅ |
| Portable Cartridges | ✅ |

**This is 60-70% of the technical complexity. Done.**

---

## Killer Feature #1: Smart Temporal Memory

> "If it's just 'show files modified in 7 days' it won't feel magical."

### What Makes It Smart

| Basic (Don't do) | Smart (Do this) |
|------------------|-----------------|
| File modified time | Git commit context |
| List of files | Diff summaries |
| Flat results | Linked related functions |
| Timestamp only | Semantic change tracking |

### Example Interaction

```
You: "What changed in the auth system recently?"

Engram: "In the last 7 days, 3 commits touched auth:

1. 'Add JWT refresh token' (3 days ago)
   - auth.py: Added refresh_token() function
   - middleware.py: Updated token validation
   - Related: user_session.py (not changed but referenced)

2. 'Fix session timeout bug' (5 days ago)
   - session.py: Changed timeout from 30m to 2h
   - Commit message: 'Users were getting logged out during long tasks'

3. 'Update error messages' (yesterday)
   - login.tsx: Improved validation error copy

Here's the relevant code context..."
```

### MCP Tools

```python
@mcp.tool()
def query_recent(query: str, days: int = 7) -> str:
    """Search with time awareness - finds recent changes related to query."""

@mcp.tool()
def whats_changed(days: int = 7) -> str:
    """Git-aware summary of what changed recently."""

@mcp.tool()
def explain_change(file_path: str) -> str:
    """Why did this file change? Shows commit context."""
```

---

## Killer Feature #2: Architecture Insight (Future)

The screenshot-worthy feature. Build after Temporal Memory ships.

```
You: "Explain the architecture of this repo"

Engram: "This is a Next.js app with 3 main domains:

📁 Authentication (src/auth/)
   - JWT-based with refresh tokens
   - Middleware validates on every request
   - 4 files, 847 lines

📁 API Layer (src/api/)
   - REST endpoints in /api/routes
   - Prisma ORM for database
   - 12 files, 2,340 lines

📁 UI Components (src/components/)
   - React components with Tailwind
   - Shared components in /common
   - 23 files, 4,102 lines

Key dependencies: Next.js 14, Prisma, NextAuth
Entry point: src/app/page.tsx"
```

This makes people screenshot and share.

---

## 2-Week Sprint Plan

### Week 1: Perfect DX (Days 1-7)

**Day 1-2: One-liner install**
```bash
curl -sSL engram.dev/install | bash
```

**Day 3-4: CLI wrapper**
```bash
engram init                    # Index current folder
engram init ~/projects/app     # Index specific folder
engram watch                   # Start Ghost
engram query "auth flow"       # Search from terminal
engram status                  # Show stats
engram setup                   # Auto-configure MCP
```

**Day 5-7: Auto MCP setup**
```bash
engram setup
# Detects Cursor → configures automatically
# Detects Claude Desktop → configures automatically
# Shows "You're ready!" with next steps
```

### Week 2: Smart Temporal Memory (Days 8-14)

**Day 8-9: Git integration**
- Parse git log for recent commits
- Extract commit messages and diffs
- Link files to commits

**Day 10-11: Smart query_recent**
- Combine semantic search with time filtering
- Include commit context in results
- Show related files

**Day 12-13: whats_changed tool**
- Summary of recent activity
- Grouped by feature/area
- Human-readable output

**Day 14: Polish + Demo**
- Record GIF of Temporal Memory
- Update README
- Prep launch posts

---

## Week 3: Soft Launch

### Launch Message

> "I got tired of Claude forgetting my codebase mid-conversation.
>
> Built an open-source memory layer. Local-first, GPU-accelerated, works with any MCP client.
>
> The killer feature: Ask 'what changed in auth this week?' and get actual git-aware context.
>
> Setup takes 60 seconds. Free forever for personal use."

### Where to Post

| Platform | Angle |
|----------|-------|
| r/LocalLLaMA | Privacy + local-first |
| r/cursor | "Cursor never forgets" |
| r/ClaudeAI | MCP integration |
| Twitter/X | Dev workflow improvement |
| Hacker News | Show HN: technical depth |

---

## HN Skeptic Q&A (Prep These)

**Q: Why not just use RAG?**
> Engram IS RAG, but optimized for codebases. Standard RAG doesn't understand git history, code structure, or temporal context. We add time awareness and git integration that generic RAG tools don't have.

**Q: Why not let Claude/Cursor handle this?**
> They lose context after ~70K tokens in practice. They don't persist between sessions. They can't answer "what changed this week?" because they don't have git access. Engram is persistent, local, and git-aware.

**Q: How is this different from project-wide indexing?**
> Three ways: (1) Temporal awareness - we track when things changed, not just what exists. (2) Git integration - we understand commits, not just files. (3) Portable - your memory cartridge is a folder you own, not locked in a cloud service.

**Q: What about embedding drift when models update?**
> Valid concern. We version the embedding model in the cartridge metadata. When you update models, you can re-index incrementally. It's a one-time operation, not continuous drift.

**Q: Why would I pay for this?**
> You probably won't need to. Free tier is generous. Pro is for power users who want the desktop app, quick search, and multi-device sync. Most devs will use free forever, and that's fine.

---

## Pricing

### Free Tier (Very Generous)
- ✅ Unlimited local indexing
- ✅ Full CLI
- ✅ MCP server
- ✅ Temporal Memory
- ✅ GPU acceleration
- ❌ Desktop app
- ❌ Multi-device

### Pro - $12/month or $99/year
- ✅ Everything in Free
- ✅ Desktop app (menu bar)
- ✅ Quick search (Cmd+Shift+E)
- ✅ Unlimited cartridges
- ✅ 3 devices
- ✅ Priority support

### Lifetime - $149 (early bird) → $199
- ✅ Pro forever
- ✅ All future updates
- ✅ 5 devices

### Conversion Reality Check

> "Pro might convert 5-8%, not 15-20%. That's fine for indie SaaS."

| Users | 5% Convert | 8% Convert |
|-------|------------|------------|
| 1,000 | 50 × $12 = $600/mo | 80 × $12 = $960/mo |
| 5,000 | 250 × $12 = $3,000/mo | 400 × $12 = $4,800/mo |
| 10,000 | 500 × $12 = $6,000/mo | 800 × $12 = $9,600/mo |

**Lifetime licenses add burst revenue:**
- 200 × $149 = $29,800 one-time

---

## Revenue Projections (Honest)

From feedback:
> "$5K-15K MRR in 12 months is realistic. $30K MRR requires strong momentum."

| Timeline | Scenario | MRR |
|----------|----------|-----|
| Month 6 | Conservative | $1,500 |
| Month 6 | Moderate | $4,000 |
| Month 12 | Conservative | $5,000 |
| Month 12 | Moderate | $12,000 |
| Month 12 | Strong momentum | $25,000+ |

**This is not a rocket. It's a sustainable indie SaaS.**

---

## Long-Term Moat

To become a company (not just a feature):

| Moat Type | How We Build It |
|-----------|-----------------|
| Plugin ecosystem | Let others build on cartridge format |
| Memory format standard | ".engram" becomes the standard for AI memory |
| Switching cost | Your data, your format, years of indexed knowledge |
| Community | Open source contributors, shared cartridges |
| Trust | Privacy-first reputation |

If our memory format becomes "the standard" for AI agents, that's real power.

---

## What NOT To Build Yet

| Feature | Why Not Now |
|---------|-------------|
| Desktop app | No users to convert yet |
| Team features | Need individual traction first |
| Web UI | Distraction |
| Cloud sync | Conflicts with local-first message |
| Multiple embedding models | Premature optimization |
| Architecture insight | Ship Temporal Memory first |

**Ship ugly. Refine after feedback.**

---

## Strategic Phases

### Phase 1: Now - Month 6
**Goal**: Dominate dev memory use case

- Ship CLI + Temporal Memory
- Launch on Reddit/HN/Twitter
- Get 1,000+ users
- Collect feedback aggressively
- Hit $1-3K MRR

### Phase 2: Month 6-12
**Goal**: Solidify position

- Ship desktop app (Pro differentiator)
- Add Architecture Insight feature
- Product Hunt launch
- Hit $5-10K MRR

### Phase 3: Year 2+
**Goal**: Expand to agent ecosystem

- Plugin system for cartridge format
- Team features
- Integrations beyond IDEs
- Position as "memory infrastructure"

---

## Immediate Action Items

### This Week

1. [ ] Build one-liner installer (`curl | bash`)
2. [ ] Build `engram` CLI wrapper
3. [ ] Build `engram setup` (auto MCP config)
4. [ ] Integrate git log parsing
5. [ ] Build `query_recent` with git context
6. [ ] Build `whats_changed` tool

### Next Week

1. [ ] Record 60-second demo GIF
2. [ ] Update README with GIF
3. [ ] Write HN skeptic answers
4. [ ] Draft launch posts
5. [ ] Post on r/LocalLLaMA

---

## Success Metrics

### Week 2
- [ ] Setup takes < 90 seconds
- [ ] Temporal Memory works with git
- [ ] Demo GIF recorded

### Month 1
- [ ] 500+ GitHub stars
- [ ] 100+ active users
- [ ] 10+ paying customers
- [ ] 1 newsletter feature

### Month 3
- [ ] 2,000+ GitHub stars
- [ ] 500+ active users
- [ ] $2K+ MRR

### Month 6
- [ ] 5,000+ GitHub stars
- [ ] 2,000+ active users
- [ ] $5K+ MRR
- [ ] Desktop app shipped

---

## The Honest Summary

From feedback:

> "This is now focused, technically achievable, market-aligned, indie-scale realistic, and aligned with your strengths."

> "It's not a guaranteed rocket. But it's a very credible indie SaaS bet."

> "If you execute well, this can absolutely become a respected tool in the AI dev ecosystem."

**That's the goal. Ship it.**

---

*"Local, persistent memory for AI development workflows."*

---

Last updated: February 2026
