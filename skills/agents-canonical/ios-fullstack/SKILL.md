---
name: ios-fullstack
description: "Skill: ios-fullstack"
---

# Skill: ios-fullstack

Unified iOS app development skill covering architecture, SwiftUI, concurrency, networking, background processing, and App Intents. Use this instead of juggling swift-architecture, swiftui-patterns, swift-concurrency, ios-networking, background-processing, and app-intents separately.

## When to Use

- Building a new iOS app from scratch
- Choosing between MVVM, TCA, VIPER, or Clean Architecture
- Structuring SwiftUI views with @Observable, @State, @Environment
- Adopting async/await and structured concurrency
- Building REST/WebSocket APIs with URLSession
- Scheduling background tasks with BGTaskScheduler
- Exposing app actions to Siri, Shortcuts, or Widget intents

---

## Architecture Selection

Choose based on complexity:

| App Type | Architecture | Why |
|----------|--------------|-----|
| Simple, few screens | **MVVM + Observation** | Minimal boilerplate, SwiftUI-native |
| Medium, multiple features | **MVVM + Coordinator** | Navigation separation without overkill |
| Complex, many teams | **Clean Architecture** | Clear boundaries, testable, scalable |
| Reactive, state-heavy | **TCA (The Composable Architecture)** | Unidirectional data flow, composable |
| Legacy migration target | **VIPER** | Only if migrating from existing VIPER code |

### MVVM + Observation (Default Choice)

```swift
@Observable
class FeatureViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: String?
    
    private let service: ItemServiceProtocol
    
    init(service: ItemServiceProtocol = ItemService()) {
        self.service = service
    }
    
    func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            items = try await service.fetch()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

struct FeatureView: View {
    @State private var viewModel = FeatureViewModel()
    
    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .overlay {
            if viewModel.isLoading {
                ProgressView()
            }
        }
        .task { await viewModel.load() }
    }
}
```

### TCA (When You Need It)

```swift
@Reducer
struct Feature {
    @ObservableState
    struct State: Equatable {
        var items: [Item] = []
        var isLoading = false
    }
    
    enum Action {
        case loadButtonTapped
        case itemsResponse(Result<[Item], Error>)
    }
    
    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .loadButtonTapped:
                state.isLoading = true
                return .run { send in
                    let items = try await service.fetch()
                    await send(.itemsResponse(.success(items)))
                }
            case .itemsResponse(.success(let items)):
                state.items = items
                state.isLoading = false
                return .none
            case .itemsResponse(.failure):
                state.isLoading = false
                return .none
            }
        }
    }
}
```

---

## SwiftUI Patterns

### View Composition

Decompose views into small, focused pieces:

```swift
struct FeatureView: View {
    @State private var viewModel = FeatureViewModel()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                headerSection
                contentSection
                footerSection
            }
        }
        .navigationTitle("Feature")
    }
    
    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Title")
                .font(.title2.bold())
            Text("Subtitle")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding(.horizontal)
    }
    
    @ViewBuilder
    private var contentSection: some View {
        if viewModel.isLoading {
            ProgressView()
                .frame(maxWidth: .infinity)
        } else {
            LazyVStack(spacing: 12) {
                ForEach(viewModel.items) { item in
                    ItemRow(item: item)
                }
            }
        }
    }
    
    private var footerSection: some View {
        Button("Load More") { Task { await viewModel.loadMore() } }
            .buttonStyle(.bordered)
            .padding()
    }
}
```

### ViewModifiers

```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .shadow(radius: 2)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}

// Usage
Text("Hello").cardStyle()
```

### State Management

```swift
// @State — local view state
@State private var isShowingSheet = false

// @Bindable — two-way binding to @Observable
@Bindable var viewModel: FeatureViewModel

// @Environment — dependency injection
@Environment(\.dismiss) private var dismiss

// @EnvironmentObject — shared state (use sparingly)
@EnvironmentObject var appState: AppState
```

---

## Concurrency Patterns

### Structured Concurrency

```swift
// Sequential
func loadData() async {
    let profile = try await fetchProfile()
    let posts = try await fetchPosts(for: profile.id)
    let comments = try await fetchComments(for: posts)
}

// Parallel
func loadDashboard() async async throws {
    async let profile = fetchProfile()
    async let posts = fetchPosts()
    async let notifications = fetchNotifications()
    
    let (p, n, notif) = try await (profile, posts, notifications)
}

// TaskGroup for dynamic collections
func loadAllItems(ids: [String]) async throws -> [Item] {
    try await withThrowingTaskGroup(of: Item.self) { group in
        for id in ids {
            group.addTask { try await fetchItem(id: id) }
        }
        return try await group.reduce(into: []) { $0.append($1) }
    }
}
```

### Actor Isolation

```swift
actor Cache {
    private var storage: [String: Data] = [:]
    
    func get(_ key: String) -> Data? { storage[key] }
    func set(_ key: String, value: Data) { storage[key] = value }
    func remove(_ key: String) { storage.removeValue(forKey: key) }
}

// Usage
let cache = Cache()
let data = await cache.get("key")
await cache.set("key", value: someData)
```

### Sendable Conformance

```swift
// Value types are automatically Sendable
struct UserProfile: Sendable {
    let id: String
    let name: String
}

// Classes need explicit conformance
final class NetworkClient: Sendable {
    let session: URLSession
    
    init(session: URLSession = .shared) {
        self.session = session
    }
}

// Nonisolated for crossing isolation boundaries
nonisolated func processItem(_ item: Item) async -> Result {
    // Process without actor context
}
```

---

## Networking

### Modern URLSession

```swift
actor APIClient {
    private let session: URLSession
    private let baseURL: URL
    
    init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }
    
    func request<T: Decodable>(
        _ endpoint: String,
        method: HTTPMethod = .GET,
        body: (any Encodable)? = nil,
        headers: [String: String] = [:]
    ) async throws -> T {
        var request = URLRequest(url: baseURL.appendingPathComponent(endpoint))
        request.httpMethod = method.rawValue
        
        for (key, value) in headers {
            request.setValue(value, forHTTPHeaderField: key)
        }
        
        if let body {
            request.httpBody = try JSONEncoder().encode(body)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
}

enum HTTPMethod: String {
    case GET, POST, PUT, DELETE, PATCH
}

enum APIError: Error {
    case invalidResponse
    case decodingError
    case unauthorized
}
```

### Caching

```swift
extension URLSession {
    func cachedRequest<T: Decodable>(
        _ request: URLRequest,
        cacheKey: String,
        ttl: TimeInterval = 300
    ) async throws -> T {
        let cache = URLCache.shared
        if let cached = cache.cachedResponse(for: request),
           let cachedDate = cached.response.date,
           Date().timeIntervalSince(cachedDate) < ttl {
            return try JSONDecoder().decode(T.self, from: cached.data)
        }
        
        let (data, response) = try await session.data(for: request)
        let cachedResponse = CachedURLResponse(
            response: response,
            data: data
        )
        cache.storeCachedResponse(cachedResponse, for: request)
        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

### WebSocket

```swift
actor ChatService {
    private var webSocket: URLSessionWebSocketTask?
    
    func connect(to url: URL) async throws {
        webSocket = URLSession.shared.webSocketTask(with: url)
        webSocket?.resume()
        
        try await receiveMessages()
    }
    
    func send(_ message: String) async throws {
        try await webSocket?.send(.string(message))
    }
    
    private func receiveMessages() async throws {
        guard let webSocket else { return }
        
        while true {
            let message = try await webSocket.receive()
            switch message {
            case .string(let text):
                await handleMessage(text)
            case .data(let data):
                await handleData(data)
            @unknown default:
                break
            }
        }
    }
}
```

---

## Background Processing

### BGTaskScheduler

```swift
class BackgroundManager {
    static let shared = BackgroundManager()
    
    func registerTasks() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.app.refresh",
            using: nil
        ) { task in
            self.handleAppRefresh(task as! BGAppRefreshTask)
        }
        
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.app.processing",
            using: nil
        ) { task in
            self.handleProcessing(task as! BGProcessingTask)
        }
    }
    
    func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
        try? BGTaskScheduler.shared.submit(request)
    }
    
    func scheduleProcessing() {
        let request = BGProcessingTaskRequest(identifier: "com.app.processing")
        request.requiresNetworkConnectivity = true
        request.requiresExternalPower = false
        try? BGTaskScheduler.shared.submit(request)
    }
    
    private func handleAppRefresh(_ task: BGAppRefreshTask) {
        let operation = RefreshOperation()
        task.expirationHandler = { operation.cancel() }
        
        Task {
            await operation.main()
            task.setTaskCompleted(success: !operation.isCancelled)
            scheduleAppRefresh()
        }
    }
    
    private func handleProcessing(_ task: BGProcessingTask) {
        let operation = ProcessingOperation()
        task.expirationHandler = { operation.cancel() }
        
        Task {
            await operation.main()
            task.setTaskCompleted(success: !operation.isCancelled)
        }
    }
}
```

### Info.plist Configuration

```xml
<key>BGTaskSchedulerPermittedIdentifiers</key>
<array>
    <string>com.app.refresh</string>
    <string>com.app.processing</string>
</array>
```

---

## App Intents

### Basic Intent

```swift
struct ToggleFeatureIntent: AppIntent {
    static var title: LocalizedStringResource = "Toggle Feature"
    static var description = IntentDescription("Toggles a feature on or off")
    
    @Parameter(title: "Feature Name")
    var featureName: String
    
    func perform() async throws -> some IntentResult & ReturnsValue<Bool> {
        let newState = !UserDefaults.standard.bool(forKey: featureName)
        UserDefaults.standard.set(newState, forKey: featureName)
        return .result(value: newState)
    }
}
```

### Entity

```swift
struct WorkoutEntity: AppEntity {
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Workout"
    
    var id: String
    var name: String
    var duration: Int
    
    static var defaultQuery = WorkoutQuery()
}

struct WorkoutQuery: EntityQuery {
    func entities(for identifiers: [String]) async throws -> [WorkoutEntity] {
        // Return workouts matching identifiers
        return []
    }
    
    func suggestedEntities() async throws -> [WorkoutEntity] {
        // Return all available workouts
        return []
    }
}
```

### Siri Phrase

```swift
struct MyAppShortcutsProvider: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: ToggleFeatureIntent(),
            phrases: [
                "Toggle \(.applicationName) feature",
                "Turn on \(.applicationName) feature"
            ],
            shortTitle: "Toggle Feature",
            systemImageName: "switch.2"
        )
    }
}
```

---

## Decision Guide

| Situation | Use This |
|-----------|----------|
| New app, simple UI | MVVM + @Observable |
| Complex state management | TCA |
| Need navigation separation | Coordinator pattern |
| Data-heavy app | Clean Architecture |
| Background sync needed | BGTaskScheduler |
| Siri/Shortcuts integration | App Intents |
| Real-time updates | WebSocket + async streams |
| Multiple parallel fetches | TaskGroup |

---

## Common Pitfalls

1. **Don't** use `@EnvironmentObject` for new code — prefer `@Observable` with `@State`
2. **Don't** mix `async let` with sequential calls unnecessarily — parallelize when independent
3. **Don't** forget `task { }` modifier for loading data in views
4. **Don't** use `DispatchQueue.main.async` in SwiftUI — use `Task { @MainActor in }`
5. **Don't** create view models in view body — create them with `@State` or inject them
