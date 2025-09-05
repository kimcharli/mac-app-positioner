# Terminology Reference

This document defines the key terms used in Mac App Positioner to avoid confusion.

## Monitor Classification Terms

### Primary Monitor (Config)
- **Definition**: The target monitor where applications will be positioned in quadrants
- **Purpose**: Defines which screen the app layout will be applied to
- **Configuration**: Set via `position: "primary"` in `config.yaml`
- **Example**: Ultra-wide monitor designated as primary for app positioning
- **Independence**: Completely independent from macOS "main" display setting

### Main Display (macOS System)
- **Definition**: The display designated as "main" by macOS Display Settings
- **Characteristics**: 
  - Contains the menubar and dock
  - Has coordinates (0, 0) in macOS coordinate system
  - Apps launch on this display by default
- **Detection**: Identified via `NSScreen.mainScreen()` API
- **Script Impact**: Should NOT affect positioning logic - script works with any main display

### Built-in Display
- **Definition**: The MacBook's internal Retina display
- **Purpose**: Identifier for the laptop's built-in screen
- **Configuration**: Can be referenced as `"macbook"` or specific resolution in config
- **Usage**: Often used for secondary apps or specific workflows

### Secondary Monitor
- **Definition**: Any additional external monitor that is not the primary positioning target
- **Purpose**: May have specific apps assigned but not the main quadrant layout
- **Configuration**: Various position descriptors: `"left"`, `"right"`, `"above"`, etc.

## Positioning Terms

### Arrangement Coordinates
- **Definition**: Monitor positions as reported by macOS `NSScreen`
- **Origin**: Bottom-left of main display (macOS coordinate system)
- **Usage**: Raw coordinates from Display Settings arrangement
- **Example**: `(-764, 1329)` for ultra-wide positioned below main display

### Positioning Coordinates  
- **Definition**: Coordinates used for actual window positioning
- **Origin**: Top-left coordinate system (standard for window management)
- **Usage**: What the script uses to place application windows
- **Conversion**: May differ from arrangement coordinates due to coordinate system differences

### Quadrant Layout
- **Definition**: Division of primary monitor into four equal sections
- **Quadrants**: `top_left`, `top_right`, `bottom_left`, `bottom_right`
- **Purpose**: Systematic organization of applications across the primary monitor
- **Configuration**: Defined in `config.yaml` under `primary`

## Configuration Terms

### Profile
- **Definition**: Complete monitor setup configuration including layout
- **Components**: Monitor definitions + application layout
- **Purpose**: Allows multiple configurations for different physical setups
- **Examples**: `"home"`, `"office"`, `"travel"`

### Resolution
- **Definition**: Monitor pixel dimensions (width x height)
- **Format**: `"3440x1440"`, `"2560x1440"`, `"2056x1329"`
- **Special Cases**: `"macbook"` as shorthand for built-in display
- **Usage**: Used to match detected monitors with configuration

### Layout
- **Definition**: Application-to-position assignments
- **Types**: 
  - `primary`: Apps positioned in quadrants of primary monitor
  - `builtin`: Apps positioned on built-in display
  - Individual monitor assignments

## Dynamic vs Static Concepts

### Dynamic Detection
- **Definition**: Real-time detection of current monitor setup
- **Method**: Reads current Display Settings arrangement via `NSScreen` API
- **Benefit**: Adapts automatically to arrangement changes
- **Independence**: Works regardless of which monitor is macOS "main"

### Static Configuration
- **Definition**: Fixed settings defined in `config.yaml`
- **Purpose**: Defines desired application layout and monitor roles
- **Limitation**: Must match actual detected monitors to function
- **Update**: Requires manual editing when monitor setup changes

## Key Principles

1. **Primary ≠ Main**: The positioning target (primary) is independent from macOS main display
2. **Dynamic Coordinates**: Monitor positions are detected in real-time from Display Settings
3. **Resolution Matching**: Monitors are matched by resolution between config and detected setup
4. **Coordinate System**: Script handles conversion between macOS and window positioning coordinates
5. **Profile Flexibility**: Multiple profiles support different physical arrangements

## Common Confusion Points

### "Primary" vs "Main"
- ❌ Wrong: "Primary monitor must be the macOS main display"  
- ✅ Correct: "Primary monitor is where you want apps positioned, independent of macOS main"

### Coordinate Systems
- ❌ Wrong: "All coordinates use the same system"
- ✅ Correct: "macOS uses bottom-left origin, window positioning uses top-left origin"

### Static vs Dynamic
- ❌ Wrong: "Monitor coordinates are hardcoded in the script"
- ✅ Correct: "Monitor coordinates are detected dynamically from current Display Settings"