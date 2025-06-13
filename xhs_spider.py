import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import os
import re
from urllib.parse import urlparse
import uuid

# 运行时输入关键词和条数
def get_user_input():
    keyword = input("请输入要搜索的城市/关键词：")
    num_notes = int(input("请输入要爬取的笔记条数："))
    return keyword, num_notes

# 登录小红书（手动扫码）
def login_xiaohongshu(driver):
    driver.get("https://www.xiaohongshu.com/explore")
    print("请在弹出的浏览器窗口中手动扫码登录小红书，登录完成后按回车继续...")
    input()

# 搜索并爬取笔记
def crawl_notes(driver, keyword, num_notes):
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
    driver.get(search_url)
    time.sleep(3)

    # 保存页面源码，方便定位真实class
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("已保存页面源码到 page.html，请用文本编辑器打开，查找每条笔记的外层class名称，告诉我。")

    notes = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while len(notes) < num_notes:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)
        cards = driver.find_elements(By.XPATH, '//section[contains(@class, "note-item")]')
        for card in cards:
            try:
                link_elem = card.find_element(By.XPATH, './/a[contains(@class, "cover mask ld")]')
                note_url = link_elem.get_attribute('href')
                if not note_url.startswith('http'):
                    note_url = 'https://www.xiaohongshu.com' + note_url
            except:
                continue
            driver.execute_script("window.open(arguments[0]);", note_url)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)
            # 提取内容
            try:
                content_elem = driver.find_element(By.XPATH, '//div[contains(@class, "note-content")]')
                full_content = content_elem.text
            except:
                try:
                    content_elem = driver.find_element(By.XPATH, '//span[contains(@class, "note-text")]')
                    full_content = content_elem.text
                except:
                    full_content = ''
            # 获取所有大图，防止死循环
            img_urls = []
            img_url_set = set()
            while True:
                imgs = driver.find_elements(By.XPATH, '//div[contains(@class, "img-container")]/img')
                new_img_found = False
                for img in imgs:
                    src = img.get_attribute('src')
                    if src and src not in img_url_set:
                        img_urls.append(src)
                        img_url_set.add(src)
                        new_img_found = True
                # 尝试点击右箭头
                try:
                    next_btn = driver.find_element(By.XPATH, '//div[contains(@class, "right-arrow") or contains(@class, "next")]')
                    if next_btn.is_displayed() and next_btn.is_enabled() and new_img_found:
                        next_btn.click()
                        time.sleep(1)
                    else:
                        break
                except:
                    break
            img_urls = list(img_url_set)
            # 下载图片到本地
            note_uuid = str(uuid.uuid4())
            def download_images(img_urls, save_dir, prefix, note_uuid):
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                prefix = re.sub(r'[\\/:*?"<>|]', '', prefix)[:5]
                now_str = time.strftime('%Y%m%d%H%M%S')
                for idx, url in enumerate(img_urls):
                    filename = f'{prefix}{now_str}_{note_uuid}_{idx+1}.png'
                    filepath = os.path.join(save_dir, filename)
                    print(f'准备保存图片到: {filepath}')
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        resp = requests.get(url, headers=headers, timeout=10)
                        with open(filepath, 'wb') as f:
                            f.write(resp.content)
                    except Exception as e:
                        print(f'下载失败: {url}，原因: {e}')
            # 用标题做前缀，若标题为空用note序号
            def safe_filename(s):
                s = re.sub(r'[\\/:*?"<>|]', '', s)
                s = re.sub(r'\s+', '_', s)
                return s if s else 'note'
            try:
                title_elem = driver.find_element(By.XPATH, '//div[contains(@class, "title")]')
                title = title_elem.text.strip()
                prefix = safe_filename(title)
                if not prefix:
                    prefix = f'note{len(notes)+1}'
            except:
                title = ''
                prefix = f'note{len(notes)+1}'
            download_images(img_urls, 'images', prefix, note_uuid)
            # 提取作者
            try:
                author_elem = driver.find_element(By.XPATH, '//a[contains(@class, "user-info")]')
                author = author_elem.text
            except:
                author = ''
            # 提取点赞数
            try:
                like_elem = driver.find_element(By.XPATH, '//span[contains(@class, "engage-like-count")]')
                like = like_elem.text
            except:
                like = ''
            note = {
                '唯一ID': note_uuid,
                '标题': title,
                '作者': author,
                '内容': full_content,
                '图片链接': ','.join(img_urls),
                '点赞数': like,
                '链接': note_url
            }
            notes.append(note)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            if len(notes) >= num_notes:
                break
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return notes[:num_notes]

def main():
    keyword, num_notes = get_user_input()
    # 启动浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        login_xiaohongshu(driver)
        notes = crawl_notes(driver, keyword, num_notes)
        df = pd.DataFrame(notes)
        df.to_excel(f"{keyword}_小红书旅游笔记.xlsx", index=False)
        print(f"已保存 {len(notes)} 条笔记到 {keyword}_小红书旅游笔记.xlsx")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 