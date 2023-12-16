from generate import generate as generate_info
from start_seeding import start_seeding as upload
from config_loader import config
import intro
import sys
import subprocess
import logging
import os
logging.basicConfig(level=logging.INFO)

def remove_ffmpeg_containers():
    try:
        logging.info("开始清除冗余ffmpeg容器")
        cmd = "docker ps -a | grep 'ffmpeg' | awk '{print $1}' | xargs -I {} docker rm {}"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"删除 Docker 容器时出错: {e}")
        sys.exit(1)

def main_menu():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # 设置 log 目录的路径
    log_directory = os.path.join(current_directory, 'log')
    # 确保 log 目录存在
    if not os.path.isdir(log_directory):
        os.makedirs(log_directory, exist_ok=True)
    # 设置 logfile.csv 的路径
    csv_file = os.path.join(log_directory, 'logfile.csv')
    # 显示初始界面
    print(intro)
    remove_ffmpeg_containers()
    while True:
        print("\n请选择操作：")
        print("1 - 生成发种信息")
        print("2 - 开始发种")
        print("0 - 退出")
        choice = input("输入选项：")

        if choice == '1':
            folder_path = config.file_dir
            generate_info(folder_path)
        elif choice == '2':
            upload(csv_file)
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效选项，请重新输入！")

if __name__ == "__main__":
    main_menu()
