import re
import requests
import ua_headers
from urllib.parse import urlencode
import time

headers = ua_headers.headers()
def loadPage(fullurl):
    tiebaUrl = 'http://tieba.baidu.com/'
    #先抓取某个吧页面，提取每个帖子的链接
    html = requests.get(fullurl,headers=headers).text
    pattern = re.compile(r'<a\shref="(/p/.*?)"\stitle=.*?</a>')
    links = re.findall(pattern,html)
    for link in links:
        linkList = tiebaUrl + link
        loadImage(linkList)
        time.sleep(2)

def loadImage(url):
    html = requests.get(url,headers=headers).text
    pattern = re.compile(r'class="BDE_Image".*?src="(http.*?jpg|png).*?>')
    items = re.findall(pattern,html)
    for item in items:
        parseImage(item)

def parseImage(url):
    #访问每个link，返回content二进制数据，保存
    res = requests.get(url,headers=headers)
    filename = url[-10:]
    for image in res:
       with open(filename,'wb') as f:
            f.write(res.content)          

def tiebaSpider(url):
    #贴吧调度器
    startPage = int(input('输入起始页序号'))
    endPage = int(input('输入终止页序号'))
    for page in range(startPage,endPage+1):
        pn = (page-1)*50
        fullurl = url + '&pn=' + str(pn)
        loadPage(fullurl)
        time.sleep(2)

if __name__ == '__main__':
    kw = input('输入你要抓取的吧名')
    baseUrl = 'http://tieba.baidu.com/f?'
    key = urlencode({'kw':kw})
    url = baseUrl + key
    tiebaSpider(url)