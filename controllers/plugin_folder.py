###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 1.0 Date: 27/02/2015
###################################################
# -*- coding: utf-8 -*-

FOLDER_PARENT = None

from plugin_folder import Folder
cms.define_folder()
folder = Folder(cms.db,auth,parent=FOLDER_PARENT)

# def copy():
	# start = 170
	# end   = 85
	# db = folder.db
	# rows = db((db.folder.parent==start)).select(orderby=db.folder.display_order)
	# for row in rows:
		# name = 'hoi-dap-%s'%(row.name)
		# db.folder.insert(parent=end,name=name,label=row.label,publish=True,setting="{'TABLES':['hoi_dap']}",layout='view_hoi_dap.html')
	# return 'Ok'
	

@auth.requires_login()		
def index():
	from bootrap import Panel
	p = Panel()
	menu = [(T("Quản lý danh mục"),[DIV(folder.display_tree(),_id="jstree")])]
	content = DIV()
	content.append(DIV(A(SPAN(_class='glyphicon glyphicon-plus'),T(" Create new folder"), _id="create",_class='btn btn-danger', _onclick="add_new('');"),_class='input_news'))
	content.append(p.panel(menu))
	content = DIV(DIV(content,_class='col-lg-3 col-md-3 col-sm-3 col-xs-3',_id='sidebar'))
	
	from plugin_folder import FolderCrud
	folder_crud = FolderCrud(cms.db,auth,parent=FOLDER_PARENT)	
	id = request.args(0)
	form = folder_crud.form_edit(id)
	ajax = "ajax('%s',['name','label','parent','publish','description','display_order','layout','url_link','tables','delete_this_record','folder_top','folder_bottom'],'msg')"%URL(f='update',args=[id] if id else None)
	# form.append(DIV(DIV(_id="msg"),INPUT(_type='button',_value=T('Submit'),_onclick=ajax,_class="btn btn-primary"),_class="col-sm-9 col-sm-offset-3"))
	form = SPAN(H3(T("Update folder" if id else "Create new folder")),form)
	content.append(DIV(DIV(form,_id='event_result'),_class='col-lg-9 col-lg-offset-3 col-md-9 col-md-offset-3 col-sm-9  col-sm-offset-3 col-xs-9 col-xs-offset-3'))
	return dict(content=content)

@auth.requires_login()	
def update_display():
	try:
		db = folder.db
		old_parent = int(request.vars.old_parent)
		parent = int(request.vars.parent)
		new_position = int(request.vars.new_position)
		old_position = int(request.vars.old_position)
		rows = db((db.folder.parent==parent)).select(orderby=db.folder.display_order)
		i = 1
		for row in rows:
			row.update_record(display_order=i)
			i+=1
		if old_parent == parent:		
			rows = db((db.folder.parent==parent)&(db.folder.display_order>old_position)&(db.folder.display_order<=new_position)).select()
			for row in rows:
				row.update_record(display_order=row.display_order-1)
			rows = db((db.folder.parent==parent)&(db.folder.display_order>=new_position)&(db.folder.display_order<old_position)).select()
			for row in rows:
				row.update_record(display_order=row.display_order+1)
		else:
			rows = db((db.folder.parent==parent)&(db.folder.display_order>=new_position)).select()
			for row in rows:
				row.update_record(display_order=row.display_order+1)	
		db(db.folder.id==request.vars.id).update(parent=parent,display_order=new_position)
		return ''	
	except Exception, e:
		return 'Báo lỗi: %s'%e

@auth.requires_login()			
def form():
	try:
		from plugin_folder import FolderCrud
		folder = FolderCrud(cms.db,auth,parent=FOLDER_PARENT)	
		id = request.vars.folder
		form = folder.form(id)
		ajax = "ajax('%s',['name','label','parent','publish','description','display_order','layout','url_link','tables','delete_this_record','folder_top','folder_bottom','avatar','avatar_bg'],'msg')"%URL(f='update',args=[id] if id else None)
		form.append(DIV(DIV(_id="msg"),INPUT(_type='button',_value=T('Submit'),_onclick=ajax,_class="btn btn-primary"),_class="col-sm-9 col-sm-offset-3"))
		form = SPAN(H3(T("Update folder" if id else "Create new folder")),form)
		return form	
	except Exception, e:
		print e
		return e

@auth.requires_login()		
def update():
	try:
		from plugin_folder import FolderCrud
		folder = FolderCrud(cms.db,auth,parent=FOLDER_PARENT)
		id = request.args(0)
		vars = request.vars
		if not request.vars.publish:
			vars['publish'] = False
		folder.update(id,vars)
	except Exception, e:
		print e
		return T("%s"%e)
	if not request.args(0):
		redirect(URL(f="index"),client_side=True)
	elif request.vars.delete_this_record:
		redirect(URL(f="index"),client_side=True)
	return H3(T("Cập nhật thành công!"))
	
	
def copy_folder():
	pr_1 = 231
	pr_2 = 274
	db = folder.db
	# rows = db((db.folder.parent==pr_1)).select(orderby=db.folder.display_order)
	rows = db((db.folder.parent==pr_2)).select(orderby=db.folder.display_order)
	for row in rows:
		db(db.folder.id==row.id).update(layout='tin_tuc_tailieu_pa.html')
	# for row in rows:
		# db.folder.insert(parent=pr_2,name=row.name.replace('tai-lieu-','tl-hoi-thao-dieu-duong-'),label=row.label, publish=True, setting=row.setting, layout=row.layout)
	return rows
