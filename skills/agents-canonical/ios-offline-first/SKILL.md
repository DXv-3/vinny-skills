---
name: ios-offline-first
description: "Skill: ios-offline-first"
---

# Skill: ios-offline-first

Complete offline-first architecture for iOS apps. Combines CloudKit, SwiftData, background processing, and networking into a unified strategy for apps that work without internet and sync seamlessly when online.

## When to Use

- App must work in airplane mode or poor connectivity
- Need conflict resolution when devices sync
- Background data sync when app returns online
- Cache-first networking patterns
- Offline queuing of user actions

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│                  UI Layer                    │
│         (SwiftUI + @Observable)             │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│              Data Layer                     │
│    (SwiftData / Core Data + CloudKit)       │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Sync Engine                      │
│   (CKSyncEngine / NSPersistentHistory)      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           Network Layer                     │
│   (URLSession + Background Tasks)           │
└─────────────────────────────────────────────┘
```

---

## 1. SwiftData + CloudKit

### Model Setup

```swift
import SwiftData
import CloudKit

@Model
class Task {
    var id: UUID
    var title: String
    var isCompleted: Bool
    var createdAt: Date
    var updatedAt: Date
    var serverRecordName: String?  // For sync
    
    init(title: String) {
        self.id = UUID()
        self.title = title
        self.isCompleted = false
        self.createdAt = Date()
        self.updatedAt = Date()
    }
}

// CloudKit container setup
let config = ModelConfiguration(
    cloudKitDatabase: .automatic,  // Uses your iCloud container
    groupContainer: .automatic
)

let container = try ModelContainer(
    for: Task.self,
    configurations: config
)
```

### Conflict Resolution

```swift
@Model
class Task {
    // ... other properties
    
    var conflictVersion: Int = 0
    
    func resolveConflict(with remote: Task) {
        // Last-write-wins (simple)
        if remote.updatedAt > self.updatedAt {
            self.title = remote.title
            self.isCompleted = remote.isCompleted
            self.updatedAt = remote.updatedAt
        }
        
        // Or merge (complex)
        // Merge specific fields based on your business rules
    }
}
```

### Sync Status

```swift
import CloudKit

class SyncManager: ObservableObject {
    @Published var syncStatus: SyncStatus = .idle
    
    enum SyncStatus {
        case idle
        case syncing
        case error(Error)
        case lastSynced(Date)
    }
    
    func sync() async {
        syncStatus = .syncing
        
        do {
            let container = try CKContainer.default()
            let database = container.privateCloudDatabase
            
            // Fetch changes
            let operation = CKFetchRecordChangesOperation()
            // ... handle changes
            
            syncStatus = .lastSynced(Date())
        } catch {
            syncStatus = .error(error)
        }
    }
}
```

---

## 2. Offline Queue

### Action Queue

```swift
import SwiftData

@Model
class PendingAction {
    var id: UUID
    var type: ActionType
    var payload: Data
    var createdAt: Date
    var retryCount: Int
    var maxRetries: Int
    var status: ActionStatus
    
    enum ActionType: Int, Codable {
        case createTask
        case updateTask
        case deleteTask
        case completeTask
    }
    
    enum ActionStatus: Int, Codable {
        case pending
        case processing
        case completed
        case failed
    }
    
    init(type: ActionType, payload: Data) {
        self.id = UUID()
        self.type = type
        self.payload = payload
        self.createdAt = Date()
        self.retryCount = 0
        self.maxRetries = 3
        self.status = .pending
    }
}

class ActionQueue: ObservableObject {
    private let modelContainer: ModelContainer
    
    init() throws {
        let config = ModelConfiguration(isStoredInMemoryOnly: false)
        self.modelContainer = try ModelContainer(
            for: PendingAction.self,
            configurations: config
        )
    }
    
    func enqueue(_ action: PendingAction) async throws {
        let context = modelContainer.mainContext
        context.insert(action)
        try context.save()
    }
    
    func processPending() async {
        let context = modelContainer.mainContext
        let descriptor = FetchDescriptor<PendingAction>(
            predicate: #Predicate { $0.status == .pending },
            sortBy: [SortDescriptor(\.createdAt)]
        )
        
        guard let actions = try? context.fetch(descriptor) else { return }
        
        for action in actions {
            await processAction(action)
        }
    }
    
    private func processAction(_ action: PendingAction) async {
        action.status = .processing
        
        do {
            try await execute(action)
            action.status = .completed
        } catch {
            action.retryCount += 1
            if action.retryCount >= action.maxRetries {
                action.status = .failed
            } else {
                action.status = .pending  // Retry later
            }
        }
        
        try? modelContainer.mainContext.save()
    }
    
    private func execute(_ action: PendingAction) async throws {
        switch action.type {
        case .createTask:
            let task = try JSONDecoder().decode(Task.self, from: action.payload)
            try await APIClient.shared.create(task)
        case .updateTask:
            let task = try JSONDecoder().decode(Task.self, from: action.payload)
            try await APIClient.shared.update(task)
        case .deleteTask:
            let id = try JSONDecoder().decode(UUID.self, from: action.payload)
            try await APIClient.shared.delete(id)
        case .completeTask:
            let id = try JSONDecoder().decode(UUID.self, from: action.payload)
            try await APIClient.shared.complete(id)
        }
    }
}
```

---

## 3. Cache-First Networking

```swift
class CacheFirstNetworker {
    private let cache = URLCache(memoryCapacity: 10_000_000, diskCapacity: 50_000_000)
    
    func fetch<T: Decodable>(_ endpoint: String, cachePolicy: CachePolicy = .cacheFirst) async throws -> T {
        switch cachePolicy {
        case .cacheFirst:
            return try await cacheFirst(endpoint)
        case .networkFirst:
            return try await networkFirst(endpoint)
        case .cacheOnly:
            return try await cacheOnly(endpoint)
        case .networkOnly:
            return try await networkOnly(endpoint)
        }
    }
    
    private func cacheFirst<T: Decodable>(_ endpoint: String) async throws -> T {
        // Try cache first
        let request = URLRequest(url: URL(string: endpoint)!)
        if let cached = cache.cachedResponse(for: request),
           let result = try? JSONDecoder().decode(T.self, from: cached.data) {
            return result
        }
        
        // Fall back to network
        return try await networkOnly(endpoint)
    }
    
    private func networkFirst<T: Decodable>(_ endpoint: String) async throws -> T {
        do {
            let result: T = try await networkOnly(endpoint)
            // Update cache
            return result
        } catch {
            // Fall back to cache
            return try await cacheOnly(endpoint)
        }
    }
    
    private func cacheOnly<T: Decodable>(_ endpoint: String) async throws -> T {
        let request = URLRequest(url: URL(string: endpoint)!)
        guard let cached = cache.cachedResponse(for: request),
              let result = try? JSONDecoder().decode(T.self, from: cached.data) else {
            throw OfflineError.noCacheData
        }
        return result
    }
    
    private func networkOnly<T: Decodable>(_ endpoint: String) async throws -> T {
        let url = URL(string: endpoint)!
        let (data, response) = try await URLSession.shared.data(from: url)
        
        // Cache the response
        let cachedResponse = CachedURLResponse(response: response, data: data)
        cache.storeCachedResponse(cachedResponse, for: URLRequest(url: url))
        
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    enum CachePolicy {
        case cacheFirst, networkFirst, cacheOnly, networkOnly
    }
    
    enum OfflineError: Error {
        case noCacheData
        case noNetwork
    }
}
```

---

## 4. Background Sync

### BGTaskScheduler for Sync

```swift
class BackgroundSyncManager {
    static let shared = BackgroundSyncManager()
    
    func registerTasks() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.app.sync",
            using: nil
        ) { task in
            self.handleSync(task as! BGProcessingTask)
        }
    }
    
    func scheduleSync() {
        let request = BGProcessingTaskRequest(identifier: "com.app.sync")
        request.requiresNetworkConnectivity = true
        request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 5)  // 5 min
        
        try? BGTaskScheduler.shared.submit(request)
    }
    
    private func handleSync(_ task: BGProcessingTask) {
        let syncTask = Task { @MainActor in
            do {
                try await self.performSync()
                task.setTaskCompleted(success: true)
            } catch {
                task.setTaskCompleted(success: false)
            }
        }
        
        task.expirationHandler = {
            syncTask.cancel()
        }
        
        Task {
            await syncTask.value
            self.scheduleSync()  // Schedule next sync
        }
    }
    
    private func performSync() async throws {
        // 1. Push pending actions
        let queue = try ActionQueue()
        await queue.processPending()
        
        // 2. Pull remote changes
        try await SyncManager.shared.sync()
        
        // 3. Resolve conflicts
        try await resolveConflicts()
    }
    
    private func resolveConflicts() async throws {
        // Implement your conflict resolution strategy
    }
}
```

### Info.plist

```xml
<key>BGTaskSchedulerPermittedIdentifiers</key>
<array>
    <string>com.app.sync</string>
</array>
```

---

## 5. Connectivity Monitor

```swift
import Network

class ConnectivityMonitor: ObservableObject {
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "ConnectivityMonitor")
    
    @Published var isConnected = true
    @Published var connectionType: ConnectionType = .unknown
    
    enum ConnectionType {
        case wifi, cellular, ethernet, unknown, none
    }
    
    func startMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isConnected = path.status == .satisfied
                self?.connectionType = self?.getType(path) ?? .unknown
                
                if path.status == .satisfied {
                    // Trigger sync when connection returns
                    NotificationCenter.default.post(name: .connectivityRestored, object: nil)
                }
            }
        }
        
        monitor.start(queue: queue)
    }
    
    func stopMonitoring() {
        monitor.cancel()
    }
    
    private func getType(_ path: NWPath) -> ConnectionType {
        if path.usesInterfaceType(.wifi) { return .wifi }
        if path.usesInterfaceType(.cellular) { return .cellular }
        if path.usesInterfaceType(.wiredEthernet) { return .ethernet }
        return .unknown
    }
}

extension Notification.Name {
    static let connectivityRestored = Notification.Name("connectivityRestored")
}
```

---

## 6. Offline UI Patterns

```swift
struct OfflineBanner: View {
    @StateObject private var connectivity = ConnectivityMonitor()
    
    var body: some View {
        VStack {
            if !connectivity.isConnected {
                HStack {
                    Image(systemName: "wifi.slash")
                    Text("You're offline")
                        .font(.caption)
                }
                .padding(8)
                .background(.yellow)
                .transition(.move(edge: .top))
            }
            
            // Main content
        }
        .animation(.easeInOut, value: connectivity.isConnected)
    }
}

struct OfflineQueueStatus: View {
    @StateObject private var queue: ActionQueue
    
    var body: some View {
        if queue.pendingCount > 0 {
            Label("\(queue.pendingCount) actions pending", systemImage: "arrow.triangle.2.circlepath")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }
}
```

---

## Decision Guide

| Situation | Strategy |
|-----------|----------|
| User-created data | SwiftData + CloudKit sync |
| Read-heavy content | Cache-first networking |
| Write-heavy actions | Offline queue + background sync |
| Real-time updates | WebSocket + local cache |
| Large datasets | Pagination + disk cache |
| Conflict-prone data | Last-write-wins or manual merge |

---

## Pitfalls

1. **Don't** forget to handle `modelContext.save()` after offline changes
2. **Don't** assume network is available — always check connectivity first
3. **Don't** queue infinite actions — implement a max queue size
4. **Don't** sync silently — show pending action count to user
5. **Don't** ignore conflicts — implement resolution strategy early
