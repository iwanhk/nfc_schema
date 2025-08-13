import requests
import json
import pandas as pd
import numpy as np
import sys
import os
from tqdm import tqdm  # pip install tqdm
from dotenv import load_dotenv, set_key
import random
import string
import urllib.parse
import logging

# --------------------------
# 配置日志
# --------------------------
log_file = "nfc_schema.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        # logging.StreamHandler()  # 同时输出到控制台
    ]
)

class WechatNFCSchemeGenerator:
    def __init__(self, appid, appsecret, model_id):
        self.appid = appid
        self.appsecret = appsecret
        self.model_id = model_id
        self.access_token = None

    def _get_access_token(self):
        """获取access_token（有效期2小时）"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        data = response.json()
        if 'access_token' not in data:
            raise Exception(f"获取token失败: {data}")
        self.access_token = data['access_token']
        return self.access_token

    def generate_nfc_scheme(self, path="/pages/index/index", query="", env_version="release", sn=None):
        """生成NFC Scheme"""
        if not self.access_token:
            self._get_access_token()

        # 构造请求体（来自）
        payload = {
            "jump_wxa": {
                "path": path,
                "query": query,  # 添加随机码到查询参数
                "env_version": env_version  # release（线上）/trial（体验）/develop（开发）
            },
            "model_id": self.model_id
        }
        if sn:
            payload["sn"] = sn  # 可选设备序列号（某些硬件场景需要）

        url = f"https://api.weixin.qq.com/wxa/generatenfcscheme?access_token={self.access_token}"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            result = response.json()
            if result.get("errcode") == 0:
                return result["openlink"]
            else:
                raise Exception(f"接口返回错误: {result}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {str(e)}")

def random_code(length=6):
    chars = string.ascii_letters + string.digits  # 大小写字母 + 数字
    return urllib.parse.quote(''.join(random.choices(chars, k=length)))

def gen_schema(sn, code, rd="release"):
    # 初始化配置（替换为实际参数）
    # 钛文创
    load_dotenv()  # 读取 .env 文件
    APPID = os.getenv("APPID")
    APPSECRET = os.getenv("APPSECRET")
    # MODEL_ID = "-UESYamd8dP0Phl5NAGh6w"
    MODEL_ID = "xt2ffIbFxRuHUZm0AUOoow"

    # 敦煌
    # APPID = "wx7ff39089532d58ed"
    # APPSECRET = "d587bcf89e0134df35f08ca1967e5e4f"
    # MODEL_ID = "UESYamd8dP0Phl5NAGh6w"
    
    generator = WechatNFCSchemeGenerator(APPID, APPSECRET, MODEL_ID)
    try:
        scheme_url = generator.generate_nfc_scheme(
            path=f"/pages/index/index",     # 小程序首页路径
            query= f"contentId=1&tenantId=1&id=1&code={code}",
            env_version=rd,      # 开发版
            sn= str(sn)          # 可选设备序列号（某些硬件场景需要）
        )
        # print("生成的NFC Scheme:", scheme_url)
    except Exception as e:
        print("生成失败:", str(e))
        return None
    return scheme_url

# 使用示例
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python genExcel.py <NUMBER> <EXCEL_FILE> <ENV_VERSION>")
        sys.exit(1)
    
    totalNumber= int(sys.argv[1])
    excelFile = sys.argv[2]
    if len(sys.argv) > 3:
        env_version = sys.argv[3]
    else:
        env_version = "release"  # 默认使用 release 版本

    # 从 .env 读取上次最大列数
    last_max = os.getenv("LAST_MAX_COLUMNS")
    last_max = int(last_max) if last_max is not None else 0
    print(f"上次生成的最大列数是: {last_max}")

    SN=[]
    SCHEMA=[]
    QUERY=[]
    CODE=[]
    ENV=[]
    for sn in tqdm(range(last_max, last_max+totalNumber ), desc="生成数据", unit="个"):
        code= random_code(6)
        schema = gen_schema(sn, code, env_version)  # 可以根据需要修改为 "trial" 或 "develop"
        if schema:
            # 更新 .env 文件中的 LAST_MAX_COLUMNS
            set_key(".env", "LAST_MAX_COLUMNS", str(sn+1))
            SN.append(sn)
            SCHEMA.append(schema)
            QUERY.append(f"contentId=1&tenantId=1&id=1&code={code}")
            CODE.append(code)
            ENV.append(env_version)
            logging.info(f"env={env_version}, sn={sn}, code={code}, schema={schema}")

        tqdm.write(f"正在生成 -> sn: {sn}, schema: {schema}")

        df = pd.DataFrame({
            "sn": SN,
            "schema": SCHEMA,
            "query参数": QUERY,
            "code": CODE,
            "类型": ENV
        })

    df.to_excel(excelFile, index=False)
    print(f"Excel 文件已生成: {excelFile}")