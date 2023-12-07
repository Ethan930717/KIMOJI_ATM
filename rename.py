import os
from pymediainfo import MediaInfo

def find_largest_video_file(folder_path):
    largest_size = 0
    video_file = None
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file_path.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            size = os.path.getsize(file_path)
            if size > largest_size:
                largest_size = size
                video_file = file_path
    return video_file

def get_media_info(file_path):
    media_info = MediaInfo.parse(file_path)
    video_tracks = [track for track in media_info.tracks if track.track_type == 'Video']
    audio_tracks = [track for track in media_info.tracks if track.track_type == 'Audio']

    if not video_tracks:
        return None

    video_track = video_tracks[0]
    audio_track = audio_tracks[0] if audio_tracks else None

    video_codec = video_track.format
    audio_codec = audio_track.format if audio_track else None
    resolution = f"{video_track.width}x{video_track.height}"

    # Additional attributes like HDR, Dolby Vision, 10bit, etc.
    additional_attrs = []
    if 'HDR' in video_track.format_profile:
        additional_attrs.append('HDR')
    if 'Dolby Vision' in video_track.format_profile:
        additional_attrs.append('DV')
    if video_track.bit_depth:
        bit_depth = video_track.bit_depth
        if bit_depth in ['10', '20']:
            additional_attrs.append(f'{bit_depth}bit')

    return video_codec, audio_codec, resolution, '.'.join(additional_attrs)

def rename_folders(directory):
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path) and 'KIMOJI' not in folder:
            largest_video_file = find_largest_video_file(folder_path)
            if largest_video_file:
                info = get_media_info(largest_video_file)
                if info:
                    video_codec, audio_codec, resolution, additional = info
                    new_folder_name = f"{folder}.{resolution}.WEB-DL.{video_codec}.{audio_codec}-{additional}-KIMOJI"
                    new_folder_path = os.path.join(directory, new_folder_name)
                    os.rename(folder_path, new_folder_path)

# Replace 'your_directory_path' with the path of your directory
directory_path = '/mnt/user/unraid/yt/media'
rename_folders(directory_path)
