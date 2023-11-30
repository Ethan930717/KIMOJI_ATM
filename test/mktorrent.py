from torf import Torrent
from progress.bar import IncrementalBar
from pathlib import Path
import os
import sys

def make_private_torrent(filepath, torrentname, tracker):
    path = Path(filepath)
    torrent_path = Path(torrentname)

    # 确定文件或目录是否存在
    if not path.exists():
        print(f"指定的路径不存在: {filepath}")
        sys.exit(1)

    # 设置种子的参数
    piece_size = 4 * 1024 * 1024  # 4 MiB
    private = True
    created_by = "ATM"
    source = "ATM"

    torrent = Torrent(path=str(path), trackers=[tracker], piece_size=piece_size, private=private, created_by=created_by, source=source)

    # 创建进度条
    bar = IncrementalBar('制种进度', max=torrent.pieces)

    # 回调函数更新进度条
    def update_progress(torrent, _path, hashed, total):
        bar.goto(hashed)

    # 生成种子文件
    torrent.generate(callback=update_progress)
    torrent.write(str(torrent_path))

    # 完成后关闭进度条
    bar.finish()
    print(f"种子文件已创建: {torrent_path}")

# 调用函数制作种子文件
make_private_torrent(
    filepath="/Users/Ethan/Desktop/media/IMAX.Enhanced.Demo.Disc.Volume.1.2019.2160p.UHD.Blu-ray.HEVC.DTS-HD.MA.7.1-AdBlue",
    torrentname="IMAX_Enhanced_Demo_Disc.torrent",
    tracker="http://your-tracker-url.com/announce"
)
