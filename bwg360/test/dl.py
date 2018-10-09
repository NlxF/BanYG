
import youtube_dl

ydl_opts = {
    'format': 'bestaudio/best', # choice of quality
    'extractaudio' : True,      # only keep the audio
    'outtmpl': 'output',        # name the location
    '-o -': True,               # to stream content out
    'noplaylist' : True,        # only download single song, not playlist
    'prefer-ffmpeg' : True,
    # 'verbose': True,
    'postprocessors': [{
            'key': 'FFmpegMetadata'
            },
            {
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': '192',
      }],
    # 'logger': MyLogger(),
    # 'progress_hooks': [my_hook],
}

url = 'https://www.youtube.com/watch?v=pqmcEGhaWPs'

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    result = ydl.download([url])

