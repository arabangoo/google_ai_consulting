## [구글 코랩에서 허깅페이스 사용]

구글 코랩에서 허깅페이스를 사용해보도록 하자. 
<br/><br/>
    
1. 허깅페이스에서 Access Token 발급받기
<br/>
(1) 우선 아래 링크에 접속해서 허깅페이스 토큰을 발급받도록 하자.
<br/>    
https://huggingface.co/settings/tokens   
<img width="1000" alt="image1" src="https://github.com/user-attachments/assets/2edc5e10-7876-4f7c-b02c-cc722c8bc00f">
<br/><br/>

(2) 토큰 이름은 자유롭게 정하면 되고 권한은 "Read"를 선택한다.   
<img width="1000" alt="image2" src="https://github.com/user-attachments/assets/6a819b36-46fd-4a8b-b57b-d71fb3ad95f0">
<br/><br/>
         
2. 구글 코랩 환경 구성
<br/>    
(1) 딥러닝 Open API를 사용하려면 코딩이 필요한데, 코딩을 하려면 파이썬이 설치된 환경이 필요하다.
<br/>              
구글이 만들어 놓은 코랩을 사용하면 파이썬으로 코딩을 할 수 있다.
<br/>       
https://colab.research.google.com/?hl=ko      
<img width="1800" alt="image3" src="https://github.com/user-attachments/assets/cf343e66-a9db-4483-bd18-a7fb98c25f88">
<br/><br/>

(2) 우선 구글 계정으로 로그인 하면 계정 정보 옆에 네모 표시가 나타난다.   
하위 메뉴에서 "드라이브"를 선택해준다.   
![image4](https://github.com/user-attachments/assets/e321da5c-c18f-4bef-8a5f-04decc61e371)
<br/><br/>
    
(3) 드라이브 왼쪽 상단에 "+ New" 버튼을 누르면, 드라이브에서 사용할 수 있는 기능이 나오는데   
"더보기" 버튼을 눌러 "Google Colaboratory"를 클릭한다.    
만약 "Google Colaboratory" 메뉴가 보이지 않으면 이 앱을 추가해줘야 한다.   
"연결할 앱 더보기" 버튼을 클릭한다.   
"Colaboratory"를 검색한 후 설치를 진행한다.   
<img width="1000" alt="image5" src="https://github.com/user-attachments/assets/9940d2d9-388d-4932-9993-8539a9c243fa">
<br/><br/>
    
(4) 이제 다시 코랩 웹페이지로 돌아가서 새 노트를 만들어보자.   
https://colab.research.google.com/?hl=ko   
이제 파이썬 코드를 작성해서 실행할 수 있는 환경이 마련되었다.   
로컬 PC에 파이썬이 설치된 것은 아니고 가공간에 파이썬을 설치하고 사용권한을 받은 것이다.   
<img width="1800" alt="image6" src="https://github.com/user-attachments/assets/b206185d-e5c6-4701-ad25-0096cb24699c">
<br/><br/>
           
(5) hello world! 출력하기   
코 노트에 아래 문구를 입력하고 실행해보자.   
코드 : print("hello world")   
<img width="500" alt="image7" src="https://github.com/user-attachments/assets/a5cbdab9-2e96-41e6-8c38-34842d45f36c">
<br/><br/>

(6) 코랩 파이썬 버전 확인하기   
아래 명령어로 코랩의 파이썬 버전을 확인해보자.    
python 앞에 !(느낌표)를 붙이면, 명령 프롬프트에서 시스템 명령어를 실행하는 것과 동일하다.   
코드 : !python --version   
<img width="400" alt="image8" src="https://github.com/user-attachments/assets/8fdb3285-3156-40e1-b74a-bcb19040a3b8">
<br/><br/>

3. 구글 코랩에서 허깅페이스 사용하기
<br/>
(1) 우선 구글 코랩의 런타임 유형을 "T4 GPU"로 바꾸도록 한다.
<br/> 
<img width="500" alt="image9" src="https://github.com/user-attachments/assets/752e75fe-1e9a-4445-bf80-707aa8efac0a">
<br/><br/>
    
(2) 구글 코랩에서 아래 코드를 입력하고 실행해보자.   
만약 코드에 기입된 모델이 더 이상 지원이 안 되면 다른 모델로 바꾸도록 하자.   
모델에 따라서는 허깅페이스 모델 페이지에서 사용 요청을 해야할 수도 있다.   
<img width="800" alt="image10" src="https://github.com/user-attachments/assets/80e0c9d9-567e-4ebc-8a06-8a5932472bca">

사용이 허락된 모델은 아래 링크에서 확인 가능하다.      
https://huggingface.co/settings/gated-repos   
<img width="800" alt="image11" src="https://github.com/user-attachments/assets/9f3691b7-210d-457d-a610-6ed8a4a5796e">
<br/><br/>

```python       
import os
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# ==== Step 1: Securely Provide Your Hugging Face API Token ====
# 추천 방법: 입력을 통해 토큰을 안전하게 제공
hf_token = input("Enter your Hugging Face API token: ")

# ==== Step 2: Define the Model ID ====
model_id = "meta-llama/Meta-Llama-3.1-8B"

# ==== Step 3: Initialize the Tokenizer and Model with Authentication ====
try:
    # 토크나이저 초기화 (토큰을 'token' 파라미터로 전달)
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        token=hf_token
    )
    
    # 모델 초기화 (토큰을 'token' 파라미터로 전달)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,  # 하드웨어가 지원하지 않으면 변경
        device_map="auto",
        token=hf_token
    )
    
    print("모델과 토크나이저가 성공적으로 로드되었습니다.")
except Exception as e:
    print(f"모델/토크나이저 로딩 중 에러 발생: {e}")
    raise e

# ==== Step 4: Create the Text Generation Pipeline ====
try:
    text_gen_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    print("텍스트 생성 파이프라인이 성공적으로 생성되었습니다.")
except Exception as e:
    print(f"파이프라인 생성 중 에러 발생: {e}")
    raise e

# ==== Step 5: Define Your Prompt and Instructions ====
PROMPT = '''당신은 유용한 AI 어시스턴트입니다. 사용자의 질의에 대해 친절하고 정확하게 답변해야 합니다.
You are a helpful AI assistant, you'll need to answer users' queries in a friendly and accurate manner.'''

instruction = "대한민국의 관광지 5곳만 추천해달라."

messages = [
    {"role": "system", "content": f"{PROMPT}"},
    {"role": "user", "content": f"{instruction}"}
]

# ==== Step 6: Construct the Chat Prompt ====
def construct_chat_prompt(messages):
    chat_prompt = ""
    for message in messages:
        if message["role"] == "system":
            chat_prompt += f"System: {message['content']}\n"
        elif message["role"] == "user":
            chat_prompt += f"User: {message['content']}\n"
        elif message["role"] == "assistant":
            chat_prompt += f"Assistant: {message['content']}\n"
    # 어시스턴트의 응답을 유도
    chat_prompt += "Assistant: "
    return chat_prompt

chat_prompt = construct_chat_prompt(messages)
print("구성된 챗 프롬프트:")
print(chat_prompt)

# ==== Step 7: Define Terminators ====
# 생성 종료 토큰 정의
terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|eot_id|>")  # 모델 따라 조정
]

# ==== Step 8: Generate the Response ====
try:
    outputs = text_gen_pipeline(
        chat_prompt,
        max_new_tokens=256,                 # 필요에 따라 조정
        eos_token_id=terminators,            # 생성 종료 토큰
        do_sample=True,                      # 샘플링 활성화
        temperature=1.0,                     # 무작위성 조절
        top_p=0.9,                           # 누적 확률 조절
    )
    
    # 생성된 텍스트 추출 및 출력
    generated_text = outputs[0]["generated_text"]
    response = generated_text[len(chat_prompt):].strip()
    print("\n생성 응답:")
    print(response)
except Exception as e:
    print(f"텍스트 생성 중 에러 발생: {e}")
    raise e
```
<br/>

(3) 모델과 instruction에 따라서 시간이 다소 걸릴 수도 있으니 30분 정도는 기다려보자.   
아래와 같이 답변이 출력되면 정상적으로 코드가 실행된 것이다.    
<img width="800" alt="image12" src="https://github.com/user-attachments/assets/be2727b4-cca4-43ab-a7d1-3fcaad75a630">
<br/><br/>

4. 기업용 구글 코랩 사용하기      
기업용 구글 코랩을 사용하려면 구글 클라우드를 통해 사용해야 한다.            
<img width="1400" alt="colab_enterprise" src="https://github.com/user-attachments/assets/e9b02a4d-43c9-4cc3-aec7-489a41f20e0b" />
