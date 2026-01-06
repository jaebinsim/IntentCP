🇰🇷 [한국어 README 보기](README.ko.md)

# Prompts (LLM #1 / LLM #2)

This directory contains versioned LLM prompts used by the **IntentCP Signal iOS Shortcut**.
Users are expected to copy these prompts and paste them directly into the iOS Shortcuts app (Signal shortcut).

---

## Prompt Architecture

The IntentCP Signal shortcut operates using a **two-stage LLM architecture**.

- **LLM #1 – URL Generator**
  - Converts user voice/text commands
  - Into a single executable **IntentCP Control URL**

- **LLM #2 – Response Summarizer**
  - Converts IntentCP server responses (JSON)
  - Into a **single, user-friendly spoken sentence**

---

## Which files should I use?

Most users only need the following two files.

- For Korean Siri responses:
  - `llm1_url_generator/v1.md`
  - `llm2_response_summarizer/v1.ko.md`

- For English Siri responses:
  - `llm1_url_generator/v1.md`
  - `llm2_response_summarizer/v1.en.md`

LLM #1 (URL Generator) is language-agnostic.
Only LLM #2 (Response Summarizer) determines the spoken language.

---

## Where to paste the prompts in the Shortcut

1. Open the iOS **Shortcuts** app
2. Tap **··· (three dots)** on the `Signal` shortcut card
3. In the shortcut editor, locate the input fields with the following placeholder text:

- `Paste LLM#1 prompt here / 이곳에 LLM#1 프롬프트 입력하세요`
- `Paste LLM#2 prompt here / 이곳에 LLM#2 프롬프트 입력하세요`

4. Copy and paste the full contents of each prompt file into the corresponding field.

### Language selection guide

- Use `v1.ko.md` for Korean Siri responses
- Use `v1.en.md` for English Siri responses

---

## LLM Provider Configuration

The Signal shortcut does not lock you into a specific LLM provider.
You may choose any of the following:

- `Private Cloud Compute`
- `ChatGPT`

> The prompt content remains the same regardless of the provider.

Language selection (KO / EN) is independent of the provider setting
and is determined solely by the selected **LLM #2 prompt file**.

---

## Versioning Policy

- `v1.md` represents the **current stable release**.
- When rules or output formats change, a new version (e.g. `v2.md`) is added.
- Older versions are preserved for compatibility and reference.
- Shortcut versions (`Signal v1.x`) and prompt versions (`v1 / v2`) are **managed independently**.

---