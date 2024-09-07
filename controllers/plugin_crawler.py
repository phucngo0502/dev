###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 1.0 Date: 26/06/2015
###################################################
# -*- coding: utf-8 -*-

import urllib, urllib2, os
from bs4 import BeautifulSoup
	
import Queue
import threading
import time

queue = Queue.Queue()
pathfile = '%s/private/url.txt'%request.folder
home = "http://nghixuan.gov.vn"

import datetime		
t1 = datetime.datetime.now()

class ThreadImage(threading.Thread):
	#Threaded Image Grab
	def __init__(self, queue, rooturl, deep=1, maxdeep=2):
		threading.Thread.__init__(self)
		self.queue = queue
		self.rooturl = rooturl
		self.deep = deep
		self.maxdeep = maxdeep
	def run(self):
		while True:
			#grabs file name from queue
			url = self.queue.get()
			getURL(self.rooturl, url, self.deep, self.maxdeep)
			#signals to queue job is done
			self.queue.task_done()

def getURL2(home, url, deep=1, max=3):
	if deep > max: return 0
	website = urllib2.urlopen(url,timeout=30)
	if not website: return 0
	html = website.read()
	soup = BeautifulSoup(html)
	tags = soup.findAll("a",href=True)
	for tag in tags:
		href = tag["href"]
		if not href.startswith(home):
			if (href.startswith("/")):
				href = home + href
		#if href.startswith(home) & (not href.endswith(".pdf")) & (not href.endswith(".doc")) & (not href.endswith(".docx")):		
		if href.startswith(home) & href.endswith(".html"):		
			file = open(pathfile,"r")
			result = file.read().split("\n")
			file.close()
			if href not in result: 
				t2 = datetime.datetime.now()
				print t2-t1
				print 
				file = open(pathfile,"a+")
				file.write(href+"\n")
				file.close()
				try:	
					getURL(home,href,deep+1,max)
				except Exception, e:
					print e
	return 1

def test():
	#connect to a URL
	home = "https://www.amazon.com/Crest-Professional-Whitestrips-Whitening-Treatments/dp/B00AHAWWO0/ref=lp_16225006011_1_2?s=beauty-intl-ship&ie=UTF8&qid=1604565039&sr=1-2"
	# home = "http://demo1.ivinh.com"
	# home = "http://baohatinh.vn"
	# url = "http://demo1.ivinh.com/huongson"
	url = home
	# file = open(pathfile,"w")
	# file.write("")
	# file.close()
	
	website = urllib2.urlopen(url,timeout=30)
	html = website.read()
	soup = BeautifulSoup(html)
	tags = soup.findAll("a",href=True)
	urls = []
	i = 1
	for tag in tags:
		href = tag["href"]
		if not href.startswith(home):
			if (href.startswith("/")):
				href = home + href
		if href.startswith(home) & (not href.endswith(".pdf")) & (not href.endswith(".doc")) & (not href.endswith(".docx")):		
			urls.append(href)
			t = ThreadImage(queue)
			t.setDaemon(True)
			t.start()
			i+=1
		if i>50: break	
	for url in urls:
		queue.put(url)
	#wait on the queue until everything has been processed     
	print "start..."
	queue.join()
	print "end"
	#getURL(home,url)
	file = open(pathfile,"r+")
	result = file.read().split("\n")
	file.close()
	ul = UL()
	for url in result:
		ul.append(LI(A(url,_href=url)))
	return dict(ul=ul)
	

def speed():
	import urllib2
	home = "https://www.google.com.vn/search?q=dong+phuc+tai+nghe+an&num=50"
	url_def = '/url?q=http://dongphucbravo.com'
	
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]

	html = opener.open(home).read()
	
	soup = BeautifulSoup(html)

	mydivs = soup.findAll("h3", {"class": "r"})
	i = 1
	ul = UL()
	for div in mydivs: 
		cite =  div.findAll("a",href=True)
		for tag in cite:
			href = tag["href"]
			if href.startswith(url_def):
				return i
			ul.append(LI(i,href))
			
			i+=1
	return XML(ul)
	
@auth.requires(auth.has_membership(role='admin'))	
def index():
	from plugin_crawler import Crawler
	c = Crawler()
	table = c.define_crawler()
	links=[dict(header="",body=lambda row: A(SPAN(_class='icon pen icon-pencil glyphicon glyphicon-pencil'),T('Edit'),_href=URL(f='edit',args=[row.id]),_class='button btn btn-default'))]
	content = SQLFORM.grid(table,csv=False,user_signature=False,links=links,editable=False,create=False)
	return dict(content=content)

def xmlcontent(content):
	if not content: return ""
	d = eval(content)
	t = TABLE()
	for key in d.keys():
		t.append(TR(TD(key),TD(XML(d[key]))))
	return t	
	
@auth.requires(auth.has_membership(role='admin'))	
def urllinks():
	from plugin_crawler import Crawler
	c = Crawler()
	table = c.define_crawlerdata()
	if request.args(0)=="view":
		table.textcontent.represent = lambda textcontent,row: xmlcontent(textcontent)
		table.urllink.represent = lambda value,row: A(value,_href=value,_target="new")
	content = SQLFORM.grid(table,csv=False,user_signature=False,editable=False,create=False)
	return dict(content=content)

def widget_process(value):
	from plugin_process import ProcessModel
	p = ProcessModel()
	db = p.db
	p.define_process()
	rows = db(db.procedures.id>0).select()
	op = []
	for row in rows:
		rs = db(db.process.procedures==row.id).select()
		for r in rs: op.append(OPTION(row.label+' -> '+r.label,_value=r.id,_selected=(str(r.id) == str(value))))
	widget = SELECT(op,_name="process",_id="process")
	return widget

@auth.requires(auth.has_membership(role='admin'))	
def menu():
	content = DIV(A(T("Thiết lập"),_href=URL(f="edit",args=request.args),_class="btn btn-primary"))
	content.append(A(T("Thu thập thông tin"),_href=URL(f="geturl",args=request.args),_class="btn btn-primary"))
	return content	
		
@auth.requires(auth.has_membership(role='admin'))	
def edit():	
	id = request.args(0)
	if id:
		from plugin_crawler import Crawler
		c = Crawler()
		table = c.define_crawler(True)
		row = table(id)
		settings = eval(row.settings) if row.settings else {}
		name = row.name
	else:
		name = ""
		settings = {}
	url = settings.get("url","")
	rooturl = settings.get("rooturl","")
	tablename = settings.get("tablename","")
	process = int(settings.get("process","0"))
	content = TABLE(_class='table table-striped defview')
	content.append(TR(TH(T('Tên website')),TD(INPUT(_id="name",_name='name',_value=name,_class="string text_urllink",_style="width:300px;"))))
	content.append(TR(TH(T('Trang chủ')),TD(INPUT(_id="rootlink",_name='rooturl',_value=rooturl,_class="string text_urllink",_style="width:100%;"))))
	content.append(TR(TH(T('Địa chỉ mẫu')),TD(INPUT(_id="urllink",_name='url',_value=url,_class="string text_urllink",_style="width:100%;"))))
	table = cms.define_dtable()
	rows = cms.db(table.publish==True).select(orderby=table.label)
	ops = [OPTION(row.label,_value=row.name,_selected=(row.name==tablename)) for row in rows]
	ajax = "ajax('%s',['tablename'],'tablefields')"%(URL(f='getfields',args=request.args))
	select = SELECT(ops,_name="tablename",_id="tablename",_onchange=ajax)
	content.append(TR(TH(T('Table name')),TD(select,DIV(LOAD(f="getfields",vars=settings),_id="tablefields"))))
	content.append(TR(TH(T('Process name')),TD(widget_process(process))))
	content = FORM(content,_action=URL(f='update_settings',args=request.args))
	content.append(INPUT(_type='button',_value=T('Lưu thông tin'),_class="btn btn-primary",_onclick="getfields();"))
	ajax = "ajax('%s',['url'],'analyse_result')"%(URL(f='analyse',args=request.args))	
	content.append(INPUT(_type='button',_value=T('Phân tích nội dung'),_class="btn btn-primary",_onclick=ajax))
	content.append(DIV(LOAD(f="gettags",vars=settings),_id='analyse_result'))
	content = DIV(menu(),content)
	return dict(content=content)

@auth.requires(auth.has_membership(role='admin'))	
def geturl():
	id = request.args(0)
	from plugin_crawler import Crawler
	c = Crawler()
	table = c.define_crawler()
	row = table(id)
	settings = eval(row.settings) if row.settings else {}
	name = row.name
	rooturl = settings.get("rooturl","")
	tr1 = TR(TH(T("Root URL")))
	tr2 = TR(TD(rooturl))
	settings["maxDeep"] = 3
	settings["maxLink"] = 10
	settings["timeOut"] = 300
	keys = ["maxDeep","maxLink","timeOut"]
	for key in keys:
		tr1.append(TH(T(key)))
		tr2.append(TD(INPUT(_name=key,_id=key,_value=settings.get(key,""),_class="integer")))
	keys.append("urllink")
	keys.append("crawler")
	ajax = "ajax('%s',%s,'analyse_result')"%(URL(f='crawlerurl',args=request.args),keys)	
	tr3 = TR(TH(T("Thu thập từ địa chỉ này")), TD(INPUT(_name="urllink",_style="width:100%;",_placeholder="http://"),_colspan=3))
	tr4= TR(TD(INPUT(_type="checkbox",_name="crawler"),LABEL(T("Thu thập mới các thông tin"))),TD(INPUT(_type='button',_value=T('Chấp nhận'),_class="btn btn-primary",_onclick=ajax),_colspan=3))	
	content = TABLE(tr1, tr2, tr3, tr4,_class='table table-striped defview')
	content = DIV(menu(),content,DIV(_id='analyse_result'))
	return dict(content=content)
	
def getfields():
	from plugin_app import select_option
	tablename = request.vars.tablename
	if not tablename: return ""
	table = cms.define_table(tablename)
	th = TR()
	tr = TR()
	for field in table.fields:
		if table[field].type.startswith('reference'):
			value = request.vars[field] if field in request.vars.keys() else "0"
			if value.isdigit(): value = int(value)
			ref= table[field].type.split(' ')[-1]
			if 'label' in cms.db[ref].fields: name = 'label'
			elif 'name' in cms.db[ref].fields: name = 'name'
			else: name = cms.db[ref].fields[-1]
			select = SELECT(['']+select_option(cms.db,auth,ref,selected=[value],field=name),_name=field)
			th.append(TH(T(field.capitalize()),_class="field_label"))
			tr.append(TD(select))
	return TABLE(th,tr)

	
def analyse():
	try:
		url = request.vars.url
		id = request.args(0)
		#settings = eval(portlet.db.portlet(id).settings or "{}")
		settings = {}
		response = urllib2.urlopen(url,timeout=30)
		data = response.read()
		soup = BeautifulSoup(data)
		tags = soup.findAll("div")
		i = 1
		for tag in tags:
			if tag.contents:
				if not tag.has_attr('id'): tag['id'] = "div%s"%i
				newtag = BeautifulSoup('''<input type='radio' name='divselected' class='divselected' onclick='getdiv("%s");'></input>'''%tag["id"])
				if tag.has_attr('class'): tag['class'].append('divborder')
				else: tag["class"] = 'divborder'				
				tag.insert(0, newtag)
				i+=1
		return soup.prettify()
	except Exception, e:
		return e
	
def getdiv():
	try:
		url = request.vars.url
		id = request.vars.id
		settings = {}
		response = urllib2.urlopen(url,timeout=30)
		data = response.read()
		soup = BeautifulSoup(data)
		tags = soup.findAll("div")
		i = 1
		for tag in tags:
			if tag.contents:
				if not tag.has_attr('id'): tag['id'] = "div%s"%i
				if id==tag['id']:
					elems = tag.findAll()
					k = 0
					for elem in elems: 
						if elem.get_text():
							key = "fieldname_%s_%s"%(k,elem.name)
							newtag = BeautifulSoup('''<input type='checkbox' name='divselected' class='divselected' value=%s></input>'''%key)
							if elem.has_attr('class'): elem['class'].append('divborder')
							else: elem["class"] = 'divborder'				
							elem.insert(0, newtag)
							k+=1
					newtag = BeautifulSoup('''<div><input type='button' id='btnsubmit' class="btn btn-primary" value='%s' onclick='gettags();'></input><input type='hidden' id='divid' value='%s'></input></div>'''%(T("Submit"),id))
					tag.append(newtag)
					return tag.prettify()
				i+=1
		return "Not found div id="+id
	except Exception, e:
		return e
		
def gettags():
	try:
		url = request.vars.url
		id = request.vars.id
		if not url: return ""
		if not id: return ""
		rooturl = request.vars.rooturl
		checkbox = request.vars.checkbox
		if not checkbox:
			checkbox = []
			for key in request.vars.keys():
				if key.startswith("fieldname_"): checkbox.append(key)
		if isinstance(checkbox, str): checkbox = [checkbox]
		response = urllib2.urlopen(url,timeout=30)
		data = response.read()
		soup = BeautifulSoup(data)
		tags = soup.findAll("div")
		tablename = request.vars.tablename
		table = cms.define_table(tablename)
		i = 1
		for tag in tags:
			if tag.contents:
				if not tag.has_attr('id'): tag['id'] = "div%s"%i
				if id==tag['id']:
					elems = tag.findAll()
					k = 0
					content = TABLE(TR(TH(T("Content crawler")),TH(T("Field name"))),_class='table table-striped defview')
					for elem in elems: 
						if elem.get_text():
							key = "fieldname_%s_%s"%(k,elem.name)
							if key in checkbox:
								ops = [OPTION(T("Publish on"),_value="publish_on")]
								for field in table.fields:
									if (field !="id") & (not table[field].type.startswith('reference')):
										if key in request.vars.keys():
											selected = (field==request.vars[key])
										else: selected = False
										ops.append(OPTION(table[field].label,_value=field,_selected=selected))
								select = SELECT(ops,_name=key,_id=key)

								for img in elem.findAll(src=True):
									href = img["src"]
									if not href.startswith(rooturl):
										if (href.startswith("/")):
											href = rooturl + href
											img["src"] = href
								
								tr = TR(TD(XML(elem.prettify())),TD(select))
								content.append(tr)
							k+=1
					return str(content)+"</input><input type='hidden' id='divid' value='%s'></input>"%id
				i+=1
		return "Not found div id="+id
	except Exception, e:
		return e
		
def update():
	id = request.args(0)
	settings = {}
	for key in request.vars.keys(): settings[key]=request.vars[key]
	from plugin_crawler import Crawler
	c = Crawler()
	table = c.define_crawler(True)
	if id:	
		table(id).update_record(name=request.vars.name,settings=settings)
	else:
		id = table.insert(name=request.vars.name,settings=settings)	
	redirect(URL(f="edit.html",args=[id]),client_side=True)

def getFieldUpdate(settings):
	from plugin_app import select_option
	tablename = settings.get("tablename")
	if not tablename: return ""
	table = cms.define_table(tablename)
	th = TR(TH(T("Process name")),TH(T("Publish time")),TH(T("Expired time")))
	tr = TR(TD(widget_process(settings.get("process"))),TD(INPUT(_name="publish_on",_class="datetime")),TD(INPUT(_name="expired_on",_class="datetime")))
	keys = ["process","crawlerid","publish_on","expired_on"]
	for field in table.fields:
		if table[field].type.startswith('reference'):
			keys.append(field)
			value = settings.get(field)
			if value.isdigit(): value = int(value)
			ref= table[field].type.split(' ')[-1]
			if 'label' in cms.db[ref].fields: name = 'label'
			elif 'name' in cms.db[ref].fields: name = 'name'
			else: name = cms.db[ref].fields[-1]
			select = SELECT(['']+select_option(cms.db,auth,ref,selected=[value],field=name),_name=field,_id=field)
			th.append(TH(T(field.capitalize()),_class="field_label"))
			tr.append(TD(select))
	ajax = "ajax('%s',%s,'analyse_result')"%(URL(f='updatecrawler',args=request.args),keys)
	bt = INPUT(_type='button',_value=T('Cập nhật dữ liệu'),_class="btn btn-primary",_onclick=ajax)		
	return DIV(TABLE(th,tr,_class='table table-striped defview'), bt)
	
def crawlerurl():
	import datetime		
	t1 = datetime.datetime.now()
	try:
		id = request.args(0)
		from plugin_crawler import Crawler
		c = Crawler(id=id)
		table = c.define_crawlerdata(True)
		maxDeep = int(request.vars.maxDeep)	
		maxLink = int(request.vars.maxLink)	
		timeOut = int(request.vars.timeOut)	
		if request.vars.crawler:
			nb = c.getURL(url=request.vars.urllink,maxDeep=maxDeep,maxLink=maxLink,timeOut=timeOut,listLink=[])
		query = (table.crawler==id)&(table.table_id==None)
		rows = c.db(query).select(orderby=~table.id,limitby=(0,int(maxLink)))
		content = TABLE(_class='table table-striped defview',_width="50%")
		content.append(TR(TH(INPUT(_type="checkbox",_name="check_all",_id="check_all",_onclick="CheckAll();")),TH(T("Chọn tất cả"))))
		i = 1
		for row in rows:
			content.append(TR(TH(INPUT(_type="checkbox",_value=row.id,_name="crawlerid")),TH(A(row.urllink,_href=row.urllink))))
			if row.textcontent:
				d = eval(row.textcontent)
				for key in d.keys():
					content.append(TR(TD(key),TD(XML(d[key]))))
			i+=1
		table = c.define_crawler()
		settings = eval(table(id).settings)
		content = DIV(getFieldUpdate(settings),DIV(content,_id="crawler_result"))
		return content
	except Exception, e:
		return e
						
def updatecrawler():
	try:
		id = request.args(0)
		from plugin_crawler import Crawler
		c = Crawler(id=id)
		table = c.define_crawlerdata()
		rows = c.db((table.crawler==id)).select()
		for key in request.vars.keys(): c.settings[key] = request.vars[key]
		ids = request.vars.crawlerid
		if isinstance(ids,str): ids = [ids]
		list_id = update_cms(c.settings,ids)
		update_process(c.settings,list_id)
		tablename = c.settings.get("tablename")
		return T("Cập nhật thành công!")
	except Exception, e:
		return "updatecrawler:",e

def update_cms(settings,ids):
	rooturl = settings.get("rooturl")
	tablename = settings.get("tablename")
	t = cms.define_table(tablename)
	fields = t.fields
	fields.remove("id")
	
	publish = False
	from plugin_process import ProcessModel
	p = ProcessModel()
	id = settings.get("process")
	process = p.define_process()
	if process(id).url:
		if process(id).url.startswith("publish"): 
			publish = True
			from dateutil import parser
			from plugin_cms import CmsPublish
			cmsp = CmsPublish()			
			expired_on = settings.get("expired_on")
	from plugin_crawler import Crawler
	c = Crawler(id=request.args(0))
	table = c.define_crawlerdata()
	list_id = []
	for id in ids:
		try:
			row = table(id)
			d = eval(row.textcontent)
			val = {}
			for field in fields:
				if field in d.keys(): 
					if field=="htmlcontent":
						val[field], avatar = update_link(d[field],"uploads/"+tablename,rooturl)
						if "avatar" in fields: val["avatar"] = avatar
					else: val[field] = d[field]
				elif field in settings.keys(): val[field] = settings[field]
			newid = t.insert(**val)
			if publish: 
				publish_on = settings.get("publish_on", request.now)
				if not publish_on: 
					publish_on = d.get("publish_on")
					if publish_on: 
						try: 
							publish_on = parser.parse(publish_on,dayfirst=True,fuzzy=True)
						except Exception, e: 
							print "Datetime error:", e
							publish_on = request.now
				cmsp.publish(tablename,newid,publish_on,expired_on)
			list_id.append(newid)
			row.update_record(tablename=tablename,table_id=newid)
			c.db.commit()
			cms.db.commit()
		except Exception, e:
			print "update_cms", e
	return list_id
		
def update_process(settings,list_id):	
	from plugin_process import Process
	p = Process()
	tablename = settings.get("tablename")
	process = settings.get("process")
	folder_id = settings.get("folder")
	folder = cms.define_folder()
	folder_name = folder(folder_id).name
	objects = p.define_objects()
	log = p.define_process_log()
	for table_id in list_id:
		objects_id = objects.insert(folder=folder_id,foldername=folder_name,tablename=tablename,table_id=table_id,auth_group=p.auth_group,process=process)
		log.insert(objects=objects_id,auth_group=p.auth_group,process=process)
		
def update_link(textcontent,path,rooturl):
	if rooturl.endswith("/"): rooturl = rooturl[:-1]
	soup = BeautifulSoup(textcontent)
	avatar = ""
	for img in soup.findAll("img",src=True):
		url = save_link(path,img["src"])
		if url: 
			img["src"] = url
			if not avatar: avatar = str(url.split("/")[-1])
	tags = soup.findAll("a",href=True)
	for tag in tags:
		href = tag["href"]
		if (href.find("javascript:")==-1)&(href.find("mailto:")==-1)&(href.find("#")==-1):
			if (not href.startswith(rooturl))&(not href.startswith("http://"))&(not href.startswith("https://")):
				if (href.startswith("/")): href = rooturl + href
				else: href = rooturl + "/" + href
			if href.startswith(rooturl):
				website = urllib2.urlopen(href,timeout=30)
				if website: 
					http_message = website.info()
					if http_message.type !="text/html": 
						url = save_link(path,href)
						if url: tag["href"] = url
	return soup.prettify(), avatar
	
def save_link(path,urllink):
	try:
		filename = path+"/"+urllink.split("/")[-1]
		urllib.urlretrieve(urllink,request.folder+"/static/"+filename)
		return "/%s/static/%s"%(request.application,filename)	
	except Exception, e:
		print 'save_link', e
		return None
		
def update_avatar():
	tablename = request.vars.tablename
	table = cms.define_table(tablename)
	if ("avatar" in table.fields)&("htmlcontent" in table.fields):
		rows = cms.db(table.avatar==None).select()
		for row in rows:
			soup = BeautifulSoup(row.htmlcontent)
			tag = soup.find("img",src=True)
			if tag: 
				img = str(tag["src"].split("/")[-1])
				row.update_record(avatar=img)
	redirect(URL(f="geturl",args=request.args))	
	