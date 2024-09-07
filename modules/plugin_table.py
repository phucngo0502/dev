# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 04/09/2015
###################################################
from gluon import current, LOAD, redirect, HTTP
from html import *
from plugin_cms import get_setting
import os

PAGE = 1
TABLENAME = 0
TABLEID = 1
SEARCHPREFIX = "search__"
FIELDPREFIX = "field__"


def safe_int(x):
    try:
        return int(x)
    except ValueError:
        return 0


def safe_float(x):
    try:
        return float(x)
    except ValueError:
        return 0


#####################################################################
## DATA MANAGER CLASS
		
class DataTable():
	def __init__(self,**attr):
		self.db = attr.get('db',current.globalenv.get('db'))
		self.auth = attr.get('auth',current.globalenv.get('auth'))
		self.cms = attr.get('cms',current.globalenv.get('cms'))
		self.c = attr.get('c',current.request.controller)
		self.ftoolbars = attr.get('ftoolbars',"toolbars")
		self.ffilter = attr.get('ffilter',"filter")
		self.toolbar = attr.get('toolbar',[])
		self.buttons = attr.get('buttons',[])
		self.tablename = attr.get('tablename',current.request.args(TABLENAME))
		self.table = self.cms.define_table(self.tablename)
		if not self.table: 
			raise HTTP(400, "Bad Request - table name not found!")
		self.id = attr.get('id',current.request.args(TABLEID))
		if self.id:
			if self.id.endswith(".html"): self.id=None
		self.default = attr.get('default',{})
		
		dtable = self.cms.define_dtable()
		row = self.cms.db(dtable.name==self.tablename).select().first()
		self.settings = eval(row.setting)
		for field in dtable.fields:
			if field not in ["id","name","settings","description"]: self.settings[field] = row[field]					
		
		self.query = attr.get('query',(self.table.id>0))
		self.vars = {}
		self.year_field = self.settings.get("year_field",None)
		self.year_value = None
		for field in self.table.fields:
			v = attr.get(field,current.request.vars.get(FIELDPREFIX+field))
			if v: 
				if field==self.year_field:
					self.year_value = v
					tmp = v.split("-")
					if self.table[field].type in ["date","datetime"]:
						if len(tmp)==2:
							self.query &= (self.table[field].year()>=tmp[0])&(self.table[field].year()<=tmp[1])
						else:
							self.year_value = int(v)
							self.query &= (self.table[field].year()==self.year_value)
					elif self.table[field].type =="integer":
						if len(tmp)==2:
							self.query &= (self.table[field]>=tmp[0])&(self.table[field]<=tmp[1])
						else:			
							self.year_value = int(v)
							self.query &= (self.table[field]==self.year_value)
				else:	
					self.query &= (self.table[field]==v)
					self.default[field] = v
				self.vars[FIELDPREFIX+field] = v 
								
		self.args = [self.tablename]
		if self.id: self.args.append(self.id)
		
	def toolbars(self):
		menu = LOAD(r=current.request,c=self.c,f=self.ftoolbars,args=self.args,vars=self.vars,ajax=False)
		for btn in self.toolbar: menu.append(btn)
		return menu

	def filter(self):
		return LOAD(r=current.request,c=self.c,f=self.ffilter,args=self.args,vars=self.vars,ajax=False)
		
	def menu_folder(self,parent=None):
		if "folder" in self.table.fields: 
			parent = parent or self.settings.get("folder")
			menu = self.menu(parent,folders=[],a_class_deep="sf_",icon_class="fa-folder-open",ul_class_1="sf-menu sf-vertical")
			if parent:
				menu = DIV(A(H4(current.T(self.cms.db.folder(parent).label)),_href=URL(r=current.request,f="explorer",args=[self.tablename]),_class="folder-parent"),menu)
		else:	
			menu = UL(_class="list-group sf-menu sf-vertical",_role="menu")
			table = self.cms.define_dtable()
			rows = self.cms.db(table.publish==False).select(orderby=table.display_order)
			for row in rows:
				if self.auth.has_membership(role='admin')|self.auth.has_permission("explorer",'dtable', row.id):
					title=current.T(row.label)
					menu.append(LI(A(I(_class="fa fa-table fa-fw"),title,_href=URL(r=current.request,c="plugin_table",f="explorer",args=[row.name])),_class="active" if self.tablename==row.name else ""))
		return menu	
		
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
		ops = [OPTION(current.T("Select %s"%table), _value ="0", _selected=True)]
		for row in rows:
			ops.append(OPTION("---",row[f], _value=row.id, _selected=(str(row.id) == value)))	
		widget = SELECT(ops,_class='js-example-placeholder-single',_name=keyname,_id="%s_%s"%(table,field.name))
		return widget

	def select_year(self):
		if not self.year_field: return ""
		db = self.db
		auth = self.auth
		keyname = FIELDPREFIX+self.year_field
		import datetime
		year = datetime.datetime.now().year
		folder = current.request.vars.get(FIELDPREFIX+"folder")
		ops = [OPTION("",_value=URL(r=current.request,f="explorer",args=[self.tablename],vars={FIELDPREFIX+'folder':folder} if folder else {}))]
		ops += [OPTION(year-i,_selected=(year-i==self.year_value),_value=URL(r=current.request,f="explorer",args=[self.tablename],vars={keyname:year-i,'folder':folder} if folder else {keyname:year-i})) for i in range(5)]
		v = "2011-2015"
		ops += [OPTION(v,_selected=(v==self.year_value),_value=URL(r=current.request,f="explorer",args=[self.tablename],vars={keyname:v,'folder':folder} if folder else {keyname:v}))]
		v = "2016-2020"
		ops += [OPTION(v,_selected=(v==self.year_value),_value=URL(r=current.request,f="explorer",args=[self.tablename],vars={keyname:v,'folder':folder} if folder else {keyname:v}))]
		widget = SELECT(ops,_name=keyname,_class='form-control', _onchange="this.options[this.selectedIndex].value && (window.location = this.options[this.selectedIndex].value);")
		return widget
			
	def get_query(self,query=None,search=True):
		query = query or self.query
		if search:
			for field in self.table.fields:
				v = current.request.vars.get(SEARCHPREFIX+field,"0")
				if v!="0": 
					if self.table[field].type.startswith("list:reference")|(self.table[field].type in ["text","string"]): query&=self.table[field].contains(v)
					elif self.table[field].type.startswith("reference"): query&=(self.table[field]==v)			
			vsearch = current.request.vars.get(SEARCHPREFIX+'key')			
			q = None
			if vsearch:
				for field in self.table.fields:
					if self.table[field].type in ["string","text",'list:string']:
						if q: q = q|self.table[field].contains(vsearch)
						else: q = self.table[field].contains(vsearch)
			if q: query&=(q)			
		return query
	
	def get_page(self):	
		try: 
			page = int(current.request.args(PAGE).split('.')[0])
		except: 
			page = 1
		return page
		
	def get_length(self):
		try: 
			return int(self.settings.get("length",30))
		except: 
			return 30 
		
	def get_rows(self,page=None,length=None,orderby=None,query=None,search=True):
		db = self.db
		query = self.get_query(query,search)	
		if not page: page = self.get_page()
		if not length: length = self.get_length()
		if not orderby: 
			orderby = ~self.table.id		
			for field in ["display_order","label","name","role","last_name","first_name"]:
				if field in self.table.fields: 
					orderby = self.table[field]
					break
		elif isinstance(orderby,str): 
			if orderby in self.table.fields: orderby = self.table[orderby]
			else:
				try:
					orderby = eval(orderby)
				except Exception, e:
					print e
					pass
		limit = None
		count = db(query).count(self.table.id)
		length = int(length)
		if length>0: 
			if count<(page-1)*length: limit = (0,length)
			else: limit = ((page-1)*length,page*length)
		rows = db(query).select(self.table.ALL,orderby=orderby,limitby=limit,distinct=True)	
		return rows,count
	
	def search(self):
		request = current.request
		div = DIV(_class="navbar-form navbar-right",_id='process_search')
		tfield = self.cms.define_tablefield()
		fields = self.cms.db((tfield.dtable==self.cms.db.dtable.id)&(self.db.dtable.name==self.tablename)).select(tfield.ALL,orderby=tfield.display_order)
		for field in fields:
			if field.search_on:
				div.append(SPAN(self.select_reference(self.table[field.dfield.name])))			
		keyname = SEARCHPREFIX+'key'
		div.append(INPUT(_type='text',_class='form-control string',_name=keyname,_placeholder="Từ khóa...",_value=request.vars.get(keyname,"")))
		div.append(INPUT(_type="submit",_value='Tìm kiếm',_class='btn btn-success'))
		div = FORM(div)
		return div
		
	def explorer(self):	
		div = DIV(_class='panel explorer process',_id='content')
		div.append(DIV(self.filter(),_class='panel-heading'))
		div.append(DIV(DIV(self.toolbars(),self.search(),_id='toolbars_search'),DIV(self.read() if self.id else self.view(settings={})),_class='panel-body'))
		return div
		
	def field_format(self,value,fname,ftype,fformat="",ckeditor=False):	
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
				if value[0:7] == 'http://':
					pass
				elif os.path.exists(request.folder+'/static/uploads/'+tablename+'/'+ value):
					value='http://'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ value
				elif os.path.exists(request.folder+'/static/uploads/ckeditor/'+ value):
					value='http://'+request.env.http_host+'/'+request.application+'/static/uploads/ckeditor/'+ value
				elif os.path.exists(request.folder+'/static/uploads/images_download/'+ value):
					value='http://'+request.env.http_host+'/'+request.application+'/static/uploads/images_download/'+ value
				else:
					value='http://'+request.env.http_host+'/'+request.application+'/static/images/img_defautl.jpg'
				value = IMG(_src=value)	
			elif self.table[fname].represent: 
				pass
			elif ckeditor: 
				value = XML(value)
			else:
				if fformat:
					if ftype in ['integer','double']: 
						value = fformat.format(value)
						value = value.replace(",","|")
						value = value.replace(".",",")
						value = value.replace("|",".")
					elif ftype in ['date','datetime','time']: value = value.strftime(fformat)
		except Exception, e:
			print "field_format: ", e, fname
		return value
		
	def view(self,header="",settings={}):
		request = current.request
		T = current.T
		content = TABLE(_class='table table-striped defview table-hover',_id="table_view")
		thead = THEAD()
		tr = TR()
		for key in self.settings.keys():
			if key not in settings.keys(): settings[key] = self.settings[key]
		
		rows, count = self.get_rows(orderby=settings.get("orderby"),length=settings.get("length"))
		
		if settings.get("check_on"): tr.append(TH(INPUT(_type='checkbox',_name='check_all',_id='check_all',_onclick="CheckAll();"),_class='stt',_style="width: 20px;text-align: center;"))
		if settings.get("index_on"): tr.append(TH(T("TT"),_style="width: 20px;text-align: center;"))
		if settings.get("edit_on"): tr.append(TH(A(I(_class="fa fa-edit fa-fw"),_href="#",_title=T("Chỉnh sửa dữ liệu")),_style="width: 20px;text-align: center;"))
		if not settings.get("link_modal"):					
			if settings.get("read_on"): tr.append(TH(A(I(_class="fa fa-folder-open-o fa-fw"),_href="#",_title=T("Xem dữ liệu")),_style="width: 20px;text-align: center;"))
		if settings.get("delete_on"): tr.append(TH(A(I(_class="fa fa-trash-o fa-fw"),_href="#",_title=T("Xóa dữ liệu")),_style="width: 20px;text-align: center;"))
		
		for btn in self.buttons: tr.append(TH(I(_class=btn[1]),_style="width: 20px;text-align: center;"))
		
		from bootrap import Modals
	
		tfield = self.cms.define_tablefield()
		fields = self.cms.db((tfield.dtable==self.cms.db.dtable.id)&(self.db.dtable.name==self.tablename)).select(tfield.ALL,orderby=tfield.display_order)
		for field in fields:
			if field.show_on_table: tr.append(TH(T(field.dlabel)))
		
		attach = False
		if settings.get("attachment",True):	
			dtable = self.cms.define_dtable()
			row = self.cms.db(dtable.name==self.tablename).select().first()
			if row:
				if row.attachment:
					from plugin_upload import FileUpload
					tr.append(TH(T("Attachment")))
					attach = True
			
		thead.append(tr)
		content.append(thead)
		page = self.get_page()
		length = self.get_length()
		i = (page-1)*length		
		for row in rows:
			tr = TR(_class='line_%s'%(i%2))
			if settings.get("check_on"): 
				tr.append(TD(INPUT(_type='checkbox',_name='table_id',_value=row.id),_class='stt'))
			if settings.get("index_on"): 
				tr.append(TD(i+1,_class='stt'))
			if settings.get("edit_on"): 
				link = settings.get("link_edit_table","medit.htm")
				if link.endswith(".htm"):
					tr.append(TD(Modals(caption = (I(_class="fa fa-edit fa-fw")),source=self.get_url(link,args=[self.tablename,row.id]),reload=True)))
				else:	
					tr.append(TD(A(I(_class="fa fa-edit fa-fw"),_href=self.get_url(link,args=[self.tablename,row.id]),_title="%s %s"%(T("Nhấn để chỉnh sửa dòng"),i+1))))
			if not settings.get("link_modal"):					
				if settings.get("read_on"): 
					tr.append(TD(Modals(caption = (I(_class="fa fa-folder-open-o fa-fw")),source=self.get_url(settings.get("link_read","read"),args=[self.tablename,row.id]))))
			if settings.get("delete_on"): 
				link = settings.get("link_delete","mdelete.htm")
				if link.endswith(".htm"):
					tr.append(TD(Modals(caption = (I(_class="fa fa-trash-o fa-fw")),source=self.get_url(link,args=[self.tablename,row.id]),reload=True)))
				else:	
					tr.append(TD(A(I(_class="fa fa-trash-o fa-fw"),_href=self.get_url(link,args=[self.tablename,row.id]))))
			for btn in self.buttons: 
				tr.append(TD(Modals(caption = I(_class=btn[1]),source=URL(r=request,c=self.c,f=btn[0],args=[self.tablename,row.id]))))			
			for field in fields:
				if field.show_on_table:
					v = self.field_format(row[field.dfield.name],field.dfield.name,field.dfield.ftype,field.fformat,field.ckeditor)
					if field.link_on_table: 
						if settings.get("link_modal",True):
							v = Modals(caption = (v),source=self.get_url(settings.get("link_read","read"),args=[self.tablename,row.id]))
						else:	
							v = A(v,_href=URL(r=request,c=self.c,f="explorer",args=[self.tablename,row.id]),_title=T("Nhấn để xem chi tiết"))
					tr.append(TD(v))
			if attach:	
				files = FileUpload(db=self.cms.db,tablename=self.tablename,table_id=row.id,upload_id=0)
				tr.append(TD(files.view_list()))

			content.append(tr)
			i += 1
		if header:
			header = H4(T(header))
		content = DIV(header,content,_id="explorer_view")
		nb = len(rows)
		if nb>0:
			if nb<count: 
				content = DIV(content,DIV(self.pagination(count,self.get_length()),_class='clearfix'))
		return content		
		
	def read(self):
		if not self.id: 
			return ''
		try:	
			T = current.T
			table = self.table
			row = self.table(self.id)		
			content = TABLE(_id=self.tablename,_class='table table-striped defview')
			
			tfield = self.cms.define_tablefield()
			fields = self.cms.db((tfield.dtable==self.cms.db.dtable.id)&(self.db.dtable.name==self.tablename)).select(tfield.ALL,orderby=tfield.display_order)
			for field in fields:
				if field.show_on_table: 
					v = self.field_format(row[field.dfield.name],field.dfield.name,field.dfield.ftype,field.fformat,field.ckeditor)
					content.append(TR(TD(B(T(field.dlabel)),_class='lablel'),TD(v)))

			dtable = self.cms.define_dtable()
			row = self.cms.db(dtable.name==self.tablename).select().first()
			if row:
				if row.attachment:
					from plugin_upload import FileUpload
					attach = FileUpload(db=self.cms.db,tablename=self.tablename,table_id=self.id,upload_id=0)
					content.append(TR(TD(B(T('Đính kèm')),_class='lablel'),TD(attach.view_publish())))
			
			content = DIV(DIV(INPUT(_type='checkbox',_name='objects',_value=self.id,_checked=True,_style="display:none"),_id='process_id'),content)
			return content
		except Exception, e:
			return e

	def get_url(self,url,args=[],vars=None):
		tmp = url.split('/')
		if len(tmp)>1: c, f = tmp[0], tmp[1]
		else: c, f = 'plugin_table', tmp[0]
		return URL(r=current.request,c=c,f=f,args=args,vars=vars)
		
	def delete(self,id):
		id = id or self.id 
		self.table(self.id).delete_record()					
				
	def pagination(self,count,length):
		T = current.T
		request = current.request
		args = [self.tablename,"1.html"]
		page = self.get_page()
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
			url = URL(r=request,args=args)
			ul.append(LI(A(T('First'),'  ',_href=url)))
			ul.append(LI(m1))
		for x in xrange(p1,p2):
			args[PAGE]='%s.html'%x
			url = URL(r=request,args=args)
			ul.append(LI(A(x,'  ',_href=url),_class='active' if x == page else ''))
		if m2=='...':
			ul.append(LI(m2))
			args[PAGE]='%s.html'%pagecount
			url = URL(r=request,args=args)
			ul.append(LI(A(T('End'),_href=url)))
		content.append(ul)
		return content			
		
	def menu(self,folder,deep=1,**attr):
		table = self.cms.define_folder()
		rows = self.cms.db(table.parent==folder).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class')),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id')))
		folders = attr.get('folders',[])
		add = None
		a_class = attr.get('a_class_deep') + str(deep) if attr.get('a_class_deep') else attr.get('a_class_%s'%deep,attr.get('a_class',""))
		a_id = attr.get('a_id_deep') + str(deep) if attr.get('a_id_deep') else attr.get('a_id_%s'%deep,attr.get('a_id',""))
		li_class = attr.get('li_class_deep') + str(deep) if attr.get('li_class_deep') else attr.get('li_class_%s'%deep,attr.get('li_class',""))
		li_id = attr.get('li_id_deep') + str(deep) if attr.get('li_id_deep') else attr.get('li_id_%s'%deep,attr.get('li_id',""))
		icon_class = attr.get('icon_class_deep') + str(deep) if attr.get('icon_class_deep') else attr.get('icon_class_%s'%deep,attr.get('icon_class',""))
		icon = I(_class="fa %s fa-fw"%icon_class) if icon_class else ""
		for row in rows:
			child = self.menu(row.id,deep+1,**attr)
			url = URL(r=current.request,f='explorer',args=[self.tablename],vars={FIELDPREFIX+'folder':row.id})
			if not (((len(folders)>0)&(row.id not in folders))|(not self.auth.has_permission("explorer", "folder", row.id))):
				link = A(icon, current.T(row.label or row.name),_href=url,_class=a_class,_id=a_id)
				content.append(LI(link,child,_class=li_class+(" active" if str(row.id)==current.request.vars.folder else ""),_id=li_id))
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
		
	def menu_breadcrumb(self):
		procedure_id = self.get_id('procedures',self.procedure_name)
		if procedure_id:
			p = self.define_procedures()
			parent = p(procedure_id).folder_parent
			from plugin_cms import get_setting
			cms = self.cms
			folder_id = cms.get_folder(self.folder_name)
			if cms.db.folder(folder_id):
				parents = [folder_id]
				while parent != folder_id:
					folder_id = cms.db.folder(folder_id).parent
					if not folder_id: break
					parents = [folder_id] + parents
				menu = OL(_class="breadcrumb")
				i = 1
				for id in parents:
					folder = cms.db.folder(id)
					icon = I(_class="fa fa-home fa-fw") if i == 1 else I(_class="fa fa-folder-open fa-fw")
					li = LI(A(icon,folder.label,_href=URL(r=current.request,c='plugin_process',f="explorer.html",args=[self.procedure_name,self.process_name,folder.name])))
					menu.append(li)
					i +=1
				menu.append(LI(self.create_news(parents[-1]),_class='btn-group'))		
				return menu
		return ''

	def create_news(self,folder_id):
		div = DIV(_class="btn-group")
		cms = self.cms
		role = 'create_'+self.procedure_name
		if self.auth.has_permission("create",'folder',folder_id)|self.auth.has_permission("edit",'folder',folder_id)|self.auth.has_permission(role,'folder',folder_id):
			tables = self.get_tables(cms.db.folder(folder_id).setting)
			for table in tables:
				div.append(A(I(_class="fa fa-edit fa-fw"),current.T('New '+table) ,_class="btn btn-danger "+table,_href=URL(r=current.request,c='plugin_process',f='edit.html',args=[self.procedure_name,self.process_name,self.folder_name,table])))
		return div
		
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
		
	def get_vars(self,vars):	
		
		record = self.table(self.id) if self.id else None
		fields = {}
		for fieldname in self.table.fields:
			if fieldname in vars.keys():
				field = self.table[fieldname]
				
				requires = field.requires
				if requires:
					if not isinstance(requires, (list, tuple)):
						requires = [requires]
					for k, validator in enumerate(requires):
						try:
							(value, errors) = validator(vars[fieldname])
							vars[fieldname] = value
						except:
							msg = "%s: %s %s" % (current.T("Validation error, field"),name,validator)
							return msg			
				
				if field.type == 'id':
					continue
				if field.type == 'boolean':
					if vars.get(fieldname, False):
						fields[fieldname] = True
					else:
						fields[fieldname] = False
				elif field.type == 'upload':
					f = vars[fieldname]
					fd = '%s__delete' % fieldname
					if f == '' or f is None:
						if vars.get(fd, False):
							f = self.table[fieldname].default or ''
							fields[fieldname] = f
						elif record:
							if record[fieldname]:
								fields[fieldname] = record[fieldname]
							else:
								f = self.table[fieldname].default or ''
								fields[fieldname] = f
						else:
							f = self.table[fieldname].default or ''
							fields[fieldname] = f
						if not f:
							continue
						else:
							f = os.path.join(
								current.request.folder,
								os.path.normpath(f))
							source_file = open(f, 'rb')
							original_filename = os.path.split(f)[1]
					elif hasattr(f, 'file'):
						(source_file, original_filename) = (f.file, f.filename)
					elif isinstance(f, (str, unicode)):
						# do not know why this happens, it should not
						(source_file, original_filename) = (cStringIO.StringIO(f), 'file.txt')
					else:
						# this should never happen, why does it happen?
						# print 'f=', repr(f)
						continue
					newfilename = field.store(source_file, original_filename,
											  field.uploadfolder)
					# this line was for backward compatibility but problematic
					# self.vars['%s_newfilename' % fieldname] = newfilename
					fields[fieldname] = newfilename
					if isinstance(field.uploadfield, str):
						fields[field.uploadfield] = source_file.read()
					# proposed by Hamdy (accept?) do we need fields at this point?
					continue
				elif fieldname in vars:
					fields[fieldname] = vars[fieldname]
					
				value = fields.get(fieldname, None)
				if field.type == 'list:string':
					if not isinstance(value, (tuple, list)):
						fields[fieldname] = value and [value] or []
				elif isinstance(field.type, str) and field.type.startswith('list:'):
					if not isinstance(value, list):
						fields[fieldname] = [safe_int(x) for x in (value and [value] or [])]
				elif field.type == 'integer':
					if value is not None:
						fields[fieldname] = safe_int(value)
				elif field.type.startswith('reference'):
					fields[fieldname] = safe_int(value)
					if fields[fieldname] == 0: fields[fieldname] = None
				elif field.type == 'double':
					if value is not None:
						fields[fieldname] = safe_float(value)
		return fields