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


def show_qrcode(unikey):
    # 提取您想要转成二维码的字段，比如 token
    data = "http://music.163.com/login?codekey=" + unikey

    # 生成二维码
    qr = qrcode.QRCode(
        version=1,  # 设置二维码的版本
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 设置错误修正级别
        box_size=2,  # 每个格子的像素大小
        border=4,  # 边框的大小
    )
    qr.add_data(data)
    qr.make(fit=True)

    # 创建二维码图像
    img = qr.make_image(fill="black", back_color="white")

    ascii_chars = ['█', ' ']
    width, height = img.size
    img = img.resize((width // 2, height // 2))
    pixels = img.load()

    for y in range(height // 2):
        for x in range(width // 2):
            print(ascii_chars[pixels[x, y] == 0], end='')
        print()

def login():
    url = 'https://music.163.com/weapi/login/cellphone'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}



def get_list_info(list_id):
    url = f'https://music.163.com/api/playlist/detail?id={list_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3','cookie':'MUSIC_U=00F16AA467062F2E08CD607249D5407A039BEF704AE78092DFA9164470FC705221D794237972DD5AAD2D92E734393C4C3CC7193263872CF0A98E243F6942DDFC71794E82FF87971B5F2C2044089B943E87611D738DB6122C2D883C3658407DE15A5837D4D5E07149AC4EC1C61E4294FE2E2BEB6A640461702834C77F2C28EE954510457C865D6A79FFC61195984A6F49FDBA10F48AE63F1837335B013F9AF1C391E4D5C0D5F84F2DAB72F61D602F934CA57F5FA5E6632E9757460721920591FC9EE33774F65132EDE9AA04AF8BBA15775FA83D10BED48C3B660011A9D6A39B5EE1E7BF324E5282946C1976F421F9C8443AA99A17C9B6425EAC88F4DAD41136C5D49B054C2F6D4E763541381B57C7A75F450F555D11D71DB9A23019F4941A7A3E4C3DD46CBA1A6204BA155B4BFD235466C7E488F852A960C4861B28C5D540B7CD3EDBCF9E198F006246382FD36CE82FDD8A006194A63E2C6B33C3F508D567F915A9'}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = response.json()
    return data

def get_song_id(list_id):
    print("getting song id")
    list_info = get_list_info(list_id)
    while(list_info['code']!=200):
        print(list_info)
        print(list_info['code'])
        time.sleep(0.5)
        list_info = get_list_info(list_id)
    playlist = list_info['result']['tracks']
    print(f'find {len(playlist)} songs')
    with open('MusicId.txt', 'w') as f:
        for i in playlist:
            f.write(str(i["id"])+"\n")
    print("done")

if __name__ == "__main__":
    show_qrcode("77dc0e20-658d-46eb-a366-ef2dbacad1c6")
