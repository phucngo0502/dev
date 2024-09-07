# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
# Version 0.2 Date: 07/03/2014
# Version 0.3 Date: 22/05/2015
# Version 1.0 Date: 14/09/2015
###################################################
from gluon import current, LOAD, redirect
from html import *
from gluon.dal import Field
from validators import IS_IMAGE, IS_NULL_OR, IS_IN_SET, IS_EMPTY_OR, IS_NOT_EMPTY
import os
from plugin_app import get_short_string

PROCEDURE = 0
PROCESS = 1
FOLDER = 2
PAGE = 3
TABLENAME = 3
OBJECTSID = 4
SEARCHPREFIX = "search__"
FIELDPREFIX = "field__"
		
class ProcessModel:
	def __init__(self,**attr):
		self.init(**attr)
						
	def init(self,**attr):
		self.db = attr.get('db',current.globalenv.get('db'))
		self.auth = attr.get('auth',current.globalenv.get('auth'))
		self.cms = attr.get('cms',current.globalenv.get('cms'))
		self.cms.auth = self.auth
		self.vars = {}
			
	def define_procedures(self,migrate=False):
		if 'procedures' not in self.db.tables: 
			self.db.define_table('procedures',
				Field('name',unique=True,required=True,length=255),
				Field('label',requires=IS_NOT_EMPTY()),
				Field('description'),
				Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/uploads/procedures')),
				Field('user_group','reference auth_group'),
				Field('auth_group','list:reference auth_group'),
				Field('folder_parent','integer'),
				Field('folder','list:integer',default=[],readable=False,writable=False),
				Field('ptype',default='on',requires=IS_IN_SET(['in','on','out'])),
				Field('controller',default="plugin_process"),
				Field('tablename',required=True),
				Field('year_field'),
				Field('is_create','boolean',default=True),
				Field('select_year','boolean',default=False),
				Field('setting','text'),
				Field('display_order','integer',default=100),
				format='%(name)s',
				migrate=migrate)
			self.db.procedures.avatar.represent = lambda value,row: IMG(_src=URL(r=current.request,c='static',f='uploads/procedures',args=[value]))

		return self.db.procedures

	def define_process(self,migrate=False):	
		if 'process' not in self.db.tables: 
			self.define_procedures(migrate)
			self.db.define_table('process',
				Field('procedures','reference procedures'),
				Field('paccess','list:reference process',default=[]),
				Field('pnext','reference process'),
				Field('name',unique=True,required=True,length=255),
				Field('label',requires=IS_NOT_EMPTY()),
				Field('description',default=''),
				Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/uploads/process')),
				Field('auth_group','list:reference auth_group',label='Groups use this process'),
				Field('view_group','list:reference auth_group',label='Groups view this process'),
				Field('process_group','list:reference auth_group',label='Process to groups'),
				Field('pmode',requires=IS_EMPTY_OR(IS_IN_SET(['radio','checkbox','set','return','org']))),
				Field('ptype',default='on',requires=IS_IN_SET(['in','on','out'])),
				Field('url'),
				Field('is_first','boolean',default=False),
				Field('is_copy','boolean',default=False),
				Field('is_confirm','boolean',default=False),
				Field('is_lock','boolean',default=False),
				Field('is_comment','boolean',default=False),
				Field('tablename',writable=False,readable=False),
				Field('field','list:string',writable=False,readable=False),
				Field('setting','text'),
				Field('display_order','integer',default=100),
				Field('time_feedback','integer',default=0,writable=False,readable=False),
				Field('time_type',default='days',requires=IS_IN_SET(['days','hours','minutes','weeks']),writable=False,readable=False),
				format='%(name)s',
				migrate=migrate)
			self.db.process.avatar.represent = lambda value,row: IMG(_src=URL(r=current.request,c='static',f='uploads/process',args=[value]))
		return self.db.process		
			
	def define_objects(self,migrate=False):	
		if 'objects' not in self.db.tables: 
			self.define_process(migrate)
			self.db.define_table('objects',
				Field('folder','integer'),
				Field('foldername'),
				Field('tablename'),
				Field('table_id','integer'),
				Field('objects_id','integer'),
				Field('process','reference process'),
				Field('auth_group','reference auth_group'),
				Field('auth_org','reference auth_group',default=self.auth.auth_org),
				Field('publish_on','datetime',default=current.request.now),
				Field('expired_on','datetime'),
				Field('ocomment','text',default=""),
				Field('created_by','integer',default=self.auth.user_id or 1),
				Field('created_on','datetime',default=current.request.now),
				format='%(tablename)s %(table_id)s',
				migrate=migrate)
		return self.db.objects		

	def define_process_lock(self,migrate=False):	
		if 'process_lock' not in self.db.tables: 
			self.define_process(migrate)
			self.db.define_table('process_lock',
				Field('tablename'),
				Field('table_id','integer'),
				Field('objects_id','integer'),
				Field('process','integer'),
				Field('comment_lock','text'),
				Field('comment_unlock','text'),
				Field('lock_by','integer',default=self.auth.user_id or 1),
				Field('lock_on','datetime',default=current.request.now),
				Field('unlock_on','datetime'),
				format='%(tablename)s %(table_id)s',
				migrate=migrate)
		return self.db.process_lock
		
	def define_process_log(self,migrate=False):	
		if 'process_log' not in self.db.tables: 	
			self.define_objects(migrate)
			self.define_process(migrate)
			self.db.define_table('process_log',
				Field('objects','reference objects'),
				Field('process','reference process'),
				Field('auth_group','reference auth_group'),
				Field('created_by','integer',default=self.auth.user_id or 1),
				Field('created_on','datetime',default=current.request.now),
				migrate=migrate)
		return self.db.process_log
	
	def define_isread(self,migrate=False):
		if 'isread' not in self.db.tables: 	
			self.db.define_table('isread',
				Field('objects','integer'),
				Field('created_by','integer',default=self.auth.user_id or 1),
				Field('created_on','datetime',default=current.request.now),
				migrate=migrate)		
		return self.db.isread

	def get_id(self,tablename,value,field='name'):
		table = eval('self.define_%s()'%tablename)
		row = self.db(table[field]==value).select().first()
		return row.id if row else 0		

	def widget_folder(self, field, value):
		from plugin_app import select_option
		cms = self.cms
		cms.define_folder()
		list_id = []
		try:
			if not value: 
				if current.request.args[FOLDER]: 
					value = cms.get_id('folder',current.request.args[FOLDER])
			if current.request.args[PROCEDURES]:
				procedure = self.define_procedures()
				list_id = procedure(current.request.args[PROCEDURES]).folder 
		except:
			pass
		widget = SELECT(['']+select_option(cms.db,self.auth,'folder',field='label',selected=[value],list_id=list_id,permission=current.request.function),_name=field.name,_id=field._tablename+'_'+field.name,requires=field.requires)
		return widget
		
#####################################################################
## PROCEDURE CLASS
		
class Procedures(ProcessModel):
	def __init__(self,**attr):
		self.init(**attr)
		self.procedure_name = attr.get('procedure',current.request.args(PROCEDURE))
		
	def menu(self,auth_group=[]):	
		import datetime
		if not auth_group: return ''
		request = current.request
		procedures = self.define_procedures()
		process = self.define_process()
		menu = UL(_class="dropdown-menu",_role="menu")
		rows = self.db(procedures.auth_group.contains(auth_group)).select(orderby=procedures.display_order)
		folder = self.cms.define_folder()
		year = datetime.datetime.now().year
		for row in rows: 
			p = self.db((process.procedures==row.id)&(process.is_first==True)).select().first()
			if not p: p = self.db(process.procedures==row.id).select(orderby=process.display_order).first()
			pname = p.name if p else None
			fname = folder(row.folder_parent).name if folder(row.folder_parent) else None
			url = URL(r=request,c=row.controller or "plugin_process",f='explorer',args=[row.name,pname,fname],vars={FIELDPREFIX+row.year_field:year} if row.year_field else {}) 
			title = current.T((row.label or row.name))
			menu.append(LI(A(I(_class="fa fa-table fa-fw"),title,_href=url)))
		return menu
		
	def menu_dashboard(self,auth_group=[]):	
		import datetime
		if not auth_group: return ''
		request = current.request
		procedures = self.define_procedures()
		process = self.define_process()
		menu = DIV(_class="def_menu_dashboard row")
		rows = self.db(procedures.auth_group.contains(auth_group)).select(orderby=procedures.display_order)
		folder = self.cms.define_folder()
		year = datetime.datetime.now().year
		for row in rows: 
			p = self.db((process.procedures==row.id)&(process.is_first==True)).select().first()
			if not p: p = self.db(process.procedures==row.id).select(orderby=process.display_order).first()
			pname = p.name if p else None
			fname = folder(row.folder_parent).name if folder(row.folder_parent) else None
			url = URL(r=request,c=row.controller or "plugin_process",f='explorer',args=[row.name,pname,fname],vars={FIELDPREFIX+row.year_field:year} if row.year_field else {}) 
			settings = {}
			if row.setting:
				settings = eval(row.setting.replace(chr(13),''))
			title = current.T((row.label or row.name))
			item_menu = DIV(_class='panel %s'%(settings.get("menu_wrapper",'panel-primary')))
			item_menu.append(DIV(DIV(DIV(I(_class='fa %s fa-4x'%(settings.get("menu_icon",'fa-tasks'))),_class='col-xs-3'),DIV(DIV(_class='huge'),H4(title),_class='col-xs-9 text-right'),_class='row'),_class='panel-heading'))
			item_menu.append(A(DIV(DIV(SPAN(current.T("Xem chi tiết"),_class='pull-left'),SPAN(I(_class='fa fa-arrow-circle-right'),_class='pull-right'),DIV(_class='clearfix')),_class='panel-footer'),_href=url))
			menu.append(DIV(item_menu,_class='col-lg-2 col-md-4'))
			# menu.append(LI(A(I(_class="fa fa-table fa-fw"),title,_href=url)))
		return menu


#####################################################################
## PROCESS CLASS
		
class Process(ProcessModel):
	def __init__(self,**attr):
		self.init(**attr)
		request = current.request
		if request.args(OBJECTSID):
			objects = self.define_objects()(request.args(OBJECTSID))
			if not objects:
				redirect(URL(r=request,vars=request.vars,args=request.args[:-1]),client_side=True)
	
		self.procedure_name = attr.get('procedure',request.args(PROCEDURE))
		p = self.define_procedures()
		row = self.db(p.name==self.procedure_name).select().first()
		if row: 
			process = self.define_process()
			if request.vars.process:
				self.process_id = int(request.vars.process)
				self.process_name = process(self.process_id).name
			else:
				self.process_name = attr.get('process',request.args(PROCESS))
				self.process_id = self.get_id('process',self.process_name)
			
			if self.process_id==0:
				self.process_id = self.get_process_first()
				self.process_name = process(self.process_id).name if process(self.process_id) else None
			
			self.folder_id = attr.get('folder_id',request.vars.folder_id)
			if not self.folder_id:
				self.folder_name = attr.get('folder',request.args(FOLDER))
				self.folder_id = self.cms.get_id('folder',self.folder_name)
			
			self.tablename = row.tablename
			self.year_field = row.year_field
			self.c = attr.get('c', row.controller or request.controller)
					
			self.auth_group = self.db.auth_user(self.auth.user_id).auth_group if self.db.auth_user(self.auth.user_id) else None
			self.auth_groups = self.auth.auth_groups()

			self.buttons = attr.get('buttons',[])			
			self.objects_id = attr.get('objects_id',request.args(OBJECTSID))
			self.table_id = self.get_table_id()	
			
			self.settings = {}
			dtable = self.cms.define_dtable()
			r = self.cms.db(dtable.name==self.tablename).select().first()
			if r:
				self.settings = eval(r.setting or "{}")
				for field in dtable.fields:
					if field not in ["id","name","settings","description"]: self.settings[field] = r[field]	
				p = process(self.process_id)
				if p:
					settings = eval(p.setting.replace(chr(13),'')) if p.setting else {}
					for key in settings.keys(): self.settings[key] = settings[key]
			
			self.query = None
			self.table = self.cms.define_table(self.tablename)	
			self.vars = {}
			self.year_value = None
			for field in self.table.fields:
				v = attr.get(field,request.vars.get(FIELDPREFIX+field))
				if v: 
					if not self.query: self.query = (self.table.id>0)
					if field==self.year_field:
						v = str(v)
						self.year_value = v
						tmp = v.split("-")
						if self.table[field].type in ["date","datetime"]:
							if len(tmp)==2:
								self.query &= (((self.table[field].year()>=tmp[0])&(self.table[field].year()<=tmp[1]))|(self.table[field]==None))
							else:
								self.year_value = int(v)
								self.query &= ((self.table[field].year()==self.year_value)|(self.table[field]==None))
						elif self.table[field].type =="integer":
							if len(tmp)==2:
								self.query &= (((self.table[field]>=tmp[0])&(self.table[field]<=tmp[1]))|(self.table[field]==None))
							else:			
								self.year_value = int(v)
								self.query &= ((self.table[field]==self.year_value)|(self.table[field]==None))
					elif self.table[field].type.startswith("reference"):
						ref = self.table[field].type.split(" ")[1]
						table = self.cms.define_table(ref)
						if "parent" in table.fields:
							ids = self.get_childs(self.cms.db,ref,v)
							self.query &= self.table[field].belongs(ids)	
						else:		
							self.query &= (self.table[field]==v)
					elif self.table[field].type.startswith("list:reference"):
						self.query &= self.table[field].contains(v)
					else:		
						self.query &= (self.table[field]==v)
					self.vars[FIELDPREFIX+field] = v	
		else:
			self.folder_id = None

	def get_childs(self,db,table,parent=None):
		ids = [parent]
		rows = db(db[table].parent==parent).select(db[table].id)
		for row in rows: ids += self.get_childs(row.id)
		return ids
			
	def get_table_id(self):		
		if not self.objects_id: return None
		objects = self.define_objects()
		return objects(self.objects_id).table_id if objects(self.objects_id) else None 

	def get_process_first(self):		
		procedure_id = self.get_id('procedures',self.procedure_name)		
		process = self.define_process()
		row = self.db((process.procedures==procedure_id)&(process.is_first==True)).select().first()
		if not row: row = self.db(process.procedures==procedure_id).select(orderby=process.display_order).first()
		return row.id if row else None
		
	def create_objects(self,folder_id,tablename,table_id):
		process_first = self.get_process_first()
		auth_groups = self.db.process(process_first).process_group or [self.auth_group]
		objects = self.define_objects()
		self.define_isread()
		log = self.define_process_log()
		folder = self.cms.define_folder()
		foldername = folder(folder_id).name
		for auth_group in auth_groups:
			objects_id = objects.insert(folder=folder_id,foldername=foldername,tablename=tablename,table_id=table_id,auth_group=auth_group,process=process_first)
			self.is_read(objects_id,True)
			log.insert(objects=objects_id,auth_group=auth_group,process=process_first)
		if "processid" in self.table.fields: self.table(table_id).update_record(processid=process_first)
		current.cache.ram.clear(None)	
		return objects_id
		
	def create_objects_work(self,folder_id,tablename,table_id,process,auth_groups):
		process_first =process
		objects = self.define_objects()
		self.define_isread()
		log = self.define_process_log()
		folder = self.cms.define_folder()
		foldername = folder(folder_id).name
		if isinstance(auth_groups, list):
			auth_groups = auth_groups
		else:
			auth_groups = [auth_groups]
		for auth_group in auth_groups:
			objects_id = objects.insert(folder=folder_id,foldername=foldername,tablename=tablename,table_id=table_id,auth_group=auth_group,process=process_first)
			log.insert(objects=objects_id,auth_group=auth_group,process=process_first)
		current.cache.ram.clear(None)	
		return objects_id
		
	def update_folder(self,folder_id,tablename,table_id):
		folder = self.cms.define_folder()
		foldername = folder(folder_id).name
		objects = self.define_objects()
		self.db((objects.tablename==tablename)&(objects.table_id==table_id)).update(folder=folder_id,foldername=foldername)

	def delete(self,objects_ids=None):
		from plugin_cms import CmsPublish
		cms = CmsPublish()
		if not objects_ids: objects_ids = self.get_objects_ids()
		objects = self.define_objects()
		log = self.define_process_log()
		for id in objects_ids:
			o = objects(id) 
			cms.delete(o.tablename,o.table_id)
			self.db((objects.tablename==o.tablename)&(objects.table_id==o.table_id)).delete()
		current.cache.ram.clear(None)	
		
	def delete_objects(self,objects_ids=[]):
		db = self.db
		auth = self.auth
		log = self.define_process_log()
		for id in objects_ids:	
			db(db.objects.id==id).delete()
			log.insert(objects=id,auth_group=self.auth_group,process=self.process_id)
		current.cache.ram.clear(None)	
			
	def is_lock(self,tablename,table_id):
		pl = self.define_process_lock()
		lock = self.db((pl.tablename==tablename)&(pl.table_id==table_id)&(pl.unlock_on==None)).select().last()
		return (lock!=None)
			
	def get_toolbars(self):
		if not self.process_name: return ''
		T = current.T
		auth = self.auth
		db = self.db
		request = current.request
		content = DIV(_id='toolbars_process')
		query = db.process.paccess.contains(self.process_id)&db.process.auth_group.contains(self.auth_groups,all=False)	
		rows = db(query).select(orderby=db.process.display_order)
		if self.objects_id:
			objects = self.define_objects()[self.objects_id] 
			pl = self.define_process_lock()
			process_lock = db((pl.tablename==objects.tablename)&(pl.table_id==objects.table_id)&(pl.unlock_on==None)).select().last()
		else:
			process_lock = None
		for row in rows:
			settings = eval(row.setting.replace(chr(13),'')) if row.setting else {}
			icon = settings.get('toolbars_icon')
			if icon: icon = I(_class="fa %s fa-fw"%icon)
			elif row.avatar: icon = IMG(_src='http://%s/%s/static/uploads/process/%s'%(request.env.http_host,request.application,row.avatar))
			else: icon = ""
			name = SPAN(icon,SPAN(T(row.label or row.name)))
			process = A(name,_href='#',_class='btn btn-default button_process_%s'%(row.is_confirm or False),_id='process_%s'%row.id)
			if self.objects_id:
				if process_lock:
					if (row.id == process_lock.process)&(process_lock.lock_by==auth.user_id): 
						content.append(process)
						name = SPAN(icon,SPAN(T('Unlock')))
						process = A(name,_href='#',_class='btn btn-default button_process_unlock',_id='process_%s'%row.id)
						content.append(process)
				elif row.is_lock:
					name = SPAN(icon,SPAN(T('Lock for %s'%row.name)))
					process = A(name,_href='#',_class='btn btn-default button_process_lock',_id='process_%s'%row.id)
					content.append(process)
				else:
					content.append(process)
			elif settings.get('check_group',False): content.append(process)
		
		if (self.settings.get('delete_toolbar')==True)&(self.auth.has_permission("delete", "folder")|self.auth.has_membership(role='admin')): 
			avatar='http://%s/%s/static/uploads/process/%s'%(request.env.http_host,request.application,'delete.png') 
			label = SPAN(IMG(_src=avatar),SPAN(T("Delete")))
			process = A(label,_href='#',_class='btn btn-default button_process_True',_id='process_delete')
			content.append(process)
		if self.objects_id:
			if self.settings.get('edit_toolbar',True): 
				avatar='http://%s/%s/static/uploads/process/%s'%(request.env.http_host,request.application,'edit.png') 
				label = SPAN(IMG(_src=avatar),SPAN(T("Edit")))
				process = A(label,_href='#',_class='btn btn-default button_process_False',_id='process_edit')
				content.append(process)
		return content

	def get_filter(self):
		T = current.T
		db = self.db
		request = current.request
		process = self.define_process()
		procedure_id = self.get_id('procedures',request.args(PROCEDURE))		
		rows = db((process.procedures==procedure_id)&process.view_group.contains(self.auth_groups,all=False)).select(orderby=process.display_order)
		if len(rows)==0: return ''
		content = UL(_id='filter_process',_class='nav nav-tabs')
		args = [arg for arg in request.args[:TABLENAME]]
		while len(args)<=PROCESS: args.append('')
		role = db.auth_user(self.auth.user_id).role
		for row in rows: 
			settings = eval(row.setting.replace(chr(13),'')) if row.setting else {}
			icon = settings.get('filter_icon')
			if icon: icon = I(_class="fa %s fa-fw"%icon)
			elif row.avatar: icon = IMG(_src='http://%s/%s/static/uploads/process/%s'%(request.env.http_host,request.application,row.avatar))
			else: icon = ""
			label = settings.get('filter_label',"")
			if (label==""): label = 'Filter %s %s'%((row.label or row.name),role)
			name = SPAN(icon,T(label),role="presentation")
			args[PROCESS] = row.name 
			url = URL(r=request,c=self.c,f='explorer',args=args,vars=self.vars)
			cls ='nav_item active' if request.args(PROCESS) == row.name else 'nav_item'
			query = self.get_query(row.id)	
			count = db(query).count(db.objects.id)
			if (settings.get("filter_show")==True)|(count>0)|(row.name==self.process_name):
				content.append(LI(A(name," ",SPAN(count,_class="badge"),_href=url,_id='process_filter',_class='filter_process_selected filter_%s'%row.name if row.name==self.process_name else 'filter_process filter_%s'%row.name),_class=cls))
		return content

	def toolbars(self):
		request = current.request
		return LOAD(r=request,c=self.c,f="toolbars",args=request.args,vars=current.request.vars,ajax=False)

	def filter(self):
		request = current.request
		return LOAD(r=request,c=self.c,f="filter",args=request.args,vars=self.vars,ajax=False)		
		
	def process_lock(self,process_id,objects_ids,lock=True,comment=''):
		db = self.db
		auth = self.auth
		pl = self.define_process_lock()
		self.define_objects()
		try:
			if lock:
				for id in objects_ids:
					objects = db.objects(id)
					pl.insert(tablename=objects.tablename,table_id=objects.table_id,objects_id=id,process=process_id,comment_lock=comment)
			else:
				for id in objects_ids:
					objects = db.objects(id)
					db((pl.tablename==objects.tablename)&(pl.table_id==objects.table_id)&(pl.process==process_id)&(pl.lock_by==auth.user_id)&(pl.unlock_on==None)).update(comment_unlock=comment,unlock_on=current.request.now)
			return 'OK'		
		except Exception, e:
			return e
			
	def process_run(self,process_id,objects_ids):
		process = self.define_process()
		process = process(process_id)
		if current.request.vars.comment_lock: 
			return self.process_lock(process_id,objects_ids,True,current.request.vars.comment_lock)
		elif current.request.vars.comment_unlock:
			return self.process_lock(process_id,objects_ids,False,current.request.vars.comment_unlock)
		elif process.url: 
			args = [self.procedure_name,self.process_name,self.folder_name]
			if self.tablename: 
				args.append(self.tablename)
				if self.objects_id: args.append(self.objects_id)
			elif current.request.vars.objects:
				if isinstance(current.request.vars.objects,str):
					args = [self.procedure_name,self.process_name,self.folder_name,self.tablename,self.objects_id]
					self.objects_id = int(current.request.vars.objects)
					args[OBJECTSID] = self.objects_id
					objects = self.define_objects()(self.objects_id)
					args[TABLENAME] = objects.tablename
					folder = self.cms.define_folder()
					if folder(objects.folder):
						args[FOLDER] = folder(objects.folder).name
			vars = {}
			for key in current.request.vars: vars[key]=current.request.vars[key]
			if '.cb' in process.url: 
				try:
					return self.bootrapmodal(process.label,self.load(process.url,args,vars))
				except Exception, e:
					print e
					return e
			url = self.get_url(process.url,args,vars)
			redirect(url,client_side=True)
		elif process.pmode in ['return']: 
			return self.process_group(process_id,objects_ids,[])
		elif process.pmode in ['radio','checkbox']: 
			return self.process_tree(process_id,selected=process.process_group or [])
		elif not process.pmode: 
			return self.process_group(process_id,objects_ids,process.process_group or [])
		else: 
			return self.process_group(process_id,objects_ids,[self.auth_group])
		
	def process_tree(self,process_id,selected,header=''):
		from plugin_app import treeview	
		request = current.request
		T = current.T
		db = self.db
		self.define_process()
		process = db.process(process_id)
		permission = self.settings.get('permission',None)
		type=process.pmode if process.pmode in ['checkbox','radio'] else 'checkbox'
		if process.process_group:
			query = db.auth_group.id.belongs(process.process_group)
		else:
			query= (db.auth_group.atype!='auth')
			if process.ptype=='on': 
				query &=(db.auth_group.parent== self.auth.auth_org)
			else: 
				query &= ~db.auth_group.atype.belongs(['sub_org','staff','group_org'])
				query &= (db.auth_group.parent==None)
		rows = db(query).select(orderby=db.auth_group.display_order)
		query = (db.auth_group.id>0)
		tr = TR()
		for row in rows:
			pnode = XML(str(INPUT(_type=type,_name='auth_group',_value=row.id,_checked=(row.id in selected),_class='check_all'))+ ' '+row.role)
			tree = treeview(self.db,self.auth,'auth_group',parent=row.id,permission=permission,field='role',depth=5,query=query,pnode=pnode,checkbox=type,selected=selected,orderby=db.auth_group.display_order|db.auth_group.role,tree='auth_group_'+str(row.id))
			if tree =="": tree = pnode
			tr.append(TD(tree))
		tree = TABLE(tr,_class="table")				
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
		# ajax = "ajax('%s', ['auth_group'], '')"%(URL(r=request,c='plugin_process',f='group.html',args=request.args,vars=request.vars))
		# button = INPUT(_type='button',_value=T('Submit'),_onclick=ajax,_id='button_submit')
		# form = DIV(XML(script),H4(T(process.name)),header,tree,button,_id='process_tree')
		form = FORM(XML(script),H4(T(process.label or process.name)),header,tree,BR(),INPUT(_type='submit',_value=T('Submit'),_id='button_submit',_class="btn btn-primary"),_action=URL(r=request,c='plugin_process',f='group.html',args=request.args,vars=request.vars))
		header = ""
		return self.bootrapmodal(header,form,footer="")
		
	def process_group(self,process_id=None,objects_ids=None,group_ids=[]):
		T = current.T
		db = self.db
		auth = self.auth
		button = XML('<button type="button" class="btn btn-default btn-modal" data-dismiss="modal">%s</button>'%T("Close"))
		try:
			if not process_id:
				if current.request.vars.process: process_id = int(current.request.vars.process)
			if not objects_ids:
				objects_ids = self.get_objects_ids()
			nb =  len(objects_ids)
			if self.settings.get("link_verify"):
				div = self.load(self.settings.get("link_verify"),args=current.request.args,vars=dict(process=process_id,objects=objects_ids),removetag=True)
				objects_ids = eval(div)
			if len(objects_ids) == 0:
				content = DIV(H4(T("Dữ liệu chọn chưa đủ điều kiện thực hiện!")),button)
			else:
				log = self.define_process_log()
				process = db.process(process_id)
				pnext = process.pnext or process_id
				i = 0	
				ocomment = current.request.vars.ocomment or ""

				for id in objects_ids:
					objects_id = id
					objects = db.objects(id)
					db.objects.folder.default = objects.folder
					db.objects.foldername.default = objects.foldername
					
					if "processid" in self.table.fields: self.table(objects.table_id).update_record(processid=pnext)
					
					if process.is_copy:
						if group_ids==[]:
							objects_id = db.objects.insert(tablename=objects.tablename,table_id=objects.table_id,objects_id=id,process=pnext,auth_group=self.auth_group,ocomment=ocomment)
							log.insert(objects=objects_id,process=pnext,auth_group=self.auth_group)
						if process.pnext:
							db((db.objects.id==id)).update(process=process_id,ocomment=ocomment)
					else:
						if (process.pmode=='return'): 
							objects_id = objects.objects_id
							db((db.objects.objects_id==id)&(db.objects.auth_org==auth.auth_org)).delete()
							db(db.objects.id==id).delete()
							db((db.objects.id==objects_id)).update(process=pnext,ocomment=ocomment)
						else:
							db(db.objects.id==id).update(process=pnext,ocomment=ocomment)
							objects_id = id
							
						# db((db.objects.objects_id==objects_id)&(db.objects.auth_org==auth.auth_org)).update(process=pnext,ocomment=ocomment)
						# db((db.objects.id==objects_id)&(db.objects.auth_org==auth.auth_org)).update(process=pnext,ocomment=ocomment)

						log.insert(objects=objects_id,process=pnext,auth_group=self.auth_group)
		
					if self.settings.get("update_process_all"):
						q = (db.objects.tablename==objects.tablename)&(db.objects.table_id==objects.table_id)
						db(q).update(process=pnext,ocomment=ocomment)
						log.insert(objects=objects_id,process=pnext)
					else:
						for id in group_ids: 
							if process.is_copy:
								db.objects.insert(tablename=objects.tablename,table_id=objects.table_id,objects_id=objects_id,auth_group=id,process=pnext,expired_on=None,ocomment=ocomment)
							else:
								#q = (db.objects.objects_id==objects_id)&(db.objects.auth_group==id)
								q = (db.objects.tablename==objects.tablename)&(db.objects.table_id==objects.table_id)&(db.objects.auth_group==id)
								if db(q).count()==0:
									db.objects.insert(tablename=objects.tablename,table_id=objects.table_id,objects_id=objects_id,auth_group=id,process=pnext,expired_on=None,ocomment=ocomment)
								else:
									db(q).update(process=pnext,ocomment=ocomment)
							log.insert(objects=objects_id,process=pnext,auth_group=id)
							i+=1				
				result = ""
				link_update = self.settings.get("link_update")
				if link_update:
					vars = current.request.vars
					vars["objects"] = objects_ids
					result = self.load(link_update,args=current.request.args,vars=vars)
				if len(objects_ids) < nb: result = SPAN(result,BR(),T("Chỉ có %(end)s/%(start)s dữ liệu được thực hiện!"%dict(start=nb,end=len(objects_ids))))	
				script = SCRIPT('''$('#button_submit').click(function () {window.location.replace("%s");})'''%URL(r=current.request,c=self.c,f="explorer.html",args=current.request.args[:TABLENAME],vars=self.vars))	
				button = INPUT(_type='button',_value=T('Close'),_id='button_submit',_class="btn btn-default")
				content = DIV(script,H4(T("Cập nhật thành công")),result,button)
				current.cache.ram.clear(None)
		except Exception, e:
			print "process_group:",e
			content = DIV(H4(e),button)
		content = self.bootrapmodal("",content,footer="")
		return content
		
	def load(self,url,args,vars,removetag=False):
		from plugin_app import remove_htmltag
		tmp = url.split('/')
		if len(tmp)>1: c, f = tmp[0], tmp[1]
		else: c, f = 'plugin_process', tmp[0]
		div = LOAD(r=current.request,c=c,f=f,args=args,vars=vars,ajax=False)
		if removetag: div = remove_htmltag(str(div))
		return div
		
	def get_url(self,url,args,vars):
		tmp = url.split('/')
		if len(tmp)>1: c, f = tmp[0], tmp[1]
		else: c, f = 'plugin_process', tmp[0]
		return URL(r=current.request,c=c,f=f,args=args,vars=vars,extension='html')
		
	def status(self):
		T = current.T
		request = current.request
		db = self.db
		auth = self.auth
		tablename = self.tablename
		table_id = self.table_id
		process = db.process		
		log = self.define_process_log()
				
		content = DIV(_id='process_status')
		#rows = db((db.objects.tablename==tablename)&(db.objects.table_id==table_id)&(db.objects.auth_group==self.auth_group)).select()
		#content.append(rows)
		
		rs = db(db.procedures.folder.contains(self.folder_name)&db.procedures.auth_group.contains(self.auth_group)).select()
		for r in rs:
			rows = db(db.process.procedures==r.id).select(orderby=db.process.display_order)
			procedure = None
			for row in rows:
				objects = db((db.objects.tablename==tablename)&(db.objects.table_id==table_id)&(db.objects.process==row.id)).select()
				if len(objects)>0:
					ul = UL()
					for o in objects: ul.append(LI(o.auth_group.role))		
					tmp = DIV(H5(row.name),ul)
					if not procedure: procedure = DIV()
					procedure.append(tmp)
			if procedure: 
				content.append(H4(T('Procedure'),' ',r.name))
				content.append(procedure)
		return content

	def get_query(self,process=None,search=True):
		auth = self.auth
		request = current.request
		objects = self.define_objects()
		if self.folder_id:
			cms = self.cms
			db = cms.db
			folders = cms.get_folders(self.folder_id)
			query = objects.folder.belongs(folders)&(objects.tablename==self.tablename)&(objects.table_id==self.table.id)
			if self.query: query &= self.query
			
			tables = [self.tablename]				
			if search:			
				qtable = None
				vsearch = current.request.vars.get(SEARCHPREFIX+'key')			
				for table in tables:
					q = None
					t = cms.define_table(table)	
					for field in t.fields:	
						v = current.request.vars.get(SEARCHPREFIX+field,"0")
						if v!="0": 
							if t[field].type.startswith("list:reference")|(t[field].type in ["text","string"]): q=(q&t[field].contains(v)) if q else t[field].contains(v)
							elif t[field].type.startswith("reference"): q=q&(t[field]==v) if q else (t[field]==v)			
					if vsearch:
						for field in t.fields:
							if t[field].type in ["string","text",'list:string']:
								if q: q = q|t[field].contains(vsearch)
								else: q = t[field].contains(vsearch)
					if q: 
						rows = cms.db(q).select(t.id,distinct=True)
						table_ids = [row.id for row in rows]
						q = objects.table_id.belongs(table_ids)
						qtable = qtable|q if qtable else q
				if qtable: query &=qtable
							
			if request.vars.query:
				for table in tables: cms.define_table(table)
				try:
					rows = db(eval(request.vars.query)).select()
					table_ids = [row.id for row in rows]
					query &= objects.table_id.belongs(table_ids)
				except Exception, e:
					print e
					pass
		else:
			query = (objects.id>0)

		query &= objects.auth_group.belongs(auth.auth_groups())
		query &=((objects.table_id!=None)|(objects.created_by==auth.user_id))

		if not process: 
			process = self.get_id('process',self.process_name)
			if process == 0: process = None
		if process:
			if not isinstance(process,list): process=[process]
			tmp = None
			for p in process: 
				if (p == '0')|(p=='None'): p = None
				tmp = tmp|(objects.process==p) if tmp else (objects.process==p)
			query&=(tmp)
			
		return query

	def is_read(self,objects,insert=False):
		if self.db((self.db.isread.objects==objects)&(self.db.isread.created_by==self.auth.user_id)).count()==0: 
			if insert: self.db.isread.insert(objects=objects)
			else: return False
		return True
	
	def count_read(self,process):
		db = self.db
		query = self.get_query(process)
		isread = self.define_isread()	
		query &= (isread.objects==db.objects.id)&(isread.created_by==self.auth.user_id)
		return db(query).count(db.objects.id)

	def get_objects_ids(self):
		objects_ids = []
		if current.request.vars.objects: 
			objects_ids = current.request.vars.objects
			if not isinstance(objects_ids,list): objects_ids = [objects_ids]
		elif self.objects_id: 
			objects_ids = [self.objects_id]
		objects_ids = [int(id) for id in objects_ids]
		return objects_ids

	def get_tables(self,setting):
		from plugin_cms import get_setting
		tables = get_setting(setting,key='TABLES')
		if not tables:
			row = self.db(self.db.procedures.name==self.procedure_name).select().first()
			setting = self.cms.db.folder(row.folder_parent).setting if self.cms.db.folder(row.folder_parent) else ""
			tables = get_setting(setting,'TABLES',[])
		if isinstance(tables,str): tables = [tables]
		return tables
		
	def bootrapmodal(self,header,body,footer=None,ajax=None):	
		if not footer:
			if ajax:
				footer = '''
<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
<button type="button" class="btn btn-primary" onclick="%s">Submit</button>'''%ajax
		content = '''
<div class="modal-dialog">
	<div class="modal-content">
		<div class="modal-header">
			<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
			%s
		</div>
		<div class="modal-body">
			%s
		</div>
		<div class="modal-footer">
			%s
		</div>
	</div>
</div>'''%(header,body,footer)
		return XML(content)	
	
	
class ProcessCms(Process):
		

	def select_reference(self,field,multiple=False,keyname=SEARCHPREFIX):
		db = self.db
		auth = self.auth
		if field.type.find("reference")==-1: return ""
		table = field.type.split(" ")[1]
		f = db[table].fields[1]
		if "label" in db[table].fields: 
			orderby = db[table].label
			f = "label"
		elif "name" in db[table].fields: 
			orderby = db[table].name
			f = "name"
		else:
			orderby = db[table].id
		if "display_order" in db[table].fields: 
			orderby = db[table].display_order
		rows = db(db[table]).select(orderby=orderby)
		keyname = keyname+field.name
		value = current.request.vars.get(keyname,"0")
		ops = [OPTION("---",current.T("Select %s"%table),"---", _value ="0", _selected=True)]
		from plugin_app import select_option
		ops += select_option(db,auth,table,selected=[int(value)],field=f)
		_class='select_reference form-control select' if "parent" in db[table].fields else 'js-example-basic-multiple'
		widget = SELECT(ops,_name=keyname,_class=_class,_id="%s_%s"%(table,field.name),_multiple=multiple)
		return widget
		
	def select_year(self):
		if not self.year_field: return ""
		db = self.db
		auth = self.auth
		keyname = FIELDPREFIX+self.year_field
		import datetime
		year = datetime.datetime.now().year
		ops = [OPTION("",_value=URL(r=current.request,c=self.c,f="explorer",args=current.request.args[:TABLENAME+1]))]
		ops += [OPTION(year-i,_selected=(str(year-i)==str(self.year_value)),_value=URL(r=current.request,c=self.c,f="explorer",args=current.request.args[:TABLENAME+1],vars={keyname:year-i})) for i in range(5)]
		v = "2011-2015"
		ops += [OPTION(v,_selected=(v==self.year_value),_value=URL(r=current.request,c=self.c,f="explorer",args=current.request.args[:TABLENAME+1],vars={keyname:v}))]
		v = "2006-2010"
		ops += [OPTION(v,_selected=(v==self.year_value),_value=URL(r=current.request,c=self.c,f="explorer",args=current.request.args[:TABLENAME+1],vars={keyname:v}))]
		v = "2001-2005"
		ops += [OPTION(v,_selected=(v==self.year_value),_value=URL(r=current.request,c=self.c,f="explorer",args=current.request.args[:TABLENAME+1],vars={keyname:v}))]
		widget = SELECT(ops,_name=keyname,_class='form-control', _onchange="this.options[this.selectedIndex].value && (window.location = this.options[this.selectedIndex].value);")
		return widget
		
	def get_page(self):	
		try: 
			page = int(current.request.args(PAGE).split('.')[0])
		except: 
			page = 1
		return page
		
	def get_length(self):
		try: 
			return int(self.settings.get("length",10))
		except: 
			return 10 
		
	def get_rows(self,process=None,page=None,length=None,orderby=None):
		db = self.db
		query = self.get_query(process)	
		if not page: page = self.get_page()
		if not length: length = self.get_length()
		if not orderby: orderby = ~db.objects.id		
		limit = None
		count = db(query).count(db.objects.id)
		if length>0: 
			if count<(page-1)*length: limit = (0,length)
			else: limit = ((page-1)*length,page*length)
		#rows = db(query).select(orderby=orderby,limitby=limit,distinct=True,cache=(current.cache.ram,300),cacheable=True)
		rows = db(query).select(orderby=orderby,limitby=limit,distinct=True)	
		return rows,count

	def search(self):
		if not self.tablename: return ""
		if self.table_id: return ""
		request = current.request
		div = DIV(_class="navbar-form navbar-right",_id='process_search')
		
		for field in self.table.fields:
			if self.settings.get("%s__search_on"%field):
				div.append(SPAN(self.select_reference(self.table[field])))			
			
		keyname = SEARCHPREFIX+'key'
		div.append(INPUT(_type='text',_class='form-control string',_name=keyname,_placeholder="Từ khóa...",_value=request.vars.get(keyname,"")))
		div.append(INPUT(_type="submit",_value='Tìm kiếm',_class='btn btn-success'))
		div = FORM(div)
		return div
		
	def breadcrumb(self):
		request = current.request
		return LOAD(r=request,c=self.c,f="breadcrumb",args=request.args,vars=self.vars,ajax=False)
		
	def explorer(self):	
		div = DIV(_class='panel explorer process',_id='content')
		div.append(DIV(self.filter(),_class='panel-heading'))
		div.append(DIV(DIV(self.toolbars(),self.search(),_id='toolbars_search'),DIV(DIV(self.read()) if self.objects_id else self.view(self.settings)),_class='panel-body'))
		div = SPAN(self.breadcrumb(),div)
		return div
		
	def field_format(self,value,fname,ftype,fformat="",short=True):	
		try:
			if not value: return ""
			request = current.request
			tablename = self.tablename
			if fname=='folder':
				value = current.T(self.cms.db.folder(value).label)
			elif ftype.startswith('reference'):
				ref = ftype[10:]
				if "label" in self.db[ref].fields: value = self.db[ref](value).label
				elif "name" in self.db[ref].fields: value = self.db[ref](value).name 
				elif "role" in self.db[ref].fields: value = self.db[ref](value).role 
				elif ref == "auth_user": value = "%s %s"%(self.db[ref](value).last_name,self.db[ref](value).first_name) 
			elif ftype.startswith('list:reference'):
				ref = ftype[15:]
				if ref == "auth_user": 
					value = "; ".join("%s %s"%(self.db[ref](id).last_name,self.db[ref](id).first_name) for id in (value or []))
				else:
					name = self.db[ref].fields[1]
					if "label" in self.db[ref].fields: name = 'label'
					elif "name" in self.db[ref].fields: name = 'name' 
					elif "role" in self.db[ref].fields: name = 'role' 
					value = "; ".join(self.db[ref](id)[name] for id in (value or []))
			elif ftype=="upload":	
				
				from plugin_config import Configsite
				site_name = Configsite().site_name
				if value[0:7] == 'http://':
					pass
				elif os.path.exists(request.folder + '/static/site/%s/uploads/%s/%s'%(site_name,tablename,value) ):
					value='http://'+request.env.http_host +'/'+request.application+'/static/site/'+ site_name +'/uploads/'+tablename+'/'+ value
					
				elif os.path.exists(request.folder + '/static/site/%s/uploads/ckeditor/%s'%(site_name,value) ):
					value='http://'+request.env.http_host +'/'+request.application+'/static/site/'+ site_name +'/uploads/ckeditor/'+ value
					
				elif os.path.exists(request.folder+'/static/uploads/images_download/'+ value):
					value='http://'+request.env.http_host+'/'+request.application+'/static/uploads/images_download/'+ value
				else:
					value='http://'+request.env.http_host+'/'+request.application+'/static/images/img_defautl.jpg'
				
				value = IMG(_src=value)	
			elif self.settings.get("%s__length"%fname):
				if short: value = get_short_string(value,int(self.settings.get("%s__length"%fname)))
			elif ftype=="text": 
				value = XML(value)
			elif fformat:
				if ftype in ['integer','double']:
						value = fformat.format(value)
						value = value.replace(",","|")
						value = value.replace(".",",")
						value = value.replace("|",".")
				elif ftype in ['date','datetime','time']: value = value.strftime(fformat)
			elif ftype in ['date']: value = value.strftime("%d/%m/%Y")
				
		except Exception, e:
			print "field_format: ", e, fname
		return value or ""
		
	def view(self,settings={}):
		request = current.request
		T = current.T
		
		for key in self.settings.keys():
			if key not in settings.keys(): settings[key] = self.settings[key]
		
		orderby = request.vars.orderby or settings.get("orderby","~id")
		if isinstance(orderby,str):
			if orderby.startswith("~"):
				orderby = ~self.table[orderby[1:]]
			else:
				orderby = self.table[orderby]
		length = int(settings.get("length") or 10)
		rows, count = self.get_rows(length=length,orderby=orderby)
			
		content = TABLE(_id='process_id',_class='table table-striped defview table-hover')
		thead = THEAD()
		tr = TR()
		
		if settings.get("check_on"): tr.append(TH(INPUT(_type='checkbox',_name='check_all',_id='check_all',_onclick="CheckAll();"),_class='stt',_style="width: 20px;text-align: center;"))
		if settings.get("index_on"): tr.append(TH(T("TT"),_style="width: 20px;text-align: center;"))
		if settings.get("edit_on"): tr.append(TH(A(I(_class="fa fa-edit fa-fw"),_href="#",_title=T("Chỉnh sửa dữ liệu")),_style="width: 20px;text-align: center;"))
		if settings.get("read_on"): tr.append(TH(A(I(_class="fa fa-folder-open-o fa-fw"),_href="#",_title=T("Xem dữ liệu")),_style="width: 20px;text-align: center;"))
		if settings.get("delete_on"): tr.append(TH(A(I(_class="fa fa-trash-o fa-fw"),_href="#",_title=T("Xóa dữ liệu")),_style="width: 20px;text-align: center;"))
		
		for btn in self.buttons: tr.append(TH(I(_class=btn[1]),_style="width: 20px;text-align: center;"))
		
		from bootrap import Modals
		vars = {}
		for key in self.vars.keys(): vars[key] = self.vars[key]	
		vsearch = request.vars.get(SEARCHPREFIX+'key')
		if vsearch: vars[SEARCHPREFIX+"key"] = vsearch
		for field in self.table.fields:	
			v = request.vars.get(SEARCHPREFIX+field)
			if v: vars[SEARCHPREFIX+field] = v
	
		tfield = self.cms.define_tablefield()
		fields = self.cms.db((tfield.dtable==self.cms.db.dtable.id)&(self.db.dtable.name==self.tablename)).select(tfield.ALL,orderby=tfield.display_order)
		for row in fields:
			field = row.dfield.name
			if settings.get("%s__show_on_table"%field):
				if request.vars.orderby == field:
					vars["orderby"] = "~" + field
					title = " ▲"
				elif request.vars.orderby == "~" + field:
					vars["orderby"] = field
					title = " ▼"
				else:
					vars["orderby"] = field	
					title = ""
				if self.table[field].type.startswith("reference")|self.table[field].type.startswith("list:reference"): title = ""
				title = A(T(settings.get("%s__dlabel"%field,field)),title,_href=URL(r=request,args=request.args,vars=vars))
				tr.append(TH(title))
				
		thead.append(tr)
		content.append(thead)
		page = self.get_page()
		i = (page-1)*length
		self.define_isread()
		
		for row in rows:
			dcontent = self.table(row.objects.table_id)
			objects = row.objects
			if dcontent:
				args = request.args[:FOLDER]+[objects.foldername,objects.tablename,objects.id]
				css = 'line_%s is_read_%s'%(i%2,self.is_read(objects.id))
				if self.settings.get("link_css"): css = css+" "+self.load(self.settings.get("link_css"),args=request.args,vars=dict(table_id=dcontent.id,objects=objects.id),removetag=True)
				tr = TR(_class=css)
				if settings.get("check_on"): tr.append(TD(INPUT(_type='checkbox',_name='objects',_value=objects.id,_class="boolean objects"),_class='stt'))
				if settings.get("index_on"): tr.append(TD(i+1,_class='stt',_style="text-align: center;"))
				if settings.get("edit_on"): tr.append(TD(A(I(_class="fa fa-edit fa-fw"),_href=URL(r=request,c=self.c,f="edit",args=args),_title="%s %s"%(T("Nhấn để chỉnh sửa dòng"),i+1))))
				if settings.get("read_on"): tr.append(TD(Modals(caption = (I(_class="fa fa-folder-open-o fa-fw")),source=URL(r=request,c=self.c,f="read",args=args))))
				if settings.get("delete_on"): tr.append(TD(A(I(_class="fa fa-trash-o fa-fw"),_href=URL(r=request,c=self.c,f="delete",args=args))))
				for btn in self.buttons: tr.append(TD(Modals(caption = I(_class=btn[1]),source=URL(r=request,c=self.c,f=btn[0],args=[self.tablename,objects.id]))))			
				for field in fields:
					if settings.get("%s__show_on_table"%field.dfield.name):
						fformat = settings.get("%s__fformat"%field.dfield.name)
						# if self.table[field.dfield.name].represent:
							# v = self.table[field.dfield.name].represent(dcontent[field.dfield.name],dcontent)
						# else: 
						v = self.field_format(dcontent[field.dfield.name],field.dfield.name,field.dfield.ftype,fformat)
						if field.link_on_table: v = A(v,_href=URL(r=request,args=args,vars=self.vars),_title=T("Nhấn để xem chi tiết"))
						tr.append(TD(v))
				content.append(tr)
				i += 1
		nb = len(rows)
		content = DIV(DIV(H5("Hiển thị %s/%s dữ liệu." %(nb,count)),_style="float:right;text-align:right;width:100%;"),content,_id="explorer_view")		
		if nb>0:
			if nb<count: 
				content = DIV(content,DIV(self.pagination(count,length,orderby=request.vars.orderby or settings.get("orderby",None)),_class='clearfix'))
		return content		
		
	def read(self,checkid=True):
		T = current.T
		if not self.objects_id: 
			return ''
		
		cmsmodel = self.cms
		objects = self.define_objects()
		objects = objects(self.objects_id)
		tablename = objects.tablename
		table = cmsmodel.define_table(objects.tablename)
		row = table(objects.table_id)
		
		self.define_isread()
		self.is_read(self.objects_id,True)
		
		if os.path.isfile('%s/views/plugin_process/read/%s.html'%(current.request.folder,tablename)):
			context = dict(request=current.request,table=table,dcontent=row,objects=objects,T=T)
			oid = str(INPUT(_type='checkbox',_name='objects',_value=self.objects_id,_checked=True,_style="display:none",_class="objects"))
			return XML(oid+current.response.render('plugin_process/read/%s.html'%tablename, context))
				
		content = TABLE(_id=tablename,_class='table table-striped defview')

		dtable = cmsmodel.define_dtable()
		tfield = self.cms.define_tablefield()
		fields = self.cms.db((tfield.dtable==dtable.id)&(dtable.name==tablename)).select(tfield.ALL,orderby=tfield.display_order)
		
		for field in fields:
			if field.readable:
				fname = field.dfield.name
				data = self.field_format(row[fname],fname,field.dfield.ftype,fformat=field.fformat or "",short=False)
				content.append(TR(TD(B(current.T(field.dlabel)),_class='lablel'),TD(data),_class=str(fname)))

		row = cmsmodel.db(dtable.name==tablename).select().first()
		if tablename =='don_hang':
			from plugin_app import number_format
			
			item_don_hang = cmsmodel.define_table('item_don_hang')
			table_item = TABLE(_class='table')
			items = cmsmodel.db(item_don_hang.don_hang==objects.table_id).select()
			if len(items)>0:
				tong_tien= 0
				table_item.append(TR(TH('Sản phẩm'),TH('Số lượng'),TH('Đơn giá'),TH('Thành tiền')))
				for item in items:
					tong_tien += int(item.price)* int(item.r_number)
					table_item.append(TR(TD(item.product.name),TD(item.r_number),TD(number_format(item.price),' VNĐ'),TD(B(number_format(int(item.price)* int(item.r_number))),' VNĐ')))
				
			content.append(TR(TD(B(current.T('Chi tiết đơn hàng')),_class='lablel'),TD(table_item,H4(B('Tổng tiền cần thanh toán:  ',number_format(tong_tien),' VNĐ',_class='pull-right')))))
		if tablename =='phongthuy_don_hang':
			from plugin_app import number_format
			
			item_don_hang = cmsmodel.define_table('phongthuy_item_don_hang')
			table_item = TABLE(_class='table')
			items = cmsmodel.db(item_don_hang.phongthuy_don_hang==objects.table_id).select()
			if len(items)>0:
				tong_tien= 0
				table_item.append(TR(TH('Sản phẩm'),TH('Số lượng'),TH('Đơn giá'),TH('Thành tiền')))
				for item in items:
					tong_tien += int(item.price)* int(item.r_number)
					table_item.append(TR(TD(item.product.name),TD(item.r_number),TD(number_format(item.price),' VNĐ'),TD(B(number_format(int(item.price)* int(item.r_number))),' VNĐ')))
				
			content.append(TR(TD(B(current.T('Chi tiết đơn hàng')),_class='lablel'),TD(table_item,H4(B('Tổng tiền cần thanh toán:  ',number_format(tong_tien),' VNĐ',_class='pull-right')))))
		if row:
			if objects.ocomment:
				content.append(TR(TD(B(current.T('Process comment')),_class='lablel'),TD(XML(objects.ocomment))))
			if row.attachment:
				from plugin_upload import FileUpload
				attach = FileUpload(db=cmsmodel.db,tablename=tablename,table_id=objects.table_id,upload_id=0)
				content.append(TR(TD(B(current.T('Đính kèm')),_class='lablel'),TD(attach.view_publish())))
			if row.is_comment:
				from plugin_comment import Comment
				comment = Comment(db=self.db,auth=self.auth,tablename=tablename,table_id=objects.table_id,objects_id=objects.id,process=self.process_id)
				content.append(TR(TD(B(current.T('Đánh giá')),_class='lablel'),TD(comment.view())))
		if checkid:
			content = DIV(DIV(INPUT(_type='checkbox',_name='objects',_value=self.objects_id,_checked=True,_style="display:none",_class="objects"),_id='explorer_view'),content)
		return content
		
	def view_lock(self,tablename,table_id):
		T = current.T
		pl = self.define_process_lock()
		locks = self.db((pl.tablename==tablename)&(pl.table_id==table_id)).select()
		table = TABLE(_class="table",_id='view_lock')
		table.append(TR(TH(T('Sự kiện')),TH(T('Lý do')),TH(T('Người thực hiện')),TH(T('Thời gian thực hiện'))))
		for lk in locks:
			user = self.db.auth_user(lk.lock_by)
			lock_by =  str(user.first_name) + ' ' + str(user.last_name)
			tr = TR(TD(T('Check Out')),TD(lk.comment_lock),TD( lock_by,_rowspan="2",_class='lock_by'),TD(lk.lock_on))
			table.append(tr)
			tr = TR(TD(T('Check In')),TD(lk.comment_unlock),TD(lk.unlock_on))
			table.append(tr)
		return table
		
	def pagination(self,count,length, orderby=None):
		T = current.T
		request = current.request
		args = request.args
		if len(args) < PAGE: return ''
		elif len(args) == PAGE: args.append('1.html')
		page = self.get_page()
		if length>0:
			tmp = int(count/length)
			if count > tmp*length: pagecount = tmp+1
			else: pagecount = tmp
			
		vars = {}
		for key in self.vars.keys(): vars[key] = self.vars[key]	
		vsearch = request.vars.get(SEARCHPREFIX+'key')
		if vsearch: vars[SEARCHPREFIX+"key"] = vsearch
		for field in self.table.fields:	
			v = request.vars.get(SEARCHPREFIX+field)
			if v: vars[SEARCHPREFIX+field] = v
		if orderby: vars["orderby"] = orderby	
		elif request.vars.orderby: vars["orderby"] = request.vars.orderby	
		content = DIV(_id='page')
		ul = UL(_class='page-ul pagination')
		(p1, m1) = (page - 5,'...') if page > 5 else (1, '')
		(p2, m2) = (page + 5,'...') if page + 5 < pagecount else (pagecount+1, '')
		if (p2 < 11) & (pagecount >10): p2 = 11
		if m1=='...':
			args[PAGE]='1.html'
			url = URL(r=request,args=args,vars=vars)
			ul.append(LI(A(T('First'),'  ',_href=url)))
			ul.append(LI(A(m1)))
		for x in xrange(p1,p2):
			args[PAGE]='%s.html'%x
			url = URL(r=request,args=args,vars=vars)
			ul.append(LI(A(x,'  ',_href=url),_class='active' if x == page else ''))
		if m2=='...':
			ul.append(LI(A(m2)))
			args[PAGE]='%s.html'%pagecount
			url = URL(r=request,args=args,vars=vars)
			ul.append(LI(A(T('End'),_href=url)))
		content.append(ul)
		return content			
		
	def menu(self,folder,deep=1,**attr):
		# if deep>attr.get('maxdeep',1): return ""
		table = self.cms.define_folder()
		rows = self.cms.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		args = [arg for arg in current.request.args[:FOLDER+1]]
		while len(args)<=FOLDER: args.append(self.process_name)
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		folders = attr.get('folders',[])
		c = attr.get('c',self.c)
		f = attr.get('f',"explorer")
		add = None
		a_class = attr.get('a_class_deep') + str(deep) if attr.get('a_class_deep') else attr.get('a_class_%s'%deep,attr.get('a_class',""))
		a_id = attr.get('a_id_deep') + str(deep) if attr.get('a_id_deep') else attr.get('a_id_%s'%deep,attr.get('a_id',""))
		li_class = attr.get('li_class_deep') + str(deep) if attr.get('li_class_deep') else attr.get('li_class_%s'%deep,attr.get('li_class',""))
		li_id = attr.get('li_id_deep') + str(deep) if attr.get('li_id_deep') else attr.get('li_id_%s'%deep,attr.get('li_id',""))
		icon_class = attr.get('icon_class_deep') + str(deep) if attr.get('icon_class_deep') else attr.get('icon_class_%s'%deep,attr.get('icon_class',""))
		icon = I(_class="fa %s fa-fw fa-2x"%icon_class) if icon_class else ""
		for row in rows:
			child = self.menu(row.id,deep+1,**attr)
			args[FOLDER] = row.name
			url = URL(r=current.request,c=c,f=f,args=args,vars=self.vars)
			link = A(icon, current.T(row.label or row.name),_href=url,_class=a_class,_id=a_id)
			if not (((len(folders)>0)&(row.id not in folders))|(not (self.auth.has_permission("explorer", "folder", row.id)|self.auth.has_membership(role='admin')))):
				link = A(icon, current.T(row.label or row.name),_href=url,_class=a_class,_id=a_id,_title=row.description)
				content.append(LI(link,child,_class=li_class,_id=li_id))
				add = True
			elif child != "": 
				link = A(icon, current.T(row.label or row.name),_href="#",_class="inactive " + a_class,_id=a_id)
				content.append(LI(link,child,_class=li_class,_id=li_id))
				add = True
		if not add: return ''
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
	def menu_breadcrumb(self,year=True):
		procedure_id = self.get_id('procedures',self.procedure_name)
		if procedure_id:
			p = self.define_procedures()
			row = p(procedure_id)
			parent = row.folder_parent
			cms = self.cms
			folder_id = self.folder_id
			if cms.db.folder(folder_id):
				parents = [folder_id]
				while parent != folder_id:
					folder_id = cms.db.folder(folder_id).parent
					if not folder_id: break
					parents = [folder_id] + parents
				menu = OL(_class="breadcrumb")
				if year:
					if self.year_field:	
						menu = OL(LI(DIV(SPAN(current.T("Năm làm việc"),_class='input-group-addon'),self.select_year(),_class="year-select input-group")),_class="breadcrumb")
				i = 1
				for id in parents:
					folder = cms.db.folder(id)
					icon = I(_class="fa fa-home fa-fw") if i == 1 else I(_class="fa fa-folder-open fa-fw")
					li = LI(A(icon,folder.label,_href=URL(r=current.request,c=self.c,f="explorer.html",args=[self.procedure_name,self.process_name,folder.name]+[self.tablename] if self.tablename else [],vars=self.vars)))
					menu.append(li)
					i +=1
				if row.is_create: menu.append(LI(self.create_news(parents[-1]),_class='btn-group'))		
				return menu
		return ''

	def menu_select(self,year=True,selects=[]):
		procedure_id = self.get_id('procedures',self.procedure_name)
		if procedure_id:
			p = self.define_procedures()
			row = p(procedure_id)
			parent = row.folder_parent
			self.cms.define_folder()
			pname = self.cms.db.folder(parent).name
			menu = OL(_class="breadcrumb")
			if year:
				if self.year_field:	
					vars = {}
					for key in self.vars.keys():
						if key != FIELDPREFIX+self.year_field: vars[key] = self.vars[key]
					url = URL(r=current.request,f="explorer",args=current.request.args[:TABLENAME],vars=vars)
					menu = OL(LI(DIV(SPAN(A(current.T("Năm làm việc"),_href=url),_class='input-group-addon'),self.select_year(),_class="year-select input-group")),_class="breadcrumb")
			from plugin_app import select_option		
			v = "this.options[this.selectedIndex].value && (window.location = '%s'.replace('folder_name',this.options[this.selectedIndex].value));"%URL(r=current.request,f="explorer",args=current.request.args[:FOLDER]+['folder_name'],vars=self.vars)
			ops = [OPTION(current.T("---Tất cả---"),_value=pname,_selected=(self.folder_name==pname))]
			ops += select_option(self.db,self.auth,'folder',id=parent,selected=[self.folder_name],field='label',field_id="name")
			widget = SELECT(ops,_name="project_folder",_id="project_folder",_class="generic-widget form-control",_onchange=v)
			url = URL(r=current.request,f="explorer",args=current.request.args[:FOLDER]+[pname],vars=self.vars)
			menu.append(LI(DIV(SPAN(A(current.T("Folder"),_href=url),_class='input-group-addon'),widget,_class="folder-select input-group")))
			for select in selects:
				menu.append(LI(select))
			if row.is_create: menu.append(LI(self.create_news(self.folder_id),_class='btn-group li_breadcrumb'))		
			return menu
		return ''
		
	def create_news(self,folder_id):
		cms = self.cms
		role = 'create_'+self.procedure_name
		if self.auth.has_membership(role='admin')|self.auth.has_permission("create",'folder',folder_id)|self.auth.has_permission("edit",'folder',folder_id)|self.auth.has_permission(role,'folder',folder_id):
			div = DIV(_class="btn-group")
			table = self.tablename
			div.append(A(I(_class="fa fa-edit fa-fw"),current.T('New '+table) ,_class="btn btn-danger "+table,_href=URL(r=current.request,c=self.c,f='edit.html',args=[self.procedure_name,"New",self.folder_name,table],vars=self.vars)))
		else:
			div = ""
		return div
		
	
class ProcessCrud(Process):
	def __init__(self,**attr):
		self.init(**attr)
		request = current.request
		
		self.tablename = None
		if (request.function=="processcrud"):
			procedures = self.define_procedures()
			process = self.define_process()
			p = None
			row = None
			if request.args(0):		
				p = process(request.args(0))
				if p: row = procedures(p.procedures)
			elif request.vars.procedures:	
				row = procedures(request.vars.procedures)
			if row: 
				self.tablename = row.tablename
				
	def procedures(self):
		from plugin_app import widget_tree, treeview

		def widget_folder(field, value):
			from plugin_app import select_option
			self.cms.define_folder()
			widget = SELECT(['']+select_option(self.db,self.auth,'folder',selected=[value],field='label'),_name=field.name,_id=field._tablename+'_'+field.name,requires=field.requires,_class="generic-widget form-control")
			return widget	
		
		def widget_folders(field, value):
			from plugin_app import treeview
			cms = self.cms
			cms.define_folder()
			db = cms.db
			auth = self.auth
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
		
		def widget_auth(field, value):
			db = self.db
			options = ['']
			rows = db(db.auth_group.atype=='auth').select(orderby=db.auth_group.role)
			for row in rows:
				options.append(OPTION(row.role,_value=row.id,_selected=(row.id==value)))
			return SELECT(options,_name=field.name,_id=field._tablename+'_'+field.name,_class="generic-widget form-control")
	
		def widget_table(field, value):
			db = self.db
			options = ['']
			dtable = self.cms.define_dtable()
			rows = db(dtable).select(orderby=dtable.display_order)
			for row in rows:
				options.append(OPTION(row.name,_value=row.name,_selected=(row.name==value)))
			ajax = "ajax('%s', ['%s'], 'procedures_year_field')"%(URL(r=current.request,f='year_field',args=current.request.args,vars=current.request.vars),field.name)
			return SELECT(options,_name=field.name,_id=field._tablename+'_'+field.name,_onchange=ajax,_class="generic-widget form-control")
	
		def widget_controller(field, value):
			files = []
			for root, dirs, files in os.walk(current.request.folder+'/controllers'):
				pass
			op = []	
			if not value: value = "plugin_process"
			for file in files:	
				if file.endswith(".py"):
					file = file[:-3]
					op.append(OPTION(file,_value=file,_selected=(value==file)))
			widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name,_class="generic-widget form-control")
			return widget

		def widget_year_field(field, value):
			widget = DIV(INPUT(_name=field.name,_value=value or "",_class="string form-control"),_id="procedures_year_field")
			return widget
			
		def widget_setting(field, value):
			v = dict()
			if value: v = eval(value)
			widget = DIV(TEXTAREA(_name="setting",_style="display:none;"),_class="col-sm-offset-3 col-sm-9")
			ul = UL(_class="list-group")
			for key in ["menu_icon","menu_wrapper"]:
				ul.append(LI(SPAN(current.T("Procedure %s"%key)),SPAN(INPUT(_name="setting_"+key,_value=v.get(key,""),_class="string form-control")),_class="list-group-item"))
			widget.append(ul)
			return widget
			
		table = self.define_procedures()
		table.user_group.widget = widget_auth
		table.auth_group.widget = widget_tree
		table.folder_parent.widget = widget_folder
		table.tablename.widget = widget_table
		table.year_field.widget = widget_year_field
		table.controller.widget = widget_controller
		table.setting.widget = widget_setting
		if not current.request.args(0):
			table.name.readable = False
			table.name.writable = False
			table.name.default = "procedurename"			
		return table
		
		
			
	def process(self):	
		from plugin_app import widget_tree, treeview
		db = self.db
		auth = self.auth
		
		def widget_auth(field, value):
			widget = treeview(db,auth,'auth_group',parent=None,tree=field.name,field='role',key=field.name,checkbox='checkbox',selected=value,orderby=db.auth_group.display_order)
			return widget
			
		def widget_procedures(field, value):
			rows = db(db.procedures.id>0).select()
			if not value:
				pass
				#if (current.request.args(1)=='process.procedures')&current.request.args(2).isdigit():
				#	value = int(current.request.args(2))
			else:
				value=int(value)
			op = [OPTION(current.T(row.label),_value=row.id,_selected=(row.id == value)) for row in rows]
			ajax = "ajax('%s',['%s'],'widget_access')"%(URL(r=current.request,c='plugin_process',f='widget_access',args=current.request.args,vars=current.request.vars),field.name)
			widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name,_onchange=ajax,_class="generic-widget form-control")
			return widget
			
		def widget_access(field, value):
			from plugin_app import input_option
			query = None
			if value:
				if not isinstance(value,list): value = [int(value)]
			if current.request.args(1)=='process.procedures':
				query = (db.process.procedures==current.request.args(2))
			elif current.request.args(0):
				if current.request.args(0).isdigit():
					row = db.process(current.request.args(0))
					query = (db.process.procedures==row.procedures)
			elif current.request.vars.procedures:
				query = (db.process.procedures==current.request.vars.procedures)			
			elif value:
				
				if len(value)>0:
					row = db(db.process.id==value[0]).select().first()
					if row: query = (db.process.procedures==row.procedures)
			else:
				query = (db.process.id>0)
			tmp = input_option('process', type='checkbox', selected=value or [], query=query, keyname=field.name, field="label")
			widget = DIV(tmp, _id='widget_access')
			return widget
			
		def widget_next(field, value):
			rows = db(db.procedures.id>0).select()
			op = [OPTION('')]
			for row in rows:
				rs = db(db.process.procedures==row.id).select()
				for r in rs: op.append(OPTION(row.name+' -> '+r.name,_value=r.id,_selected=(r.id == value)))
			widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name,_class="generic-widget form-control")
			return widget
			
		def widget_setting(field, value):
			v = dict()
			if value: v = eval(value)
			widget = DIV(TEXTAREA(_name="setting",_style="display:none;"),_class="col-sm-offset-3 col-sm-9")
			
			for key in ["update_process_all","parent_check","check_group","edit_toolbar","delete_toolbar","filter_show"]:
				widget.append(DIV(LABEL(INPUT(_type='checkbox',_name="setting_"+key,_checked=(v.get(key)==True),_class="boolean"),current.T(key.capitalize())),_class="checkbox"))
						
			ul = UL(_class="list-group")
			for key in ["link_update","link_verify","link_css","permission","toolbars_icon","filter_icon","filter_label","select_month","length"]:
				ul.append(LI(SPAN(current.T("Process %s"%key)),SPAN(INPUT(_name="setting_"+key,_value=v.get(key,""),_class="string form-control")),_class="list-group-item"))
			widget.append(ul)
					
			columns = ["dlabel","readable","writable","show_on_table","search_on","link_on_table","length","fformat"]		
			t = TABLE(_class='table table-striped defview table-hover')
			th = TR(TH(current.T("Field name")))
			for c in columns:
				th.append(TH(current.T("Field %s"%c)))
			t.append(th)
			tfield = self.cms.define_tablefield()
			rows = self.cms.db((tfield.dtable==self.cms.db.dtable.id)&(self.db.dtable.name==self.tablename)).select(tfield.ALL,orderby=tfield.display_order)
			for row in rows:
				tr = TR(TD(LABEL(row.dfield.name)))
				for c in columns:
					key = "setting_%s__%s"%(row.dfield.name,c)
					val = v.get(key[8:])
					if not val:
						if not v.get("%s__dlabel"%row.dfield.name):
							if c in tfield.fields: val = row[c]
					if c in ["dlabel"]:
						tr.append(TD(INPUT(_type="text",_name=key,_value=val,_class="string form-control")))
					elif c in ["length"]:
						if row.dfield.ftype in ["string","text"]:
							tr.append(TD(INPUT(_type="text",_name=key,_value=val,_class="integer form-control",_width="50px")))
						else: tr.append(TD())
					elif c in ["fformat"]:
						if row.dfield.ftype in ["integer","double","time","date","datetime"]:
							tr.append(TD(INPUT(_type="text",_name=key,_value=val,_class="string form-control")))
						else: tr.append(TD())
					elif c in ["search_on"]:
						if row.dfield.ftype.startswith("reference"):
							tr.append(TD(INPUT(_type="checkbox",_name=key,_checked=val,_class="boolean")))
						else: tr.append(TD())
					else:
						tr.append(TD(INPUT(_type="checkbox",_name=key,_checked=val,_class="boolean")))
				t.append(tr)
			t.append(th)
			widget.append(t)
			
			widget = DIV(widget,_class="form-group",_id="process_setting_row")
			return widget
			
		table = self.define_process()
		table.procedures.widget = widget_procedures
		table.paccess.widget = widget_access
		table.pnext.widget = widget_next
		table.auth_group.widget = widget_auth
		table.view_group.widget = widget_auth
		table.process_group.widget = widget_tree
		table.setting.widget = widget_setting
		if not current.request.args(0):
			table.name.readable = False
			table.name.writable = False
			table.name.default = "processname"	
			table.setting.default="{'check_group':False,'delete_toolbar':True,'edit_toolbar':True}"
		return table

			
		
		