# UV Setup Guide for Python Script Projects

A comprehensive guide to set up Python projects with `uv` for script-based applications (not packages for distribution).

## When to Use This Guide

Use this approach when you have:
- Standalone Python scripts (like `main.py`)
- Dependencies you want to manage cleanly
- Want to avoid manual virtual environment activation
- **Not** building a package for PyPI distribution

## Quick Setup (TL;DR)

```bash
# Create pyproject.toml (see template below)
uv sync
uv run main.py <your-commands>
```

## Step-by-Step Setup

### 1. Create `pyproject.toml`

For script-based projects, use this minimal template:

```toml
[project]
name = "your-project-name"
version = "0.1.0"
description = "Your project description"
requires-python = ">=3.11"
dependencies = [
    "dependency-1>=1.0",
    "dependency-2>=2.0"
]

[tool.uv]
dev-dependencies = []
```

### 2. Key Points for Script Projects

**✅ DO include:**
- `[project]` section with name, version, description
- `dependencies` array with your requirements
- `requires-python` for Python version constraint
- `[tool.uv]` section (can be empty)

**❌ DON'T include for script projects:**
- `[build-system]` - Only needed for packages
- `[tool.hatch.build.targets.wheel]` - Causes build errors
- Complex packaging configuration

### 3. Install Dependencies

```bash
# Install all dependencies (like pip install -r requirements.txt)
uv sync
```

### 4. Run Your Scripts

```bash
# Run scripts without activating virtual environment
uv run main.py
uv run main.py --help
uv run main.py command arg1 arg2
```

## Common Issues & Solutions

### Issue 1: "Unable to determine which files to ship"

**Error message:**
```
ValueError: Unable to determine which files to ship inside the wheel
```

**Solution:**
Remove these sections from `pyproject.toml`:
```toml
# DELETE THESE for script projects
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/foo"]
```

**Explanation:** Script projects don't need build configuration.

### Issue 2: Dependencies Not Found

**Error:** Import errors when running `uv run`

**Solution:**
1. Check your `dependencies` array in `pyproject.toml`
2. Run `uv sync` after adding new dependencies
3. Verify dependency names on PyPI

### Issue 3: Python Version Mismatch

**Error:** Python version compatibility issues

**Solution:**
```toml
[project]
requires-python = ">=3.11"  # Adjust as needed
```

## Migration from requirements.txt

### Old setup:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### New setup:
```bash
# Convert requirements.txt to pyproject.toml dependencies
uv sync
uv run main.py
```

### Conversion Example:
```txt
# requirements.txt
PyObjC>=9.0
PyYAML>=6.0
```

Becomes:
```toml
# pyproject.toml
dependencies = [
    "PyObjC>=9.0",
    "PyYAML>=6.0"
]
```

## Complete Example

Here's the exact `pyproject.toml` that worked for our Mac App Positioner:

```toml
[project]
name = "mac-app-positioner"
version = "0.1.0"
description = "A utility for positioning macOS applications across monitors"
requires-python = ">=3.11"
dependencies = [
    "PyObjC>=9.0",
    "PyYAML>=6.0"
]

[tool.uv]
dev-dependencies = []
```

## Project Structure

```
your-project/
├── .venv/              # Created by uv (don't commit)
├── main.py             # Your script
├── config.yaml         # Config files
├── pyproject.toml      # Dependencies & metadata
└── README.md           # Documentation
```

## Cleanup from Old Setup

When migrating from pip/venv:
```bash
# Remove old files
rm -rf venv/
rm requirements.txt

# Keep using uv
uv sync
uv run main.py
```

## Why This Works

1. **PEP 621 Compliance:** Uses standard `[project]` metadata
2. **No Build System:** Scripts don't need wheel packaging
3. **Clean Dependencies:** All deps in one place (`pyproject.toml`)
4. **Automatic venv:** uv handles virtual environment transparently
5. **Cross-platform:** Works on macOS, Linux, Windows

## Benefits Over Traditional Setup

| Traditional | With uv |
|-------------|---------|
| `source venv/bin/activate && python main.py` | `uv run main.py` |
| `pip install -r requirements.txt` | `uv sync` |
| Manual venv management | Automatic |
| Multiple files (requirements.txt, setup.py) | Single pyproject.toml |

## Pro Tips

1. **Add to .gitignore:**
   ```
   .venv/
   __pycache__/
   *.pyc
   ```

2. **Development dependencies:**
   ```toml
   [tool.uv]
   dev-dependencies = [
       "pytest>=7.0",
       "black>=23.0"
   ]
   ```

3. **Lock file:** uv automatically creates `uv.lock` - commit this for reproducible builds

4. **Update dependencies:**
   ```bash
   uv sync --upgrade
   ```