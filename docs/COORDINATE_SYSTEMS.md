# macOS Coordinate Systems - Complete Guide

This document explains the critical coordinate system differences in macOS and how Mac App Positioner handles them correctly.

## The Core Problem

macOS uses **two different coordinate systems** depending on which API you use:

1. **Cocoa/NSScreen**: Bottom-left origin (Y increases upward)
2. **Quartz/CoreGraphics**: Top-left origin (Y increases downward)

This creates a **fundamental mismatch** between monitor detection and window positioning.

## Coordinate System Details

### Cocoa/NSScreen (Monitor Detection)
- **Origin**: Bottom-left of main display (0, 0)
- **Y Direction**: Increases **upward**
- **Used by**: `NSScreen.screens()` for monitor detection
- **Purpose**: Display arrangement as configured in System Settings

```python
# NSScreen reports monitors with bottom-left origin
frame = screen.frame()
x, y = frame.origin.x, frame.origin.y  # Bottom-left coordinates
```

### Quartz/CoreGraphics (Window Positioning)
- **Origin**: Top-left of main display (0, 0)  
- **Y Direction**: Increases **downward**
- **Used by**: Accessibility APIs for window positioning
- **Purpose**: Actual window placement coordinates

```python
# Window positioning uses top-left origin
AXUIElementSetAttributeValue(window, kAXPositionAttribute, position_value)
```

## Real Example from Your Setup

Your physical setup:
```
    [Ultra-wide 3440x1440] ← Physically above MacBook
[Lenovo 2560x1440] [MacBook 2056x1329 MAIN]
```

### NSScreen Reports (Cocoa - Bottom-left origin):
```
MacBook:    2056x1329 at (0, 0)        ← Main display
Lenovo:     2560x1440 at (-3324, 1329) ← Left and "below" main  
Ultra-wide: 3440x1440 at (-764, 1329)  ← Right and "below" main
```

### Actual Window Coordinates (Quartz - Top-left origin):
```
MacBook:    2056x1329 at (0, 0)        ← Main display
Lenovo:     2560x1440 at (-3324, -1440) ← Left and ABOVE main
Ultra-wide: 3440x1440 at (-764, -1440)  ← Right and ABOVE main
```

## The Conversion Formula

For monitors that appear "below" main display in NSScreen (positive Y):

```python
# Convert Cocoa coordinates to Quartz coordinates
if is_main_display:
    quartz_x, quartz_y = 0, 0  # Origin in both systems
else:
    quartz_x = cocoa_x  # X coordinate stays the same
    
    if cocoa_y > 0:
        # Monitor is "below" main in Cocoa = "above" main in Quartz
        quartz_y = -monitor_height  # Negative Y = above main
    elif cocoa_y < 0:  
        # Monitor is "above" main in Cocoa = "below" main in Quartz
        quartz_y = main_display_height  # Positive Y = below main
    else:
        # Same level as main display
        quartz_y = 0
```

## Why This Matters

### Before Conversion (BROKEN):
```python
# Using NSScreen coordinates directly for window positioning
ultra_wide_y = 1329  # From NSScreen - "below" MacBook

# Window positioning targets:
top_left = (-764, 1329)     # Way below MacBook screen
bottom_right = (2676, 2769) # Far off-screen

# Result: Windows constrained to MacBook or positioned incorrectly
```

### After Conversion (WORKING):
```python
# Convert NSScreen to Quartz coordinates  
ultra_wide_y = -1440  # Converted - "above" MacBook

# Window positioning targets:
top_left = (-764, -1440)    # Top of ultra-wide monitor
bottom_right = (2676, -720) # Bottom-right of ultra-wide

# Result: Windows positioned correctly on ultra-wide monitor ✅
```

## Implementation in Mac App Positioner

### Dynamic Coordinate Mapping Generation
```python
def generate_dynamic_coordinate_mappings(self):
    screens = NSScreen.screens()
    main_screen = NSScreen.mainScreen()
    main_height = int(main_screen.frame().size.height)
    
    for screen in screens:
        frame = screen.frame()
        # Get NSScreen coordinates (Cocoa - bottom-left)
        cocoa_x, cocoa_y = int(frame.origin.x), int(frame.origin.y)
        
        if screen == main_screen:
            quartz_x, quartz_y = 0, 0  # Origin for main display
        else:
            quartz_x = cocoa_x  # X stays the same
            
            # Convert Y coordinate
            if cocoa_y > 0:
                # "Below" in Cocoa = "Above" in Quartz
                quartz_y = -height
            elif cocoa_y < 0:
                # "Above" in Cocoa = "Below" in Quartz  
                quartz_y = main_height
            else:
                quartz_y = 0
        
        # Store both coordinate systems for reference
        mappings[monitor_name] = {
            'arrangement': (cocoa_x, cocoa_y),    # NSScreen reference
            'positioning': (quartz_x, quartz_y),  # Window positioning
            'translation_rule': determine_rule(quartz_x, quartz_y)
        }
```

### Position Calculation
```python
def calculate_quadrant_positions(self, screen):
    # Use Quartz coordinates for window positioning
    if 'positioning_coords' in screen:
        x_offset, y_offset = screen['positioning_coords']  # Quartz coordinates
    else:
        x_offset, y_offset = screen['x'], screen['y']      # Fallback
    
    # Calculate quadrants using correct coordinate system
    positions = {
        'top_left': {
            'x': x_offset,
            'y': y_offset,  # Top of monitor (negative for monitors above main)
        },
        'bottom_right': {
            'x': x_offset + width // 2,
            'y': y_offset + height // 2,  # Bottom of top-half
        }
    }
```

## Verification Methods

### Check Window Positions
```python
# Get actual window positions to verify coordinate system
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly

windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
for window in windows:
    bounds = window.get('kCGWindowBounds', {})
    x, y = bounds.get('X', 0), bounds.get('Y', 0)
    print(f"Window at ({x}, {y})")  # These are Quartz coordinates
```

### Expected Results
For ultra-wide monitor above MacBook:
- **NSScreen Y**: +1329 (positive = "below" main)
- **Window Y**: -1440 (negative = above main)
- **Window positioning**: Y between -1440 and 0

## Common Issues and Solutions

### Issue 1: Windows Appear on Wrong Monitor
**Symptom**: Apps positioned on MacBook instead of target monitor
**Cause**: Using NSScreen coordinates directly for positioning
**Solution**: Convert NSScreen to Quartz coordinates

### Issue 2: Windows Positioned Off-Screen  
**Symptom**: Apps disappear or appear in unexpected locations
**Cause**: Coordinate system mismatch causes incorrect Y calculations
**Solution**: Proper Cocoa-to-Quartz Y coordinate conversion

### Issue 3: Monitor Above Main Display Not Detected
**Symptom**: Monitors physically above main display not recognized correctly
**Cause**: NSScreen reports positive Y for monitors that are physically above
**Solution**: Convert positive NSScreen Y to negative Quartz Y

## Best Practices

### 1. Always Convert Coordinates
```python
# ❌ WRONG - Direct use of NSScreen coordinates
window_position = (nsscreen_x, nsscreen_y)

# ✅ CORRECT - Convert to Quartz coordinates
quartz_coords = convert_cocoa_to_quartz(nsscreen_x, nsscreen_y)
window_position = quartz_coords
```

### 2. Store Both Coordinate Systems
```python
monitor_info = {
    'arrangement': (cocoa_x, cocoa_y),    # For Display Settings reference
    'positioning': (quartz_x, quartz_y),  # For window positioning
    'coordinate_source': 'cocoa_to_quartz_conversion'
}
```

### 3. Validate Positioning Results
```python
# Verify windows end up on intended monitor
final_position = get_window_position(app_pid)
target_monitor = identify_monitor(final_position['x'], final_position['y'])
print(f"Window positioned on: {target_monitor}")
```

## Testing Your Setup

### 1. Check Coordinate Systems
```bash
# See both coordinate systems
uv run python main.py list-screens-enhanced --verbose
```

### 2. Verify Conversion
Look for output like:
```
Monitor 2 (UltraWide_Display_2):
  Arrangement coords: (-764, 1329)     ← NSScreen (Cocoa)
  Positioning coords: (-764, -1440)    ← Window positioning (Quartz)
```

### 3. Test Positioning
```bash
# Verify windows appear on correct monitor
uv run python main.py position --verbose
```

Successful output shows:
```
Window is on: Monitor 2 (UltraWide_Display_2) [pymonctl]: 3440x1440 at (-764, -1440)
```

## Summary

The **coordinate system conversion** is the critical piece that makes Mac App Positioner work correctly:

1. **NSScreen provides monitor detection** but uses bottom-left origin
2. **Window positioning requires top-left origin** (Quartz coordinates)  
3. **Conversion formula handles the Y-axis flip** and position relationships
4. **Dynamic detection** adapts to any Display Settings arrangement
5. **Proper conversion ensures windows appear on intended monitors**

Without this conversion, monitors physically above the main display appear to be below it, causing windows to be positioned incorrectly or constrained to the main display.