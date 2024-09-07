# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
# Version 0.2 Date: 19/02/2014
###################################################

import os
import cStringIO
from bs4 import BeautifulSoup

@auth.requires(auth.has_membership(role='admin'))	
def index():
	files = []
	for root, dirs, files in os.walk(request.folder+'/views/layout/content'):
		pass
	op = ['']
	for file in files:
		if file.split(".")[-1] == "html":
			op.append(OPTION(file,_value=URL(args=[file]),_selected=(file==request.args(0))))
	ajax = "ajax('%s',['filename'],'container')"%(URL(f='get_layout'))
	onchange="this.options[this.selectedIndex].value && (window.location = this.options[this.selectedIndex].value);"
	files = SELECT(op,_name='filename',_id='filename',_onchange=onchange)
	content = get_layout()
	return dict(content=content,files=files,portlets=get_portlets())

@auth.requires(auth.has_membership(role='admin'))
def preview():
	if not request.args:
		home = PortalConfig.take('folder.home')
		redirect(URL(args=[home]))
	response.view = "layout/preview.htm"
	return dict()
			
@auth.requires(auth.has_membership(role='admin'))		
def get_layout():
	filename = request.args(0) or request.vars.filename
	if not filename: return ''
	try:
		file = open("%s/views/layout/content/%s"%(request.folder,filename))
		return XML(file.read())
	except Exception, e:
		return e

def get_portlet(id):
	content = str(portlet.display(id))
	return BeautifulSoup(content)		
		
def add_view(soup):
	tags = soup.findAll('div',**{'class':'lyrow ui-draggable'})
	for tag in tags: 
		tag["style"] = 'display: block;'
		for child in tag.children:
			if child.name=='div':
				id = child.get("id") 
				if id: 
					child.clear()
					child.append(get_portlet(id))		
		tag.insert(0,buttondrag())
	return soup				
		
def buttondrag():
	return BeautifulSoup('''<a href="#close" class="remove label label-danger"><i class="glyphicon-remove glyphicon"></i>Remove</a>
<div class="preview"><input type="text" value="" class="form-control"></div>
<span class="drag label label-default"><i class="glyphicon glyphicon-move"></i>Drag</span>''')
		
	
def htmllayout(filename,body):
	return '''<!DOCTYPE html>
<html>
<head>
</head>
{{include 'layout/js.html'}}
{{include 'layout/%s_js_css.html'}}
<body>
<div class="container">
%s
</div>
</body>
</html>'''%(filename,body)

@auth.requires(auth.has_membership(role='admin'))	
def writefile(filename,content):
	file = "%s/views/layout/%s"%(request.folder,filename)
	f = open(file,'w+')
	f.write(content)
	f.close()						

def update():
	try:
		filename = request.vars.filename
		container = request.vars.container
		soup = BeautifulSoup(container)
		content = soup.prettify().encode('utf-8')
		writefile('content/'+filename,content)
		buillayout(filename,content)
		return T("Cập nhật thành công!")
	except Exception, e:
		return e

@auth.requires(auth.has_membership(role='admin'))			
def buillayout(filename,content):
	soup = BeautifulSoup(content)
	tags = soup.findAll('div',**{'class':'preview'})
	for tag in tags: tag.replace_with("") 
	tags = soup.find_all("a", href="#close")
	for tag in tags: tag.replace_with("")
	tags = soup.find_all("span",**{'class':'drag label label-default'})
	for tag in tags: tag.replace_with("")
	tags = soup.findAll('div',**{'class':'view'})
	list_id = []
	for tag in tags:
		id = tag.get("id") 
		if id: 
			tag.replace_with('{{=portlet.display(%s)}}'%id)
			list_id.append(int(id))
	tags = soup.findAll('div',**{'class':'view'})
	for tag in tags:
		tag.replaceWithChildren()		
	tags = soup.findAll('div',**{'class':'lyrow ui-draggable'})
	for tag in tags:
		tag.replaceWithChildren()	
	body = soup.prettify().encode('utf-8')
	content = htmllayout(filename,body)
	writefile(filename,content)
	
	from plugin_cms import get_setting
	content = ""
	jsfiles = []
	cssfiles = []
	for id in list_id:
		settings = db.portlet(id).settings
		for file in get_setting(settings,"jsfile",[]):
			if file not in jsfiles: jsfiles.append(file)
		for file in get_setting(settings,"cssfile",[]):
			if file not in cssfiles: cssfiles.append(file)
	for file in jsfiles:
		content += '''<script src="{{=URL('static','portlet/js/%s.js')}}"></script>\n'''%file
	for file in cssfiles:
		content += '''<link href="{{=URL('static','portlet/css/%s.css')}}" rel="stylesheet">\n'''%file
	writefile("%s_js_css.html"%filename,content)
		
def get_portlets():
	from plugin_portlet import PortletType
	p = ""
	for type in PortletType:
		type = type[0]
		title = T('Portlet '+type)
		content = panel_ul()
		content.append(panel_title(title,'Setting',A('Portlet',_href=URL(c='plugin_portlet',f='get_portlet',vars=dict(type=type)))))
		li = panel_li()
		rows = db(db.portlet.portlettype==type).select(orderby=db.portlet.name)
		for row in rows:
			preview = row.name
			view = portlet.preview(row.id)
			li.append(panel_drag(row.id, preview, view))
		content.append(li)
		p+=str(content)
	return XML(p)

def panel_title(title,help='Help',content=''):
	return XML('''
	<li class="nav-header">
	<div class="pull-right popover-info">
	 <i class="glyphicon glyphicon-question-sign">
	 </i>
	 <div class="popover fade right">
	  <div class="arrow">
	  </div>
	  <h3 class="popover-title">
	   %s
	  </h3>
	  <div class="popover-content">
	   %s
	  </div>
	 </div>
	</div>
	<i class="glyphicon-plus glyphicon"></i>
	 %s
	</li>'''%(help, content, title))

def panel_drag(id, preview, view, remove='remove',drag='drag'):
	return XML('''
	<div class="lyrow ui-draggable">
	<a class="remove label label-danger" href="#close">
	<i class="glyphicon-remove glyphicon">
	</i>
	%s
	</a>
	<span class="drag label label-default">
	<i class="glyphicon glyphicon-move">
	</i>
	%s
	</span>
	%s
	</div>
	'''%(remove,drag,panel_content(id, preview, view)))

def panel_content(id, preview, view):
	return XML('''
	<div class="preview">
		%s
	</div>         
	<div class="view" id="%s">
		%s
	</div>'''%(preview, id, view))
	
def panel_ul():
	return UL(_class="nav nav-list accordion-group")

def panel_li():
	return LI(_class="rows",_id="estRows",_style="display: none;")

