import re
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

def extract_first_quick_summary(file_content):
    pattern = re.compile(r"QUICK SUMMARY:\s*\n(.*?)\*{20}", re.DOTALL)
    match = pattern.search(file_content)
    return match.group(1).strip() if match else "没有找到快扫结果"

def process_quick_summary(quick_summary):
    # 格式化 Quick Summary，移除每行开头的空格和标题
    lines = quick_summary.split("\n")
    formatted_summary = "\n".join(line.strip() for line in quick_summary.split("\n"))

    # 初始化变量
    type = "BLU"
    resolution = "Unknown"

    # 检查分辨率并设置相应的类型和分辨率
    if "4320p" in formatted_summary:
        type, resolution = "UHD", "4320p"
    elif "2160p" in formatted_summary:
        type, resolution = "UHD", "2160p"
    elif "1080p" in formatted_summary:
        type, resolution = "BLU", "1080p"
    elif "1080i" in formatted_summary:
        type, resolution = "BLU", "1080i"
    else:
        resolution = "1080p"  # 默认分辨率

    return formatted_summary, resolution, type

def generate_and_parse_bdinfo(folder_path):
    try:
        docker_command = ["docker", "run", "--rm", "-v", f"{folder_path}:/mnt/bd", "hudan717/kimoji-bdinfo", "/mnt/bd"]
        process = subprocess.Popen(docker_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        process.wait()
    except subprocess.CalledProcessError as e:
        logger.error(f"运行 BDInfo 时出错: {e}")
        return None

    bdinfo_file_path = os.path.join(folder_path, 'BDINFO.bd.txt')
    if not os.path.exists(bdinfo_file_path):
        logger.warning("未找到 BDInfo 扫描文件")
        return None

    with open(bdinfo_file_path, 'r') as file:
        bdinfo_content = file.read()

    # 解析 BDInfo 报告
    quick_summary = extract_first_quick_summary(bdinfo_content)
    formatted_summary, resolution, type = process_quick_summary(quick_summary)
    return formatted_summary, resolution, type


# 示例调用
#folder_path = '/Users/Ethan/Desktop/media/IMAX.Enhanced.Demo.Disc.Volume.1.2019.2160p.UHD.Blu-ray.HEVC.DTS-HD.MA.7.1-AdBlue'
#formatted_summary, resolution, type = generate_and_parse_bdinfo(folder_path)
#print(formatted_summary)
#print("Resolution:", resolution)
#print("Type:", type)