#마지막에 배포를 위해 축약하려 app.run을 사용함.
import os
from pprint import pprint as pp # 파이썬이 가지고 있는 기본 모듈. pprint as pp = pp만 써도 되도록.
from flask import Flask, request
import requests
import random
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
    
api_url = 'https://api.hphk.io/telegram' #bot{}/{}".format(token,method)
token = os.getenv('TELE_TOKEN')

@app.route(f'/{token}', methods=['POST'])
def telegram():
    #naver API 사용하기 위한 변수
    naver_client_id = os.getenv('NAVER_ID')
    naver_client_secret = os.getenv('NAVER_SECRET')
    
    
    tele_dict = request.get_json()
    # pp(request.get_json())
    # tele_dict = {'message': {'@service': 'naverservice.nmt.proxy',
    #              '@type': 'response',
    #              '@version': '1.0.0',
    #              'result': {'srcLangType': 'ko',
    #                         'tarLangType': 'en',
    #                         'translatedText': 'Why'}}}
    
    
    user_id = tele_dict['message']['from']['id'] # 유저 정보
    # text = tele_dict['message']['text'] # 유저 입력 데이터
    text = tele_dict.get("message").get("text") # 유저 입력 데이터
    # pp(request.get_json())
    
    tran = False
    img = False
    # image와 text 구분
    if tele_dict.get('message').get('photo') is not None: # 사진을 넣으면 사진이고, 그렇지 않으면 텍스트라고 인식.
        img = True
    
    
    # 유저가 입력한 데이터 맨 앞 두 글자가 "번역"이어야 번역된 말이 나오도록
    else:
        if text[:2] == "번역": # [:2] : str의 앞 두 글자
            tran = True
            text = text.replace("번역", "")
    # print(user_id)
    # print(text)
    
    if tran:
        papago = requests.post("https://openapi.naver.com/v1/papago/n2mt",
                    headers = {
                        "X-Naver-Client-Id":naver_client_id,
                        "X-Naver-Client-Secret":naver_client_secret
                    },
                    data = {
                        'source':'ko',
                        'target':'en',
                        'text':text
                    }
        )    
        
        text = papago.json()['message']['result']['translatedText']
    elif img:
        text = "사용자가 이미지를 넣었어요." 
        # 사진 정보 가져오고, 유명인 api 넘기고, 필요 정보 가져오기.
        file_id = tele_dict['message']['photo'][-1]['file_id'] #photo는 list임을 확인하고, -1번째는 마지막 번쨰라는 점!
        file_path = requests.get(f"{api_url}/bot{token}/getFile?file_id={file_id}").json()['result']['file_path']
        file_url = f"{api_url}/file/bot{token}/{file_path}"
        print(file_url)
        file = requests.get(file_url, stream=True) # stream이 뭘까?
        clova = requests.post("https://openapi.naver.com/v1/vision/celebrity",
                headers = {
                    "X-Naver-Client-Id":naver_client_id,
                    "X-Naver-Client-Secret":naver_client_secret
                },
                files = {
                    'image' : file.raw.read() # raw는 원본 데이터를 그대로 보내준다.
                }
        )
        #인식이 되었을 때
        if clova.json().get('info').get('faceCount'):
            text = clova.json()['faces'][0]['celebrity']['value']
        #인식이 되지 않았을 때
        else:
            text = "사람이 없어요"
        pp(clova.json())
    elif text == "메뉴":
        menu_list = ["버터장조림", "그라탕", "짜장면", "라면"]
        text = random.choice(menu_list) # 어차피 덮어씌워져도 괜찮으니까
    elif text == "로또":
        text = random.sample(range(1, 46), 6)
    elif text == "사망 원인":
        list_disease = []
        for page in list(range(1, 10)):
            url_death = 'https://terms.naver.com/list.nhn?cid=50871&categoryId=50871&page={}'.format(page)
            res_death = requests.get(url_death).text
            soup_death = BeautifulSoup(res_death, 'html.parser')
            for kinds in list(range(1, 7)):
                input = soup_death.select_one('#content > div.list_wrap > ul > li:nth-of-type({}) > div > div.subject > strong > a'.format(kinds))
                list_disease.append(input.text)
            text = random.choice(list_disease)
            
    requests.get(f'{api_url}/bot{token}/sendMessage?chat_id={user_id}&text={text}') # 메아리
    return ('', 200)
    
app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080))) 
# IP는 Terminal에서 $IP와 동일, PORT는숫자로 받아야하기에 int형으로 변환.

# format에 대해 // a = 123, "asdf{}".format(a) = asdf123 = f."asdf{a}"