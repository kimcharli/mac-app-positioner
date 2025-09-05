# Mac App Positioner

A Python utility to automatically position macOS applications across multiple monitors based on predefined configurations.

## Quick Start

1.  **Install dependencies:**
    ```bash
    uv sync
    ```

2.  **Run the positioner:**
    ```bash
    uv run position
    ```
    This will detect your current monitor setup and position applications based on the matching profile in `config.yaml`.

## Documentation

For more detailed information, please refer to the following documents:

*   **[Usage Guide](./docs/USAGE.md):** Detailed instructions on CLI commands and configuration.
*   **[Troubleshooting Guide](./docs/TROUBLESHOOTING.md):** Solutions for common issues, especially related to monitor coordinates.
*   **[Architecture](./docs/ARCHITECTURE.md):** An explanation of the technical design and decisions.
*   **[Development Guide](./docs/DEVELOPMENT.md):** Information for contributors.

## Permissions

This utility requires **Accessibility** permissions to control application windows.

-   You can check your permissions with `uv run check-permissions`.
-   If not granted, you will need to add your terminal application or Python interpreter in `System Settings > Privacy & Security > Accessibility`.
