---
name: ios-animation-master
description: "Skill: ios-animation-master"
---

# Skill: ios-animation-master

Motion design system for iOS. Combines swiftui-animation, swiftui-gestures, realitykit, spritekit, and pencilkit into a comprehensive guide for adding beautiful motion to your apps.

## When to Use

- Add smooth transitions between screens
- Create custom spring animations
- Build gesture-driven animations
- Animate 3D objects in AR
- Create 2D game animations
- Add drawing/inking animations

---

## Animation Hierarchy

```
Implicit (Simple)
├── .animation()
├── .transition()
└── .matchedGeometryEffect()

Explicit (Complex)
├── withAnimation { }
├── Animation types (spring, easeInOut, etc.)
└── PhaseAnimator

Gesture-Driven
├── .gesture()
├── @GestureState
└── MagnifyGesture, RotateGesture

Advanced
├── KeyframeAnimator
├── Custom Animations
└── Metal-based animations
```

---

## 1. SwiftUI Implicit Animations

### Basic Transitions

```swift
struct ContentView: View {
    @State private var isShowing = false
    
    var body: some View {
        VStack {
            Button("Toggle") {
                withAnimation(.spring(response: 0.6, dampingFraction: 0.8)) {
                    isShowing.toggle()
                }
            }
            
            if isShowing {
                Text("Hello, World!")
                    .transition(.slide)
                    // Other transitions:
                    // .opacity
                    // .scale
                    // .move(edge: .top)
                    // .asymmetric(insertion: .slide, removal: .opacity)
            }
        }
    }
}
```

### Matched Geometry Effect

```swift
struct Item: Identifiable {
    let id = UUID()
    let name: String
}

struct MatchedGeometryExample: View {
    @Namespace private var namespace
    @State private var selectedItem: Item?
    let items = [
        Item(name: "Item 1"),
        Item(name: "Item 2"),
        Item(name: "Item 3")
    ]
    
    var body: some View {
        ScrollView {
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 20) {
                ForEach(items) { item in
                    if selectedItem?.id == item.id {
                        // Expanded view
                        RoundedRectangle(cornerRadius: 20)
                            .fill(.blue)
                            .matchedGeometryEffect(id: item.id, in: namespace)
                            .frame(height: 200)
                            .overlay {
                                Text(item.name)
                                    .foregroundStyle(.white)
                                    .font(.title)
                            }
                    } else {
                        // Compact view
                        RoundedRectangle(cornerRadius: 12)
                            .fill(.blue.opacity(0.3))
                            .matchedGeometryEffect(id: item.id, in: namespace)
                            .frame(height: 100)
                            .overlay {
                                Text(item.name)
                            }
                    }
                }
            }
            .padding()
            .onTapGesture {
                withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) {
                    selectedItem = nil
                }
            }
        }
    }
}
```

### Animation Types

```swift
// Spring (most natural)
.animation(.spring(response: 0.6, dampingFraction: 0.8), value: someValue)

// Bouncy spring
.animation(.spring(response: 0.3, dampingFraction: 0.5), value: someValue)

// Smooth
.animation(.easeInOut(duration: 0.5), value: someValue)

// Snappy
.animation(.easeIn(duration: 0.2), value: someValue)

// Linear
.animation(.linear(duration: 1.0), value: someValue)

// Delayed
.animation(.easeInOut(duration: 0.5).delay(0.2), value: someValue)

// Repeated
.animation(.easeInOut(duration: 0.5).repeatCount(3), value: someValue)

// Infinite
.animation(.easeInOut(duration: 1.0).repeatForever(autoreverses: true), value: someValue)
```

---

## 2. Phase Animators

```swift
enum AnimationPhase: CaseIterable {
    case initial
    case appearing
    case rotating
    case scaling
    
    var offset: Double {
        switch self {
        case .initial: return -100
        case .appearing: return 0
        case .rotating: return 0
        case .scaling: return 0
        }
    }
    
    var rotation: Double {
        switch self {
        case .initial: return 0
        case .appearing: return 0
        case .rotating: return 360
        case .scaling: return 360
        }
    }
    
    var scale: Double {
        switch self {
        case .initial: return 0.5
        case .appearing: return 1.0
        case .rotating: return 1.0
        case .scaling: return 1.5
        }
    }
}

struct PhaseAnimatorExample: View {
    var body: some View {
        PhaseAnimator(AnimationPhase.allCases) { content, phase in
            content
                .offset(y: phase.offset)
                .rotation3DEffect(.degrees(phase.rotation), axis: (x: 1, y: 0, z: 0))
                .scaleEffect(phase.scale)
        } animation: { phase in
            .spring(response: 0.6, dampingFraction: 0.8)
        } content: {
            Image(systemName: "star.fill")
                .font(.system(size: 50))
                .foregroundStyle(.yellow)
        }
    }
}
```

---

## 3. Keyframe Animators

```swift
struct KeyframeAnimatorExample: View {
    var body: some View {
        KeyframeAnimator(initialValue: AnimationValues()) { values in
            Image(systemName: "heart.fill")
                .font(.system(size: 50))
                .foregroundStyle(.red)
                .scaleEffect(values.scale)
                .rotation3DEffect(.degrees(values.rotation), axis: (x: 1, y: 0, z: 0))
                .offset(y: values.offset)
        } keyframes: { _ in
            KeyframeTrack(\.scale) {
                LinearKeyframe(1.5, duration: 0.2)
                SpringKeyframe(0.8, duration: 0.3)
                SpringKeyframe(1.0, duration: 0.3)
            }
            
            KeyframeTrack(\.rotation) {
                LinearKeyframe(180, duration: 0.4)
                SpringKeyframe(360, duration: 0.4)
            }
            
            KeyframeTrack(\.offset) {
                SpringKeyframe(-50, duration: 0.3)
                SpringKeyframe(50, duration: 0.3)
                SpringKeyframe(0, duration: 0.3)
            }
        }
    }
}

struct AnimationValues {
    var scale: Double = 1.0
    var rotation: Double = 0.0
    var offset: Double = 0.0
}
```

---

## 4. Gesture-Driven Animations

### Basic Gesture Animation

```swift
struct GestureAnimationExample: View {
    @State private var offset = CGSize.zero
    @State private var isDragging = false
    
    var body: some View {
        Circle()
            .fill(.blue)
            .frame(width: 100, height: 100)
            .offset(offset)
            .scaleEffect(isDragging ? 1.2 : 1.0)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        offset = value.translation
                        isDragging = true
                    }
                    .onEnded { value in
                        withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) {
                            offset = .zero
                            isDragging = false
                        }
                    }
            )
    }
}
```

### Simultaneous Gestures

```swift
struct SimultaneousGestureExample: View {
    @State private var scale: CGFloat = 1.0
    @State private var angle: Angle = .zero
    @State private var lastScale: CGFloat = 1.0
    @State private var lastAngle: Angle = .zero
    
    var body: some View {
        Image(systemName: "photo")
            .font(.system(size: 100))
            .scaleEffect(scale)
            .rotationEffect(angle)
            .gesture(
                SimultaneousGesture(
                    MagnifyGesture()
                        .onChanged { value in
                            scale = lastScale * value.magnification
                        }
                        .onEnded { _ in
                            lastScale = scale
                        },
                    RotateGesture()
                        .onChanged { value in
                            angle = lastAngle + value.rotation
                        }
                        .onEnded { _ in
                            lastAngle = angle
                        }
                )
            )
    }
}
```

### Gesture State

```swift
struct GestureStateExample: View {
    @GestureState private var dragOffset = CGSize.zero
    @State private var position = CGSize.zero
    
    var body: some View {
        VStack {
            Circle()
                .fill(.green)
                .frame(width: 80, height: 80)
                .offset(x: position.width + dragOffset.width,
                        y: position.height + dragOffset.height)
                .gesture(
                    DragGesture()
                        .updating($dragOffset) { value, state, _ in
                            state = value.translation
                        }
                        .onEnded { value in
                            position.width += value.translation.width
                            position.height += value.translation.height
                        }
                )
            
            Text("Drag the circle")
                .foregroundStyle(.secondary)
        }
    }
}
```

---

## 5. Custom Animations

### Animated Gradient

```swift
struct AnimatedGradient: View {
    @State private var start = UnitPoint.topLeading
    @State private var end = UnitPoint.bottomTrailing
    
    var body: some View {
        LinearGradient(
            colors: [.blue, .purple, .pink],
            startPoint: start,
            endPoint: end
        )
        .ignoresSafeArea()
        .onAppear {
            withAnimation(.easeInOut(duration: 3.0).repeatForever(autoreverses: true)) {
                start = .bottomTrailing
                end = .topLeading
            }
        }
    }
}
```

### Animated Number Counter

```swift
struct AnimatedCounter: View {
    let targetValue: Int
    @State private var displayValue = 0
    
    var body: some View {
        Text("\(displayValue)")
            .font(.system(size: 60, weight: .bold, design: .rounded))
            .foregroundStyle(.blue)
            .onAppear {
                withAnimation(.easeInOut(duration: 1.5)) {
                    displayValue = targetValue
                }
            }
    }
}
```

### Pulsing Animation

```swift
struct PulsingView: View {
    @State private var isPulsing = false
    
    var body: some View {
        Circle()
            .fill(.red)
            .frame(width: 20, height: 20)
            .overlay {
                Circle()
                    .stroke(.red, lineWidth: 2)
                    .scaleEffect(isPulsing ? 2.0 : 1.0)
                    .opacity(isPulsing ? 0 : 1)
            }
            .onAppear {
                withAnimation(.easeOut(duration: 1.0).repeatForever(autoreverses: false)) {
                    isPulsing = true
                }
            }
    }
}
```

### Loading Skeleton

```swift
struct SkeletonView: View {
    @State private var isAnimating = false
    
    var body: some View {
        LinearGradient(
            colors: [
                .gray.opacity(0.3),
                .gray.opacity(0.5),
                .gray.opacity(0.3)
            ],
            startPoint: .leading,
            endPoint: .trailing
        )
        .frame(height: 20)
        .clipShape(RoundedRectangle(cornerRadius: 4))
        .offset(x: isAnimating ? 200 : -200)
        .onAppear {
            withAnimation(.easeInOut(duration: 1.0).repeatForever(autoreverses: false)) {
                isAnimating = true
            }
        }
    }
}
```

---

## 6. 3D Animations (RealityKit)

### Basic 3D Animation

```swift
import RealityKit

struct RealityKitAnimationView: UIViewRepresentable {
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Create a box
        let box = ModelEntity(
            mesh: .generateBox(size: 0.1),
            materials: [SimpleMaterial(color: .blue, isMetallic: true)]
        )
        
        // Animate rotation
        let rotation = Transform(
            rotation: simd_quatf(angle: .pi * 2, axis: SIMD3(0, 1, 0))
        )
        
        box.move(
            to: rotation,
            relativeTo: nil,
            duration: 2.0,
            timingFunction: .easeInOut
        )
        
        // Create anchor and add box
        let anchor = AnchorEntity(plane: .horizontal)
        anchor.addChild(box)
        arView.scene.addAnchor(anchor)
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {}
}
```

### Continuous Rotation

```swift
extension ModelEntity {
    func rotateContinuously(axis: SIMD3<Float>, speed: Float = 1.0) {
        let rotation = Transform(
            rotation: simd_quatf(angle: speed * .pi * 2, axis: axis)
        )
        
        self.move(
            to: rotation,
            relativeTo: nil,
            duration: 1.0 / Double(speed),
            timingFunction: .linear
        )
    }
}
```

### Bounce Animation

```swift
extension ModelEntity {
    func bounce(height: Float = 0.05, duration: Double = 0.5) {
        let originalTransform = self.transform
        
        var upTransform = originalTransform
        upTransform.translation.y += height
        
        self.move(
            to: upTransform,
            relativeTo: nil,
            duration: duration / 2,
            timingFunction: .easeOut
        )
        
        DispatchQueue.main.asyncAfter(deadline: .now() + duration / 2) {
            self.move(
                to: originalTransform,
                relativeTo: nil,
                duration: duration / 2,
                timingFunction: .easeIn
            )
        }
    }
}
```

---

## 7. 2D Game Animations (SpriteKit)

### Basic Sprite Animation

```swift
import SpriteKit

class GameScene: SKScene {
    override func didMove(to view: SKView) {
        backgroundColor = .white
        
        // Create sprite
        let sprite = SKSpriteNode(imageNamed: "character")
        sprite.position = CGPoint(x: frame.midX, y: frame.midY)
        addChild(sprite)
        
        // Walk animation
        let textures = [
            SKTexture(imageNamed: "walk1"),
            SKTexture(imageNamed: "walk2"),
            SKTexture(imageNamed: "walk3"),
            SKTexture(imageNamed: "walk4")
        ]
        
        let walkAnimation = SKAction.animate(with: textures, timePerFrame: 0.1)
        let walkForever = SKAction.repeatForever(walkAnimation)
        sprite.run(walkForever)
    }
}
```

### Move Animations

```swift
class GameScene: SKScene {
    func animateSprite(_ sprite: SKSpriteNode) {
        // Move to point
        let move = SKAction.move(to: CGPoint(x: 200, y: 300), duration: 1.0)
        move.timingMode = .easeInEaseOut
        
        // Move by offset
        let moveBy = SKAction.moveBy(x: 100, y: 0, duration: 0.5)
        
        // Sequence
        let sequence = SKAction.sequence([
            move,
            SKAction.wait(forDuration: 0.5),
            moveBy.reversed()
        ])
        
        // Group (simultaneous)
        let group = SKAction.group([
            SKAction.scale(to: 1.5, duration: 1.0),
            SKAction.fadeAlpha(to: 0.5, duration: 1.0)
        ])
        
        sprite.run(sequence)
    }
}
```

### Particle Effects

```swift
class GameScene: SKScene {
    func createParticleEmitter() {
        let emitter = SKEmitterNode()
        
        emitter.particleLifetime = 2.0
        emitter.particleLifetimeRange = 1.0
        emitter.particleBirthRate = 100
        emitter.numParticlesToEmit = 0  // Infinite
        
        emitter.particleSpeed = 50
        emitter.particleSpeedRange = 25
        
        emitter.emissionAngleRange = .pi * 2
        
        emitter.particleAlpha = 1.0
        emitter.particleAlphaSpeed = -0.5
        
        emitter.particleScale = 0.1
        emitter.particleScaleRange = 0.05
        emitter.particleScaleSpeed = -0.05
        
        emitter.particleColor = .orange
        emitter.particleColorBlendFactor = 1.0
        
        emitter.particleTexture = SKTexture(imageNamed: "particle")
        
        emitter.position = CGPoint(x: frame.midX, y: frame.midY)
        addChild(emitter)
    }
}
```

---

## 8. Drawing Animations (PencilKit)

### Animated Drawing

```swift
import PencilKit

struct AnimatedDrawingView: UIViewRepresentable {
    func makeUIView(context: Context) -> PKCanvasView {
        let canvasView = PKCanvasView()
        canvasView.drawingPolicy = .anyInput
        canvasView.tool = PKInkingTool(.pen, color: .black, width: 5)
        return canvasView
    }
    
    func updateUIView(_ uiView: PKCanvasView, context: Context) {}
}

// Animate a path drawing
func animatePath(_ path: UIBezierPath, in view: UIView, duration: Double = 2.0) {
    let shapeLayer = CAShapeLayer()
    shapeLayer.path = path.cgPath
    shapeLayer.fillColor = UIColor.clear.cgColor
    shapeLayer.strokeColor = UIColor.black.cgColor
    shapeLayer.lineWidth = 2
    
    view.layer.addSublayer(shapeLayer)
    
    let animation = CABasicAnimation(keyPath: "strokeEnd")
    animation.fromValue = 0
    animation.toValue = 1
    animation.duration = duration
    animation.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
    
    shapeLayer.add(animation, forKey: "strokeEnd")
}
```

---

## Animation Timing Reference

| Type | Duration | Use Case |
|------|----------|----------|
| Micro-interaction | 0.1-0.2s | Button press, toggle |
| Small transition | 0.2-0.3s | Modal appear, card flip |
| Medium transition | 0.3-0.5s | Screen change, list reorder |
| Large transition | 0.5-1.0s | Page transition, hero animation |
| Dramatic | 1.0-2.0s | Splash screen, intro |

| Spring | Response | Damping | Use Case |
|--------|----------|---------|----------|
| Snappy | 0.3 | 0.7 | Button press |
| Smooth | 0.5 | 0.8 | Screen transition |
| Bouncy | 0.4 | 0.5 | Playful feedback |
| Gentle | 0.6 | 0.9 | Subtle motion |

---

## Accessibility

```swift
// Respect Reduce Motion setting
@Environment(\.accessibilityReduceMotion) var reduceMotion

var body: some View {
    Text("Hello")
        .offset(y: isAnimating ? 100 : 0)
        .animation(
            reduceMotion ? nil : .spring(response: 0.5, dampingFraction: 0.8),
            value: isAnimating
        )
}
```

---

## Decision Guide

| Animation Type | Use This |
|----------------|----------|
| Simple state change | `.animation()` |
| Screen transition | `.transition()` |
| Matched elements | `.matchedGeometryEffect()` |
| Multi-step sequence | `PhaseAnimator` |
| Complex keyframes | `KeyframeAnimator` |
| Gesture-driven | `DragGesture` + state |
| 3D rotation | RealityKit `.move()` |
| 2D sprite | SpriteKit `SKAction` |
| Drawing effect | PencilKit + `CAShapeLayer` |
