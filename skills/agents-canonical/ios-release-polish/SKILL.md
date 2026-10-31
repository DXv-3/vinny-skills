---
name: ios-release-polish
description: "Skill: ios-release-polish"
---

# Skill: ios-release-polish

iOS app release and polish skill covering App Store submission, accessibility, localization, testing, and StoreKit. This is a NEW skill that consolidates ios-localization, ios-accessibility, swift-testing, and storekit into a unified pre-release workflow.

## When to Use

- Preparing app for App Store submission
- Adding multi-language support
- Auditing accessibility (VoiceOver, Dynamic Type)
- Writing and organizing tests
- Implementing in-app purchases or subscriptions
- Responding to App Store rejection
- Setting up TestFlight

---

## Pre-Release Checklist

```
□ All tests pass
□ Accessibility audit complete
□ Localization complete for all target languages
□ StoreKit products configured and tested
□ Privacy manifest added
□ App Store metadata prepared
□ Screenshots captured for all required sizes
□ App Clip configured (if applicable)
□ Push notifications configured
□ Background modes configured and tested
□ Deep links tested
□ Analytics verified
□ Crash reporting enabled
□ Performance profiling complete
```

---

## 1. Localization

### String Catalogs

```swift
// Localizable.xcstrings
// Use String Catalogs (Xcode 15+) instead of .strings files

struct ContentView: View {
    var body: some View {
        VStack {
            // Automatic string catalog lookup
            Text("Welcome")
            Text("settings.title")
            Text("item.count \(5)")
        }
    }
}

// With explicit catalog
Text("custom.key", table: "MyTable")
```

### Pluralization

```swift
// In String Catalog, add plural variations:
// "items.count" = {
//   "one": "%lld item",
//   "other": "%lld items"
// }

Text("items.count", tableName: "Localizable", comment: "")
    .localizedString(value: itemCount)

// Or use String.LocalizationValue
String(localized: "items.count \(itemCount)")
```

### RTL Support

```swift
// SwiftUI handles RTL automatically
// For specific alignment:
Text("Hello")
    .multilineTextAlignment(.leading)  // Flips in RTL

// For custom layouts:
HStack {
    if UIApplication.shared.userInterfaceLayoutDirection == .rightToLeft {
        Spacer()
        Image(systemName: "chevron.right")
    } else {
        Image(systemName: "chevron.left")
        Spacer()
    }
    Text("Back")
}

// Or use the environment value
@Environment(\.layoutDirection) var layoutDirection
```

### Locale-Aware Formatting

```swift
// Dates
let date = Date()
Text(date, style: .date)
Text(date, format: .dateTime.month(.wide).day())

// Numbers
let price = 9.99
Text(price, format: .currency(code: "USD"))

// Measurements
let distance = Measurement(value: 5.0, unit: UnitLength.kilometers)
Text(distance, format: .measurement(width: .abbreviated))
```

### Adding a Language

1. Project → Info → Localizations → Add Language
2. Choose "String Catalog" (recommended)
3. Use Xcode's "Export for Localization" to send to translators
4. Import translated `.xcloc` files

---

## 2. Accessibility

### VoiceOver Labels

```swift
Image(systemName: "star.fill")
    .accessibilityLabel("Favorite")

Text("Submit Order")
    .accessibilityHint("Double tap to place your order")

Button("Play") { }
    .accessibilityAddTraits(.isToggle)

// Group related elements
HStack {
    Image(systemName: "clock")
    Text("Duration: 5 minutes")
}
.accessibilityElement(children: .combine)
```

### Dynamic Type

```swift
// Use semantic fonts
Text("Title")
    .font(.headline)

Text("Body")
    .font(.body)

// Custom fonts that scale
Text("Custom")
    .font(.custom("MyFont", size: 17))  // Use fixed size, system scales it

// Test in: Settings → Developer → Larger Dynamic Type
```

### Accessibility Actions

```swift
Text("Swipe to delete")
    .accessibilityAction(.swipeDelete) {
        performDelete()
    }

Text("Custom action")
    .accessibilityAction(named: "Quick Edit") {
        enterEditMode()
    }
```

### Focus Management

```swift
struct FormView: View {
    @FocusState private var focusedField: Field?
    
    enum Field: Hashable {
        case name, email, password
    }
    
    var body: some View {
        Form {
            TextField("Name", text: $name)
                .focused($focusedField, equals: .name)
            TextField("Email", text: $email)
                .focused($focusedField, equals: .email)
            SecureField("Password", text: $password)
                .focused($focusedField, equals: .password)
        }
        .onSubmit {
            switch focusedField {
            case .name: focusedField = .email
            case .email: focusedField = .password
            default: break
            }
        }
    }
}
```

### Accessibility Audit Checklist

- [ ] All interactive elements have labels
- [ ] Images have meaningful alt text (or decorative images marked)
- [ ] Heading hierarchy is logical
- [ ] Color is not the only way to convey information
- [ ] Touch targets are at least 44x44 points
- [ ] Dynamic Type works at all sizes
- [ ] VoiceOver navigation order is logical
- [ ] Custom controls announce their state
- [ ] Animations respect Reduce Motion setting
- [ ] Contrast ratios meet WCAG AA (4.5:1 text, 3:1 large text)

### Test with Accessibility Inspector

1. Xcode → Open Developer Tool → Accessibility Inspector
2. Point at elements to verify labels and traits
3. Use "Audit" tab for automated checks
4. Test VoiceOver: Settings → Accessibility → VoiceOver

---

## 3. Testing

### Swift Testing

```swift
import Testing

@Suite("Feature Tests")
struct FeatureTests {
    @Test("Items load correctly")
    func loadItems() async throws {
        let sut = FeatureViewModel(service: MockService())
        await sut.load()
        #expect(sut.items.count == 5)
    }
    
    @Test("Empty state shows message")
    func emptyState() async throws {
        let sut = FeatureViewModel(service: MockService(items: []))
        await sut.load()
        #expect(sut.isEmpty == true)
    }
    
    @Test("Error shows alert")
    func errorState() async throws {
        let sut = FeatureViewModel(service: MockService(error: .networkError))
        await sut.load()
        #expect(sut.error != nil)
    }
}
```

### Parameterized Tests

```swift
@Test("URL validation", arguments: [
    ("https://example.com", true),
    ("http://example.com", true),
    ("ftp://example.com", false),
    ("not-a-url", false)
])
func validateURL(url: String, expected: Bool) {
    let result = URLValidator.isValid(url)
    #expect(result == expected)
}

@Test("Addition", arguments: [
    (1, 1, 2),
    (2, 3, 5),
    (0, 0, 0)
])
func addition(a: Int, b: Int, expected: Int) {
    #expect(a + b == expected)
}
```

### Mocking

```swift
protocol ItemServiceProtocol {
    func fetch() async throws -> [Item]
}

class MockItemService: ItemServiceProtocol {
    var items: [Item] = []
    var error: Error?
    
    func fetch() async throws -> [Item] {
        if let error { throw error }
        return items
    }
}

// In tests
let mock = MockItemService()
mock.items = [.mock1, .mock2]

let sut = FeatureViewModel(service: mock)
await sut.load()
#expect(sut.items.count == 2)
```

### Test Organization

```
Tests/
├── Unit/
│   ├── ViewModels/
│   ├── Models/
│   └── Services/
├── Integration/
│   ├── API/
│   └── Database/
├── UI/
│   └── Screenshots/
└── Mocks/
    └── MockServices.swift
```

---

## 4. StoreKit

### Product Fetching

```swift
import StoreKit

class StoreManager: ObservableObject {
    @Published var products: [Product] = []
    @Published var purchasedProductIDs: Set<String> = []
    
    let productIDs: Set<String> = [
        "com.app.premium",
        "com.app.monthly",
        "com.app.yearly"
    ]
    
    func loadProducts() async {
        do {
            products = try await Product.products(for: productIDs)
        } catch {
            print("Failed to load products: \(error)")
        }
    }
    
    func purchase(_ product: Product) async throws -> Transaction? {
        let result = try await product.purchase()
        
        switch result {
        case .success(let verification):
            let transaction = try checkVerified(verification)
            await updatePurchasedProducts()
            return transaction
        case .userCancelled:
            return nil
        case .pending:
            return nil
        @unknown default:
            return nil
        }
    }
    
    func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .verified(let safe):
            return safe
        case .unverified(_, let error):
            throw error
        }
    }
    
    func updatePurchasedProducts() async {
        for await result in Transaction.currentEntitlements {
            if case .verified(let transaction) = result {
                purchasedProductIDs.insert(transaction.productID)
            }
        }
    }
}
```

### Subscription Handling

```swift
class SubscriptionManager: ObservableObject {
    @Published var currentSubscription: Product?
    @Published var renewalDate: Date?
    
    func checkSubscriptionStatus() async {
        for await result in Transaction.currentEntitlements {
            if case .verified(let transaction) = result {
                if transaction.productType == .autoRenewable {
                    currentSubscription = try? await Product.products(for: [transaction.productID]).first
                    renewalDate = transaction.expirationDate
                }
            }
        }
    }
    
    func restorePurchases() async {
        for await result in Transaction.unfinished {
            if case .verified(let transaction) = result {
                await transaction.finish()
            }
        }
    }
}
```

### StoreKit Testing (Xcode)

1. File → New → File → StoreKit Configuration File
2. Add products matching your IDs
3. Edit Scheme → StoreKit Configuration → Select your file
4. Run and test purchases in Simulator

### Offer Codes & Promotions

```swift
// Present offer code redemption
func redeemOfferCode() async {
    do {
        try await AppStore.presentOfferRedemptionSheet()
    } catch {
        print("Redemption failed: \(error)")
    }
}

// Check for promotional offers
func checkPromotions(for product: Product) async -> [Product.PromotionOffer] {
    return product.promotionOffers
}
```

---

## 5. App Store Submission

### Required Metadata

- **App Name** (30 chars max)
- **Subtitle** (30 chars max)
- **Description** (4000 chars max)
- **Keywords** (100 chars max, comma-separated)
- **Support URL**
- **Marketing URL** (optional)
- **Privacy Policy URL**
- **App Icon** (1024x1024)
- **Screenshots** (required sizes per device)
- **App Clip URL** (if applicable)

### Screenshot Sizes

| Device | Size (pixels) |
|--------|---------------|
| iPhone 6.7" | 1290 × 2796 |
| iPhone 6.5" | 1284 × 2778 |
| iPhone 5.5" | 1242 × 2208 |
| iPad 12.9" | 2048 × 2732 |

### Privacy Manifest

Create `PrivacyInfo.xcprivacy` in your project:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyTrackingDomains</key>
    <array/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array/>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>CA92.1</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
```

### Common Rejection Reasons

| Reason | Fix |
|--------|-----|
| Crashes on launch | Test on clean install |
| Placeholder content | Remove all "Lorem ipsum" |
| Broken links | Verify all URLs work |
| Incomplete metadata | Fill all required fields |
| Privacy issues | Add privacy manifest, explain data usage |
| Guideline violations | Read App Store Review Guidelines |
| Payment issues | Ensure StoreKit is properly configured |
| Performance | Profile on oldest supported device |

### Response to Rejection

1. Read the rejection reason carefully
2. Fix the specific issue mentioned
3. Include in your response:
   - What you changed
   - Where to find the fix (build number)
   - Screenshots or video if helpful
   - Polite, professional tone

---

## 6. TestFlight

### Setup

1. Archive your app (Product → Archive)
2. Upload to App Store Connect
3. Go to TestFlight tab
4. Add internal testers (up to 100, no review)
5. Add external testers (up to 10,000, requires beta review)

### Beta Testing

```swift
// Check if running in TestFlight
var isTestFlight: Bool {
    let receiptURL = Bundle.main.appStoreReceiptURL
    return receiptURL?.lastPathComponent == "sandboxReceipt"
}

// Or check environment
#if DEBUG
    print("Debug build")
#elseif targetEnvironment(simulator)
    print("Simulator")
#else
    if isTestFlight {
        print("TestFlight build")
    } else {
        print("App Store build")
    }
#endif
```

### Beta Feedback

Configure feedback in App Store Connect:
- Add screenshot requirement
- Add feedback email
- Set up custom feedback form

---

## Decision Guide

| Task | Start Here |
|------|------------|
| New language support | String Catalogs section |
| VoiceOver audit | Accessibility checklist |
| In-app purchase | StoreKit product fetching |
| App rejection | Common rejections table |
| Beta testing | TestFlight setup |
| Privacy compliance | Privacy manifest section |
