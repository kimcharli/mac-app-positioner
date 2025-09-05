# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mac App Positioner - A utility for positioning and managing macOS applications on screen based on monitor configurations. Designed to handle different monitor setups at home and office.

## Project Goals

### Primary Use Case

Multi-monitor setup management for home and office environments with automatic or manual app positioning:

- **Home**: 4K monitor (main) + 2560x1440 left monitor + MacBook screen
- **Office**: 34-inch ultrawide monitor (main) + 2560x1440 side monitor + MacBook screen

### Target Application Layout

For the main (big) screen quadrant positioning:

- **Left Top**: Chrome app
- **Left Bottom**: Outlook app  
- **Right Top**: Teams app
- **Right Bottom**: KakaoTalk app

For the MacBook screen:

- **Obsidian app**: Stays on the built-in MacBook display

### Core Requirements

- Configuration file-driven app positioning
- Automatic trigger when monitor arrangement changes to configured setup
- Manual trigger capability
- Support for different monitor configurations (home vs office)

## Project Status

This is a newly initialized repository containing only:

- MIT License (Copyright 2025 Chang Hyun Kim)

## Development Setup

Since this is a new macOS utility project, likely development paths include:

### Swift/Objective-C (Native macOS App)

- Use Xcode project structure
- Main development files would be in Swift or Objective-C
- Build with `xcodebuild` or through Xcode IDE

### Python with macOS APIs

- Use PyObjC for Cocoa/AppKit integration
- Package with `setup.py` or `pyproject.toml`
- Run with `python -m mac_app_positioner`

### JavaScript/Electron

- Standard Node.js project with `package.json`
- Build with `npm run build` or `yarn build`
- Run with `npm start` or `yarn start`

## Architecture Considerations

For a macOS app positioner, key components typically include:

- Window detection and enumeration (using macOS APIs)
- Screen geometry management and monitor arrangement detection
- Application identification and control
- Position/size persistence via configuration
- Monitor change detection and event handling
- User interface for configuration management

## macOS-Specific Requirements

- Accessibility permissions will be required for window management
- May need Screen Recording permissions for certain window operations
- Bundle identifier management for app targeting
- Monitor arrangement detection using NSScreen APIs
- Consider sandboxing limitations if distributing via Mac App Store

## Additional Resources

See PROJECT_REQUIREMENTS.md for detailed functional requirements and configuration examples.