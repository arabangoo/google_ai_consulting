## [Cloud Run Functions과 Vertex AI 연동을 통한 PDF 요약]    

GCP에서 PDF 요약 AI 서비스를 구축하는 절차는 아래와 같다.   
   
(1) AI 서비스 프로젝트 생성   
(2) Cloud Storage 버킷 생성   
(3) Vertex AI API 활성화  
(4) Cloud Run Functions 함수 생성   
(5) PDF 요약 AI 서비스 테스트   
<br/>

(1) AI 서비스를 구성할 새로운 프로젝트를 만든다.      
<img width="600" alt="image_1" src="https://github.com/user-attachments/assets/fbeb8136-85d1-4bd9-9f5e-e0a3add5e8a1" />
<br/>
                
(2) Cloud Storage 버킷 생성  

1. Cloud Run Functions과 연동할 Cloud Storage 버킷과 폴더를 생성한다.           
<img width="1200" alt="image_2" src="https://github.com/user-attachments/assets/35759e8f-6778-4721-a925-970e17c42422" />
   
![image_3](https://github.com/user-attachments/assets/05b026e6-c342-4a17-ba30-8822f8dd6e29)   
<br/>
        
(3) Vertex AI Studio에서 AI 모델 요청  

1. Vertex AI Studio를 활성화한다.      
<img width="500" alt="image_4" src="https://github.com/user-attachments/assets/d749437b-fb25-4e61-8eb0-822ac784d4c4" />
<br/><br/>
                                
2. Vertex AI Studio의 모델 가든에서 원하는 AI 모델이 있는지 확인한다.     
![image_5](https://github.com/user-attachments/assets/0119cd68-186e-4a8e-b3df-ea49c7ab14db)
<img width="800" alt="image_6" src="https://github.com/user-attachments/assets/61c95814-4af1-4a90-b960-ede275310304" />
<br/><br/>

3. Vertex AI API를 활성화한다.   
Vertex AI API를 활성화 하면 구글의 AI 모델은 전부 사용할 수 있다.
<img width="600" alt="image_7" src="https://github.com/user-attachments/assets/7182d7b5-65cb-4150-a11a-cc535cf92a63" />
<br/><br/>

(4) Cloud Run Functions 함수 생성  

1. 이제 아래와 같이 파이썬 런타임 기반으로 Cloud Run Functions 함수를 생성하자.      
여기서는 Python 3.10 버전 런타임을 사용하겠다.      
메모리는 2GB 정도로 여유있게 설정하자.      
함수 생성 중간에 Cloud Build API를 활성화 하라는 문구가 뜨면 활성화 하자.   
<img width="1400" alt="image_8" src="https://github.com/user-attachments/assets/db926780-0819-4333-a4ef-dfcb0a09d445" />
<img width="800" alt="image_9" src="https://github.com/user-attachments/assets/3ca02461-8095-46ff-a9a2-8f32dd17cfe8" />
<br/><br/>

2. 다음은 Cloud Run Functions의 코드를 작성해준다.      
Cloud Run Functions은 서버에서 따로 컨테이너 띄워서 라이브러리를 패키징 해줄 필요가 없다.      
main.py에 실제 코드를 작성하고 requirements.txt에 라이브러리를 기입해주면 된다.        
<img width="1000" alt="image_10" src="https://github.com/user-attachments/assets/e8b3a3c2-30dc-4177-9c21-9684952078c4" />
<img width="1000" alt="image_11" src="https://github.com/user-attachments/assets/52484aa0-bdb3-4bbe-8285-37e40599ede6" />
<br/><br/>

3. Cloud Run Functions에서 사용할 main.py 코드는 아래와 같다.      

```python           
import functions_framework
from google.cloud import storage
from vertexai.generative_models import GenerativeModel
import pdfplumber
import os
from io import BytesIO
from urllib.parse import unquote_plus

# Google Cloud Storage 클라이언트 생성
storage_client = storage.Client()

# Gemini 모델 초기화 (Vertex AI Project ID는 환경 변수 GCP_PROJECT에서 자동 주입됨)
GEMINI_MODEL_ID = os.getenv('MODEL_ID', 'gemini-1.5-flash-001')
gemini_model = GenerativeModel(GEMINI_MODEL_ID)

# 환경 변수에서 버킷, 폴더 정보 가져오기
GCS_BUCKET_NAME = os.getenv('BUCKET_NAME')
GCS_FOLDER_NAME = os.getenv('FOLDER_NAME', 'ai-pdf-folder/')
GCS_SUMMARY_FOLDER_NAME = os.getenv('SUMMARY_FOLDER_NAME', 'ai-pdf-folder/summaries/')
GCS_ERROR_LOG_FOLDER_NAME = os.getenv('ERROR_LOG_FOLDER_NAME', 'ai-pdf-folder/error_logs/')


def invoke_gemini(query: str, max_tokens: int = 5000, temperature: float = 0.7, top_p: float = 0.9, top_k: int = 40) -> str:
    """Gemini 모델을 호출하여 텍스트를 생성합니다."""
    try:
        response = gemini_model.generate_content(
            contents=[{"role": "user", "parts": [{"text": query}]}],
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k
            }
        )
        return response.text
    except Exception as e:
        print(f"Gemini API 호출 중 오류 발생: {e}")
        raise

def get_all_texts_from_pdf(file_content: bytes) -> str:
    """PDF 파일 내용에서 모든 텍스트를 추출합니다."""
    with pdfplumber.open(BytesIO(file_content)) as pdf:
        return "".join([page.extract_text() for page in pdf.pages if page.extract_text() is not None])


@functions_framework.cloud_event
def pdf_summary_function(cloud_event):
    """
    Cloud Storage에 파일이 업로드될 때 트리거되는 Cloud Function입니다.
    PDF 파일을 요약하고 결과를 Cloud Storage에 저장합니다.
    """
    data = cloud_event.data
    
    bucket_name = data['bucket']
    file_name_encoded = data['name']
    
    file_name = unquote_plus(file_name_encoded)
    
    print(f"처리할 파일: {file_name} (버킷: {bucket_name})")

    if not file_name.endswith('.pdf'):
        print(f"PDF 파일이 아님: {file_name}. 처리 건너뜀.")
        return

    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(file_name)
        file_content = blob.download_as_bytes()
        print(f"PDF 파일 다운로드 완료: gs://{GCS_BUCKET_NAME}/{file_name}")

        pdf_text = get_all_texts_from_pdf(file_content)
        print("PDF 텍스트 추출 완료.")

        prompt = f"""
        다음 PDF 문서의 내용을 5000단어 이내로 상세히 요약해주세요.
        주요 주제, 핵심 아이디어, 중요한 세부 사항을 포함하여 문서의 전체적인 내용을 포괄적으로 다루어주세요.
        가능한 경우 문서에서 언급된 주요 통계, 데이터, 인용구 등을 포함해주세요.
        또한 문서의 구조와 논리적 흐름을 반영하여 요약해주세요.
        
        문서 내용: {pdf_text[:30000]}
        """
        print(f"프롬프트 (일부): {prompt[:500]}...")

        summary = invoke_gemini(prompt, max_tokens=4096)
        print(f"모델 응답 요약 (일부): {summary[:500]}...")

        base_file_name = os.path.basename(file_name)
        summary_file_name = base_file_name.replace('.pdf', '_summary.txt')
        summary_blob_path = f"{GCS_SUMMARY_FOLDER_NAME}{summary_file_name}"
        
        summary_blob = bucket.blob(summary_blob_path)
        summary_blob.upload_from_string(summary.encode('utf-8'))
        print(f"요약 파일 저장 완료: gs://{GCS_BUCKET_NAME}/{summary_blob_path}")

    except Exception as e:
        print(f"파일 {file_name} 처리 중 오류 발생: {str(e)}")
        error_log = f"파일: {file_name}\n오류: {str(e)}\n"
        base_file_name = os.path.basename(file_name)
        error_log_file_name = base_file_name.replace('.pdf', '_error.log')
        error_blob_path = f"{GCS_ERROR_LOG_FOLDER_NAME}{error_log_file_name}"
        
        error_blob = bucket.blob(error_blob_path)
        error_blob.upload_from_string(error_log.encode('utf-8'))
        print(f"오류 로그 저장 완료: gs://{GCS_BUCKET_NAME}/{error_blob_path}")
```
<br/>
   
4. Cloud Run Functions에서 사용할 requirements.txt 코드는 아래와 같다.         

```txt           
functions-framework
google-cloud-storage
google-cloud-aiplatform
pdfplumber
```
<br/>

5. 이제 코드에 맞는 환경변수를 설정하자.      
"새 버전 수정 및 배포"를 클릭한 후 "변수 및 보안 비밀" 항목에서 환경 변수를 설정하면 된다.       
<img width="1000" alt="image_12" src="https://github.com/user-attachments/assets/457f0963-d4db-463f-9e10-39d86c31daa8" />
<br/><br/>
   
6. Cloud Run Functions에서 Cloud Storage를 트리거로 지정한다.
![image_13](https://github.com/user-attachments/assets/94acef23-2493-4677-9873-c7410fb996e4)
<br/>

7. 트리거 설정에서 버킷을 지정하고 역할 권한 부여를 설정하고 경로까지 지정한다.   
특히 경로 지정에서는 폴더 경로와 파일의 확장자까지 명시하는 것이 핵심이다.
![image_14](https://github.com/user-attachments/assets/c36edea8-aedb-4962-a247-4d2d9d3d59ee)
<br/>

(5) PDF 요약 AI 서비스 테스트   
   
1. 이제 Cloud Storage 폴더에 PDF를 업로드한다.    
정상적으로 서비스가 실행되면 PDF 요약 파일이 생성된다.    
만약 에러가 발생하면 에러 로그 파일이 생성된다.
![image_15](https://github.com/user-attachments/assets/951bd7b6-6121-43b1-87f1-19b9d942d993)
<br/>

2. 생성된 텍스트 파일을 다운로드 하려고 하면 아래와 같이 브라우저에서 열리면서 글자가 깨져 보일 수 있다.   
![image_16](https://github.com/user-attachments/assets/c3c7fffe-c27f-4fe6-89c5-d1de66454704)
<br/>

3. 이런 현상은 텍스트 파일에 대한 GCP Cloud Storage의 렌더링 기능에 의한 것이다.       
이때는 바로 마우스 오른쪽 버튼을 클릭해서 "다른 이름으로 저장"을 선택한 후 로컬 PC에 파일을 다운로드 하면 된다.   
![image_17](https://github.com/user-attachments/assets/0732ba6c-8102-47d9-b74c-747303b2d028)
<br/>

4. 논문 요약 테스트를 위해 arXiv 등의 논문 사이트에서 논문 PDF를 다운로드해서 테스트 해보자.       
PDF 파일 요약 속도를 확인하며 너무 성능이 떨어지지 않게 Cloud Run Functions 사양을 조절해주면 된다.      
![image12](https://github.com/user-attachments/assets/1d63f609-b9a5-4fdc-85ad-93628d5208cd)
