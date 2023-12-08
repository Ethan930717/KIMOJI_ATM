import subprocess
import urllib.parse
import os
import re
import requests

def send_notification(site, video_title):
    # 这里替换成您的Server酱的URL和密钥
    server_url = "https://sctapi.ftqq.com/SCT149255TZvd5PvMXbLkYuPd0dGvSKefr.send"
    message = f"{site} {video_title} 下载完毕"
    requests.post(server_url, data={"title": "下载通知", "desp": message})
# URL 编码函数
def urlencode(str):
    return urllib.parse.quote(str, safe='')

# YouTube 下载函数
def download_youtube(video_url):
    output_folder = "/home/media"
    cookies_path = "/home/cookies/youtubecookies.txt"

    # 获取视频标题
    video_title = subprocess.check_output(
        ["yt-dlp", "--get-title", "--cookies", cookies_path, video_url]).decode().split('\n')[0]

    # 尝试提取书名号中的内容
    book_title_search = re.search(r'《([^《》]*)》', video_title)
    book_title = book_title_search.group(1) if book_title_search else None

    # 检查书名号是否存在
    if not book_title:
        series_id = re.search(r'ss\d+', video_url).group()
        output_folder = f"{output_folder}/{series_id}"
    else:
        output_folder = f"{output_folder}/{book_title}"

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 使用 yt-dlp 下载视频到对应的文件夹
    subprocess.run(["yt-dlp", "-f", "bestvideo+bestaudio", "-o",
                    f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path, video_url])


# Bilibili 下载函数
def download_bilibili(video_url):
    output_folder = "/home/media"
    cookies_path = "/home/cookies/bilicookies.txt"
    proxy = "socks5://dahu.fun:20190"

    # 获取视频标题
    video_title = subprocess.check_output(
        ["yt-dlp", "--get-title", "--cookies", cookies_path, "--proxy", proxy, video_url]).decode().split('\n')[0]

    # 对视频标题进行 URL 编码
    encoded_video_title = urlencode(video_title)

    # 使用播放列表 ID 或视频标题作为文件夹名称
    series_id_search = re.search(r'ss\d+', video_url)
    if series_id_search:
        output_folder = f"{output_folder}/{series_id_search.group()}"
    else:
        output_folder = f"{output_folder}/{encoded_video_title}"

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 使用 yt-dlp 下载视频到对应的文件夹
    subprocess.run(["yt-dlp", "-f", "bestvideo+bestaudio", "-o",
                    f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path, "--proxy", proxy, video_url])


# Youku 下载函数
def download_youku(video_url):
    output_folder = "/home/media"
    cookies_path = "/home/cookies/youkucookies.txt"
    proxy = "socks5://dahu.fun:20190"

    # 获取视频标题
    video_title = subprocess.check_output(
        ["yt-dlp", "--get-title", "--cookies", cookies_path, "--proxy", proxy, video_url]).decode().split('\n')[0]

    # 尝试提取书名号中的内容
    book_title_search = re.search(r'《([^《》]*)》', video_title)
    book_title = book_title_search.group(1) if book_title_search else None

    # 检查书名号是否存在
    if not book_title:
        series_id = re.search(r'ss\d+', video_url).group()
        output_folder = f"{output_folder}/{series_id}"
    else:
        output_folder = f"{output_folder}/{book_title}"

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 使用 yt-dlp 下载视频到对应的文件夹
    subprocess.run(["yt-dlp", "-f", "bestvideo+bestaudio", "-o",
                    f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path, "--proxy", proxy, video_url])

# IQIYI 下载函数
def download_iqiyi(video_url):
    output_folder = "/home/media"
    cookies_path = "/home/cookies/qiyicookies.txt"

    # 创建一个以系列 ID 命名的文件夹
    series_id = re.search(r'ss\d+', video_url).group()
    output_folder = f"{output_folder}/{series_id}"
    os.makedirs(output_folder, exist_ok=True)

    # 使用 yt-dlp 下载视频到对应的文件夹
    subprocess.run(["yt-dlp", "-f", "bestvideo+bestaudio", "-o",
                    f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path, video_url])


# 用户选择下载平台
platform_choice = input("请选择下载平台：\n1 - YouTube\n2 - Bilibili\n3 - Youku\n4 - IQIYI\n选择 1, 2, 3 或 4: ")

# 根据用户选择下载视频
if platform_choice == '1':
    download_youtube("这里填入YouTube的视频链接")
elif platform_choice == '2':
    download_bilibili("这里填入Bilibili的视频链接")
elif platform_choice == '3':
    download_youku("这里填入Youku的视频链接")
elif platform_choice == '4':
    download_iqiyi("这里填入IQIYI的视频链接")
else:
    print("无效的选项。请输入 1, 2, 3 或 4。")


