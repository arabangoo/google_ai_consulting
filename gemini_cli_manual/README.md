## [Gemini CLI 활용]    

제미나이 CLI는 터미널 환경에서 Gemini AI 모델과 직접 상호작용할 수 있게 해주는 도구다.   
비슷한 도구로는 오픈AI의 ‘코덱스 CLI’, 앤스로픽의 ‘클로드 코드’, AWS의 ‘아마존 Q 디벨로퍼 CLI’가 있다.
<img width="800" alt="image_1" src="https://github.com/user-attachments/assets/98a5de30-7d7a-43b1-b8a9-194b9a24c72b" />
<br/>

---
   
[제미나이 CLI 설치 방법]   
(1) 우선 로컬 PC에서 아래 명령어로 Node.js와 npm을 설치하도록 하자.      
명령어 (1) : winget install OpenJS.NodeJS        
<img width="800" alt="image_2" src="https://github.com/user-attachments/assets/3044a6c0-f2d1-46c2-aefd-456610859a58" />
<br/>
                
(2) Node.js와 npm 버전을 확인하자.         
제미나이 CLI 정상 실행을 위해서는 Node.js 버전이 18 이상이어야 한다.         
명령어 (1) : node --version         
명령어 (2) : npm --version         
<img width="300" alt="image_3" src="https://github.com/user-attachments/assets/d4dbd27e-2586-452c-a85e-40fb28a1c898" />
<br/>
        
(3) 아래 명령어를 실행하여 제미나이 CLI를 설치한다.      
명령어 (1) : npm install -g @google/gemini-cli      
명령어 (2) : gemini      
<img width="700" alt="image_4" src="https://github.com/user-attachments/assets/15979517-5de1-4952-aa94-56676e3f7776" />
<br/>
      
(4) 세 가지 로그인 방법 중 하나를 선택해 제미나이 CLI에 로그인한다.         
<img width="1000" alt="image_5" src="https://github.com/user-attachments/assets/c508c853-9abf-4ecd-a6a3-adf3d8f0e596" />
<br/>

(5) 프롬프트를 입력해서 제미나이 CLI와 실제로 대화해본다.         
제미나이 CLI가 사용자 요구에 맞춰 로컬 PC 설정 파일까지 수정하는 것도 확인 가능하다.          
<img width="900" alt="image_6" src="https://github.com/user-attachments/assets/396f71c3-bc49-4b96-8474-40b8c926364c" />
<br/>

(6) 프롬프트창을 따로 열지 않고 "gemini --prompt" 명령어로 바로 프롬프트를 입력할 수도 있다.      
<img width="500" alt="image_7" src="https://github.com/user-attachments/assets/8ed22210-1830-4737-8a86-12c4aec2ca08" />
<br/>

---

[제미나이 CLI 장점과 활용법]   
(1) 제미나이 CLI 장점   
1. 반복적인 작업 자동화, 코드 생성, 문서 요약 등 다양한 작업을 터미널에서 바로 처리할 수 있다.   
2. 개발 환경에 익숙한 사용자들은 더욱 빠르고 효율적으로 AI를 자신의 워크플로우에 통합할 수 있다.   
3. 웹 UI에 접근하기 어렵거나 스크립트 내에서 AI 기능을 활용하고자 할 때 매우 유용하다.   
4. CLI는 셸 스크립트, 파이썬 스크립트 등과 연동하여 복잡한 자동화 워크플로우를 구축하는 강력한 기반이 된다.   
<br/>

(2) 제미나이 CLI 활용법   
1. 코드 작업 : 생성 및 수정, 디버깅, 리팩토링 및 최적화   
2. 문서 작업 : 문서 요약, 초안 작성, 브레인스토밍   
3. 학습 도우미 : 개념 설명, 외국어 번역, 정보 검색   
4. 시스템 관리 : 로그 분석, 보고서 생성, 스크립트 생성
