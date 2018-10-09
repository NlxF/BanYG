from youtube_dl import YoutubeDL


def get_info():
    ydl_opts = {'outtmpl': 'tmp/%(id)s.%(ext)s',
            'keep_fragments': True,
            'retries': 3,
            'progress_hooks': [],
            'verbose': False,
            'quiet': True,
            }
    video = "http://v.youku.com/v_show/id_XMzAyMzk2NzkxNg==.html?spm=a2hww.20023042.m_226600.5~5!2~5~5~5~5~A&f=49716696"
    video = "https://www.youtube.com/watch?v=Yc55YdwmEEM"
    video = "http://91porn.com/view_video.php?viewkey=94afcfdbfd4ccf8c41a7"
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video, download=False)
        for k in info_dict.keys():
            print('key:'+str(k)+" value:"+str(info_dict[k]))

if __name__ == '__main__':
    get_info()

    