import requests
import json
import pandas as pd
import numpy as np

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

    def generate_nfc_scheme(self, path="/pages/index/index", env_version="release", sn=None):
        """生成NFC Scheme"""
        if not self.access_token:
            self._get_access_token()

        # 构造请求体（来自）
        payload = {
            "jump_wxa": {
                "path": path,
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

# 使用示例
if __name__ == "__main__":
    # 初始化配置（替换为实际参数）
    # 钛文创
    APPID = "wx97376bdd89b0c344"
    APPSECRET = "9fdebc8b0ae84cd125af9624aded94b6"
    # MODEL_ID = "-UESYamd8dP0Phl5NAGh6w"
    MODEL_ID = "xt2ffIbFxRuHUZm0AUOoow"

    # 敦煌
    # APPID = "wx7ff39089532d58ed"
    # APPSECRET = "d587bcf89e0134df35f08ca1967e5e4f"
    # MODEL_ID = "UESYamd8dP0Phl5NAGh6w"
    
    generator = WechatNFCSchemeGenerator(APPID, APPSECRET, MODEL_ID)
    try:
        scheme_url = generator.generate_nfc_scheme(
            path="/pages/index/index",     # 小程序首页路径
            env_version="release",       # 必须为已发布的线上版本（来自）
            sn= "03"          # 可选设备序列号（某些硬件场景需要）
        )
        print("生成的NFC Scheme:", scheme_url)
    except Exception as e:
        print("生成失败:", str(e))
