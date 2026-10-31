---
name: clipboardlux-macos-debugging
description: "ClipboardLUX macOS Debugging Skill"
---

# ClipboardLUX macOS Debugging Skill

## Overview

This skill documents the complete process of building, debugging, and stabilizing a native macOS SwiftUI app (ClipboardLUX) on macOS 27 beta, including workarounds for multiple Apple framework bugs.

## Key Topics Covered

1. **Native macOS App Development** - Converting from Next.js to Swift/SwiftUI
2. **macOS 27 Beta Bugs** - Multiple crashes in Apple's frameworks
3. **Workarounds Applied** - curl networking, telemetry disable, etc.
4. **UI Features** - Sidebar, detail pane, command deck, gestures
5. **Transforms Engine** - 60 text transforms across 7 categories
6. **AI Integration** - Ollama via curl subprocess
7. **GUI Automation** - AppleScript, cliclick for Feedback Assistant
8. **Apple Feedback Submission** - Bug report creation and submission

---

## 1. Native macOS App Development

### Project Structure
```
ClipboardLUX-native/
├── ClipboardLUX/
│   ├── ClipboardLUXApp.swift       (Main app entry)
│   ├── main.swift                  (Entry point with telemetry disable)
│   ├── disable_telemetry.c         (C constructor for telemetry)
│   ├── Models/
│   │   └── ClipboardModels.swift   (SwiftData models)
│   ├── Services/
│   │   ├── ClipboardMonitor.swift  (300ms polling clipboard watcher)
│   │   └── DatabaseService.swift   (SwiftData CRUD operations)
│   ├── AI/
│   │   └── OllamaService.swift     (curl-based Ollama client)
│   ├── Sync/
│   │   └── CloudKitSync.swift      (iCloud waiting area)
│   ├── Transforms/
│   │   └── TransformEngine.swift   (60 text transforms)
│   ├── Views/
│   │   ├── ContentView.swift       (Main UI with NavigationSplitView)
│   │   ├── SidebarView.swift       (Clickable sidebar items)
│   │   ├── DetailPaneView.swift    (AI actions and clip details)
│   │   ├── CommandDeck.swift       (Cmd+K search overlay)
│   │   ├── ClipCardView.swift      (Card UI with gestures)
│   │   └── SettingsView.swift      (Settings tabs)
│   └── Resources/
│       └── Info.plist
├── project.yml                     (XcodeGen config)
├── Package.swift                   (Stub for SPM)
└── README.md
```

### Key Architecture Decisions
- **SwiftData** for persistence (6 models matching original Prisma schema)
- **curl subprocess** instead of URLSession (macOS 27 CFNetwork bug)
- **C constructor** with `__attribute__((used, constructor(101)))` for telemetry disable
- **main.swift** with `@_silgen_name` to force linking of C code

---

## 2. macOS 27 Beta Bugs

### Bug 1: CFNetwork Crash
**Exception:** `-[__NSCFNumber length]: unrecognized selector sent to instance`
**Location:** `CFURLCreateStringByAddingPercentEscapes` → `initializeUserAgentString()`
**Cause:** CFNetwork's user agent initialization passes NSNumber where string expected
**Status:** Fixed by using curl instead of URLSession

### Bug 2: BiomeLibrary/ReportCrashService Crash
**Exception:** `-[__NSCFNumber length]: unrecognized selector sent to instance`
**Location:** `BMProcessCrash.writeTo:` → `PBDataWriterWriteStringField`
**Cause:** BiomeLibrary's crash report serialization type confusion
**Status:** Apple's bug, affects crash reporting system

### Bug 3: HID Telemetry Crash
**Exception:** `-[__NSCFNumber length]: unrecognized selector sent to instance`
**Location:** `__SPSubmitHIDTelemetry_block_invoke` → `CoreAnalytics::Client::sendEventAlways`
**Cause:** Apple's System Policy HID telemetry passes NSNumber where string expected
**Status:** Partially fixed with env vars, still crashes on interaction

### Bug 4: Metal/GPU Rendering Crash
**Exception:** `-[__NSCFNumber length]: unrecognized selector sent to instance`
**Location:** `getCStringForCFString` → `createContextTelemetryDataWithQueueLabelAndCallstack`
**Cause:** Metal GPU command buffer telemetry type confusion
**Status:** Fixed in macOS 27.0 (26A5388g) update

---

## 3. Workarounds Applied

### 3.1 curl-based Networking (OllamaService.swift)
**Problem:** URLSession crashes on macOS 27 due to CFNetwork bug
**Solution:** Use `Process()` + `/usr/bin/curl` for all HTTP requests

```swift
private func curlGet(_ urlString: String) throws -> Data {
    let proc = Process()
    proc.executableURL = URL(fileURLWithPath: "/usr/bin/curl")
    proc.arguments = ["-s", "-m", "10", urlString]
    let pipe = Pipe()
    proc.standardOutput = pipe
    proc.standardError = FileHandle.nullDevice
    try proc.run()
    proc.waitUntilExit()
    guard proc.terminationStatus == 0 else { throw OllamaError.requestFailed }
    return pipe.fileHandleForReading.readDataToEndOfFile()
}
```

### 3.2 Telemetry Disable (disable_telemetry.c)
**Problem:** macOS telemetry systems crash with type confusion bugs
**Solution:** C constructor that runs before main() to set env vars

```c
#include <stdlib.h>
#include <stdio.h>

void disableTelemetryForced(void);

__attribute__((used, constructor(101)))
static void disableTelemetryConstructor(void) {
    // CoreAnalytics / CFNetwork
    setenv("CA_DISABLE_ANALYTICS", "1", 1);
    setenv("APPLE_ENABLE_TELEMETRY", "0", 1);
    setenv("CFNETWORK_DISABLE_ANALYTICS", "1", 1);
    setenv("DISABLE_TELEMETRY", "1", 1);
    
    // HID telemetry (System Policy)
    setenv("SP_DISABLE_HID_TELEMETRY", "1", 1);
    setenv("DISABLE_HID_TELEMETRY", "1", 1);
    setenv("HID_TELEMETRY_DISABLED", "1", 1);
    setenv("SP_DISABLE_TELEMETRY", "1", 1);
    setenv("SYSTEM_POLICY_TELEMETRY_DISABLED", "1", 1);
    
    // Biome telemetry
    setenv("BIOME_DISABLE_TELEMETRY", "1", 1);
    setenv("DISABLE_BIOME", "1", 1);
    
    // General analytics
    setenv("DISABLE_ANALYTICS", "1", 1);
    setenv("NO_ANALYTICS", "1", 1);
    setenv("ANALYTICS_DISABLED", "1", 1);
}

void disableTelemetryForced(void) {
    disableTelemetryConstructor();
}
```

### 3.3 main.swift with @_silgen_name
**Problem:** C constructor not linked into binary
**Solution:** Swift entry point that calls forced linking function

```swift
import Foundation

@_silgen_name("disableTelemetryForced")
func disableTelemetryForced()

disableTelemetryForced()

ClipboardLUXApp.main()
```

### 3.4 MenuBarExtra Disable/Re-enable
**Problem:** MenuBarExtra crashes on macOS 27 beta
**Solution:** Comment out MenuBarExtra, re-enable after update

```swift
// TODO: Re-enable MenuBarExtra after macOS 27 beta fixes NSStatusBar diagnostics crash
// MenuBarExtra("ClipboardLUX", systemImage: "clipboard") { ... }
```

---

## 4. UI Features

### 4.1 Sidebar with Clickable Items
**Problem:** List selection with mismatched tag types
**Solution:** Use Button actions instead of List selection

```swift
struct SidebarItem: View {
    let title: String
    let icon: String
    let badge: Int?
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Label(title, systemImage: icon)
                Spacer()
                if let badge, badge > 0 {
                    Text("\(badge)")
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(.secondary.opacity(0.2), in: Capsule())
                }
            }
        }
        .buttonStyle(.plain)
        .listRowBackground(isSelected ? Color.accentColor.opacity(0.15) : Color.clear)
    }
}
```

### 4.2 Back Button
**Problem:** No way to return from detail view
**Solution:** Add toolbar button when clip is selected

```swift
.toolbar {
    if appState.selectedClip != nil {
        ToolbarItem(placement: .navigation) {
            Button(action: {
                appState.selectedClip = nil
            }) {
                HStack(spacing: 4) {
                    Image(systemName: "chevron.left")
                    Text("Back")
                }
            }
        }
    }
}
```

### 4.3 Double-Click Gestures
**Problem:** No quick way to flag/pin clips
**Solution:** Add double-click and command+double-click

```swift
.onTapGesture(count: 2) {
    // Double click to toggle favorite
    clip.isFavorite.toggle()
    Task { try? await DatabaseService.shared.updateClip(clip) }
}
.modifier(CommandDoubleClickModifier(clip: clip))

struct CommandDoubleClickModifier: ViewModifier {
    let clip: Clip
    
    func body(content: Content) -> some View {
        if #available(macOS 14.0, *) {
            content
                .gesture(
                    TapGesture(count: 2)
                        .modifiers(.command)
                        .onEnded {
                            // Command + double click to toggle pin
                            clip.isPinned.toggle()
                            Task { try? await DatabaseService.shared.updateClip(clip) }
                        }
                )
        } else {
            content
        }
    }
}
```

---

## 5. Transforms Engine

### 60 Transforms Across 7 Categories

| Category | Count | Examples |
|----------|-------|----------|
| Encoding | 11 | base64, hex, url, html, binary, utf8 |
| Unicode Styles | 10 | bold, italic, strikethrough, script, monospace, small caps |
| Ciphers & Fun | 9 | ROT13, ROT47, Atbash, Caesar, Vigenere, Beaufort |
| Case & Format | 17 | uppercase, lowercase, title, camel, snake, kebab, train |
| Steganography | 4 | ZWSP hide/reveal, tag hide, whitespace hide |
| AI Prompt Craft | 5 | ChatML, Llama2, YAML, Markdown, CSV to JSON |
| Utilities | 4 | word count, UUID, timestamp, slug |

### Key Helper Functions
- `applyUnicodeStyle(input:upperStart:lowerStart:)` - Maps ASCII to Unicode math symbols
- `caesar(_:shift:)` - Caesar cipher with shift parameter
- `vigenereEncode(_:key:)` / `vigenereDecode(_:key:)` - Vigenere cipher
- `beaufort(_:key:)` - Beaufort cipher
- `csvToJson(_:)` - CSV to JSON conversion

---

## 6. AI Integration

### OllamaService (curl-based)
**Problem:** URLSession crashes on macOS 27
**Solution:** Use curl subprocess for all HTTP requests

```swift
@MainActor
final class OllamaService: ObservableObject {
    static let shared = OllamaService()
    
    @Published var isAvailable = false
    @Published var currentModel: String = "qwen2.5:0.5b"
    
    private let baseURL = "http://localhost:11434"
    private let session: URLSession  // Not used, curl instead
    
    func checkStatus() async {
        do {
            let data = try curlGet("\(baseURL)/api/tags")
            let response = try JSONDecoder().decode(OllamaTagsResponse.self, from: data)
            isAvailable = true
            status = .available(models: response.models.map(\.name))
        } catch {
            isAvailable = false
            status = .unavailable(error: error.localizedDescription)
        }
    }
}
```

### AI Features Implemented
1. **Insights** - Analyze clip content
2. **Ask** - Q&A about clip content
3. **Filing** - Auto-categorize clips
4. **Synthesize** - Merge two clips
5. **Shelf Optimize** - Batch optimize clips
6. **Classify URL** - KEEP/MAYBE/TOSS classification

---

## 7. GUI Automation

### 7.1 cliclick (Homebrew)
```bash
brew install cliclick

# Click at coordinates
cliclick c:500,300

# Double-click
cliclick c:500,300.

# Type text
cliclick t:"Hello World"

# Press keys
cliclick kp:return
cliclick kp:tab
cliclick kd:cmd t:a ku:cmd  # Cmd+A
```

### 7.2 AppleScript Automation
```bash
# Click button
osascript -e '
tell application "System Events"
    tell process "AppName"
        click button "Button Name" of window 1
    end tell
end tell
'

# Type text
osascript -e 'tell application "System Events" to keystroke "Hello World"'

# Keyboard shortcut
osascript -e 'tell application "System Events" to keystroke "n" using command down'
```

### 7.3 Screenshot Capture
```bash
# Full screen
screencapture -x /tmp/screenshot.png

# Specific window
screencapture -l$(osascript -e 'tell app "Finder" to id of window 1') /tmp/window.png
```

---

## 8. Apple Feedback Submission

### Bug Report Template
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

### Submission Steps
1. Open Feedback Assistant: `open -a "Feedback Assistant"`
2. Create new feedback: `Cmd+N`
3. Select platform: macOS
4. Select framework: Foundation
5. Fill in title and description
6. Attach crash logs
7. Submit

### Crash Log Location
```bash
ls -lt ~/Library/Logs/DiagnosticReports/ | head -5
```

---

## 9. Common Pitfalls

### 9.1 SwiftData Macro Issues
**Problem:** SwiftData macros don't work from command line
**Solution:** Use Xcode's build system, not xcodebuild

### 9.2 SwiftUI Group Conflict
**Problem:** `Group` conflicts with SwiftUI.Group
**Solution:** Rename to `ClipGroup`

### 9.3 MenuBarExtra Crash
**Problem:** MenuBarExtra crashes on macOS 27 beta
**Solution:** Disable until Apple fixes

### 9.4 URLSession Crash
**Problem:** URLSession crashes on macOS 27 due to CFNetwork bug
**Solution:** Use curl subprocess

### 9.5 C Constructor Not Linked
**Problem:** `__attribute__((constructor))` not linked into binary
**Solution:** Use `__attribute__((used, constructor(101)))` and force linking via Swift

---

## 10. Testing Checklist

- [ ] App builds without errors
- [ ] App launches from Finder
- [ ] App runs for 60+ seconds without crashing
- [ ] Clipboard monitoring works (300ms polling)
- [ ] Type detection works (text, code, link, image, file, color)
- [ ] Sidebar items are clickable
- [ ] Back button works
- [ ] Double-click to flag works
- [ ] Command+double-click to pin works
- [ ] AI features work (insights, ask, filing, synthesize, shelf optimize, classify)
- [ ] 60 transforms work
- [ ] Settings window works
- [ ] MenuBarExtra works (when enabled)

---

## 11. macOS Version History

| Version | Build | Status |
|---------|-------|--------|
| macOS 27.0 | 26A5378n | Multiple crashes (CFNetwork, BiomeLibrary, HID telemetry, Metal) |
| macOS 27.0 | 26A5388g | Metal/GPU crash fixed, HID telemetry still crashes |

---

## 12. Files Created/Modified

### New Files
- `disable_telemetry.c` - C constructor for telemetry disable
- `main.swift` - Entry point with forced linking
- `SidebarView.swift` - Clickable sidebar items
- `DetailPaneView.swift` - AI actions and clip details
- `CommandDeck.swift` - Cmd+K search overlay

### Modified Files
- `ClipboardLUXApp.swift` - MenuBarExtra toggle, unadded `@main`
- `OllamaService.swift` - curl-based networking
- `ContentView.swift` - Back button, NavigationSplitView
- `ClipCardView.swift` - Double-click gestures

---

## 13. Lessons Learned

1. **macOS beta bugs are common** - Always have workarounds ready
2. **Telemetry systems can't be disabled easily** - Env vars don't affect all telemetry
3. **curl is a reliable fallback** - When URLSession fails, curl works
4. **C constructors need forced linking** - Use `__attribute__((used))` and Swift bridging
5. **GUI automation is fragile** - AppleScript/cliclick timing can be unreliable
6. **Apple Feedback requires manual submission** - No CLI tool available

---

## 14. Future Work

- [ ] Wait for Apple to fix HID telemetry bug
- [ ] Re-enable URLSession when CFNetwork is fixed
- [ ] Remove curl workaround when URLSession works
- [ ] Add more AI features
- [ ] Improve UI polish
- [ ] Add unit tests
- [ ] Prepare for App Store submission
