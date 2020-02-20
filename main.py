import json
import os, sys
import re
import requests
import threading
import random
import time
keyword = input("输入关键词")
if not keyword:
    raise TypeError
if not os.path.exists("cookies.json"):
    print("找不到cookies.json,请导出pixiv的cookies之后再运行！")
    input()
    sys.exit(1)
else:
    userjs = open("cookies.json", "r")
    user = json.loads(userjs.read())
    userjs.close()
    token = False
    for i in user:
        if i["Name raw"] == "device_token":
            token = i["Content raw"]
            break
    if not token:
        print("找不到你的device_token,请再次雷普（登录）pixiv并重新保存cookies以获取")
        input()
        sys.exit(0)
user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
    ]
prePattern = r"c/[0-9]+x[0-9]+_[0-9].*?/.*?/"
sufPattern = r"[0-9]_[a-z]+[0-9]+\..?.?.?"
sourcePage = "https://www.pixiv.net/ajax/search/artworks/"+keyword+"?word="+keyword+"&order=date_d&mode=all&s_mode=s_tag&type=all&p="
urlFrom = "https://www.pixiv.net/tags/"+keyword+"/artworks?s_mode=s_tag"
fakeHeader = {
    'Referer': "",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}
setOfCookies = {"device_token": token}
session = requests.session()
requests.utils.add_dict_to_cookiejar(session.cookies, setOfCookies)
page = 1
onSearching = []
searchingThreads = []


def addressPic():
    global onSearching
    global pageCount
    global fakeHeader
    for i in range(pics["pageCount"]):
        if pageCount >= allPage:
            return
        fakeHeader['User-Agent'] = random.choice(user_agent_list)
        prefix = re.findall(prePattern, step0Url)
        step1Url = step0Url.replace(prefix[0], "img-original/")
        suffix = re.findall(sufPattern, step0Url)
        step2Url = step1Url.replace(suffix[0], "")
        step2Url = step2Url.replace("tc-pximg01.techorus-cdn.com", "i-f.pximg.net")
        id = pics["id"]
        result = jpgorpng(step2Url, i, id)
        if pageCount >= allPage:
            return
        onSearching.append(result)
        pageCount += 1
        print(str(pageCount) + "/" + str(allPage))
        print(result)
        time.sleep(1)


def jpgorpng(raw, count, id):
    global fakeHeader
    fakeHeader["Referer"] = "https://www.pixiv.net/artworks/" + id
    response = str(session.head(raw + str(count) + ".jpg", headers=fakeHeader))
    if response == "<Response [200]>":
        return raw + str(count) + ".jpg"
    else:
        return raw + str(count) + ".png"


fakeHeader["Referer"] = "https://www.pixiv.net/tags/"+keyword+"/artworks?s_mode=s_tag"
try:
    print(session.head("https://www.pixiv.net", headers=fakeHeader))
    input("初始化成功，按下任意键+回车以继续")
    os.system("cls")
except:
    os.system("cls")
    print("GFW阻断了连接，请在上级路由加载科学上网工具（例如梅林路由器插件，OpenWRT V2Ray插件等）（socks代理支持正在开发）")
    input()
    sys.exit(0)
pageCount = 0
allPage = 20
running = True
firstLoop = True
while running:
    thisPage = session.get(sourcePage + str(page), headers=fakeHeader)
    jsonOfThisPage = json.loads(thisPage.text)
    mainPart = jsonOfThisPage["body"]["illustManga"]
    # print(mainPart)# https://i.pximg.net/img-original/img/2020/02/10/20/55/27/79400972_p0.png
    if firstLoop:
        #allPage = mainPart["total"]
        firstLoop = False
    for pics in mainPart["data"]:
        time.sleep(0.3)
        if pageCount >= allPage:
            break
        os.system("cls")
        try:  # https://i.pximg.net/c/250x250_80_a2/img-master/img/2020/02/10/20/55/27/79400972_p0_square1200.jpg
            step0Url = pics["url"]
            searchingThreads.append(threading.Thread(target=addressPic))
            searchingThreads[-1].start()
        except KeyError:
            pass
    if pageCount >= allPage:
        break
running = True
while running:
    for i in searchingThreads:
        if not i.is_alive():
            running = False

onSearching = set(onSearching)
onSearching = list(onSearching)
print("Ended")
downloadtxt = open("cache.txt", "w")
for i in onSearching:
    downloadtxt.write(i + "\n")
downloadtxt.close()
os.system('aria2c -i cache.txt -x 8 --load-cookies=cookies.json --header="Referer:' + urlFrom + '"')
os.remove("cache.txt")
