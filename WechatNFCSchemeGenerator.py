import requests
import json
import random
import string
import urllib.parse
import logging
from dotenv import load_dotenv, set_key
import os
import re

pattern = r'schema: ([^ ]+)'

class WechatNFCSchemeGenerator:
    def __init__(self):
        load_dotenv()  # 读取 .env 文件
        self.appid = os.getenv("APPID")
        self.appsecret = os.getenv("APPSECRET")
        self.model_id = "xt2ffIbFxRuHUZm0AUOoow"
        self.access_token = None
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

    def random_code(self, length=6):
        chars = string.ascii_letters + string.digits  # 大小写字母 + 数字
        return urllib.parse.quote(''.join(random.choices(chars, k=length)))
    
    def generate_nfc_scheme(self, sn=None, code="", env_version="release", path="/pages/index/index"):
        """生成NFC Scheme"""
        if not self.access_token:
            self._get_access_token()

        # 构造请求体（来自）
        payload = {
            "jump_wxa": {
                "path": path,
                "query": f"contentId=1&tenantId=1&id=1&code={code}",
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
                logging.info(f"env={env_version}, sn={sn}, code={code}, schema={result["openlink"]}")
                return result["openlink"]
            else:
                if result.get("errcode") == 9800010:
                    old_schema = re.findall(pattern, result['errmsg'])[0]
                    logging.info(f"env={env_version}, sn={sn}, code={code}, schema={old_schema}")
                    return old_schema
                logging.error(f"sn={sn} Error: {result['errmsg']}")
                raise Exception(f"接口返回错误: {result['errmsg']}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求异常: {str(e)}")
            