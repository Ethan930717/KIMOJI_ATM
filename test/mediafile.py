import re

mediainfo_output = """
Video
ID                                       : 1
Format                                   : AVC
Format/Info                              : Advanced Video Codec
Format profile                           : High@L4
Format settings                          : CABAC / 4 Ref Frames
Format settings, CABAC                   : Yes
Format settings, Reference frames        : 4 frames
Codec ID                                 : V_MPEG4/ISO/AVC
Duration                                 : 42 min 44 s
Bit rate mode                            : Variable
Bit rate                                 : 3 025 kb/s
Maximum bit rate                         : 20.0 Mb/s
Width                                    : 1 920 pixels
Height                                   : 1 080 pixels
Display aspect ratio                     : 16:9
Frame rate mode                          : Constant
Frame rate                               : 23.976 (24000/1001) FPS
Color space                              : YUV

"""

# 使用您的正则表达式检查
match_resolution = re.search(r'Height\s*:\s*(\d{1,4})(?:\s*(\d{1,4}))?\s*pixels', mediainfo_output, re.IGNORECASE)
match_width = re.search(r'Width\s*:\s*([\d\s]+)pixels', mediainfo_output, re.IGNORECASE)
match_scan_type = re.search(r'Scan type\s+:\s+(\w+)', mediainfo_output)
scan_type = match_scan_type.group(1) if match_scan_type else 'Progressive'
if match_resolution and match_width:
    height = int(match_resolution.group(1))
    width = int(match_width.group(1).replace(" ", ""))
    print(height,width)
    if height < 720:
        print ("SD")
    elif height == 720:
        print ("720p")
    elif height == 1080:
        print ("1080i") if 'Interlaced' in scan_type else print ("1080p")
    elif height >= 2160:
        print ("2160p")
    elif height >= 4320:
        print ("4320p")
    elif width < 1280:
        print ("SD")
    elif width == 1280:
        print ("720p")
    elif width == 1920:
        print ("1080p")
    elif width >= 3840:
        print ("2160p")
    elif width >= 7680:
        print ("4320p")
    print ("other")
print ("other")
