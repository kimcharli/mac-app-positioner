"""Profile management for Mac App Positioner."""

import time
import yaml

class ProfileManager:
    def __init__(self, config, display_manager, app_manager, verbose=False):
        self.config = config
        self.display_manager = display_manager
        self.app_manager = app_manager
        self.verbose = verbose

    def print_verbose(self, message):
        """Print message only if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def detect_profile(self):
        """Detect which profile matches current monitor configuration"""
        screens = self.display_manager.get_screens()
        current_resolutions = set(f"{s['width']}x{s['height']}" for s in screens)
        
        for profile_name, profile in self.config['profiles'].items():
            profile_resolutions = set()
            for monitor in profile['monitors']:
                if monitor['resolution'] != 'builtin':
                    profile_resolutions.add(monitor['resolution'])
            
            if profile_resolutions.issubset(current_resolutions):
                return profile_name
        
        return None

    def calculate_quadrant_positions(self, screen):
        """Calculate quadrant positions for a screen using positioning coordinates"""
        width = screen['width']
        height = screen['height']
        
        if 'positioning_coords' in screen and screen['positioning_coords']:
            x_offset, y_offset = screen['positioning_coords']
            coordinate_source = f"positioning ({screen.get('translation_rule', 'unknown')})"
        else:
            x_offset = screen['x']
            y_offset = screen['y']
            coordinate_source = "arrangement (fallback)"
        
        self.print_verbose(f"DEBUG: Using {coordinate_source} coordinates: x={x_offset}, y={y_offset}")
        self.print_verbose(f"DEBUG: Screen bounds: width={width}, height={height}")
        
        padding = 0
        usable_width = width - (2 * padding)
        usable_height = height - (2 * padding)
        
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
        
        self.print_verbose("DEBUG: Calculated positions:")
        for name, pos in positions.items():
            self.print_verbose(f"  {name}: ({pos['x']}, {pos['y']}) -> ends at ({pos['x'] + pos['width']}, {pos['y'] + pos['height']})")
            
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
        
        start_time = time.time()
        
        screens = self.display_manager.get_screens_enhanced()
        
        for monitor_layout in ['primary', 'builtin']:
            if monitor_layout in self.config['layout']:
                self._position_apps_on_monitor(profile, screens, monitor_layout)

        total_time = time.time() - start_time
        print(f"Finished positioning in {total_time:.2f} seconds")
        return True

    def _position_apps_on_monitor(self, profile, screens, monitor_position):
        monitor_config = next((m for m in profile['monitors'] if m['position'] == monitor_position), None)
        if not monitor_config:
            return

        monitor_resolution = monitor_config['resolution']
        
        if monitor_resolution == 'builtin':
            target_screen = next((s for s in screens if self.display_manager.generate_monitor_name(s['width'], s['height'], s['x'], s['y'], s['index'], s['is_main']).startswith('Built-in')), None)
        else:
            target_screen = next((s for s in screens if f"{s['width']}x{s['height']}" == monitor_resolution), None)

        if not target_screen:
            print(f"Could not find screen for position {monitor_position} with resolution {monitor_resolution}")
            return

        print(f"Positioning applications on {monitor_position} monitor ({target_screen['width']}x{target_screen['height']})")
        quadrants = self.calculate_quadrant_positions(target_screen)
        running_apps = self.app_manager.get_running_applications()
        layout = self.config['layout'][monitor_position]

        if isinstance(layout, dict):
            for quadrant, bundle_id in layout.items():
                self._position_app(bundle_id, running_apps, quadrants[quadrant], quadrant, target_screen)
        elif isinstance(layout, list):
            # For now, we don't have a specific layout for lists of apps, so we'll just print a message
            for bundle_id in layout:
                print(f"Skipping {bundle_id} on {monitor_position} monitor for now.")

    def _position_app(self, bundle_id, running_apps, position, quadrant, screen):
        target_app = next((app for app in running_apps if app['bundle_id'] == bundle_id), None)
        if not target_app:
            print(f"Application {bundle_id} not found or not running")
            return

        app_config = self.config.get('applications', {}).get(bundle_id, {})
        positioning_strategy = app_config.get('positioning_strategy')

        if self.app_manager.move_application_window(target_app['pid'], position, bundle_id, target_app['name'], quadrant, positioning_strategy):
            time.sleep(0.1)
            final_pos = self.app_manager.get_window_position(target_app['pid'])
            if final_pos:
                self.print_verbose(f"Actual: {target_app['name']} ended up at ({final_pos['x']}, {final_pos['y']}) -> {quadrant}")
                monitor_info = self.display_manager.identify_monitor(final_pos['x'], final_pos['y'], screen.get('name'))
                self.print_verbose(f"        Window is on: {monitor_info}")
        else:
            print(f"Failed to position {target_app['name']}")

    def generate_profile_config(self, profile_name):
        """Generate profile config based on current screen setup"""
        screens = self.display_manager.get_screens()
        
        print(f"Generating config for profile: {profile_name}")
        print("Current screen setup:")
        
        config_monitors = []
        for i, screen in enumerate(screens):
            resolution = f"{screen['width']}x{screen['height']}"
            main_indicator = " (main)" if screen['is_main'] else ""
            print(f"  Screen {i}: {resolution} at ({screen['x']}, {screen['y']}){main_indicator}")
            
            if self.display_manager.generate_monitor_name(screen['width'], screen['height'], screen['x'], screen['y'], i, screen['is_main']).startswith('Built-in'):
                config_monitors.append({
                    'resolution': 'builtin',
                    'position': 'builtin'
                })
            elif screen['is_main']:
                config_monitors.append({
                    'resolution': resolution,
                    'position': 'primary'
                })
            elif i == 1:
                position = 'left' if screen['x'] < 0 else 'right'
                config_monitors.append({
                    'resolution': resolution,
                    'position': position
                })
        
        print(f"\nSuggested config for {profile_name} profile:")
        print("=" * 40)
        print(f"{profile_name}:")
        print("  monitors:")
        for monitor in config_monitors:
            print(f"    - resolution: \"{monitor['resolution']}\"")
            print(f"      position: \"{monitor['position']}\"")
        print("\n# Layout is defined at top level and shared across profiles")
        print("=" * 40)
        
        return config_monitors

    def update_profile_interactive(self, profile_name, config_path="config.yaml"):
        """Interactively update a profile with current screen setup"""
        if profile_name not in self.config['profiles']:
            print(f"Profile '{profile_name}' not found in config.")
            create = input(f"Create new profile '{profile_name}'? (y/N): ").lower().strip()
            if create != 'y':
                return
        
        config_monitors = self.generate_profile_config(profile_name)
        
        update = input(f"\nUpdate '{profile_name}' profile with this configuration? (y/N): ").lower().strip()
        if update == 'y':
            self.config['profiles'][profile_name]['monitors'] = []
            for monitor in config_monitors:
                self.config['profiles'][profile_name]['monitors'].append(monitor)
            
            with open(config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False, sort_keys=False)
            
            print(f"✅ Profile '{profile_name}' updated successfully!")
            print(f"Config saved to {config_path}")
        else:
            print("Profile not updated.")

    def quick_update_profile(self, profile_name, config_path="config.yaml"):
        """Quickly update profile with current setup (no confirmation)"""
        config_monitors = []
        screens = self.display_manager.get_screens()
        
        for i, screen in enumerate(screens):
            resolution = f"{screen['width']}x{screen['height']}"
            if self.display_manager.generate_monitor_name(screen['width'], screen['height'], screen['x'], screen['y'], i, screen['is_main']).startswith('Built-in'):
                config_monitors.append({
                    'resolution': 'builtin',
                    'position': 'builtin'
                })
            elif screen['is_main']:
                config_monitors.append({
                    'resolution': resolution,
                    'position': 'primary'
                })
            elif i == 1:
                position = 'left' if screen['x'] < 0 else 'right'
                config_monitors.append({
                    'resolution': resolution,
                    'position': position
                })
        
        if profile_name not in self.config['profiles']:
            self.config['profiles'][profile_name] = {
                'monitors': config_monitors
            }
        else:
            self.config['profiles'][profile_name]['monitors'] = config_monitors
        
        with open(config_path, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Profile '{profile_name}' updated with current screen setup!")