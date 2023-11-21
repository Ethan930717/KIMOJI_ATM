import subprocess
import os

def mount_iso(iso_path, mount_point=None):
    if mount_point is None:
        mount_point = "/mnt/iso"  # 或者任何其他临时目录
    try:
        os.makedirs(mount_point, exist_ok=True)
        subprocess.run(["sudo", "mount", "-o", "loop", iso_path, mount_point], check=True)
        return mount_point
    except subprocess.CalledProcessError as e:
        logger.error(f"无法挂载 ISO 文件: {e}")
        return None
