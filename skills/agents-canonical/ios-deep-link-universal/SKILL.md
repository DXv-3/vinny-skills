---
name: ios-deep-link-universal
description: "Skill: ios-deep-link-universal"
---

# Skill: ios-deep-link-universal

Complete deep linking system for iOS. Combines app-intents, swiftui-navigation, widgetkit, and push-notifications into a unified deep linking strategy covering universal links, custom URL schemes, widget links, and notification-driven navigation.

## When to Use

- Handle incoming URLs and route to correct screens
- Support universal links from websites
- Widget tap actions that open specific content
- Push notification tap to navigate
- Siri/Shortcuts deep links
- Custom URL schemes for your app

---

## Deep Link Architecture

```
                    ┌─────────────────┐
                    │   Entry Points  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Universal     │  │ Custom URL      │  │ Push Widget     │
│ Links         │  │ Schemes         │  │ Notifications   │
└───────┬───────┘  └────────┬────────┘  └────────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Router/Router  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Destination    │
                    │  Views          │
                    └─────────────────┘
```

---

## 1. Deep Link Router

### Central Router

```swift
import SwiftUI

enum DeepLink: Hashable {
    case home
    case profile(userId: String)
    case settings
    case post(id: String)
    case search(query: String)
    case notification(id: String)
    
    init?(url: URL) {
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true) else {
            return nil
        }
        
        let path = components.path
        let queryItems = components.queryItems
        
        switch path {
        case "/", "/home":
            self = .home
        case "/profile":
            guard let userId = queryItems?.first(where: { $0.name == "id" })?.value else {
                return nil
            }
            self = .profile(userId: userId)
        case "/settings":
            self = .settings
        case "/post":
            guard let postId = queryItems?.first(where: { $0.name == "id" })?.value else {
                return nil
            }
            self = .post(id: postId)
        case "/search":
            let query = queryItems?.first(where: { $0.name == "q" })?.value ?? ""
            self = .search(query: query)
        default:
            return nil
        }
    }
    
    var path: String {
        switch self {
        case .home: return "/"
        case .profile(let id): return "/profile?id=\(id)"
        case .settings: return "/settings"
        case .post(let id): return "/post?id=\(id)"
        case .search(let query): return "/search?q=\(query)"
        case .notification(let id): return "/notification?id=\(id)"
        }
    }
    
    var url: URL? {
        URL(string: "myapp://\(path)")
    }
    
    var universalLink: URL? {
        URL(string: "https://myapp.com\(path)")
    }
}

class DeepLinkRouter: ObservableObject {
    @Published var currentLink: DeepLink?
    
    func handle(_ url: URL) {
        if let link = DeepLink(url: url) {
            currentLink = link
        }
    }
    
    func navigate(to link: DeepLink) {
        currentLink = link
    }
}
```

### Navigation Destination

```swift
struct ContentView: View {
    @StateObject private var router = DeepLinkRouter()
    
    var body: some View {
        NavigationStack {
            HomeView()
                .navigationDestination(for: DeepLink.self) { link in
                    destinationView(for: link)
                }
                .onOpenURL { url in
                    router.handle(url)
                }
                .onChange(of: router.currentLink) { _, link in
                    if let link {
                        // Navigate programmatically
                    }
                }
        }
        .environmentObject(router)
    }
    
    @ViewBuilder
    func destinationView(for link: DeepLink) -> some View {
        switch link {
        case .home:
            HomeView()
        case .profile(let userId):
            ProfileView(userId: userId)
        case .settings:
            SettingsView()
        case .post(let id):
            PostDetailView(postId: id)
        case .search(let query):
            SearchView(query: query)
        case .notification(let id):
            NotificationDetailView(notificationId: id)
        }
    }
}
```

---

## 2. Universal Links

### Associated Domains

```xml
<!-- entitlements -->
<key>com.apple.developer.associated-domains</key>
<array>
    <string>applinks:myapp.com</string>
    <string>applinks:www.myapp.com</string>
</array>
```

### apple-app-site-association

```json
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appIDs": ["TEAM_ID.com.company.app"],
        "paths": [
          "/profile/*",
          "/post/*",
          "/settings",
          "/search"
        ]
      }
    ]
  },
  "webcredentials": {
    "apps": ["TEAM_ID.com.company.app"]
  }
}
```

### Handle Universal Links

```swift
@main
struct MyApp: App {
    @StateObject private var router = DeepLinkRouter()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(router)
                .onContinueUserActivity(CSSearchableItemActivityType) { activity in
                    // Handle Spotlight deep links
                    if let url = activity.webpageURL {
                        router.handle(url)
                    }
                }
                .onContinueUserActivity("NSUserActivityTypeBrowsingWeb") { activity in
                    if let url = activity.webpageURL {
                        router.handle(url)
                    }
                }
        }
    }
}
```

---

## 3. Custom URL Schemes

### Info.plist

```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>myapp</string>
            <string>myapp-beta</string>
        </array>
        <key>CFBundleURLName</key>
        <string>com.company.app</string>
    </dict>
</array>
```

### Handle Custom Schemes

```swift
.onOpenURL { url in
    // url = myapp://profile?id=123
    router.handle(url)
}
```

### Compose Deep Links

```swift
// In-app link generation
struct ShareLink: View {
    let post: Post
    
    var body: some View {
        ShareLink(
            item: URL(string: "https://myapp.com/post?id=\(post.id)")!,
            preview: SharePreview(
                post.title,
                image: URL(string: post imageURL)!
            )
        ) {
            Label("Share", systemImage: "square.and.arrow.up")
        }
    }
}

// Copy to clipboard
struct CopyLinkButton: View {
    let link: DeepLink
    
    var body: some View {
        Button {
            if let url = link.universalLink {
                UIPasteboard.general.url = url
            }
        } label: {
            Label("Copy Link", systemImage: "doc.on.doc")
        }
    }
}
```

---

## 4. Widget Deep Links

### Widget Timeline Entry

```swift
import WidgetKit

struct SimpleEntry: TimelineEntry {
    let date: Date
    let deepLink: DeepLink?
}

struct Provider: TimelineProvider {
    func getTimeline(in context: Context, completion: @escaping (Timeline<SimpleEntry>) -> Void) {
        let entry = SimpleEntry(
            date: Date(),
            deepLink: .post(id: "featured-1")
        )
        
        let timeline = Timeline(entries: [entry], policy: .after(Date().addingTimeInterval(3600)))
        completion(timeline)
    }
}

struct MyWidgetEntryView: View {
    var entry: Provider.Entry
    
    var body: some View {
        VStack {
            Text("Featured Post")
            
            if let link = entry.deepLink, let url = link.url {
                Link(destination: url) {
                    Text("Read Now")
                        .font(.headline)
                        .foregroundStyle(.white)
                        .padding()
                        .background(.blue)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }
            }
        }
    }
}
```

### Interactive Widget with Deep Link

```swift
struct InteractiveWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "com.app.interactive", provider: Provider()) { entry in
            InteractiveWidgetView(entry: entry)
        }
        .configurationDisplayName("Quick Actions")
        .description("Quick access to features")
        .supportedFamilies([.systemMedium, .systemLarge])
    }
}

struct InteractiveWidgetView: View {
    var entry: Provider.Entry
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text("Quick Actions")
                    .font(.headline)
                
                // Action with deep link
                Link(destination: URL(string: "myapp://search?q=")!) {
                    Label("Search", systemImage: "magnifyingglass")
                }
                
                Link(destination: URL(string: "myapp://settings")!) {
                    Label("Settings", systemImage: "gear")
                }
                
                Link(destination: URL(string: "myapp://profile?id=current")!) {
                    Label("Profile", systemImage: "person")
                }
            }
            
            Spacer()
        }
        .padding()
    }
}
```

---

## 5. Push Notification Deep Links

### Notification Payload

```json
{
  "aps": {
    "alert": {
      "title": "New Post",
      "body": "Check out this new post"
    },
    "badge": 1,
    "sound": "default"
  },
  "deep_link": "/post?id=123",
  "type": "new_post"
}
```

### Handle Notification Tap

```swift
class AppDelegate: NSObject, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        // Register for remote notifications
        UNUserNotificationCenter.current().delegate = self
        return true
    }
    
    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        // Send token to server
    }
}

extension AppDelegate: UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        
        if let deepLinkPath = userInfo["deep_link"] as? String,
           let url = URL(string: "myapp://\(deepLinkPath)") {
            
            // Post notification to router
            NotificationCenter.default.post(
                name: .notificationDeepLink,
                object: nil,
                userInfo: ["url": url]
            )
        }
        
        completionHandler()
    }
}

extension Notification.Name {
    static let notificationDeepLink = Notification.Name("notificationDeepLink")
}
```

### Rich Notifications

```swift
class NotificationService: UNNotificationServiceExtension {
    func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
    ) {
        guard let content = request.content.mutableCopy() as? UNMutableNotificationContent,
              let imageURL = request.content.userInfo["image_url"] as? String else {
            contentHandler(request.content)
            return
        }
        
        // Download and attach image
        downloadImage(from: imageURL) { image in
            if let attachment = image {
                content.attachments = [attachment]
            }
            contentHandler(content)
        }
    }
    
    private func downloadImage(from urlString: String, completion: @escaping (UNNotificationAttachment?) -> Void) {
        guard let url = URL(string: urlString) else {
            completion(nil)
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, _, _ in
            guard let data,
                  let temporaryURL = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".jpg") else {
                completion(nil)
                return
            }
            
            try? data.write(to: temporaryURL)
            let attachment = try? UNNotificationAttachment(identifier: "", url: temporaryURL)
            completion(attachment)
        }.resume()
    }
}
```

---

## 6. Siri & Shortcuts Deep Links

### App Intents with Deep Links

```swift
import AppIntents

struct OpenProfileIntent: AppIntent {
    static var title: LocalizedStringResource = "Open Profile"
    static var description = IntentDescription("Opens a user's profile")
    
    @Parameter(title: "User ID")
    var userId: String
    
    func perform() async throws -> some IntentResult & OpensIntent {
        let link = DeepLink.profile(userId: userId)
        return .result(opensIntent: link)
    }
}
```

### Spotlight Indexing

```swift
class SpotlightIndexer {
    func indexPost(_ post: Post) {
        let attributeSet = CSSearchableItemAttributeSet(contentType: .content)
        attributeSet.title = post.title
        attributeSet.contentDescription = post.summary
        attributeSet.thumbnailURL = URL(string: post.imageURL)
        attributeSet.keywords = post.tags
        
        let item = CSSearchableItem(
            uniqueIdentifier: "post-\(post.id)",
            domainIdentifier: "com.app.posts",
            attributeSet: attributeSet
        )
        
        CSSearchableIndex.default().indexSearchableItems([item]) { error in
            if let error {
                print("Indexing error: \(error)")
            }
        }
    }
    
    func handleSpotlightDeepLink(activity: NSUserActivity) {
        guard activity.activityType == CSSearchableItemActivityType,
              let identifier = activity.contentAttributeSet?.relatedUniqueIdentifier else {
            return
        }
        
        // Parse identifier and navigate
        if identifier.hasPrefix("post-") {
            let postId = String(identifier.dropFirst(5))
            // Navigate to post
        }
    }
}
```

---

## 7. Testing Deep Links

### Test URLs

```swift
// Debug menu or test target
struct DeepLinkTestView: View {
    let router: DeepLinkRouter
    
    var body: some View {
        List {
            Section("Universal Links") {
                Button("myapp.com/profile?id=123") {
                    router.navigate(to: .profile(userId: "123"))
                }
                Button("myapp.com/post?id=abc") {
                    router.navigate(to: .post(id: "abc"))
                }
            }
            
            Section("Custom Schemes") {
                Button("myapp://settings") {
                    router.navigate(to: .settings)
                }
                Button("myapp://search?q=test") {
                    router.navigate(to: .search(query: "test"))
                }
            }
        }
        .navigationTitle("Test Deep Links")
    }
}
```

### Universal Links Testing

```bash
# Test universal links from terminal
xcrun simctl openurl "https://myapp.com/post?id=123"

# Test custom scheme
xcrun simctl openurl "myapp://profile?id=123"

# Or from Xcode
# Product → Scheme → Edit Scheme → Options → URL to open
```

---

## Decision Guide

| Entry Point | Use This |
|-------------|----------|
| Website → App | Universal Links |
| Email/QR → App | Custom URL Scheme |
| Widget tap → App | Link destination |
| Push notification tap | Deep link payload |
| Siri/Shortcuts | App Intents |
| Spotlight search | NSUserActivity |
| Another app → Your app | Custom URL Scheme |

---

## Pitfalls

1. **Don't** use ambiguous URL schemes — pick a unique scheme
2. **Don't** forget to test universal links with apple-app-site-association
3. **Don't** deep link to screens that require auth without checking auth first
4. **Don't** assume the app is running — handle cold start
5. **Don't** forget to handle invalid deep links gracefully
