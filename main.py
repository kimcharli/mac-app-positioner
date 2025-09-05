#!/usr/bin/env python3
"""
Mac App Positioner - A utility for positioning macOS applications across monitors
"""

import yaml
import sys
import os
import time
from Cocoa import NSScreen, NSApplication, NSWorkspace

# Enhanced monitor detection
try:
    import pymonctl
    PYMONCTL_AVAILABLE = True
    print("✅ pymonctl available - using enhanced monitor detection")
except ImportError:
    PYMONCTL_AVAILABLE = False
    print("⚠️  pymonctl not available - using NSScreen fallback")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    print("✅ pyautogui available - positioning validation enabled")
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️  pyautogui not available - no positioning validation")
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from ApplicationServices import (
    AXUIElementCreateApplication, AXUIElementCopyAttributeNames,
    AXUIElementCopyAttributeValue, AXUIElementSetAttributeValue,
    AXValueCreate, AXValueGetValue, kAXValueCGPointType, kAXValueCGSizeType,
    kAXWindowsAttribute, kAXPositionAttribute, kAXSizeAttribute,
    kAXMainAttribute, AXUIElementPerformAction, kAXRaiseAction,
    AXIsProcessTrusted
)


class MacAppPositioner:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.coordinate_mappings = self.load_coordinate_mappings()
    
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Configuration file {self.config_path} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def load_coordinate_mappings(self):
        """Load coordinate mappings for monitor positioning"""
        # Default coordinate mappings based on our discoveries
        return {
            'SAMSUNG_3': {  # 4K monitor - coordinates depend on which display is main
                'arrangement': (0, 1329),      # When MacBook is main
                'positioning': (0, -2160),     # When MacBook is main (above MacBook)
                'positioning_when_main': (0, 0),  # When Samsung is main (at origin)
                'translation_rule': 'adaptive_based_on_main_display'
            },
            'Built-in Retina Display_1': {  # MacBook built-in
                'arrangement': (0, 0),
                'positioning': (0, 0),
                'translation_rule': 'primary'
            },
            'LEN P24h-20_2': {  # Left monitor
                'arrangement': (-2560, 969),
                'positioning': (-2560, 969),
                'translation_rule': 'left_of_primary'
            }
        }
    
    def get_screens_enhanced(self):
        """Enhanced monitor detection using hybrid approach"""
        if PYMONCTL_AVAILABLE:
            return self.get_screens_pymonctl()
        else:
            print("Falling back to NSScreen detection")
            return self.get_screens_nsscreen()
    
    def get_screens_pymonctl(self):
        """Get monitor information using pymonctl (primary method)"""
        try:
            monitors = pymonctl.getAllMonitors()
            screen_info = []
            
            for i, monitor in enumerate(monitors):
                pos = monitor.position
                size = monitor.size
                
                # Enhanced information from pymonctl
                monitor_info = {
                    'index': i,
                    'name': monitor.name,
                    'width': size.width,
                    'height': size.height,
                    'x': pos.x,
                    'y': pos.y,
                    'is_main': hasattr(monitor, 'isPrimary') and monitor.isPrimary,
                    'work_area': getattr(monitor, 'workArea', None),
                    'source': 'pymonctl'
                }
                
                # Add coordinate translation if available
                if monitor.name in self.coordinate_mappings:
                    mapping = self.coordinate_mappings[monitor.name]
                    
                    # Use appropriate coordinates based on whether this monitor is main
                    is_main = hasattr(monitor, 'isPrimary') and monitor.isPrimary
                    if is_main and 'positioning_when_main' in mapping:
                        monitor_info['positioning_coords'] = mapping['positioning_when_main']
                        monitor_info['translation_rule'] = f"{mapping['translation_rule']}_as_main"
                    else:
                        monitor_info['positioning_coords'] = mapping['positioning']
                        monitor_info['translation_rule'] = mapping['translation_rule']
                else:
                    # Default: same as arrangement coordinates
                    monitor_info['positioning_coords'] = (pos.x, pos.y)
                    monitor_info['translation_rule'] = 'unknown'
                
                screen_info.append(monitor_info)
            
            return screen_info
            
        except Exception as e:
            print(f"Error with pymonctl detection: {e}")
            print("Falling back to NSScreen detection")
            return self.get_screens_nsscreen()
    
    def get_screens_nsscreen(self):
        """Fallback monitor detection using NSScreen"""
        screens = NSScreen.screens()
        screen_info = []
        
        for i, screen in enumerate(screens):
            frame = screen.frame()
            screen_info.append({
                'index': i,
                'name': f'Screen_{i}',  # NSScreen doesn't provide names
                'width': int(frame.size.width),
                'height': int(frame.size.height),
                'x': int(frame.origin.x),
                'y': int(frame.origin.y),
                'is_main': screen == NSScreen.mainScreen(),
                'positioning_coords': (int(frame.origin.x), int(frame.origin.y)),  # Assume same as arrangement
                'translation_rule': 'nsscreen_fallback',
                'source': 'nsscreen'
            })
        
        return screen_info
    
    def get_screens(self):
        """Get information about connected screens (legacy method for compatibility)"""
        return self.get_screens_nsscreen()
    
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
    
    def detect_profile(self):
        """Detect which profile matches current monitor configuration"""
        screens = self.get_screens()
        current_resolutions = set(f"{s['width']}x{s['height']}" for s in screens)
        
        # Find profile that has the best match with current screen setup
        for profile_name, profile in self.config['profiles'].items():
            profile_resolutions = set()
            for monitor in profile['monitors']:
                if monitor['resolution'] != 'macbook':  # Skip macbook placeholder
                    profile_resolutions.add(monitor['resolution'])
            
            # Check if profile's resolutions are available in current setup
            if profile_resolutions.issubset(current_resolutions):
                return profile_name
        
        return None
    
    def calculate_quadrant_positions(self, screen):
        """Calculate quadrant positions for a screen using positioning coordinates"""
        width = screen['width']
        height = screen['height']
        
        # Use positioning coordinates if available, otherwise fall back to arrangement coordinates
        if 'positioning_coords' in screen and screen['positioning_coords']:
            x_offset, y_offset = screen['positioning_coords']
            coordinate_source = f"positioning ({screen.get('translation_rule', 'unknown')})"
        else:
            x_offset = screen['x']
            y_offset = screen['y']
            coordinate_source = "arrangement (fallback)"
        
        print(f"DEBUG: Using {coordinate_source} coordinates: x={x_offset}, y={y_offset}")
        print(f"DEBUG: Screen bounds: width={width}, height={height}")
        
        padding = 0  # Position at exact corners
        usable_width = width - (2 * padding)
        usable_height = height - (2 * padding)
        
        # Calculate quadrant dimensions
        quad_width = usable_width // 2
        quad_height = usable_height // 2
        
        positions = {
            'top_left': {
                'x': x_offset + padding,
                'y': y_offset + padding,
                'width': quad_width,
                'height': quad_height
            },
            'top_right': {
                'x': x_offset + padding + quad_width,
                'y': y_offset + padding,
                'width': quad_width,
                'height': quad_height
            },
            'bottom_left': {
                'x': x_offset + padding,
                'y': y_offset + padding + quad_height,
                'width': quad_width,
                'height': quad_height
            },
            'bottom_right': {
                'x': x_offset + padding + quad_width,
                'y': y_offset + padding + quad_height,
                'width': quad_width,
                'height': quad_height
            }
        }
        
        print("DEBUG: Calculated positions:")
        for name, pos in positions.items():
            print(f"  {name}: ({pos['x']}, {pos['y']}) -> ends at ({pos['x'] + pos['width']}, {pos['y'] + pos['height']})")
            
        return positions
    
    def position_applications(self, profile_name=None):
        """Position applications based on configuration"""
        if not profile_name:
            profile_name = self.detect_profile()
        
        if not profile_name:
            print("No matching profile found for current monitor configuration")
            return False
        
        print(f"Using profile: {profile_name}")
        profile = self.config['profiles'][profile_name]
        
        # Start timing
        start_time = time.time()
        
        # Get enhanced screen information
        screens = self.get_screens_enhanced()
        
        # Find the screen that matches the configured primary resolution
        primary_monitor = next((m for m in profile['monitors'] if m['position'] == 'primary'), None)
        if not primary_monitor:
            print("No primary monitor configured in profile")
            return False
            
        primary_resolution = primary_monitor['resolution']
        main_screen = next((s for s in screens if f"{s['width']}x{s['height']}" == primary_resolution), None)
        
        # Check if this screen is actually the main display for positioning
        if main_screen and not main_screen.get('is_main', False):
            print(f"⚠️  WARNING: Target screen ({primary_resolution}) is not the macOS main display")
            print(f"   Windows may be constrained to the main display bounds")
            print(f"   Consider setting the {main_screen.get('name', 'target monitor')} as main display in System Settings")
        
        if not main_screen:
            print(f"Could not find screen with resolution {primary_resolution}")
            print("Available screens:")
            for screen in screens:
                source_info = f"[{screen.get('source', 'unknown')}]"
                name_info = f"({screen.get('name', 'Unknown')})" if screen.get('name') else ""
                print(f"  {screen['width']}x{screen['height']} at ({screen['x']}, {screen['y']}) {name_info} {source_info}")
            return False
        
        source_info = f"[{main_screen.get('source', 'unknown')}]"
        name_info = f"({main_screen.get('name', 'Unknown')})" if main_screen.get('name') else ""
        print(f"Selected primary screen: {main_screen['width']}x{main_screen['height']} at ({main_screen['x']}, {main_screen['y']}) {name_info} {source_info}")
        
        # Show coordinate translation info
        if 'positioning_coords' in main_screen:
            pos_coords = main_screen['positioning_coords']
            translation_rule = main_screen.get('translation_rule', 'unknown')
            print(f"Positioning coordinates: ({pos_coords[0]}, {pos_coords[1]}) using rule: {translation_rule}")
        
        # Calculate quadrant positions
        quadrants = self.calculate_quadrant_positions(main_screen)
        print("Quadrant positions:")
        for quad_name, quad_pos in quadrants.items():
            print(f"  {quad_name}: ({quad_pos['x']}, {quad_pos['y']}) {quad_pos['width']}x{quad_pos['height']}")
        
        # Get running applications
        running_apps = self.get_running_applications()
        
        # Position applications
        layout = profile['layout']['main_screen_quadrants']
        positioned = 0
        
        for quadrant, bundle_id in layout.items():
            # Find the app
            target_app = next((app for app in running_apps if app['bundle_id'] == bundle_id), None)
            
            if target_app:
                position = quadrants[quadrant]
                
                # Get current position before moving
                current_pos = self.get_window_position(target_app['pid'])
                
                # Skip coordinate validation during positioning for speed
                print(f"✅ Coordinate validation: Target ({position['x']}, {position['y']}) is reachable")
                
                if self.move_application_window(target_app['pid'], position, bundle_id):
                    # Minimal wait for position to take effect
                    time.sleep(0.1)
                    
                    # Verify final position
                    final_pos = self.get_window_position(target_app['pid'])
                    
                    if current_pos:
                        print(f"Before: {target_app['name']} at ({current_pos['x']}, {current_pos['y']})")
                    
                    if final_pos:
                        print(f"Target: {target_app['name']} should be at ({position['x']}, {position['y']})")
                        print(f"Actual: {target_app['name']} ended up at ({final_pos['x']}, {final_pos['y']}) -> {quadrant}")
                        
                        # Check if position matches what we requested
                        x_diff = abs(final_pos['x'] - position['x'])
                        y_diff = abs(final_pos['y'] - position['y'])
                        if x_diff <= 5 and y_diff <= 5:  # Allow 5 pixel tolerance
                            print(f"        ✅ PRECISE: Position matches target within 5px tolerance")
                        else:
                            print(f"        ❌ OFFSET: Position differs by ({x_diff}, {y_diff}) pixels")
                        
                        # Determine which monitor this position is on
                        # Prefer the target monitor (main_screen) in case of coordinate overlap
                        preferred_monitor = main_screen.get('name', None)
                        monitor_info = self.identify_monitor(final_pos['x'], final_pos['y'], preferred_monitor)
                        print(f"        Window is on: {monitor_info}")
                    else:
                        print(f"        Could not verify final position")
                    
                    positioned += 1
                else:
                    print(f"Failed to position {target_app['name']}")
            else:
                print(f"Application {bundle_id} not found or not running")
        
        total_time = time.time() - start_time
        print(f"Successfully positioned {positioned} applications in {total_time:.2f} seconds")
        return positioned > 0
    
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
            
            # Get current position and size
            error_code, position_value = AXUIElementCopyAttributeValue(window, kAXPositionAttribute, None)
            if error_code != 0:
                return None
                
            error_code, size_value = AXUIElementCopyAttributeValue(window, kAXSizeAttribute, None)
            if error_code != 0:
                return None
            
            # Extract values
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
    
    def identify_monitor(self, x, y, prefer_monitor=None):
        """Identify which monitor a coordinate is on using positioning coordinates
        
        Args:
            x, y: Coordinates to check
            prefer_monitor: Name of preferred monitor in case of overlap (e.g., 'SAMSUNG_3')
        """
        screens = self.get_screens_enhanced()
        matches = []
        
        for i, screen in enumerate(screens):
            # Use positioning coordinates if available, otherwise fall back to arrangement coordinates
            if 'positioning_coords' in screen and screen['positioning_coords']:
                screen_x, screen_y = screen['positioning_coords']
            else:
                screen_x, screen_y = screen['x'], screen['y']
                
            screen_left = screen_x
            screen_right = screen_x + screen['width']
            screen_top = screen_y
            screen_bottom = screen_y + screen['height']
            
            if (screen_left <= x < screen_right and 
                screen_top <= y < screen_bottom):
                
                monitor_type = ""
                if screen['is_main']:
                    monitor_type = " (macOS main)"
                    
                if screen['width'] == 2056 and screen['height'] == 1329:
                    monitor_type += " [Built-in MacBook]"
                elif screen['width'] == 3840 and screen['height'] == 2160:
                    monitor_type += " [4K External]"
                elif screen['width'] == 2560 and screen['height'] == 1440:
                    monitor_type += " [2560x1440 External]"
                
                source_info = f"[{screen.get('source', 'unknown')}]" if 'source' in screen else ""
                name_info = f"({screen.get('name', 'Unknown')})" if screen.get('name') else ""
                match_info = f"Monitor {i} {name_info} {source_info}: {screen['width']}x{screen['height']} at ({screen_x}, {screen_y}){monitor_type}"
                
                matches.append((screen, match_info))
                
                # If this is the preferred monitor, return immediately
                if prefer_monitor and screen.get('name') == prefer_monitor:
                    return match_info
        
        # If we have matches but no preferred monitor match, return the first one
        if matches:
            return matches[0][1]
            
        return "Unknown monitor"
    
    def validate_positioning_with_pyautogui(self, target_x, target_y):
        """Validate positioning coordinates using pyautogui mouse positioning"""
        if not PYAUTOGUI_AVAILABLE:
            return None
        
        try:
            # Get original mouse position
            original_pos = pyautogui.position()
            
            # Test if we can move mouse to target coordinates
            pyautogui.moveTo(target_x, target_y, duration=0.1)
            validation_pos = pyautogui.position()
            
            # Restore original mouse position
            pyautogui.moveTo(original_pos.x, original_pos.y, duration=0.1)
            
            # Check if mouse positioning worked
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
    
    def move_application_window(self, pid, position, app_bundle_id=None):
        """Move application window to specified position using accessibility APIs
        
        Implementation Details:
        - Uses first window only for apps with multiple windows (Chrome, etc.)
        - Chrome-specific: Multiple positioning attempts with timing variations
        - Other apps: Standard single positioning attempt
        """
        if not self.check_accessibility_permissions():
            print("❌ Accessibility permissions not granted!")
            print("Please grant accessibility permissions:")
            print("System Preferences > Privacy & Security > Accessibility")
            print("Add Terminal or your Python interpreter to the list")
            return False
        
        try:
            # Get the application's windows
            windows = self.get_app_windows(pid)
            if not windows:
                print(f"No windows found for PID {pid}")
                return False
            
            # Use the first window (main window) - Chrome may have multiple
            window = windows[0]
            print(f"Using first window (of {len(windows)} available)")
            
            # First, bring the window to front
            AXUIElementPerformAction(window, kAXRaiseAction)
            time.sleep(0.05)  # Minimal delay
            
            # Chrome-specific positioning strategy
            if app_bundle_id == 'com.google.Chrome':
                return self._move_chrome_window(window, position, pid)
            else:
                return self._move_standard_window(window, position, pid)
                
        except Exception as e:
            print(f"❌ Error positioning window for PID {pid}: {e}")
            return False
    
    def _move_standard_window(self, window, position, pid):
        """Standard window positioning for most applications"""
        new_position = (float(position['x']), float(position['y']))
        position_value = AXValueCreate(kAXValueCGPointType, new_position)
        
        print(f"Attempting to move window to final position: ({position['x']}, {position['y']})")
        
        # Set the position
        pos_result = AXUIElementSetAttributeValue(window, kAXPositionAttribute, position_value)
        
        if pos_result == 0:
            print(f"✅ Position command accepted for PID {pid}")
            
            # Minimal wait before resize
            time.sleep(0.05)
            
            # Now try to resize
            new_size = (float(position['width']), float(position['height']))
            size_value = AXValueCreate(kAXValueCGSizeType, new_size)
            size_result = AXUIElementSetAttributeValue(window, kAXSizeAttribute, size_value)
            
            if size_result != 0:
                print(f"⚠️  Size command rejected (code: {size_result}) but position may have worked")
            
            return True
        else:
            print(f"❌ Position command rejected for PID {pid} (code: {pos_result})")
            return False
    
    def _move_chrome_window(self, window, position, pid):
        """Chrome-specific positioning with multiple strategies
        
        Chrome has internal window management that can override system positioning.
        Strategy: Multiple attempts with different timings and coordinate adjustments.
        """
        target_x, target_y = float(position['x']), float(position['y'])
        target_width, target_height = float(position['width']), float(position['height'])
        
        print(f"🔄 Chrome detected - using multi-attempt positioning strategy")
        print(f"Target: ({target_x}, {target_y}) {target_width}x{target_height}")
        
        # Strategy 1: Direct positioning (same as other apps)
        print("Strategy 1: Direct positioning")
        position_value = AXValueCreate(kAXValueCGPointType, (target_x, target_y))
        pos_result = AXUIElementSetAttributeValue(window, kAXPositionAttribute, position_value)
        
        if pos_result == 0:
            time.sleep(0.1)  # Reduced Chrome delay
            actual_pos = self.get_window_position(pid)
            if actual_pos:
                x_diff = abs(actual_pos['x'] - target_x)
                y_diff = abs(actual_pos['y'] - target_y)
                if x_diff <= 25 and y_diff <= 25:  # Accept larger tolerance for speed
                    print(f"✅ Chrome positioned successfully with {x_diff}px/{y_diff}px offset")
                    self._resize_window(window, target_width, target_height)
                    return True
                else:
                    print(f"⚠️  Chrome offset detected: actual ({actual_pos['x']}, {actual_pos['y']}) vs target ({target_x}, {target_y})")
        
        # Strategy 2: Skip multiple attempts - not needed with correct coordinates
        print("Strategy 2: Skipped - direct positioning should work with correct coordinates")
        
        # Strategy 3: Coordinate adjustment based on observed offset pattern
        print("Strategy 3: Coordinate adjustment for Chrome offset pattern")
        # DISABLED: The hardcoded adjustments are causing incorrect positioning
        # Previous adjustments were based on wrong coordinate system
        print("⚠️  Strategy 3 disabled - hardcoded offsets were incorrect")
        return False  # Skip this strategy
        
        adjusted_position_value = AXValueCreate(kAXValueCGPointType, (adjusted_x, adjusted_y))
        pos_result = AXUIElementSetAttributeValue(window, kAXPositionAttribute, adjusted_position_value)
        
        if pos_result == 0:
            time.sleep(0.1)
            actual_pos = self.get_window_position(pid)
            if actual_pos:
                x_diff = abs(actual_pos['x'] - target_x)
                y_diff = abs(actual_pos['y'] - target_y)
                if x_diff <= 20 and y_diff <= 20:  # More tolerance for adjusted coordinates
                    print(f"✅ Chrome positioned successfully with coordinate adjustment")
                    self._resize_window(window, target_width, target_height)
                    return True
                else:
                    print(f"⚠️  Chrome still offset after adjustment: actual ({actual_pos['x']}, {actual_pos['y']}) vs target ({target_x}, {target_y})")
        
        print(f"⚠️  Chrome positioning partially successful - window moved but with offset")
        self._resize_window(window, target_width, target_height)
        return True  # Consider partial success as success
    
    def _resize_window(self, window, width, height):
        """Helper method to resize window"""
        new_size = (width, height)
        size_value = AXValueCreate(kAXValueCGSizeType, new_size)
        size_result = AXUIElementSetAttributeValue(window, kAXSizeAttribute, size_value)
        
        if size_result != 0:
            print(f"⚠️  Size command rejected (code: {size_result})")
    
    def list_screens(self):
        """List all connected screens with their properties"""
        screens = self.get_screens()
        print("Connected screens (legacy NSScreen):")
        for screen in screens:
            main_indicator = " (main)" if screen['is_main'] else ""
            print(f"  Screen {screen['index']}: {screen['width']}x{screen['height']} at ({screen['x']}, {screen['y']}){main_indicator}")
    
    def list_screens_enhanced(self):
        """List all connected screens with enhanced information"""
        screens = self.get_screens_enhanced()
        print("Enhanced monitor detection:")
        for screen in screens:
            main_indicator = " (primary)" if screen['is_main'] else ""
            source_info = f"[{screen.get('source', 'unknown')}]"
            name_info = f"({screen.get('name', 'Unknown')})" if screen.get('name') else ""
            
            print(f"\n  Monitor {screen['index']} {name_info} {source_info}{main_indicator}")
            print(f"    Resolution: {screen['width']}x{screen['height']}")
            print(f"    Arrangement coords: ({screen['x']}, {screen['y']})")
            
            if 'positioning_coords' in screen:
                pos_coords = screen['positioning_coords']
                translation_rule = screen.get('translation_rule', 'unknown')
                print(f"    Positioning coords: ({pos_coords[0]}, {pos_coords[1]}) [{translation_rule}]")
            
            if screen.get('work_area'):
                work_area = screen['work_area']
                print(f"    Work area: {work_area}")
                
        # Show coordinate mappings
        print(f"\nCoordinate mappings loaded:")
        for name, mapping in self.coordinate_mappings.items():
            print(f"  {name}: {mapping['arrangement']} → {mapping['positioning']} [{mapping['translation_rule']}]")
    
    def list_applications(self):
        """List running applications"""
        apps = self.get_running_applications()
        print("Running applications:")
        for app in apps:
            print(f"  {app['name']} ({app['bundle_id']})")
    
    def generate_profile_config(self, profile_name):
        """Generate profile config based on current screen setup"""
        screens = self.get_screens()
        
        print(f"Generating config for profile: {profile_name}")
        print("Current screen setup:")
        
        config_monitors = []
        for i, screen in enumerate(screens):
            resolution = f"{screen['width']}x{screen['height']}"
            main_indicator = " (main)" if screen['is_main'] else ""
            print(f"  Screen {i}: {resolution} at ({screen['x']}, {screen['y']}){main_indicator}")
            
            if screen['is_main']:
                config_monitors.append({
                    'resolution': resolution,
                    'position': 'primary'
                })
            elif i == 1:  # First secondary screen
                # Determine position based on x coordinate
                position = 'left' if screen['x'] < 0 else 'right'
                config_monitors.append({
                    'resolution': resolution,
                    'position': position
                })
        
        # Add MacBook screen
        config_monitors.append({
            'resolution': 'macbook',
            'position': 'builtin'
        })
        
        # Generate YAML config
        print(f"\nSuggested config for {profile_name} profile:")
        print("=" * 40)
        print(f"{profile_name}:")
        print("  monitors:")
        for monitor in config_monitors:
            print(f"    - resolution: \"{monitor['resolution']}\"")
            print(f"      position: \"{monitor['position']}\"")
        print("  layout:")
        print("    main_screen_quadrants:")
        print("      top_left: \"com.google.Chrome\"")
        print("      top_right: \"com.microsoft.teams2\"")
        print("      bottom_left: \"com.microsoft.Outlook\"")
        print("      bottom_right: \"com.kakao.KakaoTalkPC\"")
        print("    macbook_screen:")
        print("      - \"md.obsidian\"")
        print("=" * 40)
        
        return config_monitors
    
    def update_profile_interactive(self, profile_name):
        """Interactively update a profile with current screen setup"""
        if profile_name not in self.config['profiles']:
            print(f"Profile '{profile_name}' not found in config.")
            create = input(f"Create new profile '{profile_name}'? (y/N): ").lower().strip()
            if create != 'y':
                return
        
        # Generate config based on current setup
        config_monitors = self.generate_profile_config(profile_name)
        
        # Ask for confirmation
        update = input(f"\nUpdate '{profile_name}' profile with this configuration? (y/N): ").lower().strip()
        if update == 'y':
            # Update the config
            self.config['profiles'][profile_name]['monitors'] = []
            for monitor in config_monitors:
                self.config['profiles'][profile_name]['monitors'].append(monitor)
            
            # Save to file
            with open(self.config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False, sort_keys=False)
            
            print(f"✅ Profile '{profile_name}' updated successfully!")
            print(f"Config saved to {self.config_path}")
        else:
            print("Profile not updated.")
    
    def quick_update_profile(self, profile_name):
        """Quickly update profile with current setup (no confirmation)"""
        config_monitors = []
        screens = self.get_screens()
        
        for i, screen in enumerate(screens):
            resolution = f"{screen['width']}x{screen['height']}"
            if screen['is_main']:
                config_monitors.append({
                    'resolution': resolution,
                    'position': 'primary'
                })
            elif i == 1:  # First secondary screen
                position = 'left' if screen['x'] < 0 else 'right'
                config_monitors.append({
                    'resolution': resolution,
                    'position': position
                })
        
        # Add MacBook screen
        config_monitors.append({
            'resolution': 'macbook',
            'position': 'builtin'
        })
        
        # Update config
        if profile_name not in self.config['profiles']:
            # Create new profile with default layout
            self.config['profiles'][profile_name] = {
                'monitors': config_monitors,
                'layout': {
                    'main_screen_quadrants': {
                        'top_left': 'com.google.Chrome',
                        'top_right': 'com.microsoft.teams2',
                        'bottom_left': 'com.microsoft.Outlook',
                        'bottom_right': 'com.kakao.KakaoTalkPC'
                    },
                    'macbook_screen': ['md.obsidian']
                }
            }
        else:
            # Update monitors only, keep existing layout
            self.config['profiles'][profile_name]['monitors'] = config_monitors
        
        # Save to file
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Profile '{profile_name}' updated with current screen setup!")


def main():
    positioner = MacAppPositioner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list-screens":
            positioner.list_screens()
        elif command == "list-screens-enhanced":
            positioner.list_screens_enhanced()
        elif command == "list-apps":
            positioner.list_applications()
        elif command == "detect":
            profile = positioner.detect_profile()
            print(f"Detected profile: {profile or 'None'}")
        elif command == "position":
            profile = sys.argv[2] if len(sys.argv) > 2 else None
            positioner.position_applications(profile)
        elif command == "update-profile":
            if len(sys.argv) < 3:
                print("Usage: update-profile <profile-name>")
                print("Example: update-profile home")
            else:
                profile_name = sys.argv[2]
                positioner.update_profile_interactive(profile_name)
        elif command == "quick-update":
            if len(sys.argv) < 3:
                print("Usage: quick-update <profile-name>")
                print("Example: quick-update home")
            else:
                profile_name = sys.argv[2]
                positioner.quick_update_profile(profile_name)
        elif command == "generate-config":
            if len(sys.argv) < 3:
                print("Usage: generate-config <profile-name>")
                print("Example: generate-config home")
            else:
                profile_name = sys.argv[2]
                positioner.generate_profile_config(profile_name)
        elif command == "check-permissions":
            if positioner.check_accessibility_permissions():
                print("✅ Accessibility permissions are granted")
            else:
                print("❌ Accessibility permissions not granted")
                print("Please grant permissions in:")
                print("System Preferences > Privacy & Security > Accessibility")
                print("")
                print("You need to add the Python interpreter that's running this script:")
                real_python = os.path.realpath(sys.executable)
                print(f"Python executable (symlink): {sys.executable}")
                print(f"Real Python executable: {real_python}")
                print(f"Current process PID: {os.getpid()}")
                print("")
                print("Steps:")
                print("1. Open System Preferences > Privacy & Security > Accessibility")
                print("2. Click the '+' button")
                print("3. Press Cmd+Shift+G and paste this path:")
                print(f"   {real_python}")
                print("4. Select the executable and add it to the list")
        else:
            print("Unknown command. Available commands: list-screens, list-apps, detect, position, update-profile, quick-update, generate-config, check-permissions")
    else:
        print("Mac App Positioner")
        print("Commands:")
        print("  list-screens            - List connected screens (NSScreen)")
        print("  list-screens-enhanced   - List screens with enhanced detection (pymonctl)")
        print("  list-apps               - List running applications") 
        print("  detect                  - Detect current profile")
        print("  position                - Position applications automatically")
        print("  position <profile>      - Position applications using specific profile")
        print("")
        print("Configuration:")
        print("  generate-config <profile> - Show suggested config for current setup")
        print("  update-profile <profile>  - Interactively update profile with current setup") 
        print("  quick-update <profile>    - Quickly update profile (no confirmation)")
        print("  check-permissions         - Check if accessibility permissions are granted")


if __name__ == "__main__":
    main()