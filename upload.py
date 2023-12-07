import os
import requests

def upload_image(file_path, api_key):
    url = "https://img.kimoji.club/api/1/upload"  # 请替换为您的 API 端点
    payload = {
        'source': open(file_path, 'rb'),
        'format': 'json'
    }
    headers = {
        'Authorization': 'Bearer ' + api_key,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    response = requests.post(url, headers=headers, files=payload)
    if response.status_code == 200:
        return response.json()['image']['display_url']
    else:
        return "Error: " + str(response.status_code)

def main():
    directory = "/Users/Ethan/Documents/GitHub/KIMOJI_ATM/log"
    api_key = "chv_Qv3_df17c2e80aa516206778a352b3eff8b98bb80779924fa9d63acfd077c05d31fb6b0d443b7768550efc9be2cd02dcfe02ed4b0c72a0a1d32de328ae5aa8ac81c4"  # 替换为您的 API 密钥

    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):  # 这里假设只处理 JPG 文件
            file_path = os.path.join(directory, filename)
            image_url = upload_image(file_path, api_key)
            print(f"BBCode for {filename}: [url={image_url}][img]{image_url}[/img][/url]")

if __name__ == "__main__":
    main()
