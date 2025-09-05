# Project Requirements - Mac App Positioner

## Problem Statement

Managing application windows across different monitor setups at home and office requires manual repositioning each time the monitor configuration changes.

## Solution Overview

Create a macOS utility that automatically positions applications based on predefined configurations when monitor arrangements change, with manual trigger capability.

## Primary Use Case

### Environment Context

- **Home Setup**: 4K monitor (main) + 2560x1440 left monitor + MacBook built-in screen
- **Office Setup**: 34-inch ultrawide monitor (main) + 2560x1440 side monitor + MacBook built-in screen  
- **Main Screen**: The primary large screen (4K at home, ultrawide at office) for application positioning

### Target Application Layout

Applications should be positioned in quadrants on the main (big) screen:

```
┌─────────────────┬─────────────────┐
│   Left Top      │   Right Top     │
│   Chrome        │   Teams         │
├─────────────────┼─────────────────┤
│   Left Bottom   │   Right Bottom  │
│   Outlook       │   KakaoTalk     │
└─────────────────┴─────────────────┘
```

The MacBook built-in screen should have:

```
┌─────────────────────────┐
│        MacBook          │
│       Obsidian          │
└─────────────────────────┘
```

### Specific Applications

- **Chrome**: Web browser for general browsing (main screen, top-left)
- **Outlook**: Email client for communication (main screen, bottom-left)
- **Teams**: Microsoft Teams for collaboration (main screen, top-right)
- **KakaoTalk**: Messaging application (main screen, bottom-right)
- **Obsidian**: Note-taking app (MacBook built-in screen)

## Core Requirements

### Functional Requirements

1. **Configuration Management**
   - Support multiple monitor configuration profiles (home, office)
   - JSON/YAML configuration file for easy editing
   - Application positioning rules per configuration
   - Screen quadrant positioning system

2. **Monitor Detection**
   - Automatically detect monitor arrangement changes
   - Identify when arrangement matches a configured profile
   - Support for different resolution combinations

3. **Application Control**
   - Find and identify target applications by bundle ID or process name
   - Position and resize application windows
   - Handle applications that may not be running (optional launch)

4. **Trigger Mechanisms**
   - **Automatic**: Activate when monitor configuration matches profile
   - **Manual**: User-initiated positioning via hotkey or menu
   - **Menu Bar**: System tray integration for easy access

### Technical Requirements

1. **macOS Integration**
   - Use native macOS APIs (NSScreen, Accessibility APIs)
   - Request necessary permissions (Accessibility, Screen Recording)
   - Support macOS 11+ (Big Sur and later)

2. **Performance**
   - Low system resource usage
   - Fast detection and positioning (< 2 seconds)
   - Minimal background monitoring

3. **User Experience**
   - Simple configuration file format
   - Clear permission request flow
   - Visual feedback during positioning
   - Error handling for missing applications

## Configuration File Structure

```yaml
profiles:
  home:
    monitors:
      - resolution: "3840x2160"  # 4K main monitor
        position: "primary"
      - resolution: "2560x1440"  # Left monitor
        position: "left"
      - resolution: "macbook"     # Built-in MacBook screen
        position: "builtin"
    layout:
      main_screen_quadrants:
        top_left: "com.google.Chrome"
        top_right: "com.microsoft.teams2" 
        bottom_left: "com.microsoft.Outlook"
        bottom_right: "com.kakao.KakaoTalkPC"
      macbook_screen:
        - "md.obsidian"
        
  office:
    monitors:
      - resolution: "3440x1440"  # 34-inch ultrawide main monitor
        position: "primary"
      - resolution: "2560x1440"  # Side monitor
        position: "left"
      - resolution: "macbook"     # Built-in MacBook screen
        position: "builtin"
    layout:
      main_screen_quadrants:
        top_left: "com.google.Chrome"
        top_right: "com.microsoft.teams2"
        bottom_left: "com.microsoft.Outlook" 
        bottom_right: "com.kakao.KakaoTalkPC"
      macbook_screen:
        - "md.obsidian"
```

## Success Criteria

1. **Accuracy**: 100% success rate for positioning when applications are running
2. **Speed**: Complete positioning within 2 seconds of trigger
3. **Reliability**: Handle edge cases (missing apps, permission issues)
4. **Usability**: Non-technical users can modify configuration
5. **Stability**: Run continuously without memory leaks or crashes

## Current Implementation Status

### ✅ Completed Components
- Monitor detection and configuration matching
- Application discovery and enumeration
- Quadrant position calculation
- Configuration file management
- Profile auto-detection
- Clean uv-based command interface

### 🚧 Pending Implementation
- **Window positioning**: The `move_application_window()` function currently only prints placeholder messages
- **Accessibility API integration**: Requires PyObjC accessibility framework or AppleScript
- **Permission handling**: Need to detect and request accessibility permissions
- **Error handling**: Graceful handling of permission denials and API failures

## Future Enhancements

- Support for more complex layouts (beyond quadrants)
- Window state saving/restoring (minimized, fullscreen)
- Integration with macOS Shortcuts app
- Multiple monitor positioning (not just main screen)
- Application-specific sizing preferences