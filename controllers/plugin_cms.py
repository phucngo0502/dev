# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 15/03/2014
# Version 0.2 Date: 18/05/2015
###################################################


@auth.requires(auth.has_membership(role='admin'))	
def index():
	content = H2("Plugin CMS")
	response.view = 'plugin_cms/content.%s'%request.extension
	return dict(content=content)

@auth.requires_login()	
def datatable():
	tablename = request.args(1) or request.args(0)
	table = cms.define_table(tablename)
	if not table: redirect(URL(f="index"))
	for field in table.fields:
		if field=="email":
			table[field].requires = IS_EMAIL(error_message=T('Invalid email!'))
		elif table[field].type.startswith("reference"):
			ref = table[field].type.split(" ")[-1]
			if ref == tablename:
				table[field].requires = IS_NULL_OR(IS_IN_DB(db,'%s.id'%ref,'%(name)s'))
			else:
				table[field].requires = IS_IN_DB(db,'%s.id'%ref,'%(name)s')
			table[field].represent = lambda v,row: v.name if v else ""
	form = DIV(H3(T("Table %s"%tablename)),SQLFORM.grid(table,user_signature=False,csv=False))
	return dict(content=form)	
	
@auth.requires(auth.has_membership(role='admin'))	
def menu():
	from plugin_cms import CmsModel
	cms = CmsModel()
	table = cms.define_dtable()
	tables = [(T("Add new table"),URL(f='manage'),"fa-plus-square",[]),(T("Import new table"),URL(f='import_table'),"fa-plus-square",[])]
	rows = cms.db(table.is_import==False).select(orderby=table.display_order|table.name)
	imports = []
	for row in rows:
		actions = [(T("Edit"),URL(f='manage',args=[row.id]),"fa-edit",[]),(T("Setting"),URL(f='setting',args=[row.id]),"fa-cog",[]),(T("Fields"),URL(f='field',args=[row.id]),"fa-table",[])]
		imports.append((row.name,"#","fa-database",actions))
	tables.append((T("Cms tables"),"#","fa-database",imports))
	rows = cms.db(table.is_import==True).select(orderby=table.display_order|table.name)
	imports = []
	for row in rows:
		actions = [(T("Edit"),URL(f='manage',args=[row.id]),"fa-edit",[]),(T("Setting"),URL(f='setting',args=[row.id]),"fa-cog",[]),(T("Fields"),URL(f='field',args=[row.id]),"fa-table",[])]
		imports.append((row.name,"#","fa-sign-in",actions))
	tables.append((T("Import tables"),"#","fa-sign-in",imports))
	tables = [(T("Field manage"),URL(f='dfield'),"fa-table",[])]+tables
	from bootrap import Menu
	content = Menu().vertical(tables)	
	return content

@auth.requires(auth.has_membership(role='admin'))	
def manage():
	from plugin_cms import CmsCrud
	cms = CmsCrud()
	id = request.args(0)
	dtable = cms.dtable()
	for field in ["layout","setting","display_row","display_rows","link_edit"]:
		dtable[field].readable = False
		dtable[field].writable = False
	form = SQLFORM(dtable,id,showid=False,deletable=True)
	if form.process().accepted:
		if id: cms.define_table(form.vars.name,True)
		redirect(URL(f="setting",args=[form.vars.id]))		
	content = DIV(H3(T("Thông tin bảng")," ",B(dtable(id).name)) if request.args(0) else H3(T("Tạo mới bảng")),form)	
	response.view = 'plugin_cms/content.%s'%request.extension
	return dict(content=content)

@auth.requires(auth.has_membership(role='admin'))	
def import_table():		
	import re
	filename = "%s/modules/%s.py"%(request.folder,"datatables")
	f = open(filename)	
	expr = r"def define\w+"
	funcs = re.findall(expr,f.read())
	f.close()
	content = UL()
	dtable = cms.define_dtable()
	for f in funcs:
		f = f.replace('def ','').replace('()','')
		tablename = f.replace("define_","")
		checked = (db(dtable.name==tablename).count()==0)
		content.append(LI(INPUT(_type="checkbox",_name="tablename",_value=tablename),LABEL(tablename)))
	ajax = "ajax('%s',['tablename'],'result')"%URL(f='import_update')
	btn = INPUT(_type='button',_value=T('Submit'),_onclick=ajax,_class="btn btn-primary")
	content = DIV(H3(T("Import table from module datatables.py")),content,DIV(btn),_id="result")
	response.view = 'plugin_cms/content.%s'%request.extension
	return dict(content=content)

@auth.requires(auth.has_membership(role='admin'))	
def import_update():
	try:
		tables = request.vars.tablename or []
		if isinstance(tables,str): tables = [tables]
		dtable = cms.define_dtable()
		setting = "{'edit_on': 'on', 'link_edit_table': 'plugin_table/medit.htm', 'link_delete': 'plugin_table/mdelete.htm', 'read_on': 'on', 'link_read': 'plugin_table/read', 'check_on': 'on', 'delete_on': 'on'}"
		for table in tables:
			row = cms.db(dtable.name==table).select().first()
			tid = row.id if row else dtable.insert(name=table,label=table,is_import=True,setting=setting)
			t = cms.define_table(table,True)
			dfield = cms.define_dfield()
			tfield = cms.define_tablefield()
			rows = cms.db((tfield.dtable==tid)&(tfield.dfield==dfield.id)&(~dfield.name.belongs(t.fields))).select(tfield.ALL)
			for row in rows:	
				if cms.db((tfield.dfield==row.dfield)&(tfield.dtable!=tid)).count()==0:
					if row.dfield.name not in ["folder","name","description","htmlcontent","avatar","expired_on","created_by","created_on"]:
						cms.db(dfield.id==row.dfield).delete()
				cms.db(tfield.id==row.id).delete()		
				
			for field in t.fields:
				# row = cms.db((dfield.name==field)&(dfield.ftype!=t[field].type)).select().first()
				# if row:
					# if cms.db((tfield.dfield==row.id)&(tfield.dtable!=tid)).count()==0: cms.db(dfield.id==row.id).delete()
				row = cms.db((dfield.name==field)&(dfield.ftype==t[field].type)).select().first()
				fid = row.id if row else dfield.insert(name=field,ftype=t[field].type)
				if cms.db((tfield.dfield==fid)&(tfield.dtable==tid)).count()==0:
					if field == "id":
						tfield.insert(dtable=tid,dfield=fid,dlabel=t[field].label or field,writable=False,readable=False)
					else:
						tfield.insert(dtable=tid,dfield=fid,dlabel=t[field].label or field,show_on_table=(field=="name"),link_on_table=(field=="name"))					
				rows = cms.db((dfield.name==field)&(dfield.ftype!=t[field].type)).select()
				cms.db((tfield.dtable==tid)&tfield.dfield.belongs([row.id for row in rows])).delete()		
		return H3(T("Cập nhật thành công!"),_style="color:blue")
	except Exception, e:
		print e
		return H3(e,_style="color:red")
		
@auth.requires(auth.has_membership(role='admin'))	
def setting():
	from plugin_cms import CmsCrud, get_setting
	cms = CmsCrud()
	id = request.args(0)
	dtable = cms.dtable()
	dfield = cms.define_dfield()
	tfield = cms.define_tablefield()
	row = dtable(id)
	if not row:
		redirect(URL(f="index"))
	content = TABLE(_class="table table-hover")
	
	if not row.is_import:
		default = ['folder','name','description','avatar','publish_on','expired_on','created_on','created_by']
		field_default = get_setting(row.setting,key='field_default',default=default)
		fields = SPAN()
		for field in default:
			fields.append(INPUT(_type="checkbox",_name="field_default",_value=field,_checked=(field in field_default)))
			fields.append(SPAN(field.capitalize(),_style="padding-right:5px;"))
		content.append(TR(TD(T("Chọn trường dữ liệu")),TD(fields)))
		
	content.append(TR(TD(T("File giao diện")),TD(cms.widget_layout(dtable.layout, row.layout))))
	content.append(TR(TD(T("URL chỉnh sửa trong qui trình")),TD(INPUT(_value=row.link_edit or "",_name="link_edit",_placeholder="controller/function",_class="string form-control"))))
	
	if cms.db((tfield.dtable==id)&(tfield.dfield==cms.db.dfield.id)&(cms.db.dfield.ftype=="reference folder")).count()>0:	
		folder = get_setting(row.setting,key='folder',default=None)
		from plugin_app import select_option
		cms.define_folder()
		options = [OPTION("",_value="")]+select_option(cms.db,cms.auth,'folder',selected=[int(folder)] if folder else [],field='label')
		#select = SELECT(options,_name="folder",_class="form-control")
		select = ""
		for o in options:
			select += str(o)
		select =XML('<select class="form-control" name="folder">'+select+'</select>')	
		content.append(TR(TD(T("Thư mục chính")),TD(select)))
	
	rows = cms.db((dfield.name==row.name)&(tfield.dfield==dfield.id)&(dtable.id==tfield.dtable)).select(dtable.ALL,orderby=dtable.name)
	tables = get_setting(row.setting,key='table_attachment',default=[])
	if isinstance(tables,str): tables = [tables]
	ops = [OPTION(r.name,_value=r.name,_selected=(r.name in tables)) for r in rows]
	select = SELECT(ops,_name="table_attachment",_multiple="multiple",_class="js-example-placeholder-multiple form-control")
	content.append(TR(TD(T("Bảng dữ liệu liên kết")),TD(select)))
	
	content.append(TR(TD(T("Số dòng hiển thị")),TD(INPUT(_value=get_setting(row.setting,key='length',default="10"),_name="length",_class="integer form-control"))))
	
	rows = cms.db((tfield.dtable==id)&(tfield.dfield==cms.db.dfield.id)&(cms.db.dfield.ftype.belongs(["int","datetime","date"]))).select(tfield.ALL,orderby=tfield.display_order)	
	if len(rows)>0:
		year_field = get_setting(row.setting,key='year_field',default=None)
		ops = [OPTION(r.dfield.name,_value=r.dfield.name, _selected=(r.dfield.name==year_field)) for r in rows]
		select = SELECT([""]+ops,_name="year_field",_class="form-control")
		content.append(TR(TD(T("Năm dữ liệu theo trường")),TD(select)))
	
	checked = get_setting(row.setting,key='check_on',default=None)
	content.append(TR(TD(T("Hiển thị số thứ tự")),TD(INPUT(_type="checkbox",_checked=checked,_name="index_on"))))
	checked = get_setting(row.setting,key='check_on',default=True)
	content.append(TR(TD(T("Hiển thị nút chọn")),TD(INPUT(_type="checkbox",_checked=checked,_name="check_on"))))
	checked = get_setting(row.setting,key='edit_on',default=True)
	content.append(TR(TD(T("Hiển thị nút sửa")),TD(INPUT(_type="checkbox",_checked=checked,_name="edit_on"),INPUT(_value=get_setting(row.setting,'link_edit_table',"plugin_table/edit"),_name="link_edit_table"))))
	checked = get_setting(row.setting,key='delete_on',default=None)
	content.append(TR(TD(T("Hiển thị nút xóa")),TD(INPUT(_type="checkbox",_checked=checked,_name="delete_on"),INPUT(_value=get_setting(row.setting,'link_delete',"plugin_table/delete"),_name="link_delete"))))
	checked = get_setting(row.setting,key='read_on',default=None)
	content.append(TR(TD(T("Hiển thị nút xem trước")),TD(INPUT(_type="checkbox",_checked=checked,_name="read_on"),INPUT(_value=get_setting(row.setting,'link_read',"plugin_table/read"),_name="link_read"))))
		
	form = FORM(content,_class="form-horizontal")
	form.append(INPUT(_type="submit",_value=T("Chấp nhận"),_class="btn btn-primary"))
	
	if form.process().accepted:
		setting = {}
		for key in form.vars.keys(): 
			setting[key] = form.vars[key]
		row.update_record(setting=setting, layout=form.vars.layout, link_edit=form.vars.link_edit)
		fields = request.vars.field_default
		if fields:
			if isinstance(fields, str): fields = [fields]
			for field in fields:
				if field == 'folder': ftype = "reference folder"
				elif field == 'name': ftype = "string"
				elif field == 'avatar': ftype = "upload"
				elif field == 'created_by': ftype = "integer"
				elif field in ['htmlcontent','description']: ftype = "text"
				elif field in ['publish_on','expired_on','created_on']: ftype = "datetime"			
				r = cms.db((dfield.name==field)&(dfield.ftype==ftype)).select().first()
				fid = r.id if r else dfield.insert(name=field,ftype=ftype)
				if cms.db((tfield.dtable==row.id)&(tfield.dfield==fid)).count()==0:
					tfield.insert(dtable=row.id,dfield=fid,dlabel=field,show_on_table=(field in ["name","folder"]),link_on_table=(field=="name"))
		cms.define_table(row.name,True)
		redirect(URL(f="field",args=[id]))
	
	content = DIV(H3(T("Cấu hình hiển thị bảng dữ liệu")," ",B(dtable(id).name)),form)	
	response.view = 'plugin_cms/content.%s'%request.extension
	return dict(content=content)
	
@auth.requires(auth.has_membership(role='admin'))
def field():
	from plugin_cms import CmsModel
	cms = CmsModel()
	id = request.args(0)
	dtable = cms.define_dtable()
	tablename = dtable(id).name
	dfield = cms.define_dfield()
	tablefield = cms.define_tablefield()
	table = cms.define_table(tablename,True)
	content = TABLE(THEAD(TR(TH("STT"),TH("Tên trường"),TH("Nhãn"),TH("Kiểu dữ liệu"),TH("Được ghi"),TH("Được đọc"),TH("Có liên kết"),TH("Được hiển thị"))),_class="table table-bordered table-hover")
	if table:
		i = 1
		body = TBODY()
		rows = cms.db((tablefield.dtable==id)).select(orderby=tablefield.display_order)
		for row in rows:
			tr = TR(TD(i),_class="active")
			name = A(row.dfield.name if row.dfield else "None",_href=URL(args=[id,row.id]))
			tr.append(TD(name))
			tr.append(TD(row.dlabel))
			tr.append(TD(row.dfield.ftype if row.dfield else "None"))
			tr.append(TD(row.writable))
			tr.append(TD(row.readable))
			tr.append(TD(row.link_on_table))
			tr.append(TD(row.show_on_table))
			body.append(tr)
			i+=1
		content.append(body)
	elif dtable(id).is_import:
		content = H3(dtable(id).label, " ", T("chưa được khởi tạo."),_style="color:red;")
		response.view = 'plugin_cms/content.%s'%request.extension
		return dict(content=content)
		
	content = DIV(H3(T("Trường dữ liệu của bảng"), " ", B(T(dtable(id).label or dtable(id).name))),content)
	if (not dtable(id).is_import)|(request.args(1)!=None): 
		from plugin_cms import CmsCrud
		cms = CmsCrud()
		table = cms.tablefield()
		table.dtable.default = id
		table.dtable.writable = False
		table.dtable.readable = False
		if dtable(id).is_import:
			table.dfield.readable = False
			table.dfield.writable = False
			deletable=False
		else:
			deletable=True		
		form = SQLFORM(table,request.args(1),showid=False,deletable=deletable,keepvalues=True)
		if form.process(onvalidation=fieldvalid).accepted:
			if not dtable(id).is_import: cms.define_table(tablename,True)
			redirect(URL(args=[id]))
		content.append(H4(T("Chỉnh sửa thông tin")," ",B(table(request.args(1)).dfield.name)) if request.args(1) else H4(T("Add new field")))
		content.append(form)
	response.view = 'plugin_cms/content.%s'%request.extension
	return dict(content=content)

def fieldvalid(form):
	if request.args(1): return True
	if db((db.tablefield.dtable==request.args(0))&(db.tablefield.dfield==form.vars.dfield)).count()>0:
		form.errors.dfield = T('Trường này đã có!')
	
@auth.requires_login()	
def explorer():
	from plugin_cms import CmsTable
	cms = CmsTable()
	content = cms.view()
	response.view = 'plugin_cms/content.%s'%request.extension
	return dict(content=content)	
			
def page():
	from plugin_cms import CmsFolder
	content = CmsFolder().html()
	return dict(content=content)
		
def read():
	from plugin_cms import CmsContent
	content = CmsContent().html(request.args(1),request.args(2))
	return dict(content=content)	
	
@auth.requires(auth.has_membership(role='admin'))	
def dfield():
	from plugin_cms import CmsCrud
	cms = CmsCrud()
	
	def onupdate(form):
		cms.define_table(form.vars.name,True)
		table = cms.define_tablefield()
		rows = cms.db(table.dfield==form.vars.id).select(table.dtable,distinct=True)
		for row in rows:
			cms.define_table(row.dtable.name,True)
			
	def ondelete(table,id):
		table = cms.define_tablefield()
		rows = cms.db(table.dfield==id).select(table.dtable,distinct=True)
		for row in rows:
			cms.define_table(row.dtable.name,True)
		cms.db(table.dfield==id).delete()
		
	table = cms.dfield()
	if cms.db(table).count() == 0:
		table.insert(name="folder",ftype="reference folder")
		table.insert(name="name",ftype="string")
		table.insert(name="description",ftype="text")
		table.insert(name="htmlcontent",ftype="text",ckeditor=True)
		table.insert(name="avatar",ftype="upload")
		table.insert(name="publish_on",ftype="datetime")
		table.insert(name="expired_on",ftype="datetime")
		table.insert(name="created_on",ftype="datetime")
		table.insert(name="created_by",ftype="integer")
	
	form = SQLFORM.grid(table,onupdate=onupdate,ondelete=ondelete,csv=False,details=False)
	response.view = 'plugin_cms/content.html'	
	return dict(content=form)	

@auth.requires_login()	
def widget_type():
	if ((not request.vars.fieldtype)&('reference' in request.vars.value))|('reference' in str(request.vars.fieldtype)): 
		from plugin_cms import CmsModel
		cms = CmsModel()
		table = cms.define_dtable()
		rows = cms.db(table).select(orderby=table.name)
		tables = cms.db.tables
		if 'folder' not in cms.db.tables: tables.append('folder')
		for row in rows:
			if row.name not in cms.db.tables: tables.append(row.name)
		tables.sort()	
		op = [""]+[OPTION(T(table),_value=table,_selected=(request.vars.value.endswith(table))) for table in tables]
		widget = SELECT(op,_name='tablename',_id="tablename")
		script = SCRIPT('''$('#tablename').change(function() {document.getElementById("dfield_ftype").value = document.getElementById("fieldtype").value+' '+$(this).val(); });''')	
		return SPAN(widget,script)
	else:
		script = SCRIPT('''document.getElementById("dfield_ftype").value = document.getElementById("fieldtype").value;''')	
		return script

@auth.requires_login()		
def widget_field():
	from plugin_cms import CmsModel
	cms = CmsModel()
	table = cms.define_dfield()
	ftype = request.vars.fieldtype or request.vars.ftype
	if len(ftype.split(' '))==3: ftype = ftype.split(' ')[0] + ' ' + ftype.split(' ')[1]
	rows = cms.db(table.ftype.startswith(ftype)).select(orderby=table.name)
	op = [OPTION(row.name,_value=row.id,_selected=(row.id==int(request.vars.value))) for row in rows]
	widget = SELECT(op,_name='dfield',_id='tablefield_dfield')
	return widget
		
		
##################################

def config():
	config = dict(color='black', language='English')
	form = SQLFORM.dictform(config)
	if form.process().accepted: config.update(form.vars)
	return dict(form=form)