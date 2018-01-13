import pandas as pd
import requests
import re
import random
import time
from bs4 import BeautifulSoup
import jieba
# import pymysql

baseUrl = 'http://search.51job.com/list/020000,000000,0000,00,9,99,'

class JobSpider(object):
	def __init__(self):
		self.headers = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
			"Accept-Encoding": "gzip, deflate, sdch",
			"Accept-Language": "zh-CN,zh;q=0.8"
		}
		self.info = []
		self.details = ""

	def loadPage(self):
		#抓取列表页
		for offset in range(1,2):
			url = baseUrl + 'python,' + '2,' + str(offset) + '.html'
			try:
				res = requests.get(url,headers=self.headers)
				if res.status_code == 200:
					html = res.content.decode(encoding='gbk',errors='ignore')
					time.sleep(random.choice(range(1,5))*0.1+1)
			except Exception as e:
				print('failed,Error:%s'%e)
			pattern = re.compile(r'<div\sclass="el">\s+<p class="t1 ">.*?<a target="_blank" title="(.*?)" href="(.*?)".*?'
				+ r'<span class="t2"><a target="_blank" title="(.*?)".*?<span class="t3">(.*?)'
				+ r'</span>\s+<span class="t4">(.*?)</span>\s+<span class="t5">(.*?)</span>',re.S)
			items = re.findall(pattern,html)
			for item in items:
				job = {
					'title':item[0],
					'link':item[1],
					'company':item[2],
					'locate':item[3],
					'salary':item[4],
					'date':item[5]
				}
				self.info.append(job)

	def getJobInfo(self):
		#抓取详情页写入本地txt
		for i in self.info:
			url = i.get('link')
			try:
				res = requests.get(url,headers=self.headers)
				if res.status_code == 200:
					html = res.content.decode(encoding='gb2312',errors='ignore')
					text = re.search(r'<div class="bmsg job_msg inbox">\s+(.*?)\s+<div class="mt10">',html,re.S).group(1).replace('\t','').replace('<br>','')
					self.details += text
			except Exception as e:
				print('%s'%e)
			time.sleep(random.choice(range(1,5))*0.1+2)
		with open('jobdetails.txt','w',encoding='utf-8')as f:
			f.write(self.details)

	@staticmethod
	def count_details():
		with open('jobdetails.txt',encoding='utf-8')as f:
			words = f.read()
		words = jieba.cut(words,cut_all=False)
		word_list = list(map(lambda x:x.strip(),words))
		df = pd.DataFrame(word_list,columns=['words'])
		result = df.groupby(['words']).size()
		print(result.sort_values(ascending=False))
		

	@staticmethod
	def writeToExcel():
		df = pd.DataFrame(self.info)
		df.to_excel('joblist.xlsx',index=False)



spider = JobSpider()
# spider.loadPage()
# spider.writeToExcel()
# spider.getJobInfo()
spider.count_details()