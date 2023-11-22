import re
import os
import sys
import logging

logger = logging.getLogger(__name__)
def extract_title_info(url_name):
    # 提取路径中的最后一个文件夹名称
    media_name = url_name.split('/')[-1]
    logger.info(f'正在解析目录名称:{media_name}')
    # 提取中文片名（从开始到第一个中文字符之后的第一个点）
    match_chinese = re.search(r'([\u4e00-\u9fff]+).*?\.', media_name)
    chinese_title = match_chinese.group(1) if match_chinese else None

    # 提取季数
    match_season = re.search(r'S(\d{2})\.', media_name)
    season = match_season.group(1) if match_season else None

    # 移除中文片名和季数部分
    title_without_chinese = re.sub(r'.*[\u4e00-\u9fff]+.*?\.', '', media_name)
    title_without_season = re.sub(r'\bS\d{2}\b', '', title_without_chinese)
    title_with_english_only = re.sub(r'\bcomplete\b', '', title_without_season.lower(), flags=re.IGNORECASE)

    # 提取英文片名和年份
    match_english_year = re.match(r"(.+?)\.(\d{4})\.", title_with_english_only)
    if match_english_year:
        english_title = match_english_year.group(1).replace('.', ' ').strip()
        year = match_english_year.group(2)
    else:
        # 尝试只提取英文片名（如果没有年份）
        match_english_only = re.match(r"([^.]+)", title_without_chinese)
        english_title = match_english_only.group(1).replace('.', ' ').strip() if match_english_only else None
        year = None
    # 如果只有一个标题，则判断是中文还是英文
    if not chinese_title and english_title:
        if re.search(r'[\u4e00-\u9fff]', english_title):
            chinese_title = english_title
            english_title = None
    # 提取媒介
    match_media = re.search(r'(WEB-DL|UHD|BLURAY|BLU-RAY|HDTV|ENCODE|REMUX)', media_name.upper(), re.IGNORECASE)
    media = match_media.group(1) if match_media else None

    # 提取制作组
    if "-" in media_name:
        maker_candidate = media_name.split('-')[-1]
        if re.match(r'^[A-Za-z0-9]+$', maker_candidate):
            maker = maker_candidate
        else:
            maker = None
    else:
        maker = None
    codec,audiocodec = extract_codec(media_name)
    return analyze_file(chinese_title, english_title, year, season, media, codec, audiocodec, maker, media_name,url_name)

def extract_codec(media_name):
    #分析视频编码
    if 'H' in media_name.upper() and '264' in media_name:
        codec = 'H264'
    elif 'x' in media_name.lower() and '264' in media_name:
        codec = 'x264'
    elif 'H' in media_name.upper() and '265' in media_name:
        codec = 'H265'
    elif 'x' in media_name.lower() and '265' in media_name:
        codec = 'x265'
    elif 'AVC' in media_name.upper():
        codec = 'AVC'
    elif 'HEVC' in media_name.upper():
        codec = 'HEVC'
    elif 'MPEG-2' in media_name.upper():
        codec = 'MPEG-2'
    elif 'MPEG-4' in media_name.upper():
        codec = 'MPEG-4'
    elif 'VC1' in media_name.upper():
        codec = 'VC1'
    elif 'AV1' in media_name.upper():
        codec = 'AV1'
    elif 'VP' in media_name.upper():
        codec = 'VP9'
    else:
        codec = None

        # 分析音频编码
    if media_name.upper() == 'AAC':
        audiocodec = 'AAC'
    elif 'DTS-HD' in media_name.upper() and 'MA' in media_name.upper() and '5.1' in media_name:
        audiocodec = 'DTS-HD MA 5.1'
    elif 'DTS-HD' in media_name.upper() and 'MA' in media_name.upper() and '7.1' in media_name:
        audiocodec = 'DTS-HD MA 7.1'
    elif 'DTS-HD' in media_name.upper() and 'HR' in media_name.upper():
        audiocodec = 'DTS-HD HR'
    elif 'DTS' in media_name.upper():
        audiocodec = 'DTS'
    elif 'TRUEHD' in media_name.upper() and 'ATMOS' in media_name.upper():
        audiocodec = 'TrueHD 7.1 Atmos'
    elif 'TRUEHD' in media_name.upper():
        audiocodec = 'TrueHD 5.1'
    elif '7.1' in media_name.upper() and 'DDP' in media_name.upper():
        audiocodec = 'DDP Atmos 7.1'
    elif 'DDP' in media_name.upper():
        audiocodec = 'DDP 5.1'
    elif 'AC3' in media_name.upper() or 'AC-3' in media_name.upper() or 'DD' in media_name.upper():
        audiocodec = 'AC#'
    elif 'LPCM' in media_name.upper():
        audiocodec = 'LPCM'
    elif 'PCM' in media_name.upper():
        audiocodec = 'PCM'
    elif 'FLAC' in media_name.upper():
        audiocodec = 'FLAC'
    elif 'APE' in media_name.upper():
        audiocodec = 'APE'
    elif 'MP3' in media_name.upper():
        audiocodec = 'MP3'
    elif 'WAV' in media_name.upper():
        audiocodec = 'WAV'
    elif 'M4A' in media_name.upper():
        audiocodec = 'M4A'
    elif 'OPUS' in media_name.upper():
        audiocodec = 'OPUS'
    elif 'AAC' in media_name.upper():
        audiocodec = 'AAC'
    else:
        audiocodec = None
    return codec,audiocodec

def analyze_file(chinese_title, english_title, year, season, media, codec, audiocodec, maker, file_name , url_name):
    missing_elements = []
    upload_title = re.sub(r'\.(?!(5\.1|7\.1\b))', ' ', file_name)
    if not english_title:
        missing_elements.append("英文标题")
    if not year:
        missing_elements.append("年份")
    if not media:
        missing_elements.append("媒介")
    if not codec:
        missing_elements.append("视频编码")
    if not audiocodec:
        missing_elements.append("音频编码")
    if missing_elements:
        missing_str = "、".join(missing_elements)
        logger.error(f'当前的目录名并不是标准的0day格式文件名，不符合KIMOJI发种规则。'
                     f'\n文件名缺少以下内容：{missing_str}。'
                     '\n阿K将跳过当前文件并在文件中创建一个kimoji_error文件以避免再次读取，该文件不会影响您在其他网站的做种。'
                     '\n如需阿K重新读取该文件夹，您可以手动删除该kimoji_pass文件。'
                     '\n如果您认为阿K识别文件名有误，请在KIMOJI提交工单并写明当前文件夹名称。')
        file_path = os.path.join(url_name, "kimoji_pass")
        open(file_path, 'w').close()
        logger.info('pass文件创建成功，删除该文件前将不会再次扫描该目录，请重新启动阿K')
        sys.exit()
    if not maker:
        maker_input = input(f'{file_name}\n在文件名中无法获取到制作组信息，请手动输入，确认留空请回车: ')
        maker = maker_input if maker_input.strip() != '' else None
    if not chinese_title:
        combined_title = f"{chinese_title} {file_name}"
        upload_title = re.sub(r'\.(?!(5\.1|7\.1)(\b|\s))', ' ', combined_title)
    logger.info(f'文件名分析结果\n中文标题:{chinese_title}\n英文标题:{english_title}\n年份:{year}\n季数:{season}\n媒介:{media}\n视频编码:{codec}\n音频编码:{audiocodec}\n制作组:{maker}\n组合上传文件名:{upload_title}')
    return chinese_title, english_title, year, season, media, codec, audiocodec, maker, upload_title

#file_dir = "/Users/Ethan/Destop/media"
#media_name = "IMAX.Enhanced.Demo.Disc.Volume.1.2019.2160p.UHD.Blu-ray.HEVC.DTS-HD.MA.7.1-AdBlue"
#chinese_title, english_title, year, season, media,codec,audiocodec,maker = extract_title_info(media_name,file_dir)
#print(f"Chinese Title: {chinese_title}, English Title: {english_title}, Year: {year}, Season: {season}, Media: {media},codec: {codec}, audiocodec: {audiocodec},  Maker: {maker}")
