---
name: ios-ai-integration
description: "Skill: ios-ai-integration"
---

# Skill: ios-ai-integration

Unified iOS AI and machine learning skill. Use this instead of juggling apple-on-device-ai, coreml, vision-framework, natural-language, and speech-recognition separately.

## When to Use

- Running on-device LLMs (Apple Intelligence, Core ML, MLX)
- Adding OCR, face detection, or barcode scanning
- Performing sentiment analysis or named entity recognition
- Transcribing speech to text
- Classifying images or objects
- Adding smart suggestions to your app

---

## On-Device AI Options

| Option | Best For | Requirements |
|--------|----------|--------------|
| **Apple Intelligence / Foundation Models** | Chat, summarization, generation | iOS 18+, Apple Silicon |
| **Core ML** | Custom model inference | iOS 11+, any model format |
| **MLX Swift** | Research, custom ML pipelines | macOS 14+, Apple Silicon |
| **llama.cpp** | Running open-source LLMs | iOS 16+, any device |

---

## 1. Apple Intelligence / Foundation Models

### System Language Model

```swift
import FoundationModels

struct ChatView: View {
    @State private var model = SystemLanguageModel.default
    @State private var messages: [Message] = []
    @State private var input = ""
    @State private var isGenerating = false
    
    var body: some View {
        VStack {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 12) {
                    ForEach(messages) { message in
                        MessageBubble(message: message)
                    }
                }
                .padding()
            }
            
            HStack {
                TextField("Ask something...", text: $input)
                    .textFieldStyle(.roundedBorder)
                
                Button {
                    Task { await send() }
                } label: {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title2)
                }
                .disabled(input.isEmpty || isGenerating)
            }
            .padding()
        }
    }
    
    func send() async {
        let userMessage = Message(content: input, isUser: true)
        messages.append(userMessage)
        input = ""
        isGenerating = true
        
        do {
            let session = LanguageModelSession()
            let response = try await session.respond(
                to: "User: \(userMessage.content)\nAssistant:"
            )
            let assistantMessage = Message(content: response.content, isUser: false)
            messages.append(assistantMessage)
        } catch {
            let errorMessage = Message(content: "Error: \(error.localizedDescription)", isUser: false)
            messages.append(errorMessage)
        }
        
        isGenerating = false
    }
}

struct Message: Identifiable {
    let id = UUID()
    let content: String
    let isUser: Bool
}
```

### Tool Calling

```swift
import FoundationModels

struct WeatherTool: Tool {
    let name = "getWeather"
    let description = "Get current weather for a location"
    
    @Tool var location: String
    
    func call() async throws -> String {
        // Call your weather API
        let weather = try await WeatherService.fetch(for: location)
        return "\(weather.temperature)°F, \(weather.condition)"
    }
}

// Usage
let session = LanguageModelSession(tools: [WeatherTool()])
let response = try await session.respond(
    to: "What's the weather in San Francisco?",
    tools: [WeatherTool()]
)
```

### Structured Output

```swift
import FoundationModels

struct Recipe: Codable {
    let name: String
    let ingredients: [String]
    let steps: [String]
    let prepTime: Int
}

let session = LanguageModelSession()
let recipe = try await session.respond(
    to: "Give me a recipe for chocolate chip cookies",
    as: Recipe.self
)

print(recipe.name)  // "Chocolate Chip Cookies"
print(recipe.ingredients)  // ["flour", "sugar", ...]
```

### Tips for Foundation Models

- Keep prompts concise — on-device models have smaller context windows
- Use `transcript` for multi-turn conversations
- Handle `LanguageModelSession.Error` gracefully
- Test on device — Simulator may not have Apple Intelligence

---

## 2. Core ML

### Load and Run a Model

```swift
import CoreML

class ImageClassifier {
    private let model: VNCoreMLModel
    
    init() throws {
        let config = MLModelConfiguration()
        config.computeUnits = .all  // Use CPU, GPU, and Neural Engine
        
        let mlModel = try MyImageClassifier(configuration: config)
        self.model = try VNCoreMLModel(for: mlModel.model)
    }
    
    func classify(_ image: CGImage) async throws -> ClassificationResult {
        return try await withCheckedThrowingContinuation { continuation in
            let request = VNCoreMLRequest(model: model) { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                guard let results = request.results as? [VNClassificationObservation],
                      let top = results.first else {
                    continuation.resume(throwing: ClassifierError.noResults)
                    return
                }
                
                continuation.resume(returning: ClassificationResult(
                    label: top.identifier,
                    confidence: top.confidence
                ))
            }
            
            let handler = VNImageRequestHandler(cgImage: image)
            try? handler.perform([request])
        }
    }
}

struct ClassificationResult {
    let label: String
    let confidence: Float
}
```

### Convert Python Model to Core ML

```python
# Using coremltools
import coremltools as ct
import torch

# Load PyTorch model
model = torch.load("model.pth")
model.eval()

# Trace the model
example_input = torch.randn(1, 3, 224, 224)
traced_model = torch.jit.trace(model, example_input)

# Convert to Core ML
mlmodel = ct.convert(
    traced_model,
    inputs=[ct.ImageType(name="image", shape=(1, 3, 224, 224))],
    classifier_config=ct.ClassifierConfig("labels.txt")
)

# Save
mlmodel.save("MyModel.mlpackage")
```

### Model Compression

```python
# Quantize for smaller model size
import coremltools as ct

model = ct.models.MLModel("MyModel.mlpackage")

# Quantize weights to FP16
quantized = ct.compression_utils.quantize_weights(model, nbits=16)
quantized.save("MyModelQuantized.mlpackage")

# Quantize to INT8
quantized_int8 = ct.compression_utils.quantize_weights(model, nbits=8)
quantized_int8.save("MyModelINT8.mlpackage")
```

### Compute Unit Selection

```swift
let config = MLModelConfiguration()

// Use all available compute units (recommended)
config.computeUnits = .all

// CPU only (for debugging)
config.computeUnits = .cpuOnly

// CPU and GPU
config.computeUnits = .cpuAndGPU

// CPU and Neural Engine
config.computeUnits = .cpuAndNeuralEngine
```

---

## 3. Vision Framework

### OCR (Text Recognition)

```swift
import Vision

class TextRecognizer {
    func recognizeText(in image: CGImage) async throws -> [RecognizedText] {
        return try await withCheckedThrowingContinuation { continuation in
            let request = VNRecognizeTextRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                let results = (request.results as? [VNRecognizedTextObservation])?.compactMap { observation in
                    observation.topCandidates(1).first.map { candidate in
                        RecognizedText(
                            text: candidate.string,
                            confidence: candidate.confidence,
                            boundingBox: observation.boundingBox
                        )
                    }
                } ?? []
                
                continuation.resume(returning: results)
            }
            
            request.recognitionLevel = .accurate
            request.usesLanguageCorrection = true
            
            let handler = VNImageRequestHandler(cgImage: image)
            try? handler.perform([request])
        }
    }
}

struct RecognizedText {
    let text: String
    let confidence: Float
    let boundingBox: CGRect
}
```

### Face Detection

```swift
import Vision

class FaceDetector {
    func detectFaces(in image: CGImage) async throws -> [DetectedFace] {
        return try await withCheckedThrowingContinuation { continuation in
            let request = VNDetectFaceLandmarksRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                let results = (request.results as? [VNFaceObservation])?.map { face in
                    DetectedFace(
                        boundingBox: face.boundingBox,
                        landmarks: face.landmarks,
                        roll: face.roll,
                        yaw: face.yaw
                    )
                } ?? []
                
                continuation.resume(returning: results)
            }
            
            let handler = VNImageRequestHandler(cgImage: image)
            try? handler.perform([request])
        }
    }
}

struct DetectedFace {
    let boundingBox: CGRect
    let landmarks: VNFaceLandmarks?
    let roll: NSNumber?
    let yaw: NSNumber?
}
```

### Barcode Scanning

```swift
import Vision

class BarcodeScanner {
    func scanBarcodes(in image: CGImage) async throws -> [ScannedBarcode] {
        return try await withCheckedThrowingContinuation { continuation in
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
}

struct ScannedBarcode {
    let payload: String
    let type: String
    let boundingBox: CGRect
}
```

### Live Camera Feed

```swift
import AVFoundation
import Vision

class CameraProcessor: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    private let captureSession = AVCaptureSession()
    private let videoOutput = AVCaptureVideoDataOutput()
    
    func startCapture() {
        guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: camera) else { return }
        
        captureSession.addInput(input)
        videoOutput.setSampleBufferDelegate(self, queue: DispatchQueue(label: "camera"))
        captureSession.addOutput(videoOutput)
        captureSession.startRunning()
    }
    
    func captureOutput(_ output: AVCaptureOutput,
                       didOutput sampleBuffer: CMSampleBuffer,
                       from connection: AVCaptureConnection) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let request = VNRecognizeTextRequest { request, error in
            guard let results = request.results as? [VNRecognizedTextObservation] else { return }
            let text = results.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
            DispatchQueue.main.async {
                self.handleRecognizedText(text)
            }
        }
        
        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer)
        try? handler.perform([request])
    }
}
```

---

## 4. Natural Language

### Sentiment Analysis

```swift
import NaturalLanguage

class SentimentAnalyzer {
    func analyze(_ text: String) -> SentimentResult {
        let tagger = NLTagger(tagSchemes: [.sentimentScore])
        tagger.string = text
        
        let (sentiment, _) = tagger.tag(
            at: text.startIndex,
            unit: .paragraph,
            scheme: .sentimentScore
        )
        
        let score = Double(sentiment?.rawValue ?? "0") ?? 0
        
        return SentimentResult(
            score: score,
            label: score > 0.1 ? .positive : score < -0.1 ? .negative : .neutral
        )
    }
}

struct SentimentResult {
    let score: Double  // -1.0 to 1.0
    let label: Sentiment
}

enum Sentiment {
    case positive, negative, neutral
}
```

### Named Entity Recognition

```swift
import NaturalLanguage

class EntityRecognizer {
    func recognizeEntities(in text: String) -> [RecognizedEntity] {
        let tagger = NLTagger(tagSchemes: [.nameType])
        tagger.string = text
        
        var entities: [RecognizedEntity] = []
        
        let range = text.startIndex..<text.endIndex
        tagger.enumerateTags(in: range, unit: .word, scheme: .nameType) { tag, tokenRange in
            if let tag {
                let entity = RecognizedEntity(
                    text: String(text[tokenRange]),
                    type: entityType(from: tag),
                    range: tokenRange
                )
                entities.append(entity)
            }
            return true
        }
        
        return entities
    }
    
    private func entityType(from tag: NLTag) -> EntityType {
        switch tag {
        case .personalName: return .person
        case .placeName: return .place
        case .organizationName: return .organization
        default: return .other
        }
    }
}

struct RecognizedEntity {
    let text: String
    let type: EntityType
    let Range: Range<String.Index>
}

enum EntityType {
    case person, place, organization, other
}
```

### Language Identification

```swift
import NaturalLanguage

class LanguageIdentifier {
    func identifyLanguage(_ text: String) -> String? {
        let recognizer = NLLanguageRecognizer()
        recognizer.processString(text)
        return recognizer.dominantLanguage?.rawValue
    }
    
    func identifyWithConfidence(_ text: String) -> [(language: String, confidence: Double)] {
        let recognizer = NLLanguageRecognizer()
        recognizer.processString(text)
        
        return recognizer.languageHypotheses(withMaximum: 3).map { lang, confidence in
            (language: lang.rawValue, confidence: confidence)
        }.sorted { $0.confidence > $1.confidence }
    }
}
```

### Text Embeddings

```swift
import NaturalLanguage

class TextEmbedder {
    private let embedding = NLEmbedding.wordEmbedding(for: .english)
    
    func embedding(for word: String) -> [Double]? {
        return embedding?.vector(for: word)
    }
    
    func similarity(between word1: String, and word2: String) -> Double? {
        return embedding?.distance(between: word1, and: word2)
    }
    
    func nearestNeighbors(to word: String, count: Int = 5) -> [(word: String, distance: Double)]? {
        return embedding?.nearestNeighbors(for: word, maximumCount: count).map { (word: $0.0, distance: $0.1) }
    }
}
```

---

## 5. Speech Recognition

### Live Transcription

```swift
import Speech

class SpeechRecognizer: ObservableObject {
    @Published var isRecording = false
    @Published var transcript = ""
    
    private let audioEngine = AVAudioEngine()
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let recognizer = SFSpeechRecognizer()
    
    func requestAuthorization() async -> Bool {
        await withCheckedContinuation { continuation in
            SFSpeechRecognizer.requestAuthorization { status in
                continuation.resume(returning: status == .authorized)
            }
        }
    }
    
    func startRecording() throws {
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        
        let inputNode = audioEngine.inputNode
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest else { return }
        
        recognitionRequest.shouldReportPartialResults = true
        
        recognitionTask = recognizer?.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            guard let self else { return }
            
            if let result {
                self.transcript = result.bestTranscription.formattedString
            }
            
            if error != nil || (result?.isFinal ?? false) {
                self.audioEngine.stop()
                inputNode.removeTap(onBus: 0)
                self.recognitionRequest = nil
                self.recognitionTask = nil
                self.isRecording = false
            }
        }
        
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            self.recognitionRequest?.append(buffer)
        }
        
        audioEngine.prepare()
        try audioEngine.start()
        isRecording = true
    }
    
    func stopRecording() {
        audioEngine.stop()
        recognitionRequest?.endAudio()
        isRecording = false
    }
}
```

### File Transcription

```swift
import Speech

class FileTranscriber {
    func transcribe(audioFileURL: URL) async throws -> String {
        return try await withCheckedThrowingContinuation { continuation in
            let request = SFSpeechURLRecognitionRequest(url: audioFileURL)
            request.shouldReportPartialResults = false
            
            let recognizer = SFSpeechRecognizer()
            recognizer?.recognitionTask(with: request) { result, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                
                if let result?.isFinal {
                    continuation.resume(returning: result.bestTranscription.formattedString)
                }
            }
        }
    }
}
```

### On-Device vs Server

| Feature | On-Device | Server |
|---------|-----------|--------|
| Privacy | Yes | No |
| Offline | Yes | No |
| Accuracy | Good | Better |
| Languages | Limited | Many |
| Speed | Fast | Varies |

```swift
// Prefer on-device
let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
if recognizer?.supportsOnDeviceRecognition == true {
    request.requiresOnDeviceRecognition = true
}
```

---

## Integration Patterns

### Combine Multiple AI Features

```swift
class SmartAssistant: ObservableObject {
    let textRecognizer = TextRecognizer()
    let sentimentAnalyzer = SentimentAnalyzer()
    let entityRecognizer = EntityRecognizer()
    let speechRecognizer = SpeechRecognizer()
    
    func analyzeImage(_ image: CGImage) async throws -> ImageAnalysis {
        async let texts = textRecognizer.recognizeText(in: image)
        async let faces = FaceDetector().detectFaces(in: image)
        
        let (recognizedTexts, detectedFaces) = try await (texts, faces)
        
        return ImageAnalysis(
            text: recognizedTexts.map(\.text),
            faces: detectedFaces.count,
            textCount: recognizedTexts.count
        )
    }
    
    func analyzeText(_ text: String) -> TextAnalysis {
        let sentiment = sentimentAnalyzer.analyze(text)
        let entities = entityRecognizer.recognizeEntities(in: text)
        
        return TextAnalysis(
            sentiment: sentiment,
            entities: entities
        )
    }
}

struct ImageAnalysis {
    let text: [String]
    let faces: Int
    let textCount: Int
}

struct TextAnalysis {
    let sentiment: SentimentResult
    let entities: [RecognizedEntity]
}
```

---

## Decision Guide

| Need | Use This |
|------|----------|
| Chat / text generation | Apple Intelligence Foundation Models |
| Custom image classification | Core ML with converted model |
| OCR on documents | Vision VNRecognizeTextRequest |
| Barcode scanning | Vision VNDetectBarcodesRequest |
| Sentiment analysis | NaturalLanguage NLTagger |
| Entity extraction | NaturalLanguage NLTagger |
| Live speech to text | Speech SFSpeechRecognizer |
| Word similarity | NaturalLanguage NLEmbedding |
| On-device LLM | Core ML + llama.cpp or MLX |
