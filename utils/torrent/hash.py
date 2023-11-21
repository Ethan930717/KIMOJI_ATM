import bencodepy
import hashlib

import hashlib
import bencodepy

def calculate_info_hash(torrent_file_path):
    # Read the torrent file
    with open(torrent_file_path, 'rb') as torrent_file:
        torrent_data = bencodepy.decode(torrent_file.read())

    # Get the bencoded form of the 'info' field
    info_bencoded = bencodepy.encode(torrent_data[b'info'])

    # Calculate the SHA1 hash of the info field
    info_hash = hashlib.sha1(info_bencoded).hexdigest()
    return info_hash

# 使用函数
info_hash = calculate_info_hash('/Users/Ethan/Desktop/media/IMAX.Enhanced.Demo.Disc.Volume.1.2019.2160p.UHD.Blu-ray.HEVC.DTS-HD.MA.7.1-AdBlue.torrent')
print(info_hash)
