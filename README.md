### 微信企业号、订阅号、服务号 python sdk ###

使用方法, 以服务号为例：
    
    from basic import Wechat

    wechat_mp = Wechat(domain="api.weixin.qq.com", uri_parts=('cgi-bin',))

    # 获取 access token
    data = {'grant_type': 'client_credential', 'appid': appid, 'appsecret': appsecret}
    wechat_mp.token(http_method='get', data=data)

    # 获取