###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 1.0 Date: 07/07/2015
###################################################
# -*- coding: utf-8 -*-

import os, time
import urllib2
import mimetypes
from bs4 import BeautifulSoup
from gluon import current
from gluon.dal import Field

			
class Crawler:
	def __init__(self,**attr):
		self.db = attr.get('db',None)
		if not self.db:
			from gluon import DAL
			self.db = DAL('sqlite://crawler.db3',pool_size=1,check_reserved=['all'],fake_migrate_all=False,migrate=True,lazy_tables=True,folder=current.request.folder+'/databases/crawler')
		self.settings = attr.get('settings',{})
		self.id = attr.get('id',None)
		if not self.id: self.id = current.request.args(0)
		if not self.settings:
			table = self.define_crawler(True)
			if table(self.id): self.settings = eval(table(self.id).settings)

	def define_crawler(self,migrate=False):	
		if 'crawler' not in self.db.tables:
			self.db.define_table('crawler',
				Field('name'),
				Field('settings','text',writable=False),
				Field('publish_on','datetime'),
				migrate=migrate)
		return self.db.crawler

	def define_crawlerdata(self,migrate=False):	
		if 'crawlerdata' not in self.db.tables:
			self.db.define_table('crawlerdata',
				Field('crawler','integer'),
				Field('urllink'),
				Field('textcontent','text'),
				Field('tablename'),
				Field('table_id','integer'),
				Field('created_on','datetime',default=current.request.now),
				Field('updated_on','datetime'),
				Field('publish_on','datetime'),
				migrate=migrate)
		return self.db.crawlerdata
		
	def getURL(self, url=None, deep=0, maxDeep=3, nbLink=0, maxLink=10, listLink=[], timeStart=None, timeOut=300):
		try:
			if deep > maxDeep: return 0
			rooturl = self.settings.get("rooturl")
			url = url or rooturl
			if url in listLink: 
				print "Link exist..."
				return 0
			listLink.append(url)
			if self.db(self.db.crawlerdata.urllink==url).count()>0: return 0		
			website = urllib2.urlopen(url,timeout=30)
			if not website: return 0
			http_message = website.info()
			if http_message.type !="text/html": 
				print http_message.type
				return 0 
			if not timeStart: timeStart = time.time()
			k = time.time() - timeStart
			if k>timeOut: 
				print "timeOut"
				return 0
			print deep, int(k), url
			html = website.read()
			soup = BeautifulSoup(html)
			nb = 0
			textcontent = self.getContent(soup,self.settings)
			if textcontent != "{}":
				self.db.crawlerdata.insert(crawler=self.id,urllink=url,textcontent=textcontent)
				self.db.commit()
				nb = 1
				print nbLink+nb, url
				if maxLink==1: return nb
			if rooturl.endswith("/"): rooturl = rooturl[:-1]
			tags = soup.findAll("a",href=True)
			for tag in tags:
				href = tag["href"]
				if (href.find("javascript:")==-1)&(href.find("mailto:")==-1)&(href.find("#")==-1):
					if (not href.startswith(rooturl))&(not href.startswith("http://"))&(not href.startswith("https://")):
						if (href.startswith("/")): href = rooturl + href
						else: href = rooturl + "/" + href
					if href.startswith(rooturl):
						nb += self.getURL(href,deep+1,maxDeep,nb,maxLink,listLink,timeStart,timeOut)
						if nb>maxLink: return nb
			return nb		
		except Exception, e:
			print e
			return 0
			
	def getContent(self, soup, settings):
		rooturl = settings.get("rooturl","")		
		divid = settings.get("id","")		
		tags = soup.findAll("div")
		i = 1
		textcontent = {}
		keys = settings.keys()
		fields = []
		for key in keys:
			if key.startswith("fieldname_"): fields.append(settings[key])
		for tag in tags:
			if tag.contents:
				if not tag.has_attr('id'): tag['id'] = "div%s"%i
				if divid==tag['id']:
					elems = tag.findAll()
					k = 0
					for elem in elems: 
						if elem.get_text():
							key = "fieldname_%s_%s"%(k,elem.name)
							if key in keys:
								field = settings[key]
								fields.remove(field)
								if field == "htmlcontent": 
									for img in elem.findAll(src=True):
										href = img["src"]
										if not href.startswith(rooturl):
											if (href.startswith("/")):
												href = rooturl + href
												img["src"] = href
									textcontent[field] = elem.prettify()
								else: textcontent[field] = elem.get_text()
							k+=1
					if len(fields)>0: return "{}"
					return str(textcontent)
				i+=1
		return str(textcontent)
		
		
import threading
class ThreadGetUrl(threading.Thread):
	def __init__(self, crawler, queue, rooturl, deep=1, maxdeep=2):
		threading.Thread.__init__(self)
		self.crawler = crawler
		self.queue = queue
		self.rooturl = rooturl
		self.deep = deep
		self.maxdeep = maxdeep
	def run(self):
		while True:
			url = self.queue.get()
			self.crawler.getURL(self.rooturl, url, self.deep, self.maxdeep)
			self.queue.task_done()
		
def CrawlerUrl(crawler,maxThread=50):
	import Queue
	queue = Queue.Queue()
	id = crawler.id
	if not id: return 0
	table = crawler.define_crawler()
	if not table(id).settings: return 0
	settings = eval(table(id).settings)
	rooturl = settings.get("rooturl",None)
	if not rooturl: return 0
	crawler.define_crawlerdata(True)
	url = rooturl
	website = urllib2.urlopen(url,timeout=30)
	html = website.read()
	soup = BeautifulSoup(html)
	tags = soup.findAll("a",href=True)
	urls = []
	i = 1
	for tag in tags:
		href = tag["href"]
		if not href.startswith(rooturl):
			if (href.startswith("/")):
				href = rooturl + href
		if href.startswith(rooturl) & (not href.endswith(".pdf")) & (not href.endswith(".doc")) & (not href.endswith(".docx")):		
			urls.append(href)
			t = ThreadGetUrl(crawler,queue,rooturl)
			t.setDaemon(True)
			t.start()
			i+=1
		if i>maxThread: break	
	for url in urls:
		queue.put(url)
	#wait on the queue until everything has been processed     
	print "Start..."
	queue.join()
	print "End"
	return 1