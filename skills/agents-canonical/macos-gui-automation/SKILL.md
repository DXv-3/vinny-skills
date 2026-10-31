---
name: macos-gui-automation
description: "macOS GUI Automation Skill"
---

# macOS GUI Automation Skill

## Overview

Automate macOS GUI interactions using AppleScript, cliclick, and command-line tools. Use this skill when you need to:
- Interact with macOS applications (click buttons, fill forms, navigate menus)
- Submit bug reports to Apple via Feedback Assistant
- Automate repetitive GUI tasks
- Take screenshots and capture UI state

## Capabilities

1. **AppleScript Automation** - Control applications via AppleScript
2. **Click Automation** - Click buttons, menus, and UI elements
3. **Form Filling** - Fill in text fields and forms
4. **Screenshot Capture** - Capture screen state for debugging
5. **Apple Feedback Submission** - Submit bug reports to Apple

## Tools Required

### 1. cliclick (Install via Homebrew)
```bash
brew install cliclick
```

### 2. AppleScript (Built-in)
macOS includes AppleScript for GUI automation.

## Usage

### Click at Coordinates
```bash
cliclick c:500,300  # Click at x=500, y=300
cliclick c:500,300.  # Double-click
cliclick kd:cmd c:500,300 ku:cmd  # Cmd+Click
```

### Type Text
```bash
cliclick t:"Hello World"
```

### Press Keys
```bash
cliclick kp:return  # Press Return
cliclick kp:tab     # Press Tab
cliclick kd:cmd t:a ku:cmd  # Cmd+A
```

### AppleScript Example
```bash
osascript -e '
tell application "System Events"
    tell process "AppName"
        click button "Button Name" of window 1
    end tell
end tell
'
```

## Apple Feedback Submission

### Steps
1. Open Feedback Assistant: `open -a "Feedback Assistant"`
2. Wait for app to load
3. Click "New" button
4. Select platform (macOS)
5. Select framework (Foundation, AppKit, etc.)
6. Fill in title and description
7. Attach crash logs
8. Submit

### Feedback Content Template
```
Title: [Framework] - [Error Description]

Description:
macOS [version] - [Brief description]

The crash is in [framework name]:

Exception: [exception type and message]

Backtrace:
- [symbol1]
- [symbol2]
- [symbol3]

This is a [type of bug] where [brief explanation].

Environment: macOS [version], [hardware]

Reproducible: [Yes/No] - [steps to reproduce]

Attached: [crash log filename]
```

## Screenshot Capture

### Full Screen
```bash
screencapture -x /tmp/screenshot.png
```

### Specific Window
```bash
screencapture -l$(osascript -e 'tell app "Finder" to id of window 1') /tmp/window.png
```

### Selection
```bash
screencapture -i /tmp/selection.png
```

## Common Patterns

### Wait for Application
```bash
# Wait for app to be ready
for i in {1..10}; do
    if pgrep -f "AppName" > /dev/null; then
        echo "App is running"
        break
    fi
    sleep 1
done
```

### Wait for UI Element
```bash
# Wait for button to appear (max 10 seconds)
for i in {1..10}; do
    if osascript -e 'tell application "System Events" to tell process "AppName" to exists button "Button Name" of window 1' 2>/dev/null; then
        echo "Button found"
        break
    fi
    sleep 1
done
```

## Limitations

- AppleScript requires Accessibility permissions
- Some apps block automation
- Timing can be unreliable
- UI element detection varies by app

## Security Notes

- Only automate apps you own or have permission to control
- Don't automate sensitive operations (passwords, payments)
- Be careful with click coordinates - wrong clicks can cause issues
