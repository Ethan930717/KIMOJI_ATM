import subprocess
import os
import logging
import sys
from progress.bar import IncrementalBar
from torf import Torrent
from pathlib import Path
import time

logger = logging.getLogger(__name__)


def create_torrent(directory, torrent_name, torrent_dir, comment="KIMOJI PARK", tracker="https://kimoji.club/announce"):
    content_path = os.path.join(directory)
    torrent_path = os.path.join(torrent_dir, f"{torrent_name}.torrent")
    print(f'torrent_path:{torrent_path}')
    logger.info(f'开始制作种子，种子保存路径{torrent_path}')

    piece_size = 4 * 1024 * 1024
    max_attempts = 3
    path = Path(content_path)
    torrent = Torrent(path=str(path.absolute()), trackers=[tracker], piece_size=piece_size, private=True,
                      created_by="KIMOJI PARK", source="KIMOJI PARK")
    bar = IncrementalBar('阿K正在努力制种', max=torrent.pieces ,suffix="%(index)d/%(max)d [%(eta_td)s]")
    def cb(__torrent: Torrent, path: str, hashed_pieces: int, total_pieces: int):
        bar.next()
    for attempt_count in range(max_attempts):
        if Path(torrent_path).exists():
            try:
                os.remove(torrent_path)
            except Exception as e:
                logger.error(f"删除已存在的种子文件时出错: {e}")
        try:
            torrent.generate(callback=cb, interval=0)
            torrent.write(str(torrent_path))
            logger.info(f"种子文件已创建: {torrent_path}")
            bar.finish()
            return torrent_path
        except Exception as e:
            logger.error(f"创建种子文件时出错: {e}")
            bar.next()
            if attempt_count + 1 < max_attempts:
                logger.warning(f"重试制作种子（第 {attempt_count + 1} 次）")
            else:
                logger.error("达到最大重试次数，停止尝试")
                sys.exit()

    bar.finish()
    return None

#content_path = '/Users/Ethan/Desktop/media/IMAX.Enhanced.Demo.Disc.Volume.1.2019.2160p.UHD.Blu-ray.HEVC.DTS-HD.MA.7.1-AdBlue'
#torrent_name = '11123'
#torrent_dir = '/Users/Ethan/Desktop/media/'
#create_torrent(content_path, torrent_name, torrent_dir)