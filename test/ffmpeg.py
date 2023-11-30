import os
import subprocess
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def screenshot_from_bd(directory, pic_num, file_dir,log_dir):
    video_dir = directory
    # 这里假设每个视频文件的时长为 120 分钟，您可能需要根据实际情况调整
    duration = 20 * 60
    start_time = 5 * 60  # 开始时间为 5 分钟
    end_time = duration - 5 * 60  # 结束时间
    intervals = (end_time - start_time) / pic_num

    for i in range(1, pic_num + 1):
        screenshot_time = start_time + (i - 1) * intervals
        screenshot_name = f"screenshot_{i}.jpg"
        screenshot_path = os.path.join(file_dir, "log", screenshot_name)
        screenshot_keep = "00:00:01"

        command = [
            "docker", "run",
            "-v", f"{video_dir}:/workspace",
            "-v", f"{log_dir}:/output",  # 挂载输出目录
            "jrottenberg/ffmpeg:ubuntu",
            "-y", "-ss", str(screenshot_time),
            "-i", f"/workspace/超级飞侠.Super.Wings.S10E13.2021.4K.WEB-DL.HEVC.AAC-CHDWEB.mp4",
            "-ss", screenshot_keep,
            "-frames:v", "1",
            f"/output/screenshot_{i}.jpg",   # 将截图保存到挂载的输出目录
            "-loglevel", "error"
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"截图成功: {screenshot_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"截图失败: {e}")

# 测试参数
directory = '/Users/Ethan/Desktop/media/超级飞侠.Super.Wings.S10.2021.4K.WEB-DL.HEVC.AAC-CHDWEB'
file_dir = '/Users/Ethan/PycharmProjects/KIMOJI-ATM'
log_dir = '/Users/Ethan/PycharmProjects/KIMOJI-ATM/log'
pic_num = 3

screenshot_from_bd(directory, pic_num, file_dir,log_dir)
