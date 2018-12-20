import os
import requests
import json

token = os.getenv('TELE_TOKEN')
method = 'getUpdates' 

# url = "https://api.telegram.org/bot{}/{}".format(token, method) # c9 환경에서는 사용 불가, local에서는 가능
url = "https://api.hphk.io/telegram/bot{}/{}".format(token,method)

res = requests.get(url).json()

user_id = res["result"][0]["message"]["from"]["id"] # list는 순서로 받는다. key가 아니다.

msg = "야"

method = 'sendMessage'

msg_url = "https://api.hphk.io/telegram/bot{}/{}?chat_id={}&text={}".format(token, method, user_id, msg) # ?는 뒤에 인자값이 나온다는 뜻.
print(msg_url)
requests.get(msg_url)