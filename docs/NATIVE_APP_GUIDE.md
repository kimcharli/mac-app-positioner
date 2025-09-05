# Native macOS Application Guide

This document provides a high-level guide on how to create a native macOS application for the Mac App Positioner using Swift and SwiftUI.

## 1. Choosing the Right Technology

For a new macOS application, the modern and recommended approach is to use:

*   **Swift:** Apple's powerful and intuitive programming language. It's safe, fast, and the standard for modern Apple development.
*   **SwiftUI:** A declarative UI framework for building user interfaces. It allows you to create a clean and responsive UI with less code than the older AppKit framework.
*   **AppKit:** The underlying framework for building macOS applications. While SwiftUI is used for the UI, you'll still need to use AppKit for some of the lower-level application logic, especially for interacting with the Accessibility API.

## 2. Project Setup in Xcode

You'll use Xcode, Apple's integrated development environment (IDE), to build the application.

1.  **Create a New Project:** Open Xcode and create a new project. Select the "macOS" tab and choose the "App" template.
2.  **Choose Your Options:**
    *   **Product Name:** `MacAppPositioner`
    *   **Interface:** `SwiftUI`
    *   **Language:** `Swift`
    *   **Storage:** `None` (you can use `UserDefaults` or a custom file for configuration)
3.  **Project Structure:** Xcode will generate a project with a basic structure, including an `ContentView.swift` file for your UI and an `MacAppPositionerApp.swift` file for your application's entry point.

## 3. Translating the Core Logic to Swift

The core logic of your Python script can be translated to Swift using Apple's native frameworks.

### Monitor Detection

You'll use the `CoreGraphics` framework to get information about the connected displays.

```swift
import CoreGraphics

func getScreenInfo() -> [NSScreen] {
    return NSScreen.screens
}
```

You can then iterate through the `NSScreen` array to get the frame, resolution, and other properties of each screen, just like you did with `PyObjC`.

### Application Positioning

You'll use the `Accessibility` framework to control the position of application windows. This is the same framework you used in Python, but you'll be using it directly from Swift.

```swift
import AppKit

func moveApplicationWindow(pid: pid_t, to position: CGPoint) {
    let app = AXUIElementCreateApplication(pid)

    var window: AnyObject?
    AXUIElementCopyAttributeValue(app, kAXMainWindowAttribute as CFString, &window)

    if let window = window {
        var positionValue = position
        let positionRef = AXValueCreate(AXValueType.cgPoint, &positionValue)!
        AXUIElementSetAttributeValue(window as! AXUIElement, kAXPositionAttribute as CFString, positionRef)
    }
}
```

**Note:** You'll need to handle accessibility permissions in your native app as well. You can prompt the user to grant permissions from within the app.

### Configuration Management

You can use `UserDefaults` for simple key-value storage or a custom file format (like JSON or a property list) for more complex configurations.

```swift
// Using UserDefaults
let defaults = UserDefaults.standard
deaults.set("com.google.Chrome", forKey: "topLeftApp")

// Reading from UserDefaults
let topLeftApp = defaults.string(forKey: "topLeftApp")
```

## 4. Building the User Interface with SwiftUI

You can create a simple and elegant user interface with SwiftUI.

```swift
import SwiftUI

struct ContentView: View {
    @State private var selectedProfile = "Home"
    let profiles = ["Home", "Office"]

    var body: some View {
        VStack {
            Picker("Profile", selection: $selectedProfile) {
                ForEach(profiles, id: \.self) {
                    Text($0)
                }
            }
            .pickerStyle(SegmentedPickerStyle())
            .padding()

            Button("Position Apps") {
                // Call your application positioning logic here
            }
            .padding()
        }
    }
}
```

This would create a simple UI with a profile selector and a button to trigger the positioning.

## 5. Distribution

Once your application is ready, you have a few options for distributing it:

*   **Mac App Store:** This is the easiest way for users to discover and install your application. You'll need to enroll in the Apple Developer Program to submit your app to the App Store.
*   **Direct Distribution:** You can distribute your application directly to users by providing them with a `.app` file. You'll need to notarize your application with Apple to ensure that it can be run on other Macs without security warnings.
