#!/usr/bin/env python3
"""
Test pyautogui capabilities for multi-monitor
"""

import pyautogui
import inspect

def test_pyautogui_methods():
    """Check what methods pyautogui has"""
    print("pyautogui available methods:")
    methods = [method for method in dir(pyautogui) if not method.startswith('_')]
    
    monitor_related = []
    for method in methods:
        if any(keyword in method.lower() for keyword in ['monitor', 'screen', 'display', 'size']):
            monitor_related.append(method)
    
    print("Monitor/screen related methods:")
    for method in sorted(monitor_related):
        try:
            func = getattr(pyautogui, method)
            if callable(func):
                print(f"  {method}() - {func.__doc__[:50] if func.__doc__ else 'No doc'}")
        except:
            print(f"  {method} - (attribute)")
    
    # Test basic methods
    print(f"\nScreen size: {pyautogui.size()}")
    
    # Check if there are any monitor-related functions
    try:
        print(f"Position: {pyautogui.position()}")
    except Exception as e:
        print(f"Position error: {e}")

if __name__ == "__main__":
    test_pyautogui_methods()