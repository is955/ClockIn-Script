from flask import Flask, request
import requests
from DB import *

app = Flask(__name__)



@app.route('/AddDkUser', methods=['GET', 'POST'])
def Add():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        f = login(username, password)
        if f == -1:
            return "账号或密码错误"
        else:
            db = Database()
            temp = db.insert('dk_user',
                             {"username": username, "password": password, "email": email})
            if temp == 0:
                return "Success"
            else:
                return 'False'


@app.route('/DelDkUser')
def Del():
    username = request.form['username']
    password = request.form['password']

    f = login(username, password)
    if f == -1:
        return "账号或密码错误"
    else:
        db = Database()
        db.delete('dk_user', 'username=' + username)
        return "Success"


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


if __name__ == '__main__':
    app.config['SERVER_NAME'] = 'dk.ruut.cn'
    app.run(host='0.0.0.0', port=80, debug=True)
