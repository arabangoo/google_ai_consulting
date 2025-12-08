# GCP Docker 컨테이너 배포 가이드

> Windows 환경에서 Docker Desktop을 사용하여 FastAPI/Django 애플리케이션을 GCP에 배포하는 종합 가이드

## 📋 목차

- [개요](#개요)
- [시작하기 전에](#시작하기-전에)
- [빠른 시작 5분 완성](#빠른-시작-5분-완성)
- [개발 환경](#개발-환경)
- [프로젝트 구조](#프로젝트-구조)
- [사전 준비](#사전-준비)
- [FastAPI 가이드](#fastapi-가이드)
- [Django 가이드](#django-가이드)
- [환경 변수 관리](#환경-변수-관리)
- [데이터베이스 연결](#데이터베이스-연결)
- [배포 옵션](#배포-옵션)
- [실전 예제](#실전-예제)
- [성능 최적화](#성능-최적화)
- [CI/CD 파이프라인](#cicd-파이프라인)
- [트러블슈팅](#트러블슈팅)
- [FAQ](#faq)

---

## 개요

이 가이드는 Windows 로컬 환경에서 Docker Desktop을 사용하여 컨테이너 이미지를 빌드하고, GCP의 다양한 서비스에 배포하는 방법을 다룹니다.

### 지원하는 프레임워크
- **FastAPI**: 고성능 비동기 Python 웹 프레임워크
- **Django**: 완전한 기능을 갖춘 Python 웹 프레임워크

### 지원하는 GCP 배포 옵션
1. **Cloud Run**: 완전 관리형 서버리스 컨테이너 플랫폼 (⭐ 초급)
2. **GKE (Google Kubernetes Engine)**: Kubernetes 기반 오케스트레이션 (⭐⭐ 중급)
3. **GKE Autopilot**: 완전 관리형 Kubernetes (⭐⭐ 중급)
4. **Compute Engine + Docker**: VM 기반 컨테이너 배포 (⭐ 초급)

---

## 시작하기 전에

### 필요한 배경 지식

이 가이드를 효과적으로 따라하기 위해 다음 기본 지식이 있으면 좋습니다:

#### 필수
- **기본 프로그래밍**: Python 기초 문법
- **터미널 사용**: PowerShell 또는 명령 프롬프트 기본 명령어
- **웹 개념**: HTTP, REST API 기본 이해
- **GCP 계정**: 활성화된 GCP 계정 (신용카드 등록 필요)

#### 권장
- **Docker 기초**: 컨테이너와 이미지 개념
- **Git 기초**: 버전 관리 기본 명령어
- **클라우드 기초**: GCP 서비스 기본 개념

### 학습 리소스

Docker나 GCP가 처음이신가요? 다음 리소스를 참고하세요:

- **Docker 입문**: [Docker 공식 튜토리얼](https://docs.docker.com/get-started/)
- **GCP 기초**: [Google Cloud 시작하기](https://cloud.google.com/getting-started)
- **FastAPI 기초**: [FastAPI 튜토리얼](https://fastapi.tiangolo.com/tutorial/)
- **Django 기초**: [Django 튜토리얼](https://docs.djangoproject.com/en/5.0/intro/tutorial01/)

### 예상 소요 시간

- **환경 설정**: 30분 ~ 1시간
- **첫 배포 (Cloud Run)**: 10 ~ 20분
- **중급 배포 (GKE)**: 1 ~ 2시간
- **고급 배포 (GKE Autopilot)**: 1.5 ~ 3시간

---

## 빠른 시작 (5분 완성)

바로 시작하고 싶으신가요? 다음 단계를 따라 5분 안에 FastAPI 앱을 로컬에서 실행해보세요!

### 전제 조건
- Docker Desktop이 설치되어 실행 중이어야 합니다

### 단계별 가이드

#### 1. 프로젝트 디렉토리 생성
```powershell
mkdir C:\temp\fastapi-gcp-quick-start
cd C:\temp\fastapi-gcp-quick-start
```

#### 2. 간단한 FastAPI 앱 작성
**main.py** 파일 생성:
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on GCP!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**requirements.txt** 파일 생성:
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
```

#### 3. Dockerfile 생성
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 4. 빌드 및 실행
```powershell
# 이미지 빌드
docker build -t fastapi-gcp .

# 컨테이너 실행
docker run -d -p 8080:8080 --name fastapi-app fastapi-gcp

# 작동 확인
curl http://localhost:8080
# 또는 브라우저에서: http://localhost:8080/docs
```

#### 5. 정리
```powershell
# 컨테이너 중지 및 제거
docker stop fastapi-app
docker rm fastapi-app
```

축하합니다! 첫 Docker 컨테이너 앱을 실행했습니다. 이제 본격적인 가이드를 따라가보세요.

---

## 개발 환경

### 필수 요구사항
```powershell
# 버전 확인
python --version   # Python 3.11 이상 권장 (Python 3.12 최신)
node --version     # Node.js 20 LTS 권장 (Django만 사용 시 불필요)
docker --version   # Docker Desktop 24.0 이상
gcloud --version   # Google Cloud SDK 최신 버전
```

### 선택사항
- **VSCode**: 추천 IDE
- **PowerShell 7**: 향상된 스크립팅 경험
- **Git**: 버전 관리용
- **kubectl**: Kubernetes CLI (GKE 사용 시)

---

## 프로젝트 구조

```
gcp_container_guide/
├── README.md (현재 파일)
│
├── fastapi-gcp/                    # FastAPI 프로젝트
│   ├── 0-windows-setup/
│   │   ├── README.md              # Windows 환경 설정 가이드
│   │   ├── install-docker.md
│   │   └── install-gcloud-cli.md
│   │
│   ├── app/                       # FastAPI 애플리케이션
│   │   ├── main.py               # FastAPI 앱 진입점
│   │   ├── requirements.txt      # Python 의존성
│   │   └── .env.example          # 환경변수 템플릿
│   │
│   ├── Dockerfile                # 멀티스테이지 빌드
│   ├── docker-compose.yml        # 로컬 개발 환경
│   ├── .dockerignore
│   │
│   ├── scripts/                  # 자동화 스크립트
│   │   ├── build-local.ps1       # 로컬 빌드
│   │   ├── run-local.ps1         # 로컬 실행
│   │   ├── push-to-ar.ps1        # Artifact Registry 푸시
│   │   └── test-api.ps1          # API 테스트
│   │
│   ├── deployments/
│   │   ├── 1-cloud-run/
│   │   │   ├── README.md
│   │   │   └── service.yaml
│   │   │
│   │   ├── 2-gke-standard/
│   │   │   ├── README.md
│   │   │   └── k8s/
│   │   │       ├── deployment.yaml
│   │   │       ├── service.yaml
│   │   │       └── ingress.yaml
│   │   │
│   │   ├── 3-gke-autopilot/
│   │   │   ├── README.md
│   │   │   └── k8s/
│   │   │       ├── deployment.yaml
│   │   │       └── service.yaml
│   │   │
│   │   └── 4-compute-engine/
│   │       ├── README.md
│   │       └── startup-script.sh
│   │
│   └── README.md                 # FastAPI 프로젝트 가이드
│
└── django-gcp/                    # Django 프로젝트
    └── (FastAPI와 동일한 구조)
```

---

## 사전 준비

### 1. Docker Desktop 설치 및 설정

#### 설치
1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드
2. 설치 프로그램 실행
3. **WSL2 백엔드 옵션 선택** (필수)
4. 재시작 후 Docker Desktop 실행

#### 설정 확인
```powershell
# PowerShell에서 실행
docker --version
# 출력 예: Docker version 24.0.7, build afdd53b

docker compose version
# 출력 예: Docker Compose version v2.23.0

# Docker 데몬 실행 확인
docker ps
# 정상이면 컨테이너 목록 출력 (비어있어도 OK)
```

#### Docker Desktop 리소스 설정
1. Docker Desktop 열기
2. **Settings > Resources > WSL Integration**
3. 권장 설정:
   - **Memory**: 4GB 이상 (8GB 권장)
   - **CPUs**: 2 이상 (4 권장)
   - **Disk**: 20GB 이상
   - **Swap**: 1GB

### 2. Google Cloud SDK 설치

#### Windows에서 Google Cloud SDK 설치
```powershell
# PowerShell에서 실행
# 설치 프로그램 다운로드
# https://cloud.google.com/sdk/docs/install-sdk#windows

# 또는 Chocolatey 사용
choco install gcloudsdk

# 또는 직접 다운로드 및 설치
# https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
```

#### 설치 확인
```powershell
gcloud --version
# 출력 예: Google Cloud SDK 458.0.0
```

#### GCP 초기화 및 인증
```powershell
# gcloud 초기화
gcloud init

# 브라우저에서 인증 후 프로젝트 선택

# 또는 수동 설정
gcloud auth login
gcloud config set project [PROJECT_ID]
gcloud config set compute/region asia-northeast3  # 서울 리전
gcloud config set compute/zone asia-northeast3-a
```

#### 프로젝트 생성 (선택사항)
```powershell
# 새 프로젝트 생성
gcloud projects create my-fastapi-project --name="My FastAPI Project"

# 프로젝트 설정
gcloud config set project my-fastapi-project

# 프로젝트 확인
gcloud config get-value project
```

#### 필요한 API 활성화
```powershell
# Cloud Run API
gcloud services enable run.googleapis.com

# Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# GKE API
gcloud services enable container.googleapis.com

# Cloud SQL API
gcloud services enable sqladmin.googleapis.com

# Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Compute Engine API (Compute Engine 사용 시)
gcloud services enable compute.googleapis.com
```

### 3. Git 설치 (선택사항)

```powershell
# winget 사용 (Windows 11 또는 Windows 10 최신 버전)
winget install --id Git.Git -e --source winget

# 설치 확인
git --version
```

### 4. kubectl 설치 (GKE 사용 시)

```powershell
# gcloud를 통해 설치
gcloud components install kubectl

# 설치 확인
kubectl version --client
```

---

## FastAPI 가이드

### 빠른 시작

#### 1. 프로젝트 클론 또는 생성
```powershell
# GitHub에서 클론
git clone https://github.com/your-repo/gcp_container_guide.git
cd gcp_container_guide\fastapi-gcp

# 또는 새로 생성
mkdir fastapi-gcp
cd fastapi-gcp
```

#### 2. 로컬에서 빌드 및 실행
```powershell
# 이미지 빌드
.\scripts\build-local.ps1

# 로컬에서 실행
.\scripts\run-local.ps1

# 브라우저에서 확인
# http://localhost:8080
# http://localhost:8080/docs  (Swagger UI)
```

### FastAPI 애플리케이션 예제

#### app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI(
    title="FastAPI on GCP",
    description="FastAPI 애플리케이션 GCP 배포 예제",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    message: str
    environment: str

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/")
async def root():
    return {
        "message": "Hello from FastAPI on GCP!",
        "environment": os.getenv("ENV", "development")
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for GCP"""
    return HealthResponse(
        status="healthy",
        message="Application is running",
        environment=os.getenv("ENV", "development")
    )

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

if __name__ == "__main__":
    # Cloud Run은 PORT 환경 변수를 제공
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
```

#### app/requirements.txt
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
python-multipart==0.0.12
```

### Dockerfile (멀티스테이지 빌드)

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# 의존성 설치
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# 보안: 비-root 사용자 생성
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Builder 스테이지에서 설치한 패키지 복사
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# 애플리케이션 코드 복사
COPY app/ .

# 소유권 변경
RUN chown -R appuser:appuser /app

# 비-root 사용자로 전환
USER appuser

# Cloud Run은 PORT 환경 변수를 제공 (기본값 8080)
ENV PORT=8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# 실행 명령 - Cloud Run을 위해 PORT 환경 변수 사용
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
```

### .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# 테스트 및 개발 도구
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.ruff_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# 문서
*.md
docs/
examples/

# 로그
*.log

# 환경 변수
.env
.env.*
!.env.example

# 기타
node_modules/
.DS_Store
Thumbs.db

# GCP
.gcloudignore
```

### docker-compose.yml (로컬 개발용)

```yaml
version: '3.8'

services:
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fastapi-gcp-app
    ports:
      - "8080:8080"
    environment:
      - ENV=development
      - DEBUG=true
      - PORT=8080
    volumes:
      - ./app:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8080 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL (필요한 경우)
  db:
    image: postgres:16-alpine
    container_name: fastapi-gcp-db
    environment:
      - POSTGRES_DB=fastapi_db
      - POSTGRES_USER=fastapi_user
      - POSTGRES_PASSWORD=fastapi_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### PowerShell 스크립트 예제

#### scripts/build-local.ps1
```powershell
# FastAPI 로컬 빌드 스크립트
Write-Host "================================" -ForegroundColor Cyan
Write-Host "FastAPI Docker 이미지 빌드 시작" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 현재 디렉토리 확인
$currentDir = Get-Location
Write-Host "현재 디렉토리: $currentDir" -ForegroundColor Yellow

# Dockerfile 존재 확인
if (-not (Test-Path "Dockerfile")) {
    Write-Host "❌ Dockerfile을 찾을 수 없습니다!" -ForegroundColor Red
    exit 1
}

# 이미지 이름 설정
$IMAGE_NAME = "fastapi-gcp"
$IMAGE_TAG = "latest"

# 빌드 시작
Write-Host "`n🔨 이미지 빌드 중..." -ForegroundColor Green
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ 빌드 성공!" -ForegroundColor Green
    Write-Host "이미지 이름: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Cyan

    # 이미지 크기 확인
    Write-Host "`n📊 이미지 정보:" -ForegroundColor Yellow
    docker images ${IMAGE_NAME}:${IMAGE_TAG}
} else {
    Write-Host "`n❌ 빌드 실패!" -ForegroundColor Red
    exit 1
}

Write-Host "`n다음 단계:" -ForegroundColor Yellow
Write-Host "1. 로컬 실행: .\scripts\run-local.ps1" -ForegroundColor White
Write-Host "2. Artifact Registry 푸시: .\scripts\push-to-ar.ps1" -ForegroundColor White
```

#### scripts/run-local.ps1
```powershell
# FastAPI 로컬 실행 스크립트
Write-Host "================================" -ForegroundColor Cyan
Write-Host "FastAPI 로컬 실행" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$IMAGE_NAME = "fastapi-gcp"
$IMAGE_TAG = "latest"
$CONTAINER_NAME = "fastapi-local"
$PORT = "8080"

# 기존 컨테이너 중지 및 제거
Write-Host "`n🧹 기존 컨테이너 정리 중..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME 2>$null
docker rm $CONTAINER_NAME 2>$null

# 컨테이너 실행
Write-Host "`n🚀 컨테이너 시작 중..." -ForegroundColor Green
docker run -d `
    --name $CONTAINER_NAME `
    -p ${PORT}:8080 `
    -e PORT=8080 `
    ${IMAGE_NAME}:${IMAGE_TAG}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ 컨테이너 실행 성공!" -ForegroundColor Green
    Write-Host "`n📡 접속 정보:" -ForegroundColor Yellow
    Write-Host "  - API: http://localhost:${PORT}" -ForegroundColor White
    Write-Host "  - Swagger UI: http://localhost:${PORT}/docs" -ForegroundColor White
    Write-Host "  - ReDoc: http://localhost:${PORT}/redoc" -ForegroundColor White

    # 로그 확인
    Write-Host "`n📋 컨테이너 로그 (Ctrl+C로 종료):" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    docker logs -f $CONTAINER_NAME
} else {
    Write-Host "`n❌ 컨테이너 실행 실패!" -ForegroundColor Red
    exit 1
}
```

#### scripts/push-to-ar.ps1
```powershell
# Artifact Registry에 이미지 푸시하는 스크립트
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Artifact Registry에 이미지 푸시" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 설정값
$REGION = "asia-northeast3"  # 서울 리전
$IMAGE_NAME = "fastapi-gcp"
$IMAGE_TAG = "latest"

# GCP 프로젝트 ID 가져오기
Write-Host "`n🔍 GCP 프로젝트 정보 확인 중..." -ForegroundColor Yellow
$PROJECT_ID = (gcloud config get-value project 2>$null)

if (-not $PROJECT_ID) {
    Write-Host "❌ GCP 프로젝트가 설정되지 않았습니다!" -ForegroundColor Red
    Write-Host "gcloud init을 먼저 실행하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host "프로젝트 ID: $PROJECT_ID" -ForegroundColor Green

# Docker를 Artifact Registry 인증에 구성
Write-Host "`n🔐 Artifact Registry 인증 설정 중..." -ForegroundColor Yellow
gcloud auth configure-docker ${REGION}-docker.pkg.dev

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Artifact Registry 인증 실패!" -ForegroundColor Red
    exit 1
}

# Artifact Registry 리포지토리 존재 확인 및 생성
Write-Host "`n📦 Artifact Registry 리포지토리 확인 중..." -ForegroundColor Yellow
$repoExists = gcloud artifacts repositories describe fastapi-repo `
    --location=$REGION 2>$null

if (-not $repoExists) {
    Write-Host "리포지토리가 없습니다. 생성 중..." -ForegroundColor Yellow
    gcloud artifacts repositories create fastapi-repo `
        --repository-format=docker `
        --location=$REGION `
        --description="FastAPI Docker images"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 리포지토리 생성 완료!" -ForegroundColor Green
    } else {
        Write-Host "❌ 리포지토리 생성 실패!" -ForegroundColor Red
        exit 1
    }
}

# 이미지 태깅
Write-Host "`n🏷️  이미지 태깅 중..." -ForegroundColor Yellow
$AR_IMAGE = "${REGION}-docker.pkg.dev/${PROJECT_ID}/fastapi-repo/${IMAGE_NAME}:${IMAGE_TAG}"

docker tag ${IMAGE_NAME}:${IMAGE_TAG} $AR_IMAGE

# 이미지 푸시
Write-Host "`n⬆️  이미지 푸시 중..." -ForegroundColor Yellow
docker push $AR_IMAGE

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ 이미지 푸시 성공!" -ForegroundColor Green
    Write-Host "Artifact Registry 이미지 URI: $AR_IMAGE" -ForegroundColor Cyan

    Write-Host "`n다음 단계:" -ForegroundColor Yellow
    Write-Host "1. Cloud Run 배포: .\deployments\1-cloud-run\README.md 참조" -ForegroundColor White
    Write-Host "2. GKE 배포: .\deployments\2-gke-standard\README.md 참조" -ForegroundColor White
    Write-Host "3. GKE Autopilot 배포: .\deployments\3-gke-autopilot\README.md 참조" -ForegroundColor White
} else {
    Write-Host "`n❌ 이미지 푸시 실패!" -ForegroundColor Red
    exit 1
}
```

#### scripts/test-api.ps1
```powershell
# API 테스트 스크립트
Write-Host "================================" -ForegroundColor Cyan
Write-Host "FastAPI 엔드포인트 테스트" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$BASE_URL = "http://localhost:8080"

# 1. Health Check
Write-Host "`n1️⃣  Health Check 테스트" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
Write-Host "응답: $($response | ConvertTo-Json)" -ForegroundColor Green

# 2. Root Endpoint
Write-Host "`n2️⃣  Root Endpoint 테스트" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/" -Method Get
Write-Host "응답: $($response | ConvertTo-Json)" -ForegroundColor Green

# 3. GET Item
Write-Host "`n3️⃣  GET Item 테스트" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/items/42?q=test" -Method Get
Write-Host "응답: $($response | ConvertTo-Json)" -ForegroundColor Green

# 4. POST Item
Write-Host "`n4️⃣  POST Item 테스트" -ForegroundColor Yellow
$body = @{
    name = "Test Item"
    description = "Test Description"
    price = 99.99
    tax = 10.0
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "$BASE_URL/items/" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

Write-Host "응답: $($response | ConvertTo-Json)" -ForegroundColor Green

Write-Host "`n✅ 모든 테스트 완료!" -ForegroundColor Green
```

---

## Django 가이드

### Django 애플리케이션 예제

#### Django 프로젝트 구조
```
django-gcp/
├── app/
│   ├── manage.py
│   ├── requirements.txt
│   ├── myproject/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── api/
│       ├── __init__.py
│       ├── views.py
│       └── urls.py
```

#### app/requirements.txt
```txt
Django==5.0.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
django-environ==0.11.2
whitenoise==6.6.0
django-cors-headers==4.3.1
```

### Django Dockerfile

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 비-root 사용자
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Builder에서 패키지 복사
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# 애플리케이션 코드
COPY app/ .

# Static 파일 수집
RUN python manage.py collectstatic --noinput

# 소유권 변경
RUN chown -R appuser:appuser /app

USER appuser

# Cloud Run은 PORT 환경 변수 제공
ENV PORT=8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health/')" || exit 1

# Gunicorn으로 실행
CMD gunicorn myproject.wsgi:application --bind 0.0.0.0:${PORT} --workers 3
```

### Django docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: django-gcp-app
    ports:
      - "8080:8080"
    environment:
      - DEBUG=True
      - SECRET_KEY=django-insecure-dev-key
      - DATABASE_URL=postgresql://django_user:django_password@db:5432/django_db
      - PORT=8080
    depends_on:
      - db
    volumes:
      - ./app:/app
    command: python manage.py runserver 0.0.0.0:8080

  db:
    image: postgres:16-alpine
    container_name: django-gcp-db
    environment:
      - POSTGRES_DB=django_db
      - POSTGRES_USER=django_user
      - POSTGRES_PASSWORD=django_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 환경 변수 관리

환경 변수를 안전하게 관리하는 것은 프로덕션 배포에서 매우 중요합니다.

### 로컬 개발 환경

#### .env 파일 사용

**.env.example** (버전 관리에 포함)
```bash
# Application Settings
ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# GCP Settings
GCP_PROJECT_ID=my-project-id
GCP_REGION=asia-northeast3
GCS_BUCKET_NAME=my-app-bucket

# API Keys (절대 실제 값을 넣지 마세요!)
API_KEY=your-api-key-here
THIRD_PARTY_API_KEY=your-third-party-key
```

**.env** (버전 관리에서 제외, .gitignore에 추가)
```bash
ENV=development
DEBUG=true
SECRET_KEY=super-secret-key-do-not-commit
DATABASE_URL=postgresql://myuser:mypass@localhost:5432/mydb
API_KEY=real-api-key-value
```

**.gitignore**
```
.env
*.env
!.env.example
```

#### FastAPI에서 환경 변수 사용

**config.py**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    env: str = "development"
    debug: bool = True
    secret_key: str
    database_url: str
    api_key: str
    gcp_project_id: str
    gcp_region: str = "asia-northeast3"

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

# 사용 예
settings = get_settings()
```

**main.py**
```python
from fastapi import FastAPI, Depends
from config import get_settings, Settings

app = FastAPI()

@app.get("/config")
def read_config(settings: Settings = Depends(get_settings)):
    return {
        "env": settings.env,
        "debug": settings.debug,
        "gcp_project": settings.gcp_project_id,
        "gcp_region": settings.gcp_region,
        # 민감한 정보는 노출하지 않음
    }
```

**requirements.txt에 추가**
```txt
pydantic-settings==2.5.2
python-dotenv==1.0.1
```

### Docker 환경에서 환경 변수

#### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    env_file:
      - .env
    environment:
      - ENV=${ENV}
      - DEBUG=${DEBUG}
      - DATABASE_URL=${DATABASE_URL}
    # 또는 직접 지정
    # environment:
    #   - ENV=production
    #   - DEBUG=false
```

#### Dockerfile에서 빌드 시 환경 변수
```dockerfile
# 빌드 타임 변수 (ARG)
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim

# 런타임 환경 변수 (ENV)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app \
    PORT=8080

WORKDIR $APP_HOME
```

### GCP 배포 시 환경 변수

#### Cloud Run
```powershell
# 환경 변수와 함께 배포
gcloud run deploy fastapi-app `
    --image asia-northeast3-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-gcp:latest `
    --platform managed `
    --region asia-northeast3 `
    --set-env-vars "ENV=production,DEBUG=false" `
    --allow-unauthenticated
```

#### Cloud Run YAML
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: fastapi-app
spec:
  template:
    spec:
      containers:
      - image: asia-northeast3-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-gcp:latest
        env:
        - name: ENV
          value: "production"
        - name: DEBUG
          value: "false"
        - name: GCP_PROJECT_ID
          value: "my-project-id"
```

### GCP Secret Manager 사용

#### 시크릿 생성
```powershell
# 시크릿 생성
gcloud secrets create database-url `
    --data-file=-
# 입력: postgresql://user:pass@host:5432/db
# Ctrl+D로 종료

# 또는 직접 값 입력
echo -n "postgresql://user:pass@host:5432/db" | `
    gcloud secrets create database-url --data-file=-

# 시크릿 확인
gcloud secrets describe database-url

# 시크릿 조회
gcloud secrets versions access latest --secret="database-url"
```

#### Cloud Run에서 Secret Manager 사용
```powershell
# Secret Manager 시크릿을 환경 변수로 마운트
gcloud run deploy fastapi-app `
    --image IMAGE_URL `
    --set-secrets="DATABASE_URL=database-url:latest" `
    --set-secrets="API_KEY=api-key:latest"
```

#### Python에서 Secret Manager 사용
```python
from google.cloud import secretmanager
from functools import lru_cache

def get_secret(secret_id: str, project_id: str, version_id: str = "latest"):
    """GCP Secret Manager에서 시크릿 가져오기"""
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

@lru_cache()
def get_database_url():
    project_id = os.getenv("GCP_PROJECT_ID")
    return get_secret("database-url", project_id)
```

**requirements.txt에 추가**
```txt
google-cloud-secret-manager==2.20.0
```

### 환경별 설정 분리

**config/**
```
config/
├── __init__.py
├── base.py
├── development.py
├── production.py
└── test.py
```

**config/base.py**
```python
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    app_name: str = "My FastAPI App"
    secret_key: str
    gcp_project_id: str

    class Config:
        env_file = ".env"
```

**config/production.py**
```python
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    debug: bool = False
    database_url: str  # 반드시 설정되어야 함
```

**config/__init__.py**
```python
import os
from .development import DevelopmentConfig
from .production import ProductionConfig

def get_config():
    env = os.getenv("ENV", "development")

    if env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()

config = get_config()
```

---

## 데이터베이스 연결

컨테이너 애플리케이션을 데이터베이스와 연결하는 방법을 알아봅니다.

### FastAPI + PostgreSQL 연결

#### 1. 필요한 패키지 설치

**requirements.txt**
```txt
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
alembic==1.13.3
```

#### 2. 데이터베이스 설정

**database.py**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

# 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = settings.database_url

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 연결 확인
    pool_size=10,
    max_overflow=20
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Cloud SQL (PostgreSQL) 연결

#### 1. Cloud SQL 인스턴스 생성

```powershell
# Cloud SQL 인스턴스 생성
gcloud sql instances create fastapi-db `
    --database-version=POSTGRES_16 `
    --tier=db-f1-micro `
    --region=asia-northeast3

# 데이터베이스 생성
gcloud sql databases create fastapidb `
    --instance=fastapi-db

# 사용자 생성
gcloud sql users create dbadmin `
    --instance=fastapi-db `
    --password=SecurePassword123!

# 인스턴스 연결 이름 확인
gcloud sql instances describe fastapi-db `
    --format="value(connectionName)"
# 출력: PROJECT_ID:asia-northeast3:fastapi-db
```

#### 2. Cloud Run에서 Cloud SQL 연결

**방법 1: Unix 소켓 연결 (권장)**

```powershell
gcloud run deploy fastapi-app `
    --image IMAGE_URL `
    --add-cloudsql-instances PROJECT_ID:asia-northeast3:fastapi-db `
    --set-env-vars "DATABASE_URL=postgresql://dbadmin:SecurePassword123!@/fastapidb?host=/cloudsql/PROJECT_ID:asia-northeast3:fastapi-db"
```

**방법 2: Cloud SQL Proxy 사용**

```python
# database.py
import os
from google.cloud.sql.connector import Connector
import sqlalchemy

def getconn():
    connector = Connector()
    conn = connector.connect(
        "PROJECT_ID:asia-northeast3:fastapi-db",
        "pg8000",
        user="dbadmin",
        password="SecurePassword123!",
        db="fastapidb"
    )
    return conn

engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,
)
```

**requirements.txt에 추가**
```txt
cloud-sql-python-connector[pg8000]==1.11.0
pg8000==1.31.0
```

#### 3. Secret Manager에 DB 자격증명 저장

```powershell
# DB 연결 문자열을 시크릿으로 저장
echo -n "postgresql://dbadmin:SecurePassword123!@/fastapidb?host=/cloudsql/PROJECT_ID:asia-northeast3:fastapi-db" | `
    gcloud secrets create database-url --data-file=-

# Cloud Run 배포 시 시크릿 사용
gcloud run deploy fastapi-app `
    --image IMAGE_URL `
    --add-cloudsql-instances PROJECT_ID:asia-northeast3:fastapi-db `
    --set-secrets="DATABASE_URL=database-url:latest"
```

---

## 배포 옵션

### 1. Cloud Run (⭐ 초급)

#### 특징
- **난이도**: ⭐ 초급
- **관리 수준**: 완전 관리형 서버리스
- **비용**: 요청 수 및 사용 시간 기반
- **배포 시간**: 3-5분

#### 장점
✅ 가장 빠르고 간단한 배포
✅ HTTPS 자동 설정 (커스텀 도메인 지원)
✅ 자동 스케일링 (0으로도 축소 가능)
✅ 인프라 관리 완전 불필요
✅ 트래픽 분할 및 블루/그린 배포 지원
✅ 리전별 배포 가능

#### 단점
❌ 콜드 스타트 지연 (첫 요청)
❌ 최대 실행 시간 제한 (60분)
❌ 일부 네트워킹 제약
❌ Stateful 애플리케이션에 제한적

#### 배포 명령어
```powershell
# 기본 배포
gcloud run deploy fastapi-app `
    --image asia-northeast3-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-gcp:latest `
    --platform managed `
    --region asia-northeast3 `
    --allow-unauthenticated

# 고급 옵션과 함께 배포
gcloud run deploy fastapi-app `
    --image asia-northeast3-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-gcp:latest `
    --platform managed `
    --region asia-northeast3 `
    --cpu 1 `
    --memory 512Mi `
    --min-instances 0 `
    --max-instances 10 `
    --concurrency 80 `
    --timeout 300s `
    --set-env-vars "ENV=production,DEBUG=false" `
    --allow-unauthenticated
```

#### 예상 비용
```
CPU: $0.00002400/vCPU-초
메모리: $0.00000250/GiB-초
요청: $0.40/백만 요청

예시 (월 100만 요청, 평균 200ms, 0.5 vCPU, 512MB):
CPU: 100만 × 0.2초 × 0.5 vCPU × $0.00002400 = $2.40
메모리: 100만 × 0.2초 × 0.5 GB × $0.00000250 = $0.25
요청: 1 × $0.40 = $0.40
총 = $3.05/월

무료 티어:
- CPU: 월 180,000 vCPU-초
- 메모리: 월 360,000 GiB-초
- 요청: 월 2백만 요청
```

### 2. GKE Standard (⭐⭐ 중급)

#### 특징
- **난이도**: ⭐⭐ 중급
- **관리 수준**: 관리형 Kubernetes
- **비용**: 노드 시간당 과금 + 클러스터 관리 비용
- **배포 시간**: 15-30분

#### 장점
✅ Kubernetes 표준 사용
✅ 세밀한 리소스 제어
✅ 다양한 워크로드 지원
✅ 고급 네트워킹 기능
✅ StatefulSet, DaemonSet 등 지원
✅ 온프레미스 호환성

#### 단점
❌ 학습 곡선 높음
❌ 노드 관리 필요
❌ 비용이 상대적으로 높음
❌ 초기 설정 복잡

#### 배포 명령어
```powershell
# 1. 클러스터 생성
gcloud container clusters create fastapi-cluster `
    --region asia-northeast3 `
    --num-nodes 1 `
    --machine-type e2-medium `
    --disk-size 30 `
    --enable-autoscaling `
    --min-nodes 1 `
    --max-nodes 3

# 2. kubectl 설정
gcloud container clusters get-credentials fastapi-cluster `
    --region asia-northeast3

# 3. 배포
kubectl apply -f deployments/2-gke-standard/k8s/

# 4. 서비스 확인
kubectl get services
```

#### 예상 비용
```
클러스터 관리 비용: $0.10/시간/클러스터 = $73/월
노드 비용 (e2-medium × 3): $0.0335/시간 × 3 × 730시간 = $73.4/월

총 예상 비용: $146.4/월
```

### 3. GKE Autopilot (⭐⭐ 중급)

#### 특징
- **난이도**: ⭐⭐ 중급
- **관리 수준**: 완전 관리형 Kubernetes
- **비용**: Pod 리소스 사용량 기반
- **배포 시간**: 10-20분

#### 장점
✅ 노드 관리 불필요
✅ 자동 스케일링
✅ 보안 강화 (자동 업데이트)
✅ Standard GKE보다 운영 간단
✅ Kubernetes 표준 API 사용

#### 단점
❌ 일부 Kubernetes 기능 제한
❌ DaemonSet 제약
❌ 노드 레벨 커스터마이징 불가

#### 배포 명령어
```powershell
# 1. Autopilot 클러스터 생성
gcloud container clusters create-auto fastapi-autopilot `
    --region asia-northeast3

# 2. kubectl 설정
gcloud container clusters get-credentials fastapi-autopilot `
    --region asia-northeast3

# 3. 배포
kubectl apply -f deployments/3-gke-autopilot/k8s/
```

#### 예상 비용
```
Pod vCPU: $0.0445/vCPU-시간
Pod 메모리: $0.00491/GiB-시간

예시 (3 pods, 0.5 vCPU, 1 GB each, 24/7):
vCPU: 3 × 0.5 × 730 × $0.0445 = $48.7
메모리: 3 × 1 × 730 × $0.00491 = $10.7

총 예상 비용: $59.4/월
```

### 4. Compute Engine + Docker (⭐ 초급)

#### 특징
- **난이도**: ⭐ 초급
- **관리 수준**: VM 기반
- **비용**: VM 시간당 과금
- **배포 시간**: 5-10분

#### 장점
✅ 간단한 설정
✅ 완전한 제어 권한
✅ Docker Compose 사용 가능
✅ 예측 가능한 비용

#### 단점
❌ VM 관리 필요
❌ 수동 스케일링
❌ 고가용성 구성 복잡

#### 배포 명령어
```powershell
# 1. VM 인스턴스 생성 (Container-Optimized OS)
gcloud compute instances create-with-container fastapi-vm `
    --container-image=asia-northeast3-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-gcp:latest `
    --machine-type=e2-micro `
    --zone=asia-northeast3-a `
    --tags=http-server

# 2. 방화벽 규칙 생성
gcloud compute firewall-rules create allow-fastapi `
    --allow tcp:8080 `
    --target-tags http-server

# 3. 외부 IP 확인
gcloud compute instances describe fastapi-vm `
    --zone=asia-northeast3-a `
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

---

## 실전 예제

### 예제 1: FastAPI + Cloud Run 배포

#### 전체 워크플로우
```powershell
# 1. 프로젝트 디렉토리 생성
mkdir C:\projects\fastapi-gcp
cd C:\projects\fastapi-gcp

# 2. 애플리케이션 코드 작성
# (위의 FastAPI 예제 코드 사용)

# 3. 이미지 빌드
docker build -t fastapi-gcp:latest .

# 4. 로컬 테스트
docker run -d -p 8080:8080 --name fastapi-test fastapi-gcp:latest

# 브라우저에서 확인: http://localhost:8080/docs

# 5. GCP 프로젝트 설정
$PROJECT_ID = "my-fastapi-project"
gcloud config set project $PROJECT_ID

# 6. Artifact Registry 리포지토리 생성
gcloud artifacts repositories create fastapi-repo `
    --repository-format=docker `
    --location=asia-northeast3 `
    --description="FastAPI Docker images"

# 7. Docker 인증 설정
gcloud auth configure-docker asia-northeast3-docker.pkg.dev

# 8. 이미지 태깅 및 푸시
$IMAGE_URI = "asia-northeast3-docker.pkg.dev/${PROJECT_ID}/fastapi-repo/fastapi-gcp:latest"
docker tag fastapi-gcp:latest $IMAGE_URI
docker push $IMAGE_URI

# 9. Cloud Run 배포
gcloud run deploy fastapi-app `
    --image $IMAGE_URI `
    --platform managed `
    --region asia-northeast3 `
    --allow-unauthenticated

# 10. 서비스 URL 확인
gcloud run services describe fastapi-app `
    --region asia-northeast3 `
    --format="value(status.url)"
```

### 예제 2: FastAPI + GKE Autopilot 배포

```powershell
# 1. GKE Autopilot 클러스터 생성
gcloud container clusters create-auto fastapi-cluster `
    --region=asia-northeast3 `
    --project=$PROJECT_ID

# 2. kubectl 인증 설정
gcloud container clusters get-credentials fastapi-cluster `
    --region=asia-northeast3

# 3. 이미지 빌드 및 푸시 (예제 1과 동일)

# 4. Kubernetes 매니페스트 작성
# deployment.yaml, service.yaml 생성

# 5. 배포
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 6. 서비스 확인
kubectl get services
kubectl get pods

# 7. 외부 IP 확인
kubectl get service fastapi-service
```

#### k8s/deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: asia-northeast3-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-gcp:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENV
          value: "production"
        - name: PORT
          value: "8080"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### k8s/service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: LoadBalancer
  selector:
    app: fastapi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

### 예제 3: FastAPI + Cloud SQL + Secret Manager 연동

이 예제는 FastAPI 애플리케이션을 Cloud SQL PostgreSQL과 연결하고, Secret Manager를 사용하여 데이터베이스 자격증명을 안전하게 관리합니다.

#### 1. Cloud SQL 인스턴스 생성

```powershell
# Cloud SQL 인스턴스 생성
gcloud sql instances create fastapi-db `
    --database-version=POSTGRES_16 `
    --tier=db-f1-micro `
    --region=asia-northeast3 `
    --root-password=TempPassword123!

# 데이터베이스 생성
gcloud sql databases create fastapidb --instance=fastapi-db

# 사용자 생성
gcloud sql users create dbadmin `
    --instance=fastapi-db `
    --password=SecurePassword123!

# 연결 이름 확인
$CONNECTION_NAME = (gcloud sql instances describe fastapi-db `
    --format="value(connectionName)")
Write-Host "Connection Name: $CONNECTION_NAME"
```

#### 2. Secret Manager에 DB 자격증명 저장

```powershell
# Secret Manager API 활성화
gcloud services enable secretmanager.googleapis.com

# DB 연결 문자열을 시크릿으로 저장
$DB_URL = "postgresql://dbadmin:SecurePassword123!@/fastapidb?host=/cloudsql/$CONNECTION_NAME"
echo -n $DB_URL | gcloud secrets create database-url --data-file=-

# 시크릿 확인
gcloud secrets describe database-url
```

#### 3. FastAPI 코드 수정

**database.py**
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google.cloud import secretmanager

def get_secret(secret_id: str):
    """Secret Manager에서 시크릿 가져오기"""
    project_id = os.getenv("GCP_PROJECT_ID")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# Cloud Run에서 실행 중이면 Secret Manager 사용
if os.getenv("K_SERVICE"):  # Cloud Run 환경
    DATABASE_URL = get_secret("database-url")
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/test")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 4. Cloud Run 배포

```powershell
# Cloud Run 배포 (Cloud SQL 및 Secret Manager 연결)
gcloud run deploy fastapi-app `
    --image $IMAGE_URI `
    --platform managed `
    --region asia-northeast3 `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID" `
    --allow-unauthenticated

# Secret Manager 접근 권한 부여 (자동으로 설정되지만 확인)
$SERVICE_ACCOUNT = (gcloud run services describe fastapi-app `
    --region asia-northeast3 `
    --format="value(spec.template.spec.serviceAccountName)")

gcloud secrets add-iam-policy-binding database-url `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/secretmanager.secretAccessor"
```

### 예제 4: Docker Compose를 사용한 풀스택 로컬 개발 환경

로컬에서 FastAPI, PostgreSQL, Redis를 모두 실행하는 완전한 개발 환경 구성

#### docker-compose.yml

```yaml
version: '3.8'

services:
  # FastAPI 애플리케이션
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: fastapi-gcp-api
    ports:
      - "8080:8080"
    environment:
      - ENV=development
      - DEBUG=true
      - DATABASE_URL=postgresql://fastapi:fastapi123@db:5432/fastapi_db
      - REDIS_URL=redis://redis:6379/0
      - PORT=8080
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./app:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8080 --reload
    networks:
      - app-network

  # PostgreSQL 데이터베이스
  db:
    image: postgres:16-alpine
    container_name: fastapi-gcp-db
    environment:
      - POSTGRES_DB=fastapi_db
      - POSTGRES_USER=fastapi
      - POSTGRES_PASSWORD=fastapi123
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fastapi -d fastapi_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Redis 캐시
  redis:
    image: redis:7-alpine
    container_name: fastapi-gcp-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - app-network

  # pgAdmin (DB 관리 도구)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: fastapi-gcp-pgadmin
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@example.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    depends_on:
      - db
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

#### Dockerfile.dev

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 개발 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# 소스 코드는 볼륨 마운트로 제공됨
ENV PORT=8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
```

#### 사용 방법

```powershell
# 전체 환경 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# DB 마이그레이션
docker-compose exec api alembic upgrade head

# 테스트 실행
docker-compose exec api pytest

# 특정 서비스만 재시작
docker-compose restart api

# 전체 종료 및 데이터 삭제
docker-compose down -v

# 접속 정보:
# - API: http://localhost:8080
# - Swagger: http://localhost:8080/docs
# - pgAdmin: http://localhost:5050
```

### 예제 5: Cloud Build로 CI/CD 파이프라인 구축

#### cloudbuild.yaml

```yaml
# Cloud Build 설정 파일
steps:
  # 1. 테스트
  - name: 'python:3.12-slim'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        pip install -r requirements.txt pytest pytest-cov
        pytest tests/ -v --cov=app

  # 2. Docker 이미지 빌드
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-gcp:$COMMIT_SHA'
      - '-t'
      - 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-gcp:latest'
      - '.'

  # 3. Artifact Registry에 푸시
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-gcp:$COMMIT_SHA'

  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-gcp:latest'

  # 4. Cloud Run 배포
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'fastapi-app'
      - '--image'
      - 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-gcp:$COMMIT_SHA'
      - '--region'
      - 'asia-northeast3'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-gcp:$COMMIT_SHA'
  - 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-gcp:latest'

options:
  logging: CLOUD_LOGGING_ONLY
```

#### Cloud Build 트리거 설정

```powershell
# GitHub 리포지토리 연결 후 트리거 생성
gcloud builds triggers create github `
    --repo-name=my-fastapi-repo `
    --repo-owner=my-github-username `
    --branch-pattern='^main$' `
    --build-config=cloudbuild.yaml

# 수동 빌드 실행
gcloud builds submit --config=cloudbuild.yaml
```

---

## 성능 최적화

### Docker 이미지 최적화

#### 1. 멀티스테이지 빌드 활용

**최적화 전**
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
# 결과: ~1GB
```

**최적화 후**
```dockerfile
# Build stage
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim
RUN useradd -m appuser
WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
# 결과: ~200MB
```

#### 2. Cloud Build 캐싱

```yaml
# cloudbuild.yaml
options:
  # Kaniko 캐시 사용
  env:
    - 'DOCKER_BUILDKIT=1'
  machineType: 'N1_HIGHCPU_8'
```

### 애플리케이션 성능 최적화

#### 1. Gunicorn Worker 설정

```dockerfile
# 프로덕션용 - Gunicorn + Uvicorn workers
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:${PORT}", \
     "--timeout", "300"]
```

#### 2. Cloud Run 동시성 설정

```powershell
# 인스턴스당 동시 요청 수 설정
gcloud run deploy fastapi-app `
    --image $IMAGE_URI `
    --concurrency 80 `
    --cpu 2 `
    --memory 1Gi `
    --min-instances 1 `
    --max-instances 100
```

#### 3. Cloud CDN 사용

```powershell
# Load Balancer를 통해 Cloud CDN 활성화
gcloud compute backend-services update BACKEND_SERVICE `
    --enable-cdn `
    --cache-mode=CACHE_ALL_STATIC
```

#### 4. Memorystore (Redis) 사용

```powershell
# Redis 인스턴스 생성
gcloud redis instances create fastapi-cache `
    --size=1 `
    --region=asia-northeast3 `
    --redis-version=redis_7_0

# Redis 호스트 확인
gcloud redis instances describe fastapi-cache `
    --region=asia-northeast3 `
    --format="value(host)"
```

**Redis 캐싱 구현**
```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=6379,
    decode_responses=True
)

def cache(expire=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)

            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire, json.dumps(result))
            return result
        return wrapper
    return decorator

@app.get("/items/{item_id}")
@cache(expire=3600)
async def get_item(item_id: int):
    # 비용이 큰 데이터베이스 조회
    return {"item_id": item_id, "data": "..."}
```

---

## CI/CD 파이프라인

### GitHub Actions로 GCP 배포

#### .github/workflows/deploy-gcp.yml

```yaml
name: Deploy to GCP

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GCP_REGION: asia-northeast3
  SERVICE_NAME: fastapi-app
  REGISTRY: asia-northeast3-docker.pkg.dev

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest tests/ -v --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2

    - name: Configure Docker for Artifact Registry
      run: |
        gcloud auth configure-docker ${{ env.REGISTRY }}

    - name: Build Docker image
      run: |
        docker build -t ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/fastapi-repo/${{ env.SERVICE_NAME }}:${{ github.sha }} .
        docker tag ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/fastapi-repo/${{ env.SERVICE_NAME }}:${{ github.sha }} \
                   ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/fastapi-repo/${{ env.SERVICE_NAME }}:latest

    - name: Push Docker image
      run: |
        docker push ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/fastapi-repo/${{ env.SERVICE_NAME }}:${{ github.sha }}
        docker push ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/fastapi-repo/${{ env.SERVICE_NAME }}:latest

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy ${{ env.SERVICE_NAME }} \
          --image ${{ env.REGISTRY }}/${{ env.GCP_PROJECT_ID }}/fastapi-repo/${{ env.SERVICE_NAME }}:${{ github.sha }} \
          --platform managed \
          --region ${{ env.GCP_REGION }} \
          --allow-unauthenticated

    - name: Get Cloud Run URL
      run: |
        SERVICE_URL=$(gcloud run services describe ${{ env.SERVICE_NAME }} \
          --region ${{ env.GCP_REGION }} \
          --format='value(status.url)')
        echo "Deployed to: $SERVICE_URL"
```

### Cloud Build 설정

#### cloudbuild.yaml (상세 버전)

```yaml
steps:
  # 1. 린트 검사
  - name: 'python:3.12-slim'
    id: 'lint'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        pip install black flake8 mypy
        black --check app/
        flake8 app/ --max-line-length=100
        mypy app/ --ignore-missing-imports

  # 2. 유닛 테스트
  - name: 'python:3.12-slim'
    id: 'test'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        pip install -r requirements.txt pytest pytest-cov
        pytest tests/ -v --cov=app --cov-report=xml --cov-report=html

  # 3. Docker 이미지 빌드
  - name: 'gcr.io/cloud-builders/docker'
    id: 'build'
    args:
      - 'build'
      - '-t'
      - '$_REGISTRY/$PROJECT_ID/$_REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA'
      - '-t'
      - '$_REGISTRY/$PROJECT_ID/$_REPO_NAME/$_SERVICE_NAME:latest'
      - '--cache-from'
      - '$_REGISTRY/$PROJECT_ID/$_REPO_NAME/$_SERVICE_NAME:latest'
      - '.'

  # 4. 컨테이너 취약점 스캔
  - name: 'gcr.io/cloud-builders/gcloud'
    id: 'scan'
    args:
      - 'beta'
      - 'container'
      - 'images'
      - 'scan'
      - '$_REGISTRY/$PROJECT_ID/$_REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA'

  # 5. 이미지 푸시
  - name: 'gcr.io/cloud-builders/docker'
    id: 'push'
    args:
      - 'push'
      - '--all-tags'
      - '$_REGISTRY/$PROJECT_ID/$_REPO_NAME/$_SERVICE_NAME'

  # 6. Cloud Run 배포
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'deploy'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '$_SERVICE_NAME'
      - '--image'
      - '$_REGISTRY/$PROJECT_ID/$_REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA'
      - '--region'
      - '$_REGION'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--cpu'
      - '1'
      - '--memory'
      - '512Mi'
      - '--min-instances'
      - '0'
      - '--max-instances'
      - '10'
      - '--set-env-vars'
      - 'ENV=production'

  # 7. 헬스 체크
  - name: 'gcr.io/cloud-builders/curl'
    id: 'health-check'
    entrypoint: 'sh'
    args:
      - '-c'
      - |
        SERVICE_URL=$(gcloud run services describe $_SERVICE_NAME \
          --region $_REGION \
          --format='value(status.url)')
        curl -f $SERVICE_URL/health || exit 1

substitutions:
  _REGISTRY: asia-northeast3-docker.pkg.dev
  _REPO_NAME: fastapi-repo
  _SERVICE_NAME: fastapi-app
  _REGION: asia-northeast3

images:
  - '$_REGISTRY/$PROJECT_ID/$_REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA'
  - '$_REGISTRY/$PROJECT_ID/$_REPO_NAME/$_SERVICE_NAME:latest'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'N1_HIGHCPU_8'
  substitutionOption: 'ALLOW_LOOSE'

timeout: 1200s
```

---

## 트러블슈팅

### Windows 환경 관련

#### 문제: Docker Desktop이 시작되지 않음
**증상**: "Docker Desktop starting..." 무한 로딩
**해결방법**:
```powershell
# 1. WSL2 업데이트
wsl --update

# 2. WSL2를 기본값으로 설정
wsl --set-default-version 2

# 3. Docker Desktop 재시작
# 작업 관리자에서 Docker Desktop 프로세스 종료 후 재시작
```

### GCP 관련

#### 문제: gcloud 인증 실패
**증상**: "ERROR: (gcloud) Your current active account is not authorized"
**해결방법**:
```powershell
# 1. 재인증
gcloud auth login

# 2. 애플리케이션 기본 자격증명 설정
gcloud auth application-default login

# 3. 프로젝트 확인
gcloud config get-value project

# 4. 프로젝트 설정
gcloud config set project PROJECT_ID
```

#### 문제: Artifact Registry 푸시 실패
**증상**: "denied: Permission denied"
**해결방법**:
```powershell
# 1. Docker 인증 재설정
gcloud auth configure-docker asia-northeast3-docker.pkg.dev

# 2. 권한 확인
gcloud projects get-iam-policy PROJECT_ID

# 3. 필요한 역할 추가
gcloud projects add-iam-policy-binding PROJECT_ID `
    --member="user:YOUR_EMAIL" `
    --role="roles/artifactregistry.writer"

# 4. Artifact Registry API 활성화 확인
gcloud services enable artifactregistry.googleapis.com
```

#### 문제: Cloud Run 배포 실패
**증상**: "ERROR: (gcloud.run.deploy) Container failed to start"
**해결방법**:
```powershell
# 1. 로그 확인
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=SERVICE_NAME" `
    --limit 50 `
    --format json

# 2. 일반적인 문제:
# - PORT 환경 변수 미사용 (Cloud Run은 PORT를 동적으로 할당)
# - 컨테이너가 0.0.0.0에서 수신 대기하지 않음
# - 시작 시간 초과 (기본 300초)

# 3. 로컬에서 테스트
docker run -p 8080:8080 -e PORT=8080 IMAGE_NAME

# 4. 타임아웃 증가
gcloud run deploy SERVICE_NAME --timeout 900s
```

#### 문제: Cloud SQL 연결 실패
**증상**: "Could not connect to Cloud SQL instance"
**해결방법**:
```powershell
# 1. Cloud SQL 인스턴스 상태 확인
gcloud sql instances describe INSTANCE_NAME

# 2. 연결 이름 확인
gcloud sql instances describe INSTANCE_NAME --format="value(connectionName)"

# 3. Cloud Run 서비스에 Cloud SQL 연결 추가
gcloud run services update SERVICE_NAME `
    --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME

# 4. Cloud SQL Admin API 활성화
gcloud services enable sqladmin.googleapis.com

# 5. 서비스 계정 권한 확인
gcloud projects add-iam-policy-binding PROJECT_ID `
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" `
    --role="roles/cloudsql.client"
```

### Docker 관련

#### 문제: 이미지 빌드가 느림
**증상**: 빌드에 5분 이상 소요
**해결방법**:
```powershell
# 1. BuildKit 활성화
$env:DOCKER_BUILDKIT=1

# 2. 빌드 캐시 사용
docker build --cache-from IMAGE_NAME:latest -t IMAGE_NAME:latest .

# 3. .dockerignore 최적화
# 불필요한 파일 제외

# 4. 멀티스테이지 빌드 사용
```

### GKE 관련

#### 문제: Pod이 Pending 상태
**증상**: `kubectl get pods` 결과 STATUS가 Pending
**해결방법**:
```powershell
# 1. Pod 상세 확인
kubectl describe pod POD_NAME

# 2. 일반적인 원인:
# - 리소스 부족 (CPU/메모리)
# - 노드 부족

# 3. 노드 상태 확인
kubectl get nodes

# 4. 클러스터 오토스케일링 확인 (GKE Autopilot은 자동)
gcloud container clusters describe CLUSTER_NAME --region REGION

# 5. Pod 리소스 요청 줄이기
# deployment.yaml에서 resources.requests 값 감소
```

#### 문제: Service에 EXTERNAL-IP가 할당되지 않음
**증상**: `kubectl get svc` 결과 EXTERNAL-IP가 \<pending\>
**해결방법**:
```powershell
# 1. 서비스 타입 확인
kubectl get svc SERVICE_NAME -o yaml

# 2. LoadBalancer 타입이 맞는지 확인
# type: LoadBalancer

# 3. 방화벽 규칙 확인
gcloud compute firewall-rules list

# 4. 로드밸런서 프로비저닝 대기 (최대 5분 소요)
kubectl get svc -w

# 5. 이벤트 확인
kubectl get events --sort-by='.lastTimestamp'
```

---

## FAQ

### 일반 질문

#### Q: Docker Desktop 없이 진행할 수 있나요?
**A**: 네, WSL2에서 Docker Engine만 설치하거나, Cloud Build를 사용할 수 있습니다. 하지만 로컬 개발을 위해서는 Docker Desktop이 가장 편리합니다.

#### Q: Mac이나 Linux에서도 이 가이드를 따라할 수 있나요?
**A**: 네, PowerShell 명령어를 Bash로 변경하고 경로 구분자를 조정하면 대부분의 내용이 동일하게 적용됩니다.

#### Q: GCP 비용이 걱정됩니다. 무료로 테스트할 수 있나요?
**A**: GCP는 신규 사용자에게 $300 크레딧을 제공합니다 (90일간). 또한:
- Cloud Run: 월 2백만 요청까지 무료
- Artifact Registry: 월 0.5GB 스토리지 무료
- Cloud Build: 일 120 빌드분 무료
- 테스트 후 리소스를 즉시 삭제하면 비용을 최소화할 수 있습니다.

#### Q: 어떤 배포 옵션을 선택해야 하나요?
**A**:
- **처음 시작 / 간단한 API** → Cloud Run (가장 간단하고 저렴)
- **Kubernetes 경험 / 복잡한 워크로드** → GKE Autopilot
- **완전한 Kubernetes 제어 필요** → GKE Standard
- **간단한 VM 배포** → Compute Engine

### GCP 관련

#### Q: Cloud Run과 GKE의 차이는 무엇인가요?
**A**:
| 기능 | Cloud Run | GKE Autopilot | GKE Standard |
|------|-----------|---------------|--------------|
| 관리 수준 | 완전 관리 | 관리형 K8s | 직접 관리 |
| 학습 곡선 | 낮음 | 중간 | 높음 |
| 스케일링 | 0으로 축소 가능 | 자동 | 수동/자동 |
| 비용 | 사용량 기반 | Pod 리소스 기반 | 노드 시간 |
| 적합한 경우 | 간단한 API | 대부분 워크로드 | 고급 K8s 기능 필요 |

#### Q: Container Registry(GCR)를 사용해야 하나요?
**A**: 아니요. **Container Registry는 2024년 5월 15일부로 공식 지원이 종료**되었습니다.

**Artifact Registry**만 사용하세요:
- ✅ 더 많은 기능 (Docker, Maven, npm, Python 등 다양한 형식 지원)
- ✅ 리전별 리포지토리로 더 빠른 성능
- ✅ 통합 취약점 스캔
- ✅ 세밀한 권한 관리
- ✅ 향후 지속적인 업데이트 및 지원

이 가이드는 Artifact Registry만 사용합니다.

#### Q: Cloud Run의 콜드 스타트를 줄이려면?
**A**:
```powershell
# 최소 인스턴스 설정 (항상 warm 상태 유지)
gcloud run deploy SERVICE_NAME `
    --min-instances 1 `
    --image IMAGE_URL

# 주의: 최소 인스턴스는 24/7 과금됩니다
```

#### Q: Cloud SQL과 Cloud Run 연결 시 유의사항은?
**A**:
1. **Unix 소켓 사용** (권장): `/cloudsql/PROJECT:REGION:INSTANCE`
2. **Public IP 사용 금지**: 보안 위험, Cloud SQL Proxy 필요
3. **연결 풀 설정**: 최대 연결 수 제한 (Cloud SQL 인스턴스 크기에 따라)
4. **서비스 계정 권한**: `roles/cloudsql.client` 필요

### 성능 관련

#### Q: Cloud Run 응답이 느립니다. 개선 방법은?
**A**:
1. **CPU 할당 증가**: `--cpu 2`
2. **메모리 증가**: `--memory 1Gi`
3. **동시성 조정**: `--concurrency 80`
4. **최소 인스턴스 설정**: `--min-instances 1` (콜드 스타트 제거)
5. **캐싱 추가**: Redis (Memorystore)
6. **비동기 처리**: async/await 활용

#### Q: Docker 이미지 크기를 줄이려면?
**A**:
```dockerfile
# 1. Slim 베이스 이미지
FROM python:3.12-slim

# 2. 멀티스테이지 빌드
FROM python:3.12-slim as builder
...
FROM python:3.12-slim
COPY --from=builder ...

# 3. .dockerignore 활용

# 4. 레이어 최소화
RUN pip install ... && rm -rf ...
```

### 배포 관련

#### Q: 무중단 배포가 가능한가요?
**A**: 네, 모든 GCP 옵션에서 가능합니다:
- **Cloud Run**: 자동 롤링 배포, 트래픽 분할 지원
- **GKE**: Rolling Update, Blue/Green, Canary 모두 지원

```powershell
# Cloud Run 트래픽 분할
gcloud run services update-traffic SERVICE_NAME `
    --to-revisions REVISION1=80,REVISION2=20
```

#### Q: 배포한 버전을 롤백하려면?
**A**:
```powershell
# Cloud Run - 이전 리비전으로 롤백
gcloud run services update-traffic SERVICE_NAME `
    --to-revisions PREVIOUS_REVISION=100

# GKE - 이전 버전으로 롤백
kubectl rollout undo deployment/DEPLOYMENT_NAME

# 특정 리비전으로 롤백
kubectl rollout undo deployment/DEPLOYMENT_NAME --to-revision=2
```

### 비용 관련

#### Q: 예상치 못한 GCP 비용이 발생했습니다. 확인 방법은?
**A**:
```powershell
# 1. Cloud Console > Billing > Cost table

# 2. gcloud로 현재 실행 중인 리소스 확인
gcloud run services list
gcloud container clusters list
gcloud sql instances list
gcloud compute instances list

# 3. 주요 비용 발생 리소스:
# - Cloud Run: 최소 인스턴스 설정 시
# - GKE: 항상 실행 중인 노드
# - Cloud SQL: 인스턴스 크기 및 스토리지
# - NAT Gateway: 송신 트래픽
# - Load Balancer: 시간당 과금
```

#### Q: 개발 환경 비용을 절감하려면?
**A**:
1. **Cloud Run 사용**: 사용하지 않을 때 자동 0 축소
2. **GKE Autopilot**: Standard보다 저렴
3. **리소스 중지**: 야간/주말에 인스턴스 중지
4. **로컬 개발**: Docker Compose 활용
5. **예산 알림**: Cloud Billing 예산 설정

```powershell
# Cloud SQL 인스턴스 중지 (비용 절약)
gcloud sql instances patch INSTANCE_NAME --activation-policy NEVER

# 다시 시작
gcloud sql instances patch INSTANCE_NAME --activation-policy ALWAYS
```

### 데이터베이스

#### Q: Cloud SQL 마이그레이션을 안전하게 실행하려면?
**A**:
```powershell
# 1. 백업 먼저 수행
gcloud sql backups create --instance=INSTANCE_NAME

# 2. Cloud Run에서 별도 마이그레이션 Job 실행
gcloud run jobs create migration-job `
    --image IMAGE_WITH_ALEMBIC `
    --command alembic `
    --args "upgrade,head" `
    --add-cloudsql-instances CONNECTION_NAME

gcloud run jobs execute migration-job

# 3. 스키마 변경은 점진적으로
# - 컬럼 추가 → 배포 → 컬럼 사용 → 배포 → 기존 컬럼 제거
```

---

## 다음 단계

### FastAPI 애플리케이션 배포
1. ✅ [Windows 환경 설정](#사전-준비)
2. ✅ [로컬에서 Docker 이미지 빌드](#fastapi-가이드)
3. 배포 방식 선택:
   - [Cloud Run으로 배포](#1-cloud-run--초급) (권장)
   - [GKE Autopilot로 배포](#3-gke-autopilot--중급)
   - [GKE Standard로 배포](#2-gke-standard--중급)
   - [Compute Engine으로 배포](#4-compute-engine--docker--초급)

### Django 애플리케이션 배포
1. ✅ [Django 프로젝트 구조](#django-가이드)
2. ✅ [로컬에서 Docker 이미지 빌드](#django-가이드)
3. 배포 방식 선택 (FastAPI와 동일)

---

## 비용 예상

### Cloud Run 💰
```
무료 티어 (매월):
- 요청: 2백만 건
- CPU: 180,000 vCPU-초
- 메모리: 360,000 GiB-초
- 네트워크: 1GB 송신

유료 사용 시 (월 100만 요청, 200ms, 0.5 vCPU, 512MB):
≈ $3-5/월
```

### GKE Autopilot 💰💰
```
Pod 리소스 기반:
vCPU: $0.0445/vCPU-시간
메모리: $0.00491/GiB-시간

예시 (3 pods, 0.5 vCPU, 1GB, 24/7):
≈ $60/월
```

### GKE Standard 💰💰💰
```
클러스터 관리: $73/월
노드 비용 (e2-medium × 3): $73/월

총 예상 비용: $146/월
```

### 💡 비용 절감 팁

1. **개발/테스트 환경**
   - Cloud Run 사용 (사용하지 않을 때 0원)
   - 야간/주말에는 리소스 중지
   - 최소 스펙으로 시작

2. **프로덕션 환경**
   - Cloud Run 또는 GKE Autopilot 권장
   - 적절한 리소스 크기 설정
   - 모니터링으로 최적화

3. **비용 모니터링**
   - Cloud Billing 예산 알림 설정
   - 정기적인 리소스 리뷰
   - 미사용 리소스 삭제

---

## 참고 자료

### 공식 문서
- [Google Cloud 문서](https://cloud.google.com/docs)
- [Cloud Run 문서](https://cloud.google.com/run/docs)
- [GKE 문서](https://cloud.google.com/kubernetes-engine/docs)
- [Artifact Registry 문서](https://cloud.google.com/artifact-registry/docs)
- [Cloud SQL 문서](https://cloud.google.com/sql/docs)
- [Secret Manager 문서](https://cloud.google.com/secret-manager/docs)

### 프레임워크 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Django 공식 문서](https://docs.djangoproject.com/)
- [Uvicorn 문서](https://www.uvicorn.org/)
- [Gunicorn 문서](https://docs.gunicorn.org/)

### Docker 관련
- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [Dockerfile 베스트 프랙티스](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

### Kubernetes (GKE용)
- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [kubectl 치트시트](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### GCP CLI
- [gcloud 명령어 레퍼런스](https://cloud.google.com/sdk/gcloud/reference)
- [gcloud 치트시트](https://cloud.google.com/sdk/docs/cheatsheet)

