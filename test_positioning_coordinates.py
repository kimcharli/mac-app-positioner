#!/usr/bin/env python3
"""
Test if pymonctl coordinate system matches actual positioning
"""

import pymonctl
import pyautogui
import time
from Cocoa import NSScreen

def analyze_coordinate_systems():
    """Compare coordinate systems and test actual positioning"""
    print("=" * 60)
    print("COORDINATE SYSTEM ANALYSIS")
    print("=" * 60)
    
    # Get all detection methods
    print("1. NSScreen detection:")
    screens = NSScreen.screens()
    for i, screen in enumerate(screens):
        frame = screen.frame()
        main_indicator = " (main)" if screen == NSScreen.mainScreen() else ""
        print(f"   Screen {i}: {int(frame.size.width)}x{int(frame.size.height)} at ({int(frame.origin.x)}, {int(frame.origin.y)}){main_indicator}")
    
    print("\n2. pymonctl detection:")
    monitors = pymonctl.getAllMonitors()
    for i, monitor in enumerate(monitors):
        pos = monitor.position
        size = monitor.size
        primary = " (primary)" if hasattr(monitor, 'isPrimary') and monitor.isPrimary else ""
        print(f"   Monitor {i} ({monitor.name}): {size.width}x{size.height} at ({pos.x}, {pos.y}){primary}")
    
    # Test mouse positioning to understand coordinate space
    print("\n3. Current mouse position:")
    try:
        mouse_pos = pyautogui.position()
        print(f"   Mouse at: ({mouse_pos.x}, {mouse_pos.y})")
        
        # Test which coordinate system mouse uses
        print("\n4. Analyzing mouse coordinate system:")
        print("   Move your mouse to different monitors and observe coordinates...")
        
        for i in range(5):
            pos = pyautogui.position() 
            print(f"   Mouse position {i+1}: ({pos.x}, {pos.y})")
            
            # Check which monitor this position falls into
            for j, monitor in enumerate(monitors):
                mon_pos = monitor.position
                mon_size = monitor.size
                
                if (mon_pos.x <= pos.x < mon_pos.x + mon_size.width and 
                    mon_pos.y <= pos.y < mon_pos.y + mon_size.height):
                    print(f"      -> This is on Monitor {j} ({monitor.name})")
                    break
            else:
                print(f"      -> Position not clearly on any detected monitor")
            
            time.sleep(2)
            
    except Exception as e:
        print(f"Error with mouse positioning test: {e}")

def test_pymonctl_positioning():
    """Test if we can use pymonctl coordinates for positioning"""
    print("\n" + "=" * 60)
    print("PYMONCTL POSITIONING COORDINATE TEST")
    print("=" * 60)
    
    monitors = pymonctl.getAllMonitors()
    
    # Find the 4K monitor (SAMSUNG)
    target_monitor = None
    for monitor in monitors:
        if monitor.size.width == 3840 and monitor.size.height == 2160:
            target_monitor = monitor
            break
    
    if target_monitor:
        pos = target_monitor.position
        size = target_monitor.size
        
        print(f"4K Monitor ({target_monitor.name}):")
        print(f"  Position: ({pos.x}, {pos.y})")
        print(f"  Size: {size.width}x{size.height}")
        
        # Calculate test positions on this monitor
        test_positions = {
            'top_left': (pos.x + 100, pos.y + 100),
            'top_right': (pos.x + size.width//2, pos.y + 100),
            'center': (pos.x + size.width//2, pos.y + size.height//2),
        }
        
        print(f"\nCalculated test positions on 4K monitor:")
        for name, (x, y) in test_positions.items():
            print(f"  {name}: ({x}, {y})")
            
        # The question: Do these coordinates work for window positioning?
        print(f"\nThese coordinates should work if pymonctl matches positioning coordinate system")
        
        # Check if coordinates are positive or negative
        if pos.y > 0:
            print(f"  ⚠️  pymonctl shows positive Y ({pos.y}) - same as NSScreen")
            print(f"      But we know negative coordinates worked for positioning!")
            print(f"      This suggests pymonctl uses same coord system as NSScreen")
        elif pos.y < 0:
            print(f"  ✅ pymonctl shows negative Y ({pos.y}) - matches working positioning")
        else:
            print(f"  ℹ️  pymonctl shows Y=0 - monitor at origin")
    else:
        print("4K monitor not found in pymonctl detection")

if __name__ == "__main__":
    analyze_coordinate_systems()
    test_pymonctl_positioning()