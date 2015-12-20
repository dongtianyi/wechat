# -*- coding: utf-8 -*-

import hashlib
import logging
import requests

from logging.config import fileConfig
fileConfig('log.conf')
logger = logging.getLogger(__name__)

'''
递归动态生成可调用的类方法。
修改的时候注意三个地方：
父类：WechatCall.__init__ 
子类：Wechat.__init__
父类中的 __call__

使用例子：
wechat_basic = Wechat(domain=domain, uri_parts=('cgi-bin',), secure=False)
wechat_basic.wechat_basic.token(grant_type='client_credential', appid=appid, appsecret=appsecret)

其中发生的事情：
阶段一：初始化 Wechat 的时候
    1 Wechat首先执行初始化函数 __init__
    2 Wechat在初始化函数里执行了 WechatCall 的初始化函数 __init__
阶段二：调用 wechat_basic.wechat_basic.token（可以递归调用 wechat_basic.wechat_basic.token.xxx.xxx.yyy）
    1 由于父类 WechatCall 为可调用函数，执行父类的 动态属性 查找器 __getattr__ 
    2 在父类的 __getattr__ 中递归调用了父类本身，如果属性查找请求继续，那么将会递归调用 __getattr__ 知道属性查找完成
'''

ALLOWED_HTTP_METHOD = ('get', 'post', 'head', 'options', 'put', 'delete')

class WechatException(Exception):
    """
    微信 base Error
    """
    pass


class HttpMethodNotAllowedException(Exception):
    """
    微信 请求方法不允许
    """
    def __str__(self):
        message = 'http方法不允许'
        return (message)


def build_uri(orig_uriparts, kwargs):
    '''
    使用参数生成url, Modifies kwargs.
    kwargs 里面的参数不在这里面生成 uri，这个参数将会作为 requests的参数传入get or post
    如果有的 api 需要使用 kwargs里面的参数，在这里进行特殊处理
    '''
    # import pdb; pdb.set_trace()
    uri_parts = []
    for uri_part in orig_uriparts:
        # If this part matches a keyword argument (starting with _), use
        # the supplied value. Otherwise, just use the part.
        if uri_part.startswith("_"):
            part = (str(kwargs.pop(uri_part, uri_part)))
        else:
            part = uri_part
        uri_parts.append(part)
    uri = '/'.join(uri_parts)
    # import pdb; pdb.set_trace()
    # If an id kwarg is present and there is no id to fill in in
    # the list of uriparts, assume the id goes at the end.
    # id = kwargs.pop('id', None)
    # if id:
    #     uri += "/%s" % (id)
    return uri

def check_http_method(http_method):

    if http_method.lower() in ALLOWED_HTTP_METHOD:
        return True 
    else:
        raise HttpMethodNotAllowedException


class WechatCall(object):
    '''
    目的：发送http请求到一个URL
    1 生成 url  
    2 发送 get or post 
    3 处理 response

    python动态语言和业务逻辑抽象
    1 生成 url 
    2 决定 get 或者 post 
    3 处理 response

    编成风格借鉴自：https://github.com/sixohsix/twitter/blob/master/twitter/api.py
    '''

    def __init__(
        self, domain, callable_cls, uri_parts=None,
        secure=True, timeout=None, retry=False, is_test=False):
        self.domain = domain
        self.callable_cls = callable_cls
        # self.uri = uri
        self.uri_parts = uri_parts
        self.timeout = timeout
        self.retry = retry
        self.secure = secure
        self.is_test = is_test
        # logger.info(appid)
        # logger.info(appsecret)

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            # 递归调用，查找属性，每次的调用都将属性值作为一个参数存入 uri_parts
            def extend_call(arg):
                return self.callable_cls(
                    domain=self.domain, 
                    callable_cls=self.callable_cls,
                    uri_parts=self.uri_parts + (arg,),
                    secure=self.secure,
                    timeout=self.timeout, 
                    retry=self.retry,
                    is_test=self.is_test)
            # 以 _ 开头的键值对，只保留 value，忽略掉 key
            if k == "_":
                return extend_call
            else:
                return extend_call(k)



    def __call__(self, http_method='get', data={}, **kwargs):
        '''
        使父类成为可调用类
        '''
        uri = build_uri(self.uri_parts, kwargs)
        # logger.info(uri)
        domain = self.domain
        lower_http_method = http_method.lower()
        # 检查是否使用 https
        secure_str = ''
        if self.secure:
            secure_str = 's'
        # dot = ""
        # import pdb; pdb.set_trace()
        url_base = "http%s://%s/%s" % (secure_str, domain, uri)
        check_http_method(lower_http_method)
        # params: 展开所有的参数：
            # payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
            # ?key1=value1&key2=value2&key2=value3
        # re = getattr(requests, lower_http_method)(url_base, params=kwargs)
        # data：  send some form-encoded data — much like an HTML form
        if self.is_test:
            return (url_base, data)
        else:
            re = getattr(requests, lower_http_method)(url_base, data=data)
            return re.json()
        # json: send json data
        # re = getattr(requests, lower_http_method)(url_base, json=kwargs)
        # import pdb; pdb.set_trace()


class Wechat(WechatCall):

    def __init__(
        self, domain, secure=True, uri_parts=(), 
        timeout=None, retry=False, is_test=False):
        '''
        @secure: 是否使用 https
        @domain: api域名
        @retry : 是否重试，有两种格式 1 int 重试次数 2 bool 一直重试，直到成功
        @uri_parts: 默认添加的 url路径不属于 domain部分：
            例如 api.weixin.qq.com/cgi-bin/ 每个url 里面都含有 cgi-bin
        @is_test: 执行测试的时候传入这个参数
        '''
        # uri_parts = ()
        WechatCall.__init__(
            self, domain=domain, callable_cls= WechatCall, 
            uri_parts=uri_parts, secure=secure, timeout=timeout, retry=retry, is_test=is_test)


__all__ = ["Wechat", "WechatCall"]