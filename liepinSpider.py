import requests
import re
from time import sleep
import pandas as pd

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
			}
proxies = {}
base_url = 'https://www.liepin.com/company/7962446/'
titles,prices,areas,times,qualifications,contents,departments,links = [[], [], [], [], [], [], [], []]

def test():
	'''用来测试代理并获取公司招聘页面数并获取页面数maxPage'''
	try:
		proxy = {'http':'http://user:password@59.62.27.129:808/'}
		url2 = 'https://www.baidu.com/'
		ret = requests.get(url2,proxies=proxy,timeout=2)
		if ret.status_code == 200:
			global proxies
			proxies = proxy
	except Exception:
		print('代理失效，请重试')

	try:
		res = requests.get(base_url,headers=headers,proxies=proxies)
		if res.status_code == 200:
			maxPage = int(re.search(r'.*?共(\d+)页</span>',res.text,re.S).group(1))
			return maxPage
	except Exception as e:
		return None
		print('获取页面出错:%s'%e)


def loadPage(pageNum):
	'''用来获取招聘页面的html文本'''
	url = base_url + 'pn'+ str(pageNum) + '/'
	try:
		res = requests.get(url,headers=headers,proxies=proxies)
		if res.status_code == 200:
			print(url)
			return res.text
	except Exception as e:
		print('Error:%s'%e)


def getUrl(html):
	'''用来获取到每个招聘岗位的url'''
	p = re.compile(r'<div class="job-info">.*?href="(.*?)".*?</time>',re.S)
	jobLink = re.findall(p,html)
	return jobLink


def getData(link):
	'''用来获取到每个页面的职位详情'''
	try:
		res = requests.get(link,headers=headers,proxies=proxies)
		if res.status_code == 200:	
			title = re.findall(r'<h1 title=.*?">(.*?)</h1>',res.text,re.S)
			price = [re.findall(r'<p class="job-item-title">(.*?)<em>',res.text,re.S)[0].replace('\n','').replace('r','').strip()]
			area = [re.findall(r'<p class="basic-infor">.*?<a href="https://www.liepin.com.*?>(.*?)</a>.*?<time title="(.*?)".*?</time>',res.text,re.S)[0][0]]
			time = [re.findall(r'<p class="basic-infor">.*?<a href="https://www.liepin.com.*?>(.*?)</a>.*?<time title="(.*?)".*?</time>',res.text,re.S)[0][1]]
			qualification = [re.findall(r'<div class="job-qualifications">(.*?)/div>',res.text,re.S)[0].replace('\n','').replace('r','').replace('<span>','').replace('\r','').replace('</span>','').replace('<','').strip()]
			content = [re.findall(r'<div class="content content-word">(.*?)</div>',res.text,re.S)[0].replace('<br>','').replace('<br/>','').replace('\r\n','').strip()]
			department = re.findall(r'<div class="job-item main-message">.*?所属部门：</span><label>(.*?)</label></li>',res.text,re.S)
			link = [link]
	except Exception as e:
		print('Error:%s'%e)
	sleep(0.5)

	global titles,prices,areas,times,qualifications,contents,departments,links
	titles.extend(title)
	prices.extend(price)
	areas.extend(area)
	times.extend(time)
	qualifications.extend(qualification)
	contents.extend(content)
	departments.extend(department)
	links.extend(link)


def writeData():
	'''写入本地'''
	data = {'title':titles,
			'salary':prices,
			'area':areas,
			'date':times,
			'qualification':qualifications,
			'content':contents,
			'department':departments,
			'link':links
			}
	df = pd.DataFrame(data,columns=['title','date','area','department','content','salary','qualification','link'])
	df.to_excel('data.xlsx',index=False)
	print('写入成功')


def main():
	'''调度'''
	maxPage = test()
	jobLinks = []
	for pageNum in range(1,maxPage):
		html = loadPage(pageNum)
		jobLink = getUrl(html)
		jobLinks.extend(jobLink)
	print('等待抓取的岗位一共有%d个'%(len(jobLinks)))
	num = 1
	for link in jobLinks:
		getData(link)
		print('目前进度：%s/%s'%(str(num),str(len(jobLinks))))
		num += 1	
	writeData()


if __name__ == '__main__':
	main()