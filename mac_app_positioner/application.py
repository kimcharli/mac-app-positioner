"""Application management for Mac App Positioner."""

import time
from Cocoa import NSWorkspace
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from ApplicationServices import (
    AXUIElementCreateApplication, AXUIElementCopyAttributeNames,
    AXUIElementCopyAttributeValue, AXUIElementSetAttributeValue,
    AXValueCreate, AXValueGetValue, kAXValueCGPointType, kAXValueCGSizeType,
    kAXWindowsAttribute, kAXPositionAttribute, kAXSizeAttribute,
    kAXMainAttribute, AXUIElementPerformAction, kAXRaiseAction,
    AXIsProcessTrusted
)

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class ApplicationManager:
    def __init__(self, verbose=False):
        self.verbose = verbose
        if verbose:
            if PYAUTOGUI_AVAILABLE:
                print("✅ pyautogui available - positioning validation enabled")
            else:
                print("⚠️  pyautogui not available - no positioning validation")

    def print_verbose(self, message):
        """Print message only if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def get_running_applications(self):
        """Get list of running applications"""
        workspace = NSWorkspace.sharedWorkspace()
        running_apps = workspace.runningApplications()
        
        apps = []
        for app in running_apps:
            if not app.isHidden():
                apps.append({
                    'name': app.localizedName(),
                    'bundle_id': app.bundleIdentifier(),
                    'pid': app.processIdentifier()
                })
        
        return apps

    def check_accessibility_permissions(self):
        """Check if accessibility permissions are granted"""
        return AXIsProcessTrusted()

    def get_app_windows(self, pid):
        """Get all windows for an application"""
        try:
            app_ref = AXUIElementCreateApplication(pid)
            error_code, windows_attr = AXUIElementCopyAttributeValue(app_ref, kAXWindowsAttribute, None)
            return windows_attr if error_code == 0 and windows_attr else []
        except Exception as e:
            print(f"Error getting windows for PID {pid}: {e}")
            return []

    def get_window_position(self, pid):
        """Get current position and size of application window"""
        try:
            windows = self.get_app_windows(pid)
            if not windows:
                return None
            
            window = windows[0]
            
            error_code, position_value = AXUIElementCopyAttributeValue(window, kAXPositionAttribute, None)
            if error_code != 0:
                return None
                
            error_code, size_value = AXUIElementCopyAttributeValue(window, kAXSizeAttribute, None)
            if error_code != 0:
                return None
            
            position = AXValueGetValue(position_value, kAXValueCGPointType, None)[1]
            size = AXValueGetValue(size_value, kAXValueCGSizeType, None)[1]
            
            return {
                'x': int(position.x),
                'y': int(position.y),
                'width': int(size.width),
                'height': int(size.height)
            }
            
        except Exception as e:
            print(f"Error getting window position for PID {pid}: {e}")
            return None

    def get_window_size(self, pid):
        """Get window size for the specified PID"""
        try:
            app = AXUIElementCreateApplication(pid)
            error_code, windows = AXUIElementCopyAttributeValue(app, kAXWindowsAttribute, None)
            
            if error_code == 0 and windows:
                window = windows[0]
                error_code, size_value = AXUIElementCopyAttributeValue(window, kAXSizeAttribute, None)
                if error_code == 0:
                    size = AXValueGetValue(size_value, kAXValueCGSizeType, None)[1]
                    return {'width': int(size.width), 'height': int(size.height)}
            
        except Exception as e:
            print(f"Error getting window size for PID {pid}: {e}")
        
        return None

    def calculate_corner_aligned_position(self, quadrant_position, window_size, quadrant):
        """Calculate corner-aligned position based on quadrant and window size"""
        if not window_size:
            return quadrant_position
        
        x = quadrant_position['x']
        y = quadrant_position['y'] 
        quad_width = quadrant_position['width']
        quad_height = quadrant_position['height']
        
        if quadrant == 'top_left':
            aligned_x, aligned_y = x, y
        elif quadrant == 'top_right':
            aligned_x = x + quad_width - window_size['width']
            aligned_y = y
        elif quadrant == 'bottom_left':
            aligned_x = x
            aligned_y = y + quad_height - window_size['height']
        elif quadrant == 'bottom_right':
            aligned_x = x + quad_width - window_size['width'] 
            aligned_y = y + quad_height - window_size['height']
        else:
            aligned_x, aligned_y = x, y
            
        return {'x': aligned_x, 'y': aligned_y}

    def calculate_simple_corner_alignment(self, quadrant_position, quadrant):
        """Simple corner alignment using estimated small window sizes"""
        x = quadrant_position['x']
        y = quadrant_position['y'] 
        quad_width = quadrant_position['width']
        quad_height = quadrant_position['height']
        
        estimated_small_width = 300
        estimated_small_height = 400
        
        if quadrant == 'top_left':
            aligned_x, aligned_y = x, y
        elif quadrant == 'top_right':
            aligned_x = x + quad_width - estimated_small_width
            aligned_y = y
        elif quadrant == 'bottom_left':
            aligned_x = x
            aligned_y = y + quad_height - estimated_small_height
        elif quadrant == 'bottom_right':
            aligned_x = x + quad_width - estimated_small_width
            aligned_y = y + quad_height - estimated_small_height
        else:
            aligned_x, aligned_y = x, y
            
        return {'x': aligned_x, 'y': aligned_y}

    def move_application_window(self, pid, position, app_bundle_id=None, app_name=None, quadrant=None, positioning_strategy=None):
        """Move application window to specified position using accessibility APIs"""
        if not self.check_accessibility_permissions():
            print("❌ Accessibility permissions not granted!")
            print("Please grant accessibility permissions:")
            print("System Preferences > Privacy & Security > Accessibility")
            print("Add Terminal or your Python interpreter to the list")
            return False
        
        try:
            windows = self.get_app_windows(pid)
            if not windows:
                print(f"No windows found for PID {pid}")
                return False
            
            window = windows[0]
            self.print_verbose(f"Using first window (of {len(windows)} available)")
            
            AXUIElementPerformAction(window, kAXRaiseAction)
            time.sleep(0.05)
            
            window_size = None
            if quadrant:
                window_size = self.get_window_size(pid)
                self.print_verbose(f"DEBUG: Got window size for {quadrant}: {window_size}")
            
            if quadrant and window_size:
                aligned_position = self.calculate_corner_aligned_position(position, window_size, quadrant)
                self.print_verbose(f"Corner alignment: {quadrant} adjusted position from ({position['x']}, {position['y']}) to ({aligned_position['x']}, {aligned_position['y']})")
            else:
                if quadrant:
                    aligned_position = self.calculate_simple_corner_alignment(position, quadrant)
                    self.print_verbose(f"Fallback corner alignment: {quadrant} adjusted position from ({position['x']}, {position['y']}) to ({aligned_position['x']}, {aligned_position['y']})")
                else:
                    aligned_position = position
            
            if positioning_strategy == 'chrome':
                return self._move_chrome_window(window, aligned_position, pid, app_name)
            else:
                return self._move_standard_window(window, aligned_position, pid, app_name)
                
        except Exception as e:
            print(f"❌ Error positioning window for PID {pid}: {e}")
            return False

    def _move_standard_window(self, window, aligned_position, pid, app_name=None):
        """Standard window positioning for most applications"""
        new_position = (float(aligned_position['x']), float(aligned_position['y']))
        position_value = AXValueCreate(kAXValueCGPointType, new_position)
        
        if app_name:
            print(f"Positioning {app_name}...")
        else:
            print(f"Attempting to move window to final position: ({aligned_position['x']}, {aligned_position['y']})")
        
        pos_result = AXUIElementSetAttributeValue(window, kAXPositionAttribute, position_value)
        
        if pos_result == 0:
            if app_name:
                print(f"✅ {app_name} positioned successfully")
            else:
                print(f"✅ Position command accepted for PID {pid}")
            
            return True
        else:
            print(f"❌ Position command rejected for PID {pid} (code: {pos_result})")
            return False

    def _move_chrome_window(self, window, aligned_position, pid, app_name=None):
        """Chrome-specific positioning with multiple strategies"""
        target_x, target_y = float(aligned_position['x']), float(aligned_position['y'])
        target_width, target_height = 0, 0
        
        if app_name:
            print(f"Positioning {app_name}...")
        
        self.print_verbose(f"🔄 Chrome detected - using multi-attempt positioning strategy")
        self.print_verbose(f"Target: ({target_x}, {target_y}) {target_width}x{target_height}")
        
        self.print_verbose("Strategy 1: Direct positioning")
        position_value = AXValueCreate(kAXValueCGPointType, (target_x, target_y))
        pos_result = AXUIElementSetAttributeValue(window, kAXPositionAttribute, position_value)
        
        if pos_result == 0:
            time.sleep(0.1)
            actual_pos = self.get_window_position(pid)
            if actual_pos:
                x_diff = abs(actual_pos['x'] - target_x)
                y_diff = abs(actual_pos['y'] - target_y)
                if x_diff <= 25 and y_diff <= 25:
                    if app_name:
                        print(f"✅ {app_name} positioned successfully")
                    self.print_verbose(f"✅ Chrome positioned successfully with {x_diff}px/{y_diff}px offset")
                    return True
                else:
                    self.print_verbose(f"⚠️  Chrome offset detected: actual ({actual_pos['x']}, {actual_pos['y']}) vs target ({target_x}, {target_y})")
        
        print("Strategy 2: Skipped - direct positioning should work with correct coordinates")
        
        print("Strategy 3: Coordinate adjustment for Chrome offset pattern")
        print("⚠️  Strategy 3 disabled - hardcoded offsets were incorrect")
        return False

    def validate_positioning_with_pyautogui(self, target_x, target_y):
        """Validate positioning coordinates using pyautogui mouse positioning"""
        if not PYAUTOGUI_AVAILABLE:
            return None
        
        try:
            original_pos = pyautogui.position()
            
            pyautogui.moveTo(target_x, target_y, duration=0.1)
            validation_pos = pyautogui.position()
            
            pyautogui.moveTo(original_pos.x, original_pos.y, duration=0.1)
            
            x_diff = abs(validation_pos.x - target_x)
            y_diff = abs(validation_pos.y - target_y)
            
            return {
                'target': (target_x, target_y),
                'actual': (validation_pos.x, validation_pos.y),
                'x_diff': x_diff,
                'y_diff': y_diff,
                'precise': x_diff <= 5 and y_diff <= 5
            }
            
        except Exception as e:
            print(f"Error validating coordinates with pyautogui: {e}")
            return None

    def list_applications(self):
        """List running applications"""
        apps = self.get_running_applications()
        print("Running applications:")
        for app in apps:
            print(f"  {app['name']} ({app['bundle_id']})")