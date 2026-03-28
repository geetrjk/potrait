---
description: Standard Git branching and merging workflow for the project
---

# Project Git Workflow

This workflow ensures all research, architecture blueprints, and production ComfyUI workflows are properly version-controlled and reviewed.

1. **Update local repository:**
// turbo
```bash
git checkout main
git pull origin main
```

2. **Create a new branch for the task:**
```bash
git checkout -b <type>/<task-description>
# Types: feature, research, bugfix, or architect
```

3. **Make your changes:**
- Research Lead saves findings in `research/references/`
- Architect saves blueprints in the designated directories
- Production Engineer saves ComfyUI JSONs in `production/workflows/`

4. **Commit the changes:**
```bash
git add .
git commit -m "<type>: concise description of changes"
```

5. **Push the branch to GitHub:**
```bash
git push -u origin <branch-name>
```

6. **Create a Pull Request (PR):**
- Propose the changes on GitHub for the team to review.
- Once reviewed, merge the PR into `main`.
