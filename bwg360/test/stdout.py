import sys
import youtube_dl
import shutil
# import subprocess
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
    from io import BytesIO


old_stdout = sys.stdout
mystdout = StringIO()


class MyLogger(object):

    def debug(self, msg):
        print('debug information: %r' % msg)

    def warning(self, msg):
        print('warning: %r' % msg)

    def error(self, msg):
        print('error: %r' % msg)

def my_hook(d):
    print(d['status'])
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
        
        

class MyHook(object):
    def __init__(self):
        self.isBegin = False

    def __call__(self, d):
        if not self.isBegin:
            self.isBegin = True
            print('Start to downloading...')

            # redirect stdout to StringIO buf
            sys.stdout = mystdout
        elif d['status'] == 'finished':

        	# set back stdout
            sys.stdout = old_stdout

            print('Done downloading, now converting ...')
        else:
        	pass
            # print('Current status: ' + d['status'])

def downloader():
	ydl_opts = {
	    'format': 'bestaudio/best', # choice of quality
	    # 'extractaudio' : True,      # only keep the audio
	    # 'outtmpl': '%(title)s.%(ext)s',        # name the location
	    # '-o -': True,               # to stream content out
	    # 'noplaylist' : True,        # only download single song, not playlist
	    # 'prefer-ffmpeg' : True,
	    'postprocessors': [{
	            'key': 'FFmpegMetadata',
	            #'preferredcodec': 'mp3',
	            # 'preferredquality': '192',
	      }],
	    'logger': MyLogger(),
	    'progress_hooks': [my_hook],
        'verbose': True,
        'keep-fragments': True
	}

	url = 'http://v.youku.com/v_show/id_XNzE1NTk3Mzky.html' # 'https://www.youtube.com/watch?v=pqmcEGhaWPs'

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    result = ydl.download([url])

	# with open ('file.mp4', 'w') as fd:
	#     mystdout.seek (0)
	#     shutil.copyfileobj(mystdout, fd)

	
	# print(mystdout.getvalue())


if __name__ == '__main__':
	downloader()
