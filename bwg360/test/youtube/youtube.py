import os
import sys
import time
import uuid
import logging
import multiprocessing
from datetime import datetime
from flask import Flask, request, redirect, url_for
from flask import stream_with_context, Response
from flask import render_template_string
from youtube_dl import YoutubeDL

FORMAT = '%(message)s'
logging.basicConfig(filename='logger.log', level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger('uwsgi-server')
# logger.warning('Protocol problem: %s', 'connection reset')


def printLog(message, *args, **kwargs):
    message = '{1}|process id: {0}|{2}\r\n'.format(os.getpid(), datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), message)
    # print(message, *args, **kwargs)
    logger.debug(message, *args, **kwargs)


# 打印进程信息,用于调试
def process_info():
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


def start_test(q, x):
    printLog('multi process start, recv: {0}'.format(x))
    time.sleep(2.0)
    printLog("multi process stop!!!")
    q.put(x+1)


def start_test2(x):
    printLog('multi process start, recv: {0}'.format(x))
    time.sleep(2.0)
    printLog("multi process stop!!!")
    return x + 1


def data_generator():
    for i in range(10):
        yield str(i)
        time.sleep(3.0)


# -----------------------------youtube-dl-------------------------------
class MyLogger(object):
    def debug(self, msg):
        # printLog('Debug message: ' + msg)
        pass

    def warning(self, msg):
        printLog('Warning message: ' + msg)

    def error(self, msg):
        printLog('Error message: ' + msg)


def progress_hook(pipe):
    fragment_index = 1
    
    # inner hook
    def inner_hook(status_dict):
        nonlocal fragment_index
        isSync = False
        if status_dict['status'] == 'error':
            isSync = True
        elif status_dict['status'] == 'downloading':
            # printLog('downloading...|inner index: {0}'.format(status_dict['fragment_index']))
            if status_dict['fragment_index']==fragment_index and fragment_index!=status_dict['fragment_count']:
                isSync = True
        elif status_dict['status'] == 'finished':
            printLog('Done download with total index: {0}'.format(fragment_index))
            isSync = True                                # send的 status_dict 为结束状态,此时的fragment_index指向当前data段
            status_dict['fragment_index'] = fragment_index

        if isSync:
            # 当父进程因为poll()超时或client主动关闭连接而导致stream transport结束, 父进程端的Pipe会被close。
            # 此时再send()就会抛出[Errno 32] Broken pipe异常
            printLog('fire in the hole')
            fragment_index = fragment_index + 1   # 指向下一data段
            pipe.send(status_dict)

            # 监听客户端是否断开连接            
            # if not event.is_set():
            #     printLog('fire in the hole')
            #     fragment_index = fragment_index + 1   # 指向下一data段
            #     pipe.send(status_dict)  
            # else:
            #     printLog("Client disconnect!!!")

    return inner_hook


ydl_opts = {'outtmpl': 'tmp/%(id)s.%(ext)s',
            'keep_fragments': True,
            'retries': 3,
            'logger': MyLogger(),
            'progress_hooks': [],
            'verbose': False,
            'quiet': True,
            }


def start_download(video_url, pipe):
    printLog('start downloading...')
    #printLog('Child pipe count is: {0}'.format(sys.getrefcount(pipe)))
    dir_name = str(uuid.uuid1())                      # 下载临时目录
    ydl_opts.update({
        'outtmpl': 'tmp/'+dir_name+'/%(id)s.%(ext)s',
        'progress_hooks': [progress_hook(pipe)]
    })
    youDLer = YoutubeDL(ydl_opts)

    try:
        youDLer.download([video_url])                 # 阻塞函数，直到下载完毕后才会下一步
    except Exception as e:
        printLog('youtube-dl occure exception')
        pipe.send(e)                                  # 发送异常
        time.sleep(0.1)                               # 等待接收
    finally:
        printLog('finally close child pipe.')         # 不管是因为异常还是正常结束, 都关闭子进程端的管道
        pipe.close()


# -------------------------------multiprocessing-----------------------------
# 定义一个进程池
pool = multiprocessing.Pool(processes=1)
# manager = multiprocessing.Manager()

# ------------------------------------flask----------------------------------
app = Flask(__name__)


def on_close():
    printLog("set client close event")
    

@app.route('/')
@app.route('/home')
def home():
    # youtube https://www.youtube.com/watch?v=AyLWeiJOdyw
    btn = '''<form method="post" action="/download?url=http://v.youku.com/v_show/id_XMzAyMzk2NzkxNg==.html?spm=a2hww.20023042.m_226600.5~5!2~5~5~5~5~A&f=49716696">
                <button type="submit">Download!</button>
             </form>'''
    return render_template_string(btn)


@app.route('/download', methods=['GET', 'POST'])
def stream_data():
    printLog('kwargs: {0}'.format(request.args))
    dl_url = request.args.get('url')
    # printLog('download url: {0}'.format(dl_url))
    if dl_url:
        # event = manager.Event()                            # 客户端关闭链接事件
        # printLog('prepare to download')
        parent_conn, child_conn = multiprocessing.Pipe(False)
        result = pool.apply_async(start_download, args=(dl_url, child_conn))     # 开启子进程下载video                                
        if parent_conn.poll(timeout = 15):                 # 尝试拉取数据
            child_conn.close()                             # 在此关闭子进程的写管道，减少引用，又防止过早释放导致传入子进程的写管道为空

            def stream_generate(pipe):                     # 生成器,返回小块的数据
                while pipe.poll(timeout = 15):             # 设置超时时间太短在网速慢的情况下会造成传输中断(>=5),太长又会在有异常后造成并发量大
                    try:
                        recv_data = pipe.recv()            # 接收子进程发送来的数据
                    except EOFError:
                        printLog('Nothing left or the other end was closed')
                        return('Nothing left or the other end was closed')       # 子进程端管道已关闭
                    
                    printLog('recv data from child_conn')
                    if isinstance(recv_data, dict):         # 接收到的为状态数据
                        youDLer_status = recv_data
                        if youDLer_status['status'] == 'error':
                            printLog('recv youtube-dl error message')
                            return 'recv youtube-dl error message'
                        else:
                            index = youDLer_status['fragment_index'] - 1
                            # printLog('recv youtube-dl data with index: {0}'.format(index))
                            file_nto_read = youDLer_status['filename'] + '.part-Frag' + str(index)
                            printLog('send chunk data: {0}'.format(file_nto_read))
                            with open(file_nto_read, 'rb') as f:
                                yield f.read()  
                    elif isinstance(recv_data, Exception):       # 接收到的为异常
                        printLog('an exception occur at sub-process: {0}'.format(recv_data))
                        return 'an exception occur at sub-process'
                    else:
                        printLog('unknow exception occur at sub-process')
                        return 'unknow exception occur at sub-process'
                else:
                    printLog('poll sub-process data timeout')
                    return 'poll sub-process data timeout'
            resp = Response(stream_with_context(stream_generate(parent_conn)), content_type='text/event-stream')
            resp.call_on_close(on_close)
            return resp
        else:
            printLog('poll data timeout')
            return render_template_string("poll data timeout")   # 第一次拉取数据就超时
    else:
        printLog('video url error!')
        return render_template_string('video url error!')        # 参数错误


@app.route('/test/', methods=['GET', 'POST'])
def test_multiprocess():
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=start_test, args=(q, 10))
    p.start()
    
    return render_template_string('test multiprocess {0}'.format(q.get()))


@app.route('/test1/', methods=['GET', 'POST'])
def test_multiprocess2():
    result = pool.apply_async(start_test2, (10,))
    return render_template_string('test1 multiprocess {0}'.format(result.get()))


@app.route('/test2/', methods=['GET', 'POST'])
def test2_multiprocess():
    return render_template_string('test2 response')


@app.route('/test2/', methods=['GET', 'POST'])
def response_yield_test():
    return Response(stream_with_context(data_generator()))


if __name__ == "__main__":
    app.run('0.0.0.0', 5001, True)