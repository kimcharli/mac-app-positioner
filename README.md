# Mac App Positioner

A Python utility to automatically position macOS applications across multiple monitors based on predefined configurations.

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Commands

**List connected screens:**
```bash
python main.py list-screens
```

**List running applications:**
```bash
python main.py list-apps
```

**Detect current monitor profile:**
```bash
python main.py detect
```

**Position applications automatically:**
```bash
python main.py position
```

**Position using specific profile:**
```bash
python main.py position home
python main.py position office
```

## Configuration

Edit `config.yaml` to customize:
- Monitor configurations for home/office setups
- Application positioning (quadrants on main screen)
- Bundle identifiers for target applications

## Current Status

✅ Basic framework implemented  
✅ Screen detection working  
✅ Application enumeration working  
✅ Profile detection working  
✅ Position calculation working  
🚧 **Window positioning (placeholder only - requires implementation)**  

### What Works Now
- Detects your monitor configuration automatically
- Finds running applications (Chrome, Outlook, Teams, etc.)
- Calculates perfect quadrant positions for your main screen
- Shows exactly where each app would be positioned

### What's Missing
The `move_application_window()` function in main.py currently only prints position information as placeholders. **Actual window positioning is not implemented yet.**

## Next Steps

1. **Implement actual window positioning using accessibility APIs** (main missing piece)
2. Add error handling for missing applications
3. Test with actual multi-monitor setups
4. Add automatic trigger on monitor changes

## Permissions Required

**For full functionality, you'll need to grant:**
- **Accessibility** permissions for window control
- **Screen Recording** permissions (if needed for certain window operations)

**How to grant permissions:**
System Preferences > Privacy & Security > Accessibility > Add your terminal app or Python

**Current Limitation:** Even with permissions granted, the window positioning code needs to be implemented using macOS accessibility APIs (PyObjC AX framework or AppleScript integration).