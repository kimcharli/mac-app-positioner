# Architecture

This document explains the technical architecture and key design decisions of the Mac App Positioner.

## Core Components

### 1. Hybrid Monitor Detection

The script uses a hybrid approach to get the most reliable information about the monitor setup.

-   **Primary Tool: `pymonctl`**
    -   **Why:** It provides detailed information, including monitor **names** (e.g., "SAMSUNG_3"), which are crucial for reliably identifying specific monitors across sessions.
    -   **Limitation:** Like most tools, it provides "arrangement coordinates," which are not suitable for direct use in positioning.

-   **Fallback Tool: `NSScreen` (via PyObjC)**
    -   **Why:** As a native macOS framework, it is always available and provides a reliable baseline.
    -   **Limitation:** It does not provide monitor names, making it difficult to distinguish between two monitors with the same resolution.

-   **Validation Tool: `pyautogui`**
    -   **Why:** `pyautogui`'s mouse positioning functions use the same coordinate system as the window positioning APIs. This was instrumental in debugging and confirming that negative coordinates were the correct approach for monitors positioned above the primary display.

### 2. Adaptive Coordinate System

This is the most critical part of the architecture, designed to solve the macOS multi-monitor coordinate problem.

-   **Problem:** macOS uses two different coordinate systems: one for arranging displays and another for positioning windows. For monitors physically located above the primary display, the positioning API expects **negative Y coordinates**.

-   **Solution:** The `load_coordinate_mappings` function in `main.py` acts as a translation layer. It contains a dictionary that maps a monitor's name (from `pymonctl`) to its correct positioning coordinates.

    ```python
    # in main.py
    'SAMSUNG_3': {  # 4K monitor
        'arrangement': (0, 1329),      # What pymonctl reports
        'positioning': (0, -2160),     # What works when MacBook is main
        'positioning_when_main': (0, 0),  # What works when this monitor is main
        'translation_rule': 'adaptive_based_on_main_display'
    },
    ```

-   **How it works:** When positioning applications, the script looks up the main monitor by its name in this mapping and uses the correct `positioning` or `positioning_when_main` coordinates as the origin for all calculations. This ensures that applications are placed correctly, regardless of which monitor is set as primary.

### 3. Application Positioning

-   **Technology:** The script uses the `PyObjC` library to access the native macOS **Accessibility API** (`AXUIElement`).
-   **Process:**
    1.  It gets a reference to the target application by its process ID (PID).
    2.  It finds the application's main window.
    3.  It uses `AXUIElementSetAttributeValue` to set the window's position (`kAXPositionAttribute`) and size (`kAXSizeAttribute`).
-   **Chrome-Specific Strategy:** For Chrome, which can be resistant to positioning, the script uses a multi-attempt strategy with small delays to ensure the position is set correctly.
