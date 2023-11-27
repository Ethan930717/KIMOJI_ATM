import re
import subprocess
import os
import logging
import glob
import shutil

current_file_path = os.path.abspath(__file__)
project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
log_dir = os.path.join(project_root_dir, 'log')
logger = logging.getLogger(__name__)

def check_and_extract_bdinfo_from_file(folder_path):
    bdinfo_file_path = os.path.join(log_dir, "BDINFO.bd.txt")
    if os.path.exists(bdinfo_file_path):
        with open(bdinfo_file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
            return extract_first_quick_summary(file_content)
    return None
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

def mount_iso(iso_file):
    mount_point = '/mnt/iso_mount'  # 挂载点路径
    print (log_dir)
    # 确保挂载点目录存在
    if not os.path.exists(mount_point):
        logger.info(f"创建挂载点目录：{mount_point}")
        os.makedirs(mount_point)

    # 检查挂载点是否已被挂载
    if os.path.ismount(mount_point):
        logger.info(f"挂载点已被占用，正在卸载：{mount_point}")
        try:
            subprocess.run(['umount', mount_point], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"卸载挂载点时出错: {e}")
            return None

    # 执行挂载操作
    try:
        subprocess.run(['mount', '-o', 'loop', iso_file, mount_point], check=True)
        logger.info(f"ISO 文件已挂载到：{mount_point}")
        return mount_point
    except subprocess.CalledProcessError as e:
        logger.error(f"挂载 ISO 文件时出错: {e}")
        return None
def find_iso_in_directory(directory):
    iso_files = glob.glob(f"{directory}/**/*.iso", recursive=True)
    return iso_files[0] if iso_files else None
def find_bdmv_parent_directory(folder_path):
    for root, dirs, files in os.walk(folder_path):
        if 'BDMV' in dirs:
            return root
    return None
def generate_and_parse_bdinfo(folder_path):
    # 检查并挂载 ISO 文件（如果存在）
    iso_file = find_iso_in_directory(folder_path)
    if iso_file:
        logger.info(f"检测到 ISO 文件：{iso_file}，正在挂载...")
        mount_point = mount_iso(iso_file)
        if not mount_point:
            logger.error("无法挂载 ISO 文件")
            return None, None, None
        folder_path = mount_point
    bdmv_path = find_bdmv_parent_directory(folder_path)
    if bdmv_path:
        logger.info(f"找到 BDMV 文件夹在路径：{bdmv_path}")
    else:
        logger.error("未找到 BDMV 文件夹")
        return None, None, None
    try:
        docker_command = [
            "docker", "run", "--rm", "--name", "kimoji-bdinfo",
            "-v", f"{bdmv_path}:/mnt/bd",
            "-v", f"{log_dir}:/mnt/report",  # 挂载额外的输出目录
            "hudan717/kimoji-bdinfo", "-w", "/mnt/report"
        ]
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

    bdinfo_file_path = os.path.join(log_dir, 'BDINFO.bd.txt')
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