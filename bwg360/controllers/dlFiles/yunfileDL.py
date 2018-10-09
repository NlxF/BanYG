# -*- coding: utf-8 -*-
import base64
from PIL import Image
from urllib import request, parse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bwg360.controllers.dlFiles.baseDL import BaseDL

_username = "******"
_password = "********"


class YunfileDL(BaseDL):
    def __init__(self, file_url, url_netloc):
        super().__int__()
        self.url = file_url
        self.url_netloc = url_netloc
        self.login_page = "http://www.yunfile.com/view?module=member&action=fallineLogin"
        self.flags = {"home": (u"登录", "Login"),
                      "vip": (u"高级", u"vip")
                      }
        self.element_xpath = {"login_btn": "//button[@id='blue_bt']",
                              "user": "//input[@id='user']",
                              "pswd": "//input[@id='pwd_td']",
                              "logged": "//div[@id='LoginDiv_logged']",
                              "click_btn": "//div[@id='inputDownWait']/input[@class='slow_button']",
                              "image_id": "//img[@id='cvimg2']",
                              "input_code": "//input[@id='vcode']",
                              "download_btn": "//input[@id='slow_button']"
                              }

    def check_vip(self):
        is_vip = False
        try:
            vip = self.browser.find_element_by_xpath("//div[@id='LoginDiv_logged']/span[2]")
            if [x for x in self.flags['vip'] if x in vip.text]:
                is_vip = True
        except NoSuchElementException as e:
            pass
        return is_vip

    def login(self, username=_username, password=_password):
        return super().login(username, password)

    def get_picture(self):

        image_element = self.browser.find_element_by_xpath(self.element_xpath['image_id'])

        # get the captcha as a base64 string
        img_captcha_base64 = self.browser.execute_async_script("""
            var ele = arguments[0], callback = arguments[1];
            ele.addEventListener('load', function fn(){
              ele.removeEventListener('load', fn, false);
              var cnv = document.createElement('canvas');
              cnv.width = this.width; cnv.height = this.height;
              cnv.getContext('2d').drawImage(this, 0, 0);
              callback(cnv.toDataURL('image/jpeg').substring(22));
            }, false);
            ele.dispatchEvent(new Event('load'));
            """, image_element)

        # save the captcha to a file
        # path = '/Users/ism/projects/py/bwg360/pic/foo.png'
        # with open(path, 'wb') as f:
        #     f.write(base64.b64decode(img_captcha_base64))

        return base64.b64decode(img_captcha_base64)

    def download_work(self, video_url, video_name):
        opener = request.FancyURLopener()
        opener.retrieve(video_url, video_name)


if __name__ == '__main__':
    file_url = "http://page2.dfpan.com/fs/3yu0nf3il7ek1or9ea4n41/"
    dl = YunfileDL()
    if dl:
        print("开始下载")
        dl.start_downloads('')
