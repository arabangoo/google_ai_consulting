## [Gemini Slack Chatbot 연동]    

본 테스트의 목표는 Gemini 모델을 연동해서 Slack 챗봇을 만드는 것이다.   
Vertex AI를 통해 Gemini 호출이 가능하다는 것을 전제로 매뉴얼이 작성되어 있다.    
또한 Slack에 RSS 형식으로 뉴스나 블로그를 수신받고 있다는 것도 전제로 하고 있다.      
<br/>

(1) 우선 Cloud Run 함수를 만든다.   
Cloud Run 서비스에 들어가 함수 작성을 한다.       
<img width="900" height="400" alt="image1" src="https://github.com/user-attachments/assets/53565da0-6a31-4609-919b-89b94524aa3d" />
<img width="1200" height="800" alt="image2" src="https://github.com/user-attachments/assets/6bd8847f-c428-4649-9779-1393fc67751f" />
<img width="1200" height="800" alt="image3" src="https://github.com/user-attachments/assets/5e416fe0-a834-478b-a7a7-89d18463a18d" />
<br/>
                
(2) 함수 진입점 이름은 "slack_events_handler"으로 기입한다.      
그리고 "main.py"와 "requirements.txt"를 작성한 후 배포를 한다.          
<img width="900" height="400" alt="image4" src="https://github.com/user-attachments/assets/81662f74-58ea-4aaa-b433-97bb23c039fc" />
<br/>
        
(3) Slack API 설정 페이지에 들어가서 "Create an APP"을 클릭하고 워크스페이스를 선택한다.      
Slack API 설정 페이지 : https://api.slack.com/apps      
<img width="1600" height="800" alt="image5" src="https://github.com/user-attachments/assets/138f724f-0f8f-4034-9399-ca25406f49ca" />
<br/>

(4) 그 다음 YAML 내용을 아래와 같이 기입한다.    
"request_url" 부분은 Cloud Run 함수 URL을 기입해준다.    

```json
{
    "display_information": {
        "name": "arabot"
    },
    "features": {
        "bot_user": {
            "display_name": "arabot",
            "always_online": true
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "app_mentions:read",
                "chat:write",
                "channels:history",
                "im:read",
                "im:history"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "https://temp.url/slack/events",
            "bot_events": [
                "app_mention",
                "message.im"
            ]
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```
<img width="1600" height="900" alt="image6" src="https://github.com/user-attachments/assets/58173b50-0999-407d-b77f-84a8ae7f70e2" />
<br/><br/>
   
(5) 슬랙봇이 생성되면 "OAuth & Permissions" 항목에 들어가서 OAuth Tokens을 인스톨한다.      
이때 "Bot User OAuth Token"이 생성되는데 메모장 등에 복사해둔다.      
<img width="1600" height="900" alt="image7" src="https://github.com/user-attachments/assets/f4498554-9a55-4a7d-b568-098a2fbad7e9" />
<br/>

(6) 다음은 "Basic Information" 항목에 들어가서 Signing Secret을 확인하고 메모장에 복사해둔다.     
<img width="600" height="800" alt="image8" src="https://github.com/user-attachments/assets/007c541a-0f4d-48ac-90b6-e6a4d1a4260e" />
<br/>

(7) 다음은 슬랙에서 채널 ID를 확인하고 메모장에 복사해둔다.     
<img width="400" height="600" alt="image9" src="https://github.com/user-attachments/assets/96fd4033-8e89-4ac9-a9ec-a915bfac82aa" />   
<img width="500" height="600" alt="image10" src="https://github.com/user-attachments/assets/00ae756b-a3de-4c48-9d55-1859f9653108" />
<br/>

(8) 지금까지 메모장에 복사해넣은 정보를 함수 코드 내용에 맞게 환경변수로 등록한다.
<img width="700" height="600" alt="image11" src="https://github.com/user-attachments/assets/7aa75665-e8d1-4081-b0c6-1b5348287a06" />
<br/><br/>

함수까지 전부 작성이 끝났으면 리소스 생성 절차는 다 끝난 것이다.   
이제 남은 건 Cloud Run 함수와 Slack을 연동해주는 작업뿐이다.   
<br/>

(9) Slack API 웹페이지로 돌아간 뒤 "Event Subscriptions" 항목을 선택한다.       
"Request URL"에 Cloud Run 함수 URL을 기입한다.      
Cloud Run 함수의 여러 탭 중에서 YAML 탭을 보면 함수 URL을 확인할 수 있다.       
그 뒤, 'Verified'라는 녹색 체크가 뜨면 맨 하단의 "Save Changes" 버튼을 클릭한다.           
<img width="900" height="800" alt="image12" src="https://github.com/user-attachments/assets/1f5e4923-20dc-41b9-8fd9-f4cd965dafee" />
<br/>

(10) 이제 Slack에서 테스트만 하면 된다.      
"@봇이름"으로 AI봇을 호출한 뒤 지시를 내려본다.      
만약 봇이 채널에 없다는 메시지가 나타나면 'Add Them' 버튼을 눌러 봇을 채널에 초대한다.         
<img width="800" height="400" alt="image13" src="https://github.com/user-attachments/assets/d2a77fba-e41b-4297-8a58-7104c52e6810" />
<br/>

(11) 채널에 봇이 추가되면 다시 "@봇이름"으로 AI봇을 호출한 뒤 지시를 내려본다.      
뉴스나 블로그 메시지에 "답장" 형태로 지시를 내리면 개별 분석을 더 잘해준다.              
<img width="1800" height="800" alt="image14" src="https://github.com/user-attachments/assets/0630eef5-7a6d-49d6-bb8a-575748d19610" />
<br/>

(12) 일상적인 질문에도 잘 대답해주니 여러 가지 질문으로 테스트 해보도록 한다.           
<img width="1800" height="600" alt="image15" src="https://github.com/user-attachments/assets/3cfff26b-3169-4849-b312-9e093c21fd56" />
<br/>



