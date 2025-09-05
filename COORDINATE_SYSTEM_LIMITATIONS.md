# macOS Multi-Monitor Coordinate System Limitations

This document outlines critical limitations and discoveries about macOS coordinate systems for multi-monitor window positioning.

## Critical Discovery: Dual Coordinate Systems

### The Problem
macOS uses **two different coordinate systems** for multi-monitor setups, which creates confusion and positioning failures when not properly understood.

### Two Coordinate Systems Exist

#### 1. Display Arrangement Coordinates (NSScreen/pymonctl)
**Purpose**: Used for display settings, arrangement configuration, and system information.

**Characteristics**:
- Primary display is always at (0, 0)
- Other displays positioned relative to primary
- Matches what you see in System Settings > Displays
- **Cannot be used directly for window positioning**

**Example**:
```
MacBook (Primary): 2056x1329 at (0, 0)
4K Monitor (Above): 3840x2160 at (0, 1329)  # Reports positive Y!
Left Monitor: 2560x1440 at (-2560, 969)
```

#### 2. Positioning Coordinates (Mouse/Window/Accessibility API)
**Purpose**: Used for actual positioning of mouse cursors, windows, and interactive elements.

**Characteristics**:
- Uses different coordinate space than display arrangement
- Monitors above primary display use **negative Y coordinates**
- Monitors below primary display use **positive Y coordinates**
- **This is what actually works for window positioning**

**Example**:
```
MacBook (Primary): 2056x1329 at (0, 0)
4K Monitor (Above): 3840x2160 at (0, -831)   # Negative Y for positioning!
Left Monitor: 2560x1440 at (-2560, 969)      # Same as arrangement
```

### Evidence of Dual System

#### NSScreen vs Reality Test
```python
# NSScreen reports 4K monitor at:
Screen 2: 3840x2160 at (0, 1329)

# But mouse positioning shows:
Mouse at: (2057, -609)  # Negative Y coordinates!

# Window positioning that works:
Target: (100, -880)  # Negative Y
Actual: (100, -880)  # ✅ Perfect match

# Window positioning that fails:
Target: (100, 1429)  # Positive Y from NSScreen
Actual: (100, 1288)  # ❌ Clamped to MacBook bounds
```

## Limitation Categories

### 1. API Documentation Limitations

**Problem**: Apple's documentation doesn't clearly distinguish between the two coordinate systems.

**Impact**:
- Developers assume NSScreen coordinates work for positioning
- Window positioning fails mysteriously
- Workarounds involve changing main display settings

**Evidence**:
- NSScreen.frame() provides arrangement coordinates
- AXUIElementSetAttributeValue() expects positioning coordinates
- No official documentation explains the translation

### 2. Library Limitations

#### NSScreen (Native macOS)
```python
# What it provides:
screens = NSScreen.screens()
frame = screen.frame()  # Display arrangement coordinates

# What it DOESN'T provide:
# - Positioning coordinates
# - Coordinate system translation
# - Physical arrangement detection
```

**Limitations**:
- Only provides display arrangement info
- Cannot detect actual positioning coordinate space
- No built-in translation between coordinate systems

#### pymonctl
```python
# What it provides:
monitors = pymonctl.getAllMonitors()
position = monitor.position  # Same as NSScreen - arrangement coordinates
size = monitor.size
name = monitor.name  # Bonus: Monitor names!

# What it DOESN'T provide:
# - Positioning coordinates
# - Automatic coordinate translation
```

**Limitations**:
- Uses same coordinate system as NSScreen
- Still requires manual translation for positioning
- **Advantage**: Provides monitor names for better identification

#### pyautogui
```python
# What it provides:
size = pyautogui.size()  # Primary display size only
pos = pyautogui.position()  # Mouse position in positioning coordinates!

# What it DOESN'T provide:
# - Multi-monitor detection (no getAllMonitors())
# - Monitor arrangement information
# - Size/bounds of secondary monitors
```

**Limitations**:
- No multi-monitor support for detection
- **Advantage**: Mouse coordinates use positioning system

### 3. Coordinate Translation Limitations

#### No Built-in Translation
**Problem**: No macOS API provides automatic translation between coordinate systems.

**Manual Translation Required**:
```python
# For monitors above primary display:
def translate_to_positioning_coords(arrangement_x, arrangement_y, monitor_height):
    positioning_x = arrangement_x  # X coordinates match
    positioning_y = arrangement_y - primary_height  # Translate Y
    return positioning_x, positioning_y

# Example:
# Arrangement: (0, 1329) for 4K above MacBook
# Translation: (0, 1329 - 1329) = (0, 0)
# But empirically: (0, -831) works for positioning
```

**Translation Complexity**:
- Rules vary based on monitor position (above/below/left/right)
- No standard formula - requires empirical testing
- Different for each physical arrangement

### 4. Detection Limitations

#### Physical Arrangement Detection
**Problem**: Cannot reliably detect physical monitor arrangement programmatically.

**What We Know**:
```python
# Display arrangement coordinates:
4K Monitor: (0, 1329)  # Suggests "below" MacBook

# But physical reality:
4K Monitor is ABOVE MacBook  # Requires negative positioning coordinates
```

**Detection Challenges**:
- Arrangement coordinates don't match physical layout
- No API to query "physical above/below/left/right" relationships
- Must infer from coordinate patterns and trial-and-error

#### Assumption-Based Workarounds
**Current Solution**: Hardcoded assumptions based on monitor characteristics.

```python
# Problematic assumption-based code:
if monitor.size.width == 3840 and monitor.size.height == 2160:
    # ASSUME this 4K monitor is above MacBook
    # ASSUME negative coordinates needed
    positioning_y = -monitor_height + padding
```

**Limitations**:
- Breaks with different monitor arrangements
- Not portable across different setups
- Requires manual configuration per setup

### 5. Testing and Validation Limitations

#### No Validation Tools
**Problem**: No built-in tools to validate coordinate system translation.

**Manual Validation Required**:
```python
# Must implement custom validation:
def validate_positioning(target_coords, actual_coords):
    x_diff = abs(actual_coords.x - target_coords.x)
    y_diff = abs(actual_coords.y - target_coords.y) 
    return x_diff <= 5 and y_diff <= 5  # 5px tolerance
```

#### Trial-and-Error Development
**Problem**: Requires empirical testing to determine correct coordinates.

**Development Process**:
1. Try NSScreen coordinates → Fails
2. Try negative coordinates → May work
3. Try manual translations → Hit-or-miss
4. Test with actual window positioning → Verify results
5. Hardcode working solution → Not portable

## Architectural Implications

### 1. Cannot Trust Single Source
**No single API provides complete picture**:
- NSScreen: Display arrangement only
- pymonctl: Same as NSScreen + names
- pyautogui: Mouse positioning only
- Must combine multiple sources

### 2. Requires Translation Layer
**Essential Architecture**:
```python
class CoordinateTranslator:
    def __init__(self):
        self.arrangement_coords = self.get_arrangement_coords()  # NSScreen/pymonctl
        self.positioning_coords = self.detect_positioning_coords()  # Empirical
    
    def translate(self, arrangement_coord):
        return self.empirical_translation(arrangement_coord)
```

### 3. Configuration-Dependent
**Each monitor setup requires**:
- Empirical testing of coordinate translation
- Custom translation rules
- Validation of positioning accuracy
- **Cannot be fully automated**

## Workaround Strategies

### 1. Empirical Coordinate Mapping
**Strategy**: Test actual positioning coordinates for each monitor.

```python
def discover_positioning_coords(monitor):
    # Try various coordinate translations
    # Test actual window positioning
    # Return working coordinates
    pass
```

### 2. Configuration-Based Approach
**Strategy**: Store working coordinates per monitor setup.

```python
# config.yaml
coordinate_mappings:
  "SAMSUNG_3":  # 4K monitor name from pymonctl
    arrangement: [0, 1329]
    positioning: [0, -831]
    translation_rule: "above_primary"
```

### 3. Hybrid Detection
**Strategy**: Combine multiple detection methods.

```python
def detect_monitors():
    # pymonctl for names and arrangement
    # pyautogui for positioning validation  
    # NSScreen for fallback
    # Custom translation rules
```

## Recommendations

### 1. For Development
- **Never assume** NSScreen coordinates work for positioning
- **Always validate** positioning with actual window movement
- **Implement** comprehensive coordinate translation testing
- **Document** working coordinates for each monitor setup

### 2. For Users
- **Expect** initial setup and calibration per monitor arrangement
- **Test** positioning after any display setting changes
- **Understand** that changing main display affects coordinate systems

### 3. For Apple/Framework Developers
- **Provide** unified coordinate system for positioning
- **Document** the dual coordinate system clearly
- **Add** APIs for coordinate system translation
- **Include** physical arrangement detection methods

## Current State: Manual Configuration Required

**Bottom Line**: macOS multi-monitor coordinate systems require **manual configuration and empirical testing** for each monitor arrangement. No fully automated solution exists due to the fundamental limitations in coordinate system detection and translation APIs.

**Success Strategy**: Combine pymonctl detection + empirical coordinate testing + configuration storage for each unique monitor setup.