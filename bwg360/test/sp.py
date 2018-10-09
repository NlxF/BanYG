import subprocess


def call_back():
    print('callBack is called')

if __name__ == "__main__":
    commands = ['youtube-dl', '--keep-fragments', '--output', 'tmp/kj', 'http://v.youku.com/v_show/id_XNzE1NTk3Mzky.html']
    sp = subprocess.Popen(commands, preexec_fn=call_back)
    print('run here')

