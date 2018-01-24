import requests
import time
import re
from pymongo import MongoClient

class weiboSpider(object):
	"""微博爬虫类"""
	def __init__(self,uid):
		self.headers = {"Host": "m.weibo.cn",
		   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
		   "Referer": "https://m.weibo.cn/u/" + uid,
		   "X-Requested-With": "XMLHttpRequest"
	  	}
		self.url = 'https://m.weibo.cn/api/container/getIndex'
		self.client = MongoClient()
		self.db = self.client['weibo']
		self.collection = self.db['weibo']

	def get_info(self,page):
		"""抓取"""
		params = {'type': 'uid',
				  'value': uid,
				  'containerid': '107603'+uid,
				  'page': str(page)
		}
		try:
			res = requests.get(self.url,params=params,headers=self.headers)
			if res.status_code == 200:
				weiboJson = res.json()
				items = weiboJson.get('data').get('cards')
		except Exception as e:
			pass
	
		for item in items:
			try:
				item = item.get('mblog')
				weibo = {}
				weibo['created_at'] = item.get('created_at')
				weibo['text'] = item.get('text').replace("<br/>","").replace("</a>","")
				weibo['attitudes_count'] = item.get('attitudes_count')
				weibo['comments_count'] = item.get('comments_count')
				weibo['reposts_count'] = item.get('reposts_count')
				weibo['href'] = 'https://m.weibo.cn/status/' + item.get('id')
				yield weibo
			except Exception as e:
				print("get_info:",e.args)

	def save_to_mongo(self,result):
		"""存储到db"""
		try:
			if result:
				self.collection.insert_one(result)
				print('saved successfully,count:%d'%(self.collection.count({})))
			else:
				pass
		except Exception as e:
			print("mongo",e.args)

	@staticmethod
	def save_to_txt(result):
		"""存入txt"""
		with open('weibo.txt','a',encoding='utf-8')as f:
			f.write(result.get('text')+'\n')
			# import json
			# f.write(json.dumps(result,indent=2,ensure_ascii=False))


if __name__ == '__main__':
	uid = '5687069307' #输入任意用户的id
	max_page = 240 #在weibo.cn查看用户发了多少页微博
	spider = weiboSpider(uid)
	for page in range(1,max_page+1):
		results = spider.get_info(page)
		for result in results:
			spider.save_to_mongo(result)
			spider.save_to_txt(result)
		time.sleep(2)