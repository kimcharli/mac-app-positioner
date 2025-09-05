# AI Agents Guide for Mac App Positioner

This document provides guidelines for AI agents working with the Mac App Positioner codebase.

## Core Principles

-   **Dynamic Over Static:** Always favor dynamic detection of the monitor setup over hardcoded values. See the [Architecture](ARCHITECTURE.md) document for details.
-   **Terminology Consistency:** Refer to the [Terminology](TERMINOLOGY.md) document for precise definitions of terms like "Primary Monitor" and "Main Display."
-   **Coordinate System Awareness:** The application correctly handles the different coordinate systems in macOS. See the [Architecture](ARCHITECTURE.md) document for a detailed explanation.

## Code Architecture

The application is structured as a Python package with a modular design. For a detailed explanation of the architecture, see the [Architecture](ARCHITECTURE.md) document.

## Development

For instructions on how to set up the development environment, run the tests, and contribute to the project, see the [Development Guide](DEVELOPMENT.md).

## Usage

For detailed instructions on how to use the command-line interface and configure the application, see the [Usage Guide](USAGE.md).

## Troubleshooting

For solutions to common problems, see the [Troubleshooting Guide](TROUBLESHOOTING.md).
