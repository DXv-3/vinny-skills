---
name: ios-data-persistence
description: "Skill: ios-data-persistence"
---

# Skill: ios-data-persistence

Complete data persistence strategy for iOS. Combines core-data, swiftdata, cloudkit, keychain, and file management into a unified decision framework for choosing the right storage solution.

## When to Use

- Deciding between UserDefaults, Keychain, SwiftData, Core Data, or CloudKit
- Storing user credentials securely
- Caching API responses
- Syncing data across devices
- Migrating from one storage solution to another
- Optimizing storage performance

---

## Storage Decision Matrix

| Need | Solution | Speed | Security | Sync |
|------|----------|-------|----------|------|
| Simple key-value (non-sensitive) | UserDefaults | ⚡⚡⚡ | ❌ | ❌ |
| Simple key-value (sensitive) | Keychain | ⚡⚡⚡ | ✅ | ❌ |
| Structured data (single device) | SwiftData | ⚡⚡ | ❌ | ❌ |
| Structured data (with iCloud) | SwiftData + CloudKit | ⚡⚡ | ❌ | ✅ |
| Complex queries + relationships | Core Data | ⚡⚡ | ❌ | ❌ |
| Large binary files | FileManager | ⚡⚡ | ❌ | ❌ |
| Cross-device real-time sync | CloudKit | ⚡ | ❌ | ✅ |
| End-to-end encryption | Keychain + CryptoKit | ⚡⚡ | ✅✅ | ❌ |

---

## 1. UserDefaults

### Basic Usage

```swift
// Save
UserDefaults.standard.set("John", forKey: "username")
UserDefaults.standard.set(true, forKey: "isPremium")
UserDefaults.standard.set(Date(), forKey: "lastLogin")

// Read
let username = UserDefaults.standard.string(forKey: "username") ?? "Guest"
let isPremium = UserDefaults.standard.bool(forKey: "isPremium")

// Remove
UserDefaults.standard.removeObject(forKey: "username")
```

### Type-Safe Wrapper

```swift
@propertyWrapper
struct UserDefault<T> {
    let key: String
    let defaultValue: T
    
    var wrappedValue: T {
        get { UserDefaults.standard.object(forKey: key) as? T ?? defaultValue }
        set { UserDefaults.standard.set(newValue, forKey: key) }
    }
}

@propertyWrapper
struct UserDefaultCodable<T: Codable> {
    let key: String
    let defaultValue: T
    
    var wrappedValue: T {
        get {
            guard let data = UserDefaults.standard.data(forKey: key),
                  let value = try? JSONDecoder().decode(T.self, from: data) else {
                return defaultValue
            }
            return value
        }
        set {
            if let data = try? JSONEncoder().encode(newValue) {
                UserDefaults.standard.set(data, forKey: key)
            }
        }
    }
}

// Usage
class Settings: ObservableObject {
    @UserDefault(key: "username", defaultValue: "Guest")
    var username: String
    
    @UserDefault(key: "isPremium", defaultValue: false)
    var isPremium: Bool
    
    @UserDefaultCodable(key: "theme", defaultValue: .system)
    var theme: Theme
}

enum Theme: String, Codable {
    case light, dark, system
}
```

### When to Use

- App settings and preferences
- Feature flags
- Onboarding completion state
- Last visited screen
- Simple boolean toggles

### When NOT to Use

- Sensitive data (use Keychain)
- Large data (use FileManager)
- Structured data with relationships (use SwiftData)
- Data that needs to sync (use CloudKit)

---

## 2. Keychain

### Secure Storage

```swift
class KeychainManager {
    static let shared = KeychainManager()
    
    func save(_ data: Data, for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.saveFailed(status) }
    }
    
    func save(_ string: String, for key: String) throws {
        guard let data = string.data(using: .utf8) else {
            throw KeychainError.invalidData
        }
        try save(data, for: key)
    }
    
    func load(for key: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data else {
            throw KeychainError.loadFailed(status)
        }
        return data
    }
    
    func loadString(for key: String) throws -> String {
        let data = try load(for: key)
        guard let string = String(data: data, encoding: .utf8) else {
            throw KeychainError.invalidData
        }
        return string
    }
    
    func delete(for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.deleteFailed(status)
        }
    }
    
    enum KeychainError: Error {
        case saveFailed(OSStatus)
        case loadFailed(OSStatus)
        case deleteFailed(OSStatus)
        case invalidData
    }
}
```

### When to Use

- Auth tokens and API keys
- Passwords and credentials
- Credit card information
- Any sensitive user data

---

## 3. SwiftData

### Model Definition

```swift
import SwiftData

@Model
class Note {
    var id: UUID
    var title: String
    var content: String
    var createdAt: Date
    var updatedAt: Date
    var tags: [String]
    
    @Relationship(deleteRule: .cascade)
    var attachments: [Attachment]
    
    init(title: String, content: String = "") {
        self.id = UUID()
        self.title = title
        self.content = content
        self.createdAt = Date()
        self.updatedAt = Date()
        self.tags = []
        self.attachments = []
    }
}

@Model
class Attachment {
    var id: UUID
    var filename: String
    var data: Data
    var mimeType: String
    
    init(filename: String, data: Data, mimeType: String) {
        self.id = UUID()
        self.filename = filename
        self.data = data
        self.mimeType = mimeType
    }
}
```

### Container Setup

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Note.self, Attachment.self])
    }
}
```

### CRUD Operations

```swift
class NoteStore: ObservableObject {
    private let modelContainer: ModelContainer
    private let modelContext: ModelContext
    
    init() throws {
        let config = ModelConfiguration(isStoredInMemoryOnly: false)
        self.modelContainer = try ModelContainer(for: Note.self, configurations: config)
        self.modelContext = modelContainer.mainContext
    }
    
    // Create
    func create(title: String, content: String) throws {
        let note = Note(title: title, content: content)
        modelContext.insert(note)
        try modelContext.save()
    }
    
    // Read
    func fetchAll() throws -> [Note] {
        let descriptor = FetchDescriptor<Note>(sortBy: [SortDescriptor(\.updatedAt, order: .reverse)])
        return try modelContext.fetch(descriptor)
    }
    
    func search(query: String) throws -> [Note] {
        let descriptor = FetchDescriptor<Note>(
            predicate: #Predicate { note in
                note.title.localizedStandardContains(query) ||
                note.content.localizedStandardContains(query)
            }
        )
        return try modelContext.fetch(descriptor)
    }
    
    // Update
    func update(_ note: Note, title: String, content: String) throws {
        note.title = title
        note.content = content
        note.updatedAt = Date()
        try modelContext.save()
    }
    
    // Delete
    func delete(_ note: Note) throws {
        modelContext.delete(note)
        try modelContext.save()
    }
}
```

### Queries with Predicates

```swift
// Simple predicates
let descriptor = FetchDescriptor<Note>(
    predicate: #Predicate { $0.tags.contains("important") }
)

// Complex predicates
let descriptor = FetchDescriptor<Note>(
    predicate: #Predicate { note in
        note.createdAt > startDate && note.createdAt < endDate
    }
)

// Sort descriptors
let descriptor = FetchDescriptor<Note>(
    sortBy: [
        SortDescriptor(\.updatedAt, order: .reverse),
        SortDescriptor(\.title)
    ]
)

// Limit results
let descriptor = FetchDescriptor<Note>(
    fetchLimit: 10
)
```

### SwiftData + CloudKit

```swift
let config = ModelConfiguration(
    cloudKitDatabase: .automatic,
    groupContainer: .automatic
)

let container = try ModelContainer(
    for: Note.self,
    configurations: config
)
```

---

## 4. Core Data

### When to Use Over SwiftData

- Need batch operations (NSBatchInsertRequest)
- Need persistent history tracking
- Need lightweight migrations
- Working with existing Core Data codebase
- Need more control over SQL store

### Model Definition

```swift
// Core Data model in .xcdatamodeld
// Entity: Note
// Attributes: id (UUID), title (String), content (String), createdAt (Date)
```

### NSManagedObject Subclass

```swift
@objc(Note)
public class Note: NSManagedObject {
    @NSManaged public var id: UUID
    @NSManaged public var title: String
    @NSManaged public var content: String
    @NSManaged public var createdAt: Date
    @NSManaged public var updatedAt: Date
}

extension Note {
    @nonobjc public class func fetchRequest() -> NSFetchRequest<Note> {
        return NSFetchRequest<Note>(entityName: "Note")
    }
}
```

### Persistent Container

```swift
class CoreDataStack {
    static let shared = CoreDataStack()
    
    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "Model")
        container.loadPersistentStores { _, error in
            if let error {
                fatalError("Core Data error: \(error)")
            }
        }
        return container
    }()
    
    var context: NSManagedObjectContext {
        persistentContainer.viewContext
    }
    
    func save() {
        guard context.hasChanges else { return }
        try? context.save()
    }
}
```

### Batch Operations

```swift
// Batch insert
let batchInsert = NSBatchInsertRequest(entity: Note.entity()) { (dictionary: inout [String: Any]) in
    dictionary["id"] = UUID()
    dictionary["title"] = "New Note"
    dictionary["content"] = ""
    dictionary["createdAt"] = Date()
    return true
}
try? context.execute(batchInsert)

// Batch update
let batchUpdate = NSBatchUpdateRequest(entityName: "Note")
batchUpdate.predicate = #Predicate<Note> { $0.title.isEmpty }
batchUpdate.propertiesToUpdate = ["title": "Untitled"]
try? context.execute(batchUpdate)

// Batch delete
let batchDelete = NSBatchDeleteRequest(fetchRequest: Note.fetchRequest())
batchDelete.predicate = #Predicate<Note> { $0.content.isEmpty }
try? context.execute(batchDelete)
```

### Persistent History Tracking

```swift
// Enable in Core Data stack
let description = NSPersistentStoreDescription()
description.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)
description.setOption(true as NSNumber, forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)
```

---

## 5. FileManager (File Storage)

### Document Directory

```swift
class FileStorage {
    static let shared = FileStorage()
    
    private let documentsDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    
    func save<T: Codable>(_ object: T, to filename: String) throws {
        let url = documentsDirectory.appendingPathComponent(filename)
        let data = try JSONEncoder().encode(object)
        try data.write(to: url)
    }
    
    func load<T: Codable>(_ type: T.Type, from filename: String) throws -> T {
        let url = documentsDirectory.appendingPathComponent(filename)
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(type, from: data)
    }
    
    func delete(filename: String) throws {
        let url = documentsDirectory.appendingPathComponent(filename)
        try FileManager.default.removeItem(at: url)
    }
    
    func fileExists(filename: String) -> Bool {
        let url = documentsDirectory.appendingPathComponent(filename)
        return FileManager.default.fileExists(atPath: url.path)
    }
    
    func listFiles() throws -> [String] {
        let contents = try FileManager.default.contentsOfDirectory(
            at: documentsDirectory,
            includingPropertiesForKeys: nil
        )
        return contents.map { $0.lastPathComponent }
    }
    
    // Directory for cached data
    var cacheDirectory: URL {
        FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
    }
    
    // Directory for temporary data
    var tempDirectory: URL {
        FileManager.default.temporaryDirectory
    }
}
```

### Save Large Files

```swift
// Images
func saveImage(_ image: UIImage, named name: String) throws {
    guard let data = image.jpegData(compressionQuality: 0.8) else {
        throw FileError.invalidImage
    }
    try FileStorage.shared.save(data, to: "\(name).jpg")
}

func loadImage(named name: String) throws -> UIImage {
    let data: Data = try FileStorage.shared.load(Data.self, from: "\(name).jpg")
    guard let image = UIImage(data: data) else {
        throw FileError.invalidImage
    }
    return image
}

// Codable objects
struct CachedResponse: Codable {
    let data: Data
    let timestamp: Date
    let expiry: Date
}

func cacheResponse(_ response: Data, forKey key: String) throws {
    let cached = CachedResponse(
        data: response,
        timestamp: Date(),
        expiry: Date().addingTimeInterval(300)  // 5 minutes
    )
    try FileStorage.shared.save(cached, to: "cache_\(key).json")
}

func loadCachedResponse(forKey key: String) throws -> Data? {
    let cached: CachedResponse = try FileStorage.shared.load(CachedResponse.self, from: "cache_\(key).json")
    guard cached.expiry > Date() else { return nil }
    return cached.data
}
```

---

## 6. Migration Strategies

### SwiftData Migration

```swift
// Versioned schema
enum SchemaV1: VersionedSchema {
    static var versionIdentifier = SchemaVersion(1, 0, 0)
    
    static var models: [any VersionedSchema.Type] {
        [NoteV1.self]
    }
}

@Model
class NoteV1 {
    var id: UUID
    var title: String
    var content: String
}

enum SchemaV2: VersionedSchema {
    static var versionIdentifier = SchemaVersion(2, 0, 0)
    
    static var models: [any VersionedSchema.Type] {
        [NoteV2.self]
    }
}

@Model
class NoteV2 {
    var id: UUID
    var title: String
    var content: String
    var tags: [String]  // New property
}

// Migration plan
struct NoteMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [SchemaV1.self, SchemaV2.self]
    }
    
    static var stages: [MigrationStage] {
        [migrationV1toV2]
    }
    
    static var migrationV1toV2: MigrationStage {
        .modifySchema(sourceSchema: SchemaV1.self, destinationSchema: SchemaV2.self) { context in
            // Add default tags to existing notes
            try context.fetch(FetchDescriptor<NoteV2>()).forEach { note in
                note.tags = []
            }
        }
    }
}
```

### Core Data Migration

```swift
// Lightweight migration
let description = NSPersistentStoreDescription()
description.setOption(true as NSNumber, forKey: NSMigratePersistentStoresAutomaticallyOption)
description.setOption(true as NSNumber, forKey: NSInferMappingModelAutomaticallyOption)

// Manual migration mapping model
let mappingModel = NSMappingModel(from: nil, forSourceModel: sourceModel, destinationModels: [destinationModel])
```

---

## 7. Performance Optimization

### Batch Fetching

```swift
// SwiftData
let descriptor = FetchDescriptor<Note>(
    predicate: #Predicate { $0.tags.contains("important") },
    sortBy: [SortDescriptor(\.updatedAt)],
    fetchLimit: 50,
    fetchOffset: 0  // Pagination
)
```

### Background Context

```swift
// SwiftData
let backgroundContext = modelContainer.mainContext

Task {
    let context = ModelContext(modelContainer)
    // Perform heavy operations on background context
    try await context.perform {
        // ... heavy work
        try context.save()
    }
}

// Core Data
let backgroundContext = persistentContainer.newBackgroundContext()
backgroundContext.perform {
    // ... heavy work
    try? backgroundContext.save()
}
```

### Lazy Loading

```swift
// Only load what you need
@Model
class Note {
    var title: String
    var content: String
    
    @Transient  // Not persisted
    var isEditing: Bool = false
}
```

---

## Decision Guide

| Scenario | Solution |
|----------|----------|
| App settings, preferences | UserDefaults |
| Auth tokens, API keys | Keychain |
| Notes, tasks, simple entities | SwiftData |
| Complex relationships, migrations | Core Data |
| Images, PDFs, large files | FileManager |
| Cross-device sync | SwiftData + CloudKit |
| Offline-first with sync | SwiftData + CloudKit + Background Tasks |
| End-to-end encryption | Keychain + CryptoKit + FileManager |
