import logging
import os
import subprocess
import re

logger = logging.getLogger(__name__)

def find_largest_video_file(folder_path):
    logger.info("正在对目录下最大的视频文件进行mediainfo解析")
    largest_file = None
    largest_size = 0

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > largest_size:
                largest_file = file_path
                largest_size = file_size

    return largest_file

def parse_resolution(mediainfo_output):
    if "080 pixels" in mediainfo_output or "920 pixels" in mediainfo_output:
        if "Constant" in mediainfo_output:
            return "1080p"
        else:
            return "1080i"
    elif "720 pixels" in mediainfo_output or "280 pixels" in mediainfo_output:
        return "720p"
    elif "160 pixels" in mediainfo_output or "840 pixels" in mediainfo_output:
        return "2160p"
    elif "320 pixels" in mediainfo_output or "680 pixels" in mediainfo_output:
        return "4320p"
    else:
        return "1080p"  # 默认分辨率
def parse_video_audio_format(mediainfo_output):
    video_format_match = re.search(r'Video\n(?:.*\n)*?Format\s+:\s+([^\n]+)', mediainfo_output)
    audio_format_match = re.search(r'Audio\n(?:.*\n)*?Format\s+:\s+([^\n]+)', mediainfo_output)
    commercial_name_match = re.search(r'Commercial name\s+:\s+([^\n]+)', mediainfo_output)

    video_format = video_format_match.group(1).strip() if video_format_match else 'Unknown'
    audio_format = audio_format_match.group(1).strip() if audio_format_match else 'Unknown'
    commercial_name = commercial_name_match.group(1).strip() if commercial_name_match else ''

    if commercial_name:
        audio_format = f"{audio_format} ({commercial_name})"

    return video_format, audio_format

def save_mediainfo_to_file(folder_path, output_file_path):
    largest_video_file = find_largest_video_file(folder_path)

    if largest_video_file:
        try:
            mediainfo_output = subprocess.check_output(["mediainfo", largest_video_file], text=True)
            mediainfo_output = mediainfo_output.replace(largest_video_file, os.path.basename(largest_video_file))

            resolution = parse_resolution(mediainfo_output)
            video_format, audio_format = parse_video_audio_format(mediainfo_output)

            with open(output_file_path, 'w') as file:
                file.write(mediainfo_output)
                logger.info(f"MediaInfo 已保存至: {output_file_path}")

            return resolution, video_format, audio_format, largest_video_file, mediainfo_output
        except subprocess.CalledProcessError as e:
            logger.error(f"获取 MediaInfo 时出错: {e}")
            return None, None, None, None, None
    else:
        logger.warning("在文件夹中未找到视频文件")
        return None, None, None, None, None

def read_mediainfo(output_file_path):
    try:
        with open(output_file_path, 'r', encoding='utf-8') as file:  # 使用utf-8编码打开
            return file.read()  # 读取并返回文件内容
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return str(e)

