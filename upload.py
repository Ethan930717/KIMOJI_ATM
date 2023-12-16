import requests


def upload_torrent(torrent_data):
    """
    上传种子到指定的 API 端点。

    :param api_token: API 令牌。
    :param torrent_file_path: .torrent 文件的路径。
    :param nfo_file_path: .nfo 文件的路径。
    :param data: 包含其他参数的字典。
    :return: 请求的响应对象。
    """

    url = 'https://your-website.com/api/torrents/upload'  # 替换成您的 API URL

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json'
    }

    files = {
        'torrent': open(torrent_file_path, 'rb'),
        'nfo': open(nfo_file_path, 'rb')
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    return response


# 使用示例
api_token = 'YOUR_API_TOKEN'  # 替换成您的 API 令牌
torrent_file_path = '/path/to/your/file.torrent'  # 替换成您的 .torrent 文件路径
nfo_file_path = '/path/to/your/file.nfo'  # 替换成您的 .nfo 文件路径

# 其他参数
data = {
    'name': 'Torrent Name',
    'description': 'This is a description',
    'mediainfo': 'MediaInfo text output',
    # 添加其他需要的参数
}

response = upload_torrent(api_token, torrent_file_path, nfo_file_path, data)

# 检查响应
if response.status_code == 200:
    print(f"上传成功！{response}")
else:
    print(f"上传失败：{response.text}")
