import re
def extract_https_links(file_path):
    # 使用正则表达式匹配以 'https://' 开头的 URL
    url_pattern = re.compile(r'https://[^\s]+')

    # 存储提取出的 URL 的列表
    extracted_urls = []

    # 打开并读取文件
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 在该行中查找所有的 URL
            urls = url_pattern.findall(line)
            # 将找到的 URL 添加到列表中
            extracted_urls.extend(urls)

    return extracted_urls

# 文件路径，替换为您的文件路径
file_path = '/Users/Ethan/Desktop/updated_html_js_code.txt'

# 提取 URL
urls = extract_https_links(file_path)
for url in urls:
    print(url)