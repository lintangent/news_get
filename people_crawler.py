import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urlparse

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

BASE_URL = 'http://finance.people.com.cn/GB/70846/index.html'


def get_page_content(url, retry=3):
    for i in range(retry):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # 人民日报主要使用GB18030编码
            if 'charset=gb' in response.text[:1000].lower():
                response.encoding = 'gb18030'
            else:
                response.encoding = response.apparent_encoding

            print(f"成功获取页面: {url}")
            return response.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"页面不存在: {url}")
                return None
            print(f"请求失败(尝试 {i + 1}/{retry}): {e}")
        except Exception as e:
            print(f"请求失败(尝试 {i + 1}/{retry}): {e}")

        if i < retry - 1:
            time.sleep(2)
    return None


def extract_real_article_links(url):
    """提取实际可访问的文章链接"""
    html = get_page_content(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    links = []

    # 人民日报经济频道实际可用的链接选择器
    selectors = [
        'ul.list_14.list_ej li a',  # 主列表
        'div.ej_list_box ul li a',  # 经济频道框
        'div.hdNews.clearfix ul li a',  # 头条新闻
        'a[href*="/n1/"]',  # 包含/n1/的链接
        'a[href*="/GB/"]'  # 包含/GB/的链接
    ]

    seen_links = set()
    for selector in selectors:
        for a in soup.select(selector):
            href = a.get('href', '').strip()
            if href and href not in seen_links:
                # 转换相对链接为绝对链接
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = 'http://finance.people.com.cn' + href
                    else:
                        href = f'http://finance.people.com.cn/GB/70846/{href}'

                # 验证链接格式
                if re.search(r'/n1/\d{4}/\d{4}/c\d+-\d+\.html$', href) or \
                        re.search(r'/GB/70846/\d+/\d+\.html$', href):
                    links.append(href)
                    seen_links.add(href)

    print(f"提取到 {len(links)} 个有效链接")
    return links


def extract_article_content(url):
    html = get_page_content(url)
    if not html:
        return None, None

    soup = BeautifulSoup(html, 'html.parser')

    # 标题提取 - 更全面的选择器
    title = '无标题'
    title_selectors = [
        'div.text_title h1',  # 新版标题
        'div.col.col-1.fl h1',  # 旧版标题
        'h1.article-title',  # 可能的标题类
        'h1',  # 最后尝试所有h1
        'div.article-header h1',  # 备用选择器
        'div.article-title h1'  # 另一个可能的标题位置
    ]

    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem and title_elem.text.strip():
            title = title_elem.text.strip()
            break

    # 内容提取 - 更全面的选择器
    content = '无内容'
    content_selectors = [
        'div.rm_txt_con',  # 新版内容区
        'div.box_con',  # 旧版内容区
        'div.article-content',  # 可能的内容区
        'div.article-body',  # 备用选择器
        'div#rwb_zw',  # 人民日报网内容区
        'div.article-text'  # 另一个可能的内容区
    ]

    for selector in content_selectors:
        content_div = soup.select_one(selector)
        if content_div:
            # 移除不需要的元素
            for elem in content_div.select('script, style, iframe, div.ad, div.comment'):
                elem.decompose()

            paragraphs = content_div.find_all(['p', 'div'])
            content = '\n'.join([p.get_text(' ', strip=True) for p in paragraphs if p.get_text(strip=True)])
            break

    # 如果内容太短可能是提取错误
    if len(content) < 50 and '无内容' not in content:
        content = '无内容'

    print(f"已提取文章: {title[:30]}...")
    return title, content


def save_to_csv(data, filename):
    with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def crawl_articles(target_count=30, filename="people_news.csv"):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["标题", "内容", "链接"])

    collected = 0
    page_num = 1
    consecutive_empty = 0  # 连续空页计数器

    while collected < target_count and consecutive_empty < 3:  # 最多允许3个连续空页
        page_url = f'http://finance.people.com.cn/GB/70846/index{page_num}.html' if page_num > 1 else BASE_URL
        print(f"\n正在处理第 {page_num} 页: {page_url}")

        article_links = extract_real_article_links(page_url)
        if not article_links:
            print(f"第 {page_num} 页没有找到有效链接")
            consecutive_empty += 1
            page_num += 1
            continue

        consecutive_empty = 0  # 重置计数器

        for link in article_links:
            if collected >= target_count:
                break

            title, content = extract_article_content(link)
            if title != '无标题' and content != '无内容':
                save_to_csv([title, content, link], filename)
                collected += 1
                print(f"已收集 {collected}/{target_count}: {title[:30]}...")

        page_num += 1
        time.sleep(2)  # 礼貌性延迟

    print(f"\n完成! 共收集 {collected} 条新闻")


if __name__ == '__main__':
    start_time = time.time()
    try:
        crawl_articles(target_count=1500)  # 先测试30条
    except Exception as e:
        print(f"爬取过程中出错: {e}")
    finally:
        print(f"总耗时: {(time.time() - start_time) / 60:.2f} 分钟")