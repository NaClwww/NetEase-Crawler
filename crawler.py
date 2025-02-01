import requests
from bs4 import BeautifulSoup
import time
import random
import json
from Crypto.Cipher import AES
import base64
import codecs
import qrcode

# 获取一个随意字符串，length是字符串长度
def generate_str(lenght):
    str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    str = list(str)  # 将字符串转换为列表
    res = ''
    for i in range(lenght):
        res = res + random.choice(str)  # 累加成一个随机字符串
    return res

# AES加密获得params
def AES_encrypt(text, key):
    iv = '0102030405060708'.encode('utf-8')  # iv偏移量
    text = text.encode('utf-8')  # 将明文转换为utf-8格式
    pad = 16 - len(text) % 16
    text = text + (pad * chr(pad)).encode('utf-8')  # 明文需要转成二进制，且可以被16整除
    key = key.encode('utf-8')  # 将密钥转换为utf-8格式
    encryptor = AES.new(key, AES.MODE_CBC, iv)  # 创建一个AES对象
    encrypt_text = encryptor.encrypt(text)  # 加密
    encrypt_text = base64.b64encode(encrypt_text)  # base4编码转换为byte字符串
    return encrypt_text.decode('utf-8')

# RSA加密获得encSeckey
def RSA_encrypt(str, key, f):
    str = str[::-1]  # 随机字符串逆序排列
    str = bytes(str, 'utf-8')  # 将随机字符串转换为byte类型的数据
    sec_key = int(codecs.encode(str, encoding='hex'), 16) ** int(key, 16) % int(f, 16)  # RSA加密
    return format(sec_key, 'x').zfill(256)  # RSA加密后字符串长度为256，不足的补x

# 获取参数
def get_params(d):
    e = '010001'
    f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    g = '0CoJUm6Qyw8W8jud'
    i = generate_str(16)    # 生成一个16位的随机字符串
    # i = 'aO6mqZksdJbqUygP'
    encText = AES_encrypt(d, g)
    # print(encText)    # 打印第一次加密的params，用于测试d正确
    params = AES_encrypt(encText, i)  # AES加密两次后获得params
    encSecKey = RSA_encrypt(i, e, f)  # RSA加密后获得encSecKey
    return params, encSecKey

def get_unikey():
    url = 'https://music.163.com/weapi/login/qrcode/unikey'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    data = {
        "type": "1"
        }

    d = json.dumps(data)

    params, encSecKey = get_params(d)

    response = requests.post(url, headers=headers, data={'params': params, 'encSecKey': encSecKey})

    res = response.json()

    print(res)

    return res.get('unikey')

def show_qrcode(unikey):
    # 提取您想要转成二维码的字段，比如 token
    data = "http://music.163.com/login?codekey=" + unikey

    # 生成二维码
    qr = qrcode.QRCode(
        version=1,  # 设置二维码的版本
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 设置错误修正级别
        box_size=10,  # 每个格子的像素大小
        border=4,  # 边框的大小
    )
    qr.add_data(data)
    qr.make(fit=True)

    # 创建二维码图像
    img = qr.make_image(fill="black", back_color="white")
    img.save("qrcode.png")
    img.show()

def login():
    unikey=get_unikey()
    show_qrcode(unikey)
    print("等待扫码")
    while(True):
        res,headers=checking_login(unikey)
        if res['code']==803:
            print("二维码已失效")
            break
        elif res['code']==800:
            print("扫码成功")
            break
        else:
            time.sleep(0.5)
    print(headers)
    return headers['set-cookie']

def checking_login(unikey):
    url = 'https://music.163.com/weapi/login/qrcode/client/login?csrf_token='
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0',
    'Referer': 'https://music.163.com/',
    'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data = {
        "csrf_token": "",
        "key": unikey,
        "type": "1"
        }

    d = json.dumps(data)

    params, encSecKey = get_params(d)
    response = requests.post(url, headers=headers, data={'params': params, 'encSecKey': encSecKey})

    res_headers = response.headers

    res_body = response.json()

    return res_body,res_headers


def get_list_info(list_id,cookie):
    url = f'https://music.163.com/api/playlist/detail?id={list_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3','cookie':cookie}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = response.json()
    return data

def get_song_id(list_id,cookie):
    print("getting song id")
    list_info = get_list_info(list_id,cookie)
    while(list_info['code']!=200):
        print(list_info)
        print(list_info['code'])
        time.sleep(0.5)
        list_info = get_list_info(list_id,cookie)
    playlist = list_info['result']['tracks']
    print(f'find {len(playlist)} songs')
    with open('MusicId.txt', 'w') as f:
        for i in playlist:
            f.write(str(i["id"])+"\n")
    print("done")

if __name__ == "__main__":
    try:
        with open('cookie.txt', 'r') as cookie:
            user_cookie = cookie.read()
    except FileNotFoundError:
        user_cookie = ''

    if user_cookie == '':
        user_cookie = login()
        with open('cookie.txt', 'w') as cookie:
            cookie.write(user_cookie)

    list_id = '2681578911'
    print("cookie:", user_cookie)
    user_cookie = user_cookie.split(';')
    u_cookie = max(cookie for cookie in user_cookie if 'MUSIC_U' in cookie)
    u_cookie = u_cookie.split(',')[1].strip()
    print(type(u_cookie))
    get_song_id(list_id, u_cookie)