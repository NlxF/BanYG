import time
import uuid
import gevent
import http.cookiejar as cookiejar
from urllib.parse import quote
from flask import Response
from gevent.queue import Queue, Empty
from bwg360.util.translation_utils import gettext as _
from flask_user import current_user
from youtube_dl import YoutubeDL
from bwg360.models.download import DownloadStatus
from bwg360.util.utils import generate_crc_number, is_free_download, get_download_speed, update_cookies
from bwg360.controllers.dlFiles.baseDL import BaseDL
from youtube_dl.utils import UnsupportedError, DownloadError
from bwg360.util.mycache import minus_free_download_size, set_free_download_flag, get_file_size_of_format_id


ydl_opts = {'outtmpl': 'tmp/%(id)s.%(ext)s',
            'keep_fragments': True,
            # 'retries': 3,
            # 'buffersize': 10240,
            'progress_hooks': [],
            'verbose': False,
            'quiet': True,
            }


def _progress_hook(queue, dl_status):
    previous = 0
    fragment_index = 1
    # file_exist = False

    # inner hook
    def inner_hook(status_dict):
        nonlocal previous
        nonlocal fragment_index
        # nonlocal file_exist
        is_sync = False

        if status_dict['status'] == 'error':
            dl_status.status = 3
            is_sync = True
        if status_dict['status'] == 'downloading':
            dl_status.status = 1
            dl_status.current_size = status_dict['downloaded_bytes']
            if "fragment_index" in status_dict and status_dict['fragment_index'] == fragment_index:
                dl_status.filename = status_dict['filename']
                dl_status.fragment_index = status_dict['fragment_index']
                dl_status.current_size /= (1024 * 1024)                                    # convert byte to MB
                fragment_index += 1                                                        # 指向下一 fragment
                is_sync = True
            elif "fragment_index" not in status_dict and dl_status.current_size > 1024*20:      # 等待写入磁盘后再读取
                # if not file_exist:
                #     file_exist = file_size(status_dict['tmpfilename']) > 1024*20
                # if file_exist:
                dl_status.filename = status_dict['tmpfilename']
                dl_status.length = dl_status.current_size - previous
                dl_status.start_position = previous
                previous = dl_status.current_size
                is_sync = True
        elif status_dict['status'] == 'finished':
            print('Done download with total')
            dl_status.status = 2
            dl_status.total_size = status_dict['total_bytes'] / (1024 * 1024)              # convert byte to MB
            is_sync = True                                                                 # send的 status_dict 为结束状态

        if is_sync:
            print('fire in the hole')
            queue.put(dl_status)
            gevent.sleep(0)

    return inner_hook


class MyYoutubeDL(YoutubeDL):
    """custom YoutubeDL for cookie load issue when expires is 0"""
    def __init__(self, params=None, auto_init=True):
        super(MyYoutubeDL, self).__init__(params, auto_init)

    def _set_expires(self):
        for cookie in self.cookiejar:
            # set cookie expire date to 14 days from now
            cookie.expires = time.time() + 14 * 24 * 3600

    def _setup_opener(self):
        super(MyYoutubeDL, self)._setup_opener()

        if isinstance(self.cookiejar, cookiejar.MozillaCookieJar):
            self.cookiejar.load(ignore_expires=True)
            self._set_expires()


class YoutubeDL(BaseDL):
    def __init__(self, video_url):
        super().__int__(need_browser=False)
        self.video_url = video_url
        self.fmt_list = []

    def _parse_video_format(self, fmts):
        self.fmt_list.clear()
        for fmt in fmts.get('formats'):
            one = dict(file_title=fmts.get('title').strip())
            one['file_ext']       = fmt.get("ext")
            if 'filesize' in fmt:
                one['file_size']  = fmt.get('filesize') / (1024 * 1024) + 1  # filesize is in byte, convert byte to MB
            one['file_format']    = fmt.get('format')
            one['file_format_id'] = fmt.get('format_id')
            self.fmt_list.append(one)
        return self.fmt_list

    def fetch_url_details(self):
        # 返回url信息
        return self.errMsg if self.errMsg else self.fmt_list

    def is_support(self):
        """测试youtube-dl是否支持指定的video_url"""
        ydl_opts_inner = {
            'verbose': False,
            'socket_timeout': 3,
        }
        try:
            # update_cookies(ydl_opts_inner)
            with MyYoutubeDL(ydl_opts_inner) as ydl:
                info_dict = ydl.extract_info(self.video_url, download=False, ie_key=None)
                return self._parse_video_format(info_dict)
        except Exception as exc:
            if isinstance(exc, UnsupportedError):
                return False
            elif isinstance(exc, DownloadError):
                self.errMsg = exc.args[0]                           # 客户端无权播放
                return True

    def response_data_generator(self, queue):
        while True:
            recv_data = queue.get()  # 调试的时候不设超时，生产需要超时机制
            if isinstance(recv_data, DownloadStatus):  # 接收到的为状态数据
                dl_status = recv_data

                """0：未下载; 1: 正在下载; 2: 下载完成; 3: 下载出错"""
                if dl_status.status == 3:
                    print('recv youtube-dl error message')
                    return  # recv error return to stop generator
                elif dl_status.status == 1:
                    if dl_status.fragment_index > 0:
                        index = dl_status.fragment_index - 1
                        file_nto_read = "{}.part-Frag{}".format(dl_status.filename, index)
                        with open(file_nto_read, 'rb') as f:
                            yield f.read()
                    else:
                        file_nto_read = dl_status.filename
                        with open(file_nto_read, 'rb') as f:
                            f.seek(dl_status.start_position, 0)
                            yield f.read(dl_status.length)
                elif dl_status.status == 2:
                    print('DownloadStatus total download:%d' % dl_status.total_size)
                    return  # download finished return to stop generator
            else:
                print('youtube-dl occur an error at sub-process: {}'.format(recv_data))
                return

    def download_work(self, format_id, queue, dl_status):
        try:
            dir_name = str(uuid.uuid1())
        except ValueError as e:
            dir_name = generate_crc_number(32)

        limit = get_download_speed(current_user)                       # 下载限速
        ydl_opts.update({
            'format'    : format_id,
            'outtmpl'   : 'tmp/{}/%(id)s.%(ext)s'.format(dir_name),    # 下载临时目录
            "ratelimit" : limit,
            'progress_hooks': [_progress_hook(queue, dl_status)],
        })
        # update_cookies(ydl_opts)
        you_dl = MyYoutubeDL(ydl_opts)
        try:
            print('start downloading......')
            you_dl.download([self.video_url])                       # 阻塞函数，直到下载完毕后才会下一步
        except Exception as e:
            queue.put(e)

    def start_downloads(self, format_id, file_detail, user_info):
        """开始下载"""
        queue = Queue()                                             # 队列, 用来传递 status
        ext   = file_detail['file_ext']
        title = file_detail['file_title']
        dl_status = DownloadStatus()                                # 用于同步当前下载状态
        dl_status.url = self.video_url
        dl_status.title = title
        gl = gevent.spawn(self.download_work, format_id, queue, dl_status)
        try:
            rst = queue.peek(timeout=15)                            # switch to gl
            if isinstance(rst, DownloadStatus):
                content_type = self.get_content_type(ext)
                file_name = '{}.{}'.format(title, ext)
                resp = Response(self.response_data_generator(queue), content_type=content_type)
                resp.headers["Content-Disposition"] = "attachment; filename={}".format(quote(file_name.encode('utf-8')))
                resp.call_on_close(self.on_close(gl, dl_status, user_info))

                # 免费额度在开始下载就扣除，不等下载完毕
                if is_free_download(current_user):  # current_user.is_anonymous or current_user.brick <= 0:
                    info = current_user, user_info[1], user_info[-1]
                    set_free_download_flag(info)
                    size = get_file_size_of_format_id(self.video_url, format_id)
                    if size > 0:
                        minus_free_download_size(size)                              # 扣除免费额度

                return resp
            elif isinstance(rst, Exception):
                print("request occur exception:{}".format(rst))
                gl.kill()                                            # close greenlet
                return _("request occur exception")                  # 请求发生异常
            else:
                print("youtube-dl occur an unknown error")
                gl.kill()                                            # close greenlet
                return _("unknown error")                            # 未知异常
        except Empty:
            print("request timeout with url:{0}".format(self.video_url))
            gl.kill()                                  # close greenlet
            return _("request timeout")                # 请求超时

