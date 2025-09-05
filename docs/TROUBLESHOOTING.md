# Troubleshooting Guide

This guide provides solutions to common problems you might encounter with the Mac App Positioner.

## Problem: Applications are not positioned correctly or end up on the wrong monitor.

This is the most common issue and is almost always related to macOS's complex multi-monitor coordinate system.

### The Core Concept: Arrangement vs. Positioning Coordinates

macOS uses two different coordinate systems:

1.  **Arrangement Coordinates:** This is what you see in System Settings. The primary display is at `(0, 0)`, and other displays are arranged around it, often with positive coordinates.
2.  **Positioning Coordinates:** This is what the Accessibility API uses to place windows. For this system:
    *   Monitors **above** the primary display have **negative Y coordinates**.
    *   Monitors **left** of the primary display have **negative X coordinates**.

The script needs to use the **Positioning Coordinates** to work correctly.

### Troubleshooting Steps

1.  **Check Accessibility Permissions**

    First, make sure the script has the required permissions.

    ```bash
    uv run positioner check-permissions
    ```

    If permissions are not granted, follow the instructions to grant them in `System Settings > Privacy & Security > Accessibility`.

2.  **Inspect Your Monitor Setup**

    Use the `list-screens-enhanced` command to see how the script detects your monitors.

    ```bash
    uv run positioner list-screens-enhanced
    ```

    Look for the **Positioning coords** for your main monitor. If your main external monitor is physically located **above** your MacBook, you should see negative Y values for its positioning coordinates.

    **Example Output:**
    ```
    Monitor 2 (SAMSUNG_3) [pymonctl] (primary)
        Resolution: 3840x2160
        Arrangement coords: (0, 1329)
        Positioning coords: (0, -2160) [adaptive_based_on_main_display_as_main]
    ```
    In this example, the arrangement coordinates `(0, 1329)` are misleading. The correct positioning coordinates `(0, -2160)` are being used, which is why it works.

3.  **Verify the Dynamic Coordinate Conversion**

    The script automatically converts arrangement coordinates to positioning coordinates. If the positioning coordinates in the output of `list-screens-enhanced` do not seem to match the physical layout of your monitors, there might be an issue with the conversion logic. Refer to the `ARCHITECTURE.md` document for a detailed explanation of the coordinate system conversion.

## Problem: A specific application (like Chrome) is slightly off-center.

-   **Cause:** Some applications, especially Chrome, have their own window management logic that can interfere with precise positioning. The script includes a special multi-attempt strategy for Chrome.
-   **Solution:** The script is designed to tolerate small offsets (e.g., 25 pixels) for applications like Chrome, as this is often due to the window's title bar. As long as the application is in the correct quadrant on the correct monitor, this is usually acceptable.

## Problem: The wrong profile (`home` or `office`) is being detected.

-   **Cause:** The resolutions in your `config.yaml` for the profile do not match the resolutions of your connected monitors.
-   **Solution:**
    1.  Run `uv run positioner list-screens-enhanced` to see the exact resolutions of your monitors.
    2.  Compare this with the resolutions in your `config.yaml` under the profile you expect to be detected.
    3.  For a quick fix, run `uv run positioner quick-update <profile-name>` to automatically update the profile with your current monitor setup.