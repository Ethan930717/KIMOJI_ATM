import requests
import csv
from io import StringIO

# GitHub 上的 CSV 文件 URL
csv_url = "https://raw.githubusercontent.com/KIMOJI-PT/data/main/torrents.csv"

# 使用 requests 获取 CSV 文件内容
response = requests.get(csv_url)
response.raise_for_status()  # 确保请求成功

# 使用 StringIO 来模拟一个文件
csv_file = StringIO(response.text)

# 读取和解析 CSV 文件内容
csv_reader = csv.reader(csv_file, delimiter=',')
for row in csv_reader:
    print(row[0])

# 关闭 StringIO 对象
csv_file.close()
