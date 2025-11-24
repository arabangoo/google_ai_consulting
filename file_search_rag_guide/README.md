# File Search Store를 활용한 RAG 가이드 매뉴얼

## 목차
1. [개요](#개요)
2. [File Search Store란?](#file-search-store란)
3. [RAG 아키텍처](#rag-아키텍처)
4. [구현 가이드](#구현-가이드)
5. [API 레퍼런스](#api-레퍼런스)
6. [베스트 프랙티스](#베스트-프랙티스)
7. [트러블슈팅](#트러블슈팅)

---

## 개요

**RAG (Retrieval-Augmented Generation)**는 대규모 언어 모델(LLM)의 응답 품질을 향상시키기 위해 외부 지식 베이스에서 관련 정보를 검색하여 컨텍스트로 제공하는 기술입니다.

**File Search Store**는 문서를 업로드하면 자동으로 청킹(Chunking), 임베딩(Embedding), 인덱싱(Indexing)을 수행하여 효율적인 시맨틱 검색을 가능하게 하는 관리형 서비스입니다.

### 주요 장점
- **자동 문서 처리**: 업로드만 하면 청킹, 임베딩, 인덱싱이 자동 수행
- **시맨틱 검색**: 키워드가 아닌 의미 기반 검색
- **실시간 검색**: LLM 호출 시 자동으로 관련 문서 검색
- **확장성**: 대용량 문서도 효율적으로 처리

---

## File Search Store란?

File Search Store는 RAG 파이프라인을 단순화하는 관리형 벡터 데이터베이스입니다.

### 전통적인 RAG vs File Search Store

| 구분 | 전통적인 RAG | File Search Store |
|------|-------------|-------------------|
| 청킹 | 직접 구현 필요 | 자동 처리 |
| 임베딩 | 별도 모델 호출 필요 | 자동 생성 |
| 벡터 DB | 직접 구축/관리 | 관리형 서비스 |
| 검색 | 별도 쿼리 로직 필요 | API 호출로 통합 |
| 유지보수 | 복잡한 인프라 관리 | 최소화 |

### 데이터 흐름

#### 1. 파일 업로드 프로세스

```
파일 (PDF, DOCX, TXT)
    ↓
File Search Store API
    ↓
청킹 (Chunking) → 임베딩 (Embedding) → 벡터 인덱싱 (Indexing)
    ↓
검색 가능한 상태로 저장
```

#### 2. 검색 및 응답 생성 프로세스

```
사용자 질문
    ↓
시맨틱 검색 (File Search Store)
    ↓
관련 문서 청크 검색
    ↓
컨텍스트 주입 (프롬프트에 추가)
    ↓
LLM 응답 생성
    ↓
사용자에게 응답 반환
```

---

## RAG 아키텍처

### 핵심 컴포넌트

#### 1. File Search Store Manager
문서 업로드, 인덱싱, 검색을 담당하는 핵심 컴포넌트입니다.

```
FileSearchManager
├── store 관리 (생성/로드)
├── 파일 업로드 및 인덱싱
├── 컨텍스트 검색
└── 메타데이터 관리
```

#### 2. 메타데이터 관리
업로드된 파일 정보를 로컬에 저장하여 Store 상태를 추적합니다.

```json
{
  "store_name": "fileSearchStores/xxxxx",
  "uploaded_files": [
    {
      "name": "documents/xxxxx",
      "display_name": "example.pdf",
      "uri": "documents/xxxxx",
      "mime_type": "application/pdf",
      "state": "ACTIVE",
      "upload_time": 1699999999.0
    }
  ]
}
```

#### 3. 검색 및 컨텍스트 주입
사용자 질문에 대해 관련 문서를 검색하고 LLM 컨텍스트에 주입합니다.

---

## 구현 가이드

### Step 1: 환경 설정

```bash
# 필요한 패키지 설치
pip install google-genai python-dotenv

# 환경 변수 설정 (.env 파일)
GEMINI_API_KEY=your_api_key_here
```

### Step 2: File Search Manager 초기화

```python
from google import genai
from google.genai import types

class FileSearchManager:
    def __init__(self):
        # API 클라이언트 초기화
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)

        # 메타데이터 저장소 설정
        self.metadata_file = Path("data/file_search_metadata.json")
        self.metadata = self._load_metadata()

        # Store 참조 초기화
        self.store = None
        self.store_name = None
```

### Step 3: Store 생성 및 관리

```python
async def _ensure_store_initialized(self):
    """Store가 초기화되었는지 확인하고, 없으면 생성"""

    # 기존 store 확인
    if self.metadata.get("store_name"):
        try:
            self.store = self.client.file_search_stores.get(
                name=self.metadata["store_name"]
            )
            self.store_name = self.store.name
            return
        except Exception:
            pass  # 기존 store가 없으면 새로 생성

    # 새로운 store 생성
    self.store = self.client.file_search_stores.create(
        config={'display_name': 'My RAG Store'}
    )
    self.store_name = self.store.name

    # 메타데이터 저장
    self.metadata["store_name"] = self.store_name
    self._save_metadata()
```

### Step 4: 파일 업로드

```python
async def upload_file(self, file_path: str, display_name: str):
    """파일을 File Search Store에 업로드"""

    # Store 초기화 확인
    await self._ensure_store_initialized()

    # 파일 업로드 (비동기 작업)
    operation = self.client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=self.store_name,
        config={'display_name': display_name}
    )

    # 처리 완료 대기 (청킹, 임베딩, 인덱싱)
    while not operation.done:
        await asyncio.sleep(2)
        operation = self.client.operations.get(operation)

    # 결과 반환
    return {
        "document_name": operation.response.document_name,
        "display_name": display_name,
        "state": "ACTIVE"
    }
```

### Step 5: 컨텍스트 검색

```python
async def get_context(self, query: str):
    """쿼리와 관련된 컨텍스트 검색"""

    await self._ensure_store_initialized()

    # LLM을 사용해 File Search 수행
    response = self.client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"다음 질문과 관련된 정보를 문서에서 찾아주세요: {query}",
        config=types.GenerateContentConfig(
            temperature=0.1,  # 정확한 검색을 위해 낮은 temperature
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[self.store_name]
                    )
                )
            ]
        )
    )

    return {
        "store_name": self.store_name,
        "searched_context": response.text
    }
```

### Step 6: LLM 응답 생성 (RAG 통합)

```python
async def generate_response(self, user_message: str, file_search_context: dict):
    """RAG 컨텍스트를 포함한 LLM 응답 생성"""

    # 컨텍스트가 있으면 프롬프트에 추가
    if file_search_context and file_search_context.get("searched_context"):
        full_message = f"""<참고 문서 내용>
{file_search_context["searched_context"]}
</참고 문서 내용>

사용자 질문: {user_message}

위 문서 내용을 참고하여 답변해주세요."""
    else:
        full_message = user_message

    # LLM 응답 생성 (File Search Tool 포함)
    response = self.client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_message,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[file_search_context["store_name"]]
                    )
                )
            ]
        )
    )

    return response.text
```

---

## API 레퍼런스

### File Search Store API

#### Store 생성
```python
store = client.file_search_stores.create(
    config={'display_name': 'Store Name'}
)
```

#### Store 조회
```python
store = client.file_search_stores.get(name="fileSearchStores/xxxxx")
```

#### 파일 업로드
```python
operation = client.file_search_stores.upload_to_file_search_store(
    file="path/to/file.pdf",
    file_search_store_name="fileSearchStores/xxxxx",
    config={'display_name': 'Document Name'}
)
```

#### 작업 상태 확인
```python
operation = client.operations.get(operation)
if operation.done:
    result = operation.response
```

### File Search Tool 설정

```python
from google.genai import types

config = types.GenerateContentConfig(
    tools=[
        types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=["fileSearchStores/xxxxx"]
            )
        )
    ]
)
```

---

## 베스트 프랙티스

### 1. 파일 형식 최적화

| 형식 | 권장 사항 |
|------|----------|
| PDF | 텍스트 추출 가능한 PDF 권장, 스캔 이미지는 OCR 필요 |
| DOCX | 서식이 복잡하지 않은 문서 권장 |
| TXT | 가장 안정적인 처리 |
| JSON | 구조화된 데이터에 적합 |

### 2. 청킹 전략
- File Search Store는 자동 청킹을 수행하지만, 문서 구조가 명확할수록 검색 품질 향상
- 긴 문서는 섹션별로 분리하여 업로드 고려
- 제목, 소제목이 명확한 문서 구조 권장

### 3. 검색 품질 향상

```python
# 검색 쿼리 최적화
search_query = f"""다음 질문과 관련된 정보를 문서에서 찾아서
원문 그대로 인용해주세요: {user_query}"""

# 낮은 temperature로 정확한 검색
config = types.GenerateContentConfig(
    temperature=0.1,
    max_output_tokens=2000
)
```

### 4. 메타데이터 관리
- 업로드된 파일 정보를 로컬에 저장하여 Store 상태 추적
- Store 이름을 영구 저장하여 재시작 시 재사용
- 삭제된 파일은 메타데이터에서도 제거

### 5. 에러 처리

```python
async def safe_upload(self, file_path, display_name):
    try:
        result = await self.upload_file(file_path, display_name)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 6. 컨텍스트 주입 전략

```python
# 관련성 판단이 필요한 경우
prompt = f"""<참고 문서 내용>
{rag_context}
</참고 문서 내용>

사용자 질문: {message}

**중요 지침:**
- 문서 내용은 참고용입니다. 질문과 관련이 있을 때만 활용하세요.
- 일반적인 질문이라면 문서 내용을 무시하고 자연스럽게 답변하세요.
- 문서를 참조할 때는 출처를 명시해주세요."""
```

---

## 트러블슈팅

### 자주 발생하는 문제

#### 1. Store를 찾을 수 없음
```
Error: Store not found
```
**해결**: 메타데이터 파일을 확인하고, Store가 삭제되었다면 새로 생성

```python
# 메타데이터 초기화 후 재시도
self.metadata = {"store_name": None, "uploaded_files": []}
await self._ensure_store_initialized()
```

#### 2. 파일 처리 시간 초과
```
Error: Operation timeout
```
**해결**: 대용량 파일은 처리 시간이 길어질 수 있음. 폴링 간격 조정

```python
# 폴링 간격 늘리기
while not operation.done:
    await asyncio.sleep(5)  # 2초 → 5초
    operation = self.client.operations.get(operation)
```

#### 3. 검색 결과가 없음
```
searched_context: None
```
**해결**:
- 업로드된 파일이 완전히 처리되었는지 확인
- 검색 쿼리가 문서 내용과 관련 있는지 확인
- 파일 형식이 지원되는지 확인

#### 4. Rate Limit 에러
```
Error: 429 Resource exhausted
```
**해결**: 지수 백오프(Exponential Backoff) 적용

```python
max_retries = 3
retry_delay = 2

for attempt in range(max_retries):
    try:
        result = await api_call()
        break
    except RateLimitError:
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # 2초 → 4초 → 8초
```

#### 5. 메타데이터 동기화 문제
**해결**: 주기적으로 실제 Store 상태와 메타데이터 동기화

```python
async def sync_metadata(self):
    """Store 상태와 메타데이터 동기화"""
    try:
        store = self.client.file_search_stores.get(
            name=self.metadata["store_name"]
        )
        # Store가 존재하면 정상
    except Exception:
        # Store가 없으면 메타데이터 초기화
        self.metadata = {"store_name": None, "uploaded_files": []}
        self._save_metadata()
```

---

## 지원 파일 형식

| 형식 | 확장자 | 비고 |
|------|--------|------|
| PDF | .pdf | 텍스트 추출 가능한 PDF |
| Word | .docx | Microsoft Word 문서 |
| 텍스트 | .txt | 일반 텍스트 파일 |
| JSON | .json | 구조화된 데이터 |
| 이미지 | .png, .jpg, .jpeg | 이미지 분석 (제한적) |

---

## 참고 자료

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Google File Search Documentation](https://ai.google.dev/gemini-api/docs/file-search)
