"""Display management for Mac App Positioner."""

from Cocoa import NSScreen

# Enhanced monitor detection
try:
    import pymonctl
    PYMONCTL_AVAILABLE = True
except ImportError:
    PYMONCTL_AVAILABLE = False

class DisplayManager:
    def __init__(self, verbose=False):
        self.verbose = verbose
        if verbose:
            if PYMONCTL_AVAILABLE:
                print("✅ pymonctl available - using enhanced monitor detection")
            else:
                print("⚠️  pymonctl not available - using NSScreen fallback")
        self.coordinate_mappings = self.generate_dynamic_coordinate_mappings()

    def print_verbose(self, message):
        """Print message only if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def generate_dynamic_coordinate_mappings(self):
        """Generate coordinate mappings dynamically based on currently connected monitors"""
        try:
            screens = NSScreen.screens()
            mappings = {}
            main_screen = NSScreen.mainScreen()
            main_frame = main_screen.frame()
            main_height = int(main_frame.size.height)
            
            for i, screen in enumerate(screens):
                frame = screen.frame()
                cocoa_x, cocoa_y = int(frame.origin.x), int(frame.origin.y)
                width, height = int(frame.size.width), int(frame.size.height)
                is_main = screen == main_screen
                
                if is_main:
                    quartz_x, quartz_y = 0, 0
                else:
                    quartz_x = cocoa_x
                    if cocoa_y > 0:
                        quartz_y = -height
                    elif cocoa_y < 0:
                        quartz_y = main_height
                    else:
                        quartz_y = 0
                
                if is_main:
                    translation_rule = 'primary'
                elif quartz_y < 0:
                    translation_rule = 'above_primary'
                elif quartz_y > 0:
                    translation_rule = 'below_primary'
                elif quartz_x < 0:
                    translation_rule = 'left_of_primary'
                elif quartz_x > 0:
                    translation_rule = 'right_of_primary'
                else:
                    translation_rule = 'overlapping_primary'
                
                monitor_name = self.generate_monitor_name(width, height, quartz_x, quartz_y, i, is_main)
                
                mappings[monitor_name] = {
                    'arrangement': (cocoa_x, cocoa_y),
                    'positioning': (quartz_x, quartz_y),
                    'translation_rule': translation_rule,
                    'resolution': f'{width}x{height}',
                    'is_main': is_main,
                    'coordinate_source': 'cocoa_to_quartz_conversion'
                }
            
            return mappings
            
        except Exception as e:
            print(f"Error generating dynamic coordinate mappings: {e}")
            return {}

    def generate_monitor_name(self, width, height, x, y, index, is_main):
        """Generate a consistent monitor name based on characteristics"""
        if width == 2056 and height == 1329:
            return 'Built-in Retina Display_1'
        elif width == 3840 and height == 2160:
            return f'4K_Display_{index}'
        elif width == 2560 and height == 1440:
            return f'QHD_Display_{index}'
        elif width == 3440 and height == 1440:
            return f'UltraWide_Display_{index}'
        else:
            return f'Display_{width}x{height}_{index}'

    def get_screens_enhanced(self):
        """Enhanced monitor detection using hybrid approach"""
        if PYMONCTL_AVAILABLE:
            return self.get_screens_pymonctl()
        else:
            self.print_verbose("Falling back to NSScreen detection")
            return self.get_screens_nsscreen()

    def get_screens_pymonctl(self):
        """Get monitor information using pymonctl (primary method)"""
        try:
            monitors = pymonctl.getAllMonitors()
            screen_info = []
            
            for i, monitor in enumerate(monitors):
                pos = monitor.position
                size = monitor.size
                is_main = hasattr(monitor, 'isPrimary') and monitor.isPrimary
                
                monitor_name = self.generate_monitor_name(size.width, size.height, pos.x, pos.y, i, is_main)
                
                monitor_info = {
                    'index': i,
                    'name': monitor_name,
                    'original_name': monitor.name,
                    'width': size.width,
                    'height': size.height,
                    'x': pos.x,
                    'y': pos.y,
                    'is_main': is_main,
                    'work_area': getattr(monitor, 'workArea', None),
                    'source': 'pymonctl'
                }
                
                if monitor_name in self.coordinate_mappings:
                    mapping = self.coordinate_mappings[monitor_name]
                    monitor_info['positioning_coords'] = mapping['positioning']
                    monitor_info['translation_rule'] = mapping['translation_rule']
                else:
                    monitor_info['positioning_coords'] = (pos.x, pos.y)
                    monitor_info['translation_rule'] = 'dynamic_fallback'
                
                screen_info.append(monitor_info)
            
            return screen_info
            
        except Exception as e:
            print(f"Error with pymonctl detection: {e}")
            self.print_verbose("Falling back to NSScreen detection")
            return self.get_screens_nsscreen()

    def get_screens_nsscreen(self):
        """Fallback monitor detection using NSScreen"""
        screens = NSScreen.screens()
        screen_info = []
        
        for i, screen in enumerate(screens):
            frame = screen.frame()
            x, y = int(frame.origin.x), int(frame.origin.y)
            width, height = int(frame.size.width), int(frame.size.height)
            is_main = screen == NSScreen.mainScreen()
            
            monitor_name = self.generate_monitor_name(width, height, x, y, i, is_main)
            
            screen_info.append({
                'index': i,
                'name': monitor_name,
                'width': width,
                'height': height,
                'x': x,
                'y': y,
                'is_main': is_main,
                'positioning_coords': (x, y),
                'translation_rule': 'nsscreen_dynamic',
                'source': 'nsscreen'
            })
        
        return screen_info

    def get_screens(self):
        """Get information about connected screens (legacy method for compatibility)"""
        return self.get_screens_nsscreen()

    def identify_monitor(self, x, y, prefer_monitor=None):
        """Identify which monitor a coordinate is on using positioning coordinates"""
        screens = self.get_screens_enhanced()
        matches = []
        
        for i, screen in enumerate(screens):
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
                
                if prefer_monitor and screen.get('name') == prefer_monitor:
                    return match_info
        
        if matches:
            return matches[0][1]
            
        return "Unknown monitor"

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
                
        print(f"\nCoordinate mappings loaded:")
        for name, mapping in self.coordinate_mappings.items():
            print(f"  {name}: {mapping['arrangement']} → {mapping['positioning']} [{mapping['translation_rule']}]")
