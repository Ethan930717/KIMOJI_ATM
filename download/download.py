import subprocess
import urllib.parse
import os
import re
import requests

# URL 编码函数
def urlencode(str):
    return urllib.parse.quote(str, safe='')

# 用于发送下载完成通知的函数
def send_notification(video_title):
    server_url = "https://sctapi.ftqq.com/SCT149255TZvd5PvMXbLkYuPd0dGvSKefr.send"
    message = f"视频 {video_title} 已下载完成"
    requests.post(server_url, data={"title": "下载通知", "desp": message})

# 用于下载视频并移动文件夹的函数
def download_and_move(video_url, platform, cookies_path, proxy=None):
    # 获取视频标题
    yt_dlp_command = ["yt-dlp", "--get-title", "--cookies", cookies_path, video_url]
    if proxy:
        yt_dlp_command.extend(["--proxy", proxy])
    video_title = subprocess.check_output(yt_dlp_command).decode().strip()

    # 尝试提取书名号中的内容
    book_title_search = re.search(r'《([^《》]*)》', video_title)
    book_title = book_title_search.group(1) if book_title_search else None

    # 确定输出文件夹
    output_folder = "/home/media/" + (book_title or platform)
    os.makedirs(output_folder, exist_ok=True)

    # 下载视频
    download_command = ["yt-dlp", "-f", "bestvideo+bestaudio", "-o",
                        f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path, video_url]
    if proxy:
        download_command.extend(["--proxy", proxy])
    subprocess.run(download_command)

    # 发送下载完成通知
    send_notification(video_title)

    # 移动文件夹
    encoded_folder = "/home/encoded/" + (book_title or platform)
    os.rename(output_folder, encoded_folder)

# 主程序
platform_patterns = {
    '1': r'youtube\.com|youtubekids\.com|youtu\.be',
    '2': r'bilibili\.com',
    '3': r'youku\.com',
    '4': r'iqiyi\.com'
}

platform_cookies = {
    '1': "/home/cookies/youtubecookies.txt",
    '2': "/home/cookies/bilicookies.txt",
    '3': "/home/cookies/youkucookies.txt",
    '4': "/home/cookies/qiyicookies.txt"
}

platform_proxy = {
    '2': "socks5://dahu.fun:20190",  # 仅对 Bilibili 和 Youku 使用代理
    '3': "socks5://dahu.fun:20190"
}

# 读取视频 URL 列表
with open('/home/videourl.txt', 'r') as file:
    lines = file.readlines()

# 用户选择下载平台
platform_choice = input("请选择下载平台：\n1 - YouTube\n2 - Bilibili\n3 - Youku\n4 - IQIYI\n选择 1, 2, 3 或 4: ")

# 过滤出对应平台的 URL
pattern = platform_patterns.get(platform_choice, '')
filtered_urls = [line.strip() for line in lines if re.search(pattern, line)]

# 下载过滤出的视频
for video_url in filtered_urls:
    download_and_move(video_url, platform_choice, platform_cookies[platform_choice], platform_proxy.get(platform_choice))

    # 更新 videourl.txt 文件
    with open('videourl.txt', 'w') as file:
        file.writelines([line for line in lines if line.strip() != video_url])
