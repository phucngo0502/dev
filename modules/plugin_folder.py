# -*- coding: utf-8 -*-
###################################################
# This content was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 27/02/2015
###################################################

from gluon import current
from html import *
T = current.T
request = current.request

#####################################################################

import os
def setting_config(key=None,default={},path=None):
	try:
		if not path: path=os.path.join(request.folder,'config.py')
		file = open(path,'r')
		data = file.read().replace(chr(13),'')
		file.close()
		tmp = eval(data)
		if not key: return tmp
		return tmp[key]
	except:
		return default	

			
class Folder:

	def __init__(self,db,auth,**attr):
		self.db = db		
		self.auth = auth
		self.cms = attr.get('cms',current.globalenv['cms'])
		self.tablename = attr.get('tablename','folder')
		self.parent = attr.get('parent',None)
		self.id = attr.get('id',None)
		
	def display_tree(self):
		tree = self.menu(self.parent)
		return tree	
	
	def display_url(self):
		tree = self.menu(self.parent,url_link=True,ul_class='sf-menu sf-vertical sf-js-enabled sf-arrows')
		return tree	

	def menu(self,folder=None,deep=1,url_link=False,**attr):
		table = self.db[self.tablename]
		rows = self.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		for row in rows:
			try:
				if (row.display_order==0):
					pass
				else:
					cls_li = attr.get('li_class_%s'%deep,attr.get('li_class'))
					cls_a = attr.get('a_class_%s'%deep,attr.get('a_class'))
					folder_name =''
					p = self.db(self.db.folder.name==current.request.args(0)).select().first()
					if p:
						if p.parent==folder:
							folder_name = current.request.args(0)
						elif p.parent:
							folder_name = p.parent.name
					if row.name == folder_name:
						cls_li = str(attr.get('li_class_%s'%deep,attr.get('li_class'))) +' folder_act'
						cls_a = str(attr.get('a_class_%s'%deep,attr.get('a_class'))) +' a_act'
					link = A(row.label,_href='#',_onclick='',_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					if url_link:
						link = A(row.label,_href=row.url_link,_onclick='',_class=cls_a,_id=attr.get('a_id_%s'%deep,attr.get('a_id')))
					content.append(LI(link,self.menu(row.id,deep+1,**attr),_class=cls_li,_id=attr.get('li_id_%s'%deep,row.id)))
			except Exception, e: 
				print e
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content

		
class FolderCrud(Folder):

	def widget_folder(self, field, value):
		from plugin_app import select_option
		widget = SELECT(['']+select_option(self.db,self.auth,self.tablename,id=self.parent,selected=[value],field='label'),_name=field.name,_id=field._tablename+'_'+field.name,requires=field.requires)
		return widget	
		
	def widget_layout(self, field, value):
		import os
		files = []
		from plugin_config import Configsite
		site_name = Configsite().site_name
		template = Configsite().template
		if template !='':
			for root, dirs, files in os.walk(current.request.folder+'/views/site/%s/%s'%(site_name,template)):
				pass
		else:
			for root, dirs, files in os.walk(current.request.folder+'/views/site'):
				pass
		op = [""]+[OPTION(file,_value=file,_selected=(value==file)) for file in files]
		widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name,_class="form-control")
		return widget

	def widget_setting(self, field, value):
		from plugin_app import input_option
		from plugin_cms import get_setting
		tables = []
		if value:
			tables = get_setting(value,"TABLES",[])
		self.cms.define_dtable()
		tmp = input_option('dtable', type='checkbox', selected=tables, keyname="tables", field_id="name", field="name")
		widget = DIV(B(I(current.T("Tables of folder:"))), tmp, _id='widget_setting')
		return widget
	
	def form_edit(self,id=None):	
		from sqlhtml import SQLFORM
		from plugin_ckeditor import CKEditor
		ckeditor = CKEditor(self.db)
		
		table = self.db[self.tablename]
		table.parent.widget = self.widget_folder
		table.layout.widget = self.widget_layout
		table.folder_top.widget=ckeditor.widget
		table.folder_bottom.widget=ckeditor.widget
		
		# table.setting.widget = self.widget_setting
		for field in table.fields: table[field].label = current.T("%s %s"%(self.tablename.capitalize(), field.capitalize()))
		
		form = SQLFORM(table,id)
		if form.process().accepted: print 'ok'
		return form	
		
	def form(self,id=None):	
		from sqlhtml import SQLFORM
		from plugin_ckeditor import CKEditor
		ckeditor = CKEditor(self.db)
		table = self.db[self.tablename]
		table.parent.widget = self.widget_folder
		table.layout.widget = self.widget_layout
		table.folder_top.widget=ckeditor.widget
		table.folder_bottom.widget=ckeditor.widget
		
		table.setting.widget = self.widget_setting
		if not current.request.vars.folder:
			table.name.readable = False
			table.name.writable = False
			table.name.avatar = False
			table.name.avatar = False
		for field in table.fields: table[field].label = current.T("%s %s"%(self.tablename.capitalize(), field.capitalize()))
		if id:
			form = SQLFORM(table,id)
			if form.process().accepted: print 'ok'
		else:
			form = SQLFORM(table,id,showid=True,buttons=[],deletable=True)
		return form
										
	def update(self,id,vars):	
		table = self.db[self.tablename]
		if vars.delete_this_record:
			self.db(table.id==id).delete()
			return id
		val = {}
		for field in table.fields:
			if field in vars.keys(): val[field] = vars[field]
		tables =  vars.tables
		if tables:
			if isinstance(tables,str): tables = [tables]
			val['setting'] = "{'TABLES':%s}"%tables
		if "name" not in val.keys():
			from validators import IS_SLUG
			name = val["label"]	
			name = name.replace('đ','d')
			name = name.replace('Đ','d')
			name = IS_SLUG.urlify(name)
			i = 1
			tmp = name
			while self.db(table.name==tmp).count()>0:
				tmp = '%s-%s'%(name,i) 
				i+=1
			name = tmp			
			val["name"] = name
		if id:
			self.db(table.id==id).update(**val) 
		else: 
			id = table.insert(**val)
			self.update_permission(id,val["parent"])
		return id
																				
	def update_permission(self,id,parent):
		try:
			auth_permission = self.db[self.auth.settings.table_permission_name]
			rows = self.db((auth_permission.table_name==self.tablename)&(auth_permission.record_id==parent)).select()
			for row in rows:
				auth_permission.insert(group_id=row.group_id,name=row.name,table_name=self.tablename,record_id=id)
			self.db.commit()
		except Exception, e:
			print e
			