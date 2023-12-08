import subprocess
import urllib.parse
import os
import re
import requests
import traceback

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
    try:
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
        download_command = ["yt-dlp", "-f", "bestvideo+bestaudio[ext=webm]/bestaudio", "--ignore-errors", "-o",
                            f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path,
                            video_url]
        if proxy:
            download_command.extend(["--proxy", proxy])
        subprocess.run(download_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 发送下载完成通知
        send_notification(video_title)

        # 移动文件夹
        encoded_folder = "/home/encoded/" + (book_title or platform)
        os.rename(output_folder, encoded_folder)
        return True
    except subprocess.CalledProcessError as e:
        print(f"下载错误: {e.returncode}")
        if e.output:
            print("错误输出：", e.output.decode())
        if e.stderr:
            print("标准错误输出：", e.stderr.decode())
        error_output = e.stderr.decode() if e.stderr else ''
        print(" ".join(e.cmd))
        # 检查是否是地理位置限制错误
        if "geo restriction" in error_output():
            print("检测到地理位置限制，尝试使用代理重新下载...")
            proxy = "socks5://dahu.fun:20190"
            try:
                download_command = ["yt-dlp", "-f", "bestvideo+bestaudio[ext=webm]/bestaudio", "--ignore-errors", "-o",
                                    f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path,
                                    "--proxy", proxy, video_url]
                subprocess.run(download_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True
            except subprocess.CalledProcessError as e_proxy:
                print("使用代理下载也失败了。")
                return False
        else:
            return False
        choice = input("是否查看可用格式并手动选择下载？(y/n): ")
        if choice.lower() == 'y':
            try:
                list_formats(video_url, cookies_path, proxy)
                format_id = input("请输入要下载的视频格式编码: ")

                # 在这里确保 output_folder 已经定义
                output_folder = "/home/media/" + (book_title or platform)
                os.makedirs(output_folder, exist_ok=True)

                download_command = ["yt-dlp", "-f", f"{format_id}+bestaudio[ext=webm]/bestaudio", "--ignore-errors", "-o",
                                    f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies", cookies_path,
                                    video_url]
                if proxy:
                    download_command.extend(["--proxy", proxy])
                subprocess.run(download_command, check=True)
                send_notification(video_title)
                os.rename(output_folder, encoded_folder)
                return True

            except subprocess.CalledProcessError as e:
                print(f"下载错误: {e.returncode}")
                if e.output:
                    print("错误输出：", e.output.decode())
                if e.stderr:
                    print("标准错误输出：", e.stderr.decode())
                error_output = e.stderr.decode() if e.stderr else ''
                print("完整命令：")
                print(" ".join(e.cmd))
                if "geo restriction" in error_output():
                    print("检测到地理位置限制，尝试使用代理重新下载...")
                    proxy = "socks5://dahu.fun:20190"
                    try:
                        download_command = ["yt-dlp", "-f", "bestvideo+bestaudio[ext=webm]/bestaudio",
                                            "--ignore-errors", "-o",
                                            f"{output_folder}/%(title).20s.%(ext)s", "--embed-subs", "--cookies",
                                            cookies_path,
                                            "--proxy", proxy, video_url]
                        subprocess.run(download_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        return True
                    except subprocess.CalledProcessError as e_proxy:
                        print("使用代理下载也失败了。")
                        return False
                else:
                    return False
                print("脚本结束。")
                return False
    except Exception as e:
        print(f"发生未知错误: {e}")
        traceback.print_exc()  # 打印完整的堆栈跟踪
        return False
def list_formats(video_url, cookies_path, proxy=None):
    yt_dlp_command = ["yt-dlp", "--list-formats", "--cookies", cookies_path, video_url]
    if proxy:
        yt_dlp_command.extend(["--proxy", proxy])
    subprocess.run(yt_dlp_command)

# 主程序
platform_patterns = {
    '1': r'youtube\.com|youtubekids\.com|youtu\.be',
    '2': r'bilibili\.com',
    '3': r'youku\.com',
    '4': r'iqiyi\.com',
    '5': r'mgtv\.com'
}

platform_cookies = {
    '1': "/home/cookies/youtubecookies.txt",
    '2': "/home/cookies/bilicookies.txt",
    '3': "/home/cookies/youkucookies.txt",
    '4': "/home/cookies/qiyicookies.txt",
    '5': "/home/cookies/mangocookies.txt"

}

platform_proxy = {
    '2': "socks5://dahu.fun:20190",  # 仅对 Bilibili 和 Youku 使用代理
    '3': "socks5://dahu.fun:20190",
    #'5': "socks5://dahu.fun:20190"

}

# 读取视频 URL 列表
with open('/home/videourl.txt', 'r') as file:
    lines = file.readlines()


# 用户选择下载平台
platform_choice = input("请选择下载平台或查看格式：\n0 - 查看格式\n1 - YouTube\n2 - Bilibili\n3 - Youku\n4 - IQIYI\n5 - Mango\n选择 0, 1, 2, 3, 4 或 5: ")

if platform_choice == '0':
    # 显示所有链接并编号
    for index, video_url in enumerate(lines, start=1):
        print(f"{index} - {video_url.strip()}")

    # 让用户选择一个编号
    index_choice = int(input("选择要查看格式的视频编号：")) - 1

    # 获取对应视频的URL
    selected_video_url = lines[index_choice].strip()

    # 获取平台信息
    for key, pattern in platform_patterns.items():
        if re.search(pattern, selected_video_url):
            selected_platform = key
            break

    # 调用yt-dlp的format-list功能
    list_formats(selected_video_url, platform_cookies[selected_platform], platform_proxy.get(selected_platform))
else:
    # 过滤出对应平台的 URL
    pattern = platform_patterns.get(platform_choice, '')
    filtered_urls = [line.strip() for line in lines if re.search(pattern, line)]

    # 下载过滤出的视频并更新文件
    successful_urls = []
    for video_url in filtered_urls:
        if download_and_move(video_url, platform_choice, platform_cookies[platform_choice],
                             platform_proxy.get(platform_choice)):
            successful_urls.append(video_url)

    # 仅更新成功下载的视频链接
    with open('/home/videourl.txt', 'w') as file:
        file.writelines([line for line in lines if line.strip() not in successful_urls])