# -*- coding: utf-8 -*-

from plugin_cms import Cms
cms = Cms()

@auth.requires_login()
def index():
	content = H2("Naso")
	return dict(content=content)
	
@auth.requires_login()
def info():
	content = H2("Thông tin đại lý")
	response.view = 'salesman/index.html'	
	return dict(content=content)

@auth.requires_login()
def groups():
	content = H2("Đội nhóm")
	response.view = 'salesman/index.html'	
	return dict(content=content)
	
@auth.requires_login()
def products():
	content = H2("Sản phẩm")
	response.view = 'salesman/index.html'	
	return dict(content=content)

@auth.requires_login()
def orders():
	content = H2("Đơn hàng")
	response.view = 'salesman/index.html'	
	return dict(content=content)

@auth.requires_login()
def customer():
	content = H2("Khách hàng")
	response.view = 'salesman/index.html'	
	return dict(content=content)

@auth.requires_login()
def income():
	content = H2("Thu nhập")
	response.view = 'salesman/index.html'	
	return dict(content=content)
