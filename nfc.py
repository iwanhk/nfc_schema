import requests
import csv
import time
import sys

# 钛文创
APPID = "wx97376bdd89b0c344"
APPSECRET = "9fdebc8b0ae84cd125af9624aded94b6"
# MODEL_ID = "-UESYamd8dP0Phl5NAGh6w"
MODEL_ID = "xt2ffIbFxRuHUZm0AUOoow"

def _get_access_token():
    """获取access_token（有效期2小时）"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"HTTP请求失败: {response.status_code}")
    data = response.json()
    if 'access_token' not in data:
        raise Exception(f"获取token失败: {data}")
    return  data['access_token']

def generate_scheme(path, query):
    data = {
        "jump_wxa": {
            "path": path,
            "query": query
        },
        "is_expire": False
    }
    response = requests.post(f"https://api.weixin.qq.com/wxa/generatescheme?access_token={_get_access_token()}", json=data)
    result = response.json()
    if result.get("errcode") == 0:
        return result.get("openlink")
    else:
        print("Error:", result)
        return None

def process_csv(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        output = []
        for row in reader:
            path = row["页面路径"].strip()
            query = row["页面参数"].strip()
            remark = row.get("备注", "")
            print(f"正在处理: {path}?{query}")
            link = generate_scheme(path, query)
            if link:
                output.append([path, query, link, remark])
            time.sleep(0.2)  # 防止触发频控
    return output

def save_result(data, output_file="nfc_scheme_links.csv"):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["页面路径", "参数", "Scheme跳转链接", "备注"])
        writer.writerows(data)

if __name__ == "__main__":
    result = process_csv(sys.argv[1] if len(sys.argv) > 1 else "nfc_scheme.csv")
    save_result(result)
    print("✅ 所有 NFC 标签链接生成完毕！")
