import re
import os, sys
import pandas as pd
from tqdm import tqdm  # pip install tqdm
from dotenv import load_dotenv, set_key
from WechatNFCSchemeGenerator import WechatNFCSchemeGenerator

def extract_sn_from_logs(log_file_path):
    sn_list = []
    pattern = re.compile(r'ERROR - sn=(\d+) gen schema error')
    
    with open(log_file_path, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                sn_list.append(match.group(1))
    
    return sn_list

if __name__ == "__main__":
    if len(sys.argv)<3:
        print("Usage: python checkError.py <LOG_FILE> <EXCEL_FILE> <ENV_VERSION>")
        sys.exit(1)

    log_file_path = sys.argv[1]
    excelFile= sys.argv[2]
    if len(sys.argv) > 3:
        env_version = sys.argv[3]
    else:
        env_version = "release"  # 默认使用 release 版本

    sn_numbers = extract_sn_from_logs(log_file_path)
    if len(sn_numbers) == 0:
        print("没有找到错误日志中的 SN 号")
        sys.exit(0)
    print(sn_numbers)

    SN=[]
    SCHEMA=[]
    QUERY=[]
    CODE=[]
    ENV=[]

    generator = WechatNFCSchemeGenerator()

    print(f"共找到 {len(sn_numbers)} 个 SN 号")
    for sn in tqdm(sn_numbers, desc="生成数据", unit="个"):
        code = generator.random_code(6)
        schema = generator.generate_nfc_scheme(sn, code, env_version)  # 可以根据需要修改为 "trial" 或 "develop"
        if schema:
            # 更新 .env 文件中的 LAST_MAX_COLUMNS
            set_key(".env", "LAST_MAX_COLUMNS", sn)
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