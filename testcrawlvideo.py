
from googleapiclient.discovery import build
import yt_dlp
import os
video_url="https://www.youtube.com/watch?v=eAt4PHNF3_g"

CHANNEL_ID = 'UCorFnMmI4eXS1ftlY4PpTsw' 

ydl_opts = {
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['en'],
    # 'subtitlesformat': 'srt',
    'skip_download': True,
    # 'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    try:
        ydl.download([video_url])
        print(f"Đã tải xong phụ đề cho video: {video_url}")
    except Exception as e:
        print(f"Không thể tải phụ đề cho video {video_url}. Lỗi: {e}")

print("\nHoàn tất quá trình tải phụ đề cho tất cả các video!")
