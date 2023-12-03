from utils.progress.config_loader import load_config
from utils.progress.process import process_media_directory, create_torrent_if_needed
import logging
from utils.progress.intro import intro
import sys
import subprocess


logging.basicConfig(level=logging.INFO)
def remove_ffmpeg_containers():
    try:
        logging.info("开始清除冗余ffmpeg容器")
        cmd = "docker ps -a | grep 'ffmpeg' | awk '{print $1}' | xargs -I {} docker rm {}"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"删除 Docker 容器时出错: {e}")
        sys.exit(1)
def main():
    print(intro)
    print("您正在使用的是KIMOJI专用发种机，使用前请确认您在KIMOJI有上传权限。")
    remove_ffmpeg_containers()
    config = load_config()
    if config:
        logging.info("配置文件读取成功，正在寻找媒体目录")
        file_dir = config['basic']['file_dir']
        torrent_dir = config['basic']['torrent_dir']
        pic_num  = config['basic']['pic_num']
        username = config['basic']['username']
        password = config['basic']['password']
        internal = config['basic']['internal']
        personal = config['basic']['personal']
        #print(f'torrent_dir:{torrent_dir}')
        torrent_path, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, item_type, child, keywords, upload_title ,chinese_name = create_torrent_if_needed(file_dir, torrent_dir)

        if torrent_path:
            process_media_directory(torrent_path, file_dir,pic_num,username, password, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, item_type, child, internal, personal, keywords, upload_title, chinese_name)
        else:
            logging.error('未配置种子存放目录，请检查config.yaml')
            sys.exit()
    else:
        logging.error('未找到配置文件，请检查config.yaml')
        sys.exit()

if __name__ == "__main__":
    main()