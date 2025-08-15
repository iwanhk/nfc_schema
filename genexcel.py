
import pandas as pd
import numpy as np
import sys
import os
from tqdm import tqdm  # pip install tqdm
from dotenv import load_dotenv, set_key
from WechatNFCSchemeGenerator import WechatNFCSchemeGenerator

# 使用示例
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python genExcel.py <NUMBER> <EXCEL_FILE> <ENV_VERSION>")
        sys.exit(1)
    
    load_dotenv()  # 读取 .env 文件
    generator = WechatNFCSchemeGenerator()
    
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
        code = generator.random_code(6)
        schema = generator.generate_nfc_scheme(sn, code, env_version)  # 可以根据需要修改为 "trial" 或 "develop"
        if schema:
            # 更新 .env 文件中的 LAST_MAX_COLUMNS
            set_key(".env", "LAST_MAX_COLUMNS", str(sn+1))
            SN.append(sn)
            SCHEMA.append(schema)
            QUERY.append(f"contentId=1&tenantId=1&id=1&code={code}")
            CODE.append(code)
            ENV.append(env_version)
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