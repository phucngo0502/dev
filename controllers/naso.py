# -*- coding: utf-8 -*-

from plugin_cms import Cms
cms = Cms()


@auth.requires(auth.has_membership(role='admin'))	
def index():
	content = H2("Naso")
	return dict(content=content)
	
from salesman import Salesman
salesman = Salesman()
from datetime import date

##########################################
##Quản lý Đại lý
##########################################

##Màn hình danh sách đại lý
@auth.requires_login()	
def list_salesman():
	title = SPAN(SPAN(_class='fa fa-2x fa-address-card'),' Quản lý thông tin Đại lý - CTV')
	page = request.vars.page if request.page else 0
	content = salesman.list_salesman(page)
	return dict(content = content,title = title)
	
##Tìm kiếm tại màn hình danh sách Giáo viên
@auth.requires_login()	
def search_salesman():
	page = request.vars.page if request.vars.page else 0
	code = request.vars.fcode if request.vars.fcode else ''
	fullname = request.vars.ffullname if request.vars.ffullname else ''
	sex = request.vars.fsex if request.vars.fsex else ''
	address = request.vars.faddress if request.vars.faddress else ''	
	fstatus = True if request.vars.fstatus== "Đang hoạt động" else False
	content =  salesman.write_table_salesman(code,fullname,sex,address,page,fstatus)
	return content

# ##Form giáo viên: Thêm mới, chỉnh sửa
# @auth.requires_login()	
# def form_teacher():
	# id = request.vars.id if request.vars.id else ''
	# content = salesman.form_teacher(id)
	# response.view = "plugin_student/form_student.html"
	# return dict(content =content)
	
# ##Thêm, sửa giáo viên trong database
# @auth.requires_login()	
# def update_teacher():
	# from datatables import define_teacher
	# define_teacher(db, False)
	# import datetime
	# id = request.vars.id if request.vars.id else ''
	# var = {}
	# for key in request.vars.keys():
		# if key in db.teacher.fields:
			# var[key]=request.vars[key]
	# input,output = "%d/%m/%Y", "%Y-%m-%d"
	# if request.vars.birthday:
		# var['birthday'] = datetime.datetime.strptime(request.vars.birthday,input).strftime(output)
	# ##Tạo mã giáo viên tự động
	# #Mã học sinh = 'GV' + mã số (4 chữ số)
			
	# lenms = 4 ##độ dài của Số thứ tự mã số
	# lastteacher = db(db.teacher.id>0).select().last()
	# newstt = 1 #số thứ tự đầu tiên
	# if lastteacher:
		# xcode = lastteacher.code if lastteacher.code else ''
		# lencode = xcode[2:len(xcode)] ##lấy số thứ tự của mã số
		# intcode = int(lencode) #Convert 
		# newstt = intcode + 1
	# newstt = str(newstt)
	# lennewstt = lenms - len(newstt)
	# for x in range(0,lennewstt):
		# newstt = '0'+ newstt
	# newcode = 'GV'  + newstt
	
	# var['code'] = newcode
	# #Update	
	# if id:
		# pat = db.teacher(id)
		# x = db(db.teacher.id==id).update(**var)
		# newup = db(db.teacher.id==id).update(code=pat.code)
	# else:
		# ##Insert
		# x = db.teacher.insert(**var)
		# if x:
			# # Thêm tài khoản đăng nhập
			# txtpass = newcode +'@'+ var['phone']
			# txtuser = newcode
			# name = var['fullname']
			# db.auth_user.insert(auth_group=8,teacher=x,last_name=name,username=txtuser, password=db.auth_user.password.requires[0](txtpass)[0])
	# return redirect(URL(r=request,c='plugin_student',f='list_teacher'))
	
# ##Xóa thông tin giáo viên
# @auth.requires_login()	
# def delete_teacher():
	# from datatables import define_teacher
	# define_teacher(db, False)
	# id = request.vars.id if request.vars.id else ''
	# row_t = db(db.teacher.id==id).select().first()
	# if row_t.aactive:
		# dele = db(db.teacher.id==id).update(aactive=False)
		# if dele:
			# db(db.auth_user.teacher==id).update(registration_key='blocked')
	# else:
		# dele = db(db.teacher.id==id).update(aactive=True)
		# if dele:
			# db(db.auth_user.teacher==id).update(registration_key='')
	# # dele = db(db.teacher.id==id).delete()
	# return redirect(URL(r=request,c='plugin_student',f='list_teacher'))
		
	