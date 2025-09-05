# Development Decisions - Mac App Positioner

This document tracks key technical and design decisions to be made as the project evolves.

## Technical Stack Decision

**Options to consider:**
- **Swift/Objective-C**: Native macOS app with menu bar integration
  - Pros: Best macOS integration, performance, native APIs
  - Cons: macOS-only, requires Xcode knowledge
- **Python with PyObjC**: Cross-platform with macOS API access
  - Pros: Rapid prototyping, easy config handling, familiar language
  - Cons: Requires Python runtime, potential performance overhead
- **JavaScript/Electron**: Web technologies in desktop wrapper
  - Pros: Familiar web tech stack, cross-platform
  - Cons: Resource heavy, less native feel

**Current Status**: TBD - start small approach preferred

## User Interface Approach

**Options to consider:**
- **Menu bar app**: Simple controls in system menu bar
- **System preferences GUI**: Full configuration interface
- **Command-line tool**: Config file driven with terminal commands
- **Hybrid approach**: CLI + optional GUI

**Current Status**: TBD - minimal interface preferred for MVP

## Trigger Mechanism

**Options to consider:**
- **Polling approach**: Monitor display changes every few seconds
- **Event-driven**: Hook into macOS display change notifications (more complex)
- **Manual only**: User-initiated positioning (simplest start)
- **Hybrid**: Manual + automatic options

**Current Status**: TBD - start with manual, add automatic later

## Application Behavior

**Key decisions needed:**
- **Missing apps**: Launch automatically vs. position only running apps
- **Window sizing**: Maximize quadrants vs. specific pixel dimensions vs. user-defined
- **Multiple windows**: Which window to position if app has multiple open
- **Window states**: Handle minimized/fullscreen windows

**Current Status**: Position calculation implemented, actual window positioning pending - requires macOS accessibility APIs

## Implementation Phases

**Suggested progression:**
1. **Phase 1 (MVP)**: Manual positioning, basic config file, Python prototype
2. **Phase 2**: Automatic detection, monitor change hooks
3. **Phase 3**: GUI configuration interface
4. **Phase 4**: Advanced features (window sizing, multi-window handling)

**Current Status**: Starting small with growth potential

## Configuration Complexity

**Levels to consider:**
- **Basic**: Fixed quadrant positioning only
- **Intermediate**: Configurable sizing, multiple profiles
- **Advanced**: Complex rules, conditional positioning, app-specific behaviors

**Current Status**: Start basic, expand based on needs

## Development Philosophy

- Start small and iterate
- Prioritize working solution over perfect solution
- Add complexity gradually based on actual usage
- Focus on the core use case first (quadrant positioning)

## Next Steps

1. Choose initial technical stack
2. Create basic project structure
3. Implement manual positioning MVP
4. Test with actual monitor configurations
5. Iterate based on real-world usage