# Application Architecture

This document explains the technical architecture and key design decisions of the Mac App Positioner.

## Core Components

The application is designed with a modular architecture, separating concerns into distinct components:

-   **`mac_app_positioner/`**: The main application package.
    -   **`__main__.py`**: The main entry point for the command-line script.
    -   **`display.py`**: Manages monitor detection and coordinate systems.
    -   **`application.py`**: Manages application-related tasks.
    -   **`config.py`**: Handles loading the configuration file.
    -   **`profiles.py`**: Manages profile detection and application layout.

### 1. Hybrid Monitor Detection

The script uses a hybrid approach to get the most reliable information about the monitor setup.

-   **Primary Tool: `pymonctl`**
    -   **Why:** It provides detailed information, including monitor **names** (e.g., "SAMSUNG_3"), which are crucial for reliably identifying specific monitors across sessions.
-   **Fallback Tool: `NSScreen` (via PyObjC)**
    -   **Why:** As a native macOS framework, it is always available and provides a reliable baseline.

### 2. Adaptive Coordinate System

This is the most critical part of the architecture, designed to solve the macOS multi-monitor coordinate problem.

-   **Problem:** macOS uses two different coordinate systems: one for arranging displays (Cocoa/NSScreen with a bottom-left origin) and another for positioning windows (Quartz/CoreGraphics with a top-left origin). For monitors physically located above the primary display, the positioning API expects **negative Y coordinates**.

-   **Solution:** The `generate_dynamic_coordinate_mappings` function in `display.py` acts as a translation layer. It dynamically detects the monitors and converts the Cocoa coordinates to Quartz coordinates.

    ```python
    # Convert Cocoa coordinates to Quartz coordinates
    if is_main_display:
        quartz_x, quartz_y = 0, 0  # Origin in both systems
    else:
        quartz_x = cocoa_x  # X coordinate stays the same
        
        if cocoa_y > 0:
            # Monitor is "below" main in Cocoa = "above" main in Quartz
            quartz_y = -monitor_height  # Negative Y = above main
        elif cocoa_y < 0:  
            # Monitor is "above" main in Cocoa = "below" main in Quartz
            quartz_y = main_display_height  # Positive Y = below main
        else:
            # Same level as main display
            quartz_y = 0
    ```

### 3. Application Positioning

-   **Technology:** The script uses the `PyObjC` library to access the native macOS **Accessibility API** (`AXUIElement`).
-   **Process:**
    1.  It gets a reference to the target application by its process ID (PID).
    2.  It finds the application's main window.
    3.  It uses `AXUIElementSetAttributeValue` to set the window's position (`kAXPositionAttribute`).
-   **Application-Specific Strategies:** For applications like Chrome that can be resistant to positioning, the script can use specific strategies defined in the `config.yaml` file.

## Data Flow

1.  **Initialization:** The application loads the `config.yaml` file, detects the current monitor setup, and determines the active profile.
2.  **Detection:** It gets the list of running applications and their PIDs.
3.  **Positioning:** For each application in the active profile's layout, it calculates the target position based on the monitor's quadrant and the application's size, and then moves the application's window to the calculated position.
4.  **Validation:** The script can optionally validate the final position of the application.