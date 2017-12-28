import requests
import re
import random
import pandas as pd
from requests.packages.urllib3.exceptions import InsecureRequestWarning
#移除SSL认证的时候忽略警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
headers = {
"Host": "www.xicidaili.com",
"Connection": "keep-alive",
"Cache-Control": "max-age=0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
"Accept-Encoding": "gzip, deflate, sdch",
"Accept-Language": "zh-CN,zh;q=0.8	"
}
proxy_list = []

def loadPage():
	"""获取HTML页面"""
	page = random.randint(1,3)
	url = "http://www.xicidaili.com/nn/%d"%page
	try:
		res = requests.get(url,headers=headers,timeout=3)
		if res.status_code == 200:
			return res.text
	except Exception as e:
		print("Error:%s"%e)


def getProxies(html):
	"""正则解析出代理IP和端口,构造字典data"""
	pattern = re.compile(r'<tr class="odd">\s*<td\sclass="country">.*?<td>(.*?)</td>\s*<td>(.*?)</td>.*?高匿</td>\s+<td>(HTTP)</td>',re.S)
	ret = re.findall(pattern,html)
	ip = [i[0] for i in ret]
	port = [j[1] for j in ret]
	data = {
			"ip": ip,
			"port": port
			}
	return data


def checkip(data):
	"""检测代理IP的连通性,正常的IP不做任何处理，无法正常连接的删除"""
	header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"}
	data = pd.DataFrame(data)
	i = 0
	url = "https://www.baidu.com/"
	for k in data.values:
		proxy = {"http":"http://%s:%s"%(k[0],str(k[1]))}
		try:
			r = requests.get(url,proxies=proxy,headers=header,verify=False,timeout=3)
			if r.status_code == 200:
				proxy_list.append(proxy)
		except Exception as e:
			data = data.drop(i)
		i+=1
		return proxy_list
		# print("%d/%d"%(i,len(data)))


def get_proxy_list():
	html = loadPage()
	data = getProxies(html)
	proxy_list = checkip(data)
	return proxy_list