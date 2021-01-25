import pytz
import requests
import base64
import urllib.parse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
import datetime
import pymysql

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

conn = pymysql.connect(host="", port=, user="", passwd="", db="")
cur = conn.cursor()
cur.execute("SELECT `username`, `password` FROM `user`")
user = list(cur.fetchall())
print(user)


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


# 获取session,xAuthToken
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


# 坐标获取地址，返回（area，address）。
def getAddress(session, xAuthToken, idToken, zuobiao):
    url4 = "https://yq.huanghuai.edu.cn:7992/sys/getAddress?longAndLat=" + zuobiao
    header4 = {
        'Host': 'yq.huanghuai.edu.cn:7992',
        'Connection': 'close',
        'Accept': 'application/json, text/plain, */*',
        'x-auth-token': xAuthToken,
        'Origin': 'https://yk.huanghuai.edu.cn:8993',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX2121 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045511 Mobile Safari/537.36 SuperApp',
        'Sec-Fetch-Mode': 'cors',
        'X-Requested-With': 'com.lantu.MobileCampus.huanghuai',
        'Sec-Fetch-Site': 'same-site',
        'Referer': 'https://yk.huanghuai.edu.cn:8993/my',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'userToken=' + idToken + '; Domain=.huanghuai.edu.cn; Path=/; SESSION=' + session
    }
    r4 = requests.get(url4, headers=header4)
    area = r4.json()['data']['address_component']['province'] + " " + r4.json()['data']['address_component'][
        'city'] + " " + r4.json()['data']['address_component']['district']
    address = r4.json()['data']['address']

    # print("area:", area)
    # print("address", address)

    return area, address


# 获取学号，姓名。
def getStuNumber(session, xAuthToken, idToken):
    url3 = "https://yq.huanghuai.edu.cn:7992/student/getLoginStudent"
    header3 = {
        'Host': 'yq.huanghuai.edu.cn:7992',
        'Connection': 'close',
        'Accept': 'application/json, text/plain, */*',
        'x-auth-token': xAuthToken,
        'Origin': 'https://yk.huanghuai.edu.cn:8993',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX2121 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045511 Mobile Safari/537.36 SuperApp',
        'Sec-Fetch-Mode': 'cors',
        'X-Requested-With': 'com.lantu.MobileCampus.huanghuai',
        'Sec-Fetch-Site': 'same-site',
        'Referer': 'https://yk.huanghuai.edu.cn:8993/?type=app&token=' + xAuthToken,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'userToken=' + idToken + '; Domain=.huanghuai.edu.cn; Path=/; SESSION=' + session
    }

    r3 = requests.get(url3, headers=header3)
    student_number = r3.json()['data']['student_number']
    student_name = r3.json()['data']['student_name']
    return student_number, student_name


# 获取填表信息，返回（坐标，手机号，紧急手机号码名，紧急手机号码（加空格），recordid）
def getFormInformation(session, xAuthToken, idToken, stuNumber):
    url5 = "https://yq.huanghuai.edu.cn:7992/questionAndAnser/loadUserLastRecordAndDetail?studentNumber=" + stuNumber
    header5 = {
        'Host': 'yq.huanghuai.edu.cn:7992',
        'Connection': 'close',
        'Accept': 'application/json, text/plain, */*',
        'x-auth-token': xAuthToken,
        'Origin': 'https://yk.huanghuai.edu.cn:8993',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX2121 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045511 Mobile Safari/537.36 SuperApp',
        'Sec-Fetch-Mode': 'cors',
        'X-Requested-With': 'com.lantu.MobileCampus.huanghuai',
        'Sec-Fetch-Site': 'same-site',
        'Referer': 'https://yk.huanghuai.edu.cn:8993/?type=app&token=' + xAuthToken,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'userToken=' + idToken + '; Domain=.huanghuai.edu.cn; Path=/; SESSION=' + session
    }

    r5 = requests.get(url5, headers=header5)
    longitude_and_latitude = r5.json()['data']['studentEntity']['longitude_and_latitude']
    phone_number = r5.json()['data']['studentEntity']['phone_number']
    emergency_contact_name = r5.json()['data']['studentEntity']['emergency_contact_name']
    emergency_contact_phone = r5.json()['data']['studentEntity']['emergency_contact_phone']
    recordid = r5.json()['data']['studentRecord']['record_id']

    # print("longitude_and_latitude:", longitude_and_latitude)
    # print("recordid:", str(recordid))

    return longitude_and_latitude, phone_number, emergency_contact_name, emergency_contact_phone, recordid


# 提交问卷信息
def subWenJuan(session, xAuthToken, idToken, recordid, phoneNumber, emergencyContactName, emergencyContactPhone,
               stuNumber, area, address, zuobiao):
    post = "recordId=" + str(recordid) + "&zuobiao=" + urllib.parse.quote(
        zuobiao) + "&questionnaire=%5B%7B%22problem_id%22%3A1%2C%22problem_name%22%3A%22%E4%BB%8A%E6%97%A5%E4%BD%93%E6%B8%A9%22%2C%22result_id%22%3Anull%2C%22result_name%22%3A%2236.7%22%7D%2C%7B%22problem_id%22%3A2%2C%22problem_name%22%3A%22%E4%BD%A0%E5%BD%93%E5%89%8D%E7%9A%84%E8%BA%AB%E4%BD%93%E7%8A%B6%E5%86%B5%E6%98%AF%3F%22%2C%22result_id%22%3A2%2C%22result_name%22%3A%22%E6%AD%A3%E5%B8%B8%EF%BC%8C%E6%B2%A1%E6%9C%89%E7%97%87%E7%8A%B6%22%7D%5D&record=" + "%7B%22current_area%22%3A%22" + urllib.parse.quote(
        area) + "%22%2C%22current_address%22%3A%22" + urllib.parse.quote(
        address) + "%22%7D" + "&phoneNumber=" + phoneNumber + "&emergencyContactName=" + urllib.parse.quote(
        emergencyContactName) + "&emergencyContactPhone=" + urllib.parse.quote(
        emergencyContactPhone) + "&student_number=" + stuNumber

    url6 = "https://yq.huanghuai.edu.cn:7992/questionAndAnser/wenjuanSubmit"
    header6 = {
        'Host': 'yq.huanghuai.edu.cn:7992',
        'Connection': 'close',
        'Content-Length': str(len(post)),
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

    r6 = requests.post(url6, post, headers=header6, verify=False)

    return r6.json()


# 历史打卡记录（判断今日是否已打卡，返回1/-1，area，address）
def hisInf(session, xAuthToken, idToken, stuNumber):
    url7 = "https://yq.huanghuai.edu.cn:7992/questionAndAnser/findStudentRecordByStudentNumber?studentNumber=" + stuNumber
    header7 = {
        'Host': 'yq.huanghuai.edu.cn:7992',
        'Connection': 'close',
        'Accept': 'application/json, text/plain, */*',
        'x-auth-token': xAuthToken,
        'Origin': 'https://yk.huanghuai.edu.cn:8993',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX2121 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045511 Mobile Safari/537.36 SuperApp',
        'Sec-Fetch-Mode': 'cors',
        'X-Requested-With': 'com.lantu.MobileCampus.huanghuai',
        'Sec-Fetch-Site': 'same-site',
        'Referer': 'https://yk.huanghuai.edu.cn:8993/log',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'userToken=' + idToken + '; Domain=.huanghuai.edu.cn; Path=/; SESSION=' + session
    }
    r7 = requests.get(url7, headers=header7)

    area = r7.json()['data'][0]['current_area']
    address = r7.json()['data'][0]['current_address']

    timeStr = r7.json()['data'][0]['create_time']
    dkTime = datetime.datetime.strptime(timeStr[0:19], "%Y-%m-%dT%H:%M:%S")
    UTCTime = datetime.datetime(dkTime.year, dkTime.month, dkTime.day, dkTime.hour, tzinfo=pytz.timezone('UTC'))
    SHTime = UTCTime.astimezone(pytz.timezone('Asia/Shanghai'))
    if datetime.datetime.now().strftime("%Y-%m-%d") == SHTime.strftime("%Y-%m-%d"):
        return -1, area, address
    else:
        return 1, area, address


for u in user:
    if len(u[0]) < 10:
        print("账号:"+u[0]+" 错误，请使用手机号或学号。")
        print("=" * 50)
        continue

    ################
    idToken = login(u[0], u[1])
    if idToken == -1:
        print("账号或密码错误:" + "userName:" + u[0] + "   passWord:" + u[1])
        print("=" * 50)
        time.sleep(10)
        continue

    ################
    session, xAuthToken = getSession(idToken)

    ################
    stuNumber, stuName = getStuNumber(session, xAuthToken, idToken)
    f, area, address = hisInf(session, xAuthToken, idToken, stuNumber)
    if f == -1:
        print("Name:" + stuName + "   Number:" + stuNumber + "   执行结果：" + "今日已打卡。")
        print("=" * 50)
        time.sleep(10)
        continue

    ################
    zuobiao, phone_number, emergency_contact_name, emergency_contact_phone, recordid = getFormInformation(session,
                                                                                                          xAuthToken,
                                                                                                          idToken,
                                                                                                          stuNumber)

    ################
    data = subWenJuan(session, xAuthToken, idToken, recordid, phone_number, emergency_contact_name,
                      emergency_contact_phone,
                      stuNumber, area, address, zuobiao)

    ################
    hisInf(session, xAuthToken, idToken, stuNumber)
    # data = {"message": "Testing..."}
    print(
        "stuName:" + stuName + "   stuNumber:" + stuNumber + "   打卡地点:" + address + "   打卡时间:" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + "   执行结果：" + data['message'])
    print("=" * 50)
    time.sleep(30)