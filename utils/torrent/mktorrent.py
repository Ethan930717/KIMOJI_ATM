# utils/torrent/mktorrent.py
import subprocess
import os
import logging
logger = logging.getLogger(__name__)

def create_torrent(directory, torrent_name, torrent_dir,comment="KIMOJI PARK",tracker="https://kimoji.club/announce"):
    content_path = os.path.join(directory)
    torrent_path = os.path.join(torrent_dir, f"{torrent_name}.torrent")
    logger.info(f'开始制作种子，种子保存路径{torrent_path}')
    command = [
        "mktorrent",
        "-a", tracker,  # 添加 tracker
        "-o", torrent_path,
        "-c", comment,
        "-p",  # 设置为私有种子
        content_path
    ]
    attempt_count = 0
    max_attempts = 3
    while attempt_count < max_attempts:
        try:
            subprocess.run(command, check=True)
            logger.info(f"种子文件已创建: {torrent_path}")
            return torrent_path
        except subprocess.CalledProcessError as e:
            logger.error(f"创建种子文件时出错: {e}")
            attempt_count += 1
            if attempt_count < max_attempts:
                logger.warning(f"重试制作种子（第 {attempt_count} 次）")
            else:
                logger.warning("达到最大重试次数，停止尝试，本次ATM停止")
                break
    return None