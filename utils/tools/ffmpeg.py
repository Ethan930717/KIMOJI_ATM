import os
import subprocess
import requests
import logging
import glob
from PIL import Image
from utils.tools.mount import  mount_iso
logger = logging.getLogger(__name__)
current_file_path = os.path.abspath(__file__)
project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
log_dir = os.path.join(project_root_dir, 'log')
def get_largest_m2ts_file(directory):
    m2ts_files = glob.glob(f"{directory}/**/*.m2ts", recursive=True)
    largest_file = max(m2ts_files, key=os.path.getsize, default=None)
    return largest_file

def find_iso_in_directory(directory):
    # 在指定目录及其子目录中搜索 ISO 文件
    iso_files = glob.glob(f"{directory}/**/*.iso", recursive=True)
    return iso_files[0] if iso_files else None
def screenshot_from_bd(directory, pic_num, file_dir):
    logger.info('开始处理原盘')
    # 在目录中查找 ISO 文件
    iso_file = find_iso_in_directory(directory)
    if iso_file:
        logger.info(f"检测到 ISO 文件：{iso_file}，正在挂载...")
        mount_point = mount_iso(iso_file)
        if not mount_point:
            logger.error("无法挂载 ISO 文件")
            return
        directory = mount_point

    # 查找最大的 .m2ts 文件
    largest_file = get_largest_m2ts_file(directory)
    if not largest_file:
        logger.error("未找到有效的 .m2ts 文件")
        return

    logger.info(f"找到最大的 .m2ts 文件: {largest_file}")
    return screenshot_from_video(largest_file, pic_num,file_dir, image_format='png')

def get_video_duration(file_path):
    video_dir = os.path.dirname(file_path)  # 获取视频文件所在的目录
    video_file = os.path.basename(file_path)  # 获取视频文件名
    try:
        command = [
            "docker", "run",
            "-v", f"{video_dir}:/workspace",
            "jrottenberg/ffmpeg:ubuntu",
            "-i", f"/workspace/{video_file}",
            "2>&1"
        ]

        # 使用 shell 命令执行 Docker 命令，并通过管道传递到 grep
        result = subprocess.check_output(' '.join(command) + " | grep 'Duration'", shell=True, text=True)
        duration_str = result.split('Duration: ')[1].split(',')[0].strip()
        h, m, s = map(float, duration_str.split(':'))
        return int(h * 3600 + m * 60 + s)
    except subprocess.CalledProcessError:
        logger.error("获取视频时长失败")
        return None

def upload_to_chevereto(image_path,i):
    url = 'https://img.kimoji.club'
    api_key = 'chv_Qv3_df17c2e80aa516206778a352b3eff8b98bb80779924fa9d63acfd077c05d31fb6b0d443b7768550efc9be2cd02dcfe02ed4b0c72a0a1d32de328ae5aa8ac81c4'
    try_num = 0
    while try_num < 3:
        try:
            payload = {
                'key': api_key,
                'format': 'json',
            }
            files = {
                'source': open(image_path, 'rb')
            }
            response = requests.post(url + '/api/1/upload',files=files,data=payload)
            response.raise_for_status()
            image_url = response.json().get('image', {}).get('url')

            if image_url:
                logger.info(f"第{i}张图片上传成功: {image_url}")
                return f"[img]{image_url}[/img]"
            else:
                logger.warning(f"第{i}张图片上传失败，无返回链接")
                try_num += 1

        except requests.RequestException as e:
            logger.warning(f"第{i}张图片上传失败: {e}")
            try_num += 1

    logger.error(f"第{i}张图片连续三次上传失败")
    return None

def screenshot_from_video(file_path, pic_num, file_dir,image_format='jpg'):
    logger.info('开始截图')
    duration = get_video_duration(file_path)
    if not duration:
        logger.error("无法获取视频时长")
        return
    # 根据视频时长确定开始和结束时间
    if duration <= 20 :  # 20分钟以内
        start_time = 1  # 开始时间：1分钟
        end_time = duration - 1  # 结束时间：总时长减1分钟
    else:  # 超过20分钟
        start_time = 5  # 开始时间：5分钟
        end_time = duration - 5  # 结束时间：总时长减5分钟

    intervals = (end_time - start_time) / pic_num  # 计算时间间隔
    image_paths = []
    video_dir = os.path.dirname(file_path)  # 获取视频文件所在的目录
    video_file = os.path.basename(file_path)  # 获取视频文件名
    for i in range(1, pic_num + 1):
        screenshot_time = start_time + (i - 1) * intervals
        screenshot_name = f"{i}.{image_format}"
        screenshot_path = os.path.join(log_dir, screenshot_name)
        screenshot_keep = "00:00:01"
        command = [
            "docker", "run","--rm","--name","kimoji-bdinfo",
            "-v", f"{video_dir}:/workspace",
            "-v", f"{log_dir}:/output",  # 挂载输出目录
            "jrottenberg/ffmpeg:ubuntu",
            "-y", "-ss", str(screenshot_time),
            "-i", f"/workspace/{video_file}",
            "-ss", screenshot_keep,
            "-frames:v", "1",
            f"/output/{screenshot_name}",   # 将截图保存到挂载的输出目录
            "-loglevel", "error"
        ]
        #command = f"ffmpeg -y -ss {screenshot_time} -i '{file_path}' -ss '{screenshot_keep}' -frames:v 1 '{screenshot_path}' -loglevel error"
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"第{i}张图片截图成功: {screenshot_name}")
            image_paths.append(screenshot_path)
            if image_format == 'png':
                if i == 1:
                    logger.info(f"为了节省阿K的图床空间，将对PNG图片进行压缩处理，压缩耗时较长，请耐心等待")
                logger.info(f"正在压缩第{i}张图片")
                compress_image(i,screenshot_path)
        except subprocess.CalledProcessError:
            logger.error(f"第{i}张图片截图失败")

    pic_urls = upload_images_and_get_links(image_paths)
    logger.info(f'获取bbcode代码:\n{pic_urls}')
    return pic_urls
def upload_images_and_get_links(image_paths):
    pic_urls = []
    for i, image_path in enumerate(image_paths, start=1):
        upload_result = upload_to_chevereto(image_path, i)
        if upload_result:
            pic_urls.append(upload_result)
    return '\n'.join(pic_urls)

def compress_image(i,image_path, quality=85):
    """
    压缩图片
    :param image_path: 图片路径
    :param quality: 压缩质量，范围从 0（最差）到 100（最佳）
    """
    try:
        img = Image.open(image_path)
        img.save(image_path, "PNG", optimize=True, quality=quality)
        logger.info(f"第{i}张图片压缩成功: {image_path}")
    except Exception as e:
        logger.error(f"压缩图片时出错: {e}")

# 示例调用
#directory = '/Users/Ethan/Desktop/media/IMAX.Enhanced.Demo.Disc.Volume.1.2019.2160p.UHD.Blu-ray.HEVC.DTS-HD.MA.7.1-AdBlue'  # 视频文件路径
#file_dir = '/Users/Ethan/PycharmProjects/KIMOJI-ATM'
#pic_num = 3  # 截图数量
#screenshot_from_bd(directory,pic_num ,file_dir)
