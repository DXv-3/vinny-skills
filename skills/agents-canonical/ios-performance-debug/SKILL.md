---
name: ios-performance-debug
description: "Skill: ios-performance-debug"
---

# Skill: ios-performance-debug

Unified iOS performance and debugging skill. Use this instead of juggling swiftui-performance, debugging-instruments, ios-memgraph-analysis, ios-ettrace-performance, xcode-build-benchmark, xcode-build-fixer, xcode-build-orchestrator, xcode-compilation-analyzer, xcode-project-analyzer, spm-build-analysis, ios-metrickit, and metricoolkit separately.

## When to Use

- App feels slow or janky
- Memory usage keeps growing
- Xcode builds are taking too long
- App crashes or hangs in production
- Need to profile launch time or runtime performance
- Swift compile times are high
- SPM packages slowing down builds
- Diagnosing production issues via MetricKit

---

## Diagnostic Flowchart

```
Problem: App is slow
├── UI feels janky?
│   ├── YES → SwiftUI Performance (body updates, list churn)
│   └── NO → continue
├── Memory growing over time?
│   ├── YES → Memory Graph Analysis (leaks, heap growth)
│   └── NO → continue
├── App hangs?
│   ├── YES → Instruments: Time Profiler + Hangs
│   └── NO → continue
├── Launch is slow?
│   ├── YES → Launch Profiling (ETTrace + Instruments)
│   └── NO → continue
├── Build is slow?
│   ├── YES → Build Performance (xcode-build-*)
│   └── NO → continue
└── Production crashes?
    └── YES → MetricKit Triage
```

---

## 1. SwiftUI Performance

### Diagnose Slow Views

Use Instruments with the "SwiftUI" template:

1. Open Instruments → SwiftUI template
2. Record while navigating the slow path
3. Look for:
   - **Body calls** — excessive view body invocations
   - **Layout passes** — repeated layout calculations
   - **Identity churn** — list items losing identity

### Fix Excessive Body Updates

```swift
// BAD: Entire view re-renders
struct UserView: View {
    let user: User
    
    var body: some View {
        VStack {
            Text(user.name)
            Text(user.email)
            AsyncImage(url: user.avatarURL)
        }
    }
}

// GOOD: Split into smaller views
struct UserView: View {
    let user: User
    
    var body: some View {
        VStack {
            UserNameView(name: user.name)
            UserEmailView(email: user.email)
            UserAvatarView(url: user.avatarURL)
        }
    }
}

struct UserNameView: View {
    let name: String
    var body: some View { Text(name) }
}

struct UserEmailView: View {
    let email: String
    var body: some View { Text(email) }
}

struct UserAvatarView: View {
    let url: URL
    var body: some View { AsyncImage(url: url) }
}
```

### Fix List Performance

```swift
// BAD: No identity, no lazy loading
List(items) { item in
    HeavyRow(item: item)
}

// GOOD: LazyVStack + stable IDs
ScrollView {
    LazyVStack {
        ForEach(items, id: \.id) { item in
            HeavyRow(item: item)
        }
    }
}

// BETTER: If items don't change, use EquatableView
struct HeavyRow: View, Equatable {
    let item: Item
    static func == (lhs: HeavyRow, rhs: HeavyRow) -> Bool {
        lhs.item.id == rhs.item.id && lhs.item.name == rhs.item.name
    }
}
```

### Avoid Unnecessary State

```swift
// BAD: @State triggers full body update
@State private var counter = 0
@State private var items: [Item] = []
@State private var selectedTab = 0

// GOOD: Separate concerns
@State private var counter = 0      // This is fine alone
@State private var items: [Item] = []  // Separate view

// BETTER: Use @Observable for fine-grained updates
@Observable
class CounterViewModel {
    var count = 0
}

// Usage
struct CounterView: View {
    @State private var viewModel = CounterViewModel()
    var body: some View {
        Text("\(viewModel.count)")  // Only this Text updates
        Button("+") { viewModel.count += 1 }
    }
}
```

---

## 2. Memory Analysis

### Capture .memgraph

```bash
# Via Xcode
# Debug Navigator → Memory → Capture Memory Graph

# Via CLI
xcrun devicectl device info profile --device <device-uuid>

# Simulator
xcrun simctl io booted snapshot memgraph /tmp/snapshot.memgraph
```

### Analyze with leaks CLI

```bash
# Check for memory leaks
xcrun leaks <process-id> --outputGraph /tmp/leaks.memgraph

# Detailed output
xcrun leaks <process-id> --outputGraph /tmp/leaks.memgraph --output /tmp/leaks.txt
```

### Common Leak Patterns

```swift
// LEAK: Strong reference cycle in closures
class Service {
    var completion: (() -> Void)?
    
    func loadData() {
        completion = { [weak self] in
            guard let self else { return }
            self.updateUI()  // Strong capture of self
        }
    }
}

// FIX: Capture list
completion = { [weak self] in
    self?.updateUI()
}

// LEAK: NotificationCenter observer never removed
class Manager {
    init() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handle),
            name: .myNotification,
            object: nil
        )
    }
}

// FIX: Use modern API with automatic cleanup
class Manager {
    private var observations: [NSObjectProtocol] = []
    
    init() {
        observations.append(
            NotificationCenter.default.addObserver(
                forName: .myNotification,
                object: nil,
                queue: .main
            ) { [weak self] _ in
                self?.handle()
            }
        )
    }
}
```

### Heap Growth Analysis

```bash
# VM Map analysis
xcrun vmmap --summary <process-id>

# Detailed region analysis
xcrun vmmap <process-id> | grep -i "dirty\|resident"

# Malloc history ( Simulator only )
sudo xcrun malloc_history <process-id>
```

---

## 3. ETTrace Profiling

### Capture Launch Profile

```bash
# Install ETTrace
brew install ETTrace

# Capture profile
ettrace record --out /tmp/profile.json

# Or for specific app
ettrace record --bundleId com.app.example --out /tmp/profile.json
```

### Analyze Flamegraph

```bash
# View in browser
open https://ettrace.io/viewer

# Load profile.json in the viewer

# Key metrics to look for:
# - Launch time (target: <1s for cold, <0.5s for warm)
# - Top 5 functions by inclusive time
# - Symbolicated stacks for app-specific code
```

### Common Launch Bottlenecks

| Bottleneck | Symptom | Fix |
|-----------|---------|-----|
| Dynamic linker | `dyld` time high | Use static linking, reduce frameworks |
| ObjC setup | `+load` methods | Replace with `+initialize` or Swift static |
| Swift metadata | Type metadata init | Reduce generic specialization |
| I/O | File reads at launch | Defer to background, cache |
| Core Data | Stack creation | Lazy initialization |

---

## 4. Build Performance

### Benchmark Builds

```bash
# Clean build time
xcodebuild clean build -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15' 2>&1 | tail -5

# Incremental build time
xcodebuild build -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15' 2>&1 | tail -5

# Time it
time xcodebuild clean build -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15'
```

### Find Compile Hotspots

```bash
# Show build timing
OTHER_SWIFT_FLAGS=-Xfrontend -debug-time-function-bodies xcodebuild build

# Show type checking time
OTHER_SWIFT_FLAGS=-Xfrontend -debug-time-expression-type-checking xcodebuild build

# Parse results
cat DerivedData/MyApp/Build/Intermediates.noindex/.../MyApp.log | grep -E "^[0-9]+\.[0-9]+s" | sort -rn | head -20
```

### Fix Slow Compiles

```swift
// BAD: Complex nested generics
func process<T: Codable & Hashable & Identifiable>(
    items: [T],
    transform: @escaping (T) async throws -> U
) -> [U] where U: Codable { ... }

// GOOD: Simplify generics, use protocols
func process(items: [some Codable & Identifiable]) async throws -> [ProcessedItem] { ... }

// BAD: Large switch statements with complex types
func handle(event: SomeEvent) {
    switch event {
    case .complex(let payload):  // Payload type is huge
        // ...
    }
}

// GOOD: Extract payload handling
func handle(event: SomeEvent) {
    switch event {
    case .complex(let payload):
        handleComplexPayload(payload)
    }
}

private func handleComplexPayload(_ payload: ComplexPayload) {
    // ...
}
```

### SPM Optimization

```bash
# Check package resolution time
swift package resolve --verbose 2>&1 | grep -i "resolving\|fetching"

# Use binary targets when possible
# In Package.swift:
.target(
    name: "MyTarget",
    dependencies: [
        .product(name: "SomeLib", package: "some-lib"),
        // Prefer .binaryTarget over source
    ]
)

# Disable debug symbols for dependencies
// In .xcconfig or Build Settings:
// SWIFT_OPTIMIZATION_LEVEL = -O
// DEBUG_INFORMATION_FORMAT = dwarf-with-dsym
```

### Xcode Build Settings

```
// Faster builds
SWIFT_COMPILATION_MODE = wholemodule
SWIFT_OPTIMIZATION_LEVEL = -O
ENABLE_TESTABILITY = NO (for Release)

// Parallel building
GCCParallelizeCompilesFromTargetDirectories = YES
SWIFT_SERIALIZE_BUILDING = YES

// Module stability (for CI)
BUILD_LIBRARY_FOR_DISTRIBUTION = YES
```

---

## 5. MetricKit Triage

### Register for Reports

```swift
class MetricManager: NSObject, MXMetricManagerSubscriber {
    static let shared = MetricManager()
    
    func start() {
        MXMetricManager.shared.add(self)
    }
    
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            processMetricPayload(payload)
        }
    }
    
    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            processDiagnosticPayload(payload)
        }
    }
    
    private func processMetricPayload(_ payload: MXMetricPayload) {
        // Launch time
        if let launchMetric = payload.applicationLaunchMetrics {
            let avgResumeTime = launchMetric.histogrammedTimeToFirstDraw
            // Report to analytics
        }
        
        // Memory
        if let memoryMetric = payload.memoryMetrics {
            let peakMemory = memoryMetric.peakMemoryUsage
            // Alert if too high
        }
        
        // CPU
        if let cpuMetric = payload.cpuMetrics {
            let cumulativeCPUTime = cpuMetric.cumulativeCPUTime
            // Report
        }
    }
    
    private func processDiagnosticPayload(_ payload: MXDiagnosticPayload) {
        // Crashes
        if let crashDiagnostics = payload.crashDiagnostics {
            for crash in crashDiagnostics {
                let callStack = crash.callStackTree
                // Symbolicate and report
            }
        }
        
        // Hangs
        if let hangDiagnostics = payload.hangDiagnostics {
            for hang in hangDiagnostics {
                let duration = hang.hangDuration
                // Alert if > 1s
            }
        }
        
        // App launches
        if let launchDiagnostics = payload.appLaunchDiagnostics {
            for launch in launchDiagnostics {
                // Analyze launch time
            }
        }
    }
}
```

### Signpost Profiling

```swift
import os.signpost

let log = OSLog(subsystem: "com.app", category: "Performance")

func loadData() {
    let signpostID = OSSignpostID(log: log)
    os_signpost(.begin, log: log, name: "LoadData", signpostID: signpostID)
    
    // Your code here
    let data = try await api.fetch()
    
    os_signpost(.end, log: log, name: "LoadData", signpostID: signpostID)
}
```

### Analyze in Instruments

1. Open Instruments → select "os_signpost" template
2. Record app usage
3. Find your signposts on the timeline
4. Measure duration and identify outliers

---

## 6. LLDB Debugging

### Useful Commands

```bash
# Print variable
p variableName

# Print expression
p NSHomeDirectory()

# View memory
memory read 0x00007fff...

# Thread backtrace
thread backtrace

# Breakpoint commands
breakpoint set --name viewDidLoad
breakpoint set --selector buttonTapped:

# Conditional breakpoint
breakpoint set --name myFunction --condition "counter > 10"

# Watchpoint (variable changes)
watchpoint set variable myVariable
```

### Expression in Debugger

```swift
// In LLDB console
po view  // Print object description
p view.frame  // Print frame
e view.backgroundColor = .red  // Execute code
po UserDefaults.standard.dictionaryRepresentation()  // Debug UserDefaults
```

---

## Decision Guide

| Symptom | Tool | First Step |
|---------|------|------------|
| Janky scrolling | Instruments: SwiftUI | Check body call count |
| Memory growing | Memory Graph | Capture and check retain cycles |
| Slow launch | ETTrace | Profile and find top functions |
| Slow builds | `xcodebuild` timing | Find slow compile targets |
| Production crash | MetricKit | Check diagnostic payloads |
| App hangs | Instruments: Time Profiler | Find main thread blocked work |
| SPM slow | `swift package resolve --verbose` | Check resolution time |

---

## Quick Commands

```bash
# Build timing
time xcodebuild clean build -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15'

# Memory snapshot
xcrun simctl io booted snapshot memgraph /tmp/snapshot.memgraph

# Leaks check
xcrun leaks <pid> --outputGraph /tmp/leaks.memgraph

# Compile time analysis
OTHER_SWIFT_FLAGS=-Xfrontend -debug-time-function-bodies xcodebuild build

# ETTrace
ettrace record --out /tmp/profile.json
```
