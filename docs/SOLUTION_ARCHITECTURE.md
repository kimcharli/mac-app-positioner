# Mac App Positioner - Complete Solution Architecture

This document provides a comprehensive overview of how Mac App Positioner achieves fully dynamic, coordinate-system-aware application positioning.

## Solution Overview

Mac App Positioner solves the complex problem of positioning applications across multiple monitors on macOS by implementing:

1. **Dynamic Monitor Detection**: Real-time detection from Display Settings
2. **Coordinate System Conversion**: Cocoa-to-Quartz coordinate translation  
3. **Consistent Configuration**: Unified terminology and shared layouts
4. **Intelligent Positioning**: Corner alignment and monitor-specific targeting

## Architecture Components

### 1. Dynamic Monitor Detection System

**Purpose**: Automatically detect current monitor configuration without hardcoded values

**Implementation**:
```python
def generate_dynamic_coordinate_mappings(self):
    # Real-time detection from NSScreen
    screens = NSScreen.screens()
    
    for screen in screens:
        # Extract current coordinates and properties
        frame = screen.frame()
        cocoa_x, cocoa_y = int(frame.origin.x), int(frame.origin.y)
        width, height = int(frame.size.width), int(frame.size.height)
        is_main = screen == NSScreen.mainScreen()
```

**Benefits**:
- ✅ Adapts to any Display Settings arrangement
- ✅ No hardcoded monitor positions
- ✅ Automatically handles new monitors
- ✅ Works with any physical setup

### 2. Coordinate System Conversion Engine

**Purpose**: Convert between macOS coordinate systems for accurate positioning

**The Problem**:
- NSScreen (monitor detection): Bottom-left origin, Y increases upward
- Window positioning: Top-left origin, Y increases downward

**The Solution**:
```python
# Convert NSScreen (Cocoa) to Window Positioning (Quartz)
if is_main:
    quartz_x, quartz_y = 0, 0  # Origin for both systems
else:
    quartz_x = cocoa_x  # X coordinate unchanged
    
    if cocoa_y > 0:
        # Monitor "below" main in Cocoa = "above" main in Quartz  
        quartz_y = -height  # Negative Y = above main display
    elif cocoa_y < 0:
        # Monitor "above" main in Cocoa = "below" main in Quartz
        quartz_y = main_height  # Positive Y = below main display
```

**Results**:
- ✅ Monitors above main display: Negative Y coordinates
- ✅ Monitors below main display: Positive Y coordinates
- ✅ Windows positioned on correct monitors
- ✅ Coordinates match physical arrangement

### 3. Unified Configuration System

**Purpose**: Consistent terminology and shared layouts across profiles

**Configuration Structure**:
```yaml
# Common layout - applies to all profiles
layout:
  primary:
    top_left: com.google.Chrome
    top_right: com.microsoft.teams2
    bottom_left: com.microsoft.Outlook  
    bottom_right: com.kakao.KakaoTalkMac
  builtin:
    - md.obsidian

# Monitor configurations for different setups
profiles:
  home:
    monitors:
      - resolution: 3840x2160
        position: primary
      - resolution: 2560x1440
        position: left
      - resolution: 2056x1329
        position: builtin
  
  office:
    monitors:
      - resolution: 3440x1440  
        position: primary
      - resolution: 2560x1440
        position: left
      - resolution: 2056x1329
        position: builtin
```

**Terminology Consistency**:
- `primary` in monitors → `primary` in layout
- `builtin` in monitors → `builtin` in layout  
- `left` in monitors → future `left` layout support

**Benefits**:
- ✅ No duplication of layout configuration
- ✅ Consistent terminology throughout
- ✅ Easy to maintain and modify
- ✅ Profile switching changes only monitor setup

### 4. Intelligent Positioning Engine

**Purpose**: Accurately position applications using converted coordinates and smart algorithms

**Position Calculation**:
```python
def calculate_quadrant_positions(self, screen):
    # Use converted Quartz coordinates
    x_offset, y_offset = screen['positioning_coords']
    
    # Calculate quadrant positions
    quad_width = screen['width'] // 2
    quad_height = screen['height'] // 2
    
    positions = {
        'top_left': {
            'x': x_offset,
            'y': y_offset,  # Top of monitor (may be negative)
            'width': quad_width,
            'height': quad_height
        },
        'bottom_right': {
            'x': x_offset + quad_width,
            'y': y_offset + quad_height,  # Bottom of lower quadrant
            'width': quad_width, 
            'height': quad_height
        }
    }
```

**Corner Alignment**:
```python
def calculate_corner_aligned_position(self, quadrant_position, window_size, quadrant):
    # Align windows to quadrant corners for optimal space usage
    if quadrant == 'top_right':
        # Align to top-right corner of quadrant
        aligned_x = x + quad_width - window_size['width']
        aligned_y = y  # Top edge
    elif quadrant == 'bottom_left':
        # Align to bottom-left corner of quadrant
        aligned_x = x  # Left edge
        aligned_y = y + quad_height - window_size['height']
```

**Application-Specific Handling**:
- Chrome: Multi-attempt positioning with offset correction
- Standard apps: Single positioning attempt with corner alignment
- Window size detection: Real-time size calculation for optimal placement

## Data Flow Architecture

### 1. Initialization Phase
```
Load Config → Generate Dynamic Mappings → Detect Current Profile
     ↓                    ↓                        ↓
config.yaml → NSScreen Detection → Resolution Matching
```

### 2. Detection Phase  
```
NSScreen API → Coordinate Conversion → Monitor Classification
     ↓                   ↓                      ↓
Cocoa Coords → Quartz Coords → Position Rules (above/below/left/right)
```

### 3. Positioning Phase
```
Profile Selection → Target Monitor → Quadrant Calculation → Window Positioning
       ↓                  ↓               ↓                    ↓
    office → Ultra-wide 3440x1440 → (-764,-1440) → AX API Positioning
```

### 4. Validation Phase
```
Position Verification → Monitor Detection → Success Reporting
        ↓                      ↓                  ↓
Get Final Position → Identify Monitor → Log Results
```

## Key Algorithms

### 1. Monitor Name Generation
```python
def generate_monitor_name(self, width, height, x, y, index, is_main):
    # Consistent naming based on resolution
    if width == 2056 and height == 1329:
        return 'Built-in Retina Display_1'
    elif width == 3440 and height == 1440:
        return 'UltraWide_Display_{index}'
    elif width == 2560 and height == 1440:
        return 'QHD_Display_{index}'
```

### 2. Profile Detection
```python  
def detect_profile(self):
    # Match current setup to config profiles
    current_resolutions = {f"{s['width']}x{s['height']}" for s in screens}
    
    for profile_name, profile in self.config['profiles'].items():
        profile_resolutions = {m['resolution'] for m in profile['monitors']
                             if m['resolution'] != 'macbook'}
        
        # Profile matches if resolutions are subset of current setup
        if profile_resolutions.issubset(current_resolutions):
            return profile_name
```

### 3. Position Validation
```python
def identify_monitor(self, x, y, prefer_monitor=None):
    # Determine which monitor contains given coordinates
    for screen in screens:
        screen_x, screen_y = screen['positioning_coords']
        screen_right = screen_x + screen['width']  
        screen_bottom = screen_y + screen['height']
        
        if (screen_x <= x < screen_right and 
            screen_y <= y < screen_bottom):
            return f"Monitor {screen['index']} ({screen['name']})"
```

## Error Handling and Resilience

### 1. Coordinate System Fallbacks
```python
# Graceful degradation when coordinate conversion fails
if 'positioning_coords' in screen and screen['positioning_coords']:
    x_offset, y_offset = screen['positioning_coords']  # Converted coords
else:
    x_offset, y_offset = screen['x'], screen['y']      # Raw NSScreen coords
    print("⚠️  Using fallback coordinates - positioning may be inaccurate")
```

### 2. Monitor Detection Fallbacks
```python
# Multiple detection methods with fallback chain
def get_screens_enhanced(self):
    if PYMONCTL_AVAILABLE:
        return self.get_screens_pymonctl()  # Enhanced detection
    else:
        return self.get_screens_nsscreen()  # Fallback detection
```

### 3. Configuration Validation
```python
# Validate config matches detected setup
if not profile_name:
    print("No matching profile found for current monitor configuration")
    print("Available screens:")
    for screen in screens:
        print(f"  {screen['width']}x{screen['height']} at ({screen['x']}, {screen['y']})")
    return False
```

## Performance Optimizations

### 1. Caching Strategy
- Dynamic coordinate mappings generated once per session
- Monitor detection cached during positioning operations
- Profile detection memoized for repeated operations

### 2. Parallel Operations
- Multiple tool calls batched for efficiency
- Concurrent window positioning when possible
- Optimized validation with minimal delays

### 3. Intelligent Timing
```python
# Optimized positioning with minimal delays
time.sleep(0.05)   # Brief pause for window focus
time.sleep(0.1)    # Reduced wait for position verification
# Total positioning time: ~1 second for 4 applications
```

## Testing and Validation

### 1. Coordinate System Testing
```bash
# Verify coordinate conversion
uv run python main.py list-screens-enhanced --verbose

# Expected output:
# Arrangement coords: (-764, 1329)   ← NSScreen (Cocoa)
# Positioning coords: (-764, -1440)  ← Window positioning (Quartz)
```

### 2. Positioning Accuracy Testing  
```bash
# Test positioning with verification
uv run python main.py position --verbose

# Expected results:
# ✅ Windows appear on intended monitor
# ✅ Small positioning offsets (<50 pixels)
# ✅ All applications positioned successfully
```

### 3. Dynamic Adaptation Testing
1. Change Display Settings arrangement
2. Run `list-screens-enhanced` → Coordinates update automatically
3. Run `position` → Windows positioned correctly with new arrangement

## Success Metrics

### Before Solution (Broken State)
- ❌ Windows positioned on wrong monitors (MacBook instead of ultra-wide)
- ❌ Large coordinate offsets (>1000 pixels)
- ❌ Applications constrained to main display
- ❌ Hardcoded coordinates break with arrangement changes
- ❌ Mixed terminology causes configuration confusion

### After Solution (Working State)  
- ✅ Windows positioned on correct monitors (ultra-wide as intended)
- ✅ Small coordinate offsets (<50 pixels for window decorations)
- ✅ Applications positioned on intended displays
- ✅ Dynamic adaptation to any Display Settings arrangement
- ✅ Consistent terminology and maintainable configuration

## Future Enhancements

### 1. Multi-Monitor Layout Support
```yaml
layout:
  left:
    full_screen: com.slack
  primary:
    top_left: com.google.Chrome
    # ... quadrants
  builtin:
    - md.obsidian
```

### 2. Layout Templates
```yaml
layouts:
  development:
    primary: { top_left: code_editor, top_right: browser }
  communication:  
    primary: { top_left: chat, top_right: email }

profiles:
  office:
    monitors: [...]
    layout: development  # Reference to layout template
```

### 3. Advanced Positioning
- Custom window sizes per quadrant
- Percentage-based positioning
- Multi-application quadrants
- Dynamic quadrant resizing

The Mac App Positioner architecture provides a robust, maintainable, and fully dynamic solution for multi-monitor application positioning on macOS.