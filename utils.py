import configparser
import requests
import os
import pymysql
from lxml import etree


def selectOne(link):
    config = configparser.ConfigParser()
    config.read("./config.ini", encoding='utf-8')
    host = config.get("remoteMySQL", "hostname")
    user = config.get("remoteMySQL", "username")
    passwd = config.get("remoteMySQL", "password")
    port = config.get("remoteMySQL", "port")
    database = config.get("remoteMySQL", "database")
    charset = config.get("remoteMySQL", "charset")

    conn = pymysql.connect(host=host, user=user, passwd=passwd, port=int(port), db=database, charset=charset)
    cur = conn.cursor()
    selectSQL = "select count(title) from `article` where link = '%s'" % link
    try:
        cur.execute(selectSQL)
        data = cur.fetchall()
        return data[0][0]
    except Exception as e:
        corpsecret = config.get("generalConfig", "corpsecret")
        agentid = config.get("generalConfig", "agentid")
        corpid = config.get("generalConfig", "corpid")
        sendWechat(content="this is an error occurred.Detail:\n" + str(e), corpsecret=corpsecret, corpid=corpid,
                   agentid=agentid)
        conn.rollback()
    conn.close()


def insertData(title, time, link):
    config = configparser.ConfigParser()
    config.read("./config.ini", encoding='utf-8')
    host = config.get("remoteMySQL", "hostname")
    user = config.get("remoteMySQL", "username")
    passwd = config.get("remoteMySQL", "password")
    port = config.get("remoteMySQL", "port")
    database = config.get("remoteMySQL", "database")
    charset = config.get("remoteMySQL", "charset")
    print(title)
    conn = pymysql.connect(host=host, user=user, passwd=passwd, port=int(port), db=database, charset=charset)
    cur = conn.cursor()
    insertSQL = "insert into `article`(id, title, time, link) values (null, %(title)s, %(time)s, %(link)s)"
    value = {"title": title, "time": time, "link": link}
    print(value)
    try:
        cur.execute(insertSQL, value)
        conn.commit()
    except Exception as e:
        corpsecret = config.get("generalConfig", "corpsecret")
        agentid = config.get("generalConfig", "agentid")
        corpid = config.get("generalConfig", "corpid")
        sendWechat(content="this is an error occurred.Detail:\n" + str(e), corpsecret=corpsecret, corpid=corpid,
                   agentid=agentid)
        conn.rollback()
    conn.close()


def sendWechat(content, corpsecret, corpid, agentid):
    # 获得access_token
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    token_param = '?corpid=' + corpid + '&corpsecret=' + corpsecret
    token_data = requests.get(url + token_param)
    token_data.encoding = 'utf-8'
    token_data = token_data.json()
    access_token = token_data['access_token']
    # 发送内容
    content = content
    # 创建要发送的消息
    data = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": agentid,
        "text": {"content": content}
    }
    send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    message = requests.post(send_url, json=data)
    message.encoding = 'utf-8'
    res = message.json()
    return res


def sendFile(corpsecret, agentid, corpid, filepath, filename, content_type):
    # 获得access_token
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    token_param = '?corpid=' + corpid + '&corpsecret=' + corpsecret
    token_data = requests.get(url + token_param)
    token_data.encoding = 'utf-8'
    token_data = token_data.json()
    access_token = token_data['access_token']
    # 发送文件
    send_url1 = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=' + access_token + '&type=file'
    # 临时上传文件
    file_data = {
        "filename": filename,
        "filelength": os.filepath.getsize(filepath + filename),
        "content-type": content_type
    }
    files = {'file': open("./Articles/" + filename, 'rb')}
    message = requests.post(send_url1, data=file_data, files=files)
    message.encoding = 'utf-8'
    # 拿到临时上传文件的media_id
    res = message.json()
    # 发送多媒体文件
    data = {
        "touser": "@all",
        "agentid": agentid,
        "msgtype": "file",
        "file": {
            "media_id": res["media_id"]
        }
    }
    send_url2 = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    message = requests.post(send_url2, json=data)
    message.encoding = 'utf-8'
    res = message.json()
    return res


def getAttach(url):
    header = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 99.0.4844.82Safari / 537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh-HK;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6",
        "Host": "sise.uestc.edu.cn"

    }
    res = requests.get(url=url, headers=header)
    res.encoding = "utf-8"
    if "附件" in res.text:
        html = etree.HTML(res.text)
        title = html.xpath("/html/body/div[2]/div[2]/div[2]/ul[1]/li/a/text()")
        # The Xpath should be dispalced to your target website.
        link = "https://sise.uestc.edu.cn" + html.xpath("/html/body/div[2]/div[2]/div[2]/ul[1]/li/a/@href")[0]
        print(title[0], link)
        return title, link


