# AI Agents Guide for Mac App Positioner

This document provides guidelines for AI agents working with the Mac App Positioner codebase.

## Core Principles

### 1. Dynamic Over Static
- **Always favor dynamic detection** over hardcoded values
- **Use `NSScreen` API** to get real-time monitor coordinates
- **Never hardcode monitor positions** - they change when users rearrange displays
- **Generate coordinate mappings dynamically** based on current system state

### 2. Terminology Consistency
Refer to [TERMINOLOGY.md](./TERMINOLOGY.md) for precise definitions. Key distinctions:

- **Primary Monitor**: Positioning target (config) ≠ **Main Display** (macOS system)
- **Arrangement Coordinates**: macOS NSScreen ≠ **Positioning Coordinates**: Window management
- **Resolution Matching**: Connect detected monitors to config profiles

### 3. Coordinate System Awareness
```python
# macOS NSScreen (bottom-left origin)
frame = screen.frame()
macos_x, macos_y = frame.origin.x, frame.origin.y

# Window positioning (top-left origin) - may need conversion
positioning_x = macos_x  # X usually same
positioning_y = macos_y  # Y may need adjustment for monitors above main
```

## Code Architecture Guidelines

### Monitor Detection Pattern
```python
def detect_monitors_dynamically():
    """Always use this pattern for monitor detection"""
    from Cocoa import NSScreen
    screens = NSScreen.screens()
    
    for screen in screens:
        frame = screen.frame()
        # Extract current coordinates - never use hardcoded values
        x, y = int(frame.origin.x), int(frame.origin.y)
        width, height = int(frame.size.width), int(frame.size.height)
        is_main = screen == NSScreen.mainScreen()
        
        # Generate dynamic mappings
        monitor_info = {
            'arrangement': (x, y),      # Current Display Settings
            'positioning': (x, y),      # For window placement
            'resolution': f'{width}x{height}',
            'is_main': is_main
        }
```

### Configuration Matching Pattern
```python
def match_config_to_detected():
    """Match config profiles to actual detected monitors"""
    detected_resolutions = {f"{s['width']}x{s['height']}" for s in screens}
    
    for profile_name, profile in config['profiles'].items():
        profile_resolutions = {m['resolution'] for m in profile['monitors'] 
                             if m['resolution'] != 'macbook'}
        
        # Profile matches if its resolutions are subset of detected
        if profile_resolutions.issubset(detected_resolutions):
            return profile_name
```

### Positioning Logic Pattern
```python
def position_applications():
    """Always use primary monitor from config as positioning target"""
    # 1. Find primary monitor definition in config
    primary_config = next(m for m in profile['monitors'] if m['position'] == 'primary')
    
    # 2. Find matching detected monitor by resolution
    target_screen = next(s for s in screens 
                        if f"{s['width']}x{s['height']}" == primary_config['resolution'])
    
    # 3. Use target screen coordinates (not macOS main display)
    calculate_quadrants(target_screen)
```

## Problem-Solving Guidelines

### Monitor Arrangement Issues
When positioning fails or coordinates seem wrong:

1. **Check Display Settings arrangement** - coordinates reflect current arrangement
2. **Verify primary monitor in config** - must match intended positioning target  
3. **Test coordinate reachability** - ensure coordinates are within valid screen bounds
4. **Consider coordinate system conversion** - especially for monitors above main display

### Configuration Debugging
```python
# Always provide this debugging info
def debug_monitor_setup():
    print("Detected monitors:")
    for screen in detected_screens:
        print(f"  {screen['width']}x{screen['height']} at ({screen['x']}, {screen['y']})")
    
    print("Config expects:")
    for monitor in profile['monitors']:
        print(f"  {monitor['resolution']} as {monitor['position']}")
```

### Dynamic Updates
When monitors are rearranged:
- **No code changes needed** - detection is automatic
- **Config may need updates** - if new monitors added or roles changed
- **Test after arrangement changes** - verify coordinates update correctly

## Anti-Patterns to Avoid

### ❌ Don't Hardcode Coordinates
```python
# WRONG - Static coordinates break when arrangement changes
mappings = {
    'LEN P24h-20': {'x': -3324, 'y': 1329},  # Breaks on rearrangement
}
```

### ❌ Don't Assume Main Display Role
```python
# WRONG - Assumes main display is positioning target
if screen.is_main:
    position_apps_here(screen)  # May not be intended target
```

### ❌ Don't Mix Coordinate Systems
```python
# WRONG - Mixing macOS and window positioning coordinates
window_x = nsscreen_frame.origin.x  # May need conversion
```

## Best Practices

### ✅ Dynamic Detection
```python
# CORRECT - Always detect current state
coordinate_mappings = generate_dynamic_mappings()
```

### ✅ Clear Role Separation  
```python
# CORRECT - Separate detection from configuration
detected_monitors = detect_current_setup()
target_monitor = find_primary_from_config(detected_monitors, config)
```

### ✅ Coordinate Validation
```python
# CORRECT - Validate coordinates are reachable
if validate_coordinates(target_x, target_y):
    position_window(target_x, target_y)
```

## Testing Guidelines

### Monitor Configuration Tests
- Test with different Display Settings arrangements
- Verify profile detection with various monitor combinations
- Test coordinate updates when arrangement changes

### Positioning Accuracy Tests  
- Verify windows appear on intended monitor
- Check quadrant positioning accuracy
- Test edge cases (monitors above/below main)

### Error Handling Tests
- Handle missing monitors gracefully
- Provide clear error messages for configuration mismatches
- Fallback to safe defaults when positioning fails

## Key Files and Functions

### Core Detection
- `generate_dynamic_coordinate_mappings()`: Creates mappings from current system state
- `get_screens_enhanced()`: Primary monitor detection method
- `detect_profile()`: Matches current setup to config profiles

### Positioning Logic
- `position_applications()`: Main positioning orchestrator  
- `calculate_quadrant_positions()`: Divides primary monitor into quadrants
- `move_application_window()`: Handles actual window movement

### Configuration
- `config.yaml`: Static layout definitions and monitor roles
- Profile matching: Resolution-based monitor identification

Remember: The system should adapt to the user's Display Settings, not the other way around.