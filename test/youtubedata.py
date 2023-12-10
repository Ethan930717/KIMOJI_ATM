from googleapiclient.discovery import build

# 用你的API密钥替换这里的YOUR_API_KEY
youtube = build('youtube', 'v3', developerKey='AIzaSyDKvGQR18CSwDfjauXyt8-HmCrAthV8pT0')

# 用你的播放列表ID替换这里的PLAYLIST_ID
playlist_id = 'PLOrf2h5ONlwW9lFJ-68wtf7FdMG-45FNG'

def get_playlist_videos(playlist_id):
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50  # API一次最多返回50个结果
    )

    with open('/home/urls2.txt', 'w') as file:
        while request is not None:
            response = request.execute()

            # 仅保存视频链接
            for item in response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                file.write(video_url + '\n')

            # 获取下一页
            request = youtube.playlistItems().list_next(request, response)

get_playlist_videos(playlist_id)
