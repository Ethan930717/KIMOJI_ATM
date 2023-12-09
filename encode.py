import os
import subprocess

def list_directory_contents(directory):
    items = os.listdir(directory)
    for index, item in enumerate(items, start=1):
        print(f"{index}. {item}")
    return items

def reencode_video(input_path, output_path):
    command = ['ffmpeg', '-i', input_path, '-map', '0:v', '-map', '0:a', '-c:v', 'libx265', '-crf', '20', '-preset', 'medium', '-c:a', 'ac3', output_path]
    subprocess.run(command)

def handle_file(file_path):
    output_folder = os.path.join('/home/encoded', os.path.splitext(os.path.basename(file_path))[0])
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, os.path.basename(file_path).replace(os.path.splitext(file_path)[1], '.mkv'))
    reencode_video(file_path, output_file)
    os.remove(file_path)

def handle_directory(directory_path):
    video_files = [file for file in os.listdir(directory_path) if file.endswith(('.mp4', '.mkv', '.avi'))]
    if len(video_files) == 1:
        handle_file(os.path.join(directory_path, video_files[0]))
        os.rmdir(directory_path)
    elif len(video_files) > 1:
        for index, video_file in enumerate(video_files, start=1):
            print(f"{index}. {video_file}")
        choice = int(input("请选择要重编码的视频文件: ")) - 1
        handle_file(os.path.join(directory_path, video_files[choice]))
        count_file = os.path.join(directory_path, str(len([name for name in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, name)) and name.isdigit()])))
        open(count_file, 'a').close()
        if int(os.path.basename(count_file)) == len(video_files):
            os.rmdir(directory_path)

def main():
    directory = '/home/media'
    items = list_directory_contents(directory)
    choice = int(input("请选择一个文件或文件夹进行处理: ")) - 1
    selected_item = items[choice]
    selected_path = os.path.join(directory, selected_item)

    if os.path.isfile(selected_path):
        handle_file(selected_path)
    elif os.path.isdir(selected_path):
        handle_directory(selected_path)

if __name__ == "__main__":
    main()
