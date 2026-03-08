# Debug Skill

This skill provides tools and procedures to diagnose and troubleshoot the File Commander system.

## Components

### 1. Diagnostics Script
Run this script to verify environment variables, database connectivity, and required paths.

```bash
python3 skills/debug_skill/diagnostics.py
```

## Troubleshooting Steps

1. **Database Issues**:
   - Ensure the database server is running.
   - Check the `DATABASE_URL` in `.env`.
2. **Missing Dependencies**:
   - Run `pip install -r requirements.txt` or (recommended for speed) `uv pip install -r requirements.txt` (ensure `.venv` is active).
3. **Path Errors**:
   - Verify that external volumes are mounted (e.g., `/Volumes/Workspace`).
