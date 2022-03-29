import configparser
import datetime
import re
import requests
from bs4 import BeautifulSoup
from utils import sendWechat
from utils import selectOne
from utils import insertData
from utils import getAttach


def getNews():
    header = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 99.0.4844.82Safari / 537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh-HK;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6",
        "Host": "sise.uestc.edu.cn"

    }
    url = "https://sise.uestc.edu.cn/xwtz/tzgg/ygk.htm"

    res = requests.get(url=url, headers=header)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, 'html.parser')
    t = soup.select('.list-content > a')
    for i in t:
        # Traversing all news in the page.
        if re.sub('\s+', '', i.text)[-10:] == str(datetime.datetime.today().date()):
            title = re.sub('\s+', '', i.text)[:-10]
            time = re.sub('\s+', '', i.text)[-10:]
            # Get each link
            link = "https://sise.uestc.edu.cn" + i["href"][5:]
            # Judge each link in the database or not
            # If the link does not exist in the database, push the news to WeChat.Then archive the link to the database.
            # So each news will only push for one time and will not bother much.
            if selectOne(link=link) == 0:
                insertData(title=title, time=time, link=link)
                content = "有新动态发布，文章标题为:\n" + title + "\n" + \
                          "发布时间为：\n" + time + "\n" + \
                          "详情请点击：\n" + link
                # Check if attach is published
                attachTitle, attachLink = getAttach(link=link)
                if attachLink != '':
                    try:
                        # Send the attach file link to WeChat
                        sendWechat(content="New Attach Detected: \n"+str(attachTitle)+"\n"+"Click Here to Download:\n"+str(attachLink), corpsecret=corpsecret, corpid=corpid, agentid=agentid)
                    except Exception as e:
                        print(e)
                        sendWechat(content="Something goes wrong."+str(e), corpsecret=corpsecret, corpid=corpid, agentid=agentid)

                sendWechat(content=content, corpid=corpid, corpsecret=corpsecret, agentid=agentid)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("./config.ini", encoding='utf-8')
    corpsecret = config.get("generalConfig", "corpsecret")
    agentid = config.get("generalConfig", "agentid")
    corpid = config.get("generalConfig", "corpid")
    getNews()
