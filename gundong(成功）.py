import time
import os
import requests
import csv
from multiprocessing import Pool
from bs4 import BeautifulSoup

# 初始化URL和请求头
init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page={}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
}

# 获取总页数
def get_total_pages():
    try:
        response = requests.get(init_url.format(1), headers=headers)
        response.encoding = 'utf-8'
        data = response.json()
        total_pages = data['result']['total'] // 50 + 1  # 每页50条，计算总页数
        return total_pages
    except Exception as e:
        print(f"获取总页数失败: {e}")
        return 1  # 如果失败，默认只爬取第一页

# 获取新闻URL列表
def get_news_urls(page_num):
    try:
        page = requests.get(url=init_url.format(page_num), headers=headers).json()
        urls = [page['result']['data'][j]['wapurl'] for j in range(len(page['result']['data']))]
        return urls
    except Exception as e:
        print(f"获取第 {page_num} 页新闻URL失败: {e}")
        return []

# 获取新闻标题和内容
def get_news_details(url):
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'  # 确保编码正确
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尝试从多个地方提取标题
        title = soup.find('h1', class_='main-title')  # 新浪新闻的标题通常在这里
        if not title:
            title = soup.find('title')  # 如果找不到，尝试从 <title> 标签提取
        if not title:
            title = soup.find('h1')  # 再尝试普通的 <h1> 标签
        title = title.text.strip() if title else 'No Title'  # 如果仍然找不到，使用默认值

        # 获取内容
        content = ''
        for p in soup.find_all('p'):
            content += p.text.strip() + '\n'

        return title, content, url  # 返回标题、内容和URL
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return 'No Title', 'No Content', url  # 如果出错，返回默认值

# 生成递增的文件名
def get_next_filename(base_name='news', extension='csv'):
    index = 1
    while True:
        filename = f"{base_name}_{index}.{extension}"
        if not os.path.exists(filename):
            return filename
        index += 1

# 写入CSV文件
def write_to_csv(data, filename):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Content', 'URL'])  # 写入表头
        writer.writerows(data)  # 写入数据

# 主函数
def main():
    # 获取总页数
    total_pages = get_total_pages()
    print(f"总页数: {total_pages}")

    for page_num in range(1, total_pages + 1):
        news_data = []
        print(f"正在爬取第 {page_num} 页...")

        # 获取新闻URL
        urls = get_news_urls(page_num)
        if not urls:
            print(f"第 {page_num} 页没有数据，跳过。")
            continue

        # 使用多进程获取新闻详情
        with Pool(processes=4) as pool:  # 使用4个进程
            news_details = pool.map(get_news_details, urls)

        # 将结果添加到news_data中
        news_data.extend(news_details)

        # 生成递增的文件名
        filename = get_next_filename()

        # 写入CSV文件
        write_to_csv(news_data, filename)
        print(f"第 {page_num} 页数据已成功写入文件：{filename}")

        # 添加延迟，避免请求过于频繁
        time.sleep(2)

    print("所有页数已爬取完毕。")

if __name__ == '__main__':
    main()