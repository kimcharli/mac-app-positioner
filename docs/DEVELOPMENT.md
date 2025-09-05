# Development Guide

This guide provides information for developers who want to contribute to or modify the Mac App Positioner.

## Development Setup

This project uses `uv` for Python environment and dependency management.

1.  **Install `uv`**

    Follow the official instructions to install `uv` on your system.

2.  **Install Dependencies**

    Once you have `uv` installed, you can install the project's dependencies:

    ```bash
    uv sync
    ```

    This will create a virtual environment in the `.venv` directory and install the packages listed in `pyproject.toml`.

3.  **Run the Script**

    You can run the script using `uv run`:

    ```bash
    uv run positioner <command>
    ```

    For example:
    ```bash
    uv run positioner position
    uv run positioner list-screens-enhanced
    ```

## Project Structure

-   **`mac_app_positioner/`**: The main application package.
    -   **`__main__.py`**: The main entry point for the command-line script.
    -   **`display.py`**: Manages monitor detection and coordinate systems.
    -   **`application.py`**: Manages application-related tasks.
    -   **`config.py`**: Handles loading the configuration file.
    -   **`profiles.py`**: Manages profile detection and application layout.
-   **`main.py`**: A simple script in the root directory that allows running the application directly with `python main.py`. While not strictly necessary after the creation of the `positioner` script, it is kept for developer convenience.
-   **`config.yaml`**: The user-facing configuration file for defining profiles and layouts.
-   **`pyproject.toml`**: Defines project metadata and dependencies for `uv`.
-   **`docs/`**: Contains all the project documentation.
-   **`tests/`**: Contains the test suite.

## Development Philosophy

-   **Start Small and Iterate:** The project started as a simple script and gradually grew in complexity as new requirements and challenges were discovered.
-   **Prioritize a Working Solution:** The focus is on creating a reliable tool that solves the core problem, even if it means hardcoding some solutions (like the coordinate mappings) that are discovered through empirical testing.
-   **Document Everything:** The challenges with macOS coordinate systems were significant. All findings are documented to prevent repeating the same debugging cycles.

## Debugging Multi-Monitor Issues

When developing or troubleshooting multi-monitor positioning issues, the following debugging approaches are useful:

### Monitor Detection Libraries

The application uses two main libraries for monitor detection:

- **`pymonctl`**: Provides detailed monitor information including names, work areas, and positioning coordinates
- **`pyautogui`**: Offers basic screen size detection and coordinate validation

### Useful Debugging Commands

```python
# Test pymonctl monitor detection
import pymonctl
monitors = pymonctl.getAllMonitors()
for i, monitor in enumerate(monitors):
    print(f"Monitor {i}: {monitor.name}")
    print(f"  Position: {monitor.position}")
    print(f"  Size: {monitor.size}")
    print(f"  Work Area: {monitor.workArea}")

# Test pyautogui screen detection  
import pyautogui
monitors = pyautogui.getAllMonitors()
for i, monitor in enumerate(monitors):
    left, top, width, height = monitor
    print(f"Monitor {i}: ({left}, {top}) {width}x{height}")
```

### Coordinate System Validation

When debugging positioning issues, test coordinates by calculating expected positions:

```python
# For a monitor with position (x, y) and size (width, height)
# Quadrant corners would be at:
top_left = (x, y)
top_right = (x + width//2, y)
bottom_left = (x, y + height//2)  
bottom_right = (x + width//2, y + height//2)
```

### Common Debugging Scenarios

- **Apps positioned on wrong monitor**: Usually indicates coordinate system mismatch between arrangement and positioning coordinates
- **Apps clustered in corners**: May indicate missing corner alignment or incorrect window size detection
- **Apps not moving at all**: Often due to accessibility permissions or incorrect PID detection

## Contributing

If you want to contribute, here are some areas that could be improved:

-   **GUI:** A simple GUI for managing profiles could make the tool more accessible to non-developers.
-   **Error Handling:** The script could have more robust error handling for cases where applications are not running or windows are not found.
