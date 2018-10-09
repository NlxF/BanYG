# -*- coding: utf-8 -*-

import os
import pickle
import shutil
from io import BytesIO
from io import StringIO
from PIL import Image
from datetime import datetime
from urllib import request
from bwg360 import db, app
from bwg360.models.user import User
from bwg360.models.download import DownloadRecord
from bwg360.util import platform_, string_types
from bwg360.util.utils import is_free_download, adblock_plus_path
from bwg360.util.mycache import minus_free_download_size, set_free_download_flag
from pytesseract import image_to_string
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from seleniumrequests import PhantomJS, Chrome
from selenium.common.exceptions import NoSuchElementException


_cookies_suffix = "_cookies.pkl"

ext_type = {'avi' : 'video/avi',      'm1v': 'video/x-mpeg',       'm2v': 'video/x-mpeg',
            'm4e' : 'video/mpeg4',  'movie': 'video/x-sgi-movie', 'mp2v': 'video/mpeg',
            'mp4' : 'video/mpeg4',    'mpa': 'video/x-mpg',        'mpe': 'video/x-mpeg',
            'mpeg': 'video/mpg',      'mpg': 'video/mpg',          'mps': 'video/x-mpeg',
            'mpv' : 'video/mpg',     'mpv2': 'video/mpeg',          'rv': 'video/vnd.rn-realvideo',
            'wm'  : 'video/x-ms-wm',  'wmv': 'video/x-ms-wmv',     'wmx': 'video/x-ms-wmx',
            'wvx' : 'video/x-ms-wvx', 'asf': 'video/x-ms-asf',     'asx': 'video/x-ms-asf',
            'IVF' : 'video/x-ivf',   'html': 'text/html',          'cml': 'text/xml',
            'css' : 'text/css'
            }


class BwgException(Exception):
    def __init__(self, message, errors):
        super(BwgException, self).__init__(message)
        self.errors = errors

    def __repr__(self):
        return ""


class BaseDL(object):

    _browser = None
    WAIT_TIME = 10

    def __int__(self, need_browser=True):

        self.url = ""
        self.errMsg = ""
        self.url_netloc = ""
        self.login_page = ""
        self.flags = {}
        self.element_xpath = {}
        if need_browser:
            if not type(self)._browser:
                self.browser = self._create_browser_with_extension()
                type(self)._browser = self.browser
            else:
                self.browser = type(self)._browser

    def _create_browser_with_extension(self):
        # 加载本地插件
        # self.browser = webdriver.PhantomJS()
        # self.browser = PhantomJS()
        # self.browser.set_window_size(1120, 550)

        chrome_options = Options()
        chrome_options.add_extension(adblock_plus_path())
        driver = Chrome(chrome_options=chrome_options)
        driver.start_client()

        return driver

    def save_session(self):
        # 保存 Cookies
        pickle.dump(self.browser.get_cookies(), open(self.url_netloc+_cookies_suffix, "wb"))

    def get_session(self):
        # 载入 Cookies, Phantomjs保存完Cookies可能存在无法加载的情况
        try:
            cookies = pickle.load(open(self.url_netloc+_cookies_suffix, "rb"))
        except FileNotFoundError as e:
            return None
        return cookies

    def load_session(self, cookies):
        for cookie in cookies:
            self.browser.add_cookie(cookie)

    def validata_session(self):
        cookies = self.get_session()
        if cookies:
            self.load_session(cookies)
            self.browser.request('GET', self.url_netloc)

            is_login = self._check_login_status()
            return is_login

        return False

    def _check_login_status(self):
        # 检测登陆状态
        try:
            welcome = self.browser.find_element_by_xpath(self.element_xpath["logged"])
            is_login = True
        except NoSuchElementException as e:
            is_login = False
        return is_login

    def check_vip(self):
        # 检测是否高级会员
        pass

    def login(self, username="", password=""):
        # 访问登陆页
        self.browser.get(self.login_page)
        login_btn = self.browser.find_element_by_xpath(self.element_xpath['login_btn'])
        if not login_btn or login_btn.text not in self.flags["home"]:
            return False    # 登陆页访问失败

        # 填写邮箱与密码登陆
        self.browser.find_element_by_xpath(self.element_xpath['user']).send_keys(username)
        self.browser.find_element_by_xpath(self.element_xpath['pswd']).send_keys(password)
        login_btn.submit()
        self.browser.implicitly_wait(self.WAIT_TIME)

        is_login = self._check_login_status()

        return is_login

    def get_picture(self):
        # 获取图片验证码路径
        pass

    def get_content_type(self, ext):
        # 根据后缀，返回下载资源的类型
        default = 'application/octet-stream'
        try:
            ext = ext.lower()
            return ext_type.get(ext, default)
        except Exception as e:
            return default

    def _verifity_code(self, img_base64):
        # 根据图片获取验证码
        imgBuf = BytesIO(img_base64)             # 用BytesIO直接使用字节码
        img = Image.open(imgBuf)                 # PIL库加载图片
        # print(img.format, img.size, img.mode)  # 打印图片信息

        # img = img.convert('L')                   # 将彩色图像转化为灰度图
        #
        # def init_table(threshold=95):                 # 阈值设置为95
        #     table = []
        #     for i in range(256):
        #         if i < threshold:
        #             table.append(0)
        #         else:
        #             table.append(1)
        #
        #     return table
        # binary_image = img.point(init_table(), '1')   # 将灰度图二值化

        img = img.convert('RGBA')     # 转换为RGBA
        pix = img.load()              # 读取为像素
        # for x in range(img.size[0]):  # 处理上下黑边框
        #     pix[x, 0] = pix[x, img.size[1] - 1] = (255, 255, 255, 255)
        # for y in range(img.size[1]):  # 处理左右黑边框
        #     pix[0, y] = pix[img.size[0] - 1, y] = (255, 255, 255, 255)
        for y in range(img.size[1]):  # 二值化处理，这个阈值为R=95，G=95，B=95
            for x in range(img.size[0]):
                if pix[x, y][0] < 95 or pix[x, y][1] < 95 or pix[x, y][2] < 95:
                    pix[x, y] = (0, 0, 0, 255)
                else:
                    pix[x, y] = (255, 255, 255, 255)
        binary_image = img
        # binary_image.show()

        path = '/Users/ism/projects/py/bwg360/pic/foo.png'
        binary_image.save(path)

        code_text = image_to_string(binary_image, lang='eng.font.exp0', config='-psm 7')

        return code_text

    @classmethod
    def delete_temporary_resource(cls, filename):
        if not isinstance(filename, string_types) or len(filename) <= 0:
            return

        tmp_path = os.path.join(os.path.dirname(app.root_path), os.path.dirname(filename))

        shutil.rmtree(tmp_path, ignore_errors=True)

    @classmethod
    def on_close(cls, gl, dl_status, user_info):
        """
        :param gl:
        :param dl_status:
        :param user_info: (username, fppkcookie, ip)
        :return:
        """
        def _close():
            if gl.started:
                username, fp, ip = user_info
                user = None if username == 'anonymous' else User.query.filter(User.username == username).first()
                file_size = (int(dl_status.total_size) + 1)
                download_record_class = DownloadRecord.model()
                dr = download_record_class(url=dl_status.url, title=dl_status.title,
                                           ip=ip, fp=fp, username=username, size=file_size)
                dr.is_free = True if is_free_download(user) else False
                if user:
                    dr.user_id = user.id
                if dl_status.status == 2:
                    print("close greenlet:{0} due to normal end!".format(gl))
                    if not is_free_download(user):
                        # 免费下载额度在开始下载就已经扣除，这里不再记扣
                        # 充值用户扣除，向上取整
                        user.brick -= file_size
                        db.session.add(user)
                    dr.is_complete = True
                else:
                    # 下载失败充值用户不会减少额度；
                    # 免费额度在开始时已扣除
                    print("close greenlet:{0} due to some error!.".format(gl))
                    dr.is_complete = False
                db.session.add(dr)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()

                # 删除临时文件
                cls.delete_temporary_resource(dl_status.filename)

                gl.kill()

            print("set client close event")

        return _close

    def fetch_url_details(self):
        pass

    def response_data_generator(self, arg_queue):
        pass

    def start_downloads(self, format_id, title, ext):
        # 开启下载 #
        # needed_login = False
        if not self.validata_session():  # 当前登录状态是否有效
            # needed_login = True
            if not self.login():         # 尝试登录
                return False             # 登录失败

        # if needed_login:
        self.browser.get(self.url)
        try:
            wait = WebDriverWait(self.browser, 10)
            element = wait.until(
                expected_conditions.element_to_be_clickable((By.XPATH, self.element_xpath['click_btn'])))
            # element = self.browser.find_element_by_xpath(self.element_xpath['click_btn'])
            element.click()
        except:
            pass

        file_name = self.browser.title  # 下载的文件名
        if self.check_vip():  # 是否高级会员
            pass
        else:
            self.browser.switch_to.window(self.browser.window_handles[0])
            # self.browser.switch_to.window(file_name)

        img = self.get_picture()
        code = self._verifity_code(img_base64=img)
        print(code)
        input_code = self.browser.find_element_by_xpath(self.element_xpath['input_code'])
        input_code.send_keys(code)

        self.browser.implicitly_wait(30)  # 等待30s

        download_btn = self.browser.find_element_by_xpath(self.element_xpath['download_btn'])
        download_btn.click()

        video_url = ""
        self.download_work(video_url, file_name)

    def download_work(self, *args, **kwargs):
        pass

    def __del__(self):
        pass
        # self.browser.quit()


