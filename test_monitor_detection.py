#!/usr/bin/env python3
"""
Test monitor detection capabilities using pymonctl and pyautogui
"""

import pymonctl
import pyautogui

def test_pymonctl():
    """Test pymonctl monitor detection"""
    print("=" * 50)
    print("PYMONCTL MONITOR DETECTION")
    print("=" * 50)
    
    try:
        monitors = pymonctl.getAllMonitors()
        print(f"Found {len(monitors)} monitors:")
        
        for i, monitor in enumerate(monitors):
            print(f"\nMonitor {i}:")
            print(f"  Name: {monitor.name if hasattr(monitor, 'name') else 'Unknown'}")
            print(f"  Size: {monitor.size}")
            print(f"  Position: {monitor.position}")
            print(f"  Primary: {monitor.isPrimary if hasattr(monitor, 'isPrimary') else 'Unknown'}")
            
            if hasattr(monitor, 'box'):
                print(f"  Box (left, top, right, bottom): {monitor.box}")
            
            if hasattr(monitor, 'workArea'):
                print(f"  Work Area: {monitor.workArea}")
                
        # Get primary monitor
        try:
            primary = pymonctl.getPrimary()
            print(f"\nPrimary monitor: {primary.name if hasattr(primary, 'name') else 'Unknown'}")
            print(f"Primary position: {primary.position}")
            print(f"Primary size: {primary.size}")
        except Exception as e:
            print(f"Error getting primary monitor: {e}")
            
    except Exception as e:
        print(f"Error with pymonctl: {e}")

def test_pyautogui():
    """Test pyautogui monitor detection"""
    print("\n" + "=" * 50)
    print("PYAUTOGUI MONITOR DETECTION")
    print("=" * 50)
    
    try:
        # Get all monitors
        monitors = pyautogui.getAllMonitors()
        print(f"Found {len(monitors)} monitors:")
        
        for i, monitor in enumerate(monitors):
            print(f"\nMonitor {i}: {monitor}")
            
        # Get screen size
        screen_size = pyautogui.size()
        print(f"\nScreen size: {screen_size}")
        
        # Test positioning on different monitors
        print("\nTesting monitor coordinate spaces:")
        for i, monitor in enumerate(monitors):
            left, top, width, height = monitor
            center_x = left + width // 2
            center_y = top + height // 2
            print(f"Monitor {i} center would be at: ({center_x}, {center_y})")
            
    except Exception as e:
        print(f"Error with pyautogui: {e}")

def compare_detection_methods():
    """Compare different detection methods"""
    print("\n" + "=" * 50)
    print("COMPARISON WITH NSScreen")
    print("=" * 50)
    
    try:
        from Cocoa import NSScreen
        
        # NSScreen data
        screens = NSScreen.screens()
        print("NSScreen reports:")
        for i, screen in enumerate(screens):
            frame = screen.frame()
            main_indicator = " (main)" if screen == NSScreen.mainScreen() else ""
            print(f"  Screen {i}: {int(frame.size.width)}x{int(frame.size.height)} at ({int(frame.origin.x)}, {int(frame.origin.y)}){main_indicator}")
            
        # pyautogui data
        print("\npyautogui reports:")
        monitors = pyautogui.getAllMonitors()
        for i, monitor in enumerate(monitors):
            left, top, width, height = monitor
            print(f"  Monitor {i}: {width}x{height} at ({left}, {top})")
            
        # pymonctl data
        print("\npymonctl reports:")
        monitors = pymonctl.getAllMonitors()
        for i, monitor in enumerate(monitors):
            pos = monitor.position
            size = monitor.size
            primary = " (primary)" if hasattr(monitor, 'isPrimary') and monitor.isPrimary else ""
            print(f"  Monitor {i}: {size.width}x{size.height} at ({pos.x}, {pos.y}){primary}")
            
    except Exception as e:
        print(f"Error in comparison: {e}")

if __name__ == "__main__":
    test_pymonctl()
    test_pyautogui()
    compare_detection_methods()