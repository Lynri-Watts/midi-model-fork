import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
import random
import re  # 新增导入

# 新增依赖
from playwright.sync_api import sync_playwright

def crawl_urls_with_prefix(base_url, prefix):

    try:
        with sync_playwright() as p:
            # 启动浏览器并设置超时参数
            browser = p.chromium.launch(headless=True, timeout=60000)  # 总超时60秒
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # 增加页面加载超时时间并优化等待条件
            page.goto(base_url, wait_until="domcontentloaded", timeout=60000)  # 等待DOM加载
            time.sleep(1)

            # 分阶段滚动页面
            for _ in range(3):  # 分3次滚动到底部
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(100)  # 每次滚动后等待0.1秒
            
            # 获取渲染后的HTML
            html = page.content()
            
            browser.close()
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有<a>标签
        links = soup.find_all('a', href=True)
        
        # 收集符合前缀的URL
        # 查找所有可能包含URL的属性和标签
        url_patterns = [
            ('a', 'href'),
            ('link', 'href'),
            ('script', 'src'),
            ('img', 'src'),
            ('iframe', 'src'),
            ('div', 'data-href'),  # 常见数据属性
            ('button', 'onclick'),  # 解析JavaScript事件
            ('meta', 'content')     # Open Graph URL
        ]
        
        matched_urls = []
        for tag_name, attr in url_patterns:
            for element in soup.find_all(tag_name, {attr: True}):
                raw_url = element.get(attr)
                
                # 解析onclick事件中的URL
                if attr == 'onclick':
                    url_match = re.search(r"window\.open\(\'(.+?)\'", raw_url)
                    if url_match:
                        raw_url = url_match.group(1)
                
                # 解析meta标签的Open Graph URL
                elif tag_name == 'meta' and 'property' in element.attrs:
                    if element['property'] in ['og:url', 'og:image']:
                        absolute_url = urljoin(base_url, raw_url)
                
                if raw_url:
                    absolute_url = urljoin(base_url, raw_url)
                    if absolute_url.startswith(prefix):
                        matched_urls.append(absolute_url)
        
        # 去重处理
        matched_urls = list(set(matched_urls))
        
        # 打印结果
        
        return matched_urls  # 返回匹配的URL列表，方便后续处理或使用
                
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("访问被拒绝，请尝试：")
            print("1. 使用代理服务器")
            print("2. 更换User-Agent头")
            print("3. 增加请求间隔时间")
        else:
            print(f"HTTP错误: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"处理错误: {e}")

result = []
if __name__ == "__main__":
    for i in range(1, 101):  # 假设你想爬取1到100页的URL，根据需要调整范围
        print(f"正在爬取第 {i} 页...")
        # time.sleep(random.randint(1, 5))  # 随机等待1到5秒，避免被banne
        TARGET_URL = "https://musescore.com/sheetmusic/interactive?page=%d&sort=view_count" % (i)
        URL_PREFIX = "https://musescore.com/user/"
        
        matched_urls = crawl_urls_with_prefix(TARGET_URL, URL_PREFIX)
        # for url in matched_urls:
            # print(url)
        
        filtered_urls = [url for url in matched_urls if url.find("scores") != -1]
        print(f"找到 {len(filtered_urls)} 个匹配的URL")
        result = set(result) | set(filtered_urls)

    print(f"共找到 {len(result)} 个匹配的URL")
    with open("urls.txt", "w") as file:
        for url in result:
            file.write(url + "\n")