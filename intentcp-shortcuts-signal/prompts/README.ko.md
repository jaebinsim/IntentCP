# Prompts (LLM #1 / LLM #2)

이 폴더는 **IntentCP Signal 단축어**에서 사용하는 LLM 프롬프트를 버전별로 관리합니다.  
사용자는 이 폴더의 프롬프트를 복사하여 iOS 단축어(Signal)에 직접 붙여넣어 사용합니다.

---

## 프롬프트 구조

IntentCP Signal 단축어는 **2단계 LLM 구조**로 동작합니다.

- **LLM #1 – URL Generator**
  - 사용자 음성/텍스트 명령을
  - IntentCP 서버에서 실행 가능한 **Control URL 한 줄**로 변환

- **LLM #2 – Response Summarizer**
  - IntentCP 서버 응답(JSON)을
  - 사용자가 듣기 좋은 **한 문장 응답**으로 요약

---

## 어떤 파일을 사용하면 되나요?

대부분의 사용자는 아래 두 파일만 사용하면 됩니다.

- 한국어 응답:
  - `llm1_url_generator/v1.md`
  - `llm2_response_summarizer/v1.ko.md`
- 영어 응답:
  - `llm1_url_generator/v1.md`
  - `llm2_response_summarizer/v1.en.md`

LLM #1(URL Generator)는 언어에 독립적이며,  
LLM #2(Response Summarizer)만 언어별 파일을 선택해 사용합니다.
---

## 단축어에 붙여넣는 위치

1. iOS **단축어 앱** 실행
2. `Signal` 단축어 카드에서 **···(점 3개)** 탭
3. 단축어 편집 화면에서 아래 안내 문구가 있는 입력 칸을 찾습니다.

- `이곳에 LLM#1 프롬프트 입력하세요 / Paste LLM#1 prompt here`
- `이곳에 LLM#2 프롬프트 입력하세요 / Paste LLM#2 prompt here`

4. 각 입력 칸에 해당 프롬프트 파일의 내용을  
   **그대로 복사 / 붙여넣기** 합니다.

※ 언어 선택 가이드
- 한국어 Siri 응답을 원하면 `v1.ko.md`를 사용하세요.
- 영어 Siri 응답을 원하면 `v1.en.md`를 사용하세요.

---

## LLM 제공자 설정

Signal 단축어는 LLM 제공자를 고정하지 않습니다.  
아래 옵션 중 사용자가 원하는 방식을 선택할 수 있습니다.

- `비공개 클라우드 컴퓨팅 (Private Cloud Compute)`
- `ChatGPT`

> 어떤 제공자를 사용하더라도 **프롬프트 내용은 동일**합니다.

언어(KO / EN) 선택은 제공자 설정과 무관하며,  
선택한 LLM #2 프롬프트 파일에 의해 결정됩니다.

---

## 버전 관리 규칙

- `v1.md`는 **현재 배포 기준 안정 버전**입니다.
- 규칙이나 출력 포맷이 변경될 경우 `v2.md`를 추가합니다.
- 기존 버전은 호환성과 참고를 위해 유지합니다.
- 단축어 버전(`Signal v1.x`)과 프롬프트 버전(`v1 / v2`)은 **서로 독립적**입니다.

---

## 개발자 참고 사항

이 저장소(`intentcp-shortcuts-signal`)는  
**사용자가 직접 복사해 사용하는 최종 프롬프트(canonical output)** 를 관리합니다.

- 프롬프트 생성 / 템플릿화 / 자동화는  
  `intentcp-llm-flows` 프로젝트에서 수행
- 해당 프로젝트의 산출물을  
  이 저장소의 `prompts/`로 export 하는 방식을 권장합니다.

이렇게 역할을 분리하면,  
단축어 배포 문서와 프롬프트가 안정적으로 유지됩니다.