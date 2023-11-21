import qbittorrentapi
from utils.progress.config_loader import load_config
import logging
import time
import sys
import os
logger = logging.getLogger(__name__)


def add_torrent_to_qbittorrent(torrent_path, config_url, skip_checking=True, max_retries=3):
    config = load_config(os.path.join(config_url, 'config.yaml'))
    qbt_client = qbittorrentapi.Client(
        host=config['qbittorrent']['url'],
        port=config['qbittorrent']['port'],
        username=config['qbittorrent']['username'],
        password=config['qbittorrent']['password']
    )
    try:
        qbt_client.auth_log_in()
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return

    retries = 0
    while retries < max_retries:
        try:
            with open(torrent_path, 'rb') as torrent_file:
                qbt_client.torrents_add(
                    torrent_files=[torrent_file],
                    category='KIMOJI',
                    save_path=config['qbittorrent']['save_path'],
                    skip_checking=skip_checking
                )
            logger.info("种子添加成功,小K收工啦")
            sys.exit(0)
        except Exception as e:
            retries += 1
            logger.warning(f"添加种子时发生错误: {e}")
            if retries >= max_retries:
                logger.error("达到最大重试次数，停止尝试，请手动添加种子")
                sys.exit(1)
            logger.warning(f"正在尝试第 {retries} 次重试")
            time.sleep(5)
