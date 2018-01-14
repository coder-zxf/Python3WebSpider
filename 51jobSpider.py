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
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"
		}
		self.info = []
		self.details = ""

	def load_page(self):
		#抓取列表页
		for offset in range(1,31):
			url = baseUrl + '%25E9%25A3%258E%25E6%258E%25A7,' + '2,' + str(offset) + '.html'
			try:
				res = requests.get(url,headers=self.headers)
				if res.status_code == 200:
					html = res.content.decode(encoding='gbk',errors='ignore')
					time.sleep(random.choice(range(1,5))*0.1+1)
			except Exception as e:
				print('failed,Error:%s'%e)
			finally:
				print('%d/30'%(offset))
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

	def get_job_info(self):
		#抓取详情页写入本地
		j = 0
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
			finally:
				j+=1
				print('{}/{}'.format(j,len(self.info)))
				time.sleep(random.choice(range(1,5))*0.1+5)
		with open('jobdetails.txt','w',encoding='utf-8')as f:
			f.write(self.details)

	@staticmethod
	def count_details():
		#分词统计
		with open('jobdetails.txt',encoding='utf-8')as f:
			words = f.read()
		jieba.load_userdict('my_dict.txt')
		words = jieba.cut(words,cut_all=False)
		word_list = list(map(lambda x:x.strip(),words))
		df = pd.DataFrame(word_list,columns=['words'])
		result = df.groupby(['words']).size()
		ret = result.sort_values(ascending=False)
		ret.to_excel('count1.xlsx')

	@staticmethod
	#写入本地
	def write_to_excel(data,filename,columns):
		writer = pd.ExcelWriter(filename)
		df = pd.DataFrame(data)
		df.to_excel(writer,index=False,columns=columns)
		writer.save()


if __name__ == "__main__":
	spider = JobSpider()
	spider.load_page()
	spider.write_to_excel(data=spider.info,filename='joblist.xlsx',columns=['title','date','salary','company','locate','link'])
	spider.get_job_info()
	spider.count_details()