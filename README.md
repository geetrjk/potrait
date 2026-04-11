# Identity-Consistent Artistic Generation

A professional ComfyUI project to integrate personal identities into diverse artistic styles and themed templates.

## GitHub Repository & Agent Alignment
This project is centered around the GitHub repository. All research, design, and production artifacts are version-controlled here, with normal Git-based practices managing branch changes, PR reviews, and deployments.

The project structure is purposefully aligned for both Codex and Google Antigravity:
- **Codex Entry Point**: `AGENTS.md` contains Codex-facing project instructions.
- **Gemini / Antigravity Entry Point**: `GEMINI.md` contains Gemini / Antigravity-facing project instructions.
- **Shared Contract**: `docs/agent_contract.md` contains the tool-neutral operating model shared by both agents.
- **Skills**: Focused capabilities like the Research Analyzer are kept as specialized markdown instructions with frontmatter in `.agents/skills/`.
- **Workflows**: Standard operating procedures, such as version control protocols, are recorded using the specialized format in `.agents/workflows/`.
- **Modularity**: Code artifacts, documents, and workflow `.json` files are neatly separated by phase into folders like `research/references/` and `production/workflows/`, and synced iteratively via a Git-centric life cycle.

## Project Phases

### Phase 1: Research
The Research Lead gathers, analyzes, and summarizes methodologies, node settings, and techniques from provided reference materials (e.g., YouTube transcripts, papers, articles).

### Phase 2: Architecture Design
The Senior ComfyUI Architect translates the research findings into structured blueprints and node pipelines.

### Phase 3: Implementation
The Production Engineer constructs modular and functional ComfyUI workflows based on the architectural blueprints.

### Phase 4: Production Scaling
Refining, standardizing, and scaling the workflows for robust identity-consistent generation.
