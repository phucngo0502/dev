###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 7/03/2012
# Version 0.3 Date: 22/05/2015
# Version 1.0 Date: 14/09/2015
###################################################


###################################################
# SET INIT VARIABLES

from plugin_process import ProcessCms

PROCEDURE = 0
PROCESS = 1
FOLDER = 2
PAGE = 3
TABLENAME = 3
OBJECTSID = 4

Process = ProcessCms(	procedure=request.args(PROCEDURE),
						process=request.args(PROCESS),
						folder_name=request.args(FOLDER),
						tablename=request.args(TABLENAME),
						objects_id=request.args(OBJECTSID))
						
###################################################


@auth.requires(auth.has_membership(role='admin'))	
def table():
	tablename = request.args(0)
	eval('processmodel.define_%s(True)'%tablename)
	content = SQLFORM.grid(db[tablename],args=request.args)
	response.view = 'plugin_process/content.html'	
	return dict(content=content)

@auth.requires_login()		
def index():
	content = H2('Hệ thống quản trị tin tức')
	response.view = 'news/content.html'	
	return dict(content=content)
	
def toolbars():	
	content = Process.get_toolbars()
	# Append more button
	# avatar='http://%s/%s/static/images/%s'%(request.env.http_host,request.application,'xxx.png') 
	# label = SPAN(IMG(_src=avatar),SPAN(T("xxx")))
	# url = "#"
	# process = A(label,_href=url,_class='btn btn-default button_process_False',_id='process_xxx') #edit view explore.html or use url, modal, ...
	# content.append(process)
	return content

def filter():	
	content = Process.get_filter()
	return content
	
def breadcrumb():	
	content = Process.menu_breadcrumb()
	return content	

@auth.requires_login()			
def explorer():
	from plugin_process import ProcessCms
	p = ProcessCms()
	content = p.explorer()
	return dict(content=content)	
		
@auth.requires_login()			
def read():
	content = Process.read()
	return content		
	
@auth.requires(auth.has_membership(role='admin') or (auth.has_permission('create', 'folder', Process.folder_id) or auth.has_permission('edit', 'folder', Process.folder_id)))	
def edit():
	from plugin_app import Dropdown
	from plugin_ckeditor import CKEditor
	db = Process.cms.db
	Process.cms.define_dtable()
	tablename = Process.tablename
	table_id = Process.get_table_id()
	dtable = db(db.dtable.name==tablename).select().first()
	if not dtable: return dict(content='Table %s not existe'%tablename)		
	table = Process.cms.define_table(tablename)
	if not table: return dict(content='Can not define %s'%tablename)	
	avatar = ' <i style="color:#f00;">Nếu không chọn ảnh đại diện hệ thống sẽ dụng hình ảnh đầu tiên trong bài viết.</i>'
	if table_id:
		if table[table_id].avatar:
			avatar = str(IMG(_class='thumbnail',_src=Process.cms.get_avatar_by_size('news',table[table_id].avatar,200,180)))
	form=Process.cms.sqlform(tablename,table_id,addnew=False,default_show={'category':1},default_comment={'avatar':avatar})
	
	if dtable.attachment: 
		if not table_id: 
			if not request.vars.uuid:
				import uuid
				redirect(URL(args=request.args,vars=dict(uuid=uuid.uuid1().int)))

		from plugin_upload import FileUpload
		fileupload = FileUpload(db=db,tablename=tablename,table_id=table_id or request.vars.uuid,upload_id=None)
		upload = fileupload.formupload1(colorbox=False)
	else: 
		upload = ''

	form[0][-1].append(TR(TD(),TD(INPUT(_type='submit',_value=T('Submit'),_style="display: none;",_id='act_submit'))))
	
	if form.process().accepted:
		new_content=''
		row = table(form.vars.id)
		if form.vars.htmlcontent:
			new_content = change_img(form.vars.htmlcontent)
			row.update_record(htmlcontent=new_content)
			if not form.vars.avatar:
				update_imageURL_in_content(table,form.vars.id)
			else:
				size_img(row,tablename)
			
		if dtable.attachment:
			if request.vars.uuid:
				fileupload.update(form.vars.id,request.vars.uuid)
		if not table_id: Process.create_objects(form.vars.folder,tablename,form.vars.id)
		else: 
			Process.update_folder(form.vars.folder,tablename,table_id)
			if dtable.publish:
				from plugin_cms import CmsPublish
				cms = CmsPublish(db=db)
				cms.update(tablename,table_id)
				cms.update_no_link(tablename,table_id)
		args = request.args[:4]
		args[2] = db.folder(form.vars.folder).name
		cache.ram.clear()
		redirect(URL(f='explorer',args=args))
		
	if table_id:
		msg = T("Update table %s"%tablename)
	else:
		msg = T("Create table %s"%tablename)
		
	div = DIV(H3(msg,_class='title_box'),form,_class='def_edit_product')
	div.append(DIV(upload,_class='upload_file'))
	div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_onclick='javascript:history.go(-1)',_class='btn btn-primary')))
	script = SCRIPT('''$("#act_submit_ao").click(function () {$("#act_submit").trigger('click');});''')
	div.append(script)
	return dict(content=div)		
	
@auth.requires(auth.has_membership(role='admin') or auth.has_permission('delete', 'folder'))
def delete():
	Process.delete()
	cache.ram.clear()
	redirect(URL(c=Process.c,f='explorer.html',args=request.args[:TABLENAME+1]),client_side=True)

@auth.requires_login()
def delete_objects():
	Process.delete_objects(Process.get_objects_ids())
	cache.ram.clear()
	redirect(URL(c=Process.c,f='explorer.html',args=request.args[:TABLENAME+1]),client_side=True)	
	
	
		
@auth.requires_login()	
def process():
	try:
		process_id = int(request.vars.process)
		objects_ids = Process.get_objects_ids()
	except Exception, e:
		print e
		process_id = 0
		objects_ids = []
	process = Process.define_process()
	if not request.vars.ocomment:
		if process(process_id):
			if process(process_id).is_comment:
				redirect(URL(c='plugin_process',f='comment.html',args=request.args,vars=request.vars),client_side=True)
		
	content = Process.process_run(process_id,objects_ids)
	response.view = 'plugin_process/content.%s'%request.extension
	return dict(content=content)

@auth.requires_login()	
def comment():
	from plugin_ckeditor import CKEditor
	htmlcontent = CKEditor(db).editor("ocomment","")
	title = "Add comment for process %s %s"%(Process.process_name,Process.db.auth_user(Process.auth.user_id).role)
	form = FORM(H3(T(title)),htmlcontent,INPUT(_type="submit",_value=T('Submit'),_class="btn btn-primary"),_action=URL(f="process.html",vars=request.vars,args=request.args))
	response.view = 'plugin_process/content.html'	
	return dict(content=form)
	
@auth.requires_login()	
def group():
	if request.vars.objects: 
		objects_ids = request.vars.objects
		if not isinstance(objects_ids,list): objects_ids = [objects_ids]
	elif Process.objects_id: 
		objects_ids = [Process.objects_id]
	try:
		process_id = int(request.vars.process)
		objects_ids = [int(id) for id in objects_ids]
		group_ids = [request.vars.auth_group] if isinstance(request.vars.auth_group,str) else request.vars.auth_group
		group_ids = [int(id) for id in group_ids]
	except Exception, e:
		process_id = 0
		objects_ids = []
		group_ids = []
	try:
		content = Process.process_group(process_id,objects_ids,group_ids)
	except Exception, e: 
		content = e
	redirect(URL(c=Process.c,f='explorer.html',args=request.args[:TABLENAME]))

@auth.requires_login()	
def publish():
	import datetime
	form = TABLE(TR(TD(H2('Xuất bản nội dung'),_conspan=4)),TR(TD(T("Publish on")),TD(INPUT(_name='publish_on',_value=request.now.strftime("%d/%m/%Y %H:%M:%S"),_class="datetime form-control")),TD(T("Expired on")),TD(INPUT(_name='expired_on',_class="datetime form-control"))),_class='table table-striped defview')
	
	# form.append(TR(TD(T("Metadate: Thẻ Title"),SPAN(_id="title_number_key",_class="pull-right")),TD(INPUT(_name='title_page',_class="string form-control",_id='ip_title_page'),_colspan=3)))
	# form.append(TR(TD(T("Metadate: Thẻ description"),SPAN(_id="description_number_key",_class="pull-right")),TD(INPUT(_name='description_page',_class="string form-control",_id='ip_description_page'),_colspan=3)))
	# form.append(TR(TD(T("Metadate: Thẻ keywords")),TD(INPUT(_name='keywords',_class="text form-control"),_colspan=3)))
	form.append(TR(TD(),TD(INPUT(_type="submit",_value=T("Submit"),_class='btn btn-primary'),INPUT(_type="button",_value=T("Cancel"),_onclick="javascript:history.go(-1)",_class='btn btn-primary'))))
	form = FORM(form)
	
	
	if form.process().accepted:
		from plugin_cms import CmsPublish
		from plugin_process import Process
		cms = CmsPublish()
		process = Process()
		if request.vars.objects: 
			objects_ids = request.vars.objects
			if not isinstance(objects_ids,list): objects_ids = [objects_ids]
		elif process.objects_id: 
			objects_ids = [process.objects_id]
		try:
			process_id = int(request.vars.process) 
			objects_ids = [int(id) for id in objects_ids]
			objects = process.define_objects()
			
			publish_on = datetime.datetime.strptime(request.vars.publish_on, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') if request.vars.publish_on else None
			expired_on = datetime.datetime.strptime(request.vars.expired_on, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') if request.vars.expired_on else None
				
			for id in objects_ids:
				o = objects(id) 
				cms.publish(o.tablename,o.table_id,publish_on,expired_on)
			process.process_group(process_id,objects_ids,[])
		except Exception,e: 
			response.view = 'news/content.html'	
			return dict(content=e)
		cache.ram.clear()
		redirect(URL(c='news',f='explorer.html',args=request.args[:3]),client_side=True)
	response.view = 'news/content.html'	
	return dict(content=form)

@auth.requires_login()	
def publish_one():
	form = TABLE(TR(TD(T("Publish on")),TD(INPUT(_name='publish_on',_value=request.now.strftime("%d/%m/%Y %H:%M:%S"),_class="datetime form-control")),TD(T("Expired on")),TD(INPUT(_name='expired_on',_class="datetime form-control"))),_class='table table-striped defview')

	form.append(TR(TD(T("Metadate: Thẻ Title"),SPAN(_id="title_number_key",_class="pull-right")),TD(INPUT(_name='meta_title',_class="string form-control",_id='ip_title_page'),_colspan=3)))
	form.append(TR(TD(T("Metadate: Thẻ description"),SPAN(_id="description_number_key",_class="pull-right")),TD(INPUT(_name='meta_description',_class="string form-control",_id='ip_description_page'),_colspan=3)))
	form.append(TR(TD(T("Metadate: Thẻ keywords")),TD(INPUT(_name='meta_keywords',_class="text form-control"),_colspan=3)))
	
	form.append(TR(TD(),TD(INPUT(_type="submit",_value=T("Submit"),_class='btn btn-primary'),INPUT(_type="button",_value=T("Cancel"),_onclick="javascript:history.go(-1)",_class='btn btn-primary'))))
	form = FORM(form)
	
	scr = '''
	<script type="text/javascript">
		$('#ip_title_page').bind('input', function() {
			ar = $(this).val().length
			div = document.getElementById('title_number_key');
			if (ar <60) {
				div.innerHTML = "<span class='ms_xanh'>"+ar+"</span>" ;
			}
			else if (ar<80) {
				div.innerHTML = "<span class='ms_vang'>"+ar+"</span>" ;
			}
			else {
				div.innerHTML = "<span class='ms_do'>"+ar+"</span>" ;
			}
		});
		
		$('#ip_description_page').bind('input', function() {
			ar1 = $(this).val().length
			div = document.getElementById('description_number_key');
			if (ar1 >70 && ar1 <160) {
				div.innerHTML = "<span class='ms_xanh'>"+ar1+"</span>" ;
			}
			
			else {
				div.innerHTML = "<span class='ms_do'>"+ar1+"</span>" ;
			}
		});
	</script>
	'''
	form.append(XML(scr))
	import datetime
	if form.process().accepted:
		from plugin_cms import CmsPublish
		from plugin_process import Process
		cms = CmsPublish()
		process = Process()
		if request.vars.objects: 
			objects_ids = request.vars.objects
			if not isinstance(objects_ids,list): objects_ids = [objects_ids]
		elif process.objects_id: 
			objects_ids = [process.objects_id]
		try:
			process_id = int(request.vars.process) 
			objects_ids = [int(id) for id in objects_ids]
			objects = process.define_objects()
			publish_on = datetime.datetime.strptime(request.vars.publish_on, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') if request.vars.publish_on else None
			expired_on = datetime.datetime.strptime(request.vars.expired_on, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') if request.vars.expired_on else None
			meta_title = request.vars.meta_title
			meta_description = request.vars.meta_description
			meta_keywords = request.vars.meta_keywords
			for id in objects_ids:
				o = objects(id) 
				cms.publish_one(o.tablename,o.table_id,publish_on,expired_on,meta_title,meta_description,meta_keywords)
			process.process_group(process_id,objects_ids,[])
		except Exception,e: 
			response.view = 'news/content.html'	
			return dict(content=e)
		cache.ram.clear()
		redirect(URL(c='news',f='explorer.html',args=request.args[:3]),client_side=True)
	response.view = 'news/content.html'	
	return dict(content=form)
	
@auth.requires_login()	
def unpublish():
	from plugin_process import Process
	from plugin_cms import CmsPublish
	cms = CmsPublish()
	process = Process()
	if request.vars.objects: 
		objects_ids = request.vars.objects
		if not isinstance(objects_ids,list): objects_ids = [objects_ids]
	elif process.objects_id: 
		objects_ids = [process.objects_id]
	try:
		process_id = int(request.vars.process)
		objects_ids = [int(id) for id in objects_ids]

		objects = process.define_objects()
		for id in objects_ids:
			o = objects(id) 
			cms.unpublish(o.tablename,o.table_id)
	except Exception, e:
		print e
		pass
	cache.ram.clear()
	#process.process_group(process_id,objects_ids,[process.auth_group])
	process.process_group(process_id,objects_ids,db.process(process_id).process_group or [])
	redirect(URL(c='news',f='explorer.html',args=request.args[:3]),client_side=True)

@auth.requires(auth.has_membership(role='admin'))		
def crud():
	from plugin_process import ProcessCrud
	p = ProcessCrud()
	procedures = p.procedures()
	p.process()
	content = SQLFORM.grid(procedures)
	content = SQLFORM.smartgrid(procedures,linked_tables=['process'])
	return dict(content=content)

@auth.requires_login()	
def update_name(table,form):
	from validators import IS_SLUG
	name = form.vars.label	
	name = name.replace('đ','d')
	name = name.replace('Đ','d')
	name = IS_SLUG.urlify(name)
	i = 1
	tmp = name
	while db(table.name==tmp).count()>0:
		tmp = '%s-%s'%(name,i) 
		i+=1
	name = tmp			
	table(form.vars.id).update_record(name=name)
	
	
@auth.requires(auth.has_membership(role='admin'))		
def procedures():
	from plugin_process import ProcessCrud
	p = ProcessCrud()
	table = p.procedures()
	form = SQLFORM(table,request.args(0),showid=False,deletable=True)
	if form.process().accepted:
		if not request.args(0): update_name(table,form)
		redirect(URL(args=[]))
	response.view = 'plugin_process/crud.html'	
	return dict(content=form)
	
@auth.requires(auth.has_membership(role='admin'))	
def processcrud():
	from plugin_process import ProcessCrud
	p = ProcessCrud()
	table = p.process()
	content = DIV()
	if request.vars.procedures:
		table.procedures.default = request.vars.procedures
		table.procedures.writable = False
		table.procedures.readable = False
		content = DIV(H3("Thêm mới quy trình cho thủ tục ", T(p.db.procedures(request.vars.procedures).label)))
	id = request.args(0)
	if id in ["edit","delete","publish","unpublish"]:
		table.url.default = "%s.html"%id
		table.url.writable = False
		id = None		
	elif id:
		content = DIV(H3("Chỉnh sửa quy trình ", B(T(table(id).label))))	
	form = SQLFORM(table,id,showid=False,deletable=True)
	if form.process().accepted:
		if not id: update_name(table,form)
		setting = {}
		for key in form.vars.keys():
			if key.startswith("setting_"): 
				if form.vars[key]=="on": setting[key[8:]] = True
				elif form.vars[key]=="None": setting[key[8:]] = False
				else: setting[key[8:]] = form.vars[key]
		if table(form.vars.id): table(form.vars.id).update_record(setting=str(setting))	
		redirect(URL(args=[],vars=dict(procedures=request.vars.procedures if request.vars.procedures else form.vars.procedures)))
	content.append(form) 
	response.view = 'plugin_process/crud.html'	
	return dict(content=content)
		
@auth.requires(auth.has_membership(role='admin'))	
def pcopy():
	from plugin_process import ProcessCrud
	p = ProcessCrud()
	table = p.process()
	id = request.args(0)
	content = DIV(H3("Chấp nhận tạo mới thủ tục từ ", T(p.db.procedures(id).label)))
	ajax = "ajax('%s', [], 'msg')"%(URL(f='copy_update',args=[id]))
	button = INPUT(_type="button",_value=T("Submit"),_class="btn btn-primary",_onclick=ajax)		
	content.append(button) 
	content.append(DIV(_id='msg')) 
	response.view = 'plugin_process/crud.html'	
	return dict(content=content)

def copy_update():
	try:
		id = int(request.args(0))
		db = Process.db
		procedures = Process.define_procedures()
		process = Process.define_process()
		vars = {}
		row = procedures(id)
		for field in procedures.fields:
			if field != "id": vars[field] = row[field]
		last = db(procedures).select().last()
		vars["name"] = "%s-%s"%(vars["name"],last.id+1)
		vars["label"] = "%s %s"%(vars["label"],last.id+1)
		newid = procedures.insert(**vars)
		rows = db(process.procedures==id).select(orderby=process.display_order)
		d = {}
		for row in rows:
			vars = {}
			for field in process.fields:
				if field != "id": vars[field] = row[field]
			vars["name"] = "%s-%s"%(vars["name"],newid)
			vars["procedures"] = newid
			pid = process.insert(**vars)
			d[str(row.id)]=pid
		for key in d.keys():
			row = process(d[key])
			paccess = []
			for i in row.paccess or []:
				paccess.append(d[str(i)])
			row.update_record(paccess=paccess)
		db.commit()
		return H3("Copy dữ liệu thành công!",_style="color:blue;")
	except Exception, e:
		print e
		return H3(e,_style="color:red;")
	
@auth.requires(auth.has_membership(role='admin'))	
def year_field():
	tablename = request.vars.tablename
	if not tablename: return INPUT(_name="year_field",_value="",_class="string form-control")
	try:
		table = Process.cms.define_table(tablename)
		ops = []
		v = ""
		for field in table.fields:
			if (field !="id")&(table[field].type in ["date","datetime","integer"]): 
				ops += [OPTION(field,_value=field, _selected=(field==v))]
		select = SELECT([""]+ops,_name="year_field",_class="generic-widget form-control")
		return select	
	except Exception, e:
		return e
		
@auth.requires_login()	
def menu():
	from plugin_process import ProcessModel
	p = ProcessModel()
	procedures = p.define_procedures()
	process = p.define_process()
	menu = [(T("Create new process"),URL(f='processcrud'),"fa-plus-circle",[])]
	menu += [(T("Add Edit process"),URL(f='processcrud',args=["edit"]),"fa-plus-circle",[])]
	menu += [(T("Add Delete process"),URL(f='processcrud',args=["delete"]),"fa-plus-circle",[])]
	menu += [(T("Add Publish process"),URL(f='processcrud',args=["publish"]),"fa-plus-circle",[])]
	menu += [(T("Add Unpublished process"),URL(f='processcrud',args=["unpublish"]),"fa-plus-circle",[])]
	
	menus = [(B(T("Create new procedures"),_class="procedures"),URL(f='procedures'),"fa-plus-square",menu)]	
	rows = db(procedures).select(orderby=procedures.display_order)
	for row in rows:
		rs = db(process.procedures==row.id).select(orderby=process.display_order)
		menu = [(T("Create new process"),URL(f='processcrud',vars=dict(procedures=row.id)),"fa-plus-circle",[])]
		menu.append((T("Copy procedure"),URL(f='pcopy',args=[row.id]),"fa-arrow-circle-right",[]))
		for r in rs:
			menu.append((I(T(r.label or r.name),_class="process"),URL(f='processcrud',args=[r.id]),"fa-arrow-circle-right",[]))
		menus += [(B(T(row.label or row.name),_class="procedures"),URL(f='procedures',args=[row.id]),"fa-plus-square",menu)]
	from bootrap import Menu
	content = Menu().vertical(menus)		
	return content
	
@auth.requires_login()	
def menu_procedures():
	procedures = Process.define_procedures()
	process = Process.define_process()
	folder = Process.cms.define_folder()
	row = db(procedures.name==Process.procedure_name).select(orderby=procedures.display_order).first()
	menu = Process.menu(row.folder_parent,folders=[],c=row.controller,a_class_deep="sf_",icon_class="fa-folder-open",ul_class_1="sf-menu sf-vertical")
	return menu
	
	
@auth.requires_login()	
def load_process():
	id,object_id = request.args(0),request.args(1) 
	groups = request.vars.groups or []
	if isinstance(groups,str): groups = [groups]
	users = request.vars.users or []
	if isinstance(users,str): users = [users]
	process_run(id,object_id,groups,users)
	return T('Successfully sent')


	
	
##########################################################
### New update 18/3/2013
##########################################################	

def widget_access():
	from plugin_app import input_option
	id = request.vars.procedures 
	query = (db.process.procedures==request.vars.procedures) 
	widget = input_option('process', type='checkbox', query=query, keyname='paccess')
	return widget
	
##########################################################
### New update 21/3/2013
##########################################################	

def load_group():
	def get_parent(id):	
		parent = id
		row = db.auth_group(parent)
		while row:
			if row.type=='group': break
			parent = row.parent
			row = db.auth_group(parent)
		return parent	
	
	if request.vars.process_address=='': return ''
	from plugin_process import define_process_address
	pa = define_process_address(db,auth)
	row = pa(int(request.vars.process_address))
	list_id = row.auth_group if row else []
	i = 1
	tr = TR()		
	tmp = SPAN()
	rows = db(db.auth_group.id.belongs(list_id)).select(orderby=db.auth_group.parent|db.auth_group.position|db.auth_group.role)
	parent = None
	for row in rows:
		if (row.type in ['group','group_org']): pass
		else:
			input = SPAN(i if i>9 else '0%s'%i,INPUT(_type='checkbox',_name='auth_group',_class='auth_group',_value=row.id,_checked=True if request.vars.check_all else False),row.role,BR())
			if parent != row.parent: 
				input = SPAN(B(db.auth_group(row.parent).role),BR(),input)
			parent = row.parent
			tmp.append(input)
			if i%10==0: 
				tr.append(TD(tmp))
				tmp = SPAN()
			i+=1
	tr.append(TD(tmp))	
	return TABLE(tr)
	
def save_group():
	from plugin_process import define_process_address
	pa = define_process_address(db,auth)
	if request.vars.address_book=='': 
		if request.vars.process_address!='':
			db(pa.id==int(request.vars.process_address)).update(auth_group=request.vars.auth_group,process=request.vars.process)
			script='alert("Đã cập nhật thành công!");'
		else: script='alert("Chưa nhập tên danh bạ!");'
	else:
		pa.update_or_insert(name=request.vars.address_book,auth_group=request.vars.auth_group,process=request.vars.process)
		script='alert("Thêm mới danh bạ thành công!");'
	script = SCRIPT(script)
	return script
	
def tree_group():
	def process_check():
		rows = db(db.procedures.id>0).select()
		tr = TR()
		for row in rows:
			rs = db(db.process.procedures==row.id).select()
			td = TD(B(row.name),BR())
			add = False
			for r in rs: 
				try: settings=eval(r.setting.replace(chr(13),''))
				except: settings={}
				if settings.get('address',False): 
					td.append(SPAN(INPUT(_type='checkbox',_name='process',_value=r.id,_checked=True),r.name,BR()))
					add = True
			if add: tr.append(td)		
		return SPAN(H5('Được dùng trong các chức năng:'),TABLE(tr))
		
	def parents(id):
		ids = []
		parent = db.auth_group(id).parent
		while parent:
			ids.append(parent)
			parent = db.auth_group(parent).parent
		return ids
		
	selected = []
	script, ex = '', ''
	rows = db(db.auth_group.parent==None).select()
	for row in rows:	
		script += '$("#expand_all_%s").click();'%row.id
		ex += '<div id="auth_group%s_control"><a href="?#"></a><a href="?#" id="expand_all_%s"></a></div>'%(row.id,row.id)
	if request.vars.auth_group:
		groups = [request.vars.auth_group] if isinstance(request.vars.auth_group,str) else request.vars.auth_group
		for id in groups: 
			id = int(id)
			selected.append(id)
			list_parent = parents(id)
			list_parent.reverse()
			for parent in list_parent:
				script += '''if($('#checkbox_%s').length == 0) {$('#parent_%s').click();setTimeout(function(){$('#checkbox_%s').prop('checked', true);},500);}'''%(id,parent,id)
			script += '''$('#checkbox_%s').prop('checked', true);'''%id
	script = SCRIPT(script)
	process = db.process(plugin_process.process)
	vars=request.vars
	if vars.process: del vars['process']
	if vars.auth_group: del vars['auth_group']
	ajax = "ajax('%s', ['address_book','auth_group','process','process_address'], 'script')"%(URL(f='save_group',args=request.args,vars=vars))
	address_input = SPAN(process_check(),B('Nhập tên danh bạ '),INPUT(_name='address_book',_id='address_book'),' ',INPUT(_type='button',_value=T('Submit'),_onclick=ajax),_id='address_book')
	tree = plugin_process.get_tree(process,selected,None)
	return SPAN(XML(ex),tree,address_input,script,DIV(_id='script'))

##########################################################
# Xử lý hình ảnh trong bài viết
	
# Lấy ảnh đầu tiên trong bài viết làm ảnh đại diện.

def update_imageURL_in_content(table,id):	
	if request.vars.htmlcontent:
		row= table(id)
		new_content= row.htmlcontent
		link =''
		content = new_content.replace(' ', '')
		
		n1 = content.find('<img')
		if n1>-1: 
			n1 = content.find('src=', n1)
			if n1>-1: 
				n1 = content.find('"', n1)
				if n1>-1:
					n1+=1
					n2 = content.find('"', n1)
					link = content[n1:n2]
				else:
					n1 = content.find("'", n1)
					if n1>-1:
						n1+=1
						n2 = content.find("'", n1)
						link = content[n1:n2]	
		if (link <>'') & (link[0:7] <> 'http://'):
			ns = link.split('/')
			link = ns[len(ns)-1]
		if link:
			url = request.folder + '/static/uploads/ckeditor/%s'%(link) 
			url1 = request.folder + '/static/uploads/news/%s'%(link) 
			import os, uuid
			from PIL import Image
			if os.path.exists(url):
				im=Image.open(url)
				im.save(url1,'jpeg')
			row.update_record(avatar=link)
	return 		
	
def save_img(url,filename=None,dir='static/uploads/ckeditor'):
	import urllib
	import os
	path = '%s/%s'%(request.folder,dir)
	if not os.path.exists(path): os.makedirs(path)
	filename = filename or url.split('/')[-1]
	while os.path.exists('%s/%s/%s'%(request.folder,dir,filename)): 
		filename = '1_%s'%filename
	urllib.urlretrieve(url, '%s/%s'%(path,filename))
	try:
		i_url = "%s/%s"%(path,filename)
		if setting_config('add_logo',False):
			import uuid
			from PIL import Image
			if os.path.exists(i_url):
				# size=(800,600)
				im=Image.open(i_url)
				im=add_logo(im)
				# im.thumbnail(size,Image.ANTIALIAS)
				im.save(i_url,'jpeg')
	except Exception, e:
		print 'save_img --> ',e
	return "/%s/%s/%s"%(request.application,dir,filename)

def change_img(html):
	from bs4 import BeautifulSoup
	soup = BeautifulSoup(html)
	# return html
	imgs = []
	dir = 'static/site/'+site_name+'/uploads/ckeditor'
	for link in soup.find_all('img'):
		url = link.get('src')
		
		try:
			path = save_img(url,dir=dir)
			link['src']=path
		except Exception, e:
			print e
			pass
	for img in imgs: html = html.replace(img[0],img[1])		
	return soup.prettify().replace('<html>','').replace('</html>','')
	
def size_img(row,tablename):
	value = row.avatar
	url = None
	if not value[0:5]=='http:': url = request.folder + '/static/site/'+site_name+'/uploads/%s/%s'%(tablename,value) 
	if url:
		import os, uuid
		from PIL import Image
		size=(800,600)
		extension = url.split('.')[-1].lower()
		if extension=="jpeg":
			if os.path.exists(url):
				im=Image.open(url)
				# im=add_logo(im)
				im.thumbnail(size,Image.ANTIALIAS)
				im.save(url,'jpeg')
	return ''
	
def add_logo(img):
	if setting_config('add_logo',False):
		import os, uuid
		from PIL import Image
		logo = request.folder + '/static/logo.png'
		im1=Image.open(logo)
		rgba_logo = im1.convert('RGBA')  
		img.paste(rgba_logo,(10,10),rgba_logo)
	return img
	
def centeredCrop(img, new_height, new_width):
	half_the_width = img.size[0] / 2
	half_the_height = img.size[1] / 2
	img4 = img.crop((half_the_width - (new_width/2),half_the_height - (new_height/2),half_the_width + (new_width/2),half_the_height + (new_height/2)))
	return img4
	



def report():
	from plugin_app import select_option
	from plugin_process import Process
	process = Process()
	widget = DIV( process.cms.list_folder(),_style='with:30%; float:left;')
	
	div = DIV(_class="panel panel-default")
	heading = DIV(_class='panel-heading')
	heading.append(H4('Tạo báo cáo',_class='panel-title'))
	div.append(heading)
	
	wr_search = DIV(widget)
	div_time = DIV(_class='input-group',_style="width: 40%;float: left;")
	div_time.append(SPAN('Từ ngày ',_class="input-group-addon"))
	div_time.append(INPUT(_name='startday',_type='text',_class='form-control date'))
	div_time.append(SPAN(' đến ngày ',_class="input-group-addon"))
	div_time.append(INPUT(_name='endday',_type='text',_class='form-control date'))
	wr_search.append(div_time)
	ajax = "ajax('%s', ['list_folder','startday','endday'], 'content_report')"%(URL(r=request,c='plugin_public',f='act_report'))
	wr_search.append(A('Lọc dữ liệu',_onclick=ajax,_class='btn btn-primary'))
	
	content = DIV(wr_search,_class='panel-body')
	content.append(DIV(_id='content_report'))
	div.append(content)
	response.view = 'plugin_process/report.html'	
	return dict(content=div)
	
def act_report():
	from plugin_cms import CmsFolder,CmsModel
	db = CmsModel().db
	folders = CmsFolder().get_folders(request.vars.list_folder)
	dcontent = CmsModel().define_dcontent()
	query = dcontent.folder.belongs(folders)
	if request.vars.startday:
		query &= dcontent.publish_on>=request.vars.startday
	if request.vars.endday:
		query &= dcontent.publish_on<=request.vars.endday
	rows  = db(query).select()
	table = TABLE(_class='table',_id="table2excel")
	table.append(TR(TH('Stt'),TH('Ngày xuất bản'),TH('Tiêu đề')))
	i = 1
	for row in rows:
		table.append(TR(TD(i),TD(row.publish_on.strftime("%d/%m/%Y")),TD(row.name)))
		i+=1
	div = DIV(H4('Có tổng %s bản ghi'%(len(rows))))
	div.append(table)
	content = DIV(A('Xuất Excel',_id='export_excel',_class='btn btn-primary'))
	content.append(div)
	scr ='''
	<script>
		$("#export_excel").click(function(){
			$("#table2excel").table2excel({
				exclude: ".noExl",
				name: "Excel Document Name"

			});
		});

	</script>
	'''
	content.append(XML(scr))
	return content
	

def mail():
	content = TABLE(_style="width:100%;")

	content.append(TR(TD(INPUT(_type='text',_name='you_email',_id='you_email',_class='form-control string',_placeholder="Email của bạn"),_style='padding:5px 0;')))
	content.append(TR(TD(INPUT(_type='text',_name='you_name',_id='you_name',_class='form-control string',_placeholder="Tên của bạn"),_style='padding:5px 0;')))
	content.append(TR(TD(INPUT(_type='text',_name='send_to',_id='send_to',_class='form-control string',_placeholder="Email người nhận"),_style='padding:5px 0;')))
	content.append(TR(TD(TEXTAREA(_name='message',_cols="40",_placeholder="Lời nhắn",_style="height: 100px; width:100%;"),_class='message',_style='padding:5px 0;')))
	ajax = "ajax('%s', ['you_email','you_name','send_to','message'], 'window_sendmail')"%(URL(f='sendmail',args=request.args,vars=request.vars))
	content.append(TR(TD(INPUT(_type='button',_value=T(' Gửi '),_class='btn btn-primary',_onclick=ajax),INPUT(_type='button',_class='btn btn-default',_value=T(' Đóng '),_onclick='window.parent.close()'),_style="text-align: center;")))
	h2 = H2(T('Chia sẻ qua email'),_style=" background: #158BD5; height: 40px; line-height: 40px; color: #fff; text-align: center; text-transform: uppercase; margin:5px 0; ",_class='title')
	content = DIV(h2,content,_id='window_sendmail',_class='col-sm-12')
	return dict(content=content)

def sendmail():
	you_email = request.vars.you_email.replace(' ','')
	you_name  = request.vars.you_name
	send_to   = request.vars.send_to.replace(' ','')
	send_to   = send_to.replace(';',',')
	send_to   = send_to.split(',')
	message   = request.vars.message
	subject   = you_name +' đã chia sẻ với bạn:'
	url = 'http://'+request.env.http_host + str(URL(r=request.r,c='portal',f='read',args=request.args))
	mailto = "mailto:"+ you_email
	content   = you_name+'<'+str(A(you_email,_href=mailto))+'>' +' đã chia sẻ với bạn 1 bài viết tại' + str(A('đây',_href=url)) + '.<br/> Với lời nhắn: <br/>' + message
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Process execute and send mail successfully')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Send mail error')),XML(scr),_class='notice')
	return div


def add_on():
	scr = '''
		<script type="text/javascript">
		var min=8;
		var max=38;
		function zoominLetter() {
				var s = parseInt($("#object_table_content").css("font-size").replace("px",""));
				if (s!=max){ s+=1}
				setCookie('font_size_content',s,365);
				$("#object_table_content").css({'font-size':s+"px"});
			
		  
		}
		function zoomoutLetter() {
		  var s = parseInt($("#object_table_content").css("font-size").replace("px",""));
				if (s!=min){
				s-=1
				}
				setCookie('font_size_content',s,365);
				$("#object_table_content").css({'font-size':s+"px"});
		}
		function setCookie(cname, cvalue, exdays) {
				var d = new Date();
				d.setTime(d.getTime() + (exdays*24*60*60*1000));
				var expires = "expires="+d.toUTCString();
				document.cookie = cname + "=" + cvalue + "; " + expires;
			}

		function getCookie(cname) {
			var name = cname + "=";
			var ca = document.cookie.split(';');
			for(var i = 0; i < ca.length; i++) {
			var c = ca[i];
			while (c.charAt(0) == ' ') {
			c = c.substring(1);
			}
			if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
			}
			}
			return "";
		}
	
		$(document).ready(function() {
			if (getCookie("font_size_content") !=''){ $("#object_table_content").css({'font-size':getCookie("font_size_content")+"px"});}
			else {setCookie('font_size_content',15,365);}
			
			$("#simplePrint").click(function(){
				$('#object_table_content').printElement();
			});
		   
			
        });
		</script>
	'''
	div = DIV(_id='add_on')
	div.append(XML(scr))
	compose = 'window.open("%s","%s","width=600,height=400,toolbar=no,location=no,directories=no,status=no,menubar=no,left=400,top=200")'%(URL(c='news',f='mail.html',args=request.args,vars=request.vars),T('Send email'))
	div.append(A(T('Email'),_onclick=compose ,_title='Chia sẻ qua email',_id="email"))
	div.append(A(T('Print') ,_title='In bài viết',_id="simplePrint"))
	div.append(A(T('A'),_href="javascript:zoominLetter();" ,_title='Tăng phông chữ (Việc tăng này sẽ được lưu trên máy tính của bạn)',_id='zoominLetter'))
	div.append(A(T('a'),_href="javascript:zoomoutLetter();" ,_title='Giảm phông chữ (Việc giảm này sẽ được lưu trên máy tính của bạn)',_id='zoomoutLetter'))
	
	return div
	
	

def update_meta():
	from plugin_cms import CmsFolder,CmsModel
	from plugin_cms import CmsPublish
	from plugin_process import Process
	cms = CmsPublish()
	process = Process()
	
	db = CmsModel().db
	folders = CmsFolder().get_folders(request.vars.list_folder)
	dcontent = CmsModel().define_dcontent()
	objects = process.define_objects()
	o = objects(request.args(4)) 
	row = db((dcontent.dtable==o.tablename)&(dcontent.table_id==o.table_id)).select().first()
	
	if not row:
		return ''
	form = TABLE(_class='table table-striped defview',_id='update_meta')

	form.append(TR(TD(T("Metadate: Title"),SPAN(_id="title_number_key",_class="pull-right")),TD(INPUT(_name='meta_title',_class="string form-control",_id='ip_title_page',_value=row.meta_title))))
	form.append(TR(TD(T("Metadate: Description"),SPAN(_id="description_number_key",_class="pull-right")),TD(INPUT(_name='meta_description',_class="string form-control",_id='ip_description_page',_value=row.meta_description))))
	form.append(TR(TD(T("Metadate: Keywords")),TD(INPUT(_name='meta_keywords',_class="text form-control",_value=row.meta_keywords))))
	ajax = "ajax('%s', ['meta_title','meta_description','meta_keywords'], 'update_meta')"%(URL(f='act_update_meta',args=request.args))
	form.append(TR(TD(),TD(INPUT(_type="button",_value=T("Submit"),_class='btn btn-primary',_onclick=ajax),A(T("Đóng"),_class='btn btn-default',**{"_data-dismiss":"modal"}))))
	
	scr = '''
	<script type="text/javascript">
		$('#ip_title_page').bind('input', function() {
			ar = $(this).val().length
			div = document.getElementById('title_number_key');
			if (ar <60) {
				div.innerHTML = "<span class='ms_xanh'>"+ar+"</span>" ;
			}
			else if (ar<80) {
				div.innerHTML = "<span class='ms_vang'>"+ar+"</span>" ;
			}
			else {
				div.innerHTML = "<span class='ms_do'>"+ar+"</span>" ;
			}
		});
		
		$('#ip_description_page').bind('input', function() {
			ar1 = $(this).val().length
			div = document.getElementById('description_number_key');
			if (ar1 >70 && ar1 <160) {
				div.innerHTML = "<span class='ms_xanh'>"+ar1+"</span>" ;
			}
			
			else {
				div.innerHTML = "<span class='ms_do'>"+ar1+"</span>" ;
			}
		});
	</script>
	'''
	form.append(XML(scr))
	
	
	return form
	
def act_update_meta():
	from plugin_cms import CmsFolder,CmsModel
	from plugin_cms import CmsPublish
	from plugin_process import Process
	cms = CmsPublish()
	process = Process()
	objects = process.define_objects()
	o = objects(request.args(4)) 
	
	db = CmsModel().db
	dcontent = CmsModel().define_dcontent()
	table = cms.define_table(o.tablename)
	
	
	
	meta_title = request.vars.meta_title
	meta_description = request.vars.meta_description
	meta_keywords = request.vars.meta_keywords
	
	cms.update_meta(o.tablename,o.table_id,meta_title,meta_description,meta_keywords)
	# row = db(table.id==o.table_id).select().first()
	# if row.avatar:
		# cms.update_davatar(o.tablename,o.table_id,row.avatar)
	
	return update_meta()

		