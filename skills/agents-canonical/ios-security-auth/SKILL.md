---
name: ios-security-auth
description: "Skill: ios-security-auth"
---

# Skill: ios-security-auth

Unified iOS security and authentication skill. Use this instead of juggling authentication, swift-security, cryptokit, device-integrity, and cryptotokenkit separately.

## When to Use

- Implementing Sign in with Apple or passkeys
- Storing credentials in Keychain
- Encrypting/decrypting data
- Verifying device authenticity
- Certificate pinning for API security
- Biometric authentication (Face ID / Touch ID)
- Smart card / NFC token integration

---

## Authentication Flows

### Sign in with Apple

```swift
import AuthenticationServices

struct SignInWithAppleButton: UIViewRepresentable {
    let onRequest: (ASAuthorizationAppleIDRequest) -> Void
    let onCompletion: (Result<ASAuthorization, Error>) -> Void
    
    func makeUIView(context: Context) -> ASAuthorizationAppleIDButton {
        let button = ASAuthorizationAppleIDButton(type: .signIn, style: .black)
        button.addTarget(context.coordinator, action: #selector(Coordinator.handleTap), for: .touchUpInside)
        return button
    }
    
    func updateUIView(_ uiView: ASAuthorizationAppleIDButton, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(onRequest: onRequest, onCompletion: onCompletion)
    }
    
    class Coordinator: NSObject {
        let onRequest: (ASAuthorizationAppleIDRequest) -> Void
        let onCompletion: (Result<ASAuthorization, Error>) -> Void
        
        init(onRequest: @escaping (ASAuthorizationAppleIDRequest) -> Void,
             onCompletion: @escaping (Result<ASAuthorization, Error>) -> Void) {
            self.onRequest = onRequest
            self.onCompletion = onCompletion
        }
        
        @objc func handleTap() {
            let provider = ASAuthorizationAppleIDProvider()
            let request = provider.createRequest()
            request.requestedScopes = [.fullName, .email]
            onRequest(request)
            
            let controller = ASAuthorizationController(authorizationRequests: [request])
            controller.delegate = self
            controller.presentationContextProvider = self
            controller.performRequests()
        }
    }
}

extension SignInWithAppleButton.Coordinator: ASAuthorizationControllerDelegate {
    func authorizationController(controller: ASAuthorizationController,
                                 didCompleteWithAuthorization authorization: ASAuthorization) {
        guard let credential = authorization.credential as? ASAuthorizationAppleIDCredential else { return }
        
        let userId = credential.user
        let email = credential.email
        let fullName = credential.fullName
        let identityToken = credential.identityToken
        
        // Send identityToken to your server for verification
        onCompletion(.success(authorization))
    }
    
    func authorizationController(controller: ASAuthorizationController,
                                 didCompleteWithError error: Error) {
        onCompletion(.failure(error))
    }
}

extension SignInWithAppleButton.Coordinator: ASAuthorizationControllerPresentationContextProviding {
    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        UIApplication.shared.windows.first!
    }
}
```

### Passkey / WebAuthn

```swift
import AuthenticationServices

class PasskeyManager: NSObject {
    func createPasskey() async throws -> ASAuthorizationPlatformPublicKeyCredential {
        let challenge = Data("server-challenge".utf8)  // From your server
        
        let request = ASAuthorizationPlatformPublicKeyCredentialProvider()
            .createCredentialRegistrationRequest(
                challenge: challenge,
                name: "user@example.com",
                userID: "user-id".data(using: .utf8)!
            )
        
        let controller = ASAuthorizationController(authorizationRequests: [request])
        let result = try await controller.performRequests()
        
        guard let credential = result.credential as? ASAuthorizationPlatformPublicKeyCredential else {
            throw PasskeyError.invalidCredential
        }
        
        return credential
    }
    
    func signInWithPasskey() async throws -> ASAuthorizationPlatformPublicKeyCredential {
        let challenge = Data("server-challenge".utf8)
        
        let request = ASAuthorizationPlatformPublicKeyCredentialProvider()
            .createCredentialAssertionRequest(challenge: challenge)
        
        let controller = ASAuthorizationController(authorizationRequests: [request])
        let result = try await controller.performRequests()
        
        guard let credential = result.credential as? ASAuthorizationPlatformPublicKeyCredential else {
            throw PasskeyError.invalidCredential
        }
        
        return credential
    }
}

enum PasskeyError: Error {
    case invalidCredential
    case userCancelled
    case noCredentialsAvailable
}
```

### Biometric Authentication

```swift
import LocalAuthentication

class BiometricAuthManager {
    func authenticate(reason: String) async throws -> Bool {
        let context = LAContext()
        context.localizedCancelTitle = "Use Passcode"
        
        var error: NSError?
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            throw BiometricError.notAvailable(error?.localizedDescription ?? "Biometrics not available")
        }
        
        return try await withCheckedThrowingContinuation { continuation in
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                                   localizedReason: reason) { success, error in
                if let error {
                    continuation.resume(throwing: BiometricError.authenticationFailed(error))
                } else {
                    continuation.resume(returning: success)
                }
            }
        }
    }
    
    func biometricType() -> BiometricType {
        let context = LAContext()
        var error: NSError?
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            return .none
        }
        
        switch context.biometryType {
        case .faceID: return .faceID
        case .touchID: return .touchID
        case .opticID: return .opticID
        @unknown default: return .none
        }
    }
}

enum BiometricType {
    case none, faceID, touchID, opticID
}

enum BiometricError: Error {
    case notAvailable(String)
    case authenticationFailed(Error)
    case cancelled
}
```

---

## Keychain

### Basic CRUD

```swift
class KeychainManager {
    static let shared = KeychainManager()
    
    func save(_ data: Data, for key: String, service: String = Bundle.main.bundleIdentifier!) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)  // Delete existing
        
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.saveFailed(status)
        }
    }
    
    func save(_ string: String, for key: String, service: String = Bundle.main.bundleIdentifier!) throws {
        guard let data = string.data(using: .utf8) else {
            throw KeychainError.invalidData
        }
        try save(data, for: key, service: service)
    }
    
    func load(for key: String, service: String = Bundle.main.bundleIdentifier!) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
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
    
    func loadString(for key: String, service: String = Bundle.main.bundleIdentifier!) throws -> String {
        let data = try load(for: key, service: service)
        guard let string = String(data: data, encoding: .utf8) else {
            throw KeychainError.invalidData
        }
        return string
    }
    
    func delete(for key: String, service: String = Bundle.main.bundleIdentifier!) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.deleteFailed(status)
        }
    }
    
    func update(_ data: Data, for key: String, service: String = Bundle.main.bundleIdentifier!) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]
        
        let attributes: [String: Any] = [
            kSecValueData as String: data
        ]
        
        let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        guard status == errSecSuccess else {
            throw KeychainError.updateFailed(status)
        }
    }
}

enum KeychainError: Error {
    case saveFailed(OSStatus)
    case loadFailed(OSStatus)
    case updateFailed(OSStatus)
    case deleteFailed(OSStatus)
    case invalidData
}
```

### Keychain with Biometric Protection

```swift
func saveWithBiometric(_ data: Data, for key: String) throws {
    let accessControl = SecAccessControlCreateWithFlags(
        kCFAllocatorDefault,
        kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
        [.biometryCurrentSet, .privateKeyUsage],
        nil
    )!
    
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: Bundle.main.bundleIdentifier!,
        kSecAttrAccount as String: key,
        kSecValueData as String: data,
        kSecAttrAccessControl as String: accessControl
    ]
    
    SecItemDelete(query as CFDictionary)
    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else { throw KeychainError.saveFailed(status) }
}
```

---

## Cryptography

### Hashing

```swift
import CryptoKit

// SHA-256
let data = Data("hello".utf8)
let hash = SHA256.hash(data: data)
let hashString = hash.map { String(format: "%02x", $0) }.joined()

// SHA-3
let sha3Hash = SHA3_256.hash(data: data)

// HMAC
let key = SymmetricKey(size: .bits256)
let signature = HMAC<SHA256>.authenticationCode(for: data, using: key)
```

### Encryption

```swift
import CryptoKit

// AES-GCM Encryption
func encrypt(_ plaintext: Data, using key: SymmetricKey) throws -> Data {
    let sealedBox = try AES.GCM.seal(plaintext, using: key)
    return sealedBox.combined!
}

func decrypt(_ ciphertext: Data, using key: SymmetricKey) throws -> Data {
    let sealedBox = try AES.GCM.SealedBox(combined: ciphertext)
    return try AES.GCM.open(sealedBox, using: key)
}

// ChaChaPoly Encryption (faster on devices without AES hardware)
func encryptChaCha(_ plaintext: Data, using key: SymmetricKey) throws -> Data {
    let sealedBox = try ChaChaPoly.seal(plaintext, using: key)
    return sealedBox.combined!
}
```

### Key Agreement

```swift
import CryptoKit

// ECDH Key Agreement
func performKeyAgreement() throws -> SymmetricKey {
    let privateKey = P256.KeyAgreement.PrivateKey()
    let publicKey = privateKey.publicKey
    
    // Exchange publicKey with server
    let serverPublicKey = try P256.KeyAgreement.PublicKey(x963Representation: serverKeyData)
    
    let sharedSecret = try privateKey.sharedSecretFromKeyAgreement(with: serverPublicKey)
    let symmetricKey = sharedSecret.hkdfDerivedSymmetricKey(
        using: SHA256.self,
        salt: Data(),
        sharedInfo: "app-context".data(using: .utf8)!,
        outputByteCount: 32
    )
    
    return symmetricKey
}
```

### Digital Signatures

```swift
import CryptoKit

// Sign
let privateKey = P256.Signing.PrivateKey()
let signature = try privateKey.signature(for: data)

// Verify
let publicKey = privateKey.publicKey
let isValid = publicKey.isValidSignature(signature, for: data)
```

---

## Device Integrity

### DeviceCheck

```swift
import DeviceCheck

class DeviceIntegrityManager {
    func generateToken() async throws -> Data {
        try await withCheckedThrowingContinuation { continuation in
            DCDevice.current.generateToken { token, error in
                if let error {
                    continuation.resume(throwing: error)
                } else if let token {
                    continuation.resume(returning: token)
                } else {
                    continuation.resume(throwing: DeviceError.noToken)
                }
            }
        }
    }
    
    func isSupported() -> Bool {
        DCDevice.current.isSupported
    }
}

enum DeviceError: Error {
    case noToken
    case notSupported
}
```

### App Attest

```swift
import DeviceCheck

class AppAttestManager {
    private let service = DCAppAttestService.shared
    
    func attest() async throws -> Attestation {
        guard service.isSupported else {
            throw AttestationError.notSupported
        }
        
        let keyId = try await service.generateKey()
        let clientDataHash = SHA256.hash(data: Data("attestation-challenge".utf8))
        let attestation = try await service.attestKey(keyId, clientDataHash: Data(clientDataHash))
        
        return Attestation(keyId: keyId, attestation: attestation)
    }
    
    func assert(keyId: String, challenge: Data) async throws -> Data {
        let clientDataHash = SHA256.hash(data: challenge)
        return try await service.generateAssertion(keyId, clientDataHash: Data(clientDataHash))
    }
}

struct Attestation {
    let keyId: String
    let attestation: Data
}

enum AttestationError: Error {
    case notSupported
    case keyGenerationFailed
    case attestationFailed
}
```

### Server-Side Verification

```swift
// Server-side (Node.js example)
/*
const { jwtVerify } = require('jose');

async function verifyAttestation(attestation, keyId, challenge) {
  // Apple's root certificate
  const appleRootCA = await fetchAppleRootCA();
  
  // Verify the attestation chain
  // Validate the challenge matches
  // Store keyId for future assertions
  
  return { valid: true, keyId };
}

async function verifyAssertion(assertion, keyId, challenge) {
  // Verify the assertion against stored public key
  // Check challenge freshness
  // Validate counter against stored value
  
  return { valid: true };
}
*/
```

---

## Certificate Pinning

```swift
import Foundation

class PinningDelegate: NSObject, URLSessionDelegate {
    private let pinnedCertificates: [SecCertificate]
    
    init(pinnedCertificateNames: [String]) {
        self.pinnedCertificates = pinnedCertificateNames.compactMap { name in
            guard let url = Bundle.main.url(forResource: name, withExtension: "cer"),
                  let data = try? Data(contentsOf: url),
                  let cert = SecCertificateCreateWithData(nil, data as CFData) else {
                return nil
            }
            return cert
        }
        super.init()
    }
    
    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust,
              let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        // Check if server certificate matches pinned certificate
        for pinnedCert in pinnedCertificates {
            if SecCertificateCopyData(certificate) as Data == SecCertificateCopyData(pinnedCert) as Data {
                completionHandler(.useCredential, URLCredential(trust: serverTrust))
                return
            }
        }
        
        // Pinning failed
        completionHandler(.cancelAuthenticationChallenge, nil)
    }
}

// Usage
let delegate = PinningDelegate(pinnedCertificateNames: ["my-server-cert"])
let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: nil)
```

---

## Security Checklist

### Before Release

- [ ] All API calls use HTTPS
- [ ] Certificate pinning implemented for sensitive endpoints
- [ ] Keychain used for all credential storage (never UserDefaults)
- [ ] Biometric auth has fallback to passcode
- [ ] Sensitive data encrypted at rest
- [ ] No secrets hardcoded in source code
- [ ] App Attest / DeviceCheck for fraud prevention
- [ ] Sign in with Apple implemented (required if offering social login)
- [ ] Privacy manifest includes all required reason APIs
- [ ] No sensitive data in logs or analytics

### Common Mistakes

```swift
// BAD: Storing tokens in UserDefaults
UserDefaults.standard.set(token, forKey: "authToken")

// GOOD: Storing in Keychain
try KeychainManager.shared.save(token, for: "authToken")

// BAD: Hardcoding API keys
let apiKey = "sk-1234567890"

// GOOD: Using environment variables or config
let apiKey = ProcessInfo.processInfo.environment["API_KEY"]!

// BAD: Logging sensitive data
print("User token: \(token)")

// GOOD: Redacted logging
print("User token: \(String(repeating: "*", count: 8))")
```

---

## Decision Guide

| Need | Use This |
|------|----------|
| Social login | Sign in with Apple (required if any social login) |
| Passwordless | Passkeys / WebAuthn |
| Simple auth | Biometric + Keychain |
| API security | Certificate pinning + token in Keychain |
| Device fraud | App Attest + DeviceCheck |
| Data encryption | AES-GCM (most devices) or ChaChaPoly |
| Key exchange | ECDH with P256 |
| Password storage | Argon2 or bcrypt (server-side, never client) |
