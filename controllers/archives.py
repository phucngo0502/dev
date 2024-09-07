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
	content = H2('Hệ thống quản trị văn bản')
	response.view = 'archives/content.html'	
	return dict(content=content)
	
def toolbars():	
	content = Process.get_toolbars()
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
	
	from plugin_app import widget_auto_nguoi_ky
	table['user_signed'].widget = widget_auto_nguoi_ky
	from plugin_app import widget_auto_chuc_vu
	table['user_office'].widget = widget_auto_chuc_vu
	from plugin_app import widget_auto_co_quan_ban_hanh
	table['org_publish'].widget = widget_auto_co_quan_ban_hanh
				
	form=Process.cms.sqlform(tablename,table_id,default_show={'daystart':request.now})
	
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
		
	div = DIV(H3(msg,_class='title_box'),form,_class='def_edit ',_id='add_%s'%(tablename))
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
		redirect(URL(c='archives',f='explorer.html',args=request.args[:3]),client_side=True)
	response.view = 'archives/content.html'	
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
	redirect(URL(c='archives',f='explorer.html',args=request.args[:3]),client_side=True)

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
	
	
	