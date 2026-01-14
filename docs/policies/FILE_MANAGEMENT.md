# File Management Policy

This document outlines the directory structure and file management rules for the **Echoes of Error** project.

## Directory Structure

- `/src`: Core source code (Agent logic, Experiment engine, Utilities).
- `/logs`: Raw experiment logs (`.jsonl`) and summary files (`.json`), organized by batch ID.
- `/plots`: Generated visualizations and charts.
- `/docs`: Project documentation, organized as follows:
  - `/docs/specs`: Experiment specifications and requirements.
  - `/docs/roadmaps`: Project timelines and roadmaps.
  - `/docs/policies`: Guidelines and management rules.
  - `/docs/thesis`: Thesis blueprint and implementation plans.
  - `/docs/reports`: Analysis reports from experiment batches.
  - `/docs/notes`: Research notes, drafts, and miscellaneous files.
- `/data`: Static data files (Scenarios, etc.).
- `/tmp`: **Temporary scripts, analysis snippets, and intermediate files.**

## Guidelines for Developers (and AI)

1. **Core Code**: All production-ready logic must reside in `/src` or the project root (e.g., `run_batch.py`, `analyze.py`).
2. **Temporary Files**: Any script created for quick data verification, one-off analysis, or debugging must be placed in the `/tmp` directory.
    - Example: `tmp/quick_check.py`
3. **Logs**: Never manually modify files in `/logs` unless using the official resume/cleanup utilities.
4. **Cleanup**: Periodically review the `/tmp` directory and remove obsolete scripts.

---
*Last Updated: 2026-01-15*
