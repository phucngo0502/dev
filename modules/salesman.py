# -*- coding: utf-8 -*-
###################################################
# This file was developed by AnhNT
# CREATED_ON:11/09/2021
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
from plugin_process import ProcessCms	
	
class Salesman(ProcessCms):
	#############################################
	##Quản lý Đại lý
	#############################################
	
	##Màn hình danh sách đại lý
	def list_salesman(self,page):
		db = self.db
		request = current.request
		T = current.T
		auth = self.auth
		
		from datatables import define_salesman
		define_salesman(db, False)
		from bootrap import Modals
		##Tìm kiếm theo các tiêu chí
		inpcode = INPUT(_type='text',_class='form-control',_name='name_code')#Mã giới thiệu
		labelcode = LABEL('Mã giới thiệu')
		divcode = DIV(labelcode,inpcode,_class='form-group')
		
		inpname = INPUT(_type='text',_class='form-control',_name='name') #Họ tên
		labelname = LABEL('Họ tên')
		divname = DIV(labelname,inpname,_class='form-group')
		
		selectsex = SELECT(_name='sex',_class='form-control') #Giới tính
		list_sex =['sex_male','sex_female']
		for r in list_sex:
			selectsex.append(OPTION(T(r),_value=T(r)))
		labelsex = LABEL('Giới tính')
		divsex = DIV(labelsex,selectsex,_class='form-group')	
		
		# selectstatus = SELECT(_name='fstatus',_class='form-control') #Trạng thái
		# list_status =['Is_True','Is_False']
		# for r in list_status:
			# selectstatus.append(OPTION(T(r),_value=T(r)))
		# labelstatus = LABEL('Trạng thái')
		# divstatus = DIV(labelstatus,selectstatus,_class='form-group')	
		
			
		# inpaddress = INPUT(_type='text',_class='form-control',_name='faddress') #Địa chỉ
		# labeladdress = LABEL('Địa chỉ')
		# divaddress = DIV(labeladdress,inpaddress,_class='form-group')
		
		table = TABLE(_class='table table-hover')
		table.append(TR(TD(divcode),TD(divname),TD(divsex)))
		
		#Tìm kiếm
		urlsea = URL(r=request,c='naso',f='search_salesman')	
		ajax = "ajax('%s', ['fcode','ffullname','fsex','faddress','fstatus'], 'content_student')"%(urlsea)
		btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Tìm kiếm',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		#Thêm mới
		urladd = URL(r=request,c='plugin_student',f='form_student')
		# btnadd = A(SPAN(SPAN(_class='fa fa-plus-circle')," Thêm bệnh nhân" ,_class="btn btn-success"),_href=urladd)
		xbtnadd = SPAN(SPAN(_class='fa fa-plus-circle')," Thêm mới" ,_class="btn btn-success",_title="Thêm mới học sinh")
		btnadd = Modals(caption=(xbtnadd),source=urladd,id='modals-addpatient')	
		# btnadd = A(xbtnadd,_href=urladd,id='modals-addpatient')	
				
		divhd = DIV()
		divhd.append(table)
		divhd.append(DIV(btnadd,btnsearch,_class='list-control'))
		script_cl = SCRIPT('''$('#btn-firstcl').click();''')
		divhd.append(script_cl)
		
		divhd.append(DIV(self.write_table_salesman('','','','',0),_id='content_student'))
		return divhd

	
	def write_table_salesman(self,code,fullname,sex,address,page,status=True):
		db = self.db
		request = current.request
		T = current.T
		auth = self.auth
		from datatables import define_salesman
		define_salesman(db, False)
		import datetime
		today = request.now
		
		query = db.salesman.id>0
		if code!='':
			query&= db.salesman.name_code==code
		if fullname!='':
			query&= db.salesman.name.like('%'+fullname+'%')
		# if sex!='Tất cả':
			# query&= db.salesman.sex==sex
		# if address!='':
			# query&= db.salesman.address.like('%'+address+'%')
		# if status:
			# query&= db.salesman.aactive==True
		# else:
			# query&= db.salesman.aactive==False		
			
		##Phân trang
		LEN_PAGE = 20
		start = 0
		end = 10
		page = int(page)
		if (page!=0):
			end = page*LEN_PAGE
			start = end-LEN_PAGE
		len = db(query).count()
		numbers = (len/LEN_PAGE)
		if len%LEN_PAGE>0:
			numbers = numbers + 1
		ul = UL(_class='page-ul pagination pull-right',_style='margin:0px;')
		i=1
		vars = request.vars
		while i<=numbers:
			vars['page']=i
			url = URL(r=request, vars=vars)
			ajax = "ajax('%s',[],'patient_page')"%(url)
			if (i-page<15):
				if i==page:
					ul.append(LI(A(i,_onClick=ajax,_style='border-radius:50%;'),_class='active'))
				else:
					ul.append(LI(A(i,_onClick=ajax,_style='border-radius:50%;')))			
			i+=1
		rows = db(query).select(limitby=(start,end))
		table = self.table_salesman(rows,page)
		div= DIV(_id="patient_page")	
		coupatien = db(query).count()	
		divcount = DIV(SPAN('Có tổng số: ',coupatien, ' đại lý',_class='pull-right cou-patient'))
		div.append(divcount)
		div.append(table)
		div.append(ul)
		return div
		
	##Bảng danh sách thông tin  
	def table_salesman(self,rows,page=0):
		db = self.db
		request = current.request
		T = current.T
		auth = self.auth
		
		from datatables import define_salesman
		define_salesman(db, False)
		import datetime
		from bootrap import Modals
		
		table = TABLE(_class='table table-bordered table-center')
		table.append(THEAD(TR(TH('STT'),TH('Mã giới thiệu'),TH('Họ tên'),TH('Giới tính'),TH('Ngày sinh'),TH('Chức năng'))))
		tbody = TBODY()
		i = 1
		if page >1:
			i = ((page-1)*20)+1
		for r in rows:
			tr = TR()
			tr.append(TD(i))
			tr.append(TD(r.name_code if r.name_code else ''))
			tr.append(TD(r.name if r.name else '')) 
			tr.append(TD(T(r.sex if r.sex else '')))
			tr.append(TD(r.birthday.strftime('%d/%m/%Y') if r.birthday else ''))
			
			urlupdate_pass = URL(r=request,c='plugin_student',f='update_pass_student',vars=dict(id=r.id))
			xinpupdate_pass = BUTTON(SPAN(_class='fa fa-cogs'),_class='btn btn-warning circle removeid')
			inpeupdate_pass = Modals(caption=(xinpupdate_pass),source=urlupdate_pass,id='modals-pass'+str(i))	
			
			urledit = URL(r=request,c='plugin_student',f='form_student',vars=dict(id=r.id))
			xinpedit = BUTTON(SPAN(_class='fa fa-edit'),_class='btn btn-primary circle removeid')
			inpedit = Modals(caption=(xinpedit),source=urledit,id='modals-edit'+str(i))	
			
			urldelete = URL(r=request,c='plugin_student',f='delete_student',vars=dict(id=r.id))
			inpremove = A(BUTTON(SPAN(_class='fa fa-flag'),_class='btn btn-danger circle'),_href=urldelete,_onclick="return confirmDelete()",_title='Thay đổi trạng thái')
			tr.append(TD(SPAN(inpeupdate_pass),' ',SPAN(inpedit),' ',SPAN(inpremove)))
			# tr.append(TD(SPAN(inpedit)))
			tbody.append(tr)
			i+=1
		table.append(tbody)
		##Xóa hết ID khi bật modals
		scr = SCRIPT('''$('.removeid').click(function(){
				$('#div_create_patient').find('input[type="submit"]').removeAttr('id');
				});''')
		table.append(TR(TD(scr,_style='display:none;')))
		return table
	
	# ##Form Học sinh
	# def form_student(self,id):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_student,define_course
		# define_student(db, False)
		# define_course(db, False)
		
		# row = db.student(id)
		
		# table = TABLE(_class='table table-striple table-left')
		# inpname = INPUT(_type='text',_class='form-control',_id='fullname',_name='fullname',_value=row.fullname if row else '') #Họ tên
		# labelname = LABEL('Họ tên học sinh (*)')
		# divname = DIV(labelname,inpname,_class='form-group')
		
		# birthday = ''
		# if row:
			# birthday = row.birthday.strftime('%d/%m/%Y') if row.birthday else ''
		# inpbirthday = INPUT(_type='text',_class='form-control datepicker',_id='birthday',_name='birthday',_value=birthday) #Ngày sinh
		# labelbirthday = LABEL('Ngày sinh (*)')
		# divbirthday = DIV(labelbirthday,inpbirthday,_class='form-group')
		
		# selectsex = SELECT(_name='sex',_class='form-control') #Giới tính
		# list_sex =['Nam','Nữ']
		# for r in list_sex:
			# if row:
				# if row.sex==r:
					# selectsex.append(OPTION(T(r),_value=r,_selected='selected'))
				# else:
					# selectsex.append(OPTION(T(r),_value=r))
			# else:
				# selectsex.append(OPTION(T(r),_value=r))
		# labelsex = LABEL('Giới tính')
		# divsex = DIV(labelsex,selectsex,_class='form-group')	

		# ##Khóa học
		# list_course = db(db.course.id>0).select()
		# selectcou = SELECT(_name='course',_class='form-control') #Giới tính
		# for r in list_course:
			# if row:
				# if row.course:
					# if int(row.course)==r.id:
						# selectcou.append(OPTION(r.name,_value=r.id,_selected=True))
					# else:
						# selectcou.append(OPTION(r.name,_value=r.id))
			# else:
				# if r.id==2:
					# selectcou.append(OPTION(r.name,_value=r.id,_selected=True))
				# else:
					# selectcou.append(OPTION(r.name,_value=r.id))
		# labelcou = LABEL('Niên khóa')
		# divcou = DIV(labelcou,selectcou,_class='form-group')
				
		# inpaddress = INPUT(_type='text',_class='form-control',_name='address',_value=row.address if row else '') #Địa chỉ
		# labeladdress = LABEL('Địa chỉ')
		# divaddress = DIV(labeladdress,inpaddress,_class='form-group')	
		
		# inpbo = INPUT(_type='text',_class='form-control',_id='dad_name',_name='dad_name',_value=row.dad_name if row else '') #Họ tên bố
		# labelbo = LABEL('Họ tên Cha')
		# divbo = DIV(labelbo,inpbo,_class='form-group')
		
		# inpme = INPUT(_type='text',_class='form-control',_id='mother_name',_name='mother_name',_value=row.mother_name if row else '') #Họ tên bố
		# labelme = LABEL('Họ tên Mẹ')
		# divme = DIV(labelme,inpme,_class='form-group')
		
		
		# inpphone = INPUT(_type='text',_class='form-control',_id='phone',_name='phone',_value=row.phone if row else '') #Điện thoại
		# labelphone = LABEL('Điện thoại khi cần (chính) (*)')
		# divphone = DIV(labelphone,inpphone,_class='form-group')
		
		# inpphone1 = INPUT(_type='text',_class='form-control',_id='phone',_name='phone1',_value=row.phone1 if row else '') #Điện thoại
		# labelphone1 = LABEL('Điện thoại khi cần (phụ)')
		# divphone1 = DIV(labelphone1,inpphone1,_class='form-group')

		# inpdescription = TEXTAREA(row.description if row else '',_class='form-control',_name='description',_style='height:80px;') #Ghi chú
		# labeldesciption = LABEL('Ghi chú')
		# divjdesciption = DIV(labeldesciption,inpdescription,_class='form-group')
		
		# table.append(TR(TD(divname,_colspan='2')))
		# table.append(TR(TD(divbirthday),TD(divsex)))
		# table.append(TR(TD(divcou,_colspan='2')))
		# table.append(TR(TD(divbo),TD(divme)))
		# table.append(TR(TD(divphone),TD(divphone1)))
		# table.append(TR(TD(divaddress,_colspan='2')))
		# table.append(TR(TD(divjdesciption,_colspan='2')))
		
		# if id:
			# url = URL(r=request,c='plugin_student',f='update_student',vars=dict(id=id))
		# else:
			# url = URL(r=request,c='plugin_student',f='update_student')
		# div = DIV(FORM(table,DIV(_id='form_alert'),INPUT(_type='submit',_id='act_submit',_value=T('Submit'),_style='display:none;'),_id="form1",_name="form1",_action=url),_id='div_create_patient')
		
		# div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_class='btn btn-danger closemodals',_style='margin-left:5px;',_id='cancel_btn'),_class='text-center'))
		# script = SCRIPT("""$('#act_submit_ao').click(function(){
								# if (validateFormStudent()) {
									# $('#act_submit').click();
									# $('.closemodals').attr({'data-dismiss':'modal'});
									# }
							# });
							
							# $('#cancel_btn').click(function(){
								# $('.closemodals').attr({'data-dismiss':'modal'});
							# });
							
							# """)
		# div.append(script)
		# return div
	
	
	# ############################################
	# ##Quản lý thông tin lỗi vi phạm
	# ############################################
	# def list_violation(self,page):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		
		# from datatables import define_violation
		# define_violation(db, False)
		# from bootrap import Modals
		# ##Tìm kiếm theo các tiêu chí
		
		# inpname = INPUT(_type='text',_class='form-control',_name='name') #Tên lỗi
		# labelname = LABEL('Tên lỗi')
		# divname = DIV(labelname,inpname,_class='form-group')
				
		# table = TABLE(_class='table table-hover')
		# table.append(TR(TD(divname)))
		
		# #Tìm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_violation')	
		# ajax = "ajax('%s', ['name'], 'content_patient')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Tìm kiếm',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		# #Thêm mới
		# urladd = URL(r=request,c='plugin_student',f='form_violation')
		# xbtnadd = SPAN(SPAN(_class='fa fa-plus-circle')," Thêm mới" ,_class="btn btn-success",_title="Thêm mới lỗi vi phạm")
		# btnadd = Modals(caption=(xbtnadd),source=urladd,id='modals-addpatient')	
				
		# divhd = DIV()
		# divhd.append(table)
		# divhd.append(DIV(btnadd,btnsearch,_class='list-control'))
		# script_cl = SCRIPT('''$('#btn-firstcl').click();''')
		# divhd.append(script_cl)
		
		# divhd.append(DIV(self.write_table_violation('',0),_id='content_patient'))
		# return divhd
		
	# def write_table_violation(self,name,page):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		
		# from datatables import define_violation
		# define_violation(db, False)
		# import datetime
		# today = request.now
		
		# query = db.violation.id>0
		# if name!='':
			# query&= db.violation.name.like('%'+name+'%')
		
		# ##Phân trang
		# LEN_PAGE = 10
		# start = 0
		# end = 10
		# page = int(page)
		# if (page!=0):
			# end = page*LEN_PAGE
			# start = end-LEN_PAGE
		# len = db(query).count()
		# numbers = (len/LEN_PAGE)
		# if len%LEN_PAGE>0:
			# numbers = numbers + 1
		# ul = UL(_class='page-ul pagination pull-right',_style='margin:0px;')
		# i=1
		# vars = request.vars
		# while i<=numbers:
			# vars['page']=i
			# url = URL(r=request, vars=vars)
			# ajax = "ajax('%s',[],'patient_page')"%(url)
			# if (i-page<15):
				# if i==page:
					# ul.append(LI(A(i,_onClick=ajax,_style='border-radius:50%;'),_class='active'))
				# else:
					# ul.append(LI(A(i,_onClick=ajax,_style='border-radius:50%;')))			
			# i+=1
		# rows = db(query).select(limitby=(start,end))
		# table = self.table_violation(rows)
		# div= DIV(_id="patient_page")	
				
		# cou = db(query).count()	
		# divcount = DIV(SPAN('Có tổng số: ',cou, ' Lỗi vi phạm',_class='pull-right cou-patient'))
		# div.append(divcount)
		# div.append(table)
		# div.append(ul)
		# return div
		
	# ##Bảng danh sách thông tin Lỗi vi phạm
	# def table_violation(self,rows):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		
		# from datatables import define_violation
		# define_violation(db, False)
		# import datetime
		# from bootrap import Modals
		
		# table = TABLE(_class='table table-bordered table-center')
		# table.append(THEAD(TR(TH('STT'),TH('Lỗi vi phạm'),TH('Trạng thái'),TH('Chức năng'))))
		# tbody = TBODY()
		# i = 1
		# for r in rows:
			# tr = TR()
			# tr.append(TD(i,_style='with:60px;'))
			# tr.append(TD(r.name if r.name else '',_style='text-align:justify;')) 
			
			# #Kích hoạt hoặc khóa lỗi vi phạm
			# if r.aactive==True:
				# urlunactive = URL(r=request,c='plugin_student',f='unactive_violation',vars=dict(id = r.id))
				# ajaxunactive = "ajax('%s', [], 'content_active%s')"%(urlunactive,r.id)
				# aactive = INPUT(_type='checkbox',_name='aactive',_checked='checked',_onchange=ajaxunactive)
			# else:
				# urlactive = URL(r=request,c='plugin_student',f='active_violation',vars=dict(id = r.id))
				# ajaxactive = "ajax('%s', [], 'content_active%s')"%(urlactive,r.id)
				# aactive = INPUT(_type='checkbox',_name='aactive',_onchange=ajaxactive)
			
			# tr.append(TD(aactive,_id='content_active'+str(r.id)))

			# urledit = URL(r=request,c='plugin_student',f='form_violation',vars=dict(id=r.id))
			# xinpedit = BUTTON(SPAN(_class='fa fa-edit'),_class='btn btn-primary circle removeid')
			# inpedit = Modals(caption=(xinpedit),source=urledit,id='modals-edit'+str(i))	
			
			# urldelete = URL(r=request,c='plugin_student',f='delete_violation',vars=dict(id=r.id))
			# inpremove = A(BUTTON(SPAN(_class='fa fa-remove'),_class='btn btn-danger circle'),_href=urldelete,_onclick="return confirmDelete()",_title='Xóa')
			# tr.append(TD(SPAN(inpedit),' ',SPAN(inpremove)))
			# tbody.append(tr)
			# i+=1
		# table.append(tbody)
		# ##Xóa hết ID khi bật modals
		# scr = SCRIPT('''$('.removeid').click(function(){
				# $('#div_create_patient').find('input[type="submit"]').removeAttr('id');
				# });''')
		# table.append(TR(TD(scr,_style='display:none;')))
		# return table
		
	# ##Form Lỗi vi phạm
	# def form_violation(self,id):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_violation
		# define_violation(db, False)
		
		# row = db.violation(id)
		
		# table = TABLE(_class='table table-striple table-left')
		# inpname = INPUT(_type='text',_class='form-control',_name='name',_value=row.name if row else '') #Họ tên
		# labelname = LABEL('Tên lỗi')
		# divname = DIV(labelname,inpname,_class='form-group')
	
				
		# inpdescription = TEXTAREA(row.description if row else '',_class='form-control',_name='description',_style='height:80px;') #Ghi chú
		# labeldesciption = LABEL('Mô tả')
		# divjdesciption = DIV(labeldesciption,inpdescription,_class='form-group')
		
		# table.append(TR(TD(divname)))
		# table.append(TR(TD(divjdesciption)))
		
		# if id:
			# url = URL(r=request,c='plugin_student',f='update_violation',vars=dict(id=id))
		# else:
			# url = URL(r=request,c='plugin_student',f='update_violation')
		# div = DIV(FORM(table,INPUT(_type='submit',_id='act_submit',_value=T('Submit'),_style='display:none;'),_id="form1",_name="form1",_action=url,_onsubmit="return validateFormDoctor()"),_id='div_create_patient')
		
		# div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_class='btn btn-danger closemodals',_style='margin-left:5px;'),_class='text-center'))
		# script = SCRIPT("""$('#act_submit_ao').click(function(){
								# $('#act_submit').click();
							# });
							# $('.closemodals').attr({'data-dismiss':'modal'});
							# """)
		# div.append(script)
		# return div
	
	# #############################################
	# ##Quản lý Thông tin Giáo Viên
	# #############################################
	
	# ##Màn hình danh sách Giáo viên
	# def list_teacher(self,page):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		
		# from datatables import define_student
		# define_student(db, False)
		# from bootrap import Modals
		# ##Tìm kiếm theo các tiêu chí
		# inpcode = INPUT(_type='text',_class='form-control',_name='fcode')#Mã học sinh
		# labelcode = LABEL('Mã giáo viên')
		# divcode = DIV(labelcode,inpcode,_class='form-group')
		
		# inpname = INPUT(_type='text',_class='form-control',_name='ffullname') #Họ tên
		# labelname = LABEL('Họ tên')
		# divname = DIV(labelname,inpname,_class='form-group')
		
		# selectsex = SELECT(_name='fsex',_class='form-control') #Giới tính
		# list_sex =['all','sex_male','sex_female']
		# for r in list_sex:
			# selectsex.append(OPTION(T(r),_value=T(r)))
		# labelsex = LABEL('Giới tính')
		# divsex = DIV(labelsex,selectsex,_class='form-group')	
			
		# selectstatus = SELECT(_name='fstatus',_class='form-control') #Trạng thái
		# list_status =['Is_True','Is_False']
		# for r in list_status:
			# selectstatus.append(OPTION(T(r),_value=T(r)))
		# labelstatus = LABEL('Trạng thái')
		# divstatus = DIV(labelstatus,selectstatus,_class='form-group')	
			
		# inpaddress = INPUT(_type='text',_class='form-control',_name='faddress') #Địa chỉ
		# labeladdress = LABEL('Địa chỉ')
		# divaddress = DIV(labeladdress,inpaddress,_class='form-group')
		
		# table = TABLE(_class='table table-hover')
		# table.append(TR(TD(divcode),TD(divname),TD(divsex),TD(divstatus),TD(divaddress)))
		
		# #Tìm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_teacher')	
		# ajax = "ajax('%s', ['fcode','ffullname','fsex','fstatus','faddress'], 'content_student')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Tìm kiếm',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		# #Thêm mới
		# urladd = URL(r=request,c='plugin_student',f='form_teacher')

		# xbtnadd = SPAN(SPAN(_class='fa fa-plus-circle')," Thêm mới" ,_class="btn btn-success",_title="Thêm mới giáo viên")
		# btnadd = Modals(caption=(xbtnadd),source=urladd,id='modals-addpatient')	
		# # btnadd = A(xbtnadd,_href=urladd,id='modals-addpatient')	
				
		# divhd = DIV()
		# divhd.append(table)
		# divhd.append(DIV(btnadd,btnsearch,_class='list-control'))
		# script_cl = SCRIPT('''$('#btn-firstcl').click();''')
		# divhd.append(script_cl)
		
		# divhd.append(DIV(self.write_table_teacher('','','','',0),_id='content_student'))
		# return divhd	
	
	# def write_table_teacher(self,code,fullname,sex,address,page,status=True):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_teacher
		# define_teacher(db, False)
		# import datetime
		# today = request.now
		
		# query = db.teacher.id>0
		# if code!='':
			# query&= db.teacher.code==code
		# if fullname!='':
			# query&= db.teacher.fullname.like('%'+fullname+'%')
		# if sex!='Tất cả':
			# query&= db.teacher.sex==sex
		# if address!='':
			# query&= db.teacher.address.like('%'+address+'%')
			
		# if status:
			# query&= db.teacher.aactive==True
		# else:
			# query&= db.teacher.aactive==False
		# ##Phân trang
		# LEN_PAGE = 10
		# start = 0
		# end = 10
		# page = int(page)
		# if (page!=0):
			# end = page*LEN_PAGE
			# start = end-LEN_PAGE
		# len = db(query).count()
		# numbers = (len/LEN_PAGE)
		# if len%LEN_PAGE>0:
			# numbers = numbers + 1
		# ul = UL(_class='page-ul pagination pull-right',_style='margin:0px;')
		# i=1
		# vars = request.vars
		# while i<=numbers:
			# vars['page']=i
			# url = URL(r=request, vars=vars)
			# ajax = "ajax('%s',[],'patient_page')"%(url)
			# if (i-page<15):
				# if i==page:
					# ul.append(LI(A(i,_onClick=ajax,_style='border-radius:50%;'),_class='active'))
				# else:
					# ul.append(LI(A(i,_onClick=ajax,_style='border-radius:50%;')))			
			# i+=1
		# rows = db(query).select(limitby=(start,end))
		# table = self.table_teacher(rows)
		# div= DIV(_id="patient_page")	
				
		# coupatien = db(query).count()	
		# divcount = DIV(SPAN('Có tổng số: ',coupatien, ' giáo viên',_class='pull-right cou-patient'))
		# div.append(divcount)
		# div.append(table)
		# div.append(ul)
		# return div
		
	# ##Bảng danh sách thông tin Giáo viên
	# def table_teacher(self,rows):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		
		# from datatables import define_teacher
		# define_teacher(db, False)
		# import datetime
		# from bootrap import Modals
		
		# table = TABLE(_class='table table-bordered table-center')
		# table.append(THEAD(TR(TH('STT'),TH('Mã giáo viên'),TH('Họ tên'),TH('Giới tính'),TH('Ngày sinh'),TH('Số điện thoại'),TH('Email'),TH('Chức năng'))))
		# tbody = TBODY()
		# i = 1
		# for r in rows:
			# tr = TR()
			# tr.append(TD(i))
			# tr.append(TD(r.code if r.code else ''))
			# tr.append(TD(r.fullname if r.fullname else '')) 
			# tr.append(TD(T(r.sex if r.sex else '')))
			# tr.append(TD(r.birthday.strftime('%d/%m/%Y') if r.birthday else ''))
			# tr.append(TD(r.phone if r.phone else ''))
			# tr.append(TD(r.email if r.email else ''))
			
			# urlupdate_pass = URL(r=request,c='plugin_student',f='update_pass_teacher',vars=dict(id=r.id))
			# xinpupdate_pass = BUTTON(SPAN(_class='fa fa-cogs'),_class='btn btn-warning circle removeid')
			# inpeupdate_pass = Modals(caption=(xinpupdate_pass),source=urlupdate_pass,id='modals-pass'+str(i))	
			
			# urledit = URL(r=request,c='plugin_student',f='form_teacher',vars=dict(id=r.id))
			# xinpedit = BUTTON(SPAN(_class='fa fa-edit'),_class='btn btn-primary circle removeid')
			# inpedit = Modals(caption=(xinpedit),source=urledit,id='modals-edit'+str(i))	
			
			# urldelete = URL(r=request,c='plugin_student',f='delete_teacher',vars=dict(id=r.id))
			# inpremove = A(BUTTON(SPAN(_class='fa fa-flag'),_class='btn btn-danger circle'),_href=urldelete,_onclick="return confirmDelete()",_title='Cập nhật trạng thái')
			# tr.append(TD(SPAN(inpeupdate_pass),' ',SPAN(inpedit),' ',SPAN(inpremove)))
			# # tr.append(TD(SPAN(inpedit),' ',SPAN(inpremove)))
			# tbody.append(tr)
			# i+=1
		# table.append(tbody)
		# ##Xóa hết ID khi bật modals
		# scr = SCRIPT('''$('.removeid').click(function(){
				# $('#div_create_patient').find('input[type="submit"]').removeAttr('id');
				# });''')
		# table.append(TR(TD(scr,_style='display:none;')))
		# return table
	
	# ##Form Giáo viên
	# def form_teacher(self,id):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_teacher
		# define_teacher(db, False)
		
		# row = db.teacher(id)
		
		# table = TABLE(_class='table table-striple table-left')
		# inpname = INPUT(_type='text',_class='form-control',_id='fullname',_name='fullname',_value=row.fullname if row else '') #Họ tên
		# labelname = LABEL('Họ tên (*)')
		# divname = DIV(labelname,inpname,_class='form-group')
		
		# birthday = ''
		# if row:
			# birthday = row.birthday.strftime('%d/%m/%Y') if row.birthday else ''
		# inpbirthday = INPUT(_type='text',_class='form-control datepicker',_id='birthday',_name='birthday',_value=birthday) #Ngày sinh
		# labelbirthday = LABEL('Ngày sinh (*)')
		# divbirthday = DIV(labelbirthday,inpbirthday,_class='form-group')
		
		# selectsex = SELECT(_name='sex',_class='form-control') #Giới tính
		# list_sex =['Nam','Nữ']
		# for r in list_sex:
			# if row:
				# if row.sex==r:
					# selectsex.append(OPTION(T(r),_value=r,_selected='selected'))
				# else:
					# selectsex.append(OPTION(T(r),_value=r))
			# else:
				# selectsex.append(OPTION(T(r),_value=r))
		# labelsex = LABEL('Giới tính')
		# divsex = DIV(labelsex,selectsex,_class='form-group')	
		
		# inpphone = INPUT(_type='text',_class='form-control',_id='phone',_name='phone',_value=row.phone if row else '') #Số điện thoại
		# labelphone = LABEL('Số điện thoại (*)')
		# divphone = DIV(labelphone,inpphone,_class='form-group')
		
		# inpemail = INPUT(_type='text',_class='form-control',_name='email',_value=row.email if row else '') #Email
		# labelemail = LABEL('Địa chỉ email')
		# divemail = DIV(labelemail,inpemail,_class='form-group')
				
		# inpaddress = INPUT(_type='text',_class='form-control',_name='address',_value=row.address if row else '') #Địa chỉ
		# labeladdress = LABEL('Địa chỉ')
		# divaddress = DIV(labeladdress,inpaddress,_class='form-group')

		# inpdescription = TEXTAREA(row.description if row else '',_class='form-control',_name='description',_style='height:80px;') #Ghi chú
		# labeldesciption = LABEL('Ghi chú')
		# divjdesciption = DIV(labeldesciption,inpdescription,_class='form-group')
		
		# table.append(TR(TD(divname,_colspan='2')))
		# table.append(TR(TD(divbirthday),TD(divsex)))
		# table.append(TR(TD(divphone),TD(divemail)))
		# table.append(TR(TD(divaddress,_colspan='2')))
		# table.append(TR(TD(divjdesciption,_colspan='2')))
		
		# if id:
			# url = URL(r=request,c='plugin_student',f='update_teacher',vars=dict(id=id))
		# else:
			# url = URL(r=request,c='plugin_student',f='update_teacher')
		# div = DIV(FORM(table,INPUT(_type='submit',_id='act_submit',_value=T('Submit'),_style='display:none;'),_id="form1",_name="form1",_action=url),_id='div_create_patient')
		
		# div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_class='btn btn-danger closemodals',_style='margin-left:5px;',_id='cancel_btn'),_class='text-center'))
		# script = SCRIPT("""$('#act_submit_ao').click(function(){
								# if (validateFormStudent()) {
									# $('#act_submit').click();
									# $('.closemodals').attr({'data-dismiss':'modal'});
									# }
							# });
							
							# $('#cancel_btn').click(function(){
								# $('.closemodals').attr({'data-dismiss':'modal'});
							# });
							
							# """)
		# div.append(script)
		# return div
	
	# #############################################
	# ##Quản lý Thông tin Lớp học
	# #############################################
	
	# ##Màn hình danh sách Lớp học
	# def list_classroom(self,page):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datetime import date,datetime, timedelta
		# from datatables import define_classroom,define_scholastic
		# define_classroom(db, False)
		# define_scholastic(db, False)
		# from bootrap import Modals
		# ##Tìm kiếm theo các tiêu chí
		# inpname = INPUT(_type='text',_class='form-control',_name='fname')#Tên Lớp
		# labelname = LABEL('Tên lớp')
		# divname = DIV(labelname,inpname,_class='form-group')
		# scholastic = ''
		# rowsch = db(db.scholastic.id>0).select()
		# selectsch = SELECT(OPTION('-- Chọn năm học --',_value=''),_name='fscholastic',_class='form-control') #Giới tính
		# for r in rowsch:
			# from datetime import date
			# d = date.today()
			# if (r.start_date<= d)&(r.end_date>=d):
				# selectsch.append(OPTION(r.name,_value=r.id,_selected=True))
				# scholastic = r.id
			# else:
				# selectsch.append(OPTION(r.name,_value=r.id))
		# labelsch = LABEL('Năm học')
		# divsch = DIV(labelsch,selectsch,_class='form-group')	
			
		# table = TABLE(_class='table table-hover')
		# table.append(TR(TD(divname),TD(divsch)))
		
		# #Tìm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_classroom')	
		# ajax = "ajax('%s', ['fname','fscholastic'], 'content_student')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Tìm kiếm',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		# #Thêm mới
		# urladd = URL(r=request,c='plugin_student',f='form_classroom')

		# xbtnadd = SPAN(SPAN(_class='fa fa-plus-circle')," Thêm mới" ,_class="btn btn-success",_title="Thêm mới Lớp học")
		# btnadd = Modals(caption=(xbtnadd),source=urladd,id='modals-addpatient')	
		# # btnadd = A(xbtnadd,_href=urladd,id='modals-addpatient')	
				
		# divhd = DIV()
		# divhd.append(table)
		# divhd.append(DIV(btnadd,btnsearch,_class='list-control'))
		# script_cl = SCRIPT('''$('#btn-firstcl').click();''')
		# divhd.append(script_cl)
		
		# divhd.append(DIV(self.write_table_classroom('',scholastic,0),_id='content_student'))
		# return divhd	
	
	# def write_table_classroom(self,name,scholastic,page):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_classroom
		# define_classroom(db, False)
		# import datetime
		# today = request.now
		
		# query = db.classroom.id>0
		# if name!='':
			# query&= db.classroom.name.like('%'+name+'%')
		# if scholastic!='':
			# query&= db.classroom.scholastic==scholastic
		
		# ##Phân trang
		# LEN_PAGE = 20
		# start = 0
		# end = 20
		# page = int(page)
		# if (page!=0):
			# end = page*LEN_PAGE
			# start = end-LEN_PAGE
		# len = db(query).count()
		# numbers = (len/LEN_PAGE)
		# if len%LEN_PAGE>0:
			# numbers = numbers + 1
		# ul = UL(_class='page-ul pagination pull-right',_style='margin:0px;')
		# i=1
		# vars = request.vars
		# while i<=numbers:
			# vars['page']=i
			# url = URL(r=request, vars=vars)
			# ajax = "ajax('%s',[],'patient_page')"%(url)
			# if (i-page<15):
				# if i==page:
					# ul.append(LI(A(i,_onClick=ajax,_style='border-radius:50%;'),_class='active'))
				# else:
					# ul.append(LI(A(i,_onClick=ajax,_style='border-radius:50%;')))			
			# i+=1
		# rows = db(query).select(limitby=(start,end))
		# table = self.table_classroom(rows,page,LEN_PAGE)
		# div= DIV(_id="patient_page")	
				
		# coupatien = db(query).count()	
		# divcount = DIV(SPAN('Có tổng số: ',coupatien, ' Lớp học',_class='pull-right cou-patient'))
		# div.append(divcount)
		# div.append(table)
		# div.append(ul)
		# return div
		
	# ##Bảng danh sách thông tin Lớp học
	# def table_classroom(self,rows,page=0,len_page = 10):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		
		# from datatables import define_classroom,define_scholastic,define_teacher
		# define_classroom(db, False)
		# define_scholastic(db, False)
		# define_teacher(db, False)
		# import datetime
		# from bootrap import Modals
		
		# table = TABLE(_class='table table-bordered table-center')
		# table.append(THEAD(TR(TH('STT'),TH('Năm học'),TH('Tên lớp học'),TH('Giáo viên chủ nhiệm'),TH('Chức năng'))))
		# tbody = TBODY()
		# i = 1
		# try:
			# if page>1:
				# i = (page-1)*len_page +1
		# except Exception,e: return e
		# for r in rows:
			# tr = TR()
			# url = URL(r=request,c='plugin_student',f='list_student_class',vars=dict(idclass=r.id))
			# tr.append(TD(i))
			# namesch = ''
			# if r.scholastic:
				# scholastic = db.scholastic(r.scholastic)
				# namesch = scholastic.name if scholastic.name else ''
			# tr.append(TD(namesch)) #Năm học
			# tr.append(TD(A(r.name if r.name else '',_href=url)))  #Tên lớp học
			
			# nametea = ''
			# if r.teacher:
				# teacher = db.teacher(r.teacher)
				# nametea = teacher.fullname if teacher.fullname else ''
			# tr.append(TD(T(nametea))) #Giáo viên chủ nhiệm
		
			# urledit = URL(r=request,c='plugin_student',f='form_classroom',vars=dict(id=r.id))
			# xinpedit = BUTTON(SPAN(_class='fa fa-edit'),_class='btn btn-primary circle removeid')
			# inpedit = Modals(caption=(xinpedit),source=urledit,id='modals-edit'+str(i))	
			
			# urldelete = URL(r=request,c='plugin_student',f='delete_classroom',vars=dict(id=r.id))
			# inpremove = A(BUTTON(SPAN(_class='fa fa-remove'),_class='btn btn-danger circle'),_href=urldelete,_onclick="return confirmDelete()",_title='Xóa')
			# tr.append(TD(SPAN(inpedit),' ',SPAN(inpremove)))
			# tbody.append(tr)
			# i+=1
		# table.append(tbody)
		# ##Xóa hết ID khi bật modals
		# scr = SCRIPT('''$('.removeid').click(function(){
				# $('#div_create_patient').find('input[type="submit"]').removeAttr('id');
				# });''')
		# table.append(TR(TD(scr,_style='display:none;')))
		# return table
	
	# ##Form Lớp học
	# def form_classroom(self,id):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_classroom,define_teacher,define_scholastic
		# define_classroom(db, False)
		# define_teacher(db, False)
		# define_scholastic(db, False)
		
		# row = db.classroom(id)
		
		# table = TABLE(_class='table table-striple table-left')
		# inpname = INPUT(_type='text',_class='form-control',_name='name',_value=row.name if row else '') #Tên Lớp
		# labelname = LABEL('Tên lớp')
		# divname = DIV(labelname,inpname,_class='form-group')
		
		# ##Năm học
		# rowsch = db(db.scholastic.id>0).select()
		# selectsch = SELECT(OPTION('-- Chọn năm học --',_value=''),_name='scholastic',_class='form-control') 
		# for r in rowsch:
			# if row:
				# scholastic = int(row.scholastic) if row.scholastic else ''
				# if scholastic==r.id:
					# selectsch.append(OPTION(r.name,_value=r.id,_selected='selected'))
				# else:
					# selectsch.append(OPTION(r.name,_value=r.id))
			# else:
				# selectsch.append(OPTION(r.name,_value=r.id))
		# labelsch = LABEL('Năm học')
		# divsch = DIV(labelsch,selectsch,_class='form-group')	
		
		# ##Giáo viên chủ nhiệm
		# rowtea = db(db.teacher.id>0).select()
		# selecttea = SELECT(OPTION('-- Chọn giáo viên chủ nhiệm  --',_value=''),_name='teacher',_class='form-control') 
		# for r in rowtea:
			# if row:
				# teacher = int(row.teacher) if row.teacher else ''
				# if r.id==teacher:
					# selecttea.append(OPTION(r.fullname,_value=r.id,_selected='selected'))
				# else:
					# selecttea.append(OPTION(r.fullname,_value=r.id))
			# else:
				# selecttea.append(OPTION(r.fullname,_value=r.id))
		# labelsch = LABEL('Giáo viên chủ nhiệm')
		# divtea = DIV(labelsch,selecttea,_class='form-group')	
		
		# inpdescription = TEXTAREA(row.description if row else '',_class='form-control',_name='description',_style='height:80px;') #Ghi chú
		# labeldesciption = LABEL('Ghi chú')
		# divjdesciption = DIV(labeldesciption,inpdescription,_class='form-group')
		
		# table.append(TR(TD(divname,_colspan='2')))
		# table.append(TR(TD(divsch),TD(divtea)))
		# table.append(TR(TD(divjdesciption,_colspan='2')))
		
		# if id:
			# url = URL(r=request,c='plugin_student',f='update_classroom',vars=dict(id=id))
		# else:
			# url = URL(r=request,c='plugin_student',f='update_classroom')
		# div = DIV(FORM(table,INPUT(_type='submit',_id='act_submit',_value=T('Submit'),_style='display:none;'),_id="form1",_name="form1",_action=url,_onsubmit="return validateFormStudent()"),_id='div_create_patient')
		
		# div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_class='btn btn-danger closemodals',_style='margin-left:5px;'),_class='text-center'))
		# script = SCRIPT("""$('#act_submit_ao').click(function(){
								# $('#act_submit').click();
							# });
							# $('.closemodals').attr({'data-dismiss':'modal'});
							# """)
		# div.append(script)
		# return div
	
	# ###########################################
	# ##Quản lý danh sách học sinh vi phạm nội quy
	# ##Đánh giá theo tuần
	# ###########################################
	# def student_violation_week(self):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from bootrap import Modals
		# from datetime import date,datetime, timedelta
		# from datatables import define_classroom
		# define_classroom(db, False)
		# ##Đầu tuần
		# monday = date.today() - timedelta(days=date.today().weekday())
		# ##Cuối tuần
		# sunday = monday + timedelta(days=6)
		
		# ##lấy tháng của năm học	
		# nowyear = request.now.year
		# if request.now.month<9:
				# nowyear = nowyear - 1
		# else:
			# nowyear = nowyear	
	
		# ##Lấy tuần hiện tại của năm học
		# inday = str(nowyear) +'-9-1' #mốc thời gian của năm học
		# d = datetime.strptime(inday, '%Y-%m-%d')
		# numbday = (request.now - d).days #Ngày hiện tại trừ mốc thời gian
		# numw = (numbday/7) +1 #Số tuần tính từ mốc thời gian
	
		
		# urlsea = URL(r=request,c='plugin_student',f='date_between_violation')	
		# ajax = "ajax('%s', ['numberyear','numberweek'], 'get_date')"%(urlsea)
		# #Tuần
		# selectweek = SELECT(OPTION('-- Chọn tuần --',_value=''),_class='form-control',_name='numberweek',_onchange=ajax,_id='numberweek')
		# for w in range(1,55):
			# if w ==numw:
				# selectweek.append(OPTION('Tuần '+str(w),_value=w-1,_selected='selected'))
			# else:
				# selectweek.append(OPTION('Tuần '+str(w),_value=w-1))
		
		# selectyear = SELECT(OPTION('-- Chọn năm học --',_value=''),_class='form-control',_name='numberyear')			
		# for y in range(nowyear-3,nowyear+3):
			# if nowyear==y:
				# selectyear.append(OPTION(y , ' - ',y+1,_value=y,_selected='selected'))	
			# else:
				# selectyear.append(OPTION(y , ' - ',y+1,_value=y))	
			
		# inpstart = INPUT(_type='text',_class='form-control datepicker',_name='start_date',_value=monday.strftime('%d/%m/%Y'))	
		# inpend = INPUT(_type='text',_class='form-control datepicker',_name='end_date',_value=sunday.strftime('%d/%m/%Y'))	
		# ##Danh sách lớp học
		# if auth.has_membership(role='admin'):
			# query = db.classroom.id>0
		# else:
			# list_cl = self.get_classroom_teacher()
			# query = db.classroom.id.belongs(list_cl)
		# rowcl = db(query).select()
		# selectcl = SELECT(_class='form-control',_name='classroom')
		# for rc in rowcl:
			# selectcl.append(OPTION('Lớp ' ,rc.name if rc.name else '',_value=rc.id))	
		
		# table = TABLE(_class='table')
		# table.append(TR(TD(selectcl,_colspan='2')))
		# table.append(TR(TD(selectyear),TD(selectweek)))
		# table.append(TBODY(TR(TD(inpstart),TD(inpend)),_id='get_date'))
		
		# ##TÌm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_student_violation')	
		# ajax = "ajax('%s', ['classroom','start_date','end_date'], 'write_student_violation')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Tìm kiếm',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		
		# ##Thêm mới
		# urladd = URL(r=request,c='plugin_student',f='form_student_violation')
		# xbtnadd = SPAN(SPAN(_class='fa fa-plus-circle')," Thêm mới" ,_class="btn btn-success",_title="Thêm mới lỗi vi phạm")
		# btnadd = Modals(caption=(xbtnadd),source=urladd,id='modals-addpatient')	
		# # btnadd = A(xbtnadd,_href=urladd,id='modals-addpatient')	
				
		# table.append(TR(TD(btnadd, ' ',btnsearch,_colspan='2')))
		# divhd = DIV()
		# divhd.append(table)
		# divhd.append(DIV(self.list_student_violation('',request.now.strftime('%d/%m/%Y'),request.now.strftime('%d/%m/%Y')),_id='write_student_violation'))
		# scr = SCRIPT('''$('#btn-firstcl').click();
					# ''')
		# divhd.append(scr)
		# return divhd	
		
	# def date_between_violation(self,numberyear,numberweek):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datetime import datetime, timedelta
		# if numberyear=='':
			# numberyear = str(request.now.year)
		# inday = numberyear +'-9-1'
		# d = datetime.strptime(inday, '%Y-%m-%d')
		# first_monday = self.next_weekday(d, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
		# ##Lấy ngày thứ 2 theo mốc tuần đầu tiên của năm học
		# ##Số thứ tự theo tuần * 7
		# numbday = 0
		# numsunday = 6
		# if numberweek!='':
			# numbday = int(numberweek) * 7
			# numsunday = (int(numberweek) * 7) + 6
		# xmonday = first_monday  + timedelta(numbday)
		# xsunday = first_monday + timedelta(numsunday)
		
		# tr = TR()
		# inpstart = INPUT(_type='text',_class='form-control datepicker',_name='start_date',_value=xmonday.strftime('%d/%m/%Y'))	
		# inpend = INPUT(_type='text',_class='form-control datepicker',_name='end_date',_value=xsunday.strftime('%d/%m/%Y'))
		# tr.append(TD(inpstart))
		# tr.append(TD(inpend))
		
		# return tr
		
	
	# def list_student_violation(self,classroom,start_date,end_date):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_student_violation,define_classroom,define_violation,define_student,define_student_classroom
		# define_student_violation(db, False)
		# define_classroom(db, False)
		# define_violation(db, False)
		# define_student(db, False)
		# define_student_classroom(db, False)
		# from bootrap import Modals
		# import calendar
		# import datetime
		# # from datetime import datetime,  timedelta
		# input,output = "%d/%m/%Y", "%Y-%m-%d"	
		# if (start_date!='')&(end_date!=''):
			# timestart= datetime.datetime.strptime(start_date,input).strftime(output)
			# timeend = datetime.datetime.strptime(end_date,input).strftime(output)
		# ##Header Table
		# ##Danh sách lỗi vi phạm
		# query = db.violation.aactive==True
		# cou = db(query).count()
		# table = TABLE(_class='table table-bordered table-center')
		# thead = THEAD(TR(TH('TT',_rowspan='2'),TH('Họ và tên',_rowspan='2'),TH('Vi phạm',_colspan=cou),TH('#',_rowspan='2')))
		# rowvio = db(query).select()
		# tr = TR()
		# for r in rowvio:
			# tr.append(TH(r.name if r.name else ''))
		# thead.append(tr)
		# table.append(thead)
		# ##Body table
		# ##Danh sách học sinh
		# div = DIV()
		# if classroom!='':
			# que = (db.student_classroom.classroom==classroom)&(db.student_classroom.student==db.student.id)
			# rowstu = db(que).select(orderby=(db.student.lastname|db.student.firstname))
			# i = 1
			# tbody = TBODY()
			# for ru in rowstu:
				# tr = TR()
				# tr.append(TD(i))
				# tr.append(TD(ru.student.fullname if ru.student.fullname else ''))
				# for ro in rowvio:
					# ##Đếm số lỗi vi phạm
					# quex = (db.student_violation.violation==ro.id)&(db.student_violation.student_classroom==ru.student.id)
					# if (start_date!='')&(end_date!=''):
						# quex &= (db.student_violation.datevio>=timestart)&(db.student_violation.datevio<=timeend)
					# co = db(quex).count()
					# tr.append(TD(co))
				
				# ##Chỉnh sửa lỗi vi phạm
				# urledit = URL(r=request,c='plugin_student',f='form_student_violation',vars=dict(idstu=ru.student.id,start_date=start_date,end_date=end_date))
				# xinpedit = BUTTON(SPAN(_class='fa fa-edit'),_class='btn btn-primary circle removeid')
				# inpedit = Modals(caption=(xinpedit),source=urledit,id='modals-edit'+str(i))	
				# # inpedit = A(xinpedit,_href=urledit,id='modals-edit'+str(i))	
				# tr.append(TD(inpedit))	
				# tbody.append(tr)	
				# i+=1
			# table.append(tbody)
			
			# div.append(table)
		# else:
			# div.append(DIV('Chưa chọn lớp học cần xem',_style='font-size:20px;'))
		# return div
	
	# ##Form học sinh vi phạm
	# def form_student_violation(self,idstu,start_date,end_date):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_student_violation,define_classroom,define_student
		# define_student_violation(db, False)
		# define_classroom(db, False)
		# define_student(db, False)
				
		# table = TABLE(_class='table')
		# rowstu = db(db.student.id>0).select()
		# selectstu = SELECT(_class='form-control tags',_name='student_classroom')
		# for ru  in rowstu:
			# if idstu:
				# idstu = int(idstu)
				# if (ru.id==idstu):
					# selectstu.append(OPTION(ru.fullname,_value=ru.id,_selected='selected'))
			# else:
				# selectstu.append(OPTION(ru.fullname,_value=ru.id))
		# labelstu = LABEL('Học sinh vi phạm')
		# divstu = DIV(labelstu,selectstu,_class='form-group')
		# table.append(TR(TD(divstu)))
		
		# ##Lỗi vi phạm
		# vio = self.get_violation(idstu,start_date,end_date)
		# divform = DIV()
		# divform.append(table)
		# divform.append(DIV(vio))
										
		# url = URL(r=request,c='plugin_student',f ='update_student_violation')			
		# div = DIV(FORM(divform,INPUT(_type='submit',_id='act_submit',_value=T('Submit'),_style='display:none;'),_id="form1",_name="form1",_action=url,_onsubmit="return validateFormPatient()"),_id='div_create_patient')
		
		# div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_class='btn btn-danger closemodals',_style='margin-left:5px;'),_class='text-center'))
		# script = SCRIPT("""$('#act_submit_ao').click(function(){
								# $('#act_submit').click();
							# });
							# $('.closemodals').attr({'data-dismiss':'modal'});
							# """)
		# div.append(script)
		# return div
		
	# def get_violation(self,idstu,start_date,end_date):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_violation,define_student_violation
		# define_violation(db, False)
		# define_student_violation(db, False)
		# import datetime
		# input,output = "%d/%m/%Y", "%Y-%m-%d"	
		
		
		# table = TABLE(_class='table',_id='tablevio')
		# table.append(THEAD(TR(TH('STT',_style='width:50px;'),TH('Lỗi vi phạm'),TH('Thời gian'),TH('#',_style='width:70px;'))))
		
		# query = (db.student_violation.student_classroom==idstu)
		# if (start_date!='')&(end_date!=''):
			# timestart= datetime.datetime.strptime(start_date,input).strftime(output)
			# timeend = datetime.datetime.strptime(end_date,input).strftime(output)
			# query&=(db.student_violation.datevio>=timestart)&(db.student_violation.datevio<=timeend)
		# rows = db(query).select()
		# if rows:
			# i = 1
			# for ru in rows:
				# rowvio = db(db.violation.aactive==True).select()
				# selectvio = SELECT(OPTION('--Lỗi vi phạm--',_value=''),_class='form-control tags',_name='violationlast'+str(ru.id))
				# for ro in rowvio:
					# vio = int(ru.violation) if ru.violation else ''
					# if ro.id == vio:
						# selectvio.append(OPTION(ro.name,_value=ro.id,_selected='selected'))
					# else:
						# selectvio.append(OPTION(ro.name,_value=ro.id))
						
				# vadatevio = ru.datevio.strftime('%d/%m/%Y') if ru.datevio else ''
				# datevio = INPUT(_type='text',_name='dateviolast'+str(ru.id),_class='form-control datepicker',_value=vadatevio)
				# table.append(TR(TD(i),TD(selectvio),TD(datevio),TD(SPAN('Xóa',_class='removesupplies'))))
				# i+=1
		# else:
			# ##Danh sách lỗi
			# rowvio = db(db.violation.aactive==True).select()
			# selectvio = SELECT(OPTION('--Lỗi vi phạm--',_value=''),_class='form-control tags',_name='violation')
			# for ro in rowvio:
				# selectvio.append(OPTION(ro.name,_value=ro.id))
			
			# datevio = INPUT(_type='text',_name='datevio',_class='form-control datepicker',_value=request.now.date().strftime('%d/%m/%Y'))
			# table.append(TR(TD('1'),TD(selectvio),TD(datevio),TD(SPAN('Xóa',_class='removesupplies'))))
		
		# defaultvio = SELECT(OPTION('--Lỗi vi phạm--',_value=''),_class='form-control tags',_name='violation')
		# for ro in rowvio:
			# defaultvio.append(OPTION(ro.name,_value=ro.id))
		# defautldatevio = INPUT(_type='text',_name='datevio',_class='form-control datepicker',_value=request.now.date().strftime('%d/%m/%Y'))
			
		# inpadd = SPAN(SPAN(_class='fa fa-plus'),' Thêm mới',_id='add-supplies',_class='btn btn-warning')
		# div = DIV()
		# div.append(DIV(table))
		# div.append(DIV(inpadd,_style='text-align:left;'))
		
		# script = SCRIPT('''//Thêm hàng mới
				# $('#add-supplies').click(function(){
				# var xid = $('#tablevio tr:last').find('td:first').text();
				# if (xid==''){
					# xid = 0;
				# }
				# var intid = parseInt(xid);
				# var newid = intid + 1;
				# var tr = '<tr>'
				# tr+= '<td>'
				# tr+= newid
				# tr+= '</td>'
				# tr+= '<td style="width:500px;">%s</td>' 
				# tr+= '<td>%s</td>' 
				# tr+= "<td><span class='removesupplies'> Xóa </span></td>" 
				# $('#tablevio').append(tr);
				# sc = '<script>'
				# sc+='$(".tags").chosen({no_results_text: "Không tìm thấy dữ liệu!"}); '
				# sc+='</script>'
				# $('body').append(sc);
				# $('.removesupplies').click(function(){
					# $(this).parent().parent().remove();
				# });
				# $('.datepicker').datepicker({autoclose: true,format: 'dd/mm/yyyy',}); 
			# })'''%(defaultvio,defautldatevio))
		# div.append(script)
		# scr = SCRIPT('''
			# $('.removesupplies').click(function(){
			# $(this).parent().parent().remove();
			# });
		# ''')
		# div.append(scr)
		# return div

	
	# ##Xem ngày thứ 2 đầu tiên tính từ ngày được chọn
	# def next_weekday(self,d, weekday):
		# import datetime
		# days_ahead = weekday - d.weekday()
		# if days_ahead <= 0: # 
			# days_ahead += 7
		# return d + datetime.timedelta(days_ahead)

	# ###########################################
	# ##Điểm danh học sinh ăn sáng trong ngày
	# def student_breakfast(self):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_scholastic,define_teacher_classroom
		# define_classroom(db, False)
		# define_scholastic(db, False)
		# define_teacher_classroom(db, False)
		
		# inpday = INPUT(_type='text',_class='form-control datepicker',_name='inday',_value=request.now.strftime('%d/%m/%Y'))
		
		# scholastic = ''
		# from datetime import date
		# d = date.today()
		# rowsch = db((db.scholastic.start_date<= d)&(db.scholastic.end_date>=d)).select().first()
		# if rowsch: scholastic = rowsch.id
				
		# ##Danh sách lớp học
		
		# if auth.has_membership(role='admin'):
			# query = db.classroom.id>0
			# if scholastic !='':
				# query &= (db.classroom.scholastic==scholastic)
			# rowclass = db(query).select()
			# selectcr = SELECT(_name='classroom',_class='form-control')
			# for r in rowclass:
				# selectcr.append(OPTION('Lớp ',r.name,_value=r.id))
		
		# else:
			
			# list_cl = self.get_id_teacher()
			# if list_cl:
				
				# rowclass = db((db.teacher_classroom.teacher==list_cl)&(db.teacher_classroom.breakfast==True)&(db.teacher_classroom.classroom==db.classroom.id)&(db.classroom.scholastic==scholastic)).select()
				# selectcr = SELECT(_name='classroom',_class='form-control')
				# for r in rowclass:
					# selectcr.append(OPTION('Lớp ',r.classroom.name,_value=r.classroom.id))
		
		# ##TÌm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_student_breakfast')	
		# ajax = "ajax('%s', ['classroom','inday'], 'write_student_breakfast')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Tìm kiếm',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		
		# table = TABLE(_class='table')
		# table.append(TR(TD(inpday),TD(selectcr),TD(btnsearch,_style='width:100px;')))
		
		# div = DIV()
		# div.append(table)
		# div.append(DIV(self.write_student_breakfast('',request.now.strftime('%d/%m/%Y')),_id='write_student_breakfast'))
		# scr = SCRIPT('''$('#btn-firstcl').click();
					# ''')
		# div.append(scr)
		# return div
		
	# def student_list_view(self):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_scholastic,define_teacher_classroom
		# define_classroom(db, False)
		# define_scholastic(db, False)
		# define_teacher_classroom(db, False)
		
		# inpday = INPUT(_type='text',_class='form-control datepicker',_name='inday',_value=request.now.strftime('%d/%m/%Y'))
		
		# scholastic = ''
		# from datetime import date
		# d = date.today()
		# rowsch = db((db.scholastic.start_date<= d)&(db.scholastic.end_date>=d)).select().first()
		# if rowsch: scholastic = rowsch.id
				
		# ##Danh sách lớp học
		
		# if auth.has_membership(role='admin'):
			# query = db.classroom.id>0
			# if scholastic !='':
				# query &= (db.classroom.scholastic==scholastic)
			# rowclass = db(query).select()
			# selectcr = SELECT(_name='classroom',_class='form-control')
			# for r in rowclass:
				# selectcr.append(OPTION('Lớp ',r.name,_value=r.id))
		
		# else:
			
			# list_cl = self.get_id_teacher()
			# if list_cl:
				
				# rowclass = db((db.teacher_classroom.teacher==list_cl)&(db.teacher_classroom.breakfast==True)&(db.teacher_classroom.classroom==db.classroom.id)&(db.classroom.scholastic==scholastic)).select()
				# selectcr = SELECT(_name='classroom',_class='form-control')
				# for r in rowclass:
					# selectcr.append(OPTION('Lớp ',r.classroom.name,_value=r.classroom.id))
		
		# ##TÌm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_student_list_view')	
		# ajax = "ajax('%s', ['classroom'], 'write_student_list_view')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Lọc dữ liệu',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		
		# table = TABLE(_class='table')
		# table.append(TR(TD(selectcr),TD(btnsearch,_style='width:100px;')))
		
		# div = DIV()
		# div.append(table)
		# div.append(DIV(self.write_student_list_view(''),_id='write_student_list_view'))
		# scr = SCRIPT('''$('#btn-firstcl').click();
					# ''')
		# div.append(scr)
		# return div
	
	# def write_student_list_view(self,classroom):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_student,define_student_classroom,define_student_breakfast
		# define_classroom(db, False)
		# define_student(db, False)
		# define_student_classroom(db, False)
		# define_student_breakfast(db, False)
		
		# input,output = "%d/%m/%Y", "%Y-%m-%d"	

		# table = TABLE(_class='table table-bordered')	
		# table.append(THEAD(TR(TH('STT',_style='width:60px;'),TH('Mã học sinh',_style='width:120px;'),TH('Tên học sinh'),TH('Giới tính',_style='width:80px;'),TH('Họ tên bố'),TH('Họ tên mẹ'))))
		# rows = db((db.student_classroom.classroom==classroom)&(db.student_classroom.student==db.student.id)&(db.student_classroom.aactive==True)).select(orderby=(db.student.lastname|db.student.firstname))
		# i = 1
		# for r in rows:
			# tr = TR(i)
			# tr.append(TD(r.student.code if r.student.code else ''))
			# tr.append(TD( r.student.fullname if r.student.fullname else '',BR(),I(r.student.birthday.strftime('%d/%m/%Y') if r.student.birthday else '' ,_class='textright')))
			# tr.append(TD(r.student.sex if r.student.sex else ''))
			
			# tr.append(TD(r.student.dad_name if r.student.dad_name else '',BR(),I(r.student.phone if r.student.phone else ''),_class='textleft'))
			# tr.append(TD(r.student.mother_name if r.student.mother_name else '',BR(),I(r.student.phone1 if r.student.phone1 else ''),_class='textleft'))
			
			# table.append(tr)
			# i+=1
		# return DIV(table,_style="overflow-x:auto;")

	# def student_comment_lop(self):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_scholastic,define_teacher_classroom
		# define_classroom(db, False)
		# define_scholastic(db, False)
		# define_teacher_classroom(db, False)
		
		# inpday = INPUT(_type='text',_class='form-control datepicker',_name='inday',_value=request.now.strftime('%d/%m/%Y'))
		
		# scholastic = ''
		# from datetime import date
		# d = date.today()
		# rowsch = db((db.scholastic.start_date<= d)&(db.scholastic.end_date>=d)).select().first()
		# if rowsch: scholastic = rowsch.id
		
		# ##Danh sách lớp học
		# if auth.has_membership(role='admin'):
			# query = db.classroom.id>0
			# if scholastic !='':
				# query &= (db.classroom.scholastic==scholastic)
			# rowclass = db(query).select()
			# selectcr = SELECT(_name='classroom',_class='form-control')
			# for r in rowclass:
				# selectcr.append(OPTION('Lớp ',r.name,_value=r.id))
		# else:
			# list_cl = self.get_id_teacher()
			# if list_cl:
				# rowclass = db((db.teacher_classroom.teacher==list_cl)&(db.teacher_classroom.breakfast==True)&(db.teacher_classroom.classroom==db.classroom.id)&(db.classroom.scholastic==scholastic)).select()
				# selectcr = SELECT(_name='classroom',_class='form-control')
				# for r in rowclass:
					# selectcr.append(OPTION('Lớp ',r.classroom.name,_value=r.classroom.id))
		# ##TÌm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_student_comment_lop')	
		# ajax = "ajax('%s', ['classroom'], 'write_student_comment_lop')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Lọc dữ liệu',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		
		# table = TABLE(_class='table')
		# table.append(TR(TD(selectcr),TD(btnsearch,_style='width:100px;')))
		
		# div = DIV()
		# div.append(table)
		# div.append(DIV(self.write_student_comment_lop(''),_id='write_student_comment_lop'))
		# scr = SCRIPT('''$('#btn-firstcl').click();
					# ''')
		# div.append(scr)
		# return div
	
	# def write_student_comment_lop(self,classroom):
		# db = self.db
		# request = current.request
		
		# from datatables import define_classroom,define_scholastic,define_student
		# define_classroom(db, False)
		# define_student(db, False)
		# if not classroom:
			# return 'Ko co lop'
		# lop = db(db.classroom.id==int(classroom)).select().first()
		# from plugin_comment import Comment
		# content = DIV(_class='')
		# content.append(DIV(Comment(tablename='classroom',table_id=classroom).view_happy_hoc_sinh(title='Thông báo tới phụ huynh lớp %s'%(lop.name)),_class="col-md-12"))
		
		# return content
		
		
	# def student_list_comment(self):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_scholastic,define_teacher_classroom
		# define_classroom(db, False)
		# define_scholastic(db, False)
		# define_teacher_classroom(db, False)
		
		# inpday = INPUT(_type='text',_class='form-control datepicker',_name='inday',_value=request.now.strftime('%d/%m/%Y'))
		
		# scholastic = ''
		# from datetime import date
		# d = date.today()
		# rowsch = db((db.scholastic.start_date<= d)&(db.scholastic.end_date>=d)).select().first()
		# if rowsch: scholastic = rowsch.id
		
		# ##Danh sách lớp học
		# if auth.has_membership(role='admin'):
			# query = db.classroom.id>0
			# if scholastic !='':
				# query &= (db.classroom.scholastic==scholastic)
			# rowclass = db(query).select()
			# selectcr = SELECT(_name='classroom',_class='form-control')
			# for r in rowclass:
				# selectcr.append(OPTION('Lớp ',r.name,_value=r.id))
		# else:
			# list_cl = self.get_id_teacher()
			# if list_cl:
				# rowclass = db((db.teacher_classroom.teacher==list_cl)&(db.teacher_classroom.breakfast==True)&(db.teacher_classroom.classroom==db.classroom.id)&(db.classroom.scholastic==scholastic)).select()
				# selectcr = SELECT(_name='classroom',_class='form-control')
				# for r in rowclass:
					# selectcr.append(OPTION('Lớp ',r.classroom.name,_value=r.classroom.id))
		# ##TÌm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_student_list_comment')	
		# ajax = "ajax('%s', ['classroom'], 'write_student_list_comment')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Lọc dữ liệu',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		
		# table = TABLE(_class='table')
		# table.append(TR(TD(selectcr),TD(btnsearch,_style='width:100px;')))
		
		# div = DIV()
		# div.append(table)
		# div.append(DIV(self.write_student_list_comment(''),_id='write_student_list_comment'))
		# scr = SCRIPT('''$('#btn-firstcl').click();
					# ''')
		# div.append(scr)
		# return div
	
	# def write_student_list_comment(self,classroom):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_student,define_student_classroom
		# define_classroom(db, False)
		# student = define_student(db, False)
		# define_student_classroom(db, False)
		# from gluon.tools import prettydate
		
		# input,output = "%d/%m/%Y", "%Y-%m-%d"	

		# table = TABLE(_class='table table-bordered')	
		# table.append(THEAD(TR(TH('STT',_style='width:50px;'),TH('Tên học sinh'),TH('Sinh nhật'),TH('Địa chỉ'),TH('Liên lạc khi cần (chính)'),TH('Liên lạc khi cần (phụ)'))))
		# rows = db((db.student_classroom.classroom==classroom)&(db.student_classroom.student==db.student.id)&(db.student_classroom.aactive==True)).select(orderby=(db.student.lastname|db.student.firstname))
		# try:
			# from plugin_comment import Comment
			# comment = Comment().define_comment
			
			# hoc_sinhs = []
			# i = 1
			# table = TABLE(_class='table table-striped bring-up nth-2-center')
			# for r in rows:
				# hoc_sinhs.append(r.student.id)
				# num = Comment(tablename='student',table_id=r.student.id).read_count_id_read()
				# num2 = Comment(tablename='student',table_id=r.student.id).read_count()
				
				# urlcomment = URL(r=request,c='plugin_student',f='view_comment_hs',args=[r.student.id])
				# ajaxcomment = "ajax('%s', [], 'wr_view_comment')"%(urlcomment)
				
				
				# if num2 - num>0:
					# table.append(TR(TD(A(r.student.fullname,_onclick=ajaxcomment)),TD(A(I(_class='fa fa-comments'),' ',num2 - num,_class="btn btn-danger  btn-xs"))))
				# else:
					# table.append(TR(TD(A(r.student.fullname,_onclick=ajaxcomment)),TD(A(I(_class='fa fa-comments'),' ',num2 - num,_class="btn btn-primary btn-xs"))))
			
			# db_c = Comment().db
			# ul = DIV(_class='direct-chat',_id='wr_view_comment')
			# com_rows = db_c((db_c.tcomment.tablename=='student')&(db_c.tcomment.table_id.belongs(hoc_sinhs))).select(orderby=~db_c.tcomment.created_on)
			# for com in com_rows:
				# div = DIV(_class='box-body')
				# url_r = URL(r=request,c='plugin_student',f='read_by_user',args=[com.id])
				# ajax_r = "ajax('%s', [], 'wr_r_comment_%s')"%(url_r,com.id)
				
				# if Comment().read_by_user(com.id):
					# div.append(DIV(SPAN('Phụ huynh bé: %s'%(student[com.table_id].fullname),_class='direct-chat-name pull-left'),SPAN(I(com.created_on.strftime('%H:%M %d/%m/%Y'),' (',prettydate(com.created_on,T),')',_class='fa fa-clock-o'),_class='direct-chat-timestamp pull-left'),_class='direct-chat-info clearfix'))
					# div.append(SPAN(A(I(_class='fa fa-eye'),_class="btn btn-primary pull-left"),_class='direct-chat-img',_id="wr_r_comment_%s"%(com.id)))
					# div.append(SPAN(com.txtcontent,_class='direct-chat-text'))
				# else:
					# div.append(DIV(SPAN('Phụ huynh bé: %s'%(student[com.table_id].fullname),_class='direct-chat-name pull-left'),SPAN(I(com.created_on.strftime('%H:%M %d/%m/%Y'),' (',prettydate(com.created_on,T),')',_class='fa fa-clock-o'),_class='direct-chat-timestamp pull-left'),_class='direct-chat-info clearfix'))
					# div.append(SPAN(A(I(_class='fa fa-eye-slash'),_class="btn btn-danger pull-left",_onclick=ajax_r),_class='direct-chat-img',_id="wr_r_comment_%s"%(com.id)))
					# div.append(SPAN(com.txtcontent,_class='direct-chat-text'))
				# ul.append(DIV(div,_class="direct-chat-msg"))
			# return DIV(DIV(table,_class='col-lg-3'),DIV(DIV(ul),_class='col-lg-9'),_class='row')
		# except Exception,e: return e
			
	# def student_list_calendar(self):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_scholastic,define_teacher_classroom
		# define_classroom(db, False)
		# define_scholastic(db, False)
		# define_teacher_classroom(db, False)
		
		# inpday = INPUT(_type='text',_class='form-control datepicker',_name='inday',_value=request.now.strftime('%d/%m/%Y'))
		
		# scholastic = ''
		# from datetime import date
		# d = date.today()
		# rowsch = db((db.scholastic.start_date<= d)&(db.scholastic.end_date>=d)).select().first()
		# if rowsch: scholastic = rowsch.id
		
		# ##Danh sách lớp học
		# if auth.has_membership(role='admin'):
			# query = db.classroom.id>0
			# if scholastic !='':
				# query &= (db.classroom.scholastic==scholastic)
			# rowclass = db(query).select()
			# selectcr = SELECT(_name='classroom',_class='form-control')
			# for r in rowclass:
				# selectcr.append(OPTION('Lớp ',r.name,_value=r.id))
		# else:
			# list_cl = self.get_id_teacher()
			# if list_cl:
				# rowclass = db((db.teacher_classroom.teacher==list_cl)&(db.teacher_classroom.breakfast==True)&(db.teacher_classroom.classroom==db.classroom.id)&(db.classroom.scholastic==scholastic)).select()
				# selectcr = SELECT(_name='classroom',_class='form-control')
				# for r in rowclass:
					# selectcr.append(OPTION('Lớp ',r.classroom.name,_value=r.classroom.id))
		# ##TÌm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_student_list_calendar')	
		# ajax = "ajax('%s', ['classroom'], 'write_student_list_calendar')"%(urlsea)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Lọc dữ liệu',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		
		# table = TABLE(_class='table')
		# table.append(TR(TD(selectcr),TD(btnsearch,_style='width:100px;')))
		
		# div = DIV()
		# div.append(table)
		# div.append(DIV(self.write_student_list_calendar(''),_id='write_student_list_calendar'))
		# scr = SCRIPT('''$('#btn-firstcl').click();
					# ''')
		# div.append(scr)
		# return div
	
	# def write_student_list_calendar(self,classroom):
		# from plugin_table import DataTable
		# tablename = 'schedule_classroom'
		# data = DataTable(tablename=tablename,id=None,buttons=[],c="plugin_table",classroom=classroom)
		# # if Process.process_name==PROCESS1:
		# toolbars = data.toolbars()
		# content = DIV(toolbars,data.view(settings={"length":-1,"delete_on":False,"read_on":False}))
		# return content
		
		
	# def write_student_list_calendar(self,classroom):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_student,define_student_classroom,define_schedule_classroom
		# define_classroom(db, False)
		# student = define_student(db, False)
		# define_student_classroom(db, False)
		# define_schedule_classroom(db, False)
		# from gluon.tools import prettydate
		
		# input,output = "%d/%m/%Y", "%Y-%m-%d"	
		# rows = db((db.schedule_classroom.classroom==classroom)).select(orderby=~db.schedule_classroom.id)
		# content = DIV(_class='row')
		# from bootrap import Modals
		# # btnadd = Modals(caption=(xbtnadd),source=urladd,id='modals-addpatient')
		# if  auth.has_membership(role='admin'):
			# urladd = URL(r=request,c='plugin_student',f='form_add_schedule',args=[classroom],vars=dict(classroom=classroom))
			# xbtnadd = SPAN(SPAN(_class='fa fa-plus-circle')," Thêm mới" ,_class="btn btn-success",_title="Thêm mới thời khóa biểu")
			# ajax = "ajax('%s', [], 'wr_new_calendar')"%(urladd)
			# content.append(DIV(A(xbtnadd,_onClick=ajax),_class='col-lg-12'))	
		# div_top = DIV(_class='div_calendar')	
		# if len(rows)==0:
			
			# div_top.append(H2('Lớp chưa có thời khóa biểu nào'))	
			# content.append(DIV(DIV(div_top,_id='wr_new_calendar'),_class='col-lg-12'))
		# elif len(rows)==1:
			# row = rows[0]
			# urldelete = URL(r=request,c='plugin_student',f='delete_schedule',args=[classroom],vars=dict(id=row.id))
			# ajaxuncall = "confirmDelete(); ajax('%s', [], 'write_student_list_calendar')"%(urldelete)
			# inpremove = A(BUTTON(SPAN(_class='fa fa-remove'),_class='btn btn-danger circle'),_onclick=ajaxuncall,_title='Thay đổi trạng thái')
			
			# ngay = ''
			# if row.start_date:
				# ngay += 'Từ: %s'%(row.start_date.strftime('%d/%m/%Y'))
			# if row.end_date:
				# ngay += ' đến %s' %(row.end_date.strftime('%d/%m/%Y'))
			# div_top.append(DIV(inpremove,_class='text-right'))	
			# # div_top.append(H2('Chủ đề: %s'%(row.name),_style="text-align: center;"))	
			# # div_top.append(P(ngay,_style="text-align: center;"))	
			# div_top.append(XML(row.htmlcontent))	
			# # content.append(div_top)
			# content.append(DIV(DIV(div_top,_id='wr_new_calendar'),_class='col-lg-12'))
		# elif len(rows)>1:
			# table = TABLE(_class='table table-bordered')	
			# table.append(THEAD(TR(TH('STT',_style='width:50px;'),TH('Thời gian'),TH('Chủ đề'),TH('Chức năng'))))
			# i =0
			# for row in rows:
				# urldelete = URL(r=request,c='plugin_student',f='delete_schedule',args=[classroom],vars=dict(id=row.id))
				# ajaxuncall = "confirmDelete();ajax('%s', [], 'write_student_list_calendar')"%(urldelete)
				# inpremove = A(BUTTON(SPAN(_class='fa fa-remove'),_class='btn btn-danger circle'),_onclick=ajaxuncall,_title='Thay đổi trạng thái')
				
				# ngay = ''
				# if row.start_date:
					# ngay += 'Từ: %s'%(row.start_date.strftime('%d/%m/%Y'))
				# if row.end_date:
					# ngay += ' đến %s' %(row.end_date.strftime('%d/%m/%Y'))
				# if i==0:

					# # div_top.append(H2('Chủ đề: %s'%(row.name),_style="text-align: center;"))	
					# div_top.append(DIV(inpremove,_class='text-right'))	
					# # div_top.append(P(ngay,_style="text-align: center;"))	
					# div_top.append(XML(row.htmlcontent))	
				# else:
					# tr = TR()
					# urlread = URL(r=request,c='plugin_student',f='read_schedule',args=[row.id])
					# tr.append(TD(i))
					# tr.append(TD(Modals(caption=(ngay),source=urlread)))
					# tr.append(TD(Modals(caption=(row.name),source=urlread)))
					
					
					# tr.append(TD(inpremove))
					# table.append(tr)
				# i+=1
			# content.append(DIV(DIV(div_top,_id='wr_new_calendar'),H4('Thời khóa biểu cũ'),table,_class='col-lg-12'))
		# return content
		
	# def delete_schedule(self,id):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_schedule_classroom
		# define_schedule_classroom(db, False)
		# de = db(db.schedule_classroom.id==id).delete()
		# if de: return True
		# else: return False
		
	# def read_schedule(self,id):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_schedule_classroom
		# define_schedule_classroom(db, False)
		# content = DIV(_class='row')
		# input,output = "%d/%m/%Y", "%Y-%m-%d"	
		# row = db((db.schedule_classroom.id==id)).select().first()
		# if row:
			# ngay = ''
			# if row.start_date:
				# ngay += 'Từ: %s'%(row.start_date.strftime('%d/%m/%Y'))
			# if row.end_date:
				# ngay += ' đến %s' %(row.end_date.strftime('%d/%m/%Y'))
			# div_top = DIV()
			# div_top.append(H2('Chủ đề: %s'%(row.name),_style="text-align: center;"))	
			# div_top.append(P(ngay,_style="text-align: center;"))	
			# div_top.append(XML(row.htmlcontent))	
			# content.append(div_top)
		# else:
			# content.append(H2('Thời khóa biểu lỗi'))
		# return content

		
	# def write_student_breakfast(self,classroom,inday):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_student,define_student_classroom,define_student_breakfast
		# define_classroom(db, False)
		# define_student(db, False)
		# define_student_classroom(db, False)
		# define_student_breakfast(db, False)
		
		# input,output = "%d/%m/%Y", "%Y-%m-%d"	

		# table = TABLE(_class='table table-bordered')	
		# table.append(THEAD(TR(TH('STT',_style='width:50px;'),TH('Tên học sinh'),TH('Có đi học'))))
		# rows = db((db.student_classroom.classroom==classroom)&(db.student_classroom.student==db.student.id)&(db.student_classroom.aactive==True)).select(orderby=(db.student.lastname|db.student.firstname))
		# # rows = db(db.student.id>0).select()
		# i = 1
		# for r in rows:
			# tr = TR(i)
			# tr.append(TD(r.student.fullname))
			# cou = 0
			# if (inday!=''):
				# cinday= datetime.datetime.strptime(inday,input).strftime(output)
				# cou = db((db.student_breakfast.student_classroom==r.student.id)&(db.student_breakfast.dateeat==cinday)).count()
			# if cou>0:
				# urluncall = URL(r=request,c='plugin_student',f='unactive_breakfast',vars=dict(student=r.student.id,inday=inday))
				# ajaxuncall = "ajax('%s', [], 'iscall_active%s')"%(urluncall,r.student.id)
				# inpcall = INPUT(_type='checkbox',_name='is_breakfast',_checked='checked',_onchange=ajaxuncall,_style='width:30px;height:30px')
			# else:
				# urlcall = URL(r=request,c='plugin_student',f='active_breakfast',vars=dict(student=r.student.id,inday=inday))
				# ajaxcall = "ajax('%s', [], 'iscall_active%s')"%(urlcall,r.student.id)
				# inpcall = INPUT(_type='checkbox',_name='is_breakfast',_onchange=ajaxcall,_style='width:30px;height:30px')
					
			# tr.append(TD(inpcall,_id='iscall_active'+str(r.student.id),_style='text-align:center;'))
			
			# table.append(tr)
			# i+=1
		# return table
		
	# ###########################################
	# ##Đánh giá học sinh trong ngày
	# def student_follow(self):
		
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_scholastic, define_teacher_classroom,define_question
		# define_classroom(db, False)
		# define_scholastic(db, False)
		# define_teacher_classroom(db, False)
		# question = define_question(db, False)
		
		# inpday = INPUT(_type='text',_class='form-control datepicker',_name='inday',_value=request.now.strftime('%d/%m/%Y'))
		
		# scholastic = ''
		# from datetime import date
		# d = date.today()
		# rowsch = db((db.scholastic.start_date<= d)&(db.scholastic.end_date>=d)).select().first()
		# if rowsch: scholastic = rowsch.id
				
		# ##Danh sách lớp học
		
		# if auth.has_membership(role='admin'):
			# query = db.classroom.id>0
			# if scholastic !='':
				# query &= (db.classroom.scholastic==scholastic)
			# rowclass = db(query).select()
			# selectcr = SELECT(_name='classroom',_class='form-control')
			# for r in rowclass:
				# selectcr.append(OPTION('Lớp ',r.name,_value=r.id))
		
		# else:
			
			# list_cl = self.get_id_teacher()
			# if list_cl:
				
				# # rowclass = db((db.teacher_classroom.teacher==list_cl)&(db.teacher_classroom.follow==True)&(db.teacher_classroom.classroom==db.classroom.id)&(db.classroom.scholastic==scholastic)).select()
				# rowclass = db((db.teacher_classroom.teacher==list_cl)&(db.teacher_classroom.follow==True)&(db.teacher_classroom.classroom==db.classroom.id)).select()
				# selectcr = SELECT(_name='classroom',_class='form-control')
				# for r in rowclass:
					# selectcr.append(OPTION('Lớp ',r.classroom.name,_value=r.classroom.id))
		
		
		
		# tieu_chi = UL(_class='search_tieuchi')
		# v_tieu_chi =['classroom','inday',]
		# rows_q =  db(question.id>0).select(orderby=db.question.vi_tri)
		# for q in rows_q:
			# if q.id in [1,2,3,5]:
				# tieu_chi.append(LI(INPUT(_type='checkbox',_name='tieu_chi_%s'%(q.id),_checked=True),SPAN(q.name)))
			# else:
				# tieu_chi.append(LI(INPUT(_type='checkbox',_name='tieu_chi_%s'%(q.id)),SPAN(q.name)))
			# v_tieu_chi.append('tieu_chi_%s'%(q.id))
		
		
		# ##TÌm kiếm
		# urlsea = URL(r=request,c='plugin_student',f='search_student_follow')	
		# ajax = "ajax('%s', %s, 'write_student_follow')"%(urlsea,v_tieu_chi)
		# btnsearch = SPAN(SPAN(_class='fa fa-search'), ' Tìm kiếm',_id='btn-firstcl',_class='btn btn-primary',_onClick=ajax)
		
		
		# table = TABLE(_class='table')
		# table.append(TR(TD(inpday),TD(selectcr),TD(btnsearch,_style='width:100px;vertical-align: middle;',_rowspan=2)))
		# table.append(TR(TD(tieu_chi,_colspan=2)))
		
		# div = DIV()
		# div.append(table)
		# div.append(P("(*) Lưu ý: Mặc định sẽ không còn được tích sẵn, hãy tích vào các tiêu chí muốn đánh giá để phù hợp theo ngày.",_style='color:#F00;'))
		# div.append(DIV(self.write_student_follow('',request.now.strftime('%d/%m/%Y')),_id='write_student_follow'))
		# # scr = SCRIPT('''$('#btn-firstcl').click();
					# # ''')
		# # div.append(scr)
		# return div
	
	# def write_student_follow(self,classroom,inday,tieu_chi=[]):
		
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# import datetime
		# from datatables import define_classroom,define_student,define_student_classroom,define_student_breakfast,define_student_aq,define_fees_month,define_question
		# define_classroom(db, False)
		# define_student(db, False)
		# define_student_classroom(db, False)
		# define_student_breakfast(db, False)
		# define_student_aq(db, False)
		# fees_month = define_fees_month(db, False)
		# question = define_question(db, False)
		# l_tieu_chi=''
		
		
		# input,output = "%d/%m/%Y", "%Y-%m-%d"	
		
		# # from datetime import datetime
		# # time_now = datetime.strptime(inday, '%d/%m/%Y')
		# # if T(time_now.strftime("c_%a"))=="CN":
			# # return H2("Chủ Nhật không đánh giá")
		
		# rows = db((db.student_classroom.classroom==classroom)&(db.student_classroom.student==db.student.id)&(db.student_classroom.aactive==True)).select(orderby=(db.student.lastname|db.student.firstname))
		# # rows = db(db.student.id>0).select()
		# try:
			# i = 1
			# div_l = DIV(_class='row update_status')
			
			# if len(tieu_chi) ==0:
				# row_q = db(question.id>0).select(orderby=db.question.vi_tri)
			# else:
				# if not isinstance(tieu_chi,list):
					# tieu_chi = [tieu_chi]
				# row_q = db(question.id.belongs(tieu_chi)).select(orderby=db.question.vi_tri)
			# for tc in tieu_chi:
				# if l_tieu_chi=="":
				
					# l_tieu_chi += '%s'%(tc)
				# else:
					# l_tieu_chi += '_%s'%(tc)	
			# for r in rows:
				# div_l.append(DIV(self.get_question(r.student.id,False,l_tieu_chi,row_q),_id='wr_hs_%s'%(r.student.id),_class='col-lg-6'))
				# i+=1
			
			# return div_l
		# except Exception,e: return e
		
	
	# ## View hiển thị đánh giá	
	# def get_question (self,hs_id,status,l_tieu_chi,row_q):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_student, define_question,define_answer,define_answer,define_student_aq,define_student_breakfast,define_student_aq,define_fees_month
		# hoc_sinh = define_student(db, False)
		# question = define_question(db, False)
		# answer = define_answer(db, False)
		# hoc_sinh_aq = define_student_aq(db, False)
		# fees_month = define_fees_month(db, False)
		# student_breakfast = define_student_breakfast(db, False)
		# hs = db(hoc_sinh.id==hs_id).select().first()
		
		# content_body = DIV()
		# list_vars =['inday']
		
		# from datetime import datetime
		# time_now = datetime.strptime(request.vars.inday, '%d/%m/%Y')
		
		
		# rows_aq = db((db.student_aq.student==hs_id)&(db.student_aq.days_check==time_now)).select()
		# if len(rows_aq)>0:
			# div_hs = DIV(_class='panel panel-default is_checkin')
		# else:
			# div_hs = DIV(_class='panel panel-default')
		# div_hs.append(DIV(B(hs.fullname),_class='panel-heading'))
		# # st_br = db((student_breakfast.student_classroom==hs_id)&(student_breakfast.dateeat==hs_id)).select()	
		# da_co =0
		# for q in row_q:
			# content_body.append(H2(q.name,_class='name_question'))
			# row_hs_aq = db((hoc_sinh_aq.question==q.id)&(hoc_sinh_aq.student==hs_id)&(hoc_sinh_aq.days_check==time_now)).select().first()
			
			# if q.question_type=='text':
				# if row_hs_aq:
					# content_body.append(TEXTAREA(row_hs_aq.name,_class='answer_textarea',_name='question_%s_hs_%s'%(q.id,hs.id)))
				# else:
					# content_body.append(TEXTAREA(_class='answer_textarea',_name='question_%s_hs_%s'%(q.id,hs.id)))
				# list_vars.append('question_%s_hs_%s'%(q.id,hs.id))
			# elif q.question_type=='radio':
				# row_a = db(answer.question==q.id).select()
				# i = 1
				# list_vars.append('question_%s_hs_%s'%(q.id,hs.id))
				# if row_hs_aq:
					# for a in row_a:
						# if str(a.id)==row_hs_aq.name:
							# content_body.append(LABEL(a.name,INPUT(_type='radio',_name='question_%s_hs_%s'%(q.id,hs.id),_checked="checked",_value=a.id),SPAN(_class='checkmark'),_class="container_input"))
						# else:
							# content_body.append(LABEL(a.name,INPUT(_type='radio',_name='question_%s_hs_%s'%(q.id,hs.id),_checked=False,_value=a.id),SPAN(_class='checkmark'),_class="container_input"))
						# i+=1
				# else:	
					# for a in row_a:
						# # if i==1:
							# # content_body.append(LABEL(a.name,INPUT(_type='radio',_name='question_%s_hs_%s'%(q.id,hs.id),_checked="checked",_value=a.id),SPAN(_class='checkmark'),_class="container_input"))
						# # else:
						# content_body.append(LABEL(a.name,INPUT(_type='radio',_name='question_%s_hs_%s'%(q.id,hs.id),_checked=False,_value=a.id),SPAN(_class='checkmark'),_class="container_input"))
						# i+=1
			# else:
				# row_a = db(answer.question==q.id).select()
				# i = 1
				# list_vars.append('question_%s_hs_%s'%(q.id,hs.id))
				# if row_hs_aq:
					# for a in row_a:
						# if a.id==row_hs_aq.name:
							# content_body.append(LABEL(a.name,INPUT(_type='radio',_name='question_%s_hs_%s'%(q.id,hs.id),_checked="checked",_value=a.id),SPAN(_class='checkmark'),_class="container_input"))
						# else:
							# content_body.append(LABEL(a.name,INPUT(_type='radio',_name='question_%s_hs_%s'%(q.id,hs.id),_checked=False,_value=a.id),SPAN(_class='checkmark'),_class="container_input"))
						# i+=1
				# else:	
					# for a in row_a:
						# # if i==1:
							# # content_body.append(LABEL(a.name,INPUT(_type='radio',_name='question_%s_hs_%s'%(q.id,hs.id),_checked="checked",_value=a.id),SPAN(_class='checkmark'),_class="container_input"))
						# # else:
						# content_body.append(LABEL(a.name,INPUT(_type='radio',_name='question_%s_hs_%s'%(q.id,hs.id),_checked=False,_value=a.id),SPAN(_class='checkmark'),_class="container_input"))
						# i+=1
			# if row_hs_aq:	
				# da_co +=1
				# if q.id==3:
					# if row_hs_aq.name in ['7','8']:
						# break
		

		# from datetime import datetime
		
		# f_month = int(time_now.strftime('%m'))
		# f_year =int(time_now.strftime('%Y'))
		# if f_month +1<12:
			# f_month_check = f_month +1
			# f_year_check  = f_year
		# else:
			# f_month_check = 1
			# f_year_check  = f_year+1
		
		# check =  db((fees_month.select_month==f_month_check )&(fees_month.select_year==f_year_check)).count()
		
		# if (check==0) or auth.has_membership(role='admin'):
			# div_b = DIV(_style="display: inline-block;width: 100%;")
			# ajax = "ajax('%s', %s,'wr_hs_%s')"%(URL(r=request,f='update_status_act',args=[hs.id],vars=dict(tieu_chi=l_tieu_chi)),list_vars,hs_id)
			# div_b.append(A(I(_class='fa fa-save'),' Lưu đánh giá',_onclick=ajax,_class='btn btn-primary'))	
			# if da_co>0:
				# ajax = "ajax('%s', %s,'wr_hs_%s')"%(URL(r=request,f='delete_status_act',args=[hs.id],vars=dict(tieu_chi=l_tieu_chi)),list_vars,hs_id)
				# div_b.append(A(I(_class='fa fa-trash-o'),' Xóa đánh giá',_onclick=ajax,_class='btn btn-danger'))	
			# content_body.append(div_b)	
		# else:
			# content_body.append(B("Thông báo học phí %s/%s đã được tạo."%(f_month,f_year),_style='text-align:center; color:#f00;'))
		# div_hs.append(DIV(content_body,_class='panel-body'))
		# return div_hs	
		
	# ## View hiển thị đánh giá cho phụ huynh
	# def get_question_by_breakfast(self,breakfast_id,status=False):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_student, define_question,define_answer,define_answer,define_student_aq,define_student_breakfast
		# hoc_sinh = define_student(db, False)
		# question = define_question(db, False)
		# answer = define_answer(db, False)
		# hoc_sinh_aq = define_student_aq(db, False)
		# student_breakfast = define_student_breakfast(db, False)
		
		# breakfast = db(db.student_breakfast.id==breakfast_id).select().first()
		# if not breakfast.aactive:
			# return H2(breakfast.description)
		# hs_id = breakfast.student_classroom
		
		# hs = db(hoc_sinh.id==hs_id).select().first()
		# row_q = db(question.id>0).select(orderby=db.question.vi_tri)
		# # row_q = db(question.id>0).select()
		# content_body = DIV()
		# list_vars =['inday']
		
		# from datetime import datetime
		# time_now = breakfast.dateeat
		
		# if status:
			# div_hs = DIV(_class='panel panel-default is_checkin')
		# else:
			# div_hs = DIV(_class='panel panel-default')
		# div_hs.append(DIV(B(hs.fullname),_class='panel-heading'))
		# # st_br = db((student_breakfast.student_classroom==hs_id)&(student_breakfast.dateeat==hs_id)).select()	
		# for q in row_q:
			# content_body.append(H4(q.name,_class='name_question'))
			# row_hs_aq = db((hoc_sinh_aq.question==q.id)&(hoc_sinh_aq.student==hs_id)&(hoc_sinh_aq.days_check==time_now)).select().first()
			# if q.question_type=='text':
				# if row_hs_aq:
					# content_body.append(P(row_hs_aq.name))
				# else:
					# content_body.append(P('...'))
				# list_vars.append('question_%s_hs_%s'%(q.id,hs.id))
			# elif q.question_type=='radio':
				# row_a = db(answer.question==q.id).select()
				# i = 1
				# list_vars.append('question_%s_hs_%s'%(q.id,hs.id))
				# ul = DIV(_class='answer_list')
				# if row_hs_aq:
					# for a in row_a:
						# if str(a.id)==row_hs_aq.name:
							# ul.append(LI(B(a.name),_class='active_ok col-md-3'))
						# else:
							# ul.append(LI(a.name,_class='col-md-3'))
						# i+=1
				# content_body.append(ul)
			# else:
				# row_a = db(answer.question==q.id).select()
				# i = 1
				# list_vars.append('question_%s_hs_%s'%(q.id,hs.id))
				# ul = DIV(_class='answer_list')
				# if row_hs_aq:
					# for a in row_a:
						# if a.id==row_hs_aq.name:
							# ul.append(LI(B(a.name),_class='active_ok col-md-3'))
						# else:
							# ul.append(LI(a.name,_class='col-md-3'))
						# i+=1
				# content_body.append(ul)	
		
		# div_hs.append(DIV(content_body,_class='panel-body get_question_by_breakfast'))
		# return div_hs
		
	
	# ######################################
	# ##Danh sách học sinh trong lớp học
	# def list_student_class(self,idclass):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_student, define_student_classroom
		# define_student(db, False)
		# define_student_classroom(db, False)
		# from bootrap import Modals
		
		# table = TABLE(_class='table table-bordered table-center')
		# table.append(THEAD(TR(TH('STT',_style='width:60px;'),TH('Mã học sinh',_style='width:120px;'),TH('Tên học sinh'),TH('Ngày sinh'),TH('Giới tính',_style='width:80px;'),TH('Họ tên bố'),TH('Họ tên mẹ'),TH('Chức năng',_style='width:80px;'))))
		# rows = db((db.student_classroom.classroom==idclass)&(db.student_classroom.student==db.student.id)&(db.student_classroom.aactive==True)).select(orderby=(db.student.lastname|db.student.firstname))
		# i = 1
		# for r in rows:
			# tr = TR()
			# tr.append(TD(i))
			# tr.append(TD(r.student.code if r.student.code else ''))
			# tr.append(TD(r.student.fullname if r.student.fullname else '',_class='textleft'))
			# tr.append(TD(r.student.birthday.strftime('%d/%m/%Y') if r.student.birthday else ''))
			# tr.append(TD(r.student.sex if r.student.sex else ''))
			
			# tr.append(TD(r.student.dad_name if r.student.dad_name else '',BR(),I(r.student.phone if r.student.phone else ''),_class='textleft'))
			# tr.append(TD(r.student.mother_name if r.student.mother_name else '',BR(),I(r.student.phone1 if r.student.phone1 else ''),_class='textleft'))
			
			# urldelete = URL(r=request,c='plugin_student',f='delete_student_classroom',vars=dict(idclass=idclass,id=r.student_classroom.id))
			# inpremove = A(BUTTON(SPAN(_class='fa fa-remove'),_class='btn btn-danger circle'),_href=urldelete,_onclick="return confirmDelete()",_title='Xóa')
			# tr.append(TD(SPAN(inpremove)))
			# table.append(tr)
			# i+=1
			
		# div = DIV(_id='explorer_view')
		# urladd = URL(r=request,c='plugin_student',f='form_student_class',vars=dict(idclass=idclass))
		# xbtnadd = SPAN(SPAN(_class='fa fa-plus-circle')," Thêm mới học sinh" ,_class="btn btn-success",_title="Thêm mới học sinh")
		# btnadd = Modals(caption=(xbtnadd),source=urladd,id='modals-addpatient')	
		
		# urlmover= URL(r=request,c='plugin_student',f='mover_student_class',vars=dict(idclass=idclass))
		# ajax = "ajax('%s', ['student_id'], 'table_content')"%(urlmover)
		# xbtnmover = SPAN(SPAN(_class='fa fa-mail-forward')," Chuyển lớp" ,_onclick=ajax,_class="btn btn-success button_process_False",_title="Chuyển lớp học sinh")
		# # btn_mover = Modals(caption=(xbtnmover),source=urlmover,id='modals-mover')	
		
		# url_lever= URL(r=request,c='plugin_student',f='form_student_class',vars=dict(idclass=idclass))
		# xbtn_lever = SPAN(SPAN(_class='fa fa-mail-forward')," Lên lớp" ,_class="btn btn-success",_title="Lên lớp")
		# btn_lever = Modals(caption=(xbtn_lever),source=url_lever,id='modals-lever')	
		
		# # btnadd = A(xbtnadd,_href=urladd,id='modals-addpatient')	
		
		# # div.append(DIV(btnadd,xbtnmover,btn_lever))
		# div.append(DIV(btnadd))
		# div.append(DIV(table,_id='table_content',_style='overflow-x:auto;'))
		# scr ='''
		# <script type="text/javascript">
			# function CheckAll() {
				# $('#explorer_view :checkbox').each(function () {
					# $(this).prop('checked', document.getElementById("check_all").checked);
				# });         
			# };  
		# </script>		
		# '''
		# div.append(XML(scr))
		# return div
		
	# ##Form danh sách học sinh lớp học
	# def form_student_class(self,idclass):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_student,define_classroom,define_student_classroom,define_course
		# define_student(db, False)
		# define_classroom(db, False)
		# define_student_classroom(db, False)
		# define_course(db, False)
		# import datetime
		
		# rowcl = db.classroom(idclass)
		# namecl = ''
		# if rowcl:
			# namecl = rowcl.name if rowcl.name else ''			
		# table = TABLE(_class='table')
		# table.append(TR(TH('Lớp'),TD(namecl)))
		
		# ##Danh sách khóa học (lọc học sinh theo khóa)	
		# # rowcou = db(db.course.id>0).select()
		# # selectcou = SELECT(OPTION('-- Chọn khóa học --',_value=''),_name='course',_class='form-control')
		# # for rc in rowcou:
			# # selectcou.append(OPTION(rc.name,_value=rc.id))
		# # labelcou = LABEL('Khóa học')
		# # divcou = DIV(labelcou,selectcou,_class='form-group')
		# # table.append(TR(TD(divcou,_colspan='2')))
			
		# ##Danh sách học sinh
		# rowstu = db(db.student.aactive==True).select()
		# tabstu = TABLE(_class='table table-bordered table-center table-student-class')
		# tabstu.append(THEAD(TR(TH('STT'),TH('#'),TH('Mã học sinh'),TH('Họ tên'),TH('Ngày sinh'))))
		# i = 1
		# for r in rowstu:
			# tr = TR(i)
			# check = db((db.student_classroom.student==r.id)&(db.student_classroom.aactive==True)).select().first()
			# if check:
				# class_now = db.classroom(check.classroom)
				# try:
					# inpradio = SPAN(class_now.name)
				# except:
					# inpradio = SPAN("Lớp học đã xóa")
			# else:
				# inpradio = INPUT(_type='checkbox',_name='idstudent'+str(r.id),_value=r.id,_id='radiostudent'+str(i),_class='uncheck',_style='height:25px;width:25px;')
			# tr.append(TD(inpradio))
			# tr.append(TD(r.code))
			# tr.append(TD(r.fullname))
			# tr.append(TD(r.birthday.strftime('%d/%m/%Y') if r.birthday else ''))
			# # tr.append(TD(r.course if r.course else ''))
			# tabstu.append(tr)
			# i+=1
		
		# divform = DIV()
		# divform.append(DIV(table))
		# ##Ô tìm kiếm
		# inpsearch = INPUT(_type='text',_class='form-control',_id='seastudent_classroom',_onkeyup='funcTimKiem();')
		# divform.append(DIV(inpsearch))
		# divform.append(DIV(tabstu))
		
		# url = URL(r=request,c='plugin_student',f='update_student_class',vars=dict(idclass=idclass))
		# div = DIV(FORM(divform,INPUT(_type='submit',_id='act_submit',_value=T('Submit'),_style='display:none;'),_id="form1",_name="form1",_action=url,_onsubmit="return validateFormStudent()"),_id='div_create_patient')
		
		# div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_class='btn btn-danger closemodals',_style='margin-left:5px;'),_class='text-center'))
		# script = SCRIPT("""$('#act_submit_ao').click(function(){
								# $('#act_submit').click();
							# });
							# $('.closemodals').attr({'data-dismiss':'modal'});
							# """)
		# div.append(script)
		# scrfind = SCRIPT('''$('#seastudent_classroom').attr({'placeholder':'Nhập tên học sinh'});
				# function funcTimKiem(){
					# var keyword = $('#seastudent_classroom').val().toUpperCase();	 //Dữ liệu trong input tìm kiếm
					# $('tr').show();
					# //Lặp tất cả các dòng tr
					# $('.table-student-class tr>td:nth-child(4)').each(function(){
						# var x = $(this).text().toUpperCase();
						
						# if (x.indexOf(keyword)<0){ //Nếu dữ liệu tìm kiếm không có thì ẩn đi
							# $(this).parent().hide();
						# }
				# });					
				# }
		
		# ''')
		# div.append(scrfind)
		# return div
	
	# ######################################
	# ##Danh sách Giáo viên quản lý
	# def list_teacher_class(self,idclass):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_teacher, define_teacher_classroom
		# define_teacher(db, False)
		# define_teacher_classroom(db, False)
		# from bootrap import Modals
		
		# table = TABLE(_class='table table-bordered table-center')
		# table.append(THEAD(TR(TH(INPUT(_class='',_type='checkbox',_name='check_all',_id='check_all',_onclick="CheckAll();"),_style='width:60px;'),TH('STT',_style='width:60px;'),TH('Mã giáo viên',_style='width:120px;'),TH('Tên giáo viên'),TH('Điểm danh',_style='width:100px;'),TH('Đánh giá',_style='width:100px;'),TH('Sửa ngày',_style='width:100px;'),TH('Chức năng',_style='width:100px;'))))
		# rows = db((db.teacher_classroom.classroom==idclass)&(db.teacher_classroom.teacher==db.teacher.id)&(db.teacher.aactive==True)).select()
		# i = 1
		# for r in rows:
			# tr = TR(INPUT(_class='student_id',_type='checkbox',_name='student_id',_value=r.teacher.id))
			# tr.append(TD(i))
			# tr.append(TD(r.teacher.code if r.teacher.code else ''))
			# tr.append(TD(r.teacher.fullname if r.teacher.fullname else ''))
			# if r.teacher_classroom.breakfast:
				# tr.append(TD(A(IMG(_src=URL(r=request,c='static',f='images/ok.png'),_style='width:30px;'),_href=URL(r=request,c='plugin_student',f='update_breakfast',args=[r.teacher_classroom.id,1],vars=dict(idclass=idclass)))))
			# else:
				# tr.append(TD(A(IMG(_src=URL(r=request,c='static',f='images/false.png'),_style='width:30px;'),_href=URL(r=request,c='plugin_student',f='update_breakfast',args=[r.teacher_classroom.id,0],vars=dict(idclass=idclass)))))
			# if r.teacher_classroom.follow:
				# tr.append(TD(A(IMG(_src=URL(r=request,c='static',f='images/ok.png'),_style='width:30px;'),_href=URL(r=request,c='plugin_student',f='update_follow',args=[r.teacher_classroom.id,1],vars=dict(idclass=idclass)))))
			# else:
				# tr.append(TD(A(IMG(_src=URL(r=request,c='static',f='images/false.png'),_style='width:30px;'),_href=URL(r=request,c='plugin_student',f='update_follow',args=[r.teacher_classroom.id,0],vars=dict(idclass=idclass)))))
			
			# if r.teacher_classroom.edit_date:
				# tr.append(TD(A(IMG(_src=URL(r=request,c='static',f='images/ok.png'),_style='width:30px;'),_href=URL(r=request,c='plugin_student',f='update_edit_date',args=[r.teacher_classroom.id,1],vars=dict(idclass=idclass)))))
			# else:
				# tr.append(TD(A(IMG(_src=URL(r=request,c='static',f='images/false.png'),_style='width:30px;'),_href=URL(r=request,c='plugin_student',f='update_edit_date',args=[r.teacher_classroom.id,0],vars=dict(idclass=idclass)))))
			
			# urldelete = URL(r=request,c='plugin_student',f='delete_teacher_classroom',vars=dict(idclass=idclass,id=r.teacher_classroom.id))
			# inpremove = A(BUTTON(SPAN(_class='fa fa-remove'),_class='btn btn-danger circle'),_href=urldelete,_onclick="return confirmDelete()",_title='Xóa')
			# tr.append(TD(SPAN(inpremove)))
			# table.append(tr)
			# i+=1
			
		# div = DIV(_id='explorer_view')
		# urladd = URL(r=request,c='plugin_student',f='form_teacher_class',vars=dict(idclass=idclass))
		# xbtnadd = SPAN(SPAN(_class='fa fa-plus-circle')," Thêm mới giáo viên quản lý" ,_class="btn btn-success",_title="Thêm mới giáo viên quản lý")
		# btnadd = Modals(caption=(xbtnadd),source=urladd,id='modals-addteacher')	
		
		# div.append(DIV(btnadd))
		# div.append(DIV(table,_id='table_content'))
		# scr ='''
		# <script type="text/javascript">
			# function CheckAll() {
				# $('#explorer_view :checkbox').each(function () {
					# $(this).prop('checked', document.getElementById("check_all").checked);
				# });         
			# };  
		# </script>		
		# '''
		# div.append(XML(scr))
		# return div
		
	# ##Form danh sách học sinh lớp học
	# def form_teacher_class(self,idclass):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_teacher,define_classroom,define_teacher_classroom,define_course
		# define_teacher(db, False)
		# define_classroom(db, False)
		# define_teacher_classroom(db, False)
		# define_course(db, False)
		# import datetime
		
		# rowcl = db.classroom(idclass)
		# namecl = ''
		# if rowcl:
			# namecl = rowcl.name if rowcl.name else ''			
		# table = TABLE(_class='table')
		# table.append(TR(TH('Lớp'),TD(namecl)))
		
		# rowstu = db(db.teacher.id>0).select()
		# tabstu = TABLE(_class='table table-bordered table-center table-student-class')
		# tabstu.append(THEAD(TR(TH('STT'),TH('#'),TH('Mã giáo viên'),TH('Họ tên'))))
		# i = 1
		# for r in rowstu:
			# kiemtra = db((db.teacher_classroom.teacher==r.id)&(db.teacher_classroom.classroom==idclass)).select().first()
			# tr = TR(i)
			# if kiemtra:
				# inpradio = SPAN('Đã có')
			# else:
				# inpradio = INPUT(_type='checkbox',_name='idstudent'+str(r.id),_value=r.id,_id='radiostudent'+str(i),_class='uncheck',_style='height:25px;width:25px;')
			# tr.append(TD(inpradio))
			# tr.append(TD(r.code))
			# tr.append(TD(r.fullname))
			# # tr.append(TD(r.course if r.course else ''))
			# tabstu.append(tr)
			# i+=1
		
		# divform = DIV()
		# divform.append(DIV(table))
		# ##Ô tìm kiếm
		# inpsearch = INPUT(_type='text',_class='form-control',_id='seastudent_classroom',_onkeyup='funcTimKiem();')
		# divform.append(DIV(inpsearch))
		# divform.append(DIV(tabstu))
		
		# url = URL(r=request,c='plugin_student',f='update_teacher_class',vars=dict(idclass=idclass))
		# div = DIV(FORM(divform,INPUT(_type='submit',_id='act_submit',_value=T('Submit'),_style='display:none;'),_id="form1",_name="form1",_action=url),_id='div_create_patient')
		
		# div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_class='btn btn-danger closemodals',_style='margin-left:5px;'),_class='text-center'))
		# script = SCRIPT("""$('#act_submit_ao').click(function(){
								# $('#act_submit').click();
							# });
							# $('.closemodals').attr({'data-dismiss':'modal'});
							# """)
		# div.append(script)
		# scrfind = SCRIPT('''$('#seastudent_classroom').attr({'placeholder':'Nhập tên giáo viên'});
				# function funcTimKiem(){
					# var keyword = $('#seastudent_classroom').val().toUpperCase();	 //Dữ liệu trong input tìm kiếm
					# $('tr').show();
					# //Lặp tất cả các dòng tr
					# $('.table-student-class tr>td:nth-child(4)').each(function(){
						# var x = $(this).text().toUpperCase();
						
						# if (x.indexOf(keyword)<0){ //Nếu dữ liệu tìm kiếm không có thì ẩn đi
							# $(this).parent().hide();
						# }
				# });					
				# }
		
		# ''')
		# div.append(scrfind)
		# return div
		

	# ###Lấy ID giáo viên từ tài khoản
	# def get_classroom_teacher(self):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_classroom
		# define_classroom(db, False)
		# auth_user = db.auth_user(auth.user_id)
		# idteacher = ''
		# if auth_user:
			# idteacher = auth_user.teacher if auth_user.teacher else ''
		
		# rows = db(db.classroom.teacher==idteacher).select()
		# list_cl = []
		# for r in rows:
			# list_cl.append(r.id)
		# return list_cl
	
	# ###Lấy ID giáo viên từ tài khoản
	# def get_id_teacher(self):
		# db = self.db
		# request = current.request
		# T = current.T
		# auth = self.auth
		# from datatables import define_classroom
		# define_classroom(db, False)
		# auth_user = db.auth_user(auth.user_id)
		# if auth_user.teacher:
			# # return auth_user.teacher
		# else: return None
	
	
	
		
	





	
		
		