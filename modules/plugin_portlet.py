###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 1.0 Date: 24/01/2015
###################################################
# -*- coding: utf-8 -*-

import os, datetime
import cStringIO
import re
import urllib2
from bs4 import BeautifulSoup
from gluon import current, LOAD, redirect
from gluon.dal import Field
from html import *
from validators import IS_IN_DB, IS_IN_SET,IS_NULL_OR
from plugin_app import select_option, get_short_string
from gluon.sqlhtml import SQLFORM
from plugin_ckeditor import CKEditor
T = current.T
PortletType = [('table',T('Data table'),'fa-database'),('replace',T('Replace'),'fa-slack'),('load',T('Load url'),'fa-download'),('html',T('HTML code'),'fa-list-alt'),('view',T('View code'),'fa-codepen'),('banner',T('Banner'),'fa-photo'),('rss',T('RSS'),'fa-rss'),('service',T('Webservice'),'fa-exchange')]
PortletViewType = [('news',T('News'),'fa-list'),('archives',T('Archives'),'fa-file-pdf-o'),('image',T('Image'),'fa-photo'),('video',T('Video'),'fa-video-camera'),('banner',T('Banner'),'fa-flag'),('other',T('Other view'),'fa-sliders')]
PortletStyle = [("font-family",['sans-serif', 'serif', 'arial']),("font-size",[str(i) for i in range(8,32)]),("font-style",['normal','italic','oblique','initial','inherit']),("color",['red','black','white','blue','gray'])]

SEARCHKEY = "searchkey"

		
def setting_config(key=None,default={},path=None):
	try:
		if not path: path=os.path.join(current.request.folder,'config.py')
		file = open(path,'r')
		data = file.read().replace(chr(13),'')
		file.close()
		tmp = eval(data)
		if not key: return tmp
		return tmp[key]
	except Exception, e:
		print "setting ->", e
		return default	

class PortletModel:
	def __init__(self,cms,**attr):
		self.cms = cms
		self.db = self.cms.db		
		self.auth = attr.get('auth',None)

	def define_portlet(self,migrate=False):	
		if 'portlet' not in self.db.tables:
			portlettypes = [type[:2] for type in PortletType]
			viewtypes = [type[:2] for type in PortletViewType]
			self.db.define_table('portlet',
				Field('portlettype',requires=IS_IN_SET(portlettypes)),
				Field('portletview',requires=IS_NULL_OR(IS_IN_SET(viewtypes))),
				Field('name'),
				Field('settings','text',writable=False),
				Field('textcontent','text',default=''),
				Field('htmlcontent','text',default=''),
				migrate=migrate,redefine=migrate)
		return self.db.portlet

	def define_portletview(self,migrate=False):	
		if 'portletview' not in self.db.tables:
			viewtypes = [type[:2] for type in PortletViewType]
			self.db.define_table('portletview',
				Field('portlettype',requires=IS_IN_SET(viewtypes)),
				Field('name',required=True),
				Field('htmlcontent','text',default=''),
				Field('jsfile','list:string',default=[]),
				Field('cssfile','list:string',default=[]),
				migrate=migrate)
		return self.db.portletview
					
	def get_settings(self,table,id):
		db = self.db
		try:
			settings = db[table](id).settings
			settings = eval(settings)
		except Exception, e:
			settings = {}
		return 	settings
			
			
class Portlet(PortletModel):

	def display(self,id):
		try:
			db = self.db
			table = self.define_portlet()
			row = table(id)
			settings = self.get_settings('portlet',id)
			textcontent = row.textcontent or ""
			htmlcontent = row.htmlcontent or ""
			portlettype = row.portlettype
			if portlettype=='table':
				content = self.portlet_render(textcontent,settings,htmlcontent)	
			elif portlettype=='replace':
				content = self.portlet_replace(textcontent,settings)	
			elif portlettype=='html':
				content = current.response.render(cStringIO.StringIO(htmlcontent), {})
			elif portlettype=='view':
				content = current.response.render(cStringIO.StringIO(htmlcontent), {})
			elif portlettype=='banner':
				content = self.portlet_banner(settings)	
			elif portlettype=='load':
				url = settings.get('url')
				if url:
					url = URL(r=current.request,c='plugin_portlet',f='get_url',args=current.request.args,vars=dict(url=url))
				else:	
					url = URL(r=current.request,c=settings.get('c'),f=settings.get('f'),args=current.request.args,vars=current.request.vars)
				img = URL(r=current.request,c='static',f='images/loading.gif')
				content = "<div id='portletid_%s'><img src='%s'></img></div><script>$( '#portletid_%s' ).load('%s')</script>"%(id,img,id,url)
			elif portlettype=='service':
				url = URL(r=current.request,c="plugin_portlet",f="webservice",args=[id])
				img = URL(r=current.request,c='static',f='images/loading.gif')
				content = "<div id='portletid_%s'><img src='%s'></img></div><script>$( '#portletid_%s' ).load('%s')</script>"%(id,img,id,url)
			elif portlettype=='rss':
				url = URL(r=current.request,c="plugin_portlet",f="rss",args=[id])
				img = URL(r=current.request,c='static',f='images/loading.gif')
				content = "<div id='portletid_%s'><img src='%s'></img></div><script>$( '#portletid_%s' ).load('%s')</script>"%(id,img,id,url)
			content += settings.get("style_script","")
			if settings.get("classname",None):
				return DIV(XML(content),_class='ivinh_display '+str(settings.get("classname")),_id='display_%s'%(id) )
				
			content = "<!-- Start display_%s--> %s <!-- End display_%s--> "%(id,content,id)
			return DIV(XML(content),_class='ivinh_display',_id='display_%s'%(id))
		except Exception, e:
			return 'Portlet ID=%s, error: %s'%(id,e)
			
	def display_no_wr(self,id):
		try:
			db = self.db
			table = self.define_portlet()
			row = table(id)
			settings = self.get_settings('portlet',id)
			textcontent = row.textcontent or ""
			htmlcontent = row.htmlcontent or ""
			portlettype = row.portlettype
			if portlettype=='table':
				content = self.portlet_render(textcontent,settings,htmlcontent)	
			elif portlettype=='replace':
				content = self.portlet_replace(textcontent,settings)	
			elif portlettype=='html':
				content = htmlcontent	
			elif portlettype=='view':
				content = current.response.render(cStringIO.StringIO(htmlcontent), {})
			elif portlettype=='banner':
				content = self.portlet_banner(settings)	
			elif portlettype=='load':
				url = settings.get('url')
				if url:
					url = URL(r=current.request,c='plugin_portlet',f='get_url',args=current.request.args,vars=dict(url=url))
				else:	
					url = URL(r=current.request,c=settings.get('c'),f=settings.get('f'),args=current.request.args,vars=current.request.vars)
				img = URL(r=current.request,c='static',f='images/loading.gif')
				content = "<div id='portletid_%s'><img src='%s'></img></div><script>$( '#portletid_%s' ).load('%s')</script>"%(id,img,id,url)
			elif portlettype=='service':
				url = URL(r=current.request,c="plugin_portlet",f="webservice",args=[id])
				img = URL(r=current.request,c='static',f='images/loading.gif')
				content = "<div id='portletid_%s'><img src='%s'></img></div><script>$( '#portletid_%s' ).load('%s')</script>"%(id,img,id,url)
			elif portlettype=='rss':
				url = URL(r=current.request,c="plugin_portlet",f="rss",args=[id])
				img = URL(r=current.request,c='static',f='images/loading.gif')
				content = "<div id='portletid_%s'><img src='%s'></img></div><script>$( '#portletid_%s' ).load('%s')</script>"%(id,img,id,url)
			content += settings.get("style_script","")
			# content = "<!-- Start display_%s--> %s <!-- End display_%s--> "%(id,content,id)
			
			return XML(content)
		except Exception, e:
			return 'Portlet ID=%s, error: %s'%(id,e)
			
	def preview(self,id):
		return self.display(id)
			
	def portlet_replace(self,textcontent,settings):
		cms = self.cms
		db = cms.db
		rows = self.portlet_rows(settings)
		table = settings.get('table')
		fields = settings.get('fields',[])
		content = ''
		for row in rows:
			tmp = textcontent
			for field in fields:
				key = settings.get('map_%s'%field,None)
				value =cms.field_format(row,field,db[table][field].type,settings) if key else row[field]
				tmp = tmp.replace(key,value)
			content += tmp			
		return content

	def portlet_banner(self,settings):	
		request = current.request
		content = UL()
		tmp = {}
		i = 1
		for key in settings.keys():
			if key.startswith("banner_"): 
				tmp["%s_%s"%(settings[key].get("position",1),i)] = key
				i += 1
		keys = tmp.keys()
		keys.sort()
		for key in keys:
			add = True
			value = settings[tmp[key]]
			publish_on = value.get("publish_on","")
			expired_on = value.get("expired_on","")
			folder = value.get("folder","")
			if publish_on:
				publish_on = publish_on.split(".")[0]
				publish_on = datetime.datetime.strptime(publish_on, "%Y-%m-%d %H:%M:%S")
				if request.now < publish_on: add = False
			if expired_on:
				expired_on = expired_on.split(".")[0]
				expired_on = datetime.datetime.strptime(expired_on, "%Y-%m-%d %H:%M:%S")
				if request.now > expired_on: add = False
			if folder:
				if folder != request.args(0): add = False
			if add:	
				htmlcontent = XML(value.get("htmlcontent",""))
				link = value.get("link","")
				if link:
					if link[0:7] != 'http://':
						link = 'http://%s/%s/%s'%(request.env.http_host,request.application,link)
					htmlcontent = A(htmlcontent,_href=link)
				content.append(LI(htmlcontent))
		if str(content)=="UL()": return ""
		return content
		
	def portlet_render(self,textcontent,settings,htmlcontent=''):
		query = self.get_query(settings)
		rows = self.portlet_rows(settings,query)
		if len(rows)==0: 
			if settings.get('return_folder',"")=="on":	
				folder = self.cms.define_folder()	
				row_folder = self.cms.db(folder.name==current.request.args(0)).select().first()
				div = DIV(DIV(DIV(row_folder.label,_class="pull-left"),_class='title_page'))
				div.append(DIV(current.T("Folder no data"),_class='box_content'))
				return div
			else:
				return DIV(current.T("No data"),_class='no_data')
		row = rows[0]		
		context = dict(cms=self.cms,rows=rows,row=row,settings=settings,table=settings.get('table'),query=query)
		content = ""
		textcontent = cStringIO.StringIO(textcontent)
		try:
			content = current.response.render(textcontent, context)
		except Exception, e:
			print "portlet_render: ", e
		if settings.get('pagination',"")=="on":	
			page = self.cms.get_page()
			length = int(settings.get('limitby',5))
			count = self.cms.db(query).count()
			content += str(self.pagination(page,length,count))
		return content
			
	def portlet_rows(self,settings,query):
		cms = self.cms
		db = cms.db
		table = settings.get('table','news')
		if not cms.define_table(table): return ''
		orderby = settings.get('orderby',None)
		if orderby:
			orderby = ~db[table][orderby[1:]] if orderby[0]=='~' else db[table][orderby]
		else:
			orderby = ~db[table].id
		length = int(settings.get('limitby',5))
		startby = int(settings.get('startby',0))
		if settings.get('pagination',"")=="on":
			page = cms.get_page()
			p1 = (page-1)*length
			p2 = page*length
			limitby=(p1,p2)
		else:
			limitby=(startby,length)
		rows = db(query).select(db[table].ALL,orderby=orderby,limitby=limitby,distinct=True)
		return rows	

	def get_query(self,settings):
		cms = self.cms
		db = cms.db
		table = settings.get('table','news')
		if not cms.define_table(table): return ''
		dcontent = cms.define_dcontent()
		query = settings.get('query',(db[table].id>0))
		if query == "": query = (db[table].id>0)
		if isinstance(query,str): query = eval(query)
		folder = settings.get('folder',None)
		if settings.get('cmsquery',"")=="on":
			query&=cms.get_query(None,table)
			if cms.get_link(): query &= (dcontent.link==cms.get_link())&(dcontent.dtable==table)&(dcontent.table_id==db[table].id)
		else:
			if folder:
				query &= cms.get_query(folder,table)
			if settings.get('publishonly',"")=="on":
				query &=((dcontent.dtable==table)&(dcontent.table_id==db[table].id))
				query &=((dcontent.expired_on>=current.request.now)|(dcontent.expired_on==None))&(dcontent.publish_on<=current.request.now)
				
		vsearch = current.request.vars.get(SEARCHKEY)			
		q = None		
		for field in db[table].fields:
			if field != 'folder':
				v = settings.get(field,None)
				if not v:
					if settings.get("use_request"): v = current.request.vars.get(field)
				if v: query &= (db[table][field]==v)
			if vsearch:
				if db[table][field].type in ["string","text",'list:string']:
					if q: q = q|db[table][field].contains(vsearch)
					else: q = db[table][field].contains(vsearch)
		if q: query &= q
		
		return query	
		
	def pagination(self,page,length,count):
		PAGE = 1
		T = current.T
		request = current.request
		args = request.args		
		if len(args) < PAGE: return ''
		elif len(args) == PAGE: args.append('1.html')
		if count<=length: return ''
		if length>0:
			tmp = int(count/length)
			if count > tmp*length: pagecount = tmp+1
			else: pagecount = tmp
		content = DIV(_id='page')
		ul = UL(_class='page-ul pagination')
		(p1, m1) = (page - 5,'...') if page > 5 else (1, '')
		(p2, m2) = (page + 5,'...') if page + 5 < pagecount else (pagecount+1, '')
		if (p2 < 11) & (pagecount >10): p2 = 11
		if m1=='...':
			args[PAGE]='1.html'
			# url = URL(r=request,args=args,vars=request.vars)
			url ='../'+ request.args(0) +'/1.html'
			ul.append(LI(A(T('First page'),'  ',_href=url)))
			ul.append(LI(A(m1)))
		for x in xrange(p1,p2):
			args[PAGE]='%s.html'%x
			# url = URL(r=request,args=args,vars=request.vars)
			url ='../'+ request.args(0) +'/%s.html'%x
			ul.append(LI(A(x,'  ',_href=url),_class='active' if x == page else ''))
		if m2=='...':
			ul.append(LI(A(m2)))
			args[PAGE]='%s.html'%pagecount
			# url = URL(r=request,args=args,vars=request.vars)
			url ='../'+ request.args(0) +'/%s.html'%pagecount
			ul.append(LI(A(T('End page'),_href=url)))
		content.append(ul)
		return content			
			
class PortletManage(Portlet):

	def select_type(self):
		settings = {}
		id = current.request.args(0)
		if id:
			portlettype = self.db.portlet(id).portlettype
			if portlettype=='load':
				settings = self.get_settings('portlet',id)
				return self.select_controller(settings.get('c',''),settings.get('f',''),settings.get('url',''))
			elif portlettype=='table':
				return self.select_table()
			elif portlettype=='html':
				return self.html(id)
			elif portlettype=='view':
				return self.html(id,ck=False)
			elif portlettype=='banner':
				return DIV(DIV(self.banner_update(id),_id="portletbanner"),DIV(self.banner_form(id),_id="portletbannerform"))
			elif portlettype=='service':
				return self.service(id)
			elif portlettype=='rss':
				return self.url_rss(id)
				
		ajax = "ajax('%s', ['portlettype'], 'portletchoice')"%(URL(r=current.request,f='select_type',args=current.request.args))
		content = DIV(BR(),_class='portlettype')
		for type in PortletType:
			content.append(INPUT(_type='radio',_name='portlettype',_value=type[0],_onclick=ajax,_style="margin-left:15px;"))
			content.append(I(type[1]))
		content.append(DIV(_id='portletchoice',_class='portletchoice'))
		return content

	def select_controller(self,controller='',function='',url=''):	
		files = []
		for root, dirs, files in os.walk(current.request.folder+'/controllers'):
			pass
		op = ['']
		for file in files:
			c = file.replace('.py','')
			op.append(OPTION(c,_value=c,_selected=(c==controller)))
		if url:
			url1 = URL(r=current.request,c='plugin_portlet',f='set_url',args=current.request.args,vars=dict(url=url))
		elif function != '': 
				url1 = URL(r=current.request,c=settings.get('c'),f=settings.get('f'),args=current.request.args,vars=current.request.vars)
		else: url1 = ""
		if url1:
			id = current.request.args(0)
			img = URL(r=current.request,c='static',f='images/loading.gif')
			load = XML("<div id='portletid_%s'><img src='%s'></img></div><script>$( '#portletid_%s' ).load('%s')</script>"%(id,img,id,url1))
		else: load = ""
		ajax = "ajax('%s',['c'],'function')"%(URL(r=current.request,f='select_function',args=current.request.args))	
		content = TABLE(_class='table table-striped defview')
		content.append(TR(TD(T('Url link')),TD(INPUT(_name='url',_value=url,_class="string text_urllink",_style="width:500px;"))))
		content.append(TR(TD('Controller'),TD(SELECT(op,_name='c',_id='controller',_onchange=ajax,_class="select_controller"))))
		content.append(TR(TD('Function'),TD(DIV(self.select_function(controller,function),_id='function'))))
		content = FORM(content,_action=URL(r=current.request,c='plugin_portlet',f='update_settings',args=current.request.args))
		content.append(INPUT(_type='submit',_value=T('Submit'),_class="btn btn-primary"))
		content.append(INPUT(_type='button',_value=T('Analyse'),_class="btn btn-primary",_onclick="analyse();"))
		content.append(DIV(_id='analyse_result'))
		content.append(DIV(load,_id='preview'))
		return content
		
	def select_function(self,controller,function=''):		
		if controller=='': return ''
		try:
			filename = "%s/controllers/%s.py"%(current.request.folder,controller)
			f = open(filename)	
			expr = r"def \w+\(\)"
			funcs = re.findall(expr,f.read())
			f.close()
			op = ['']
			for f in funcs:
				f = f.replace('def ','').replace('()','')
				op.append(OPTION(f,_value=f,_selected=(f==function)))
			ajax = "ajax('%s',['f'],'preview')"%(URL(r=current.request,f='load_function',args=current.request.args,vars=dict(c=controller)))	
			content = SELECT(op,_name='f',_id='function',_onchange=ajax)
			return content
		except Exception, e:
			return e

	def url_rss(self,id):	
		settings = self.get_settings('portlet',id)
		url = settings.get("url","")
		table = TABLE(_class='table table-striped defview')
		table.append(TR(TD("Rss url"),TD(INPUT(_name='url',_value=url,_class="string text_urllink",_style="width:500px;"))))
		table.append(TR(TD("Rss length"),TD(INPUT(_name='length',_value=settings.get("length","10"),_class="integer"))))
		content = DIV()
		ajax = "ajax('%s',['url','length'],'rss_result')"%(URL(r=current.request,f='rss_preview',args=current.request.args))	
		content.append(INPUT(_type='button',_value=T('Preview RSS'),_class="btn btn-primary",_onclick=ajax))
		ajax = "ajax('%s',['url'],'rss_result')"%(URL(r=current.request,f='get_rss',args=current.request.args))	
		content.append(INPUT(_type='button',_value=T('Submit'),_class="btn btn-primary",_onclick=ajax))
		table.append(TR(TD(),TD(content)))
		if url:
			url1 = URL(r=current.request,f='rss',args=[id])
			img = URL(r=current.request,c='static',f='images/loading.gif')
			load = XML("<div id='portletid_%s'><img src='%s'></img></div><script>$( '#portletid_%s' ).load('%s')</script>"%(id,img,id,url1))
		else: load = ""		
		content = DIV(table, DIV(load,_id='rss_result'))
		return content
			
	def select_table(self,table=''):
		self.cms.define_tables()
		db = self.db
		settings = {}
		id = current.request.args(0)
		if id:
			settings = self.get_settings('portlet',id)
			table = settings.get('table',table)
		
		option = []
		for name in db.tables:
			row = db(db.dtable.name==name).select().first()
			if row:
				if row.publish: 
					option.append(OPTION(T(name),_value=name,_selected=(name==table)))
		
		ajax = "ajax('%s', ['table'], 'select_fields')"%(URL(r=current.request,f='select_fields',args=current.request.args))
		select = SELECT(['']+option,_name='table',_onchange=ajax,_class="portletslecttable")
		content = DIV(BR(),SPAN(T("Table data source"))," ",select,DIV(self.select_fields(table,settings) if table else T('Pls select one table!'),_id='select_fields'))
		return content
		
	def select_fields(self,table,settings={}):
		db = self.db
		self.cms.define_table(table)		
		orderby = settings.get('orderby','')
		limitby = settings.get('limitby',5)
		startby = settings.get('startby',0)
		fields = settings.get('fields',[])
		images = settings.get('images',db[table].fields)
		view = settings.get('view','list')
		return_folder = settings.get('return_folder','')
		if isinstance(fields,str): fields = [fields]
		if isinstance(images,str): images = [images]
		fields_url = settings.get('fields_url',[])
		if isinstance(fields_url,str): fields_url = [fields_url]
		url = settings.get('url','')
	
		select = TABLE(_class='table table-striped defview')
		tr = TR(TH(T('Field name')),TH(T('Display')),TH(T('Is link')),TH(T('Order up')),TH(T('Order down')),TH(T('Length/Format/Size')),TH(T('Header')))
		select.append(tr)
		tablefields = db[table].fields
		tablefields.remove("id")
		for field in tablefields:
			tr = TR(TD(T(field.capitalize()),_class="field_label"))
			tr.append(TD(INPUT(_type='checkbox',_name='fields',_value=field,_checked=(field in fields))))
			tr.append(TD(INPUT(_type='checkbox',_name='fields_url',_value=field,_checked=(field in fields_url))))
			tr.append(TD(INPUT(_type='radio',_name='orderby',_value=field,_checked=(orderby==field))))
			tr.append(TD(INPUT(_type='radio',_name='orderby',_value='~%s'%field,_checked=(orderby=='~%s'%field))))
			if (db[table][field].type in ['upload'])|(field in ['avatar','image']):
				options = [OPTION(T(f),_value=f,_selected=(f==settings.get('size_%s'%field,'default') )) for f in setting_config('img_size',{'default'})]
				tr.append(TD(T('Image'),INPUT(_type='checkbox',_name='images',_value=field,_checked=(field in images)),T('|| Size'),SELECT(options,_name='size_%s'%(field) )))
				# tr.append(TD(INPUT(_type='checkbox',_name='images',_value=field,_checked=(field in images)),T('Image')))
			elif db[table][field].type in ['string','text']:
				tr.append(TD(INPUT(_name='length_%s'%field,_class='integer',_value=settings.get('length_%s'%field,''))))
			elif db[table][field].type.startswith('reference'):
				ref= db[table][field].type.split(' ')[-1]
				options = [OPTION(T(f),_value=f,_selected=(f==settings.get('reference_%s'%field,'name'))) for f in db[ref].fields]
				tr.append(TD(SELECT(options,_name='reference_%s'%field)))
			else:	
				tr.append(TD(INPUT(_name='format_%s'%field,_class='string',_value=settings.get('format_%s'%field,''))))
			tr.append(TD(INPUT(_name='header_%s'%field,_class='header string',_value=settings.get('header_%s'%field,''))))
			select.append(tr)
		form = FORM(select,_action=URL(r=current.request,f='update_settings',args=current.request.args,vars=dict(table=table)))	
		
		t = TABLE(_class='table table-striped defview')
		
		t.append(TR(TD(T('Record start'),_class="field_label"),TD(INPUT(_name='startby',_value=startby,_class="integer"))))		
		t.append(TR(TD(T('Length'),_class="field_label"),TD(INPUT(_name='limitby',_value=limitby,_class="integer"))))		
		t.append(TR(TD(T('Pagination?'),_class="field_label"),TD(INPUT(_type="checkbox",_name='pagination',_checked=(settings.get('pagination')=="on")))))
		t.append(TR(TD(T('Out link'),_class="field_label"),TD(INPUT(_name='url',_value=url),_id='url',_class="string")))
		
		auth = self.auth or current.globalenv['auth']

		for field in db[table].fields:
			if db[table][field].type.startswith('reference'):
				value = settings.get(field,'0')
				if value.isdigit(): value = int(value)
				ref= db[table][field].type.split(' ')[-1]
				if 'label' in db[ref].fields: name = 'label'
				elif 'name' in db[ref].fields: name = 'name'
				else: name = db[ref].fields[-1]
				select = SELECT(['']+select_option(db,auth,ref,selected=[value],field=name),_name=field)
				t.append(TR(TD(T(field.capitalize()),_class="field_label"),TD(select)))
		
		t.append(TR(TD(T('Query'),_class="field_label"),TD(INPUT(_name='query',_value=settings.get('query',''),_class="string"))))
		t.append(TR(TD(T('Add Cms query'),_class="field_label"),TD(INPUT(_type="checkbox",_name='cmsquery',_checked=(settings.get('cmsquery')=="on")))))
		t.append(TR(TD(T('Use request vars'),_class="field_label"),TD(INPUT(_type="checkbox",_name='use_request',_checked=(settings.get('use_request')=="on")))))
		dtable = self.cms.get_dtable(table)
		if dtable:
			if dtable.publish:
				t.append(TR(TD(T('Publish data only'),_class="field_label"),TD(INPUT(_type="checkbox",_name='publishonly',_checked=(settings.get('publishonly')=="on")))))
		t.append(TR(TD(T('View style'),_class="field_label"),TD(T('Table'),INPUT(_type='radio',_name='view',_value='table',_checked=(view=='table')),T('List'),INPUT(_type='radio',_name='view',_value='list',_checked=(view=='list')),_id='limitby')))
		
		t.append(TR(TD(T('No data return'),_class="field_label"),TD(T('folder name'),INPUT(_type='radio',_name='return_folder',_value='folder name',_checked=(return_folder=='folder_name')),T('Folder data'),INPUT(_type='radio',_name='return_folder',_value='folder_data',_checked=(return_folder=='folder_data')),T('Not data'),INPUT(_type='radio',_name='return_folder',_value='no_data',_checked=(return_folder=='')),_id='limitby')))

		form.append(t)
		form.append(INPUT(_type='submit',_value=T('Submit'),_class="btn btn-primary"))
		return form

	def widget_file(self,field,value):	
		import os
		if value:
			from plugin_cms import get_setting
			js = get_setting(value,"jsfile",[])
			css = get_setting(value,"cssfile",[])
		else:
			js, css = [], []
		files = []
		for root, dirs, files in os.walk(current.request.folder+'/static/portlet/js'):
			pass
		content = DIV(_class="checkbox",_id="jsfile")
		for file in files:
			if file.split(".")[-1]=="js":
				label = LABEL(INPUT(_type="checkbox",_name="jsfile",_value=file[:-3],_checked=(file[:-3] in js),_class="boolean"))
				label.append(file[:-3])
				content.append(SPAN(label,_style="margin-right:20px;"))
		files = []
		for root, dirs, files in os.walk(current.request.folder+'/static/portlet/css'):
			pass
		content2 = DIV(_class="checkbox",_id="cssfile")
		for file in files:
			if file.split(".")[-1]=="css":
				label = LABEL(INPUT(_type="checkbox",_name="cssfile",_value=file[:-4],_checked=(file[:-4] in css),_class="boolean"))
				label.append(file[:-4])
				content2.append(SPAN(label,_style="margin-right:20px;"))
		return DIV(B(current.T("Add js file")),content,B(current.T("Add css file")),content2,TEXTAREA(value=value,_name="settings",_hidden=True))
	
		
	def html(self,id=None,ck=True,fieldedit="htmlcontent"):
	
		for field in self.db.portlet.fields:
			self.db.portlet[field].readable = False
			self.db.portlet[field].writable = False
		self.db.portlet.settings.writable = True
		self.db.portlet.settings.widget = self.widget_file
		if fieldedit:
			self.db.portlet[fieldedit].writable = True
			if ck: self.db.portlet[fieldedit].widget=CKEditor(self.db).widget
		form = SQLFORM(self.db.portlet,id,showid=False)
		form[0][0][0][0] = ""
		if form.process().accepted:
			settings = eval(form.vars.settings or "{}")
			add = False
			if form.vars.jsfile:
				settings["jsfile"] = form.vars.jsfile if isinstance(form.vars.jsfile,list) else [form.vars.jsfile]
				add = True
			if form.vars.cssfile:
				settings["cssfile"] = form.vars.cssfile if isinstance(form.vars.cssfile,list) else [form.vars.cssfile]
				add = True
			if add: self.db.portlet(id).update_record(settings=str(settings))
			current.response.flash = T('Update True')
			# redirect(URL(r=current.request,c='plugin_portlet',f='setting_view',args=current.request.args))
		return form

	def service(self,id):
		settings = eval(self.db.portlet(id).settings or "{}")
		link = SPAN(LABEL(current.T("WSDL Location"),_style="margin-right:5px;"),INPUT(_name="location",_class='string',_value=settings.get("location"),_placeholder="http://",_style="width:500px;margin-right:10px;"))
		form = FORM(link,_class="navbar-form")
		ajax = "ajax('%s', ['location'], 'get_service_info')"%(URL(r=current.request,f='get_service',args=[id]))
		form.append(INPUT(_type='button',_value=T('Test'),_class="btn btn-primary",_onclick=ajax))	
		form.append(DIV(_id="get_service_info"))
		return form
		
	def banner_form(self,id,key=None):	
		if key:
			settings = eval(self.db.portlet(id).settings or "{}")
			settings = settings[key]
		else: 
			settings = {}
		self.cms.define_folder()	
		select = SELECT(['']+select_option(self.db,self.auth,"folder",id=None,selected=[settings.get("folder")],field='label',field_id="name"),_name="folder",_id="folder_select")
		folder = SPAN(LABEL(current.T("Folder show"),_style="margin-right:5px;"),select,_style="margin-right:10px;") 
		publish_on = SPAN(LABEL(current.T("Publish on"),_style="margin-right:5px;"),INPUT(_name="publish_on",_class='datetime',_value=settings.get("publish_on",current.request.now)),_style="margin-right:10px;")
		expired_on = SPAN(LABEL(current.T("Expired on"),_style="margin-right:5px;"),INPUT(_name="expired_on",_class='datetime',_value=settings.get("expired_on",'')),_style="margin-right:10px;")
		p = settings.get("position",'29')
		op = []
		for value in range(1,30):
			value = "0%s"%value if value<10 else str(value)
			op.append(OPTION(value,_selected=(value==p)))
		position = SPAN(LABEL(current.T("Position on"),_style="margin-right:5px;"),SELECT(op,_name="position",_class='string'))
		htmlcontent = CKEditor(self.db).editor("htmlcontent",settings.get("htmlcontent",''))
		link = SPAN(LABEL(current.T("Url link"),_style="margin-right:5px;"),INPUT(_name="link",_class='string',_value=settings.get("link",'')),_style="margin-right:10px;")
		form = FORM(htmlcontent,DIV(folder,publish_on,expired_on,position),DIV(link),_class="navbar-form")
		ajax = "ajax('%s', ['folder','publish_on','expired_on','htmlcontent','position','link'], 'portletbanner')"%(URL(r=current.request,f='banner_update',args=[id,key] if key else [id]))
		form.append(INPUT(_type='button',_value=T('Submit'),_class="btn btn-primary",_onclick=ajax))
		return form

	def banner_update(self,id,key=None,vars=None):
		import uuid
		row = self.db.portlet(id)
		if not row: return ""
		settings = eval(self.db.portlet(id).settings or "{}")
		if vars:
			bkey = "banner_%s"%uuid.uuid1().int if not key else key
			settings[bkey] = vars
			row.update_record(settings=str(settings))
			if key: redirect(URL(r=current.request,f="setting_data",args=[id]),client_side=True)
		content = UL()
		tmp = {}
		i = 1
		for key in settings.keys():
			if key.startswith("banner_"): 
				tmp["%s_%s"%(settings[key].get("position",1),i)] = (key,settings[key]["htmlcontent"])
				i += 1
		keys = tmp.keys()
		keys.sort()
		for key in keys:
			ajax = "ajax('%s', [], 'portletbannerform')"%(URL(r=current.request,f='banner_form',args=[id,tmp[key][0]]))
			soup = BeautifulSoup(tmp[key][1])
			tags = soup.findAll("a")
			for tag in tags: 
				tag["href"] = "#"
				tag["onclick"] = ajax
			content.append(LI(A(XML(soup.prettify()),_href="#",_onclick=ajax)))	
		return content
		
	def mapfield(self,htmlcontent):
		id = current.request.args(0)
		if self.db.portlet(id).portlettype=="rss": return self.maprss(htmlcontent)
		settings = self.get_settings('portlet',id)
		fields = settings.get('fields',[])
		if isinstance(fields,str): fields = [fields]
		fields = ["PortletHeaderByName"] + fields
		table = settings.get('table')
		dtable = self.cms.define_dtable()
		row = self.db(dtable.name==table).select().first()
		if row:
			if row.attachment: fields.append("PortletAttachment")
			if row.is_comment: fields.append("PortletComment")
		titles = []
		soup = BeautifulSoup(htmlcontent)
		tags = soup.findAll(**{'title':True})
		for tag in tags:
			title = tag['title'].encode('utf-8')
			if title not in titles: titles.append(title)
		content = TABLE(TR(TH(T('Field'),_class="field_label"),TH(T('Position'))),_class="table table-striped defview")
		for field in fields:
			options = [OPTION(title,_value=title,_selected=(title==settings.get('map_%s'%field,''))) for title in titles]
			select = SELECT(['']+options,_name='map_%s'%field)
			tr = TR(TD(T(field.capitalize()),_class="field_label"),TD(select))
			content.append(tr)
		form = FORM(HR(),content,keepvalues=True)
		form.append(INPUT(_type='submit',_value=T('Submit'),_class="btn btn-primary"))
		return form

	def maprss(self,htmlcontent):
		id = current.request.args(0)
		settings = self.get_settings('portlet',id)
		fields = settings.keys()
		fields.append("PortletHeaderByName")
		titles = []
		soup = BeautifulSoup(htmlcontent)
		tags = soup.findAll(**{'title':True})
		for tag in tags:
			title = tag['title'].encode('utf-8')
			if title not in titles: titles.append(title)
		content = TABLE(TR(TH(T('Rss Field'),_class="field_label"),TH(T('Position'))),_class="table table-striped defview")
		for field in ["PortletHeaderByName","title","image","description","published"]:
			if field in fields:
				options = [OPTION(title,_value=title,_selected=(title==settings.get('map_%s'%field,''))) for title in titles]
				select = SELECT(['']+options,_name='map_%s'%field)
				tr = TR(TD(T(field.capitalize()),_class="field_label"),TD(select))
				content.append(tr)
		form = FORM(HR(),content,keepvalues=True)
		form.append(INPUT(_type='submit',_value=T('Submit'),_class="btn btn-primary"))
		return form		
		
	def customize(self,settings={}):
		db = self.db
		id = current.request.args(0)
		T = current.T
		textcontent = ''
		settings = self.get_settings('portlet',id)
			
		table = settings.get('table')
		self.cms.define_table(table)
		fields = settings.get('fields',[])
		images = settings.get('images',[])
		
		if isinstance(fields,str): fields = [fields]
		if isinstance(images,str): images = [images]

		form = FORM(H3(T("Customize portlet view")),_class="navbar-form navbar-left",_action=URL(r=current.request,f="customize_update",args=current.request.args))	
		
		if len(fields) > 0: 
			select = TABLE(_class='table table-striped defview')
			tr = TR(TH(T('Field name')),TH(T('Length/Format')))
			for type in PortletStyle: tr.append(TH(T(type[0].capitalize())))
			select.append(tr)
			for field in fields:
				if field not in images:
					tr = TR(TD(T(field.capitalize())))
					if db[table][field].type in ['integer','double','time','date','datetime']:	
						tr.append(TD(INPUT(_name='format_%s'%field,_class='string',_value=settings.get('format_%s'%field,''))))
					else:
						tr.append(TD(INPUT(_name='length_%s'%field,_class='integer',_value=settings.get('length_%s'%field,''))))
					for type in PortletStyle:
						td = TD()
						options = [OPTION(v,_value=v,_selected=(v==settings.get('%s_%s'%(type[0],field),''))) for v in type[1]]
						td.append(SELECT(['']+options,_name='%s_%s'%(type[0],field)))
						tr.append(td)
					select.append(tr)
			if len(images)>0:
				tr = TR(TH(T('Images')),TH(T('Width')),TH(T('Height'),_colspan=4))
				select.append(tr)
				for field in images:
					tr = TR(TD(T(field.capitalize())))
					tr.append(TD(INPUT(_name='width_%s'%field,_class='integer image_width',_value=settings.get('width_%s'%field,''))))
					tr.append(TD(INPUT(_name='height_%s'%field,_class='integer image_width',_value=settings.get('height_%s'%field,'')),_colspan=4))
					select.append(tr)
			form.append(select)	
		form.append(SPAN(LABEL(T("Add class name")),BR(),INPUT(_name='classname',_class="string form-control",_placeholder="Class Name",_value=settings.get('classname','')),_class="help-block"))	
		form.append(SPAN(LABEL(T("Add style script")),BR(),TEXTAREA(_name='style_script',_class="string form-control",_placeholder="<script></script>",value=settings.get('style_script','')),_class="help-block"))	
		form.append(SPAN(_class="help-block"))
		form.append(INPUT(_type='submit',_value=T('Submit'),_class="btn btn-primary"))
		return form
		
