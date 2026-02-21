# Engram Landing Page

## Setup Options

Choose your stack:

### Option 1: Next.js (Recommended)
```bash
cd website
npx create-next-app@latest . --typescript --tailwind --app
npm run dev
```

### Option 2: Astro (Faster, simpler)
```bash
cd website
npm create astro@latest .
npm run dev
```

### Option 3: Plain HTML + Tailwind
```bash
cd website
npm init -y
npm install -D tailwindcss
npx tailwindcss init
```

---

## Deployment

- **Vercel**: Connect GitHub repo, set root to `website/`
- **Netlify**: Same approach
- **GitHub Pages**: Use `gh-pages` branch

---

## Domain

Suggested: `engram.dev` or `getengram.dev`

---

## Page Sections

1. **Hero**
   - Headline: "Your AI finally remembers your codebase"
   - Subhead: "Local, persistent memory for AI development workflows"
   - CTA: "Get Started" → GitHub

2. **Problem**
   - "Cursor forgets after 5 minutes"
   - "Claude loses context mid-conversation"
   - "You keep re-explaining the same things"

3. **Solution**
   - 3-step setup (init, setup, done)
   - Demo GIF here

4. **Features**
   - Semantic search
   - Temporal Memory (killer feature)
   - GPU accelerated
   - Local-first / private

5. **How It Works**
   - Architecture diagram
   - "Files → Chunks → Vectors → FAISS → MCP → AI"

6. **Pricing** (optional for launch)
   - Free: Full CLI, unlimited indexing
   - Pro: Desktop app, multi-device ($12/mo)
   - Lifetime: $149

7. **FAQ**
   - HN skeptic answers

8. **Footer**
   - GitHub link
   - Twitter
   - MIT License

---

## Assets Needed

- [ ] Logo
- [ ] Demo GIF (60 seconds)
- [ ] Architecture diagram
- [ ] Social preview image (1200x630)
