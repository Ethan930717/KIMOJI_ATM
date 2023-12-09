from selenium import webdriver
import time

def get_youtube_cookies():
    # 指定 Chrome WebDriver 的路径
    driver_path = '/path/to/chromedriver'

    # 初始化 WebDriver
    driver = webdriver.Chrome(driver_path)

    # 访问 YouTube
    driver.get('https://www.youtube.com')

    # 等待页面加载（根据需要调整时间）
    time.sleep(5)

    # 获取 cookies
    cookies = driver.get_cookies()

    # 关闭浏览器
    driver.quit()

    # 将 cookies 保存到 Netscape 格式的文件
    with open('youtube_cookies.txt', 'w') as file:
        for cookie in cookies:
            file.write(f"{cookie['domain']}\tTrue\t{cookie['path']}\tFalse\t{cookie['expiry']}\t{cookie['name']}\t{cookie['value']}\n")

    print("Cookies saved to youtube_cookies.txt")

# 获取并保存 YouTube cookies
get_youtube_cookies()
