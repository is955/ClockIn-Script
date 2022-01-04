from urllib import parse

import pytz
import requests
import base64
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime
import pymysql
from Crypto.Cipher import AES

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

##数据库相关信息
host = ""
port = 3306
user = ""
password = ""
db_name = ""


# 从数据库获取需要打卡的用户。
def getUser():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db_name)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT username,password,email FROM dk_user")
    all_query = cursor.fetchall()
    cursor.close()
    conn.close()
    return all_query


# 登录获取idToken
def login(username, password):
    url = "https://token.huanghuai.edu.cn/password/passwordLogin?username=" + username + "&password=" + password + "&appId=com.lantu.MobileCampus.huanghuai&geo=&deviceId=YAqOUnHhOr0DAFVhHKu599LR&osType=android&clientId=19ad852d696e1e0eb003a8f41712f834"

    header = {
        'Content-Length': '0',
        'Host': 'token.huanghuai.edu.cn',
        'Connection': 'close',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.12.1'
    }
    post = ""
    r = requests.post(url, post, headers=header)
    if 'data' in r.json():
        idToken = r.json()['data']['idToken']
        return idToken
    else:
        return -1


# 获取session,xAuthTokenAAA
def getSession(idToken):
    url2 = "https://yq.huanghuai.edu.cn:7992/cas/studentLogin"
    header2 = {'Host': 'yq.huanghuai.edu.cn:7992',
               'Connection': 'close',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX2121 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045511 Mobile Safari/537.36 SuperApp',
               'Sec-Fetch-Mode': 'navigate',
               'Sec-Fetch-User': '?1',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'usertoken': idToken,
               'x-id-token': idToken,
               'X-Requested-With': 'com.lantu.MobileCampus.huanghuai',
               'Sec-Fetch-Site': 'none',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
               'Cookie': 'userToken=' + idToken + '; Domain=.huanghuai.edu.cn; Path=/'
               }

    req = requests.get(url2, headers=header2, allow_redirects=False)
    # allow_redirects参数为True会自动解析重定向链接，且默认为True，这里我们不能让他解析，以便获取"set-Cookie"。

    setCookie = req.headers['set-Cookie']
    beginIndex = setCookie.find("SESSION=") + 8
    endIndex = setCookie.find(";", beginIndex)
    session = setCookie[beginIndex:endIndex]
    xAuthToken = bytes.decode(base64.b64decode(session))

    # print("session:", session)
    # print("xAuthToken:" + xAuthToken)

    return session, xAuthToken


# 提交问卷信息
def subWenJuan(session, xAuthToken, idToken, phoneNumber, emergencyContactName, emergencyContactPhone,
               stuNumber, area, address, longitude_and_latitude):
    post_data = {
        "recordId": '',
        "zuobiao": longitude_and_latitude,
        "questionnaire": "[{/\"problem_id/\":1,/\"problem_name/\":/\"今日体温/\",/\"result_id/\":null,/\"result_name/\":/\"36.1/\"},{/\"problem_id/\":2,/\"problem_name/\":/\"你当前的身体状况是?/\",/\"result_id/\":2,/\"result_name/\":/\"正常，没有症状/\"}]",
        "record": "{/\"current_area/\":/\"" + area + "/\",/\"current_address/\":/\"" + address + "/\"}",
        "phoneNumber": phoneNumber,
        "emergencyContactName": emergencyContactName,
        "emergencyContactPhone": emergencyContactPhone,
        "student_number": stuNumber
    }

    m_text = str(post_data).replace('\'', '\"').replace('/', '\\')

    aesText = "content=" + parse.quote(aes_encrypt("W0W6jsCj5s9r8mmM", m_text))
    url6 = "https://yq.huanghuai.edu.cn:7992/questionAndAnser/wenjuanSubmit"
    header6 = {
        'Host': 'yq.huanghuai.edu.cn:7992',
        'Connection': 'close',
        'Content-Length': str(len(aesText)),
        'Accept': 'application/json, text/plain, */*',
        'x-auth-token': xAuthToken,
        'Origin': 'https://yk.huanghuai.edu.cn:8993',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX2121 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045511 Mobile Safari/537.36 SuperApp',
        'Sec-Fetch-Mode': 'cors',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'com.lantu.MobileCampus.huanghuai',
        'Sec-Fetch-Site': 'same-site',
        'Referer': 'https://yk.huanghuai.edu.cn:8993/?type=app&token=' + xAuthToken,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'userToken=' + idToken + '; Domain=.huanghuai.edu.cn; Path=/; SESSION=' + session
    }
    r6 = requests.post(url6, aesText, headers=header6, verify=False)
    print(r6.json())


# 获取最后一条打卡记录
def getLastRecard(xAuthToken, userToken, session):
    last_reacrd_url = "https://yq.huanghuai.edu.cn:7992/questionAndAnser/loadUserLastRecordAndDetail?studentNumber="
    last_reacrd_header = {
        'Host': 'yq.huanghuai.edu.cn:7992',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'x-auth-token': xAuthToken,
        'Origin': 'https://yk.huanghuai.edu.cn:8993',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; RMX2121 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045710 Mobile Safari/537.36 SuperApp',
        'Referer': 'https://yk.huanghuai.edu.cn:8993/?ver=3.0&type=app&token=' + xAuthToken,
        'Cookie': 'Domain=.huanghuai.edu.cn; Path=/; hhxy_site=jwc; hhxy_P8SESSION=3918910acf6eead8; userToken=' + userToken + ';SESSION=' + session
    }
    r = requests.get(last_reacrd_url, headers=last_reacrd_header).json()
    if r['code'] == 20000:
        stuNumber = r['data']['studentEntity']['student_number']
        stuName = r['data']['studentEntity']['student_name']
        phoneNumber = r['data']['studentEntity']['phone_number']
        emergencyContactName = r['data']['studentEntity']['emergency_contact_name']
        emergencyContactPhone = r['data']['studentEntity']['emergency_contact_phone']
        area = r['data']['studentEntity']['address']
        longitude_and_latitude = r['data']['studentEntity']['longitude_and_latitude']

        last_time = r['data']['studentEntity']['last_time']
        dkTime = datetime.datetime.strptime(last_time[0:19], "%Y-%m-%dT%H:%M:%S")
        UTCTime = datetime.datetime(dkTime.year, dkTime.month, dkTime.day, dkTime.hour, tzinfo=pytz.timezone('UTC'))
        SHTime = UTCTime.astimezone(pytz.timezone('Asia/Shanghai'))
        if datetime.datetime.now().strftime("%Y-%m-%d") == SHTime.strftime("%Y-%m-%d"):
            return -1, stuNumber, stuName, phoneNumber, emergencyContactName, emergencyContactPhone, area, longitude_and_latitude
        else:
            return 1, stuNumber, stuName, phoneNumber, emergencyContactName, emergencyContactPhone, area, longitude_and_latitude


# 获取地址
def getAddress(xAuthToken, userToken, session, longitude_and_latitude):
    address_url = "https://yq.huanghuai.edu.cn:7992/sys/getAddress?longAndLat=" + longitude_and_latitude
    address_header = {
        'Host': 'yq.huanghuai.edu.cn:7992',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'x-auth-token': xAuthToken,
        'Origin': 'https://yk.huanghuai.edu.cn:8993',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; RMX2121 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045710 Mobile Safari/537.36 SuperApp',
        'Referer': 'https://yk.huanghuai.edu.cn:8993/?ver=3.0&type=app&token=' + xAuthToken,
        'Cookie': 'Domain=.huanghuai.edu.cn; Path=/; hhxy_site=jwc; hhxy_P8SESSION=3918910acf6eead8; userToken=' + userToken + ';SESSION=' + session
    }
    r = requests.get(address_url, headers=address_header).json()
    if r['code'] == 20000:
        address = r['data']['address']
        return address
    else:
        return -1


def pkcs7padding(text):
    """明文使用PKCS7填充 """
    bs = 16
    length = len(text)
    bytes_length = len(text.encode('utf-8'))
    padding_size = length if (bytes_length == length) else bytes_length
    padding = bs - padding_size % bs
    padding_text = chr(padding) * padding
    return text + padding_text


def aes_encrypt(key, content):
    """ AES加密 """
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    # 处理明文
    content_padding = pkcs7padding(content)
    # 加密
    encrypt_bytes = cipher.encrypt(content_padding.encode('utf-8'))
    # 重新编码
    result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
    return result


'''
使用函数：
login()
getSession()
getLastRecard()
getAddress()
subWenJuan()
'''


def main():
    user_list = getUser()
    for u in user_list:
        try:
            idToken = login(u['username'], u['password'])
            if idToken == -1:
                print("账号或密码错误")
                return
                ################
            # 获取token
            session, xAuthToken = getSession(idToken)

            ################
            # 获取上次打卡信息
            f, stuNumber, stuName, phoneNumber, emergencyContactName, emergencyContactPhone, area, longitude_and_latitude = getLastRecard(
                xAuthToken, idToken, session)
            if f == -1:
                print(stuName + " 今日已打卡")
                return
                ################
            # 获取地址
            address = getAddress(xAuthToken, idToken, session, longitude_and_latitude)

            ################
            # 提交打卡
            # print(stuName)
            subWenJuan(session, xAuthToken, idToken, phoneNumber, emergencyContactName,
                       emergencyContactPhone,
                       stuNumber, area, address, longitude_and_latitude)
        except Exception as e:
            print("打卡异常，请手动打卡")


if __name__ == '__main__':
    main()
