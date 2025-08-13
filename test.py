import requests

APPID = "wx97376bdd89b0c344"
APPSECRET = "9fdebc8b0ae84cd125af9624aded94b6"

url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
response = requests.get(url)
print(response.json())

