import time
import os
import requests
import csv
from multiprocessing import Pool
from bs4 import BeautifulSoup

# initialize URL and requesting heads
init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page={}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
}

# get the total page
def get_total_pages():
    try:
        response = requests.get(init_url.format(1), headers=headers)
        response.encoding = 'utf-8'
        data = response.json()
        total_pages = data['result']['total'] // 50 + 1
        return total_pages
    except Exception as e:
        print(f"获取总页数失败: {e}")
        return 1  # if failed，only get the first page

# the url lists
def get_news_urls(page_num):
    try:
        page = requests.get(url=init_url.format(page_num), headers=headers).json()
        urls = [page['result']['data'][j]['wapurl'] for j in range(len(page['result']['data']))]
        return urls
    except Exception as e:
        print(f"获取第 {page_num} 页新闻URL失败: {e}")
        return []

# news title and content
def get_news_details(url):
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # try different roots
        title = soup.find('h1', class_='main-title')
        if not title:
            title = soup.find('title')  # if not，try extract from <title> tap
        if not title:
            title = soup.find('h1')  #try again normal tap
        title = title.text.strip() if title else 'No Title'  # the condition that still failed

        # get the content
        content = ''
        for p in soup.find_all('p'):
            content += p.text.strip() + '\n'

        return title, content, url
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return 'No Title', 'No Content', url  # the condition that still failed

# generate the increasing name of the files
def get_next_filename(base_name='news', extension='csv'):
    index = 1
    while True:
        filename = f"{base_name}_{index}.{extension}"
        if not os.path.exists(filename):
            return filename
        index += 1

# write in the csv files
def write_to_csv(data, filename):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Content', 'URL'])  # write in the header
        writer.writerows(data)  # write in data

# main function
def main():

    total_pages = get_total_pages()
    print(f"总页数: {total_pages}")

    for page_num in range(1, total_pages + 1):
        news_data = []
        print(f"正在爬取第 {page_num} 页...")

        # get url
        urls = get_news_urls(page_num)
        if not urls:
            print(f"第 {page_num} 页没有数据，跳过。")
            continue

        # Use multiprocessing to obtain news details
        with Pool(processes=4) as pool:  # four processings
            news_details = pool.map(get_news_details, urls)

        # write in the outcome
        news_data.extend(news_details)


        filename = get_next_filename()


        write_to_csv(news_data, filename)
        print(f"第 {page_num} 页数据已成功写入文件：{filename}")

        # sleep
        time.sleep(2)

    print("所有页数已爬取完毕。")

if __name__ == '__main__':
    main()