🇰🇷 [한국어 README 보기](README.ko.md)

# IntentCP

> **A lightweight Intent Control Plane for natural-language control via iOS Shortcuts**  
> Without hosting a local LLM or GPU server, IntentCP turns the intent parsed on your phone into a  
> **safe execution format (Control URL)** and connects it to real actions.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![iOS Shortcuts](https://img.shields.io/badge/iOS-Shortcuts-FF4A00.svg?logo=shortcuts&logoColor=white)](https://support.apple.com/guide/shortcuts/welcome/ios)

> **Note (naming / MCP confusion)**
>
> IntentCP is **not** an implementation of Anthropic’s **Model Context Protocol (MCP)**.
> In this project, “Control Plane” refers to an architecture that connects **natural-language intent → execution request (Control URL) → local execution**.

IntentCP does **not** execute natural-language commands directly.
Instead, it translates them into a **standardized execution request (Control URL)**,
and the server executes it **only within a defined spec and constraints**.

Today, IntentCP takes a **Shortcuts-first** approach:
- Siri + mobile AI (Apple Intelligence / optional ChatGPT) are used as the *intent parsing layer*
- the execution layer is designed to be extensible beyond smart-home IoT, including **local system control via a Windows Agent**

**TL;DR**
- 📱 **Shortcuts-first UX**: trigger with “Hey Siri” + a Shortcut
- 🤖 **No local AI hosting**: no GPU / no always-on local LLM server at home
- 🔗 **URL-based execution model**: natural language → Control URL → server execution
- 🧩 **Multi-target control**: Tuya + Windows Agent (and more planned)

## ✨ Why IntentCP?

- **Predictable execution**: natural language is normalized into a **Control URL**, and the server executes only within the defined spec.
- **No local AI hosting**: reuse mobile AI (on-device / private cloud / optional cloud) instead of running AI infra at home.
- **Control URL (standard execution surface)**: one URL spec shared across voice, scripts, automation, and dashboards.
- **Designed to extend**: Tuya-first today, but structured to grow toward Windows Agent, Matter/Zigbee, and more.

## 🚀 The Vision: Intent Control Plane

IntentCP is not a “just demo it with a chatbot” project.
It aims to separate and compose:
**intent parsing (LLM) ↔ execution (Control Plane) ↔ feedback (LLM/TTS)**.

---

## Demo

Below are short real-world demos showing **natural language voice commands**
executed through iOS Shortcuts → IntentCP → real devices.

### 🎥 Demo 1 — “Make the house feel cozy”

**GIF (quick preview)** ![Make the house feel cozy – GIF](docs/images/demo-make-the-house-feel-cozy-record.gif)

**Video (full clip)**  
[Open demo-make-the-house-feel-cozy.mp4](docs/videos/demo-make-the-house-feel-cozy.mp4)

---

### 🎥 Demo 2 — “I'm going to sleep”

**Video (full clip)**  
[Open demo-im-going-to-sleep.mp4](docs/videos/demo-im-going-to-sleep.mp4)

---

- Example calls
  ```bash
  # Light ON
  curl -X POST "http://localhost:8000/tuya/living_light/on"

  # Status query
  curl -X GET "http://localhost:8000/tuya/living_light/status"

  # Sequence (URL-encoded step delay)
  curl -X GET "http://localhost:8000/tuya/sequence?actions=living_light:on,subdesk_light:off%3Fdelay%3D5"
  ```

## ⚡ 2-minute Quick Start

Verify the core loop in three steps:

1) Run `intentcp init` to generate your Tuya + device configuration
2) Run the server
3) Test with `curl` (on/status) or the Web Panel

👉 See the full guide in **[Quick Start](#quick-start-development--local)** below.

---

## Key Features

- 📱 **iOS Shortcuts-first UX**: Shortcuts are the distribution + usage unit (not an extra app/dashboard)
- 🤖 **No AI Hosting Required**
  - no local LLM, no dedicated model server, no GPU/VRAM
  - works with **Apple Intelligence features available in Shortcuts** and **ChatGPT (optional)**
- 🧠 **Lightweight Core Server**
  - IntentCP Core focuses on orchestration (HTTP control + device gateway)
  - designed to run 24/7 on low-power home servers (e.g., Raspberry Pi / mini PC)
- 🧠 **Two-stage LLM pipeline (as a product feature)**
  - **LLM #1**: natural language → **Control URL** (safe execution format)
  - **LLM #2**: result JSON → **one-line feedback** (includes failure reasons/status)
- 🔗 **Unified Control URL spec** (GET/POST): one format shared by voice/buttons/scripts/schedulers
- ☁️ **Real Tuya Cloud device control** (on/off, brightness, status, scenes, sequences)
- 🧩 **Extensible action mapping**: designed to expand beyond Tuya (e.g., Windows Agent)
- 🖥️ Built-in **Web Panel** for configuration checks and quick tests
- 🧰 **Monorepo**: core server / Shortcuts distribution / (WIP) prompt & schema orchestration
- 🗺️ Unified GUI for device/scene/account management (planned)

---

## System Overview

AI Assistant (Siri) → iOS Shortcuts → LLM #1 → IntentCP Server → (Tuya Cloud | Windows Agent) → Physical Devices  
Physical Devices → (Tuya Cloud | Windows Agent) → IntentCP Server → LLM #2 → iOS Shortcuts → AI Assistant (Siri)

---

## Repository Structure

This project is a **monorepo**, where each subdirectory represents a core component of the IntentCP pipeline.

```bash
IntentCP/
  README.md                         # Project overview (EN)
  README.ko.md                      # Project overview (KO)

  intentcp-core/                    # Core server (FastAPI)
    src/                            # Server implementation
    cli/                            # CLI for setup / operations
    pyproject.toml
    web/                            # Web panel (templates/static)

  intentcp-shortcuts-signal/   # Siri Shortcut (Signal) distribution & docs
    README.md
    README.ko.md
    install/                        # iCloud link + setup checklist (KO/EN)
    prompts/                        # Canonical prompts (LLM #1 / #2)
    shortcuts/                      # Signal.shortcut + example
    scripts/                        # Export / validation helpers

  intentcp-llm-flows/               # Prompt orchestration (planned / WIP)
    # Schemas, generators, CLI/GUI (future)
```

---

## What is IntentCP?

IntentCP is **Shortcuts-first today** (so you can start without running your own AI),
but long-term it aims to become an **integrated Home Control Plane** that automatically connects
accounts/devices/scenes/prompts and voice shortcut distribution from a single configuration.

Below is the “ultimate integration scenario” IntentCP is aiming for.

### Ultimate Vision

From a single GUI or CLI, users will be able to:

- Authenticate IoT accounts (Tuya and more)
- Auto-discover and register devices
- Assign human-friendly aliases
- Define custom Scenes

Based on this configuration, IntentCP automatically generates:

- `intentcp-core` server configuration
- LLM control & response prompts
- Siri Shortcut distribution links

In other words, IntentCP aims to become:

> **A unified orchestration system that turns user configuration into server logic, LLM behavior, and voice shortcuts automatically.**

---

## End-to-End Control Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Siri as Siri
    participant Shortcuts as iOS Shortcuts (Signal)
    participant LLM1 as LLM #1 (URL Generator)
    participant IntentCP as IntentCP Server
    participant Tuya as Tuya Cloud
    participant LLM2 as LLM #2 (Response Summarizer)

    User->>Siri: Trigger the shortcut
    Siri->>Shortcuts: Run Shortcut
    Shortcuts->>User: Ask for voice/text input
    User->>Shortcuts: Natural language command

    Shortcuts->>LLM1: Forward command
    LLM1-->>Shortcuts: Return Control URL path (single line)

    Shortcuts->>IntentCP: HTTP GET/POST /tuya/living_light/on
    IntentCP->>Tuya: Device Control API call
    Tuya-->>IntentCP: Control result (JSON)
    IntentCP-->>Shortcuts: JSON response

    Shortcuts->>LLM2: Original command + JSON result
    LLM2-->>Shortcuts: One-sentence response
    Shortcuts->>Siri: Speak via TTS
    Siri-->>User: Voice feedback
```

---

### (Roadmap) Dynamic context injection via `/context`

This is **not implemented yet**. The planned flow is:
- Shortcuts fetches the latest device specs/states from the local server (`/context`)
- that context is injected into the prompt before calling the LLM

```mermaid
sequenceDiagram
    participant User as User
    participant Siri as Siri
    participant Shortcuts as iOS Shortcut (Signal)
    participant IntentCP as IntentCP Server
    participant LLM1 as LLM #1 (URL Generator)

    User->>Siri: Trigger the shortcut
    Siri->>Shortcuts: Run Shortcut

    Shortcuts->>IntentCP: HTTP GET /context
    IntentCP-->>Shortcuts: Device specs + states (JSON)
    Note over Shortcuts: Inject context into the prompt

    Shortcuts->>LLM1: Natural language + context
    LLM1-->>Shortcuts: Control URL

    Shortcuts->>IntentCP: HTTP GET/POST (Control URL)
```

---

## Component Roles

| Component | Role |
|----------|------|
| User | Issues voice commands |
| AI Assistant (Siri) | Voice trigger |
| iOS Shortcuts | Speech-to-text, LLM calls, HTTP execution, TTS output |
| LLM #1 | Natural language → control URL path |
| IntentCP Server | Personal MCP server + IoT gateway |
| Tuya Cloud | Real-world IoT device control |
| LLM #2 | Control JSON → natural language response |

---

## Supported Capabilities

- Device ON / OFF
- Light brightness control
- Device status queries
- Preset Scene execution
  - Mood lighting
  - Movie mode
  - Sleep mode
- Windows PC control (screen, application launch – agent-based)

---

<details>
<summary><b>Control URL Specification (API)</b> — expanded spec (click to open)</summary>

## Control URL Specification (IntentCP v1)

IntentCP uses a **URL-based control scheme** that unifies voice commands, LLM output, and automation routines.  
All controls can be executed via HTTP **GET / POST**, and this specification is the contract used by **LLM #1**.

### 1) Single Action

```text
/tuya/{device}/{action}
```

Optional delay:

```text
/tuya/{device}/{action}?delay={seconds}
```

Examples:

- Turn on living room light  
  `/tuya/living_light/on`
- Turn off desk light after 10 seconds  
  `/tuya/subdesk_light/off?delay=10`
- Query device status  
  `/tuya/living_light/status`

### 2) Sequence (Multiple Actions)

Run multiple actions in a single request:

```text
/tuya/sequence?actions=step1,step2,...
```

Step format:

```text
{device}:{action}[?delay=seconds]
```

- `delay` is optional and represents a **relative delay from “now”**.
- Steps without `delay` run immediately.
- Steps execute **in the order they appear**.

Examples:

- Open door, then turn on living room light
```text
/tuya/sequence?actions=door:open,living_light:on
```

- Turn on light, turn it off after 2 hours, and turn off PC after 1 hour
```text
/tuya/sequence?actions=living_light:on,living_light:off?delay=7200,pc:off?delay=3600
```

This URL scheme is a core design of IntentCP to standardize execution across voice, LLM, and automation.

---
 </details>


## Planned Extensions

- Schedule / weather / location / sensor-driven automation
- **(Roadmap) Dynamic context injection (`/context`)**: Shortcuts fetches device specs/states at runtime to stabilize Control URL generation.
- A home-server operation guide for low-power always-on setups (Raspberry Pi, mini PC, etc.)
- **Multi IoT platform support**
  - Integrate other IoT platforms that provide Cloud APIs (beyond Tuya)
  - Vendor-agnostic common Action layer
- **Local protocol device control** (Zigbee / Matter, etc.)
- Windows / macOS agent-based local system control
- Camera and security sensor integration
- Hybrid control across multiple platforms (including HomeKit)
- Mobile web dashboard + unified Web GUI
- Google Assistant and other voice platforms

---

## Quick Start (Development / Local)

> This is a minimal setup for development/testing. Production hardening (auth, SSL, network security) will be documented separately.

### 0) Recommended Environment

- **Python 3.11+**
  - **3.12** is recommended for local development
- macOS / Linux recommended

### 1) Clone

```bash
git clone https://github.com/jaebinsim/IntentCP
cd IntentCP
```

### 2) (Optional) Install / pin Python with pyenv (macOS)

```bash
brew update
brew install pyenv

pyenv install 3.12.2
pyenv local 3.12.2
```

> If you already have Python 3.11+ available, you can skip this.

### 3) Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
```

### 4) Install `intentcp-core`

IntentCP is a monorepo, but **Python dependencies are currently managed in `intentcp-core/pyproject.toml`**.  
For the initial run, installing `intentcp-core` is enough.

```bash
python -m pip install -e ./intentcp-core
```

### 5) Configure via Wizard (no manual TOML editing)

You no longer need to copy/edit TOML files by hand.
`intentcp init` guides you through required settings (account/region/devices) and generates config files automatically.

```bash
intentcp --help
intentcp init
```

- Generated config files:
  - `intentcp-core/config/settings.toml`
  - `intentcp-core/config/devices.toml`

### 6) Run the server

```bash
uvicorn intentcp_core.app:app --host 0.0.0.0 --port 8000 --reload
```

- Web Panel
  - Local: `http://127.0.0.1:8000/panel/`
  - Same Wi‑Fi/LAN: `http://<your-local-ip>:8000/panel/`

### 7) Device management CLI

```bash
intentcp devices --help
```

### 8) Basic control tests (optional)

```bash
# Single action: Light ON
curl -X POST "http://localhost:8000/tuya/living_light/on"

# Single action: Light OFF
curl -X POST "http://localhost:8000/tuya/living_light/off"

# Status query
curl -X GET "http://localhost:8000/tuya/living_light/status"

# Sequence: turn on living light, then turn off desk light after 5 seconds
curl -X GET "http://localhost:8000/tuya/sequence?actions=living_light:on,subdesk_light:off?delay=5"
```

### 9) Connect Siri Shortcuts

Follow the setup guide:

- `intentcp-shortcuts-signal/install/setup-checklist.md` (EN) / `intentcp-shortcuts-signal/install/setup-checklist.ko.md` (KO)

> ⚠️ Prompt/flow auto-generation is still in the design stage.
> For now, documentation focuses on the concept and how Shortcuts uses the prompts.

---

## Troubleshooting

- **Tuya control not working**
  - Verify endpoint (region), device IDs, and device capabilities (e.g., brightness support).
- **Server works but iOS Shortcut fails**
  - Check local network permissions, firewall/port-forwarding, and SSL configuration.

---

## 📱 Siri Shortcuts (Signal) – Related Documentation

The documents below explain how these prompts are actually used inside the
**IntentCP Signal iOS Shortcut**, from installation to full configuration.

If you are setting up voice control for the first time, it is recommended
to read them in order.

- 📄 **Signal Shortcut Overview**
  - [intentcp-shortcuts-signal/README.md](intentcp-shortcuts-signal/README.md)

- 🔗 **Install Signal Shortcut (iCloud Link)**
  - [intentcp-shortcuts-signal/install/iCloud-link.md](intentcp-shortcuts-signal/install/iCloud-link.md)

- ✅ **Signal Setup Checklist**
  - [intentcp-shortcuts-signal/install/setup-checklist.md](intentcp-shortcuts-signal/install/setup-checklist.md)

- 🧠 **LLM Prompt Usage Guide**
  - [intentcp-shortcuts-signal/prompts/README.md](intentcp-shortcuts-signal/prompts/README.md)

---