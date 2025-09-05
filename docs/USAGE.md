# Usage Guide

This guide provides detailed instructions on how to use and configure the Mac App Positioner.

## CLI Commands

You can run all commands using `uv run`.

-   **`position [profile]`**

    Positions applications based on your monitor setup. If you don't specify a profile, it will automatically detect the matching one.

    ```bash
    # Automatically detect profile and position apps
    uv run position

    # Position apps using a specific profile
    uv run position home

    # Show detailed debugging information during positioning
    uv run position --verbose
    ```

    **Options:**
    - `--verbose`: Show detailed debugging information including coordinate calculations, window sizes, and positioning details

-   **`detect`**

    Detects and displays the monitor profile that matches your current setup.

    ```bash
    uv run detect
    ```

-   **`list-screens-enhanced`**

    Lists all connected monitors with detailed information, including names and both arrangement and positioning coordinates. This is very useful for debugging.

    ```bash
    uv run list-screens-enhanced
    ```

-   **`list-apps`**

    Lists all currently running applications and their bundle identifiers.

    ```bash
    uv run list-apps
    ```

-   **`check-permissions`**

    Checks if the necessary Accessibility permissions have been granted.

    ```bash
    uv run check-permissions
    ```

-   **`quick-update <profile>`**

    Updates the specified profile in `config.yaml` with your current monitor setup. This is a quick way to configure the tool.

    ```bash
    uv run quick-update home
    ```

## Configuration (`config.yaml`)

The `config.yaml` file is the heart of the Mac App Positioner. It defines your monitor setups and how you want your applications arranged.

### Structure

```yaml
profiles:
  home:
    monitors:
      - resolution: "3840x2160"
        position: primary
      - resolution: "2560x1440"
        position: left
      - resolution: "2056x1329"
        position: builtin
    layout:
      primary:
        top_left: com.google.Chrome
        top_right: com.microsoft.teams2
        bottom_left: com.microsoft.Outlook
        bottom_right: com.kakao.KakaoTalkMac
      builtin:
        - md.obsidian
  office:
    # ... another profile for your office setup
```

### `profiles`

You can define multiple profiles, such as `home` and `office`.

### `monitors`

Under each profile, the `monitors` list describes the monitor setup for that profile. The script will use this list to detect which profile to use.

*   **`resolution`**: The resolution of the monitor (e.g., `3840x2160`).
*   **`position`**: A label to identify the monitor's role. Use `primary` for the main monitor where you want to position the apps.

### `layout`

The `layout` section defines where each application should go.

*   **`primary`**: This is for the monitor you marked as `primary`.
    *   `top_left`, `top_right`, `bottom_left`, `bottom_right`: Assign an application's **bundle identifier** to each quadrant.
*   **`builtin`**: You can define layouts for other screens as well.

### How to Find Bundle Identifiers

Use the `list-apps` command to find the bundle identifiers for your running applications:

```bash
uv run list-apps
```

## Application Positioning Behavior

### Corner Alignment

The Mac App Positioner intelligently aligns applications within their designated quadrants based on their actual window sizes:

- **Large applications** (like Chrome, Teams, Outlook): These typically fill most or all of their quadrant space
- **Small applications** (like KakaoTalk): These are aligned to the appropriate corner of their quadrant:
  - `top_left`: Application's top-left corner aligns to quadrant's top-left corner
  - `top_right`: Application's top-right corner aligns to quadrant's top-right corner  
  - `bottom_left`: Application's bottom-left corner aligns to quadrant's bottom-left corner
  - `bottom_right`: Application's bottom-right corner aligns to quadrant's bottom-right corner

### Window Size Preservation

Applications maintain their natural/preferred window sizes rather than being forced to fill entire quadrants. This ensures:
- Small utility apps like KakaoTalk remain compact and usable
- Large apps like browsers can use their optimal dimensions
- Better overall user experience with appropriately sized windows
