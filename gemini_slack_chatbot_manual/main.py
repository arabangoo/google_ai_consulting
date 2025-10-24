import os
import re
import threading
import vertexai
from flask import Flask, request
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from vertexai.generative_models import GenerativeModel

# --- 설정 (Cloud Function 환경 변수에서 값을 읽어옴) ---
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
MODEL_ID = os.environ.get("MODEL_ID", "gemini-1.5-pro-latest")

# GCP 환경에서는 project와 location을 자동으로 인식합니다.
vertexai.init() 
slack_client = WebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# --- 프롬프트 정의 ---
ANALYSIS_SYSTEM_PROMPT = """
# **역할**:
당신은 최고의 AI 분석 파트너 '아라봇'입니다. 당신은 뉴스, 블로그, 리포트 등의 텍스트를 깊이 있게 분석하고, 객관적인 사실 기반의 분석과 날카로운 통찰력을 제공합니다.

# **임무**:
주어진 뉴스, 블로그, 리포트를 전문 분석가로서 핵심 요약, 이해관계자 분석, 잠재적 파급 효과, 최종 결론을 포함한 심층 분석 보고서를 작성합니다.
"""

GENERAL_SYSTEM_PROMPT = """
# **역할**:
당신은 친근하고 도움이 되는 AI 어시스턴트 '아라봇'입니다. 사용자와 자연스럽고 창의적인 대화를 나누며, 다양한 질문에 유용하고 흥미로운 답변을 제공합니다.

# **임무**:
사용자의 질문이나 요청에 대해 창의적이고 도움이 되는 답변을 제공합니다. 딱딱한 보고서 형식이 아닌, 자연스러운 대화 형태로 응답합니다.
"""

analysis_model = GenerativeModel(MODEL_ID, system_instruction=[ANALYSIS_SYSTEM_PROMPT])
general_model = GenerativeModel(MODEL_ID, system_instruction=[GENERAL_SYSTEM_PROMPT])

# --- Flask 앱 초기화 ---
app = Flask(__name__)

def is_news_or_report_request(text):
    """뉴스, 블로그, 리포트 관련 요청인지 판단"""
    keywords = ["뉴스", "기사", "블로그", "리포트", "보고서", "분석", "요약", "정리", "소식", "발표", "공지"]
    analysis_keywords = ["분석해줘", "분석해달라", "요약해줘", "요약해달라", "정리해줘", "정리해달라"]
    
    # 키워드 기반 검사
    text_lower = text.lower()
    has_keyword = any(keyword in text for keyword in keywords)
    has_analysis_request = any(keyword in text for keyword in analysis_keywords)
    
    return has_keyword and has_analysis_request

def extract_news_content(messages):
    """메시지 목록에서 뉴스, 블로그, 리포트 관련 내용만 추출"""
    news_content = []
    
    # URL이 포함된 메시지나 뉴스 관련 키워드가 포함된 긴 메시지를 찾음
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    news_keywords = ["뉴스", "기사", "블로그", "리포트", "보고서", "발표", "공지", "소식"]
    
    for msg in messages:
        text = msg.get("text", "")
        
        # URL이 포함되었거나, 뉴스 키워드가 있으면서 충분히 긴 메시지
        if (re.search(url_pattern, text) or 
            (any(keyword in text for keyword in news_keywords) and len(text) > 100)):
            news_content.append(text)
    
    return news_content

def process_slack_event(event):
    """실제 AI 처리 로직을 별도 스레드에서 실행"""
    try:
        channel_id = event.get("channel")
        user_text_full = event.get("text", "")
        thread_ts = event.get("thread_ts") # 스레드 여부 확인

        # 멘션 부분(<@Uxxxx>) 제거
        prompt_text = user_text_full.split('>', 1)[-1].strip()

        # 1. 스레드(Thread) 안에서의 대화일 경우 (토론 기능)
        if thread_ts:
            replies = slack_client.conversations_replies(channel=channel_id, ts=thread_ts)
            conversation_history = []
            for message in replies['messages']:
                role = "model" if message.get("bot_id") else "user"
                content = message["text"].split('>', 1)[-1].strip()
                conversation_history.append(f"{role}: {content}")
            
            context_prompt = "\n".join(conversation_history)
            final_prompt = f"다음 대화의 맥락을 보고 마지막 사용자 질문에 답변해줘.\n\n--- 대화 기록 ---\n{context_prompt}\n---"
            
            # 스레드에서는 일반 모델 사용 (자유로운 대화)
            response_text = general_model.generate_content(final_prompt).text
            slack_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=thread_ts)

        # 2. 메인 채널에서의 새로운 호출일 경우
        else:
            # 뉴스/리포트 분석 요청인지 확인
            if is_news_or_report_request(prompt_text):
                # 최근 메시지에서 뉴스/리포트 관련 내용만 추출
                history = slack_client.conversations_history(channel=channel_id, limit=20)
                news_articles = extract_news_content(history["messages"][1:])  # 봇 호출 메시지 제외
                
                if news_articles:
                    news_content = "\n\n=== 뉴스/리포트 구분 ===\n".join(news_articles)
                    final_prompt = f"다음은 최근 공유된 뉴스, 블로그, 리포트 내용입니다. 심층 분석해 주세요:\n\n--- 분석 대상 ---\n{news_content}\n---"
                    response_text = analysis_model.generate_content(final_prompt).text
                else:
                    response_text = "최근 채널에서 분석할 뉴스, 블로그, 리포트 관련 내용을 찾을 수 없습니다. 분석하고 싶은 내용을 직접 공유해 주세요."
                
                slack_client.chat_postMessage(channel=channel_id, text=response_text)
            
            # 긴 텍스트가 포함된 분석 요청 (사용자가 직접 뉴스/리포트를 제공)
            elif len(prompt_text) > 200 and any(keyword in prompt_text for keyword in ["분석", "요약", "정리"]):
                final_prompt = f"다음 텍스트를 심층 분석해 주세요:\n\n--- 분석 대상 ---\n{prompt_text}\n---"
                response_text = analysis_model.generate_content(final_prompt).text
                slack_client.chat_postMessage(channel=channel_id, text=response_text)
            
            # 일반적인 질문이나 대화
            else:
                response_text = general_model.generate_content(prompt_text).text
                slack_client.chat_postMessage(channel=channel_id, text=response_text)

    except Exception as e:
        channel_id = event.get("channel")
        slack_client.chat_postMessage(channel=channel_id, text=f"요청 처리 중 오류가 발생했습니다: {e}")

@app.route("/", methods=["POST"])
def slack_events_handler(request):
    """ Slack 이벤트를 받아 처리하는 기본 핸들러 """
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return "Invalid request", 403
    
    request_json = request.get_json(silent=True)

    if request_json and "challenge" in request_json:
        return request_json["challenge"]

    if request_json and "event" in request_json:
        event = request_json["event"]
        if event.get("type") == "app_mention":
            threading.Thread(target=process_slack_event, args=(event,)).start()

    return "OK", 200