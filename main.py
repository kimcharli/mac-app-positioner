#!/usr/bin/env python3
"""
Mac App Positioner - A utility for positioning macOS applications across monitors
"""

import yaml
import sys
import os
import time
from Cocoa import NSScreen, NSApplication, NSWorkspace
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
    
    def get_screens(self):
        """Get information about connected screens"""
        screens = NSScreen.screens()
        screen_info = []
        
        for i, screen in enumerate(screens):
            frame = screen.frame()
            screen_info.append({
                'index': i,
                'width': int(frame.size.width),
                'height': int(frame.size.height),
                'x': int(frame.origin.x),
                'y': int(frame.origin.y),
                'is_main': screen == NSScreen.mainScreen()
            })
        
        return screen_info
    
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
        """Calculate quadrant positions for a screen"""
        width = screen['width']
        height = screen['height']
        x_offset = screen['x']
        y_offset = screen['y']
        
        print(f"DEBUG: Screen bounds: x={x_offset}, y={y_offset}, width={width}, height={height}")
        
        # Use pure math-based positioning regardless of main display
        # The coordinate system should work with any monitor as target
        
        padding = 100
        usable_width = width - (2 * padding)
        usable_height = height - (2 * padding)
        
        # Calculate quadrant dimensions
        quad_width = usable_width // 2
        quad_height = usable_height // 2
        
        # Use NSScreen coordinates directly - let's trust what the system reports
        print(f"DEBUG: Using NSScreen coordinates directly: x={x_offset}, y={y_offset}")
        
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
        
        # Get screen information
        screens = self.get_screens()
        
        # Find the screen that matches the configured primary resolution
        primary_monitor = next((m for m in profile['monitors'] if m['position'] == 'primary'), None)
        if not primary_monitor:
            print("No primary monitor configured in profile")
            return False
            
        primary_resolution = primary_monitor['resolution']
        main_screen = next((s for s in screens if f"{s['width']}x{s['height']}" == primary_resolution), None)
        
        if not main_screen:
            print(f"Could not find screen with resolution {primary_resolution}")
            print("Available screens:")
            for screen in screens:
                print(f"  {screen['width']}x{screen['height']} at ({screen['x']}, {screen['y']})")
            return False
        
        print(f"Selected primary screen: {main_screen['width']}x{main_screen['height']} at ({main_screen['x']}, {main_screen['y']})")
        
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
                
                if self.move_application_window(target_app['pid'], position):
                    # Wait a moment for the position to take effect
                    time.sleep(0.5)
                    
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
                        monitor_info = self.identify_monitor(final_pos['x'], final_pos['y'])
                        print(f"        Window is on: {monitor_info}")
                    else:
                        print(f"        Could not verify final position")
                    
                    positioned += 1
                else:
                    print(f"Failed to position {target_app['name']}")
            else:
                print(f"Application {bundle_id} not found or not running")
        
        print(f"Successfully positioned {positioned} applications")
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
    
    def identify_monitor(self, x, y):
        """Identify which monitor a coordinate is on"""
        screens = self.get_screens()
        
        for i, screen in enumerate(screens):
            screen_left = screen['x']
            screen_right = screen['x'] + screen['width']
            screen_top = screen['y']
            screen_bottom = screen['y'] + screen['height']
            
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
                
                return f"Screen {i}: {screen['width']}x{screen['height']} at ({screen['x']}, {screen['y']}){monitor_type}"
        
        return "Unknown monitor"
    
    def move_application_window(self, pid, position):
        """Move application window to specified position using accessibility APIs"""
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
            
            # Use the first window (main window)
            window = windows[0]
            
            # First, bring the window to front
            AXUIElementPerformAction(window, kAXRaiseAction)
            time.sleep(0.1)
            
            # Direct positioning - let's trust the math and coordinates
            new_position = (float(position['x']), float(position['y']))
            position_value = AXValueCreate(kAXValueCGPointType, new_position)
            
            print(f"Attempting to move window to final position: ({position['x']}, {position['y']})")
            
            # TEST: Check if we're trying to use negative coordinates (which might not work)
            if position['y'] < 0:
                print(f"WARNING: Attempting to use negative Y coordinate ({position['y']}) - this may not work")
            
            # Set the final position
            pos_result = AXUIElementSetAttributeValue(window, kAXPositionAttribute, position_value)
            
            if pos_result == 0:
                print(f"✅ Position command accepted for PID {pid}")
                
                # Wait a moment then try to resize
                time.sleep(0.2)
                
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
                
        except Exception as e:
            print(f"❌ Error positioning window for PID {pid}: {e}")
            return False
    
    def list_screens(self):
        """List all connected screens with their properties"""
        screens = self.get_screens()
        print("Connected screens:")
        for screen in screens:
            main_indicator = " (main)" if screen['is_main'] else ""
            print(f"  Screen {screen['index']}: {screen['width']}x{screen['height']} at ({screen['x']}, {screen['y']}){main_indicator}")
    
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
        print("  list-screens     - List connected screens")
        print("  list-apps        - List running applications") 
        print("  detect           - Detect current profile")
        print("  position         - Position applications automatically")
        print("  position <profile> - Position applications using specific profile")
        print("")
        print("Configuration:")
        print("  generate-config <profile> - Show suggested config for current setup")
        print("  update-profile <profile>  - Interactively update profile with current setup") 
        print("  quick-update <profile>    - Quickly update profile (no confirmation)")
        print("  check-permissions         - Check if accessibility permissions are granted")


if __name__ == "__main__":
    main()