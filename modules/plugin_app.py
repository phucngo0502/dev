###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
# Version 1.0 Date: 16/10/2015
###################################################
# -*- coding: utf-8 -*-
from gluon import current, HTTP
from html import *
import datetime, os


class Dropdown:
	def __init__(self,field=None,caption='New',close="Close",id=None,width=70,height=70, create=None,select=None):
		import uuid
		self.field=field
		self.caption=caption
		self.close=close
		self.id=id or str(uuid.uuid4()).replace('-','')
		self.width=width
		self.height=height
		self.create=create or URL(r=current.request,c='plugin_app',f='create_dropdown',args=[str(field)])
		self.select=select or URL(r=current.request,c='plugin_app',f='select_dropdown',args=[str(field)])
	def __str__(self):
		return self.xml()
	def xml(self):
		session = current.session
		session['_plugin_dropbox:%s' % self.field]=None
		return '<div id="%(id)s" style="display:none"><div style="display_order:fixed;top:0%%;left:0%%;width:100%%;height:100%%;background-color:black;z-index:1001;-moz-opacity:0.8;opacity:.80;opacity:0.8;"></div><div style="display_order:fixed;top:%(top)s%%;left:%(left)s%%;width:%(width)s%%;height:%(height)s%%;padding:16px;border:2px solid black;background-color:white;opacity:1.0;z-index:1002;overflow:auto;-moz-border-radius: 10px; -webkit-border-radius: 10px;"><span style="font-weight:bold">%(title)s</span><span style="float:right">[<a href="#" onclick="jQuery.ajax({url:\'%(select)s\',success:function(data){jQuery(\'select[name=%(name)s]\').html(data);}});jQuery(\'#%(id)s\').hide();return false;">%(close)s</a>]</span><hr/><div style="width:100%%;height:90%%;" id="c%(id)s"><iframe id="popup_modal_content%(id)s" style="width:100%%;height:100%%;border:0">loading...</iframe></div></div></div><a href="#" onclick="jQuery(\'#popup_modal_content%(id)s\').attr(\'src\',\'%(create)s\');jQuery(\'#%(id)s\').fadeIn(); return false">%(title)s</a>' % dict(title=self.caption,create=self.create,select=self.select,close=self.close,id=self.id,left=(100-self.width)/2,top=(100-self.height)/2,width=self.width,height=self.height,name=self.field.name)

class Popup:
	def __init__(self,caption=current.T('Preview'),close=current.T("Close"),id=None,width=70,height=70,source=None,target='',url=None,reload=False):
		import uuid
		self.caption=caption
		self.close=close
		self.id=id or str(uuid.uuid4())
		self.width=width
		self.height=height
		self.source = source
		self.update = 'location.reload();' if reload else ''
		if url: self.update = "jQuery.ajax({url:\'%s\',success:function(data){jQuery('#%s').html(data);}});"%(url,target)
	def xml(self):
		return '<div id="%(id)s" style="display:none"><div style="display_order:fixed;top:0%%;left:0%%;width:100%%;height:100%%;background-color:black;z-index:1001;-moz-opacity:0.8;opacity:.80;opacity:0.8;"></div><div id="popup_ivinh" style="display_order:fixed;top:%(top)s%%;left:%(left)s%%;width:%(width)s%%;height:%(height)s%%;padding:16px;border:2px solid black;background-color:white;opacity:1.0;z-index:1002;overflow:auto;-moz-border-radius: 10px; -webkit-border-radius: 10px;"><span id="title" style="font-weight:bold">%(title)s</span><span style="float:right"><a id="close" href="#" onclick="%(update)s jQuery(\'#%(id)s\').hide();return false;">%(close)s</a></span><div id="popup_content" style="width:100%%;height:90%%;" id="c%(id)s"><iframe id="popup_modal_content%(id)s" style="width:100%%;height:100%%;border:0">%(loading)s</iframe></div></div></div><a href="#" onclick="jQuery(\'#popup_modal_content%(id)s\').attr(\'src\',\'%(source)s\');jQuery(\'#%(id)s\').fadeIn(); return false" id="plugin_wiki_open_attachments%(id)s"">%(title)s</a>' % dict(title=self.caption,source=self.source,close=self.close,id=self.id,left=(100-self.width)/2,top=(100-self.height)/2,width=self.width,height=self.height,loading=current.T('loading...'),update=self.update)		
		
class ColorBox:		
	def __init__(self,caption=current.T('Preview'),close=current.T("Close"),id=None,width='95%',height='95%',source=None,target='',url=None,reload=False,input_name='archives',iframe='true',onCleanup='',jquery=''):
		import uuid
		self.caption=caption
		self.close=close
		self.id=id or str(uuid.uuid4())
		self.width=width
		self.height=height
		self.source = source
		self.iframe = iframe
		self.onCleanup = onCleanup
		self.input_name = input_name
		self.update = jquery
		if reload: self.update += 'location.reload();'  
		if url: 
			if not isinstance(url,list):
				url = [url]
				target = [target]
			i = 0
			for u in url:
				t = target[i]
				self.update += "jQuery.ajax({url:\'%s\',success:function(data){jQuery('#%s').html(data);}});"%(u,t)
				i+=1
	def xml(self):
		script = '''<script type="text/javascript">
				$(function() {
					var checks = $("#searchi_input").val();
					$('.colorbox_%s').colorbox({
						iframe:%s, width:"%s", height:"%s",
						//onOpen:function(){},
						//onLoad:function(){},
						//onComplete:function(){alert($.colorbox.settings.href);},
						onCleanup:function(){%s},
						onClosed:function(){%s},
						input_name:'%s'
					});
				});
			</script>'''%(self.id,self.iframe,self.width,self.height,self.onCleanup,self.update,self.input_name)
		content = "<a href='%s' class='colorbox_%s'>%s</a>"%(self.source,self.id,self.caption)
		return script+content	
		
def get_setting(key=None,default={},path=None):
	try:
		if not path: path=os.path.join(current.request.folder,'config.py')
		file = open(path,'r')
		data = file.read().replace(chr(13),'')
		file.close()
		tmp = eval(data)
		if not key: return tmp
		return tmp[key]
	except:
		return default

def remove_htmltag(text):
	import re
	x = re.compile(r'<[^<]*?/?>')
	tmp = x.sub('', text)
	return tmp
	
def get_short_string(text, length, display_order=0):
	tmp = remove_htmltag(text)
	if display_order>0:
		n = tmp[display_order-1:].find(' ')
		tmp = '...'+tmp[n+1:]
	if length>=len(tmp): return tmp
	n = tmp[:length-1].rfind(' ')
	tmp = tmp[:n]
	return tmp[:n] + '...' 
	
def get_short_string2(text, length, display_order=0):
	tmp = remove_htmltag(text)
	if display_order>0:
		n = tmp[display_order-1:].find(' ')
		tmp = '...'+tmp[n+1:]
	if length>=len(tmp): return tmp
	n = tmp[:length-1].rfind('_')
	tmp = tmp[:n]
	return tmp[:length] + '...' 

def number_format(number, type='integer'):
	if (number == None) | (number=='None'): return number
	f = ''
	s = ''
	v = ''
	if type=='integer': s = str(int(number))
	elif type=='double': 
		s = str(float(number))
		(s,v) = s.split('.')
		if int(v)==0: v=''
		else: v = ','+v
	else:
		return number
	while len(s)>3:
		if f =='': f = s[-3:]
		else: f = s[-3:] + '.' + f
		s = s[:-3]
	if s == '': f = f + v
	elif f =='': f = s + v
	else: f = s + '.' + f + v
	return f
	
def mony_format(number):
	if not number:
		return ""
	number= str(number)
	if len(number)>3:
		if int(number[len(number)-3]) ==0:
			if int(number[len(number)-2]) ==0:
				if int(number[len(number)-1]) ==0:
					return str(number[0:len(number)-3]) +" tỷ "
				else:
					return str(number[0:len(number)-3]) +" tỷ " + str(number[len(number)-1]) +" triệu " 
			else:
				return str(number[0:len(number)-3]) +" tỷ " + str(number[len(number)-2:len(number)]) +" triệu " 
		else:
			return str(number[0:len(number)-3]) +" tỷ " + str(number[len(number)-3:len(number)]) +" triệu " 
	else:
		return str(number) + " triệu"
	
def get_url(url):
	tmp = url.split('/')
	if len(tmp)==1: c,f = 'plugin_app', tmp[0]
	else: c,f = tmp[0], tmp[1]
	tmp = f.split('.')
	if len(tmp)==1: f,e = tmp[0], current.request.extension
	else: f,e = tmp[0], tmp[1]						
	return c,f,e
	
def get_represent(table, field, value, width=30, height=30):
	try:
		if not value: return ''
		db = current.globalenv['db']
		request = current.request
		if (db[table][field].type=='upload'):
			if value[0:7] == 'http://': return XML('<img src=%s width=%s height=%s />'%(value,width,height)) if width*height>0 else XML('<img src=%s />'%(value))
			if os.path.exists(request.folder+'/static/uploads/'+table+'/'+ value):
				value='/%s/static/uploads/%s/%s'%(request.application,table,value)
			else: value='/%s/static/uploads/images/%s'%(request.application,value)
			return XML('<img src=%s width=%s height=%s />'%(value,width,height)) if width*height>0 else XML('<img src=%s />'%(value))	
		elif not value: return XML('&nbsp')
		elif (db[table][field].type[:14]=='list:reference'):
			reference = db[table][field].type[15:]
			tmp = ''
			if 'name' in db[reference].fields:
				for id in value:
					if db[reference](id): tmp += db[reference](id).name + '|'
			elif 'role' in db[reference].fields:
				for id in value:
					if db[reference](id): tmp += db[reference](id).role + '|'
			return tmp[:-1]
		elif (db[table][field].type[:9]=='reference'):
			reference = db[table][field].type[10:]
			if not db[reference](value): return value
			if 'label' in db[reference].fields:
				tmp = db[reference](value).label
				if (tmp <> '')&(tmp<>None): return tmp
			elif 'name' in db[reference].fields: return db[reference](value).name
			elif 'role' in db[reference].fields: return db[reference](value).role
		elif db[table][field].represent:
			return db[table][field].represent(value)
		elif (db[table][field].type=='date'):
			return value.strftime(get_setting('date','%d/%m/%Y'))
		elif (db[table][field].type=='datetime'):
			return value.strftime(get_setting('datetime','%d/%m/%Y %H:%M'))
		elif field=='year': return value
		elif field=='created_by': 
			if db.auth_user(value): return db.auth_user(value).last_name+' '+db.auth_user(value).first_name
		elif (db[table][field].type=='integer')|(db[table][field].type=='double'):
			return number_format(value,db[table][field].type)
	except: pass
	return value	

def input_option(table, type='radio', order=None, selected=[], query=None, field='name', field_id='id',list_id=[],keyname=None, db=None, auth=None):
	db = db or current.globalenv['db']
	auth = auth or current.globalenv['auth']
	if not order:
		order = db[table][field]
		if 'display_order' in db[table].fields: order = db[table].display_order|order
	input = DIV()
	if not keyname: keyname = table
	rows = db(query if query else (db[table].id>0)).select(orderby=order)
	for row in rows:
		if (list_id == [])|(row.id in list_id):
			if auth.has_permission('explorer', db[table], row.id, auth.user_id)|True:	
				v = row[field] or ''
				input.append(SPAN(INPUT(_type=type,_name=keyname,_value=row[field_id],_checked=(row[field_id] in selected)),v,_style="margin-right:20px;"))
	return input
	
def select_option(db, auth, table, id=None, order=None, space='', selected=[], query=None, field='name', field_id='id',list_id=[], level=-1, permission='explorer',length=100):
	if not auth: return select_option_publish(db,table,id,order,space,selected,query,field,field_id,list_id,level)
	if level==0: return []
	option = []
	if not order:
		if 'display_order' in db[table].fields: 
			order = db[table].display_order
		else:
			order = db[table][field]
	if ('parent' in db[table].fields):
		q = (db[table].parent==id)
		if query: q &= query
		rows = db(q).select(orderby=order)
		# if (space =='')&(id !=None):
			# row = db[table](id)
			# if row:
				# if auth.has_permission(permission, db[table], row.id, auth.user_id)|auth.has_membership(role='admin'):
					# option = [OPTION(row[field],_value=row[field_id],_selected=(row[field_id] in selected))]
					# space = '---'
		for row in rows:
			op = []
			if (list_id == [])|(row.id in list_id):
				if auth.has_permission(permission, db[table], row.id, auth.user_id)|auth.has_membership(role='admin'):	
					v = row[field] or ''
					op = [OPTION(space+str(v),_value=row[field_id],_selected=(row[field_id] in selected))]
			tmp = select_option(db,auth,table,row.id,order,space+'---',selected,query,field,field_id,list_id,level-1,permission,length) 	
			option += (op + tmp)
	else:
		rows = db(query if query else (db[table].id>0)).select(orderby=order)
		for row in rows:
			if (list_id == [])|(row.id in list_id):
				if auth.has_permission(permission, db[table], row.id, auth.user_id)|auth.has_membership(role='admin'):	
					v = row[field] or ''
					v = get_short_string(space+str(v), length)
					op = [OPTION(v,_value=row[field_id],_selected=(row[field_id] in selected))]
					option += op
	return option

def select_option_publish(db, table, id=None, order=None, space='', selected=[], query=None, field='name', field_id='id',list_id=[], level=-1):
	if level==0: return []
	option = []
	if not order:
		order = db[table][field] if field in db[table].fields else db[table].id
		if 'display_order' in db[table].fields: order = db[table].display_order|order
	if ('parent' in db[table].fields):
		q = (db[table].parent==id)
		if id==None: q = (q|(db[table].parent==0))
		if query: q &= query
		rows = db(q).select(orderby=order)
		# if (space =='')&(id !=None):
			# row = db(db[table].id==id).select().first()
			# option = [OPTION(row[field],_value=row[field_id],_selected=(row[field_id] in selected))]
			# space = '---'
		for row in rows:
			op = []
			if (list_id == [])|(row.id in list_id):
				v = row[field] or ''
				op = [OPTION(space+v,_value=row[field_id],_selected=(row[field_id] in selected))]
			tmp = select_option_publish(db,table,row.id,order,space+'---',selected,query,field,field_id,list_id,level-1) 	
			option += op + tmp
	else:
		rows = db(query if query else (db[table].id>0)).select(orderby=order)
		for row in rows:
			if (list_id == [])|(row.id in list_id):
				v = row[field] or ''
				op = [OPTION(space+v,_value=row[field_id],_selected=(row[field_id] in selected))]
				option += op
	return option	
	
def get_tree(db,auth,table,parent=None,**attributes):
	depth = attributes.get('depth',-1)
	if depth>0: attributes['depth'] = depth-1
	elif depth==0: return ''
	request = current.request
	selected = attributes.get('selected',[])
	if not isinstance(selected, list): selected = [selected]
	active = attributes.get('active',None)
	field = attributes.get('field','name')
	orderby = attributes.get('orderby',None)
	checkbox = attributes.get('checkbox','radio')
	check = attributes.get('check','check_all')
	key = attributes.get('key',table)
	tree_id = attributes.get('tree',table)
	ajax = attributes.get('ajax',None)
	query = attributes.get('query',db[table].id>0)
	permission = attributes.get('permission',request.vars.permission)
	if isinstance(query,str):
		query = '%s AND %s'%(query, (db[table].parent==parent))
		query = 'SELECT * FROM %s WHERE %s'%(table,query)
		if orderby: query += ' ORDER BY '+str(orderby)
		rows=db.executesql(query,as_dict=True)
	else:
		if 'parent' in db[table].fields: query &= (db[table].parent==parent)
		rows=db(query).select(orderby=orderby)
	tree = UL()
	for row in rows:
		add = row[active] if active else True
		if permission: 
			if add:
				add = auth.has_permission(permission, db[table], row['id'], auth.user_id)
		tmp = get_tree(db,auth,table,row['id'],**attributes) if 'parent' in db[table].fields else ''
		node = row[field]
		if depth==1:
			if db(db[table].parent==row['id']).count()>0:
				_id='%s_%s'%(tree_id,row['id'])
				url = URL(r=request,c='plugin_app',f='treedepth',args=[table,row['id']],vars=attributes,extension='load')
				ajx="ajax('%s', [], '%s')"%(url,_id)
				node = SPAN(A(node,_href='#',_onclick=ajx,_alt='Click'),BR(),DIV(_id=_id),_class='node_parent')
		if add: 
			ajx = ajax.replace('%23id',str(row.id)) if ajax else None
			if checkbox in ['checkbox','radio']:
				node = SPAN(INPUT(_type=checkbox,_name=key,_value=row['id'],_checked=(row['id'] in selected),_onclick=ajx, _class=check),' ',node)
			elif checkbox=='ajax': node = SPAN(A(node,_href='#',_onclick=ajx, _class=check))
			else: node = SPAN(A(node,_href=ajx, _class=check))
		else: node = SPAN(node)
		if ((permission!=None)&add)|(not permission):
			tree.append(LI(node,tmp) if str(tmp)!=str(UL()) else LI(node))
	return tree		

def treeview(db, auth, table, parent=None, **attributes):
	tree_id = attributes.get('tree',table)
	script = SCRIPT('''$(document).ready(function(){
		$("#%s_tree").treeview({
			animated: "fast",
			collapsed: true,
			control:"#%s_control",'''%(tree_id,tree_id)+'''
			persist: "cookie",
			toggle: function() {
				window.console && console.log("%o was toggled", this);
			}
		});
	});''')
	tree = get_tree(db,auth,table,parent,**attributes)
	pnode =  attributes.get('pnode',None)
	if str(tree)!=str(UL()):
		pnode =  attributes.get('pnode',None)
		if pnode: tree = UL(LI(pnode,tree))
	else: return ''		
	header =  attributes.get('header','')
	return DIV(script,header,tree,_id='%s_tree'%tree_id,_class='treeview-red')
	
def widget_select(field, value):
	db = current.globalenv['db']
	auth = current.globalenv['auth']
	table = field.type[10:]
	if "label" in db[table].fields: name = "label"
	elif "name" in db[table].fields: name = "name"
	elif "role" in db[table].fields: name = "role"
	else: name = db[table].fields[1]
	if not value: value = field.default
	widget = SELECT(['']+select_option(db,auth,table,selected=[value],field=name),_name=field.name,requires=field.requires,_class="generic-widget form-control")
	return widget

def widget_folder(field, value):
	table = 'folder'
	list_id = []
	db = current.globalenv['db']
	if not value: 
		if current.request.vars.folder_id: value = int(current.request.vars.folder_id)
	if current.request.vars.procedure_id:
		from plugin_process import define_procedure
		auth = current.globalenv['auth']
		procedure = define_procedure(db,auth)(current.request.vars.procedure_id)
		if procedure: list_id = procedure.folder 
	else:
		row = db(db.object.name==field._tablename).select().first()
		if row: list_id = [r.id for r in db(db.folder.object==row.id).select()]
	widget = SELECT(['']+select_option(db,auth,table,selected=[value],list_id=list_id),_name=field.name,_id=field._tablename+'_'+field.name,requires=field.requires,_class="generic-widget form-control")
	return widget

def widget_folders(field, value):
	db = current.globalenv['db']
	auth = current.globalenv['auth']
	if not value: value = []
	rows = db(db.folder.parent==None).select(orderby=db.folder.display_order|db.folder.name)
	tr = TR()
	for row in rows:
		pnode = XML(str(INPUT(_type='checkbox',_name=field.name,_value=row.id,_checked=(row.id in value),_class='check_all'))+' '+row.name)
		tree = treeview(db,auth,'folder',parent=row.id,checkbox='checkbox',pnode=pnode,key=field.name,selected=value,orderby=db.folder.display_order|db.folder.name,tree=field.name+str(row.id))
		tr.append(TD(tree))
	script = '''<script type="text/javascript">
				$(document).ready(function(){
					$('.check_all').click(function(){
						if ($(this).is(':checked')) {
							$(this).parent().find('input:checkbox').attr('checked', true);
						}
						else{
							$(this).parent().find('input:checkbox').attr('checked', false);
						}
					});
				});
		</script>'''	
	return DIV(XML(script),TABLE(tr))
	
def widget_org(field, value):
	db = current.globalenv['dbprocess']
	auth = current.globalenv['auth']
	if not value: 
		row = db(db.org.auth_group==auth.auth_org).select().first()
		if row: value = [row.id]
	url = URL(r=current.request,c='plugin_app',f='get_signer',extension='load')
	ajax="ajax('%s', ['org'], 'org_signer')"%(url)
	widget = SELECT(select_option(db,auth,'org',selected=value or []),_name=field.name,_onchange=ajax,_multiple=True)
	return widget	
	
def widget_org_tree(field, value):
	db = current.globalenv['dbprocess']
	auth = current.globalenv['auth']
	if not value: 
		row = db(db.org.auth_group==auth.auth_org).select().first()
		if row: 
			if not auth.has_membership(role='admin'):
				if current.request.function=='create':
					if current.request.vars.procedure_id:
						from plugin_process import define_procedure
						procedure = define_procedure(db,auth)
						if procedure(current.request.vars.procedure_id):
							if procedure(current.request.vars.procedure_id).type=='out': 
								db[field.tablename][field.name].readable = False
								db[field.tablename][field.name].writable = False
								db[field.tablename][field.name].default = row.id
								return B(row.name)
	url = URL(r=current.request,c='plugin_app',f='get_signer',extension='load')
	ajax="ajax('%s', ['org'], 'org_signer')"%(url)
	widget = treeview(db,auth,'org',checkbox='checkbox',depth=2,key=field.name,selected=value,ajax=ajax,check='org_tree',orderby=db.org.display_order|db.org.name,tree=field.name)
	return widget
	
def widget_tree(field, value):
	db = current.globalenv['db']
	auth = current.globalenv['auth']
	if not value: value = []
	if field.type[:14] == 'list:reference':
		table = field.type[15:]
		checkbox = 'checkbox'
	elif field.type[:9] == 'reference':
		table = field.type[10:]
		checkbox = 'radio'
	else: return None
	if table=='auth_group':
		name = 'role'
		query = db[table].atype.belongs(['org','group','auth'])
	else: 
		name = 'name'
		query = (db[table].id>0)
	rows = db((db[table].parent==None)&query).select(orderby=db[table].display_order|db[table][name])
	tr = TR()
	for row in rows:
		pnode = XML(str(INPUT(_type=checkbox,_name=field.name,_value=row.id,_checked=(row.id in value),_class='check_all'))+' '+row[name])
		tree = treeview(db,auth,table,parent=row.id,depth=3,checkbox=checkbox,pnode=pnode,query=query,key=field.name,field=name,selected=value,orderby=db[table].display_order|db[table][name],tree=field.name+str(row.id))
		tr.append(TD(tree))
	script = '''<script type="text/javascript">
				$(document).ready(function(){
					$('.check_all').click(function(){
						if ($(this).is(':checked')) {
							$(this).parent().find('input:checkbox').attr('checked', true);
						}
						else{
							$(this).parent().find('input:checkbox').attr('checked', false);
						}
					});
				});
		</script>'''	
	return DIV(XML(script),TABLE(tr))
	
def widget_signer(field, value):
	db = current.globalenv['db']
	auth = current.globalenv['auth']
	if not value:
		row = db(db.org.auth_group==auth.auth_org).select().first()
		query = (db.signer.org==row.id) if row else None
		widget = DIV(SELECT(['']+select_option(db,auth,'signer',query=query),_name=field.name,_id='archives_signer'),_id='org_signer')
	else:
		widget = DIV(SELECT(select_option(db,auth,'signer',selected=value,list_id=value),_name=field.name,_multiple=(len(value)>1),_id='archives_signer'),_id='org_signer')
	return widget	

def widget_input_radio(field, value):
	if not value: value = field.default
	table = field.type[10:]
	widget = input_option(table,selected=[value])
	return widget
	
def widget_radio(field, value):
	table = field.type[10:]
	widget = treeview(db,auth,table,checkbox='radio',key=field.name,selected=value)
	return widget
	
def widget_checkbox(field, value):
	db = current.globalenv['db']
	auth = current.globalenv['auth']
	table = field.type[15:]
	widget = treeview(db,auth,table,checkbox='checkbox',key=field.name,selected=value)
	return widget	
		
def widget_multiselect2(field, value):
	db = current.globalenv.get('db')
	auth = current.globalenv.get('auth')
	table = field.type.split(" ")[1]
	f = db[table].fields[1]
	if "label" in db[table].fields: 
		orderby = db[table].label
		f = "label"
	elif "name" in db[table].fields: 
		orderby = db[table].name
		f = "name"
	elif table=="auth_group": 
		orderby = db[table].role
		f = "role"
	else:
		orderby = db[table].id
	if "display_order" in db[table].fields: 
		orderby = db[table].display_order
	rows = db(db[table]).select(orderby=orderby)
	selected = value or []
	ops = []
	for row in rows:
		v = row[f]
		if table=="auth_user": v = "%s %s"%(row.last_name,row.first_name)
		ops.append(OPTION(v, _value=row.id, _selected=(row.id in selected)))	
	widget = SELECT([""]+ops,_name=field.name,_id="%s_%s"%(table,field.name),_multiple=True,_class="widget_multiselect2 form-control")
	return widget		
		
def widget_multiselect2_ajax(field, value):
	db = current.globalenv.get('db')
	auth = current.globalenv.get('auth')
	table = field.type.split(" ")[1]
	f = db[table].fields[1]
	for a in ["label","name","role"]:
		if a in db[table].fields: 
			f = a
			break
	selected = value or []
	ops = []
	for id in selected:
		row = db[table](id)
		if row:
			v = row[f]
			if table=="auth_user": v = "%s %s"%(row.last_name,row.first_name)
			ops.append(OPTION(v, _value=row.id, _selected=True))	
	widget = SELECT(ops,_name=field.name,_id="%s_%s"%(table,field.name),_multiple=True,_class="form-control")
	url = URL(r=current.request,c="plugin_app",f="get_select2",args=[table,f])
	script = XML('''
<script>
$(document).ready(function() {
	$("#%s").select2({
	  ajax: {
		url: "%s",
		dataType: 'json',
		delay: 0,
		data: function (params) {
		  return {
			q: params.term, // search term
			page: params.page
		  };
		},
		processResults: function (data, page) {
		  return {
			results: data
		  };
		},
		cache: true
	  },
	  escapeMarkup: function (markup) { return markup; },
	  minimumInputLength: 1
	});
});
</script>	
	'''%("%s_%s"%(table,field.name),url))
	widget = SPAN(widget,script)
	return widget	
	
def widget_select2(field, value):
	db = current.globalenv.get('db')
	auth = current.globalenv.get('auth')
	table = field.type.split(" ")[1]
	f = db[table].fields[1]
	if "label" in db[table].fields: 
		orderby = db[table].label
		f = "label"
	elif "name" in db[table].fields: 
		orderby = db[table].name
		f = "name"
	elif table=="auth_group": 
		orderby = db[table].role
		f = "role"
	else:
		orderby = db[table].id
	if "display_order" in db[table].fields: 
		orderby = db[table].display_order
	rows = db(db[table]).select(orderby=orderby)
	ops = []
	for row in rows:
		v = row[f]
		if table=="auth_user": v = "%s %s"%(row.last_name,row.first_name)
		ops.append(OPTION(v, _value=row.id, _selected=(row.id == value)))	
	widget = SELECT([""]+ops,_name=field.name,_id="%s_%s"%(table,field.name),_multiple=False,_class="widget_select2 form-control")
	return widget	
		
def widget_select_supplier(field, value):
	from plugin_cms import Cms
	cms = Cms()
	db = cms.db
	supplier = cms.define_table('supplier')
	dcontent = cms.define_dcontent()
	f = "name"
	orderby = db['supplier'].display_order	
	rows = db((supplier.id==dcontent.table_id)&(dcontent.dtable=='supplier')).select(db.supplier.ALL,orderby=orderby)
	ops = []
	for row in rows:
		v = row[f]
		ops.append(OPTION(v, _value=row.id, _selected=(row.id == value)))	
	widget = SELECT([""]+ops,_name=field.name,_id="%s_%s"%('table',field.name),_multiple=False,_class="widget_select2 form-control")
	return widget	
		
	
def widget_select_by_search(table,name=None,show_name="Tất cả"):
	from plugin_cms import Cms
	cms = Cms()
	db = cms.db
	table = cms.define_table(table)

	rows = db(db[table]).select()
	ops = []
	ops.append(OPTION(show_name, _value=0))
	for row in rows:
		v = row['name']
		ops.append(OPTION(v, _value=row.id, ))
	if name:
		widget = SELECT(ops,_name=name,_multiple=False,_class="widget_select2 form-control")
	else:
		widget = SELECT(ops,_name=table,_multiple=False,_class="widget_select2 form-control")
	return widget	
	

def widget_select_loca(city="",dist="",street=""):
	if not city:
		city = 1
	from plugin_cms import Cms
	cms = Cms()
	db = cms.db
	div = DIV()
	realty_city = cms.define_table("realty_city")
	realty_dist = cms.define_table("realty_dist")
	realty_street = cms.define_table("realty_street")
	
	rows = db(db[realty_city]).select()
	ops = []
	ops.append(OPTION('Tỉnh/Thành phố', _value=0))
	for row in rows:
		v = row['name']
		if city and (city!='0'):
			ops.append(OPTION(v, _value=row.id, _selected=(row.id == int(city))))
		else:	
			ops.append(OPTION(v, _value=row.id))		
	ajax = "ajax('%s', ['%s','%s','%s'], 'widget_select_loca')"%(URL(r=current.request,c='plugin_app',f='widget_select_loca'),"city","dist","street")
	div.append(DIV(SELECT(ops,_name="city",_multiple=False,_class="widget_select2 form-control",_onchange=ajax)))
	
	rows = db(realty_dist.city==city).select()
	ops = []
	ops.append(OPTION('Quận/huyện', _value=0))
	for row in rows:
		v = row['name']
		if city and (city!='0'):
			if dist and (dist!='0'):
				ops.append(OPTION(v, _value=row.id, _selected=(row.id == int(dist))))	
			else:	
				ops.append(OPTION(v, _value=row.id))
	ajax = "ajax('%s', ['%s','%s','%s'], 'widget_select_loca')"%(URL(r=current.request,c='plugin_app',f='widget_select_loca'),"city","dist","street")
	div.append(DIV(SELECT(ops,_name="dist",_multiple=False,_class="widget_select2 form-control",_onchange=ajax)))
	
	rows = db(realty_street.dist==dist).select()
	ops = []
	ops.append(OPTION('Phường/xã', _value=0))
	for row in rows:
		v = row['name']
		if dist and (dist!='0'):
			if street and (street!='0'):
				ops.append(OPTION(v, _value=row.id, _selected=(row.id == int(street))))
			else:	
				ops.append(OPTION(v, _value=row.id))	
	ajax = "ajax('%s', ['%s','%s','%s'], 'widget_select_loca')"%(URL(r=current.request,c='plugin_app',f='widget_select_loca'),"city","dist","street")
	div.append(DIV(SELECT(ops,_name="street",_multiple=False,_class="widget_select2 form-control",_onchange=ajax)))
	
	return div
	
	
def widget_mask_integer(field, value):
	id = "%s_%s"%(field._tablename,field.name)
	v = value
	if v: 
		v = int(v)
		v = "{:,d}".format(v).replace(",",".")
	
	show = INPUT(_id=id+"_show",_value=v,_class="form-control string mask mask-integer")
	hidden = INPUT(_type="hidden",_id=id,_name=field.name,_value=value)
	script = XML('''
<script>
$(document).ready(function(){
	var id = "#%s";
	var show = id+"_show";
	$(show).iMask({type: 'number', decDigits: 0, decSymbol: '', groupSymbol: '.'});
	$(show).keyup(function( event ) {
		$(id).val(parseInt($(show).val().replace( /\D/g, '' )));
	});	
});
</script>'''%(id))			
	return SPAN(show,hidden,script)
		
def widget_month(field, value):
	id = "%s_%s"%(field._tablename,field.name)
	month = INPUT(_type="month",_name=field.name,_id=id,_value=value,_class="form-control string date-month")
	return month		

def widget_date_month(field, value):
	id = "%s_%s"%(field._tablename,field.name)
	if value:
		v = str(value).split("-")
		v = v[0]+"-"+v[1]
	else: v = ""
	show = INPUT(_type="month",_id=id+"_show",_value=v,_class="form-control string date-month")
	hidden = INPUT(_type="hidden",_id=id,_name=field.name,_value=value)
	script = XML('''
<script>
$(document).ready(function(){
	var id = "#%s";
	var show = id+"_show";
	$(show).focusout(function() {
		$(id).val($(show).val()+"-1");
	});	
});
</script>'''%(id))			
	return SPAN(show,hidden,script)

	
def widget_number_name(field, value):
	request = current.request
	if not value:
		from plugin_cms import Cms
		from plugin_cms import CmsFolder
		folder_id = CmsFolder().get_folder(request.args(2))
		cms = Cms()
		document = cms.define_table('documents',True)
		row = cms.db(document.folder==folder_id).select().last()
		if row:
			value = row.name
			number=''
			name =''
			i = 0
			for va in value:
				if i ==0:
					if not va=='/':	number += va
					else: i+=1
				else:name += va
			value = str(int(number)+1) +'/'+ name
	widget = DIV(INPUT(_type='text',_id='name',_name='name',_value=value),_class='so_kyhieu')
	return widget
	

### Tuan anh  update 30/10/2014
# widget chi su dung cho db tu plugin_cms, can dung cho plugin khac thi dinh nghia lai data o get_name(c = plugin_app)
def widget_number_name(field, value):
	request = current.request
	if not value:
		from plugin_cms import Cms
		from plugin_cms import CmsFolder
		folder_id = CmsFolder().get_folder(request.args(2))
		cms = Cms()
		document = cms.define_table('documents',True)
		row = cms.db(document.folder==folder_id).select().last()
		if row:
			value = row.name
			number=''
			name =''
			i = 0
			for va in value:
				if i ==0:
					if not va=='/':	number += va
					else: i+=1
				else:name += va
			value = str(int(number)+1) +'/'+ name
	widget = DIV(INPUT(_type='text',_id='name',_name='name',_value=value),_class='so_kyhieu')
	return widget
		
def widget_auto(f,v):
	from sqlhtml import SQLFORM
	import uuid
	d_id = "autocomplete-" + str(uuid.uuid4())[:8]
	get_url = URL(r=current.request,c='plugin_app',f='get_name')
	wrapper = DIV(_id=d_id)
	inp = SQLFORM.widgets.string.widget(f,v)
	scr = SCRIPT('jQuery("#%s input").autocomplete("%s",{extraParams:{field:"%s",table:"%s"}});' % \
				  (d_id, get_url,f.name,f._tablename))
	wrapper.append(inp)
	wrapper.append(scr)
	return wrapper	
	
def widget_auto_chuc_vu(f,v):
	from sqlhtml import SQLFORM
	import uuid
	d_id = "autocomplete-" + str(uuid.uuid4())[:8]
	get_url = URL(r=current.request,c='plugin_app',f='get_name')
	wrapper = DIV(_id=d_id)
	inp = DIV(SQLFORM.widgets.string.widget(f,v),_id='wrapper_chuc_vu')
	scr = SCRIPT('jQuery("#%s input").autocomplete("%s",{extraParams:{field:"%s",table:"%s"}});' % \
				  (d_id, get_url,f.name,f._tablename))
	wrapper.append(inp)
	wrapper.append(scr)
	return wrapper	
	
	
def widget_auto_co_quan_ban_hanh(f,v):
	from sqlhtml import SQLFORM
	import uuid
	d_id = "autocomplete-" + str(uuid.uuid4())[:8]
	get_url = URL(r=current.request,c='plugin_app',f='get_name')
	wrapper = DIV(_id=d_id)
	inp = DIV(SQLFORM.widgets.string.widget(f,v),_id='wrapper_co_quan_ban_hanh')
	scr = SCRIPT('jQuery("#%s input").autocomplete("%s",{extraParams:{field:"%s",table:"%s"}});' % \
				  (d_id, get_url,f.name,f._tablename))
	wrapper.append(inp)
	wrapper.append(scr)
	return wrapper
	
def widget_auto_nguoi_ky(f,v):
	from sqlhtml import SQLFORM
	import uuid
	d_id = "autocomplete-" + str(uuid.uuid4())[:8]
	get_url = URL(r=current.request,c='plugin_app',f='get_name')
	wrapper = DIV(_id=d_id)
	inp = SQLFORM.widgets.string.widget(f,v)
	scr = SCRIPT('jQuery("#%s input").autocomplete("%s",{extraParams:{field:"%s",table:"%s"} } );'%(d_id, get_url,f.name,f._tablename))
	wrapper.append(inp)
	wrapper.append(scr)
	url1 =URL(r=current.request,c='plugin_app',f='get_chuc_vu')
	url2 =URL(r=current.request,c='plugin_app',f='get_co_quan')
	script = '''<script type="text/javascript">
		jQuery('#archives_user_signed').focusout(function(){
			ajax('%s', ['user_signed'], 'wrapper_chuc_vu');
			ajax('%s', ['user_signed'], 'wrapper_co_quan_ban_hanh');
		});
	</script>'''%(url1,url2)	
	widget= DIV(wrapper,XML(script))
	
	return widget	
	

### End new	
	
def get_start_end_week(datenow=None):
	import datetime;
	if datenow==None:
		datenow = datetime.datetime.now()
	date = datenow.ctime()
	thu = date[0:3]
	start = 0
	end   = 0
	if thu == 'Mon':
		start = 0
		end = 6
	elif thu == 'Tue':
		start = 1
		end = 5
	elif thu == 'Wed':
		start = 2
		end = 4
	elif thu == 'Thu':
		start = 3
		end = 3
	elif thu == 'Fri':
		start = 4
		end = 2
	elif thu == 'Sat':
		start = 5
		end = 1
	elif thu == 'Sun':
		start = 6
		end = 0
	return start,end
	
### Video Youtobe.com	
def widget_url(field, value):
	widget =None
	if value:
		widget = DIV(INPUT(_type='text',_name='url_run',_id='video_url_run',_class='string',_value=value),_id='wrapper_url_run')
	else:
		widget = DIV(INPUT(_type='text',_name='url_run',_id='video_url_run',_class='string'),_id='wrapper_url_run')
	url = URL(r=current.request,c='plugin_app',f='get_url_run')
	scr='''<script>
			$("#videos_url_youtobe").focusout(function() {
				
				if(document.getElementById("videos_url_youtobe").value!=''){
				
				ajax('%s', ['url_youtobe'], 'wrapper_url_run');
				$("#videos_url_run").focus();
				}
			});
			</script>''' %(url)
	widget.append(XML(scr))
	return widget	
	
def multiselect_org(selected=[]):
	db = current.globalenv.get('db')
	from plugin_cms import Cms
	cms = Cms()
	org = cms.define_table('org',True)
	ops = []
	for id in selected:
		row = db.org[id]
		if row:
			v = row['name']
			ops.append(OPTION(v, _value=row.id, _selected=True))	
	widget = SELECT(ops,_name='org_ban_giao',_id="auth_group_select",_multiple=False,_class="form-control")
	url = URL(r=current.request,c="plugin_app",f="get_select2",args=[db.org,'name'])
	script = XML('''
	<script>
	$(document).ready(function() {
		$("#%s").select2({
		  ajax: {
			url: "%s",
			dataType: 'json',
			delay: 0,
			data: function (params) {
			  return {
				q: params.term, // search term
				page: params.page
			  };
			},
			processResults: function (data, page) {
			  return {
				results: data
			  };
			},
			cache: true
		  },
		  placeholder: "Đơn vị nhận bàn giao",
		  allowClear: true,

		  escapeMarkup: function (markup) { return markup; },
		  minimumInputLength: 1
		});
	});
	</script>	
	'''%('auth_group_select',url))
	widget = SPAN(widget,script)
	return widget	
	

def change_img(html):
	domain_naso ="https://quanly.naso.vn"
	from bs4 import BeautifulSoup
	soup = BeautifulSoup(html)
	# return html
	imgs = []
	dir = 'static/uploads/ckeditor'
	for link in soup.find_all('img'):
		url = link.get('src')
		try:
			if url[0:3] != 'http':
				link_new= domain_naso+url
				imgs.append([url,link_new])
		except Exception, e:
			return e
			pass
	for img in imgs: html = html.replace(img[0],img[1])		
	return html
	
def number_text(number):
	try:
		number_text= str(number)
		span = SPAN(_class="btCounter animate", **{'_data-digit-length':len(number_text)})
		j = 0
		for i in number_text:
			# p là số thứ tự 
			num = int(i)
			span1 = SPAN(_class="onedigit p%s d%s"%(len(number_text)-j,num), **{'_data-digit':'3'})
			z = 0
			while z<num:
				span1.append(SPAN(_class="n%s"%z))
				z += 1
			j+=1
			span.append(span1)
		
		return DIV(span,_class='btCounterHolder')
	except Exception, e:
		return e