# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 04/09/2015
# Version 0.2 Date: 15/09/2015
###################################################

FILTERMENU = [] #[("thuyetminh","Chờ duyệt TM"),("duocduyet","Duyệt thuyết minh"),("nghiemthu1","Giai đoạn 1"),("nghiemthu2","Kết thúc")]

fADD = ("medit","fa fa-plus-circle fa-fw","Add new")
fEDIT = ("medit","fa fa-edit fa-fw","Edit")
fDELETE = ("mdelete","fa fa-trash-o fa-fw","Delete")
fDELETECHECK = ("cdelete","fa fa-trash-o fa-fw","Delete")

BUTTONS = []

from bootrap import Modals
from plugin_table import DataTable
data = DataTable(buttons=BUTTONS)
	
@auth.requires_login()	
def index():
	content = H2("Plugin Table")
	if request.vars.e:
		content.append(H3(request.vars.e,_style="color:red"))
	return dict(content=content)

def toolbars():
	content = SPAN(_id='toolbars-table')
	for f in [fADD]:
		label = SPAN(I(_class=f[1]),T(f[2]))
		button = Modals(caption = (BUTTON(label,_class='btn btn-default')),source=URL(r=request,f=f[0],args=[data.tablename],vars=request.vars),reload=True)
		content.append(button)
	if data.id:
		for f in [fEDIT,fDELETE]:
			label = SPAN(I(_class=f[1]),T(f[2]))
			button = Modals(caption = (BUTTON(label,_class='btn btn-default')),source=URL(r=request,f=f[0],args=request.vars,vars=request.vars),reload=True)
			content.append(button)
	else:
		for f in [fDELETECHECK]:
			label = SPAN(I(_class=f[1]),SPAN(T(f[2])))
			button = A(label,_href="#",_class='btn btn-default confirm',_id=f[0],_onclick="btnclick('%s');"%f[0])
			content.append(button)			
	return content

def filter():
	SEARCHPREFIX = "search__"
	vars = {}
	for key in request.vars.keys(): 
		if not key.startswith(SEARCHPREFIX): vars[key]=request.vars[key]
	content = UL(_id='filter-table',_class='nav nav-tabs')
	i = 1
	for f in FILTERMENU:
		label = SPAN(T(f[1]))
		button = A(label,_href='#',_class='btn btn-default button_process_%s'%(False),_id='process_%s'%i)		
		vars["statusp"] = f[0]
		url = URL(r=request,f='explorer',args=[data.tablename],vars=vars)
		cls ='nav_item active' if f[0]==request.vars.statusp else 'nav_item'	
		content.append(LI(A(label,_href=url,_id='process_filter',_class='filter_process_selected filter'),_class=cls))
		i+=1
	return content			


def explorer():
	try:
		content = data.explorer()
	except Exception, e:
		content = e
	return dict(content=content)

def read():
	content = data.read()
	return content
	
def delete():
	data.delete()
	return 1	
	
	
@auth.requires_login()	
def edit():

	db = data.cms.db
	tablename = data.tablename
	table_id = data.id
	data.cms.define_dtable()
	dtable = db(db.dtable.name==tablename).select().first()
	if not dtable: return dict(content='Table %s not existe'%tablename)		
	table = data.cms.define_table(tablename)
	if not table: return dict(content='Can not define %s'%tablename)		
	
	form=data.cms.sqlform(tablename,table_id,default=data.default,submit=True)
		
	if form.process().accepted:		
		if dtable.attachment:
			if request.vars.uuid:
				fileupload.update(form.vars.id,request.vars.uuid)
				
	msg = H4(T("Update table" if table_id else "Create table")," ",B(T(dtable.label)),_class="title_edit")
	
	div = DIV(msg,_class='edit',_id='edit_%s'%(tablename))	
	div.append(form)
	# if request.extension=="html":
		# cancel = INPUT(_type='button',_value=T('Cancel'),_onclick='javascript:history.go(-1)',_class='btn btn-default')
	# else:
		# cancel = INPUT(_type='button',_value=T('Cancel'),_class='btn btn-default')
		# cancel["data-dismiss"]="modal"
		# cancel = ""
	# div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),cancel))
	# script = SCRIPT('''$("#act_submit_ao").click(function () {$("#act_submit").trigger('click');});''')
	# div.append(script)
	
	response.view = 'plugin_table/content.%s'%request.extension	
	return dict(content=div)	

def edit_menu(id):	
	ul = UL(_class="nav nav-tabs")
	for f in ["edit","projectwork","projectbudget"]:
		if f == request.function:
			ul.append(LI(A(f,_href="#"),_role="presentation", _class="active"))
		else:
			ul.append(LI(A(f,_href=URL(f=f,args=[id])),_role="presentation"))  
	return ul

def approve():
	content = ""
	response.view = 'plugin_table/content.html'	
	return dict(content=content)
	
	
def folder_menu():
	menu = data.menu_folder()
	menu = SPAN(menu,data.select_year())
	return menu
	

def medit():
	try:
		table = data.cms.define_table(data.tablename)
		form=data.cms.sqlform(data.tablename,data.id,buttons=[],submit="ajax",default=data.default,attachment=True)
		header = H4(T("Update table" if data.id else "Create table")," ",B(T(data.tablename.capitalize())),_class="title_edit")
		header.append(XML('''
<script type="text/javascript">
$(document).ready(function(){
	$(".widget_select2").select2({
		placeholder: "Chọn dữ liệu ...",
		allowClear: true
	});
	$(".widget_multiselect2").select2({
		placeholder: "Chọn dữ liệu ...",
		allowClear: true	
	});	
});
</script>'''))
		content = DIV(header,form)
		return content
	except Exception, e:
		print "medit", e
		return e

		
def medit_update():
	try:
		vars = data.get_vars(request.vars)
		if request.args(0) =='org':
			return 'Khách hàng'
		
		if isinstance(vars,dict):
			if vars == "{}": return H4(T("Không có thông tin!"),_style="color:red;")
			if data.id: data.db(data.table.id==data.id).update(**vars) 
			else: data.id = data.table.insert(**vars)
			if request.vars.uuid:
				from plugin_upload import FileUpload
				fileupload = FileUpload(db=data.db,tablename=data.tablename,table_id=data.id,upload_id=None)
				fileupload.update(data.id,request.vars.uuid)
			return H4(T("Cập nhật thành công!"),_style="color:blue;")
		else:
			return H4(vars,_style="color:red;")
	except Exception, e:
		print e
		return H4(e,_style="color:red;")
		
		
def mdelete():
	try:
		table = data.cms.define_table(data.tablename)
		form=data.read()
		header = H4(T("Delete this record?"),_class="title_edit")
		ajax = "ajax('%s', %s, '')"%(URL(f='mdelete_update',args=request.args,vars=request.vars),[])
		bt = XML('<button type="submit" class="btn btn-primary" data-dismiss="modal" aria-label="Close" onclick="%s"><span aria-hidden="true">%s</span></button>'%(ajax,T('Submit')))
		form.append(bt)
		content = DIV(header,form)
		return content
	except Exception, e:
		print e
		return e
		
def mdelete_update():
	try:
		data.delete(data.id)
	except Exception, e:
		print e

def cdelete():
	try:
		ids = request.vars.ids
		if isinstance(ids,str): ids = [ids]
		ids = [int(id) for id in ids]
		data.db(data.table.id.belongs(ids)).delete()
		return H4(T("Đã xóa dữ liệu lựa chọn!"),_style="color:blue;")
	except Exception, e:
		print e

		
def select2():
	search = request.vars.q
	print request.vars
	rows = data.db(data.table).select()
	return {"a":"xyz"}
	