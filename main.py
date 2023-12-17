from generate import generate as generate_info
from start_seeding import start_seeding as upload
from config_loader import config
from intro import intro as intro_info
import sys
import subprocess
import csv
import ffmpeg
import logging
import os
logging.basicConfig(level=logging.INFO)



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
    print(intro_info)
    while True:
        print("\n请选择操作：")
        print("1 - 生成发种信息")
        print("2 - 开始发种")
        print("3 - 上传截图")
        print("0 - 退出")
        choice = input("输入选项：")

        if choice == '1':
            folder_path = config.file_dir
            generate_info(folder_path)
        elif choice == '2':
            upload(csv_file)
        elif choice == '3':
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)

            for index, row in enumerate(rows[1:], start=1):
                print(f"{index} - {row}")

            try:
                selected_index = int(input("选择要处理的行号：")) - 1
                if 0 <= selected_index < len(rows) - 1:
                    selected_row = rows[selected_index + 1]
                    folder_path = selected_row[0]

                    largest_video_file = get_largest_video_file(folder_path)
                    if largest_video_file:
                        pic_urls = ffmpeg.screenshot_from_video(largest_video_file, log_directory)
                        print(f"截图链接：\n{pic_urls}")
                    else:
                        print("未找到有效的视频文件")
                else:
                    print("无效的行号")
            except ValueError:
                print("输入无效，请输入数字")
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效选项，请重新输入！")



def get_largest_video_file(directory):
    """在指定目录中找到最大的视频文件"""
    video_extensions = ['.mp4', '.mkv', '.avi', '.m2ts', '.mov']  # 根据需要添加其他视频格式
    largest_file = None
    max_size = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in video_extensions):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size > max_size:
                    max_size = file_size
                    largest_file = file_path

    return largest_file

if __name__ == "__main__":
    main_menu()
