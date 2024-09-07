# -*- coding: utf-8 -*-
###################################################
# This content was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 26/05/2015
# Version 1.0 Date: 01/10/2015
###################################################

from gluon import current,os
from gluon.dal import Field
from gluon.sqlhtml import SQLFORM
from validators import IS_EMPTY_OR, IS_NOT_EMPTY, IS_IMAGE, IS_NULL_OR, IS_IN_DB, IS_IN_SET, IS_NOT_IN_DB, IS_SLUG, IS_DATE
		
def define(db,tablename,migrate=False):
	dbsource = db	
	migrate = migrate
	return eval('define_%s(dbsource,%s)'%(tablename,migrate))

########################################################
#Bảng tin tức
def define_news(db,migrate=False):
	tablename = 'news'
	from plugin_config import Configsite
	if tablename in db.tables: return db[tablename]
	define_news_category(db,migrate)
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('category','reference news_category'),
		Field('name'),
		Field('description','text'),
		Field('htmlcontent','text',length=650000),
		Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/news'%(Configsite().site_name))),
		Field('publish_on','datetime'),  
		Field('expired_on','datetime'),  
		Field('created_on','datetime'),  
		Field('created_by',"integer"),
		Field('display_order','integer',default=100),
		migrate=migrate,redefine=migrate)
	return db[tablename]
	
########################################################
#Bảng loại tin tức
def define_news_category(db,migrate=False):
	tablename = 'news_category'
	if tablename in db.tables: return db[tablename]
	db.define_table(tablename,
		Field('name',required=True,unique=True,length=255),
		Field('display_order',"integer",default=100),
		migrate=migrate,redefine=migrate)
	return db[tablename]
	
########################################################
#Bảng văn bản
def define_archives(db,migrate=False):
	tablename = 'archives'
	if tablename in db.tables: return db[tablename]
	define_news_category(db,migrate)
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name'),
		Field('description','text'),
		Field('daystart',"date"),
		Field('dayend',"date"),
		Field('user_signed'),
		Field('user_office'),
		Field('org_publish'),
		Field('publish_on','datetime'),  
		Field('expired_on','datetime'),  
		Field('created_on','datetime'),  
		Field('created_by',"integer"),
		Field('display_order','integer',default=100),
		migrate=migrate,redefine=migrate)
	return db[tablename]
	
########################################################
#Bảng Lịch công tác
def define_lichcongtac(db,migrate=False):
	tablename = 'lichcongtac'
	if tablename in db.tables: return db[tablename]
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name','text'),
		Field('start_date','date'),
		Field('start_time','time'),
		Field('person','string'),
		Field('work_place','string'),
		Field('expediency','string'),
		Field('display_order','integer',default=100),
		Field('created_by','integer'),
		Field('created_on','datetime'),
		migrate=migrate)
	db[tablename].start_date.represent = lambda v, row: v.strftime("%d/%m/%Y") if v else ''
	return db[tablename]	
	
########################################################
#Bảng Thông báo
def define_thongbao(db,migrate=False):
	tablename = 'thongbao'
	if tablename in db.tables: return db[tablename]
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name','text'),
		Field('daystart','date'),
		Field('dayend','date'),
		Field('display_order','integer',default=100),
		Field('created_by','integer'),
		Field('created_on','datetime'),
		migrate=migrate)
	db[tablename].daystart.represent = lambda v, row: v.strftime("%d/%m/%Y ") if v else ''
	db[tablename].dayend.represent = lambda v, row: v.strftime("%d/%m/%Y") if v else ''
	return db[tablename]	
	
def define_h_comment(db,migrate=False):
	tablename = 'h_comment'
	if tablename in db.tables: return db[tablename]
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name','string'),
		Field('description','text'),
		Field('email','string'),
		Field('tablename','string'),
		Field('tableid','string'),
		Field('display_order','integer',default=100),
		Field('created_by','integer'),
		Field('created_on','datetime'),
		migrate=migrate)
	return db[tablename]	

def define_hoi_dap(db,migrate=False):
	tablename = 'hoi_dap'
	if tablename in db.tables: return db[tablename]
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name','string'),
		Field('description','text'),
		Field('tra_loi','text'),
		Field('nguoi_hoi','string'),
		Field('dien_thoai','string'),
		Field('email','string'),
		Field('display_order','integer',default=100),
		Field('created_by','integer'),
		Field('created_on','datetime'),
		migrate=migrate)
	return db[tablename]	
	
def define_galerry(db,migrate=False):
	tablename = 'galerry'
	from plugin_config import Configsite
	if tablename in db.tables: return db[tablename]
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name','string'),
		Field('description','text'),
		Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/galerry'%(Configsite().site_name))),
		Field('display_order','integer',default=100),
		Field('created_by','integer'),
		Field('created_on','datetime'),
		migrate=migrate)
	return db[tablename]	
	
########################################################
#Bảng sản phẩm
def define_product(db,migrate=False):
	tablename = 'product'
	from plugin_config import Configsite
	if tablename in db.tables: return db[tablename]
	define_product_category(db,migrate)
	define_supplier(db,migrate)
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('category','reference product_category'),
		Field('supplier','reference supplier'),
		Field('name'),
		Field('code_name'),
		Field('description','text'),
		Field('htmlcontent','text',length=125000),
		Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/product'%(Configsite().site_name))),
		Field('price','integer'),
		Field('price_old','integer'),
		Field('units'),
		Field('publish_on','datetime'),  
		Field('expired_on','datetime'),  
		Field('created_on','datetime'),  
		Field('created_by',"integer"),
		Field('display_order','integer',default=100),
		migrate=migrate,redefine=migrate)
	return db[tablename]
	
########################################################
#Bảng loại sản phẩm
def define_product_category(db,migrate=False):
	tablename = 'product_category'
	if tablename in db.tables: return db[tablename]
	db.define_table(tablename,
		Field('name',required=True,unique=True,length=255),
		Field('display_order',"integer",default=100),
		migrate=migrate,redefine=migrate)
	return db[tablename]
	
########################################################
#Bảng đơn hàng
def define_don_hang(db,migrate=False):
	tablename = 'don_hang'
	if tablename in db.tables: return db[tablename]
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name'),
		Field('dien_thoai'),
		Field('name2'),
		Field('dien_thoai2'),
		Field('dia_chi'),
		Field('description','text'),
		Field('created_on','datetime'),  
		Field('created_by',"integer"),
		Field('display_order','integer',default=100),
		migrate=migrate,redefine=migrate)
	return db[tablename]
	
########################################################
#Bảng chi tiết đơn hàng
def define_item_don_hang(db,migrate=False):
	tablename = 'item_don_hang'
	if tablename in db.tables: return db[tablename]
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	define_don_hang(db,migrate)
	define_product(db,migrate)
	db.define_table(tablename,
		Field('don_hang','reference don_hang'),
		Field('product','reference product'),
		Field('r_number','integer'),
		Field('price','integer'),
		Field('created_on','datetime'),  
		Field('created_by',"integer"),
		Field('display_order','integer',default=100),
		migrate=migrate,redefine=migrate)
	return db[tablename]
	

########################################################
#NASO: Bảng NCC
def define_supplier(db,migrate=False):
	tablename = 'supplier'
	from plugin_config import Configsite
	if tablename in db.tables: return db[tablename]
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name'),
		Field('dien_thoai'),
		Field('dia_chi'),
		Field('description','text'),
		Field('htmlcontent','text',length=650000),
		Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/supplier'%(Configsite().site_name))),
		Field('avatar_bg','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/supplier_bg'%(Configsite().site_name))),
		Field('r_number_products','integer'), # số lượng sp
		Field('start_date','date'),  # ngày tham gia
		Field('created_on','datetime'),  
		Field('created_by',"integer"),
		Field('display_order','integer',default=100),
		migrate=migrate,redefine=migrate)
	db[tablename].start_date.represent = lambda v, row: v.strftime("%d/%m/%Y") if v else ''
	return db[tablename]
	
########################################################
#NASO: Bảng Đại lý, người bán hàng
def define_salesman(db,migrate=False):
	tablename = 'salesman'
	from plugin_config import Configsite
	if tablename in db.tables: return db[tablename]
	define_d_tinh(db,migrate)
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('s_manager','reference salesman'), # người giới thiệu
		Field('name'),
		Field('name_code'), # mã đại lý
		Field('birthday','date'),  # ngày sinh 
		Field('sex',requires=IS_IN_SET(['Nam','Nữ'])),#Giới tính
		Field('id_card'),# Căn cước
		Field('id_day','date'),  # ngày cấp
		Field('id_by'),  # Nơi cấp
		Field('phone'),
		Field('email'),
		Field('d_tinh','reference d_tinh'), # địa bàn
		Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/salesman'%(Configsite().site_name))),
		Field('auth_user_pass',writable=False,readable=False), # Lưu mật khẩu tạm
		Field('auth_user_id','integer',writable=False,readable=False), # ID tài khoản đăng nhập
		Field('r_number_products','integer',writable=False,readable=False), # số lượng hàng đã bán
		Field('start_date','date',writable=False,readable=False),  # ngày tham gia
		Field('created_on','datetime',writable=False,readable=False),  
		Field('created_by',"integer",writable=False,readable=False),
		Field('display_order','integer',default=100,writable=False,readable=False),
		migrate=migrate,redefine=migrate)
	db[tablename].birthday.represent = lambda v, row: v.strftime("%d/%m/%Y") if v else ''
	db[tablename].start_date.represent = lambda v, row: v.strftime("%d/%m/%Y") if v else ''
	return db[tablename]
	

########################################################
#NASO: Bảng Hình ảnh quảng cáo
def define_img_ads(db,migrate=False):
	tablename = 'img_ads'
	from plugin_config import Configsite
	if tablename in db.tables: return db[tablename]
	define_news_category(db,migrate)
	from plugin_cms import CmsModel
	CmsModel().define_folder()
	db.define_table(tablename,
		Field('folder','reference folder'),
		Field('name'),
		Field('url_link','string'),
		Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/img_ads'%(Configsite().site_name))),
		Field('publish_on','datetime'),  
		Field('expired_on','datetime'),  
		Field('created_on','datetime'),  
		Field('created_by',"integer"),
		Field('display_order','integer',default=100),
		migrate=migrate,redefine=migrate)
	return db[tablename]
	
	
# Tỉnh/TP
def define_d_tinh(db,auth,migrate=False):
	tablename = 'd_tinh'
	if tablename in db.tables: return db[tablename]
	
	db.define_table(tablename,
		Field('code'),
		Field('name'),
		Field('status','boolean',default=True),
		migrate=migrate)
	return db[tablename]		
# Huyện/Quận
def define_d_huyen(db,auth,migrate=False):
	tablename = 'd_huyen'
	if tablename in db.tables: return db[tablename]
	define_d_tinh(db,auth,migrate=migrate)
	db.define_table(tablename,
		Field('code'),
		Field('name'),
		Field('d_tinh','reference d_tinh'),
		Field('status','boolean',default=True),
		migrate=migrate)
	return db[tablename]	
	
# Thị trấn/ Phường/xã
def define_d_xa(db,auth,migrate=False):
	tablename = 'd_xa'
	if tablename in db.tables: return db[tablename]
	define_d_huyen(db,auth,migrate=migrate)
	db.define_table(tablename,
		Field('code'),
		Field('name'),
		Field('d_huyen','reference d_huyen'),
		Field('c_type'),
		Field('status','boolean',default=True),
		migrate=migrate)
	return db[tablename]	
	