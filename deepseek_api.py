import time
import pandas as pd
import os
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(api_key="your api_key", base_url="https://api.deepseek.com")

# 加载 CSV 文件
csv_file_path = "新闻切割_4.csv"  # 替换为你的 CSV 文件路径
df = pd.read_csv(csv_file_path)

# 检查列名是否正确
expected_columns = ["title", "link", "content"]
for col in expected_columns:
    if col not in df.columns:
        raise ValueError(f"CSV文件中缺少必需的列: {col}")

# 检查并添加缺失的列
for col in ["粗颗粒分类", "细颗粒分类", "原因", "多分类"]:
    if col not in df.columns:
        df[col] = ""


# 提示词
PROMPT = """

"""
# 定义调用 DeepSeek-R1 的函数 (保持不变)
def analyze_news(title, content):
    """调用 DeepSeek API 分析新闻标题党类型"""
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": f"请分析以下新闻的标题党类型：\n标题：{title}\n内容：{content}"},
            ],
            stream=False
        )

        print("Raw Response:", response)  # 打印 API 响应（调试用）

        if not response or not response.choices:
            print(" API 返回空！")
            return "粗颗粒分类：未知\n细颗粒分类：未知\n原因：API 返回空\n多分类：未知"

        return response.choices[0].message.content

    except Exception as e:
        print(f" API 调用失败: {e}")
        time.sleep(5)  # API 失败时等待 5 秒再试
        return "粗颗粒分类：未知\n细颗粒分类：未知\n原因：API 调用异常\n多分类：未知"

# 输出 CSV 文件路径
output_csv_file_path = "情感1.csv"

# 如果文件不存在，先写入表头
if not os.path.exists(output_csv_file_path):
    df.to_csv(output_csv_file_path, index=False, mode="w", header=True, encoding="utf_8_sig")

# 遍历所有行数据
for index, row in df.iterrows():
    title = row["title"]  # 修改为 Title
    content = row["content"]  # 修改为 Content
    url = row["link"]  # 新增URL变量，虽然当前代码未使用

    print(f" 分析第 {index+1} 条新闻...")
    print(f" URL: {url}")  # 打印URL信息（可选）

    # 跳过空数据
    if pd.isna(title) or pd.isna(content):
        print(f" 第 {index+1} 条数据为空，跳过！")
        continue  

    # 限制 API 速率
    time.sleep(1)

    result = analyze_news(title, content)

    # 解析 API 结果
    try:
        lines = [line.strip() for line in result.split("\n") if line.strip()]
        result_dict = {}
        for line in lines:
            if "：" in line:
                key, value = line.split("：", 1)
                result_dict[key.strip()] = value.strip()
        
        coarse_grained = result_dict.get("粗颗粒分类", "未知")
        fine_grained = result_dict.get("细颗粒分类", "未知")
        reason = result_dict.get("原因", "未知")
        multi_class = result_dict.get("多分类", "未知")
        
    except Exception as e:
        print(f" 解析结果出错: {e}")
        coarse_grained, fine_grained, reason, multi_class = "未知", "未知", "解析出错", "未知"

    print(f" 标题: {title}")
    print(f" 粗颗粒分类: {coarse_grained}")
    print(f" 细颗粒分类: {fine_grained}")
    print(f" 原因: {reason}")
    print(f" 多分类: {multi_class}")
    print("------")

    # 更新 DataFrame
    df.at[index, "粗颗粒分类"] = coarse_grained
    df.at[index, "细颗粒分类"] = fine_grained
    df.at[index, "原因"] = reason
    df.at[index, "多分类"] = multi_class

    # 追加写入 CSV
    with open(output_csv_file_path, "a", encoding="utf_8_sig", newline="") as f:
        df.iloc[[index]].to_csv(f, index=False, mode="a", header=False)
        f.flush()

print(f"🎉 结果已保存到: {output_csv_file_path}")