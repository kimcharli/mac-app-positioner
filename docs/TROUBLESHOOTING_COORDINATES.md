# Coordinate System Troubleshooting Guide

Quick reference for diagnosing and fixing coordinate-related positioning issues.

## Quick Diagnosis Commands

### 1. Check Current Coordinate Systems
```bash
uv run python main.py list-screens-enhanced --verbose
```

**Expected Output:**
```
Monitor 2 (UltraWide_Display_2):
  Arrangement coords: (-764, 1329)     ← NSScreen (Cocoa) 
  Positioning coords: (-764, -1440)    ← Window positioning (Quartz)
  Translation rule: above_primary      ← Correct for monitor above MacBook
```

### 2. Test Positioning
```bash
uv run python main.py position --verbose
```

**Success Indicators:**
- ✅ `Window is on: Monitor 2 (UltraWide_Display_2)`
- ✅ Small offsets (`Position differs by (0, 25) pixels`)
- ✅ All apps positioned successfully

## Common Issues and Fixes

### Issue 1: Windows Appear on Wrong Monitor

**Symptoms:**
```
Window is on: Monitor 0 (Built-in Retina Display_1)
Target: Should be on ultra-wide monitor
```

**Diagnosis:**
```bash
# Check if coordinates are converted properly
uv run python main.py list-screens-enhanced | grep "Positioning coords"
```

**Fix:**
Ensure coordinate conversion is working:
- NSScreen Y > 0 should convert to Quartz Y < 0 for monitors above main
- Check `coordinate_source: 'cocoa_to_quartz_conversion'` in output

### Issue 2: Large Coordinate Offsets

**Symptoms:**
```
❌ OFFSET: Position differs by (1000, 800) pixels
```

**Diagnosis:**
```bash
# Check if using raw NSScreen coordinates
grep "positioning (.*primary)" position_output.log
```

**Fix:**
- Verify coordinate conversion is enabled
- Check for `using rule: above_primary` instead of `below_primary`
- Raw NSScreen coordinates (no conversion) cause massive offsets

### Issue 3: Monitor Above Main Display Not Recognized

**Symptoms:**
```
Translation rule: below_primary  # Should be above_primary
Positioning coords: (-764, 1329) # Should be (-764, -1440)
```

**Root Cause:** Coordinate conversion not applied

**Fix:**
```python
# In generate_dynamic_coordinate_mappings()
if cocoa_y > 0:
    # Monitor is "below" main in Cocoa = "above" main in Quartz
    quartz_y = -height  # This converts to negative Y
```

### Issue 4: Profile Not Found

**Symptoms:**
```
No matching profile found for current monitor configuration
```

**Diagnosis:**
```bash
# Check detected vs configured resolutions
uv run python main.py detect
uv run python main.py list-screens
```

**Fix:**
Update config.yaml to match detected resolutions:
```yaml
office:
  monitors:
  - resolution: 3440x1440  # Must match detected resolution exactly
    position: primary
```

## Verification Checklist

### ✅ Coordinate System Health Check

1. **NSScreen Detection:**
   ```
   ✅ Multiple monitors detected
   ✅ Main display identified correctly  
   ✅ Resolutions match physical setup
   ```

2. **Coordinate Conversion:**
   ```
   ✅ Arrangement coords ≠ Positioning coords (for non-main displays)
   ✅ Monitors above main have negative positioning Y
   ✅ Translation rules match physical layout
   ```

3. **Configuration Matching:**
   ```
   ✅ Profile detected automatically
   ✅ Primary monitor resolution matches config
   ✅ Layout section accessible
   ```

4. **Positioning Results:**
   ```
   ✅ Windows appear on intended monitor
   ✅ Coordinate offsets < 100 pixels
   ✅ All applications positioned successfully
   ```

## Advanced Debugging

### Check Window API Coordinates
```python
# Verify actual window positions match Quartz coordinate system
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly

windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
for window in windows[:3]:
    bounds = window.get('kCGWindowBounds', {})
    x, y = bounds.get('X', 0), bounds.get('Y', 0)
    print(f"Actual window: {window.get('kCGWindowOwnerName')} at ({x}, {y})")
    # For monitors above main display, expect negative Y values
```

### Manual Coordinate Conversion Test
```python
# Test coordinate conversion logic
cocoa_y = 1329  # NSScreen Y for monitor "below" main
main_height = 1329  # Main display height
monitor_height = 1440  # Ultra-wide height

# Expected conversion for monitor above main:
quartz_y = -monitor_height  # Should be -1440
print(f"Cocoa Y: {cocoa_y} → Quartz Y: {quartz_y}")
```

### Profile Matching Debug
```python
# Check resolution matching logic
detected_resolutions = {'2056x1329', '2560x1440', '3440x1440'}
profile_resolutions = {'3440x1440', '2560x1440'}  # From config

print(f"Profile matches: {profile_resolutions.issubset(detected_resolutions)}")
# Should be True for successful matching
```

## Emergency Fixes

### Temporary Override
If coordinate conversion fails, add temporary override:
```python
# In get_physical_layout_overrides()
return {
    '3440x1440': {
        'x': -764,
        'y': -1440,  # Force correct coordinates
        'rule': 'above_primary_override'
    }
}
```

### Reset to Known Good State
```bash
# Backup current config
cp config.yaml config.yaml.backup

# Use minimal config for testing
cat > config.yaml << 'EOF'
layout:
  primary:
    top_left: com.google.Chrome
  builtin:
    - md.obsidian

profiles:
  office:
    monitors:
    - resolution: 2056x1329
      position: primary
EOF

# Test with MacBook as primary
uv run python main.py position
```

### Force Profile Selection
```bash
# Skip auto-detection and force specific profile
uv run python main.py position office
```

## When to Contact Support

Contact support if:
- ✅ Coordinate conversion shows correct values
- ✅ Profile detection works correctly  
- ✅ Configuration matches detected monitors
- ❌ Windows still positioned incorrectly

Provide debug output:
```bash
uv run python main.py list-screens-enhanced --verbose > debug_output.txt
uv run python main.py position --verbose >> debug_output.txt
```

The coordinate system conversion is the most critical component - when working correctly, positioning should be accurate within ~50 pixels.