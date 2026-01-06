# IntentCP Signal Shortcut – Setup Checklist

이 문서는 **IntentCP + iOS 단축어(Signal)** 를 처음 설정할 때 필요한 최소 체크리스트입니다.  
아래 항목을 **위에서부터 순서대로** 확인하면 정상 동작 여부를 빠르게 검증할 수 있습니다.

---

## 1. 사전 준비 사항

- [ ] iOS 기기 (iPhone / iPad)
- [ ] iOS **단축어(Shortcuts)** 앱 설치
- [ ] IntentCP Core 서버 실행 중
  - 예: `http://127.0.0.1:8000`
  - 외부 접근 시 HTTPS 권장
- [ ] IntentCP Core에 디바이스 등록 완료 (`devices.toml`)

---

## 2. 단축어 설치

1. `install/iCloud-link.md` 에서 **Signal.shortcut** 설치 링크 열기 (실제 사용용)

참고:
- `shortcuts/Signal.shortcut` : 실제 사용/배포용 단축어 (직접 설정 필요)
- `shortcuts/Signal (Example).shortcut` : 예시 단축어
  - BASE_URL을 제외한 LLM 프롬프트 구조가 미리 채워져 있음
  - 각 입력 필드에 사용되는 **단축어 변수 구성 예시**를 확인하는 용도
2. 단축어 앱에서 **“단축어 추가”** 선택
3. 설치 후 단축어 이름이 `Signal` 인지 확인
4. 단축어 이름을 Siri로 호출할 이름으로 변경 (권장)

   ```
   기본 단축어 이름은 `Signal` 입니다.
   iOS에서는 **단축어 이름이 곧 Siri 호출 문장**이 되므로,
   한국어 사용자의 경우 이름을 한글로 변경하는 것을 권장합니다.

   예시:
   - Signal → 시그널

   이렇게 변경하면 Siri에게 다음과 같이 말할 수 있습니다.
   - "시리야, 시그널"

   변경 방법:
   1. 단축어 앱에서 `Signal` 단축어를 길게 누르거나 **···(점 3개)** 탭
   2. 상단의 단축어 이름 탭
   3. 원하는 이름으로 수정 (예: `시그널`)
   ```

---

## 3. 단축어 권한 설정 (중요)

Signal 단축어는 음성 입력과 네트워크 요청을 사용합니다.  
아래 권한이 허용되지 않으면 정상 동작하지 않습니다.

- [ ] **마이크 접근 허용**
- [ ] **음성 받아쓰기 허용**
- [ ] **네트워크 접근 허용**
- [ ] **“신뢰되지 않은 바로가기” 실행 허용**

> 최초 실행 시 iOS가 권한을 순차적으로 요청합니다.  
> 한 번 거부한 경우 **설정 → 개인정보 보호**에서 수동으로 다시 허용해야 합니다.

---

## 4. IntentCP 서버 주소(Base URL) 설정

배포용 Signal 단축어에는 **IntentCP 서버 주소(Base URL)** 가 기본값으로 포함되어 있습니다.  
사용 환경에 맞게 반드시 수정해야 합니다.

### 예시

- 로컬 테스트:
  ```
  http://127.0.0.1:8000
  ```
- 외부 접근:
  ```
  https://your-domain.example.com
  ```

### 수정 위치

단축어 편집 화면에서 아래 항목을 확인하세요.

- **LLM #1 (URL Generator) 프롬프트 내부**
- **HTTP 요청(Action)의 URL 입력 필드**

Signal.shortcut 에서는 Base URL이 별도의 입력 필드로 분리되어 있습니다.

이 필드에는 다음 값만 입력해야 합니다.
- IntentCP 서버의 호스트 + 포트 (또는 도메인)

예:
- http://127.0.0.1:8000
- https://your-domain.example.com

⚠️ 이 필드에는 `/tuya/...` 와 같은 경로를 포함하지 않습니다.

---

## 5. 단축어 편집 & LLM 프롬프트 설정

Signal 단축어는 **2단계 LLM 구조(LLM #1 / LLM #2)** 로 동작합니다.

---

### 5-1) 단축어 편집 화면 열기

1.  iOS **단축어 앱** 실행
2.  `Signal` 단축어 카드에서 **···(점 3개)** 탭
3.  단축어 편집 화면에서 아래 항목을 찾습니다.
  - **LLM #1 프롬프트 입력 칸**
  - **LLM #2 프롬프트 입력 칸**

> 배포용 단축어에는 각 입력 칸에  
> `이곳에 LLM#1 프롬프트 입력하세요 / Paste LLM#1 prompt here`  
> 와 같은 안내 문구가 포함되어 있습니다.

#### 필수 설정 항목 요약

Signal.shortcut 에서 사용자가 반드시 설정해야 하는 항목은 아래 3가지입니다.

1. **Base URL**
   - IntentCP 서버 주소
   - HTTP 요청 액션에서 사용

2. **LLM #1 프롬프트 (URL Generator)**
   - 자연어 명령 → Control URL 경로(`/tuya/...`) 생성

3. **LLM #2 프롬프트 (Response Summarizer)**
   - 서버 응답(JSON) → Siri가 읽을 한 문장 요약

각 항목은 단순 텍스트가 아니라,
**단축어 변수(Output of previous actions)** 를 참조하도록 구성되어 있습니다.

⚠️ 중요: 단축어 변수 설정

LLM 프롬프트 및 HTTP 요청 액션에는
이전 단계의 출력값을 참조하는 **단축어 변수**가 올바르게 연결되어야 합니다.

예시:
- LLM #1 출력 → HTTP 요청 URL에 변수로 삽입
- HTTP 요청 결과(JSON) → LLM #2 입력으로 전달

변수 연결 방식은 iOS 단축어 UI 상에서 확인해야 하며,
정확한 구성 예시는 `Signal (Example).shortcut` 파일을 참고하세요.

---

### 5-2) LLM 제공자 설정 (사용자 선택)

단축어 내 LLM 호출은 제공자를 고정하지 않습니다.  
아래 옵션 중 사용자가 원하는 방식을 선택해 사용할 수 있습니다.

- `비공개 클라우드 컴퓨팅 (Private Cloud Compute)`
- `ChatGPT`

> 어떤 제공자를 사용하더라도 **프롬프트 내용(LLM #1 / #2)은 동일**합니다.

---

### 5-3) LLM #1 – URL Generator

**역할**
- 사용자 음성/텍스트 명령을  
- IntentCP 서버에서 실행 가능한 **Control URL 한 줄**로 변환

**프롬프트 파일**
- `prompts/llm1_url_generator/v1.md`

**적용 방법**
1. 위 파일 내용을 복사
2. 단축어 편집 화면에서 **LLM #1 프롬프트 입력 칸**에 붙여넣기

---

### 5-4) LLM #2 – Response Summarizer

**역할**
- IntentCP 서버 응답(JSON)을  
- 사용자에게 들려줄 **한 문장 응답**으로 요약

**프롬프트 파일**
- `prompts/llm2_response_summarizer/v1.md`

**적용 방법**
1. 위 파일 내용을 복사
2. 단축어 편집 화면에서 **LLM #2 프롬프트 입력 칸**에 붙여넣기

---

### 5-5) 프롬프트 관리 기준

이 저장소(`intentcp-shortcuts-signal`)는  
**단축어 배포/설치에 필요한 프롬프트의 기준본(canonical)** 을 포함합니다.

- 일반 사용자: 이 저장소의 `prompts/`를 그대로 사용
- 프롬프트 자동 생성 / 확장 / 오케스트레이션:
  - `intentcp-llm-flows`에서 관리
  - 최종 산출물을 이 저장소로 **export** 하는 방식 권장

---

## 6. 기본 동작 테스트

아래 순서로 테스트하는 것을 권장합니다.

### 1) 단일 동작 테스트

말해보기:
- “거실 불 켜줘”

기대 동작: 

```
/tuya/living_light/on
```

---

### 2) 지연 동작 테스트

말해보기:
- “책상 불 5초 뒤에 꺼줘”

기대 동작:

```
/tuya/subdesk_light/off?delay=5
```

---

### 3) 시퀀스 테스트

말해보기:
- “불 다 켜고 5초 뒤에 책상 불 꺼줘”

기대 동작:

```
/tuya/sequence?actions=living_light:on,subdesk_light:on,subdesk_light:off?delay=5
```

---

## 7. 문제 해결 가이드

### ❌ 아무 반응이 없을 때
- IntentCP 서버 실행 여부 확인
- Base URL 오타 여부 확인
- iOS 네트워크 권한 허용 여부 확인

### ❌ 엉뚱한 동작이 실행될 때
- LLM #1 프롬프트 버전 확인
- 디바이스 별칭이 `devices.toml`과 일치하는지 확인

### ❌ 서버 응답은 성공인데 Siri 응답이 이상할 때
- LLM #2 프롬프트 확인
- sequence 응답 요약 규칙 확인

---
