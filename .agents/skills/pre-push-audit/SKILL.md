---
name: pre-push-audit
description: >-
  Audits the project directory before a git push to prevent sensitive files
  (API keys, databases, credentials, virtual environments) from being
  accidentally committed. Automatically secures them in .gitignore.
---

# Pre-Push Security Audit

## Overview
This skill audits the current project directory before a git push to prevent sensitive files (API keys, databases, credentials, virtual environments, private media) from being accidentally committed. It aggressively and automatically updates `.gitignore` to secure these files.

## Dependencies
None.

## Quick Start
Trigger this skill when the user says: "Run a pre-push audit", "Audit my code before I push", or "Check for security risks".

## Workflow

### 1. Verify Git Repository
- Run `git status` using `run_command`.
- If the directory is not a git repository, inform the user and halt the workflow.

### 2. Scan for Sensitive Files
- Use `find` via terminal or `find_by_name` to scan the project directory for sensitive patterns. Look for:
  - Environment files: `.env`, `.env.*`
  - Database files: `*.db`, `*.sqlite`, `*.sqlite3`
  - Keys and certificates: `*.pem`, `*.key`, `id_rsa`
  - Virtual environments: `.venv*`, `venv*`, `env/`
  - Suspicious config/token files: e.g., `*credentials*.json`, `*secret*`
  - Data volumes or media directories (e.g., `abs-config`, `abs-audiobooks`).

### 3. Aggressive Ignore Rule (Handle Ambiguity)
- If you find any file that you *suspect* contains secrets (e.g., an un-ignored JSON file that looks like a GCP service account key, or an unrecognized sqlite database), automatically assume it is sensitive. Do not ask for the user's permission to secure it.

### 4. Update .gitignore
- Check if `.gitignore` exists in the project root. If it does not exist, create it.
- Append the paths, extensions, or directory patterns of all sensitive files found in Steps 2 and 3 into `.gitignore`.
- Ensure you do not duplicate entries that already exist in the file.

### 5. Final Report
- Output a concise summary to the user detailing exactly which files/patterns were automatically added to `.gitignore`.
- Give the user the green light that the repository is secure and ready to be pushed.

## Common Mistakes
- **Asking for permission:** This workflow is designed to be aggressive. Do not ask the user if they want to ignore a suspicious file — just add it to `.gitignore` and tell them you did it.
- **Overlooking missing .gitignore:** Always check if `.gitignore` exists before trying to modify it. If it's missing, create it.
- **Ignoring existing rules:** Make sure to read the current `.gitignore` first so you don't add duplicate lines.
