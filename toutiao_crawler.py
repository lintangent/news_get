import requests
from bs4 import BeautifulSoup
import csv
import time
import os

# url
url = 'https://www.toutiao.com/'

# headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'Cookie': 'id=verify_m71d8a57_lHm0q7Mj_HlLw_4rSc_ApAB_EIpHqDNzHwjU; passport_csrf_token=d02e9c40ea727ca727fdab106e38ad26; passport_csrf_token_default=d02e9c40ea727ca727fdab106e38ad26; passport_mfa_token=CjdthMToCQRqD8OmPmkqtkekoOvK1kR7jLclaI5hjSD9%2BY7g7B2inGw8vOI1QF88RSF2G929oj1PGkoKPDRxSCavT%2BhJ99EmFL3vzb%2FuIrXQaihnLD6LBr26xy0kXa%2FqrWC677LH8Uw%2FwsDkF4CJwhuxPPAs1RyzNxD0qekNGPax0WwgAiIBA7i4K%2FE%3D; d_ticket=9f3148c49b193f44e1b55d43016dea4aa4389; n_mh=_tz1_F6kjPIMud2oAyubvMgfxjg8V9hXd5aVWxaAsAE; sso_auth_status=1e9b3fe54f4d34feb77acb270057beb2; sso_auth_status_ss=1e9b3fe54f4d34feb77acb270057beb2; sso_uid_tt=c3008b03b9e3a1999642b0229de8ecdb; sso_uid_tt_ss=c3008b03b9e3a1999642b0229de8ecdb; toutiao_sso_user=e9b683bb8d203329166dc343200f703c; toutiao_sso_user_ss=e9b683bb8d203329166dc343200f703c; sid_ucp_sso_v1=1.0.0-KGQ0ZDIxZDk3ZWFhNzk1YzM1MjcyY2M5OGU2M2JhNjg0MjYyNWU2ODcKHgit-_CpvY2YBhD9trC9BhgYIAwwy6z1hQY4AkDxBxoCaGwiIGU5YjY4M2JiOGQyMDMzMjkxNjZkYzM0MzIwMGY3MDNj; ssid_ucp_sso_v1=1.0.0-KGQ0ZDIxZDk3ZWFhNzk1YzM1MjcyY2M5OGU2M2JhNjg0MjYyNWU2ODcKHgit-_CpvY2YBhD9trC9BhgYIAwwy6z1hQY4AkDxBxoCaGwiIGU5YjY4M2JiOGQyMDMzMjkxNjZkYzM0MzIwMGY3MDNj; passport_auth_status=4fda5515f21724298a2c440d7a6e5e63%2C402f1285cdc35039feeb2e51cc94e189; passport_auth_status_ss=4fda5515f21724298a2c440d7a6e5e63%2C402f1285cdc35039feeb2e51cc94e189; sid_guard=d35b24c9bf7bf79cd7c2d6eb24e6647c%7C1739332478%7C5184001%7CSun%2C+13-Apr-2025+03%3A54%3A39+GMT; uid_tt=b6e4a7fe569f6a60d251a1ce0c409eb4; uid_tt_ss=b6e4a7fe569f6a60d251a1ce0c409eb4; sid_tt=d35b24c9bf7bf79cd7c2d6eb24e6647c; sessionid=d35b24c9bf7bf79cd7c2d6eb24e6647c; sessionid_ss=d35b24c9bf7bf79cd7c2d6eb24e6647c; is_staff_user=false; sid_ucp_v1=1.0.0-KDVhMDU3MDY3ZGNkNWQzNjgwNDI1YWNjOTIxYjQ3MDNjZTdlNzZhYWQKGAit-_CpvY2YBhD-trC9BhgYIAw4AkDxBxoCbHEiIGQzNWIyNGM5YmY3YmY3OWNkN2MyZDZlYjI0ZTY2NDdj; ssid_ucp_v1=1.0.0-KDVhMDU3MDY3ZGNkNWQzNjgwNDI1YWNjOTIxYjQ3MDNjZTdlNzZhYWQKGAit-_CpvY2YBhD-trC9BhgYIAw4AkDxBxoCbHEiIGQzNWIyNGM5YmY3YmY3OWNkN2MyZDZlYjI0ZTY2NDdj; store-region=cn-gd; store-region-src=uid; odin_tt=c994ae7168579ab6f36f0870d178081b935cd6bf0f57409af964879039cc6fef7adb230ac0ef2d7341040d2f5743e353; ttwid=1%7C1SdLX4d9UsuQTZMZG4J0YpwayW0qJp83Lt4L4e6EpW8%7C1739421688%7C2dc60bffdd4bb61ad3d8a4a2b938987d8d9763c2f29a0b1e28d3d988a7acbd66; tt_anti_token=6X4t9mYCKEIGZ-225a1c743e4d589f42665864897a15306c704a2bc51c7e6ded537f91989bd3d6; tt_scid=tsb-0P',
}

# serve list
all_news_data = []
target_count = 500  # the nums of the news
filename = "新闻1.csv"  # output file_name

# initialize the csv file and write in the headers
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["title", "link", "content"])
    writer.writeheader()

# Start
while len(all_news_data) < target_count:
    try:
        print(f"已收集 {len(all_news_data)} 条新闻，目标 {target_count} 条")

        # send request and get the content
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # extract all the news title and url
        articles = soup.find_all('a', class_='title')  # Adjust the selector based on the actual page structure

        # if not
        if not articles:
            print("未找到文章，可能是页面结构变化或请求失败")
            time.sleep(10)
            continue

        # go through every artile
        for article in articles:
            if len(all_news_data) >= target_count:
                break

            try:
                title = article.get_text().strip()
                link = article['href']

                # make sure the completement of the link
                if not link.startswith('http'):
                    link = 'https://www.toutiao.com' + link

                print(f"正在处理: {title}")

                # get the detail of the content
                article_response = requests.get(link, headers=headers, timeout=10)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')


                content_div = article_soup.find('div', class_='article-content') or \
                              article_soup.find('div', class_='content') or \
                              article_soup.find('article')

                content_text = content_div.get_text().strip() if content_div else "无内容"

                # add to the list
                all_news_data.append({
                    'title': title,
                    'link': link,
                    'content': content_text
                })

                # save per 10 news
                if len(all_news_data) % 10 == 0:
                    with open(filename, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=["title", "link", "content"])
                        writer.writerows(all_news_data[-10:])
                    print(f"已保存 {len(all_news_data)} 条新闻到 {filename}")

            except Exception as e:
                print(f"处理文章时出错: {e}")
                continue

        # sleep
        time.sleep(5)

    except Exception as e:
        print(f"主循环出错: {e}")
        time.sleep(30)
        continue

# final
with open(filename, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["title", "link", "content"])
    # 只写入尚未写入的数据
    writer.writerows(all_news_data[len(all_news_data) - (len(all_news_data) % 10):])

print(f"已完成！共爬取 {len(all_news_data)} 条新闻，已保存到 {filename}")