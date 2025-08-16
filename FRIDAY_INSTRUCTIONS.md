# Friday Instructions

This repo is managed by **Friday** — an autonomous AI agent that edits, commits, and deploys code.

---

## Workflow

1. **Add tasks**
   - Put tasks in `TASKS.md` as bullet points.
   - Example:
     ```
     - Add an About page with description
     - Fix app.py to read PORT from os.environ
     ```

2. **Friday Runner**
   - In Codespaces terminal, Friday is started automatically (see below).
   - It will:
     - Read `TASKS.md`
     - Apply code changes
     - Commit & push with message `AUTO: ...`
     - Trigger GitHub Actions
     - Render redeploys automatically to:
       https://friday-starter.onrender.com

3. **Deployment**
   - GitHub Actions workflow `.github/workflows/deploy.yml` runs on every push.
   - Render is connected to repo → auto-deploys each commit.

---

## Collaboration

- Anyone can add tasks to `TASKS.md` and open the Codespace.
- Friday Runner launches automatically and handles everything.
- No manual copy/paste or deployment needed.

---

## Safety

- Friday pushes directly to `main`.  
- If stability is critical, create a `dev` branch and adjust workflows.  
- Logs are stored in `state/log.txt`.

---
