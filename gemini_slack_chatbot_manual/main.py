import os
import re
import threading
import requests  
from bs4 import BeautifulSoup  
import vertexai
from flask import Flask, request
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from vertexai.generative_models import GenerativeModel

# --- 설정 (Cloud Function 환경 변수에서 값을 읽어옴) ---
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
MODEL_ID = os.environ.get("MODEL_ID", "gemini-2.5-flash")

# GCP 환경 초기화
vertexai.init() 
slack_client = WebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# --- 프롬프트 정의 ---
ANALYSIS_SYSTEM_PROMPT = """
# **역할**:
당신은 최고의 AI 분석 파트너 '아라봇'입니다. 
제공된 **뉴스 기사 본문**을 바탕으로 깊이 있는 분석을 수행해야 합니다.
단순히 내용을 요약하는 것을 넘어, 이면의 함의, 업계에 미칠 영향, 이해관계자 분석 등을 포함해 주세요.

# **임무**:
전문 분석가로서 핵심 요약, 주요 쟁점, 잠재적 파급 효과, 결론을 포함한 심층 리포트를 작성하세요.
"""

GENERAL_SYSTEM_PROMPT = """
# **역할**:
당신은 친근하고 도움이 되는 AI 어시스턴트 '아라봇'입니다.

# **임무**:
사용자의 질문에 자연스럽고 창의적인 대화 형태로 응답하세요.
"""

analysis_model = GenerativeModel(MODEL_ID, system_instruction=[ANALYSIS_SYSTEM_PROMPT])
general_model = GenerativeModel(MODEL_ID, system_instruction=[GENERAL_SYSTEM_PROMPT])

# --- Flask 앱 초기화 ---
app = Flask(__name__)

def scrape_webpage(url):
    """URL에서 본문 텍스트를 추출하는 함수"""
    try:
        # 일부 사이트는 봇 접근을 막으므로 헤더를 설정하여 브라우저처럼 위장
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5) # 5초 타임아웃
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # <script>, <style> 등 불필요한 태그 제거
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()

        # 본문 텍스트 추출 (주로 <p> 태그나 본문 div에 있음. 여기서는 전체 텍스트 추출 후 정제)
        text = soup.get_text(separator=' ', strip=True)
        
        # 텍스트가 너무 길면 자름 (토큰 비용 절약 및 오류 방지, 약 10,000자)
        return text[:10000]
        
    except Exception as e:
        print(f"Scraping failed for {url}: {e}")
        return None

def is_news_or_report_request(text):
    """뉴스 분석 요청인지 키워드로 판단"""
    keywords = ["뉴스", "기사", "블로그", "리포트", "보고서", "분석", "요약", "정리"]
    analysis_keywords = ["분석해줘", "분석해달라", "요약해줘", "요약해달라", "정리해줘", "정리해달라"]
    
    text_lower = text.lower()
    has_keyword = any(keyword in text for keyword in keywords)
    has_analysis_request = any(keyword in text for keyword in analysis_keywords)
    
    return has_keyword and has_analysis_request

def extract_news_content_with_scraping(messages):
    """메시지에서 URL을 찾아 내용을 스크래핑하거나 텍스트를 추출"""
    extracted_contents = []
    
    # URL 정규표현식
    url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
    
    # 분석 대상 키워드
    news_keywords = ["뉴스", "기사", "블로그", "리포트", "보고서", "발표", "공지", "소식"]

    for msg in messages:
        text = msg.get("text", "")
        
        # 1. URL이 있는지 확인
        urls = re.findall(url_pattern, text)
        if urls:
            for url in urls:
                # URL 끝에 붙은 '>' 같은 찌꺼기 제거 (Slack 포맷 특성)
                clean_url = url.rstrip('>')
                print(f"Scraping URL: {clean_url}")
                scraped_text = scrape_webpage(clean_url)
                
                if scraped_text:
                    extracted_contents.append(f"--- [기사 원문 내용: {clean_url}] ---\n{scraped_text}")
                else:
                    # 스크래핑 실패 시 원본 메시지 텍스트라도 사용
                    extracted_contents.append(f"--- [기사 요약(스크래핑 실패)] ---\n{text}")
        
        # 2. URL은 없지만 뉴스 키워드가 있고 긴 텍스트인 경우
        elif any(keyword in text for keyword in news_keywords) and len(text) > 100:
            extracted_contents.append(f"--- [텍스트 뉴스] ---\n{text}")
            
    return extracted_contents

def process_slack_event(event):
    """실제 AI 처리 로직 (스레드 실행)"""
    try:
        channel_id = event.get("channel")
        user_text_full = event.get("text", "")
        thread_ts = event.get("thread_ts") 

        # 멘션 부분 제거
        if '>' in user_text_full:
            prompt_text = user_text_full.split('>', 1)[-1].strip()
        else:
            prompt_text = user_text_full

        # 1. 스레드 대화 (토론)
        if thread_ts:
            replies = slack_client.conversations_replies(channel=channel_id, ts=thread_ts)
            conversation_history = []
            for message in replies['messages']:
                role = "model" if message.get("bot_id") or message.get("user") == "USLACKBOT" else "user"
                content = message["text"]
                if '>' in content: content = content.split('>', 1)[-1].strip()
                conversation_history.append(f"{role}: {content}")
            
            context_prompt = "\n".join(conversation_history)
            final_prompt = f"다음 대화 맥락을 보고 답변해줘:\n{context_prompt}"
            
            response_text = general_model.generate_content(final_prompt).text
            slack_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=thread_ts)

        # 2. 메인 채널 호출
        else:
            # A. 뉴스/리포트 분석 요청
            if is_news_or_report_request(prompt_text):
                # 최근 메시지 가져오기
                history = slack_client.conversations_history(channel=channel_id, limit=10) # 10개만 봐도 충분
                
                # 봇 호출 메시지 제외하고 이전 메시지들에서 뉴스 추출
                # [수정됨] 스크래핑 함수 사용
                news_contents = extract_news_content_with_scraping(history["messages"][1:])
                
                if news_contents:
                    full_content = "\n\n".join(news_contents)
                    final_prompt = f"다음은 수집된 뉴스 기사의 원문 내용입니다. 이를 바탕으로 아주 상세하게 분석해 주세요:\n\n{full_content}"
                    response_text = analysis_model.generate_content(final_prompt).text
                else:
                    response_text = "최근 대화에서 분석할 만한 뉴스 링크나 긴 텍스트를 찾지 못했습니다."
                
                slack_client.chat_postMessage(channel=channel_id, text=response_text)
            
            # B. 직접 URL이나 긴 텍스트를 입력하며 분석 요청한 경우
            elif len(prompt_text) > 200 or "http" in prompt_text:
                # 입력된 텍스트 안에 URL이 있다면 스크래핑 시도
                urls = re.findall(r'(http[s]?://\S+)', prompt_text)
                if urls:
                    scraped_data = []
                    for url in urls:
                        clean_url = url.rstrip('>')
                        content = scrape_webpage(clean_url)
                        if content: scraped_data.append(content)
                    
                    if scraped_data:
                         prompt_text = "\n".join(scraped_data)

                final_prompt = f"다음 내용을 심층 분석해 주세요:\n\n{prompt_text}"
                response_text = analysis_model.generate_content(final_prompt).text
                slack_client.chat_postMessage(channel=channel_id, text=response_text)
            
            # C. 일반 대화
            else:
                response_text = general_model.generate_content(prompt_text).text
                slack_client.chat_postMessage(channel=channel_id, text=response_text)

    except Exception as e:
        print(f"Error: {e}")
        slack_client.chat_postMessage(channel=event.get("channel"), text=f"오류 발생: {e}")

@app.route("/", methods=["POST"])
def slack_events_handler(request):
    """ Slack 이벤트 핸들러 (재시도 방지 포함) """
    
    # 중복 요청 방지
    if request.headers.get("X-Slack-Retry-Num"):
        return "OK", 200

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

