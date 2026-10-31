---
name: mengto-coding-skill
description: "GitHub profile skill from @MengTo. Use it when the task would benefit from mimicking this developer's repo choices, coding style, and implementation techniques."
---

## What they tend to build

- **Designer-first tools and demos**: libraries, templates, plugins, and learning projects that help non-engineers build polished UI faster.
- **Highly demoable systems**: the repo usually includes a clear example app, screenshot, or interactive showcase, not just source code.
- **Reusable primitives over giant apps**: animation helpers, prompt/workflow packs, templates, and small libraries that can be dropped into other work.
- **Teaching artifacts**: many projects double as tutorials or courses, with code organized to make concepts easy to copy and adapt.

## Coding patterns to mirror

- **Optimize for quick adoption**
  - simple install steps
  - copy/paste usage snippets
  - minimal setup friction
  - compatibility notes up front
- **Keep APIs small and memorable**
  - Spring exposes a compact set of functions like `animate()`, `animateNext`, `animateTo()`
  - properties are named plainly (`force`, `duration`, `damping`, `velocity`, `rotate`)
- **Prefer self-contained examples**
  - single-file or few-file demos where possible
  - separate library code from a runnable sample app
  - include tests or demo targets when the behavior is nontrivial
- **Document with examples, not theory**
  - show storyboard setup and code usage side by side
  - list available animations/options explicitly
  - note caveats and known issues directly
- **Bias toward portability**
  - skills and workflows are packaged as reusable folders with plain Markdown instructions
  - assets/scripts live alongside the guidance so they can travel with the repo

## Product and UI taste

- **Motion is a core feature, not decoration**: animation, transitions, and interaction feedback are treated as product value.
- **Polished but approachable visuals**: they favor clean layouts with a premium feel, often guided by strong composition and spacing rather than heavy UI chrome.
- **Narrative/experiential interfaces**: projects like `kage`, `sketchbook`, and `towers` suggest a taste for scroll/drag-driven storytelling and interactive scenes.
- **Tactile, material-inspired presentation**: `complete-shelf`, `AppStoreSketch`, and `sketchbook` lean into paper, books, shelves, and app-store presentation details.
- **Design-reference thinking**: the work often transforms a visual idea into a working system, not just a static mockup.

## Tech stack clues

- **Swift + iOS/Xcode** are central, especially for libraries and app prototypes.
- **Objective-C appears in older app work**, so compatibility and legacy integration matter.
- **CocoaPods and submodules** show up as dependency patterns.
- **HTML/CSS/JavaScript** are used heavily for demos, interaction experiments, and no-build experiences.
- **Three.js** is a clear clue for creative-coding, generative scenes, and interactive 3D web work.
- **Sketch plugins/templates** indicate comfort with design tooling and workflow automation.
- **Markdown-first repo structure** is common in the skills repo: the repo itself is part of the product.

## When to inspect repos first

- When the task involves **animation or interaction behavior**; the preferred API shape and motion language matter.
- When building **anything intended for designers**; inspect for setup flow, terminology, and example-driven documentation.
- When working on **web demos or creative coding**; look for whether the repo is meant to be single-file, no-build, or highly self-contained.
- When creating **agent workflows or prompt packs**; mirror the portable folder structure and concise procedural tone from `Skills`.
- When compatibility or integration matters; older iOS repos show specific Xcode/iOS/version constraints and dependency expectations.

## Repo Map

- [MengTo/Spring](https://github.com/MengTo/Spring): A library to simplify iOS animations in Swift. (14043 stars, Swift)
- [MengTo/Skills](https://github.com/MengTo/Skills): Agent skills for designers and builders using Codex, Claude, Cursor, and other AI coding agents (4868 stars, HTML)
- [MengTo/DesignerNewsApp](https://github.com/MengTo/DesignerNewsApp): Build a Swift App as a designer (2420 stars, Objective-C)
- [MengTo/AppStoreSketch](https://github.com/MengTo/AppStoreSketch): A quick App Store template for Sketch (1557 stars)
- [MengTo/kage](https://github.com/MengTo/kage): An interactive five-chapter night walk through a Kyoto mountain temple, rendered live in Three.js. (1094 stars, HTML, topics: creative-coding, generative-art, interactive-storytelling, japanese-design)
- [MengTo/complete-shelf](https://github.com/MengTo/complete-shelf): An original single-file Three.js library of seven interactive clothbound hardcovers. (610 stars, HTML, topics: book-design, creative-coding, github-pages, interactive-design)
- [MengTo/react-native-for-designers](https://github.com/MengTo/react-native-for-designers): React Native for Designers course (276 stars, JavaScript)
- [MengTo/Angle-Sketch-Plugin](https://github.com/MengTo/Angle-Sketch-Plugin): A free Sketch plugin for creating perspective mockups. (216 stars, JavaScript)
- [MengTo/my-react-app](https://github.com/MengTo/my-react-app): Template for the React for Designers course (177 stars, JavaScript)
- [MengTo/sketchbook](https://github.com/MengTo/sketchbook): A page-flipping sketchbook of Singapore. One static HTML file: drag to turn the page, drag the magnifier across it. (175 stars, HTML, topics: css, html, javascript, no-build)
- [MengTo/Ripple](https://github.com/MengTo/Ripple): Learn Xcode as a designer. (125 stars, Objective-C)
- [MengTo/towers](https://github.com/MengTo/towers): A tower builds itself from the ground up in four and a half seconds: a Japanese tenshu, a Chinese pagoda or a Thai prang, in one self-contained HTML file. (85 stars, HTML, topics: architecture, generative, procedural-generation, single-file)

## How To Use This Skill

- Reach for this skill when the user asks for Meng To's style, when the repo stack matches this person's ecosystem, or when studying their real code would reduce made-up output.
- Pick one or more relevant repositories from the list above based on the current task.
- Clone the most relevant repository or repositories into `/tmp` for temporary inspection.
- Study the implementation details, naming patterns, architecture, UI taste, and tooling choices there.
- Return to the main task and apply the useful patterns you observed instead of copying blindly.
- Treat the upstream repositories as reference material for style and technique, then adapt them to the current codebase responsibly.
