from utils.progress.config_loader import load_config
from utils.progress.process import process_media_directory, create_torrent_if_needed
import logging
from utils.progress.intro import intro
import sys


logging.basicConfig(level=logging.INFO)

def main():
    print(intro)
    user_input = input("您正在使用的是KIMOJI专用发种机，请确认您在KIMOJI有上传权限。\n确认开始请回车，否则请输入任意字符关闭KIMOJI-ATM: ")
    if user_input:
        print("KIMOJI-ATM已关闭")
        return  # 结束程序
    config = load_config()
    if config:
        logging.info("配置文件读取成功，正在寻找媒体目录")
        file_dir = config['basic']['file_dir']
        torrent_dir =  config['basic']['torrent_dir']
        pic_num  = config['basic']['pic_num']
        username = config['basic']['username']
        password = config['basic']['password']
        internal = config['basic']['internal']
        personal = config['basic']['personal']
        torrent_path, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, mal_id, tvdb_id ,media_type, child, keywords, upload_title = create_torrent_if_needed(file_dir, torrent_dir)

        if torrent_path:
            process_media_directory(torrent_path, file_dir,pic_num,username, password, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, mal_id, tvdb_id ,media_type, child, internal, personal, keywords, upload_title)
        else:
            logging.error('未配置种子存放目录，请检查config.yaml')
            sys.exit()
    else:
        logging.error('未找到配置文件，请检查config.yaml')
        sys.exit()

if __name__ == "__main__":
    main()