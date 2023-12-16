from generate import generate as generate_info
from config_loader import config
import intro
import sys
import subprocess
import logging
logging.basicConfig(level=logging.INFO)

def remove_ffmpeg_containers():
    try:
        logging.info("开始清除冗余ffmpeg容器")
        cmd = "docker ps -a | grep 'ffmpeg' | awk '{print $1}' | xargs -I {} docker rm {}"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"删除 Docker 容器时出错: {e}")
        sys.exit(1)

def start_seeding():
    # 这里填入发种的逻辑
    print("开始发种...")

def main_menu():
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
            start_seeding()
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效选项，请重新输入！")

if __name__ == "__main__":
    main_menu()
