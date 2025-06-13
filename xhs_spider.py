import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

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
        # 滚动加载更多内容
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)
        # 获取所有笔记卡片
        cards = driver.find_elements(By.XPATH, '//section[contains(@class, "note-item")]')
        for card in cards:
            print('卡片内容:', card.text.replace('\n', ' | '))  # 打印卡片文本内容
            # 下面字段提取暂时注释掉，后续根据实际结构调整
            # try:
            #     title = card.find_element(By.XPATH, './/div[contains(@class, "title")]').text
            # except:
            #     title = ''
            # try:
            #     author = card.find_element(By.XPATH, './/div[contains(@class, "author")]').text
            # except:
            #     author = ''
            # try:
            #     date = card.find_element(By.XPATH, './/div[contains(@class, "date")]').text
            # except:
            #     date = ''
            # try:
            #     desc = card.find_element(By.XPATH, './/div[contains(@class, "desc")]').text
            # except:
            #     desc = ''
            # try:
            #     like = card.find_element(By.XPATH, './/span[contains(@class, "like")]').text
            # except:
            #     like = ''
            # note = {
            #     '标题': title,
            #     '作者': author,
            #     '日期': date,
            #     '内容': desc,
            #     '点赞数': like
            # }
            # if note not in notes:
            #     notes.append(note)
            # if len(notes) >= num_notes:
            #     break
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 没有更多内容
        last_height = new_height
    # 暂时返回空
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