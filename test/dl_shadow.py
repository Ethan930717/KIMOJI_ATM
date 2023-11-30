import requests
from requests.exceptions import RequestException
import os
from time import sleep

# 设置下载链接的基本部分和Cookie
BASE_URL = "https://star-space.net/download.php"
COOKIES = {
    "c_secure_uid": "MTAxMDE%3D",
    "c_secure_pass": "c6d9cbc34bff5b2b31f8807861b0bd0a",
    "c_secure_ssl": "eWVhaA%3D%3D",
    "c_secure_tracker_ssl": "eWVhaA%3D%3D",
    "c_secure_login": "bm9wZQ%3D%3D"
}

# 设置下载文件的保存目录
SAVE_DIR = "/mnt/user/unraid/torrents/影"

# 确保保存目录存在
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 设置日志文件路径
LOG_FILE = os.path.join(SAVE_DIR, "download_log.txt")

# 定义下载函数
def download_torrent(torrent_id):
    try:
        # 构建下载URL
        url = f"{BASE_URL}?id={torrent_id}&passkey=4e1fb7c4e7cef9733d35c6633ac053f2"
        response = requests.get(url, cookies=COOKIES)

        # 检查响应状态
        if response.status_code == 200 and 'application/x-bittorrent' in response.headers.get('Content-Type', ''):
            # 保存种子文件
            file_path = os.path.join(SAVE_DIR, f"{torrent_id}.torrent")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return True
        else:
            return False
    except RequestException as e:
        return False

# 开始下载
with open(LOG_FILE, "a") as log_file:
    for torrent_id in range(1, 10001):
        success = download_torrent(torrent_id)
        if success:
            log_file.write(f"Successfully downloaded: {torrent_id}\n")
        else:
            log_file.write(f"Failed to download or already exists: {torrent_id}\n")
        # 为了防止过于频繁的请求，我们在每次请求之间设置短暂的休眠时间
        sleep(0.5)  # 休眠0.5秒
        if torrent_id % 100 == 0:
            print(f"Progress: {torrent_id}/10000")

print("Download completed.")
