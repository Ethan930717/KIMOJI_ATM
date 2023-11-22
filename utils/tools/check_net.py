import subprocess
import platform
from utils.progress.intro import intro

def check_network(urls):
    # 根据操作系统选择 ping 命令
    param = '-n' if platform.system().lower()=='windows' else '-c'

    for url in urls:
        try:
            # 提取域名/IP地址
            domain = url.split("//")[-1].split("/")[0]
            response = subprocess.run(['ping', param, '1', domain], stdout=subprocess.PIPE)

            # 检查响应
            if response.returncode == 0:
                print(f"成功连接到 {url}")
            else:
                print(f"无法连接到 {url}，请检查您的网络连接。")
                return False
        except Exception as e:
            print(f"检测 {url} 时出错: {e}")
            return False
    return True

def check():
    print(intro)
    print("正在检查网络环境，请稍后")
    urls_to_check = [
        "https://www.themoviedb.org",
        "https://www.imdb.com",
        "https://myanimelist.net",
        "https://thetvdb.com",
        "https://kimoji.club"
    ]
    if not check_network(urls_to_check):
        print("网络检查失败，请检查您的网络环境...")
        return  # 结束程序

check()
