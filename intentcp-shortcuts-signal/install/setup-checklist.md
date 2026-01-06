🇰🇷 [한국어 README 보기](setup-checklist.ko.md)

# IntentCP Signal Shortcut – Setup Checklist

This document is a **minimal setup checklist** required to configure **IntentCP + iOS Shortcut (Signal)** for the first time.
By following the steps **from top to bottom**, you can quickly verify that everything is working correctly.

---

## 1. Prerequisites

- [ ] iOS device (iPhone / iPad)
- [ ] iOS **Shortcuts** app installed
- [ ] IntentCP Core server running
  - Example: `http://127.0.0.1:8000`
  - HTTPS is recommended for external access
- [ ] Devices registered in IntentCP Core (`devices.toml`)

---

## 2. Install the Shortcut

1. Open the **Signal.shortcut** install link from `install/iCloud-link.md` (real-use shortcut)

Reference:
- `shortcuts/Signal.shortcut` : Actual shortcut for real use / distribution (manual configuration required)
- `shortcuts/Signal (Example).shortcut` : Example shortcut
  - LLM prompt structure is pre-filled (except BASE_URL)
  - Used to reference how **Shortcut variables** are configured in each field

2. In the Shortcuts app, tap **“Add Shortcut”**
3. After installation, confirm that the shortcut name is `Signal`
4. Rename the shortcut to the phrase you want to use with Siri (recommended)

```
The default shortcut name is `Signal`.
In iOS, the shortcut name itself becomes the phrase Siri listens for.

Renaming the shortcut to something easy to pronounce and remember
is strongly recommended.

After renaming, you can invoke it like:
- "Hey Siri, <your shortcut name>"

How to rename:
1. Long-press the `Signal` shortcut or tap **··· (three dots)**
2. Tap the shortcut name at the top
3. Change it to your preferred name
```

---

## 3. Shortcut Permissions (Important)

The Signal shortcut uses voice input and network requests.
If the following permissions are not granted, it will not function correctly.

- [ ] **Microphone access allowed**
- [ ] **Dictation allowed**
- [ ] **Network access allowed**
- [ ] **Allow “Untrusted Shortcuts”**

> On first execution, iOS will request permissions sequentially.
> If you previously denied a permission, you must re-enable it manually in
> **Settings → Privacy & Security**.

---

## 4. IntentCP Server Address (Base URL)

The distributed Signal shortcut includes a default **IntentCP server Base URL**.
You must modify it to match your environment.

### Examples

- Local testing:
  ```
  http://127.0.0.1:8000
  ```
- External access:
  ```
  https://your-domain.example.com
  ```

### Where to edit

In the shortcut edit screen, check the following locations:

- **LLM #1 (URL Generator) prompt**
- **HTTP Request action – URL field**

In `Signal.shortcut`, the Base URL is separated into its own input field.

This field must contain **only**:
- IntentCP server host + port (or domain)

Examples:
- http://127.0.0.1:8000
- https://your-domain.example.com

⚠️ Do NOT include paths such as `/tuya/...` in this field.

---

## 5. Shortcut Editing & LLM Prompt Setup

The Signal shortcut operates using a **two-stage LLM architecture (LLM #1 / LLM #2)**.

---

### 5-1) Open the Shortcut Editor

1. Open the iOS **Shortcuts** app
2. Tap **··· (three dots)** on the `Signal` shortcut card
3. In the editor, locate the following fields:
   - **LLM #1 prompt input**
   - **LLM #2 prompt input**

> The distributed shortcut includes placeholder text such as:
> `Paste LLM#1 prompt here / 이곳에 LLM#1 프롬프트 입력하세요`

#### Required Configuration Summary

Users must configure the following three items in `Signal.shortcut`:

1. **Base URL**
   - IntentCP server address
   - Used by the HTTP Request action

2. **LLM #1 Prompt (URL Generator)**
   - Converts natural language commands into Control URL paths (`/tuya/...`)

3. **LLM #2 Prompt (Response Summarizer)**
   - Converts server responses (JSON) into a single sentence Siri response

Each item is not just plain text.
They are designed to reference **Shortcut variables (outputs of previous actions)**.

⚠️ Important: Shortcut variable configuration

LLM prompts and HTTP request actions must correctly reference
outputs from previous steps using **Shortcut variables**.

Examples:
- Output of LLM #1 → inserted into the HTTP request URL
- HTTP response JSON → passed as input to LLM #2

Variable wiring must be verified in the iOS Shortcuts UI.
For an exact reference, see `Signal (Example).shortcut`.

---

### 5-2) LLM Provider Selection (User Choice)

The Signal shortcut does not lock you into a specific LLM provider.
You may choose any of the following:

- `Private Cloud Compute`
- `ChatGPT`

> Regardless of the provider, the **LLM #1 / #2 prompt content remains the same**.

---

### 5-3) LLM #1 – URL Generator

**Role**
- Converts user voice/text commands
- Into a single executable **IntentCP Control URL**

**Prompt file**
- `prompts/llm1_url_generator/v1.md`

**How to apply**
1. Copy the contents of the file
2. Paste it into the **LLM #1 prompt input** field

---

### 5-4) LLM #2 – Response Summarizer

**Role**
- Converts IntentCP server responses (JSON)
- Into a **single spoken sentence** for the user

**Prompt file**
- `prompts/llm2_response_summarizer/v1.md`

**How to apply**
1. Copy the contents of the file
2. Paste it into the **LLM #2 prompt input** field

---

### 5-5) Prompt Management Policy

This repository (`intentcp-shortcuts-signal`) contains the
**canonical prompt versions required for shortcut distribution and setup**.

- General users: use the `prompts/` directory as-is
- Prompt generation / expansion / orchestration:
  - Managed in `intentcp-llm-flows`
  - Final outputs should be **exported** into this repository

---

## 6. Basic Functionality Tests

The following test order is recommended.

### 1) Single Action Test

Say:
- “Turn on the living room light”

Expected result:
```
/tuya/living_light/on
```

---

### 2) Delayed Action Test

Say:
- “Turn off the desk light in 5 seconds”

Expected result:
```
/tuya/subdesk_light/off?delay=5
```

---

### 3) Sequence Test

Say:
- “Turn on all lights, then turn off the desk light after 5 seconds”

Expected result:
```
/tuya/sequence?actions=living_light:on,subdesk_light:on,subdesk_light:off?delay=5
```

---

## 7. Troubleshooting

### ❌ No response at all
- Verify the IntentCP server is running
- Check for Base URL typos
- Confirm iOS network permissions

### ❌ Incorrect device or action executed
- Verify the LLM #1 prompt version
- Ensure device aliases match `devices.toml`

### ❌ Server succeeds but Siri response sounds wrong
- Verify the LLM #2 prompt
- Check sequence response summarization rules

---