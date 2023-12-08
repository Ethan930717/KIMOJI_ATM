import subprocess
import urllib.parse
import os
import re
import requests


# 发送通知函数
def send_notification(site, video_title):
    server_url = "https://sctapi.ftqq.com/SCT149255TZvd5PvMXbLkYuPd0dGvSKefr.send"
    message = f"{site} {video_title} 下载完毕"
    requests.post(server_url, data={"title": "下载通知", "desp": message})


# URL 编码函数
def urlencode(str):
    return urllib.parse.quote(str, safe='')


# 从文件中读取链接并过滤特定平台的链接
def read_links_from_file(platform_pattern):
    with open("/home/videourl.txt", "r") as file:
        links = file.readlines()
    return [link.strip() for link in links if re.search(platform_pattern, link)]


# 删除已下载的链接
def remove_downloaded_link(downloaded_link):
    with open("videourl.txt", "r") as file:
        links = file.readlines()
    links.remove(downloaded_link + "\n")
    with open("videourl.txt", "w") as file:
        file.writelines(links)


# 通用下载函数
def download_video(video_url, cookies_path, proxy=None):
    # 获取视频标题
    yt_dlp_command = ["yt-dlp", "--get-title", "--cookies", cookies_path, video_url]
    if proxy:
        yt_dlp_command.extend(["--proxy", proxy])
    video_title = subprocess.check_output(yt_dlp_command).decode().split('\n')[0]

    # 尝试提取书名号中的内容
    book_title_search = re.search(r'《([^《》]*)》', video_title)
    book_title = book_title_search.group(1) if book_title_search else None

    # 输出文件夹
    output_folder = "/home/media"
    if book_title:
        output_folder = f"{output_folder}/{book_title}"
    else:
        series_id_search = re.search(r'ss\d+', video_url)
        series_id = series_id_search.group() if series_id_search else "unknown"
        output_folder = f"{output_folder}/{series_id}"

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 下载命令
    download_command = ["yt-dlp", "-f", "bestvideo+bestaudio", "-o",
                        f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path, video_url]
    if proxy:
        download_command.extend(["--proxy", proxy])

    subprocess.run(download_command)

    # 发送下载完成通知
    send_notification("下载完成", video_title)


# 用户选择下载平台
platform_choice = input("请选择下载平台：\n1 - YouTube\n2 - Bilibili\n3 - Youku\n4 - IQIYI\n选择 1, 2, 3 或 4: ")

# 根据用户选择下载视频
platform_patterns = {
    '1': r'youtube\.com|youtubekids\.com|youtu\.be',
    '2': r'bilibili\.com',
    '3': r'youku\.com',
    '4': r'iqiyi\.com'
}

cookies_paths = {
    '1': "/home/cookies/youtubecookies.txt",
    '2': "/home/cookies/bilicookies.txt",
    '3': "/home/cookies/youkucookies.txt",
    '4': "/home/cookies/qiyicookies.txt"
}

if platform_choice in platform_patterns:
    pattern = platform_patterns[platform_choice]
    proxy = "socks5://dahu.fun:20190" if platform_choice in ['2', '3', '4'] else None
    cookies_path = cookies_paths[platform_choice]
    links = read_links_from_file(pattern)

    for link in links:
        download_video(link, cookies_path, proxy)
        remove_downloaded_link(link)
else:
    print("无效的选项。请输入 1, 2, 3 或 4。")
