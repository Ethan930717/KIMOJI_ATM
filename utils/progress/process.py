from utils.info.tmdb_id import search_tmdb
from utils.info.imdb_id import search_imdb
from utils.info.additional_ids import get_additional_ids,search_ids_from_imdb
from utils.progress.config_loader import find_media_folder
from utils.torrent.mktorrent import create_torrent
from utils.info.title import extract_title_info
from utils.info.tvdb_id import search_tvdb
from utils.tools.mediainfo import save_mediainfo_to_file
from utils.tools.bdinfo import generate_and_parse_bdinfo
from utils.tools.ffmpeg import screenshot_from_video,screenshot_from_bd
from utils.tools.bdinfo import check_and_extract_bdinfo_from_file,process_quick_summary
from utils.progress.upload import kimoji_upload
import os
import sys
import logging
import csv
import datetime
logger = logging.getLogger(__name__)
current_file_path = os.path.abspath(__file__)
project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
log_dir = os.path.join(project_root_dir, 'log')
log_file_path = os.path.join(log_dir, 'record.csv')
#寻找同名种子
def check_existing_torrent(torrent_dir, file_name):
    torrent_name = file_name + ".torrent"
    torrent_path = os.path.join(torrent_dir, torrent_name)
    if os.path.exists(torrent_path):
        return torrent_path  # 返回找到的种子文件路径
    return None  # 如果没有找到文件，则返回 None

#制作种子
def create_torrent_if_needed(file_dir, torrent_dir):
    result = find_media_folder(file_dir)
    if result:
        #file_name是媒体目录路径
        file_name, action = result
        file_name = file_name.split('/')[-1]
        folder_path = os.path.join(file_dir, file_name)

        chinese_title, english_title, year, season, media, codec, audiocodec, maker, upload_title = extract_title_info(folder_path)
        tmdb_id, imdb_id, mal_id, tvdb_id, media_type, child, keywords = handle_media(chinese_title, english_title, year, season, media, maker)
        if not media_type:
            logger.error('无法确认视频类型，已记录跳过本目录，请重新召唤阿K')
            file_path = os.path.join(folder_path, "kimoji_pass")
            open(file_path, 'w').close()
            logger.info('pass文件创建成功，删除该文件前将不会再次扫描该目录，请重新启动阿K')
            log_to_csv(folder_path, "失败", log_file_path , "")
            sys.exit()
        imdb_id = "0" if not imdb_id else imdb_id
        mal_id = "0" if not mal_id else mal_id
        tvdb_id = "0" if not tvdb_id else tvdb_id
        tmdb_id = "0" if not tmdb_id else tmdb_id
        existing_torrent_path = check_existing_torrent(torrent_dir, file_name)
        if not existing_torrent_path:
            logger.warning(f"未找到同名种子，开始制作种子")
            create_torrent(folder_path, file_name, torrent_dir)
            #print(folder_path, file_name, torrent_dir)
            torrent_path = os.path.join(torrent_dir, f"{file_name}.torrent")
            logger.info(f"种子文件已创建: {torrent_path}")
            return torrent_path, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, mal_id, tvdb_id, media_type, child, keywords, upload_title
        else:
            logger.info(f"找到同名种子：{existing_torrent_path}，跳过制种")
            return existing_torrent_path, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, mal_id, tvdb_id, media_type, child, keywords, upload_title
    else:
        logging.error("未找到可用的媒体文件夹，找不到可以发布的资源,请检查配置文件")
        sys.exit()
        return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None


#mediainfo/bdinfo解析
def process_media_directory(torrent_path, file_dir, pic_num, username, password, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, mal_id, tvdb_id, media_type,  child, internal, personal, keywords, upload_title):
    file_name, action = find_media_folder(file_dir)
    mediainfo_output = ''
    bd_info = ''
    if file_name:
        folder_path = os.path.join(file_dir, file_name)
        logger.info(f'当前文件目录:{folder_path}')
         # 根据视频文件类型执行相应操作
        if action == "mediainfo":
            mediainfo_output_path = os.path.join(folder_path, "mediainfo.txt")
            resolution, video_format, audio_format ,largest_video_file, mediainfo_output = save_mediainfo_to_file(folder_path, mediainfo_output_path)
            if resolution and video_format and audio_format:
                print(
                    f"分析结果: \n分辨率: {resolution}, 视频格式: {video_format}, 音频格式: {audio_format}")
                pic_urls = screenshot_from_video(largest_video_file,pic_num,file_dir)
            else:
                logger.error("无法获取 Mediainfo 分析结果，请检查视频文件是否损坏")
                file_path = os.path.join(file_name, "kimoji_pass")
                open(file_path, 'w').close()
                logger.info('pass文件创建成功，删除该文件前将不会再次扫描该目录，请重新启动阿K')
                log_to_csv(folder_path, "失败", log_file_path, "")
                sys.exit()
        elif action == "bdinfo":
            logger.info("检测到原盘，开始使用bdinfo解析")
            quick_summary = check_and_extract_bdinfo_from_file(folder_path)
            if quick_summary:
                bd_info, resolution, type = process_quick_summary(quick_summary)
                logger.info("从文件中成功提取 BDInfo，准备开始截图")
                pic_urls = screenshot_from_bd(folder_path, pic_num, file_dir)
            else:
                logger.info("未找到 BDInfo 文件，开始使用 bdinfo 工具解析")
                bd_info, resolution, type = generate_and_parse_bdinfo(folder_path)
                if bd_info:
                    media = "disc"
                    logger.info("BDInfo 分析完成")
                    print("输出快扫信息:")
                    print(bd_info)
                    pic_urls = screenshot_from_bd(folder_path,pic_num,file_dir)
                else:
                    logger.error("BDInfo 分析失败或未找到有效文件，请检查文件是否正常")
                    file_path = os.path.join(file_name, "kimoji_pass")
                    open(file_path, 'w').close()
                    logger.info('pass文件创建成功，删除该文件前将不会再次扫描该目录，请重新启动阿K')
                    log_to_csv(folder_path, "失败", log_file_path ,"")
                    sys.exit()
        else:
            logger.error("无法找到可解析的影片")
            sys.exit()
        kimoji_upload(torrent_path, file_name, username, password, chinese_title, english_title, year, season, media, codec, audiocodec, maker ,pic_urls, tmdb_id, imdb_id, mal_id, tvdb_id, media_type, child, resolution, bd_info, internal,personal,keywords,upload_title, mediainfo_output)
    else:
        logger.warning("没有找到合适的媒体文件夹")



def handle_media(chinese_title, english_title, year, season, media, maker):
    item_type, tmdb_id, media_type, chinese_name, child, keywords = search_tmdb(english_title)
    imdb_id, mal_id, tvdb_id = None, None, None
    if tmdb_id != 0:
        imdb_id, mal_id = get_additional_ids(tmdb_id, item_type, english_title)
        tvdb_id = search_tvdb(english_title) if english_title else 0
        media_type = item_type
    else:
        imdb_search_id, media_type = search_imdb(english_title, media)
        if imdb_search_id:
            tmdb_id, imdb_id, mal_id = search_ids_from_imdb(imdb_search_id, english_title, media_type)
            tvdb_id = search_tvdb(english_title) if english_title else 0
    print(f'最终结果:\nmedia_type:{media_type}\ntmdb:{tmdb_id}\nimdb:{imdb_id}\nmal:{mal_id}\ntvdb:{tvdb_id}')
    return tmdb_id, imdb_id, mal_id, tvdb_id, media_type, child, keywords

def log_to_csv(url_name, status, log_file_path,torrent_url):
    with open(log_file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([url_name, status, current_time, torrent_url])

#def handle_found_media(tmdb_id, item_type, media_type, chinese_title, english_title, child, year, season, maker):
    #imdb_id, mal_id = get_additional_ids(tmdb_id, item_type, english_title)
    #tvdb_id = search_tvdb(english_title) if english_title else 0
    #logger.info(f'最终结果:\nmedia_type:{media_type}\ntmdb:{tmdb_id}\nimdb:{imdb_id}\nmal:{mal_id}\ntvdb:{tvdb_id}')



#chinese_title = "汪汪队"
#english_title="汪汪队"
#tmdb_id = "12225"
#year="2014"
#season= 1
#maker= "kimoji"
#handle_media(chinese_title, english_title, year, season, "series", maker)