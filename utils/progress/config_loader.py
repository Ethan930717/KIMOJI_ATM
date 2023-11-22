import yaml
import os
import logging
logger = logging.getLogger(__name__)
def load_config(filename='config.yaml'):
    try:
        with open(filename, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("配置文件未找到")
        return None
    except yaml.YAMLError as exc:
        print("解析配置文件时发生错误:", exc)
        return None

def find_media_in_folder(file_dir, mediainfo_supported_formats, bdinfo_supported_formats):
    for entry in os.listdir(file_dir):
        full_path = os.path.join(file_dir, entry)

        if os.path.isdir(full_path) and all(
                exclusion not in os.listdir(full_path) for exclusion in ["kimoji_exclude", "kimoji_pass"]):
            # 递归检查子目录
            media_type = has_media_file(full_path, mediainfo_supported_formats, bdinfo_supported_formats)
            if media_type:
                # 如果在这个子目录或其子目录中找到媒体文件，则返回当前子目录的路径及媒体类型
                return full_path, media_type
    return None

def has_media_file(file_dir, mediainfo_supported_formats, bdinfo_supported_formats):
    for entry in os.listdir(file_dir):
        full_path = os.path.join(file_dir, entry)

        if os.path.isfile(full_path):
            file_format = entry.split('.')[-1].lower()
            if file_format in mediainfo_supported_formats:
                return "mediainfo"
            elif file_format in bdinfo_supported_formats:
                return "bdinfo"
        elif os.path.isdir(full_path):
            # 递归检查子目录
            media_type = has_media_file(full_path, mediainfo_supported_formats, bdinfo_supported_formats)
            if media_type:
                return media_type

    return None  # 没有找到媒体文件

def find_media_folder(file_dir):
    mediainfo_supported_formats = {'mkv', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'mpg', 'mpeg'}
    bdinfo_supported_formats = {'iso', 'm2ts'}
    result = find_media_in_folder(file_dir, mediainfo_supported_formats, bdinfo_supported_formats)
    if result:
        return result
    else:
        # 没有找到合适的文件夹，返回 None
        return None


# 示例调用
#file_dir = "/Users/Ethan/Desktop/media"
#result = find_media_folder(file_dir)
#print(result)
#if result:
 #   folder, media_type = result
  #  print(f"Found media in folder: {folder}, Type: {media_type}")
#else:
 #   print("No media found in any folders.")
