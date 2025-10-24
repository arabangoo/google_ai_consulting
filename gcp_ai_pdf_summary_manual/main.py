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