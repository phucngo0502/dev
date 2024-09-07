###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 1.0 Date: 27/02/2015
###################################################
# -*- coding: utf-8 -*-

FOLDER_PARENT = 44

from plugin_folder import Folder
cms.define_folder()
folder = Folder(cms.db,auth,parent=FOLDER_PARENT)

import cStringIO
from plugin_portlet import PortletManage, PortletType
portlet = PortletManage(cms)

def index():
	from bootrap import Panel
	p = Panel()
	menu = [(T("Quản lý hiển thị"),[DIV(folder.display_url(),_id="jstree")])]
	content = DIV()
	content.append(DIV(A(SPAN(_class='glyphicon glyphicon-plus'),T(" Create new folder"), _id="create",_class='btn btn-danger', _onclick="update('');"),_class='input_news'))
	content.append(p.panel(menu))
	return dict(content='')
	
def menu_top():
	from bootrap import Panel
	p = Panel()
	menu = [(T("Quản lý hiển thị"),[DIV(folder.display_url(),_id="jstree")])]
	content = DIV()
	content.append(DIV(A(SPAN(_class='glyphicon glyphicon-plus'),T(" Create new folder"), _id="create",_class='btn btn-danger', _onclick="update('');"),_class='input_news'))
	content.append(p.panel(menu))
	return content


def menu():
	content  = DIV(_i="portletmenu",_class="portletmenu")
	menus = [('setting_name','fa-edit'),('setting_data','fa-cog'),('setting_view','fa-eye'),('customize','fa-eye')] if request.args(0) else [('setting_name','fa-edit')]
	for f in menus:
		name = T('Portlet %s'%f[0])
		if f[0]==request.function: 
			name = B(name)
			active = "active"
		else: active = ""
		button = A(I(_class="fa %s fa-fw"%f[1]),SPAN(name,_class='buttontext button'),_class="button btn btn-default %s"%active,_href=URL(f=f[0],args=request.args))
		content.append(button)
	return content

@auth.requires(auth.has_membership(role='admin'))		
def porletgrid():
	links=[dict(header="",body=lambda row: A(SPAN(_class='icon pen icon-pencil glyphicon glyphicon-pencil'),T('Edit'),_href=URL(f='setting_data',args=[row.id]),_class='button btn btn-default'))]
	content = SQLFORM.grid(portlet.db.portlet,csv=False,user_signature=False,links=links,editable=False,create=False)
	return dict(content=content)

@auth.requires(auth.has_membership(role='admin'))		
def viewgrid():
	links=[dict(header="",body=lambda row: A(SPAN(_class='icon pen icon-pencil glyphicon glyphicon-pencil'),T('Edit'),_href=URL(f='portletview',args=[row.id]),_class='button btn btn-default'))]
	content = SQLFORM.grid(portlet.db.portletview,csv=False,user_signature=False,links=links,editable=False,create=False)
	return dict(content=content)

def update_settings():
	row = portlet.db.portlet(request.args(0))
	settings = portlet.get_settings('portlet',row.id)
	for key in settings.keys():
		if key.startswith("map_"): pass
		elif key.startswith("width_"): pass
		elif key.startswith("height_"): pass
		elif key.startswith("font-"): pass
		elif key in ["portletview","jsfile","cssfile","style_script","classname"]: pass
		else: del settings[key]
	for key in request.vars.keys(): 
		if request.vars[key] != "":
			settings[key] = request.vars[key]
	row.update_record(settings=settings)
	redirect(URL(f='setting_view',args=request.args))
	
def select_type():
	if not request.vars.portlettype: return ''
	try:
		if request.vars.portlettype=='load':
			content = portlet.select_controller()
		elif request.vars.portlettype=='table':
			content = portlet.select_table()		
		elif request.vars.portlettype=='html':
			content = portlet.html(id=request.args(0))	
		elif request.vars.portlettype=='view':
			content = portlet.html(id=request.args(0),ck=False)	
	except Exception, e:
		content = e
	return content	

def select_function():
	if not request.vars.c: return ''
	try:
		content = portlet.select_function(request.vars.c)
	except Exception, e:
		content = e
	return content	
	
def load_function():
	try:
		content = LOAD(c=request.vars.c,f=request.vars.f,ajaxtrap=True)
	except Exception, e:
		content = e
	return content

def select_fields():
	if not request.vars.table: return ''
	try:
		content = portlet.select_fields(request.vars.table)
	except Exception, e:
		content = e
	return content
	
@auth.requires(auth.has_membership(role='admin'))	
def setting_name():
	table = portlet.db.portlet
	table.settings.readable=False
	table.textcontent.writable = False
	table.textcontent.readable = False
	table.htmlcontent.writable = False
	table.htmlcontent.readable = False
	form = SQLFORM(table,request.args(0),showid=False,deletable=True)
	ajax = "ajax('%s', ['portlettype','portletview','name'], '')"%(URL(f='portlet_copy',args=request.args))
	if request.args(0): form[0][4][1].append(INPUT(_type='button',_value=T('Copy'),_class="btn btn-primary",_onclick=ajax))
	if form.process().accepted:
		if form.vars.delete_this_record:
			redirect(URL(f='get_portlet',vars=dict(type=request.vars.type)))		
		redirect(URL(f='setting_data',args=[form.vars.id],vars=dict(type=form.vars.portlettype)))
	return dict(content=DIV(menu(),form))

@auth.requires(auth.has_membership(role='admin'))
def portlet_copy():
	id = request.args(0)
	table = portlet.db.portlet
	row = table(id)
	if request.vars.name != row.name:
		id = table.insert(portlettype=request.vars.portlettype,portletview=request.vars.portletview,name=request.vars.name,settings=row.settings,textcontent=row.textcontent,htmlcontent=row.htmlcontent)
	redirect(URL(f='setting_data',args=[id],vars=dict(type=request.vars.portlettype)),client_side=True)
	
@auth.requires(auth.has_membership(role='admin'))		
def setting_data():
	form = portlet.select_type()
	content = DIV(menu(),form)
	return dict(content=content)

@auth.requires(auth.has_membership(role='admin'))		
def banner_update():
	id = request.args(0)
	bkey = request.args(1)
	vars = {} if len(request.vars.keys())>0 else None 
	for key in  request.vars.keys(): vars[key]=request.vars[key]
	return portlet.banner_update(id,bkey,vars)

@auth.requires(auth.has_membership(role='admin'))		
def banner_form():
	return portlet.banner_form(request.args(0),request.args(1))
	
@auth.requires(auth.has_membership(role='admin'))		
def setting_view():
	from bs4 import BeautifulSoup
	id = request.args(0)
	if not id: return dict(portletview='',content=menu())
	row = portlet.db.portlet(id)
	if row.portlettype=='html': 
		content= DIV(menu(),DIV(XML(row.htmlcontent)))
		return dict(portletview='',content=content)	
	elif row.portlettype=='banner': 
		content = portlet.html(id,ck=False,fieldedit=None)
		content= DIV(menu(),DIV(content))
		return dict(portletview='',content=content)	
	elif row.portlettype=='view': 
		content= DIV(menu(),DIV(portlet.preview(id)))
		return dict(portletview='',content=content)	
	elif not row.portletview:	
		form = portlet.html(id,ck=False,fieldedit="textcontent")
		content= DIV(menu(),DIV(form),DIV(portlet.preview(id)))
		return dict(portletview='',content=content)	
		
	settings = eval(row.settings) if row.settings else {} 
	idview = request.args(1) or settings.get('portletview') 
	if idview:
		title = H3(T("Portlet view selected"), ": ", B(portlet.db.portletview(idview).name))
		htmlcontent = db.portletview(idview).htmlcontent
	else: 
		title = H3(T("No portlet view selected!"))
		htmlcontent = row.htmlcontent
	form = portlet.mapfield(htmlcontent)
	content= DIV(menu(),title,form,HR(),DIV(portlet.display(id),_style='width:100%;'))
	if form.process().accepted:
		soup = BeautifulSoup(htmlcontent)
		tag = soup.find(**{'repeat':True})
		if tag:
			del tag['repeat']
			parent = tag.parent or soup
			parent.clear()
			parent.append('{{pass}}')
			parent.insert(0,tag)
			parent.insert(0,'{{for row in rows:}}')
		table = settings.get("table")
		fields = []
		if table: 
			if cms.define_table(table): fields = db[table].fields
			href = '{{=cms.url_content(row,"%s")}}'%table
		elif row.portlettype=="rss":
			fields = ["title","image","description","published"]
			href = '{{=row["link"]}}'
		if idview: 
			settings['portletview'] = int(idview)
			settings['jsfile'] = db.portletview(idview).jsfile
			settings['cssfile'] = db.portletview(idview).cssfile
		for key in request.vars.keys():
			if key.startswith('map_'): 
				if settings.has_key(key): del settings[key]
				if request.vars[key].strip() !='':
					field = key[4:]
					settings[key] = request.vars[key]
					tag = soup.find(**{'title':request.vars[key]})
					if tag:
						del tag['title']
						if field=="PortletHeaderByName":
							tag.clear()
							if settings.get('cmsquery'): tag.append('{{=cms.field_format(row,"PortletHeaderByName","header",settings)}}')
							else: tag.append('{{=T("%s")}}'%row.name)
						elif field=="PortletAttachment":
							tag.clear()
							tag.append('{{=cms.field_format(row,"PortletAttachment","attachment",settings)}}')
						elif field=="PortletComment":
							tag.clear()
							tag.append('{{=cms.field_format(row,"PortletComment","comment",settings)}}')
						elif field in fields:
							if row.portlettype=="rss":
								new = '{{=row["%s"]}}'%(field)
							else:
								new = '{{=cms.field_format(row,"%s","%s",settings)}}'%(field,db[table][field].type)
							if tag.name=='img':
								tag['src'] = new
								parent = tag.parent
								if parent:
									if parent.name == 'a':
										parent['href'] = "%s"%href
							else:
								if tag.name=='a':
									tag['href'] = "%s"%href
								elif field in settings.get('fields_url',[]):
									new = '<a href="%s">%s</a>'%(href,new)
								tag.clear()
								tag.append(new)
		settings = str(settings)
		textcontent = soup.prettify()
		row.update_record(settings=settings,textcontent=textcontent,htmlcontent=htmlcontent)
		redirect(URL(args=request.args))
		
	from bootrap import Panel
	rows = db((db.portletview.portlettype==row.portletview)).select(orderby=db.portletview.name)
	pv = []
	for r in rows:
		pv.append(A(r.name,_href=URL(args=[id,r.id])))
	portletview = Panel().panel(elements=[(T("Views of %s type"%row.portletview),pv)],id="panel-group",cls="panel-default")
	return dict(portletview=portletview,content=content)

def update_text():
	try:
		table = portlet.db.portlet
		table(request.args(0)).update_record(textcontent=request.vars.textcontent)
	except Exception, e:
		print e
	redirect(URL(f='setting_view',args=request.args),client_side=True)		
	
@auth.requires(auth.has_membership(role='admin'))	
def get_portlet():
	if request.vars.type:
		rows = db((db.portlet.portlettype==request.vars.type)).select(orderby=db.portlet.name)
		content = DIV(_class="panel-group",_id='get_portlet',**{ '_role':"tablist",'_aria-multiselectable':"true"} )
		i = 1
		for row in rows:
			div_c = DIV(_class="panel portletview")
			div_c.append(DIV(SPAN(_class='glyphicon glyphicon-plus-sign',**{'_data-toggle':'collapse','_data-parent':'#get_portlet','_aria-expanded':"false", '_data-target':'#wr_content_%s'%(i) }),A(" "+row.name,_class="portletview_name",_href=URL(f="setting_name",args=[row.id],vars=request.vars))))
			div_c.append(DIV(portlet.preview(row.id),_class="well portletview_content collapse",_id='wr_content_%s'%(i)))
			i+= 1
			content.append(div_c)
		content = DIV(H3(T("Portlet type %s"%request.vars.type)),content)
		return dict(content=content)
	else:
		redirect(URL(f="setting_name"))

@auth.requires(auth.has_membership(role='admin'))	
def portletview():
	if request.args(0):
		content = DIV(H3(T("Edit portlet view")),editview())
	elif not request.vars.type:
		content = DIV(H3(T("Create new portlet view")),editview())
	else:
		rows = db((db.portletview.portlettype==request.vars.type)).select(orderby=db.portletview.name)
		content = DIV(_class="panel-group",_id='get_portlet',**{ '_role':"tablist",'_aria-multiselectable':"true"} )
		i = 1
		for row in rows:
			div_c = DIV(_class="panel portletview")
			div_c.append(DIV(SPAN(_class='glyphicon glyphicon-plus-sign',**{'_data-toggle':'collapse','_data-parent':'#get_portlet','_aria-expanded':"false", '_data-target':'#wr_content_%s'%(i) }),A(" "+row.name,_class="portletview_name",_href=URL(args=[row.id],vars=request.vars))))
			div_c.append(DIV(XML(row.htmlcontent),_class="well portletview_content collapse",_id='wr_content_%s'%(i)))
			i+= 1
			content.append(div_c)
		content = DIV(H3(T("Portlet view type %s"%request.vars.type)),content) 	
	return dict(content=content)

@auth.requires(auth.has_membership(role='admin'))		
def editview():
	import os
	def widget_js(field,value):	
		files = []
		for root, dirs, files in os.walk(request.folder+'/static/portlet/js'):
			pass
		content = DIV(_class="checkbox",_id="jsfile")
		for file in files:
			if file.split(".")[-1]=="js":
				label = LABEL(INPUT(_type="checkbox",_name=field.name,_value=file[:-3],_checked=(file[:-3] in (value or [])),_class="boolean"))
				label.append(file[:-3])
				content.append(SPAN(label,_style="margin-right:20px;"))
		return content
	def widget_css(field,value):	
		files = []
		for root, dirs, files in os.walk(request.folder+'/static/portlet/css'):
			pass
		content = DIV(_class="checkbox",_id="cssfile")
		for file in files:
			if file.split(".")[-1]=="css":
				label = LABEL(INPUT(_type="checkbox",_name=field.name,_value=file[:-4],_checked=(file[:-4] in (value or [])),_class="boolean"))
				label.append(file[:-4])
				content.append(SPAN(label,_style="margin-right:20px;"))
		return content

	try:
		idview = request.args(0)
		htmlcontent = db.portletview(idview).htmlcontent if idview else ''
		script = XML('''<script>
var editor = CodeMirror.fromTextArea(document.getElementById("portletview_htmlcontent"), {
	lineNumbers: true,
	mode: "text/html",
	matchBrackets: true
});
$('#submit').click(function(){
	if (document.getElementById("portletview_portlettype").value=='') {
		alert('Type not null');
		return 0;
	} 
	if (document.getElementById("portletview_name").value=='') {
		alert('Name not null');
		return 0;
	} 
	var data = '&portlettype=' + document.getElementById("portletview_portlettype").value +'&name=' + document.getElementById("portletview_name").value + '&htmlcontent=' + encodeURIComponent(editor.getValue());
	var js = $.map($("#jsfile input:checked"), function(elem, idx) {return "&jsfile=" + $(elem).val();}).join('');	
	var css = $.map($("#cssfile input:checked"), function(elem, idx) {return "&cssfile=" + $(elem).val();}).join('');	
	data = data + js + css
	$.ajax({
		url: "%s",
		type: "GET",
		data: data,
		cache: true,
		success: function (html) {
			if (html!='') {
				$("#portletview").html(html);
			}
		}
	});		
})
</script>'''%URL(f='saveview',args=request.args,vars=request.vars))
		db.portletview.jsfile.widget = widget_js
		db.portletview.cssfile.widget = widget_css
		form = SQLFORM(db.portletview,idview,showid=False,buttons=[])
		submit = INPUT(_type='button',_value=T('Submit'),_id='submit',_class="btn btn-primary")
		ajax = "ajax('%s',['name','portlettype','jsfile','cssfile'],'portletview')"%URL(f='copyview',args=request.args,vars=request.vars)
		copy = INPUT(_type='button',_value=T('Copy'),_onclick=ajax,_class="btn btn-primary") if idview else ''
		ajax = "ajax('%s',[],'portletview')"%URL(f='delview',args=request.args,vars=request.vars)
		delete = INPUT(_type='button',_value=T('Delete'),_onclick=ajax,_class="btn btn-primary") if idview else ''
		content = DIV(form,submit,copy,delete,HR(),XML(htmlcontent),script)
		return content	
	except Exception, e:
		return e

def copyview():
	id = request.args(0)
	row = db.portletview(id)
	if request.vars.name != row.name:
		jsfile=request.vars.jsfile or []
		cssfile=request.vars.cssfile or []
		id = db.portletview.insert(portlettype=request.vars.portlettype,name=request.vars.name,jsfile=jsfile,cssfile=cssfile,htmlcontent=row.htmlcontent)
	redirect(URL(f='portletview',args=[id],vars=dict(type=request.vars.type)),client_side=True)	
		
def delview():
	idview = request.args(0)
	db(db.portletview.id==idview).delete()
	redirect(URL(f='portletview',vars=dict(type=request.vars.type)),client_side=True)	
	
def saveview():
	from bs4 import BeautifulSoup
	htmlcontent = request.vars.htmlcontent
	jsfile=request.vars.jsfile or []
	cssfile=request.vars.cssfile or []
	soup = BeautifulSoup(htmlcontent)
	tag = soup.find(title=True)
	if not tag:
		tags = soup.find_all(True)
		i = 1	
		for tag in tags: 
			tag['title'] = 'tag %s position %s'%(tag.name, i)
			i+=1
	htmlcontent = soup.prettify()
	idview = request.args(0)
	if idview:
		db(db.portletview.id==idview).update(name=request.vars.name,portlettype=request.vars.portlettype,htmlcontent=htmlcontent,jsfile=jsfile,cssfile=cssfile)
	else:
		db.portletview.insert(name=request.vars.name,portlettype=request.vars.portlettype,htmlcontent=htmlcontent,jsfile=jsfile,cssfile=cssfile)
	redirect(URL(f='portletview',vars=dict(type=request.vars.portlettype)),client_side=True)
	return XML(htmlcontent)
	
@auth.requires(auth.has_membership(role='admin'))		
def edit():
	id = request.args(0)
	if not request.vars.portlet: redirect(URL(f='index'))
	form = portlet.portlet_customize()
	if form.process().accepted:
		row = portlet.db.portlet(request.vars.portlet)
		if id:
			portlet.db.portlet(id).update_record(name=request.vars.name,folder=request.vars.folder,layout=request.vars.layout)
		else:
			id = portlet.db.portlet.insert(portlet=row.id,settings=row.settings,name=request.vars.name,folder=request.vars.folder,layout=request.vars.layout)
		redirect(URL(f='customize',args=[id]))
	return dict(content=form)
	
@auth.requires(auth.has_membership(role='admin'))		
def customize():
	if not request.args(0): redirect(URL(f='view'))
	form = portlet.customize()
	response.view = "plugin_portlet/setting_data.html"
	content = DIV(menu(),form)
	return dict(content=content)
	
@auth.requires(auth.has_membership(role='admin'))		
def customize_update():
	row = portlet.db.portlet(request.args(0))
	settings = eval(row.settings or "{}")
	for key in request.vars.keys():
		if key not in ['_formkey', '_formname']:
			settings[key] = request.vars[key]
	row.update_record(settings=str(settings))
	redirect(URL(f="customize",args=request.args))

@auth.requires(auth.has_membership(role='admin'))	
def get_service():	
	try:
		from gluon.contrib.pysimplesoap.client import SoapClient
		link = request.vars.location or ""
		if not link.endswith("?WSDL"): link += "?WSDL" 
		#client = SoapClient(wsdl="http://www.webservicex.net/globalweather.asmx?WSDL")
		#client = SoapClient(wsdl="http://127.0.0.1:8000/cms/default/call/soap?WSDL")
		#client = SoapClient(wsdl=link)
		client = SoapClient()
		client.services = client.wsdl_parse(link)
		if not client.services: return "Error"
		t = TABLE(_class='table table-striped defview')
		name = []
		vars = {}
		id = request.args(0)
		settings = eval(portlet.db.portlet(id).settings or "{}")
		for service in client.services.values():
			for port in service['ports'].values():
				for op in port["operations"].values():
					if "output" in op.keys():
						if op["name"] not in name:
							t.append(TR(TH(T("Location")), TH(port['location'],_colspan=3)))
							t.append(TR(TD(T("Action")), TD(op['action'],_colspan=3)))
							t.append(TR(TD(T("Documentation")), TD(op['documentation'],_colspan=3)))
							vars["location"] = port['location']
							vars["action"] = op['action']
							vars["name"] = op["name"]
							vars["input"] = []
							vars["output"] = []
							input_key = []
							name.append(op["name"])
							t.append(TR(TD(T("Name")), TD(op["name"])))
							key = "input"
							if key in op.keys():
								a = op[key].keys()[0]
								tmp = op[key][a]
								i = 0
								for k in tmp.keys(): 
									label = T(key.capitalize()) if i==0 else ""
									inputname = str("%s_%s"%(op["name"],k))
									t.append(TR(TD(label), TD(k), TD(INPUT(_name=inputname,_clas="string",_value=settings.get(inputname,""))), TD(tmp[k])))
									vars["input"].append(str(k))
									input_key.append(inputname)
									i+=1
							key = "output"
							tmp = op[key][op[key].keys()[0]]
							i = 0
							for k in tmp.keys(): 
								label = T(key.capitalize()) if i==0 else ""
								t.append(TR(TD(label), TD(k), TD(), TD(tmp[k])))
								vars["output"].append(str(k))
								i+=1
							# for key in op.keys():
								# if key not in ["name","input","output"]:
									# t.append(TR(TD(key.capitalize()),TD(op[key],_colspan=3)))
							divid = "%s_output_result"%op["name"]
							ajax = "ajax('%s', %s, '%s')"%(URL(r=request,c='plugin_portlet',f='get_output',vars=vars,args=[id]),input_key,divid)
							t.append(TR(TD(INPUT(_type="button",_value=T("Submit"),_onclick=ajax,_class="btn btn-primary")),TD(DIV(_id=divid),_colspan=3)))
		return t
	except Exception, e:
		print e
		return e
	
def get_output():	
	def get_tag(tag):		
		if len(tag.children()) == 0: return tag.get_name()
		ul = UL()
		for children in tag.children():
			ul.append(LI(get_tag(children)))
		return ul
	
	try:
		from gluon.contrib.pysimplesoap.client import SoapClient
		from gluon.contrib.pysimplesoap.simplexml import SimpleXMLElement
		import xml.etree.ElementTree as ET
		from bs4 import BeautifulSoup
		settings = {}
		for key in request.vars.keys():
			settings[key] = request.vars[key]
		id = request.args(0)
		portlet.db.portlet(id).update_record(settings=str(settings))
		
		location = request.vars.location
		action = request.vars.action
		name = request.vars.name

		#client = SoapClient(location = location, action = action, namespace = action, soap_ns="soap11", trace=True)
		
		client = SoapClient(wsdl = location+"?WSDL")
			
		inputs = [request.vars.input] if isinstance( request.vars.input,str) else request.vars.input
		input = {}
		v = ""
		for key in inputs:
			v+="<%s>%s</%s>"%(key,request.vars["%s_%s"%(name,key)],key)
			input[key] = request.vars["%s_%s"%(name,key)]

		result = eval('client.%s(**input)'%name)
		return XML(result[request.vars.output])
				
		params = SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?><%s>%s</%s>'%(name,v,name)) 		
		res = client.call(name, params)
		result = eval('res.%s'%request.vars.output)
		return result.as_xml()
	except Exception, e:
		return e
		
def webservice():	
	try:
		from gluon.contrib.pysimplesoap.client import SoapClient
		id = request.args(0)
		settings = eval(portlet.db.portlet(id).settings or "{}")
		client = SoapClient(wsdl = settings.get("location")+"?WSDL")
		inputs = settings.get("input",[])	
		if isinstance(inputs,str): inputs = [inputs]
		input = {}
		v = ""
		name = settings.get("name")
		for key in inputs:
			v+="<%s>%s</%s>"%(key,request.vars["%s_%s"%(name,key)],key)
			input[key] = settings.get("%s_%s"%(name,key))
		result = eval('client.%s(**input)'%name)
		return XML(result[settings.get("output")])
	except Exception, e:
		return e
		
def set_url():
	try:
		url = request.vars.url
		id = request.args(0)
		settings = eval(portlet.db.portlet(id).settings or "{}")
		import urllib2
		from bs4 import BeautifulSoup
		response = urllib2.urlopen(url,timeout=30)
		data = response.read()
		soup = BeautifulSoup(data)
		tags = soup.findAll("div")
		i = 1
		for tag in tags:
			if tag.contents:
				v = str(tag.attrs).replace("{","$").replace("}","@").replace("'","*")
				if v == settings.get("divselected"):
					newtag = BeautifulSoup("<input type='radio' name='divselected' value='%s' checked='checked'></input>"%v)
				else:
					newtag = BeautifulSoup("<input type='radio' name='divselected' value='%s'></input>"%v)
				if tag.has_attr('class'): tag['class'].append('divborder')
				else: tag["class"] = 'divborder'				
				tag.insert(0, newtag)
				i+=1
		return soup.prettify()
	except Exception, e:
		return e
				
def get_url():
	try:
		url = request.vars.url
		id = request.args(0)
		settings = eval(portlet.db.portlet(id).settings or "{}")
		import urllib2
		from bs4 import BeautifulSoup
		response = urllib2.urlopen(url,timeout=30)
		data = response.read()
		attr = settings.get("divselected")
		if not attr: return data
		attr = attr.replace("$","{").replace("@","}").replace("*","'")
		attr = eval(attr)
		soup = BeautifulSoup(data)
		tag = soup.find("div", attrs=attr)
		if tag: 
			links = soup.findAll("link")
			for link in links:
				tag.insert(0,link)
			return tag.prettify()
		return "Error"
	except Exception, e:
		return e				
		
def get_url():
	try:
		url = request.vars.url
		id = request.args(0)
		settings = eval(portlet.db.portlet(id).settings or "{}")
		import urllib2
		from bs4 import BeautifulSoup
		response = urllib2.urlopen(url,timeout=30)
		data = response.read()
		attr = settings.get("divselected")
		if not attr: return data
		attr = attr.replace("$","{").replace("@","}").replace("*","'")
		attr = eval(attr)
		soup = BeautifulSoup(data)
		tag = soup.find("div", attrs=attr)
		if tag: 
			links = soup.findAll("link")
			for link in links:
				tag.insert(0,link)
			return tag.prettify()
		return "Error"
	except Exception, e:
		return e
		
def get_rss():
	from gluon.contrib import feedparser
	from bs4 import BeautifulSoup
	url = request.vars.url
	d = feedparser.parse(url)
	if len(d.entries) == 0: return  T("No rss entry")
	entry = d.entries[0]
	keys = entry.keys()
	settings = {"url":url,"length":request.vars.length or 10}
	for key in ["link","title","image","description","published"]:
		settings[key] = entry[key] if entry.has_key(key) else None
	if entry.has_key("summary"):
		soup = BeautifulSoup(entry["summary"])
		tag = soup.find("img")
		if tag: 
			if not settings["image"]: settings["image"] = tag["src"]
			tag.replace_with("")
		tag = soup.find("a")
		if tag: 
			if not settings["link"]: settings["link"] = tag["href"]
			tag.replace_with("")
		if not settings["description"]: settings["description"] = soup.get_text()
	for key in ["title","image","description","published"]:
		if not settings[key]: del settings[key]
	id = request.args(0)
	portlet.db.portlet(id).update_record(settings=str(settings))
	redirect(URL(f='setting_view',args=request.args),client_side=True)		
		
def rss():
	try:
		from gluon.contrib import feedparser
		from bs4 import BeautifulSoup
		id = request.args(0)
		p = portlet.db.portlet(id)
		settings = eval(p.settings or "{}")
		d = feedparser.parse(settings.get("url"))
		if len(d.entries) == 0: return ""
		rows = []
		i = 0
		for entry in d.entries:
			if i == int(settings.get("length",10)): break
			i+=1
			keys = entry.keys()
			row = {}
			for key in ["link","title","image","description","published"]:
				row[key] = entry[key] if entry.has_key(key) else None
			if entry.has_key("summary"):
				soup = BeautifulSoup(entry["summary"])
				tag = soup.find("img")
				if tag: 
					if not row["image"]: row["image"] = tag["src"]
					tag.replace_with("")
				tag = soup.find("a")
				if tag: 
					if not row["link"]: row["link"] = tag["href"]
					tag.replace_with("")
				row["description"] = soup.get_text()
			rows.append(row)
		context = dict(rows=rows,row=row)
		textcontent = cStringIO.StringIO(p.textcontent)
		content = response.render(textcontent, context)
		return content
	except Exception, e:
		return e
		
def rss_preview():
	try:
		from gluon.contrib import feedparser
		from bs4 import BeautifulSoup
		url = request.vars.url
		d = feedparser.parse(url)
		if len(d.entries) == 0: return T("No rss entry")
		rows = []
		i = 0
		for entry in d.entries:
			if i == int(request.vars.length or 10): break
			i+=1
			keys = entry.keys()
			row = {}
			for key in ["link","title","image","description","published"]:
				row[key] = entry[key] if entry.has_key(key) else None
			if entry.has_key("summary"):
				soup = BeautifulSoup(entry["summary"])
				tag = soup.find("img")
				if tag: 
					if not row["image"]: row["image"] = tag["src"]
					tag.replace_with("")
				tag = soup.find("a")
				if tag: 
					if not row["link"]: row["link"] = tag["href"]
					tag.replace_with("")
				row["description"] = soup.get_text()
			rows.append(row)
		content = UL(_class="rss-preview")	
		for row in rows:
			td1 = TD(_width="20%")
			if row.has_key("image"): td1.append(IMG(_src=row["image"],_class="rss-image"))		
			td2 = TD()
			for key in ["title","description","published"]:
				if row.has_key(key): td2.append(P(row[key],_class="rss-%s"%key))
			entry = TABLE(TR(td1,td2),_class="rss-entry")				
			content.append(LI(entry))
		return content
	except Exception, e:
		return e
				