---
name: ios-camera-ar-pipeline
description: "Skill: ios-camera-ar-pipeline"
---

# Skill: ios-camera-ar-pipeline

End-to-end camera workflows for iOS. Combines photokit, realitykit, vision-framework, core-motion, and core-nfc into complete pipelines for capturing, processing, analyzing, and storing camera data.

## When to Use

- Build a camera app with filters or effects
- Scan documents or barcodes
- Create AR experiences with camera passthrough
- Process images with AI/ML models
- Read NFC tags and display camera content
- Motion-triggered camera actions

---

## Pipeline Overview

```
Capture → Process → Analyze → Store → Share
   │          │          │         │        │
   ▼          ▼          ▼         ▼        ▼
AVCapture  Filters    Vision    Photos   UIActivity
Session    Effects    CoreML    Library  ViewController
```

---

## 1. Camera Capture

### Basic Camera Session

```swift
import AVFoundation
import SwiftUI

struct CameraView: UIViewControllerRepresentable {
    let session: AVCaptureSession
    
    func makeUIViewController(context: Context) -> CameraViewController {
        let vc = CameraViewController()
        vc.session = session
        return vc
    }
    
    func updateUIViewController(_ uiViewController: CameraViewController, context: Context) {}
}

class CameraViewController: UIViewController {
    var session: AVCaptureSession!
    private var previewLayer: AVCaptureVideoPreviewLayer!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
    }
    
    private func setupCamera() {
        session = AVCaptureSession()
        session.sessionPreset = .photo
        
        guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: camera) else { return }
        
        session.addInput(input)
        
        previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.videoGravity = .resizeAspectFill
        previewLayer.frame = view.bounds
        view.layer.addSublayer(previewLayer)
        
        session.startRunning()
    }
}
```

### Photo Capture

```swift
class PhotoCapture: NSObject, AVCapturePhotoCaptureDelegate {
    private let output = AVCapturePhotoOutput()
    var photoCompletion: ((Result<UIImage, Error>) -> Void)?
    
    func capturePhoto(session: AVCaptureSession) {
        guard session.canAddOutput(output) else { return }
        session.addOutput(output)
        
        let settings = AVCapturePhotoSettings()
        settings.flashMode = .auto
        settings.isHighResolutionPhotoEnabled = true
        
        output.capturePhoto(with: settings, delegate: self)
    }
    
    func photoOutput(_ output: AVCapturePhotoOutput,
                     didFinishProcessingPhoto photo: AVCapturePhoto,
                     error: Error?) {
        if let error {
            photoCompletion?(.failure(error))
            return
        }
        
        guard let data = photo.fileDataRepresentation(),
              let image = UIImage(data: data) else {
            photoCompletion?(.failure(CaptureError.invalidData))
            return
        }
        
        photoCompletion?(.success(image))
    }
    
    enum CaptureError: Error {
        case invalidData
        case noCamera
    }
}
```

### Video Recording

```swift
class VideoRecorder: NSObject, AVCaptureFileOutputRecordingDelegate {
    private let output = AVCaptureMovieFileOutput()
    private var recordingURL: URL?
    
    func startRecording(session: AVCaptureSession) {
        guard session.canAddOutput(output) else { return }
        session.addOutput(output)
        
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("recording_\(Date().timeIntervalSince1970).mov")
        recordingURL = url
        
        output.startRecording(to: url, recordingDelegate: self)
    }
    
    func stopRecording() {
        output.stopRecording()
    }
    
    func fileOutput(_ output: AVCaptureFileOutput,
                    didFinishRecordingTo outputFileURL: URL,
                    from connections: [AVCaptureConnection],
                    error: Error?) {
        if let error {
            print("Recording error: \(error)")
            return
        }
        
        // Video saved to outputFileURL
        UISaveVideoAtPathToSavedPhotosAlbum(outputFileURL.path, nil, nil, nil)
    }
}
```

---

## 2. Image Processing Pipeline

### Real-Time Filters

```swift
import CoreImage

class ImageFilterPipeline {
    private let context = CIContext(options: [.useSoftwareRenderer: false])
    
    func applyFilter(_ filter: CIFilter, to image: UIImage) -> UIImage? {
        guard let ciImage = CIImage(image: image) else { return nil }
        
        filter.setValue(ciImage, forKey: kCIInputImageKey)
        
        guard let outputImage = filter.outputImage,
              let cgImage = context.createCGImage(outputImage, from: outputImage.extent) else {
            return nil
        }
        
        return UIImage(cgImage: cgImage, scale: image.scale, orientation: image.imageOrientation)
    }
    
    // Common filters
    func applyVintage(to image: UIImage) -> UIImage? {
        let filter = CIFilter(name: "CIPhotoEffectProcess")!
        return applyFilter(filter, to: image)
    }
    
    func applyBloom(to image: UIImage, intensity: Float = 1.0) -> UIImage? {
        let filter = CIFilter(name: "CIBloom")!
        filter.setValue(intensity, forKey: kCIInputIntensityKey)
        return applyFilter(filter, to: image)
    }
    
    func applyPerspectiveCorrection(to image: UIImage, points: [CGPoint]) -> UIImage? {
        guard let ciImage = CIImage(image: image) else { return nil }
        
        let filter = CIFilter(name: "CIPerspectiveCorrection")!
        filter.setValue(ciImage, forKey: kCIInputImageKey)
        filter.setValue(CIVector(cgPoint: points[0]), forKey: "inputTopLeft")
        filter.setValue(CIVector(cgPoint: points[1]), forKey: "inputTopRight")
        filter.setValue(CIVector(cgPoint: points[2]), forKey: "inputBottomRight")
        filter.setValue(CIVector(cgPoint: points[3]), forKey: "inputBottomLeft")
        
        guard let outputImage = filter.outputImage,
              let cgImage = context.createCGImage(outputImage, from: outputImage.extent) else {
            return nil
        }
        
        return UIImage(cgImage: cgImage)
    }
}
```

### Document Detection & Crop

```swift
import Vision

class DocumentDetector {
    func detectDocument(in image: UIImage) async throws -> DetectedDocument? {
        guard let cgImage = image.cgImage else { return nil }
        
        return try await withCheckedThrowingContinuation { continuation in
            let request = VNDetectRectanglesRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                guard let results = request.results as? [VNRectangleObservation],
                      let largest = results.max(by: { $0.area < $1.area }) else {
                    continuation.resume(returning: nil)
                    return
                }
                
                let document = DetectedDocument(
                    topLeft: largest.topLeft,
                    topRight: largest.topRight,
                    bottomLeft: largest.bottomLeft,
                    bottomRight: largest.bottomRight,
                    confidence: largest.confidence
                )
                
                continuation.resume(returning: document)
            }
            
            request.minimumAspectRatio = 0.3
            request.maximumAspectRatio = 1.0
            request.minimumSize = 0.2
            request.maximumObservations = 1
            
            let handler = VNImageRequestHandler(cgImage: cgImage)
            try? handler.perform([request])
        }
    }
    
    func cropDocument(_ image: UIImage, document: DetectedDocument) -> UIImage? {
        // Use perspective correction to straighten
        let pipeline = ImageFilterPipeline()
        let points = [
            CGPoint(x: document.topLeft.x * image.size.width, y: document.topLeft.y * image.size.height),
            CGPoint(x: document.topRight.x * image.size.width, y: document.topRight.y * image.size.height),
            CGPoint(x: document.bottomRight.x * image.size.width, y: document.bottomRight.y * image.size.height),
            CGPoint(x: document.bottomLeft.x * image.size.width, y: document.bottomLeft.y * image.size.height)
        ]
        return pipeline.applyPerspectiveCorrection(to: image, points: points)
    }
}

struct DetectedDocument {
    let topLeft: CGPoint
    let topRight: CGPoint
    let bottomLeft: CGPoint
    let bottomRight: CGPoint
    let confidence: Float
    
    var area: Float {
        // Calculate area from points
        let width = hypot(topRight.x - topLeft.x, topRight.y - topLeft.y)
        let height = hypot(bottomLeft.x - topLeft.x, bottomLeft.y - topLeft.y)
        return width * height
    }
}
```

---

## 3. Vision Analysis

### Complete Image Analysis

```swift
import Vision

class ImageAnalyzer {
    func analyze(_ image: UIImage) async throws -> ImageAnalysis {
        guard let cgImage = image.cgImage else {
            throw AnalysisError.invalidImage
        }
        
        async let text = recognizeText(in: cgImage)
        async let faces = detectFaces(in: cgImage)
        async let barcodes = detectBarcodes(in: cgImage)
        async let objects = classifyObjects(in: cgImage)
        
        let (recognizedText, detectedFaces, detectedBarcodes, classifiedObjects) = try await (text, faces, barcodes, objects)
        
        return ImageAnalysis(
            text: recognizedText,
            faces: detectedFaces,
            barcodes: detectedBarcodes,
            objects: classifiedObjects
        )
    }
    
    private func recognizeText(in image: CGImage) async throws -> [RecognizedText] {
        try await withCheckedThrowingContinuation { continuation in
            let request = VNRecognizeTextRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                let results = (request.results as? [VNRecognizedTextObservation])?.compactMap { obs in
                    obs.topCandidates(1).first.map { candidate in
                        RecognizedText(
                            text: candidate.string,
                            confidence: candidate.confidence,
                            boundingBox: obs.boundingBox
                        )
                    }
                } ?? []
                
                continuation.resume(returning: results)
            }
            
            request.recognitionLevel = .accurate
            let handler = VNImageRequestHandler(cgImage: image)
            try? handler.perform([request])
        }
    }
    
    private func detectFaces(in image: CGImage) async throws -> [DetectedFace] {
        try await withCheckedThrowingContinuation { continuation in
            let request = VNDetectFaceLandmarksRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                let results = (request.results as? [VNFaceObservation])?.map { face in
                    DetectedFace(
                        boundingBox: face.boundingBox,
                        landmarks: face.landmarks,
                        confidence: face.confidence
                    )
                } ?? []
                
                continuation.resume(returning: results)
            }
            
            let handler = VNImageRequestHandler(cgImage: image)
            try? handler.perform([request])
        }
    }
    
    private func detectBarcodes(in image: CGImage) async throws -> [ScannedBarcode] {
        try await withCheckedThrowingContinuation { continuation in
            let request = VNDetectBarcodesRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                let results = (request.results as? [VNBarcodeObservation])?.map { barcode in
                    ScannedBarcode(
                        payload: barcode.payloadStringValue ?? "",
                        type: barcode.symbology.rawValue,
                        boundingBox: barcode.boundingBox
                    )
                } ?? []
                
                continuation.resume(returning: results)
            }
            
            let handler = VNImageRequestHandler(cgImage: image)
            try? handler.perform([request])
        }
    }
    
    private func classifyObjects(in image: CGImage) async throws -> [ClassifiedObject] {
        try await withCheckedThrowingContinuation { continuation in
            let request = VNClassifyImageRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                let results = (request.results as? [VNClassificationObservation])?.prefix(5).map { classification in
                    ClassifiedObject(
                        label: classification.identifier,
                        confidence: classification.confidence
                    )
                } ?? []
                
                continuation.resume(returning: results)
            }
            
            let handler = VNImageRequestHandler(cgImage: image)
            try? handler.perform([request])
        }
    }
}

struct ImageAnalysis {
    let text: [RecognizedText]
    let faces: [DetectedFace]
    let barcodes: [ScannedBarcode]
    let objects: [ClassifiedObject]
}

struct RecognizedText {
    let text: String
    let confidence: Float
    let boundingBox: CGRect
}

struct DetectedFace {
    let boundingBox: CGRect
    let landmarks: VNFaceLandmarks?
    let confidence: Float
}

struct ScannedBarcode {
    let payload: String
    let type: String
    let boundingBox: CGRect
}

struct ClassifiedObject {
    let label: String
    let confidence: Float
}

enum AnalysisError: Error {
    case invalidImage
}
```

---

## 4. AR Experiences

### Basic AR View

```swift
import RealityKit
import ARKit

struct ARExperienceView: UIViewRepresentable {
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Start AR session
        let config = ARWorldTrackingConfiguration()
        config.planeDetection = [.horizontal, .vertical]
        config.environmentTexturing = .automatic
        
        arView.session.run(config)
        
        // Add coaching overlay
        let coachingOverlay = ARCoachingOverlayView()
        coachingOverlay.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        coachingOverlay.session = arView.session
        coachingOverlay.goal = .horizontalPlane
        arView.addSubview(coachingOverlay)
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {}
}
```

### Place 3D Object

```swift
extension ARView {
    func placeObject(named name: String, at position: SIMD3<Float>) {
        let entity = try? Entity.load(named: name)
        
        let anchor = AnchorEntity(plane: .horizontal)
        anchor.position = position
        anchor.addChild(entity!)
        
        self.scene.addAnchor(anchor)
    }
    
    func placeObjectAtCenter() {
        guard let query = self.makeRaycastQuery(
            from: self.center,
            allowing: .estimatedPlane,
            alignment: .horizontal
        ) else { return }
        
        guard let result = self.raycast(from: self.center, using: query).first else { return }
        
        let position = SIMD3<Float>(
            result.worldTransform.columns.3.x,
            result.worldTransform.columns.3.y,
            result.worldTransform.columns.3.z
        )
        
        placeObject(named: "Cube", at: position)
    }
}
```

### Gesture Interaction

```swift
extension ARExperienceView {
    func setupGestures(_ arView: ARView) {
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap))
        arView.addGestureRecognizer(tapGesture)
        
        let panGesture = UIPanGestureRecognizer(target: self, action: #selector(handlePan))
        arView.addGestureRecognizer(panGesture)
        
        let pinchGesture = UIPinchGestureRecognizer(target: self, action: #selector(handlePinch))
        arView.addGestureRecognizer(pinchGesture)
    }
    
    @objc func handleTap(_ gesture: UITapGestureRecognizer) {
        let location = gesture.location(in: gesture.view)
        guard let arView = gesture.view as? ARView else { return }
        
        let results = arView.raycast(from: location, allowing: .estimatedPlane, alignment: .horizontal)
        if let first = results.first {
            let position = SIMD3<Float>(
                first.worldTransform.columns.3.x,
                first.worldTransform.columns.3.y,
                first.worldTransform.columns.3.z
            )
            arView.placeObject(named: "Object", at: position)
        }
    }
    
    @objc func handlePan(_ gesture: UIPanGestureRecognizer) {
        // Move object
    }
    
    @objc func handlePinch(_ gesture: UIPinchGestureRecognizer) {
        // Scale object
    }
}
```

---

## 5. NFC + Camera

### NFC Tag Reading with Camera Preview

```swift
import CoreNFC
import AVFoundation

class NFCCameraReader: NSObject, NFCTagReaderSessionDelegate {
    private var session: NFCTagReaderSession?
    private var cameraSession: AVCaptureSession?
    
    func startReading() {
        guard NFCTagReaderSession.readingAvailable else { return }
        
        session = NFCTagReaderSession(pollingOption: [.iso14443, .iso15693], delegate: self)
        session?.alertMessage = "Hold your iPhone near the NFC tag"
        session?.begin()
    }
    
    func tagReaderSession(_ session: NFCTagReaderSession, didDetect tags: [NFCTag]) {
        for tag in tags {
            if case .iso7816(let iso7816Tag) = tag {
                let data = iso7816Tag.initialSelectedAID
                
                // Process NFC data
                processNFCData(data, session: session)
            }
        }
    }
    
    func tagReaderSessionDidBecomeActive(_ session: NFCTagReaderSession) {
        // Session became active, could show camera preview
    }
    
    func tagReaderSession(_ session: NFCTagReaderSession, didInvalidateWithError error: Error) {
        // Session ended
    }
    
    private func processNFCData(_ data: Data, session: NFCTagReaderSession) {
        // Analyze NFC data and trigger camera action
        if let urlString = String(data: data, encoding: .utf8),
           let url = URL(string: urlString) {
            // Open camera with NFC context
            NotificationCenter.default.post(
                name: .nfcTagDetected,
                object: nil,
                userInfo: ["url": url]
            )
        }
        
        session.invalidate()
    }
}

extension Notification.Name {
    static let nfcTagDetected = Notification.Name("nfcTagDetected")
}
```

---

## 6. Motion-Triggered Camera

```swift
import CoreMotion

class MotionCameraTrigger: ObservableObject {
    private let motionManager = CMMotionManager()
    @DeviceMotion var deviceMotion
    
    func startMonitoring() {
        guard motionManager.isDeviceMotionAvailable else { return }
        
        motionManager.deviceMotionUpdateInterval = 0.1
        motionManager.startDeviceMotionUpdates(to: .main) { motion, error in
            guard let motion else { return }
            
            // Detect specific motions
            if abs(motion.userAcceleration.z) > 2.0 {
                // Strong shake detected - trigger camera
                NotificationCenter.default.post(name: .motionTriggeredCamera, object: nil)
            }
            
            if motion.attitude.pitch > .pi / 4 {
                // Phone tilted up - switch to front camera
                NotificationCenter.default.post(
                    name: .switchCamera,
                    object: nil,
                    userInfo: ["position": AVCaptureDevice.Position.front]
                )
            }
        }
    }
    
    func stopMonitoring() {
        motionManager.stopDeviceMotionUpdates()
    }
}

extension Notification.Name {
    static let motionTriggeredCamera = Notification.Name("motionTriggeredCamera")
    static let switchCamera = Notification.Name("switchCamera")
}
```

---

## Complete Pipeline Example

```swift
class CameraPipeline: ObservableObject {
    private let captureSession = AVCaptureSession()
    private let photoOutput = AVCapturePhotoOutput()
    private let filterPipeline = ImageFilterPipeline()
    private let analyzer = ImageAnalyzer()
    private let documentDetector = DocumentDetector()
    
    @Published var lastCapture: UIImage?
    @Published var analysisResult: ImageAnalysis?
    @Published var isProcessing = false
    
    func captureAndAnalyze() async {
        isProcessing = true
        
        // 1. Capture
        guard let image = await capturePhoto() else {
            isProcessing = false
            return
        }
        
        // 2. Detect document
        if let document = try? await documentDetector.detectDocument(in: image),
           document.confidence > 0.8 {
            // 3. Crop and straighten
            if let cropped = documentDetector.cropDocument(image, document: document) {
                lastCapture = cropped
                
                // 4. Analyze content
                analysisResult = try? await analyzer.analyze(cropped)
            }
        } else {
            lastCapture = image
            analysisResult = try? await analyzer.analyze(image)
        }
        
        // 5. Save to Photos Library
        if let lastCapture {
            UIImageWriteToSavedPhotosAlbum(lastCapture, nil, nil, nil)
        }
        
        isProcessing = false
    }
    
    private func capturePhoto() async -> UIImage? {
        await withCheckedContinuation { continuation in
            let settings = AVCapturePhotoSettings()
            photoOutput.capturePhoto(with: settings, delegate: PhotoCaptureDelegate { result in
                continuation.resume(returning: try? result.get())
            })
        }
    }
}
```

---

## Decision Guide

| Need | Components |
|------|------------|
| Simple photo capture | AVCaptureSession + AVCapturePhotoOutput |
| Video recording | AVCaptureMovieFileOutput |
| Document scanning | Vision VNDetectRectangles + CIPerspectiveCorrection |
| Barcode reading | Vision VNDetectBarcodesRequest |
| AR placement | RealityKit + ARKit |
| NFC-triggered camera | CoreNFC + NotificationCenter |
| Motion-triggered | CoreMotion + AVCaptureSession |
| Image analysis | Vision + CoreML |
