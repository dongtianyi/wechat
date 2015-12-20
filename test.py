# -*- coding: utf-8 -*-

from basic import Wechat

import unittest

appid = "APPID"
appsecret = 'APPSECRET'
domain = 'api.weixin.qq.com'

class TestWechatBasic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.wechat_basic = Wechat(domain=domain, uri_parts=('cgi-bin',), is_test=True)
        # cls.wechat_basic = Wechat(domain=domain, secure=True)

    def test_url_data(self):
        # https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
        # url = 'https://api.weixin.qq.com/cgi-bin/%s?grant_type=%s&appid=%s&secret=%s'
        self.wechat_basic.secure = True
        url = 'https://api.weixin.qq.com/cgi-bin/token'
        data = {'grant_type': 'client_credential', 'appid': appid, 'appsecret': appsecret}
        re = self.wechat_basic.token(http_method='post', data=data)
        # 检查生成的url和传入参数是否正确
        self.assertEqual(re[0], url)
        self.assertEqual(re[1], data)

    def test_secure(self):
        self.wechat_basic.secure = False
        url = 'http://api.weixin.qq.com/cgi-bin/token'
        data = {'grant_type': 'client_credential', 'appid': appid, 'appsecret': appsecret}
        re = self.wechat_basic.token(http_method='post', data=data)
        # 检查生成的url和传入参数是否正确
        self.assertEqual(re[0], url)
        self.assertEqual(re[1], data)

if __name__ == '__main__':
    unittest.main()