from googleapiclient.discovery import build

# 用你的API密钥替换这里的YOUR_API_KEY
youtube = build('youtube', 'v3', developerKey='AIzaSyDKvGQR18CSwDfjauXyt8-HmCrAthV8pT0')

# 用你的播放列表ID替换这里的PLAYLIST_ID
playlist_id = 'PLOrf2h5ONlwW9lFJ-68wtf7FdMG-45FNG'

# 获取播放列表中的视频
request = youtube.playlistItems().list(
    part='snippet',
    playlistId=playlist_id,
    maxResults=50  # API一次最多返回50个结果
)
response = request.execute()

# 打印视频标题和链接
for item in response.get('items', []):
    title = item['snippet']['title']
    video_id = item['snippet']['resourceId']['videoId']
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    print(f'{title}: {video_url}')
