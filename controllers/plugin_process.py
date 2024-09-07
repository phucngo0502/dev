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
	redirect(URL(c='plugin_process',f='procedures'))
	response.view = 'plugin_process/content.html'	
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
	
# @auth.requires(auth.has_membership(role='admin') or (auth.has_permission('create', 'folder') or auth.has_permission('edit', 'folder')))	
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
	
	if dtable.link_edit: 
		from plugin_app import get_url
		c,f,e=get_url(dtable.link_edit)
		redirect(URL(c=c,f=f,extension=e,args=request.args,vars=request.vars))
	
	form=Process.cms.sqlform(tablename,table_id)
	
	if dtable.attachment: 
		if not table_id: 
			if not request.vars.uuid:
				import uuid
				redirect(URL(args=request.args,vars=dict(uuid=uuid.uuid1().int)))

		from plugin_upload import FileUpload
		fileupload = FileUpload(db=db,tablename=tablename,table_id=table_id or request.vars.uuid,upload_id=None)
		upload = fileupload.formupload(colorbox=False)
	else: 
		upload = ''

	form[0][-1].append(TR(TD(),TD(INPUT(_type='submit',_value=T('Submit'),_style="display: none;",_id='act_submit'))))
	
	if form.process().accepted:
		
		#update_imageURL_in_content(table,form.vars.id)
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
		args = request.args[:4]
		args[2] = db.folder(form.vars.folder).name
		cache.ram.clear()
		redirect(URL(f='explorer',args=args))
		
	if table_id:
		msg = T("Update table %s"%tablename)
	else:
		msg = T("Create table %s"%tablename)
		
	div = DIV(H3(msg,_class='title_box'),form,_class='def_edit')
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
	cache.ram.clear()
	redirect(URL(c=Process.c,f='explorer.html',args=request.args[:TABLENAME]))

@auth.requires_login()	
def publish():
	form = TABLE(TR(TD(T("Publish on")),TD(INPUT(_name='publish_on',_value=request.now,_class="datetime"))),_class='table table-striped defview')
	form.append(TR(TD(T("Expired on")),TD(INPUT(_name='expired_on',_class="datetime"))))
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
			publish_on = request.vars.publish_on
			expired_on = request.vars.expired_on
			for id in objects_ids:
				o = objects(id) 
				cms.publish(o.tablename,o.table_id,publish_on,expired_on)
			process.process_group(process_id,objects_ids,[])
		except Exception,e: 
			print e
			pass
		cache.ram.clear()
		redirect(URL(c='plugin_process',f='explorer.html',args=request.args[:3]),client_side=True)
	response.view = 'plugin_process/content.html'	
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
	redirect(URL(c='plugin_process',f='explorer.html',args=request.args[:3]),client_side=True)

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
		setting = {}
		for key in form.vars.keys():
			if key.startswith("setting_"): 
				if form.vars[key]=="on": setting[key[8:]] = True
				elif form.vars[key]=="None": setting[key[8:]] = False
				else: setting[key[8:]] = form.vars[key]
		if table(form.vars.id): table(form.vars.id).update_record(setting=str(setting))	
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


def mail():
	content = TABLE()
	from plugin_process import define_process_email
	define_process_email(db,auth,True)
	rows = db(db.process_email.created_by==auth.user_id).select(db.process_email.email,distinct=True)
	list = '['
	for row in rows:
		temp=''
		temp+='"'+row['email']+'",'
		list+=temp
	list=list[0:len(list)-1]
	list+=']'
	table = TABLE()
	input = TEXTAREA( _id="suggest4", _name="emails")
	script = '''<script type="text/javascript">
				$().ready(function() {
					function formatItem(row) {
						return "<strong>" + row[0] + "</strong>";
					}
					function formatResult(row) {
						return row[0].replace(/(<.+?>)/gi, '');
					}
					$("#suggest4").autocomplete(%s, {
						width: 300,
						multiple: true,
						matchContains: true,
						formatItem: formatItem,
						formatResult: formatResult
					});
				});
				</script>'''%(list)
	content.append(TR(TH(T('To emails')),TD(input,XML(script),_class='send_email')))
	content.append(TR(TH(),TD('Ví dụ: user@hatinh.gov.vn,user@chinhphu.vn')))
	content.append(TR(TH(T('Notes')),TD(TEXTAREA(_name='notes',_cols="30"),_class='notes')))
	content.append(TR(TH(T('Attachment')),TD(INPUT(_type='checkbox',_name='attach',_checked=True))))
	ajax = "ajax('%s', ['emails','notes','attach'], 'window_sendmail')"%(URL(c='plugin_process',f='sendmail',args=request.args,vars=request.vars))
	content.append(TR(TH(),TD(INPUT(_type='button',_value=T('Send'),_onclick=ajax),INPUT(_type='button',_value=T('Close'),_onclick='window.parent.close()'))))
	#response.view = 'plugin_app/content.%s'%request.extension
	h2 = H2(T('Gui email'),_class='title')
	content = DIV(h2,content,_id='window_sendmail')
	return dict(content=content)

def sendmail():
	emails = request.vars.emails.replace(' ','')
	emails = emails.replace(';',',')
	emails = emails.split(',')
	mail = auth.setting_mail()
	object = request.args(0)
	object_id = request.args(1)
	row = db[object](object_id)
	name = row.name
	if 'folder' in db[object].fields: name = row.folder.name +' ' + name
	subject = '[%s] %s'%(db.auth_group(auth.user_org).role, name)
	content = ''
	from plugin_app import get_represent
	for field in db[object].fields:
		if (field <>'id') & (db[object][field].readable==True):		
			content += str(T(db[object][field].label))+': '+get_represent(object,field,row[field])
			content += chr(13)
	# content += url 
	content += chr(13)+chr(13) + 'Với lời nhắn:  '+ request.vars.notes
	attachments = []
	if request.vars.attach:
		from gluon.tools import Mail
		from plugin_attach import Attachment
		attachs = Attachment(object,object_id).files()
		attachments = [Mail.Attachment(file) for file in attachs]
	user = db.auth_user(auth.user_id)
	sender = user.username + '@hatinh.gov.vn'
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=emails,subject=subject,reply_to=sender,message=content,attachments=attachments):
		div = DIV(H2(T('Process execute and send mail successfully')),XML(scr),_class='notice')
		from plugin_process import define_process_email
		table = define_process_email(db,auth)
		o = plugin_process
		attach = request.vars.attach or False
		for email in emails:
			table.insert(email=email,description=request.vars.notes,attach=attach,objects=o.objects.id)
	else: 
		div = DIV(H2(T('Send mail error')),XML(scr),_class='notice')
	return div
	
	
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

def update_imageURL_in_content(table,id):	
	if request.vars.htmlcontent:
		row= table(id)
		if not row.avatar:
			new_content= request.vars.htmlcontent
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
				link = "http://%s/%s/static/uploads/ckeditor/%s"%(request.env.http_host,request.application,link)
			row.update_record(avatar=link)
	return 	
	
	
def send_sms():
	from plugin_process import Process
	process = Process()
	objects = process.define_objects()
	o = objects(request.vars.objects) 
	table = process.cms.define_table(o.tablename)
	row = db(table.id==o.table_id).select().first()
	
	div = DIV(H3('Thông tin lịch hẹn'),_id='wr_send_sms')
	if row:
		table = TABLE(_class='table')
		table.append(TR(TD("Họ tên bệnh nhân"),TD(row.name)))
		table.append(TR(TD("Đặt lịch hẹn với bác sỹ"),TD(row.doctor.name if row.doctor else "")))
		table.append(TR(TD("Thời gian hẹn"),TD(row.start_date.strftime('%d/%m/%Y'))))
		table.append(TR(TD("Lưu ý:"),TD(row.htmlcontent)))
		div.append(table)
	ajax = "ajax('%s', [], 'wr_send_sms')"%(URL(f='act_send_sms',args=[o.tablename,o.table_id],vars=request.vars))
	div.append(DIV(A("Xác nhận và gửi tin nhắn thông báo",_onclick=ajax,_class='btn btn-primary text-center'),_class='text-center'))
	return div
	
def act_send_sms():
	from plugin_sms import MEDIC_SMS
	from plugin_process import Process
	process = Process()
	objects = process.define_objects()
	table = process.cms.define_table('register')
	row = db(table.id==request.args(1)).select().first()
	if row:
		db(objects.id==request.vars.objects).update(process=request.vars.process)
		name = "Bệnh nhân %s đặt lịch khám với %s ngày %s."%(row.name, row.doctor.name,row.start_date.strftime('%d/%m/%Y'))
		params = str([{"NUM":"1","CONTENT":row.name},{"NUM":"2","CONTENT":row.doctor.name},{"NUM":"3","CONTENT":row.start_date.strftime('%d/%m/%Y')}])
		
		from plugin_sms import MEDIC_SMS
		if row.phone1:
			MEDIC_SMS().send(id=1,name=name,params=params,mobilelist=row.phone1,send_end=row.start_date)
		return MEDIC_SMS().send(1,name,params,row.phone,row.start_date)
	return 'Gửi tin nhắn thành công.'
	
def re_send_sms():
	from plugin_process import Process
	process = Process()
	objects = process.define_objects()
	o = objects(request.vars.objects) 
	table = process.cms.define_table(o.tablename)
	row = db(table.id==o.table_id).select().first()
	
	div = DIV(H3('Thông tin lịch hẹn'),_id='wr_send_sms')
	if row:
		table = TABLE(_class='table')
		table.append(TR(TD("Họ tên bệnh nhân"),TD(row.name)))
		table.append(TR(TD("Đặt lịch hẹn với bác sỹ"),TD(row.doctor.name)))
		table.append(TR(TD("Thời gian hẹn"),TD(row.start_date.strftime('%d/%m/%Y'))))
		div.append(table)
	ajax = "ajax('%s', [], 'wr_send_sms')"%(URL(f='re_act_send_sms',args=[o.tablename,o.table_id],vars=request.vars))
	div.append(DIV(A("Xác nhận và gửi tin nhắn thông báo",_onclick=ajax,_class='btn btn-primary text-center'),_class='text-center'))
	return div
	
def re_act_send_sms():
	from plugin_sms import MEDIC_SMS
	from plugin_process import Process
	process = Process()
	objects = process.define_objects()
	table = process.cms.define_table('register')
	row = db(table.id==request.args(1)).select().first()
	if row:
		# db(objects.id==request.vars.objects).update(process=request.vars.process)
		name = "Bệnh nhân %s đặt lịch khám với %s ngày %s."%(row.name, row.doctor.name,row.start_date.strftime('%d/%m/%Y'))
		params = str([{"NUM":"1","CONTENT":row.name},{"NUM":"2","CONTENT":row.doctor.name},{"NUM":"3","CONTENT":row.start_date.strftime('%d/%m/%Y')}])
		
		from plugin_sms import MEDIC_SMS
		if row.phone1:
			MEDIC_SMS().send(id=1,name=name,params=params,mobilelist=row.phone1,send_end=row.start_date)
		return MEDIC_SMS().send(1,name,params,row.phone,row.start_date)
	return 'Gửi tin nhắn thành công.'
	

def img():
	from PIL import Image


	im = Image.open("/home/9014-cmswebna/applications/cms/static/site/vantainamloc/uploads/ckeditor/images.thumb.2fb78f9d-5d2f-494b-8b5f-11b288638802.jpg")
	left = int(im.size[0]/2-224/2)
	upper = int(im.size[1]/2-100/2)
	right = left +224
	lower = upper + 100

	im_cropped = im.crop((left, upper,right,lower))
	return im_cropped

	
	