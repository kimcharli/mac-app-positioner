#!/usr/bin/env python3
"""
Mac App Positioner - A utility for positioning macOS applications across monitors
"""

import sys
import os
from mac_app_positioner import MacAppPositioner

def main():
    """Main function for the Mac App Positioner CLI."""
    verbose = "--verbose" in sys.argv
    if verbose:
        sys.argv.remove("--verbose")

    positioner = MacAppPositioner(verbose=verbose)
    args = sys.argv[1:]

    if not args:
        print_help()
        sys.exit(0)

    command = args[0]

    if command == "list-screens":
        positioner.display_manager.list_screens()
    elif command == "list-screens-enhanced":
        positioner.display_manager.list_screens_enhanced()
    elif command == "list-apps":
        positioner.app_manager.list_applications()
    elif command == "detect":
        profile = positioner.profile_manager.detect_profile()
        print(f"Detected profile: {profile or 'None'}")
    elif command == "position":
        profile = args[1] if len(args) > 1 else None
        positioner.profile_manager.position_applications(profile)
    elif command == "update-profile":
        if len(args) < 2:
            print("Usage: update-profile <profile-name>")
        else:
            positioner.profile_manager.update_profile_interactive(args[1])
    elif command == "quick-update":
        if len(args) < 2:
            print("Usage: quick-update <profile-name>")
        else:
            positioner.profile_manager.quick_update_profile(args[1])
    elif command == "generate-config":
        if len(args) < 2:
            print("Usage: generate-config <profile-name>")
        else:
            positioner.profile_manager.generate_profile_config(args[1])
    elif command == "check-permissions":
        if positioner.app_manager.check_accessibility_permissions():
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
        print(f"Unknown command: {command}")
        print_help()

def print_help():
    """Prints the help message."""
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
    print("")
    print("Options:")
    print("  --verbose                 - Show detailed debugging information and positioning details")

if __name__ == "__main__":
    main()
