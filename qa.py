from docx import Document
import pandas as pd
import re
import sys

# 输入文件路径
input_docx = "input.docx"
output_excel = "qa_output.xlsx"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python qa.py <input_docx> <output_excel>")
        sys.exit(1)


    # 输入文件路径
    input_docx = sys.argv[1]
    output_excel = sys.argv[2]
    # 读取docx文件
    doc = Document(input_docx)

    qa_list = []
    current_question = None
    current_answer = []

    # 匹配 1.  /  1、  /  1)  等数字开头
    question_pattern = re.compile(r"^\s*(\d+)[\.\)、]?\s*(.+)")
    # 记录前两个段落是否都是空行
    prev_empty_count = 0

    for para in doc.paragraphs:
        text = para.text.strip()

        # 是否是符合条件的问题段落
        is_question = bool(question_pattern.match(text)) and prev_empty_count >= 2

        if is_question:
            # 保存上一个问答
            if current_question is not None:
                qa_list.append({
                    "问题": current_question,
                    "答案": "\n".join(current_answer).strip()
                })
                current_answer = []

            # 设置当前问题
            current_question = question_pattern.match(text).group(2).strip()
            prev_empty_count = 0
        else:
            if current_question is not None:
                current_answer.append(text)  # 答案包含空行也记录

            # 空行计数
            if text == "":
                prev_empty_count += 1
            else:
                prev_empty_count = 0

    # 最后一个问答
    if current_question is not None:
        qa_list.append({
            "问题": current_question,
            "答案": "\n".join(current_answer).strip()
        })
    # 保存为Excel
    df = pd.DataFrame(qa_list)
    df.to_excel(output_excel, index=False)

    print(f"已保存问答表格到 {output_excel}")