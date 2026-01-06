# IntentCP Signal (iOS Shortcut)

**IntentCP Signal**은 iOS 단축어(Siri Shortcuts)를 통해
자연어 음성 명령을 **IntentCP 서버 제어 요청(URL)** 으로 연결하는
 음성 인터페이스 레이어입니다.

이 저장소는 **iOS 단축어 배포와 사용자 설정**에 초점을 둡니다.

iOS Shortcuts는 별도의 앱 설치 없이,
휴대폰의 음성 UX와 AI 기능을 그대로 활용할 수 있는
가장 얇은 진입점으로 선택되었습니다.

또한 Shortcuts 환경에서는 **Apple 온디바이스 AI**와  
**Apple Intelligence 기반 프라이빗 클라우드 추론**을  
자연스럽게 활용할 수 있어,
별도의 AI 인프라를 운영하지 않고도 음성 기반 의도 해석이 가능합니다.

---

## 이 저장소는 무엇을 담당하나요?

- iOS 단축어 `Signal.shortcut` 배포
- LLM 프롬프트(LLM #1 / LLM #2) 기준본 제공
- 사용자가 따라 할 수 있는 설치/설정 문서 제공

---

## 전체 IntentCP 구조에서의 위치

```
[사용자 음성]
      ↓
[iOS Siri / Signal Shortcut]
      ↓
[LLM #1] 자연어 → Control URL
      ↓
[IntentCP Core Server]
      ↓
[IoT / Device / Agent]
      ↓
[LLM #2] 응답 요약 → 사용자
```

Signal 단축어는 위 흐름에서 **Siri ↔ IntentCP Core를 연결하는 진입점** 역할을 합니다.

---

## Quick Start (요약)

1. iOS 단축어 설치
   - `install/iCloud-link.md`
2. 단축어 이름 변경 (권장)
   - `Signal` → `시그널`
   - Siri 호출 예: `"시리야, 시그널"`
3. LLM 프롬프트 설정
   - LLM #1 / #2 프롬프트 복사 & 붙여넣기
4. 음성으로 테스트
   - "거실 불 켜줘"

자세한 단계별 가이드는 아래 문서를 참고하세요.

👉 **install/setup-checklist.md**

---

## LLM 프롬프트 구조

Signal 단축어는 **2단계 LLM 구조**로 동작합니다.

### LLM #1 – URL Generator
- 사용자 음성/텍스트 명령을
- IntentCP 서버에서 실행 가능한 **Control URL 한 줄**로 변환

### LLM #2 – Response Summarizer
- IntentCP 서버 응답(JSON)을
- 사용자에게 들려줄 **한 문장 응답**으로 요약

프롬프트 파일 위치:
- `prompts/llm1_url_generator/v1.md`
- `prompts/llm2_response_summarizer/v1.md`

---

## 단축어 호출 이름에 대하여 (중요)

iOS에서는 **단축어 이름이 곧 Siri 호출 문장**이 됩니다.

기본 이름은 `Signal` 이지만,
한국어 사용자의 경우 아래와 같이 변경하는 것을 권장합니다.

- `Signal` → `시그널`

이렇게 변경하면 Siri에게 다음과 같이 말할 수 있습니다.

- `"시리야, 시그널"`

자세한 변경 방법은 설치 가이드에 포함되어 있습니다.

---
