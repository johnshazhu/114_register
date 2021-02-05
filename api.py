import json
import sys
import urllib.request
import urllib.parse
import time
import ssl
from threading import Timer

config_dict = {}
# smsCode 2 => 不需要验证码
# smsCode 4 => 需要验证码


def load_config_info():
    with open('data/config.property', 'r') as f:
        global config_dict
        for line in f.readlines():
            line = line.strip()
            if not len(line):
                continue
            key = line.split('=')[0]
            config_dict[key] = str(line)[(len(key) + 1):]
        return config_dict


def api_call(url, query=None, post_data=None):
    try:
        if query is None:
            query = {}
        if isinstance(query, dict):
            query['_time'] = int(round(time.time() * 1000))

        param = urllib.parse.urlencode(query)
        req = urllib.request.Request(url + '?%s' % param, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 2 XL Build/RP1A.201005.004.A1; wv) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile '
                          'Safari/537.36 MMWEBID/3643 MicroMessenger/7.0.17.1701(0x27001141) Process/tools '
                          'WeChat/arm64 GPVersion/1 NetType/WIFI Language/zh_CN ABI/arm64',
            'Content-Type': 'application/json;charset=UTF-8',
            'X-Requested-With': 'com.tencent.mm',
            'Request-Source': 'WE_CHAT',
            'Referer': 'https://www.114yygh.com/wechat/nuclein',
            'Cookie': config_dict['cookie']
        })
        req.data = post_data
        res = urllib.request.urlopen(req, timeout=5)
        res_content = res.read()
        # print(res_content)
        rsp = json.loads(res_content, encoding='utf-8')
        return rsp
    except Exception as ex:
        print(sys.stderr, 'api_call ex : ', ex)
        return None


def is_success_response(resp):
    if isinstance(resp, dict):
        if 'resCode' in resp and resp['resCode'] == 0:
            if 'data' in resp and resp['data'] is not None:
                return True
    return False
