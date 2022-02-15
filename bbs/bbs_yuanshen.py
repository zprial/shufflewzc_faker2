# 米游社-原神签到

import requests
import math
import time
import random
import hashlib
import json
import string
from sendNotify import send

APP_VERSION = '2.3.0'
ACT_ID = 'e202009291139501'
USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
    'miHoYoBBS/{}'.format(APP_VERSION)
REFERER_URL = 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?' \
    'bbs_auth_required={}&act_id={}&utm_source={}&utm_medium={}&' \
    'utm_campaign={}'.format('true', ACT_ID, 'bbs', 'mys', 'icon')


def getHeader(cookie):
    header = {
        'User-Agent': USER_AGENT,
        'Referer': REFERER_URL,
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': cookie
    }
    return header


def getDs():
    md5 = hashlib.md5()
    s = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl'
    t = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = MD5('salt=' + s + '&t=' + t + '&r=' + r)

    ds = t + ',' + r + ',' + c
    # print(ds)
    return ds


def MD5(text: str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


def getInfo(cookie):
    # cookie={
    #     'cookie_token':cookie_token,
    #     'account_id':account_id,
    #     'ltuid':account_id,
    #     '_MHYUUID':MHYUUID,
    #     'ltoken':ltoken,
    #     '_ga':ga,
    #     '_gid':gid
    # }
    print('开始获取登录信息...')
    headers = getHeader(cookie)
    r = requests.get(
        url='https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn', headers=headers)
    u = json.loads(r.text)
    userlist = u['data']['list'][0]
    if not userlist['game_uid']:
        print('信息获取失败，请检查cookie')
    else:
        print('信息获取成功')
        # print(userlist)
        return userlist


def getSignInfo(cookie, userInfo):
    print('获取签到天数...')
    headers = getHeader(cookie)
    r = requests.get(url='https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?region={}&act_id={}&uid={}'.format(
        userInfo['region'], ACT_ID, userInfo['game_uid']), headers=headers)
    u = json.loads(r.text)
    if u['message'] == 'OK':
        print('获取签到天数成功')
        return u['data']
    else:
        print('获取签到天数失败')

# 获取签到奖励列表


def getSignAwards(cookie):
    print('获取签到奖励列表...')
    headers = getHeader(cookie)
    r = requests.get(
        url='https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id={}'.format(ACT_ID), headers=headers)
    u = json.loads(r.text)
    if u['message'] == 'OK':
        print('获取签到奖励列表成功')
        return u['data']
    else:
        print('获取签到奖励列表失败')


def GenShinSign(userlist, cookie):
    uid = userlist['game_uid']
    region = userlist['region']
    region_name = userlist['region_name']
    nickname = userlist['nickname']
    level = userlist['level']
    info = '服务器：'+region_name+'\t当前账号：'+nickname+'\t等级：'+str(level)
    print(info)
    data = {
        'act_id': ACT_ID,
        'region': region,
        'uid': uid
    }
    # print(data)
    header = {
        'Accept': 'application/json, text/plain, */*',
        'DS': getDs(),
        'Origin': 'https://webstatic.mihoyo.com',
        'x-rpc-device_id': 'F8459954-D990-496-A49B-7BA82C0FE3CB',
        'x-rpc-app_version': '2.3.0',
        'x-rpc-client_type': '5',
        "x-rpc-device_id": "F8459954-D990-4961-A49B-7BA82C0FE3CB",
        'User-Agent': USER_AGENT,
        'Referer': REFERER_URL,
        'Accept-Encoding': 'gzip, deflate, br',
        'cookie': cookie
    }
    print('开始签到...')
    req = requests.post(url='https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign',
                        headers=header, data=json.dumps(data, ensure_ascii=False))
    message = json.loads(req.text)

    msg_list = []
    if message['retcode'] == 0:
        msg_list.append('签到成功！')
    elif message['retcode'] == -5003:
        msg_list.append('签到失败!\n旅行者,你已经签到过了')
    else:
        msg_list.append('签到失败!请检查设置')
    rewards = getSignAwards(cookie)
    signInfo = getSignInfo(cookie, userlist)
    reward = rewards['awards'][signInfo['total_sign_day'] - 1]
    msg_list.append(info)
    msg_list.append('今天签到的奖励: ' + reward['name'] + '👑👑👑')
    msg_list.append('累计签到天数：' + str(signInfo['total_sign_day']))
    print('\n'.join(msg_list))
    send('[原神]', '\n'.join(msg_list))


genshinCookies = []


def task_run():
    print('GenShinSign\n共检测到' + str(len(genshinCookies)) + '个账号')
    count = 1
    for i in genshinCookies:
        print('正在进行第' + str(count) + '个账号')
        userlist = getInfo(i)
        GenShinSign(userlist, i)
        count += 1


task_run()
