import time
import subprocess

def start_test():
    rst = []
    cmd = 'curl --connect-timeout {1} -m {2} -X GET -s "127.0.0.1:5001/download?index={0}&url=http://v.youku.com/v_show/id_XMzAyMzk2NzkxNg==.html?spm=a2hww.20023042.m_226600.5~5!2~5~5~5~5~A&f=49716696" -o "dl/file{0}.mp4" '
    for i in range(5):
        cmdstr = cmd.format(i, (i+1)*450, i*450)
        print('start shell with command: ', cmdstr)
        rc = subprocess.Popen(cmdstr, shell=True)
        rst.append(rc)
        # time.sleep(0.1)
        # rc.wait()
        # fileName = 'file{0}.mp4'.format(i)
        # print('{0} finish with md5: '.format(fileName))
        # subprocess.call(['md5sum', 'dl/'+fileName])

    for idx, child in enumerate(rst):
        print('\nWait for child process over...')
        child.wait()
        fileName = 'file{0}.mp4'.format(idx)
        print('{0} finish with md5: '.format(fileName))
        subprocess.call(['md5sum', 'dl/'+fileName])



if __name__ == '__main__':
    start_test()