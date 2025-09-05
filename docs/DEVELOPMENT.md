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
    uv run main.py <command>
    # or simply
    uv run <command>
    ```

    For example:
    ```bash
    uv run position
    uv run list-screens-enhanced
    ```

## Project Structure

-   **`main.py`**: The main entry point of the application. It contains all the logic for monitor detection, application positioning, and the CLI.
-   **`config.yaml`**: The user-facing configuration file for defining profiles and layouts.
-   **`pyproject.toml`**: Defines project metadata and dependencies for `uv`.
-   **`docs/`**: Contains all the project documentation.

## Development Philosophy

-   **Start Small and Iterate:** The project started as a simple script and gradually grew in complexity as new requirements and challenges were discovered.
-   **Prioritize a Working Solution:** The focus is on creating a reliable tool that solves the core problem, even if it means hardcoding some solutions (like the coordinate mappings) that are discovered through empirical testing.
-   **Document Everything:** The challenges with macOS coordinate systems were significant. All findings are documented to prevent repeating the same debugging cycles.

## Contributing

If you want to contribute, here are some areas that could be improved:

-   **Automatic Coordinate Detection:** The `coordinate_mappings` in `main.py` are currently hardcoded. A more advanced version of this tool could attempt to automatically discover the correct positioning coordinates.
-   **GUI:** A simple GUI for managing profiles could make the tool more accessible to non-developers.
-   **Error Handling:** The script could have more robust error handling for cases where applications are not running or windows are not found.
