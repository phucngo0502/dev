###################################################
# This file was developed by IVINH
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 15/05/2015
###################################################
# -*- coding: utf-8 -*-


@service.jsonrpc
@service.jsonrpc2
def add(a, b):
    return a + b
		
@auth.requires_login()
def call():
    return service()
	
def kiemtra():
	import requests
	url_produc = '%s/api/v1/folder/%s.json?field=name'%(api_naso,request.args(0))
	r1 = requests.get(url_produc).json()
	r_produc = r1['result']
	return dict(c=(len(r_produc)>0))

	
def bravo():
	browser=request.env.http_user_agent
	return browser
	if 'Chrome' in browser:
		return "Chrome"
		
	elif 'Opera' in browser:
		return "Opera"
	elif 'Firefox' in browser:
		return "Firefox"
	else:
		return 'Chua xac dinh'

@auth.requires_login()	
def index():	
	if auth.get_group()==18:
		redirect(URL(c='salesman',f='index'))
		
	from plugin_process import Procedures
	auth_group = auth.auth_groups()
	content =Procedures().menu_dashboard(auth_group)
	from plugin_config import Configsite
	
	return dict(content=content)

#@auth.requires_login()	
def menu_top():
	try:
		ul = UL(_class="nav navbar-nav menu_dashboard")
		ul.append(LI(A(I(_class="fa fa-dashboard fa-fw fa-2x"),T("Dashboard"),_href=URL(c='admin',f='index.html'))))
		
		from plugin_process import Procedures
		auth_group = auth.auth_groups()
		menu = Procedures().menu(auth_group)
		if len(menu) > 1:
			a = XML('''<a href="%s" class='dropdown-toggle' data-hover="dropdown" role="button" aria-expanded="false"> <i class="fa fa-codepen fa-fw fa-2x"></i>%s<span class="caret"></span></a>'''%(URL(c="admin",f="index.html"),T("Procedures")))
			ul.append(LI(a,menu,_class="dropdown"))
		elif len(menu) == 1:
			a = menu[0][0]
			a["class"] = ""
			a[0] = I(_class="fa fa-codepen fa-fw fa-2x") 
			ul.append(LI(a))
		menu = UL(_class="dropdown-menu",_role="menu")
		table = cms.define_dtable()
		rows = cms.db(table.publish==False).select(orderby=table.display_order)
		for row in rows:
			if auth.has_membership(role='admin')|auth.has_permission("explorer", row.name):
				title=T(row.label)
				menu.append(LI(A(I(_class="fa fa-table fa-fw"),title,_href=URL(c="plugin_table",f="explorer",args=[row.name]))))
		if len(menu) > 0:
			a = XML('''<a href="%s" class='dropdown-toggle' data-hover="dropdown" role="button" aria-expanded="false"> <i class="fa  fa-database fa-fw fa-2x"></i>%s<span class="caret"></span></a>'''%(URL(c="admin",f="index.html"),T("Datatables")))
			ul.append(LI(a,menu,_class="dropdown"))
		menu = UL(_class="dropdown-menu",_role="menu")
		if auth.has_membership(role='admin'):
			import os
			files = []
			for root, dirs, files in os.walk(request.folder+'/controllers'):
				pass
			for file in files:
				if file.startswith("plugin"):
					c = file.replace(".py","")
					title=T("Plugin %s"%c.split("_")[1].capitalize())
					menu.append(LI(A(I(_class="fa fa-cog fa-fw"),title,_href=URL(c=c,f="index"))))
			a = XML('''<a href="%s" class='dropdown-toggle' data-hover="dropdown" role="button" aria-expanded="false"> <i class="fa  fa-gears fa-fw fa-2x"></i>%s<span class="caret"></span></a>'''%(URL(c="admin",f="index.html"),T("Plugin Manage")))
			ul.append(LI(a,menu,_class="dropdown"))
		else:
			if auth.has_membership(role='phangia'):
				ul.append(LI(A(I(_class='fa-th-list  fa fa-2x'),'Quản lý thông tin',_href=URL(c='plugin_table',f='explorer',args='mau_sac'))))
				
			
			if auth.has_membership(role='manager'):
				ul.append(LI(A(I(_class='fa-desktop fa fa-2x'),'Khối giao diện',_href=URL(c='plugin_portlet',f='index'))))
				ul.append(LI(A(I(_class='fa-th-list fa fa-2x'),'Danh mục',_href=URL(c='plugin_folder',f='index'))))
				ul.append(LI(A(I(_class='fa-user fa fa-2x'),'Người dùng',_href=URL(c='plugin_auth',f='set_password'))))
			# if auth.has_membership(role='Tổng biên tập')| auth.has_membership(role='admin'):
				# ul.append(LI(A(I(_class='glyphicon glyphicon-registration-mark fa-2x'),'Báo cáo',_href=URL(c='report',f='index'))))
					
		if auth.has_membership(role='van_tai'):
			ul.append(LI(A(I(_class='fa-th-list  fa fa-2x'),'Khoảng cách',_href=URL(c='admin',f='vantai'))))
		return ul
	except:
		return ""
		
def icon():
	return dict()
	
def datatable():
	return dict()
	
def tags():
	return dict()	
	
def modals():
	return dict()
	
def test():
	return 'Ghi lại thành công'	
	
def calendar():
	return dict()
	
def get_items():
	print request.vars.value
	content = [{ "value": 1 , "text": "anh" , "continent": "Europe"}]
	return str(content)

def theme():
	div = DIV(_class='admin_theme')
	import os
	from gluon.contrib.appconfig import AppConfig
	rootDir = request.folder+'views\site\%s'%(site_name)
	print rootDir,'----'
	for dirName, subdirList, fileList in os.walk(rootDir):
		if 'theme.ini' in fileList:
			path= dirName + '/theme.ini'
			my_theme = AppConfig(path,reload=True)	
			if my_theme:
				if template == my_theme.take('theme.folder'):
					div_1 = DIV(_class='panel panel-primary')
					div_1.append(DIV(my_theme.take('theme.name') if my_theme.take('theme.name') else '' ,_class='panel-heading'))
					url = str(URL(c='static',f='site/%s/template/%s/%s')%(site_name,str(my_theme.take('theme.folder')),str(my_theme.take('theme.avarta')))).replace(' ','')
					div_1.append(DIV(IMG(_src=url,_class='avarta_theme'),_class='panel-body'))
					div.append(DIV(div_1,_class='col-lg-3'))
				else:
					div_1 = DIV(_class='panel panel-default')
					div_1.append(DIV(my_theme.take('theme.name') if my_theme.take('theme.name') else '',_class='panel-heading'))
					url = str(URL(c='static',f='site/%s/template/%s/%s')%(site_name,str(my_theme.take('theme.folder')),str(my_theme.take('theme.avarta')))).replace(' ','')
					div_1.append(DIV(IMG(_src=url,_class='avarta_theme'),BR(),INPUT(_type='button',_value='Sử dụng giao diện này',_class='btn btn-primary is_defautl_template'),_class='panel-body'))
					
					div.append(DIV(div_1,_class='col-lg-3'))
	return dict(content=div)
	
def clear_cache():
	cache.ram.clear()
	cache.disk.clear()
	return 'Ok'

def get_html():
	url = 'https://track.aftership.com/viettelpost/BRAVO10041606'
	url = 'http://dantri.com.vn/'
	# url = 'http://hatinhtrade.com.vn/sgd/portal/folder/home'
	import urllib2
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	html = response.read()
	return html
	from BeautifulSoup import BeautifulSoup
	soup = BeautifulSoup(html.decode('utf-8'))
	soup.prettify()
	ul =UL()
	for row in soup.findAll("div", {"id":"home_list_products"}):
		ul.append(LI(row))
	response.view = 'plugin_process/content.%s'%request.extension
	return dict(content=ul)
	
def like():
	try:
		photos_like = cms.define_table('photos_like')
		photos = cms.define_table('photos')
		rows = cms.db((photos_like.photo==request.args(0))&(photos_like.created_by==auth.user_id)).select()
		
		if len(rows):
			cms.db((photos_like.photo==request.args(0))&(photos_like.created_by==auth.user_id)).delete()
			like = cms.db(photos_like.photo==request.args(0)).select()
			cms.db(photos.id==request.args(0)).update(like_number=len(like))
			return  SPAN(I(_class='fa fa-thumbs-o-up'),'Thích')
		else:
			cms.db.photos_like.insert(photo=request.args(0),created_by=auth.user_id)
			like = cms.db(photos_like.photo==request.args(0)).select()
			cms.db(photos.id==request.args(0)).update(like_number=len(like))
			return SPAN(I(_class='fa fa-thumbs-up'),SPAN( 'Thích',_class='up_like'))
	except Exception,e:
		return e
		
def update_num_like():
	photos_like = cms.define_table('photos_like')
	rows = cms.db(photos_like.photo==request.args(0)).select()
	return len(rows)
	

def korealink():
	import requests
	import cStringIO
	import urllib, urllib2, os
	from bs4 import BeautifulSoup

	url  = "https://eps.hrdkorea.or.kr/epstopik/pass/candidate/sucessReportDetail.do?lang=en"
	headers_api = {
		'Connection':"keep-alive",
		'Pragma':"no-cache",
		'Cache-Control':"no-cache",
		'Origin':"https://eps.hrdkorea.or.kr",
		'Upgrade-Insecure-Requests':"1",
		'Content-Type':"application/x-www-form-urlencoded",
		'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
		'Sec-Fetch-Mode':"navigate",
		'Sec-Fetch-User':"?1",
		'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
		'Sec-Fetch-Site':"same-origin",
		'Referer':"https://eps.hrdkorea.or.kr/epstopik/pass/candidate/sucessReportList.do?lang=en",
		'Accept-Encoding':"gzip, deflate, br",
		'Accept-Language':"vi,en;q=0.9,vi-VN;q=0.8,en-US;q=0.7",
		'Cookie':"JSESSIONID=X9MaqT4yliI8xoMFSLieLeppBgJE0Bg6UlSaguBvowbUkAT7ycBGKDRFTcroTSxA.topik-cbtmain_servlet_engine1; WLCK-TV=1570525937543; WLCK-US=544331623037574459; WLCK-UV=1570525999892"
	
	}
	body = {
		"searchBirthDay":"19990810",
		"searchCondition":"0",
		"searchKeyword":"187662722",
		"year":"1999",
		"month":"M08",
		"day":"10",
	}
	r = requests.post(url,headers=headers_api, data =body)
	
	content = r.text.encode('utf-8')
	soup = BeautifulSoup(content)
	mydivs = soup.findAll("table", {"class": "tableType"})
	return XML(mydivs[0])
	
def vantai():
	div = DIV(H3("Cấu hình khoảng cách vận chuyển"))
	div.append(P("(*) Không thay đổi địa điểm đi"))
	div.append(B("Điểm đi",_style='float:left;line-height: 35px;margin: 0 10px;'))
	div.append(DIV(LOAD(f='di',vars=dict(di_tinh=29,di_huyen=298,di_xa=5664)),_id='wr_di',_style='float:left;'))
	div.append(B("Điểm đến",_style='float:left;line-height: 35px;margin: 0 10px;'))
	div.append(DIV(LOAD(f='den'),_id='wr_den',_style='float:left;'))
	ajax ="ajax('%s',['di_tinh','di_huyen','di_xa','den_tinh','den_huyen','den_xa'],'wr_act_vantai')"%URL(c='admin',f='act_vantai')
	div.append(A("Khởi tạo form",_class='btn btn-primary',_style='float:left;margin: 0 10px;',_onclick=ajax))
	div.append(DIV(_id='wr_act_vantai',_class='col-lg-12'))
	return dict(content=div)
	
def act_vantai():
	d_tinh = cms.define_table('d_tinh')
	d_huyen = cms.define_table('d_huyen')
	d_xa = cms.define_table('d_xa')
	van_tai = cms.define_table('van_tai')
	
	
	xas = db((db.d_xa.status==True)&(db.d_xa.d_huyen==request.vars.den_huyen)).select()
	table = TABLE(TR(TH("Phường/Xã/Thị trấn",_style='width:200px; text-align:center;     vertical-align: middle;'),TH("Khoảng cách(/km)",_style='width:250px; text-align:center;     vertical-align: middle;'),TH()),_class='table')
	for x in xas:
		km = ''
		vt = db((van_tai.p_tinh==request.vars.di_tinh)&(van_tai.p_huyen==request.vars.di_huyen)&(van_tai.p_xa==request.vars.di_xa)&(van_tai.s_tinh==request.vars.den_tinh)&(van_tai.s_huyen==request.vars.den_huyen)&(van_tai.s_xa==x.id)).select().first()
		if vt:
			if vt.khoang_cach:
				km = vt.khoang_cach
		ajax ="ajax('%s',['di_tinh','di_huyen','di_xa','den_tinh','den_huyen','km_%s'],'wr_add_van_tai_%s')"%(URL(c='admin',f='add_vantai',args=[x.id]),x.id,x.id)
		table.append(TR(TD(x.name,_style='text-align: right;'),TD(DIV(INPUT(_name='km_%s'%x.id,_value=km,_type='text',_class='form-control'),A(I(_class='fa fa-save',_onclick=ajax),_class=' btn btn-primary input-group-addon'),_class="input-group")),TD(DIV(_id='wr_add_van_tai_%s'%x.id))))
	
	
	return table

def add_vantai():
	van_tai = cms.define_table('van_tai')
	ipkm = "km_%s"%request.args(0)
	vkm = request.vars[ipkm]
	vt = db((van_tai.p_tinh==request.vars.di_tinh)&(van_tai.p_huyen==request.vars.di_huyen)&(van_tai.p_xa==request.vars.di_xa)&(van_tai.s_tinh==request.vars.den_tinh)&(van_tai.s_huyen==request.vars.den_huyen)&(van_tai.s_xa==request.args(0))).select().first()
	if vt:
		db((van_tai.p_tinh==request.vars.di_tinh)&(van_tai.p_huyen==request.vars.di_huyen)&(van_tai.p_xa==request.vars.di_xa)&(van_tai.s_tinh==request.vars.den_tinh)&(van_tai.s_huyen==request.vars.den_huyen)&(van_tai.s_xa==request.args(0))).update(khoang_cach=vkm)
	else:
		db.van_tai.insert(p_tinh=request.vars.di_tinh,p_huyen=request.vars.di_huyen,p_xa=request.vars.di_xa,s_tinh=request.vars.den_tinh,s_huyen=request.vars.den_huyen,s_xa=request.args(0),khoang_cach=vkm)
	return 'Lưu thành công, khoảng cách: %s km'%vkm
	
def di():
	v_tinh = request.vars.di_tinh or 0
	v_huyen = request.vars.di_huyen or 0
	v_xa = request.vars.di_xa or 0
	d_tinh = cms.define_table('d_tinh')
	d_huyen = cms.define_table('d_huyen')
	d_xa = cms.define_table('d_xa')
	
	tinhs = db(db.d_tinh.status==True).select()
	options_tinh = []
	for t in tinhs:
		if v_tinh:
			if t.id==int(v_tinh):
				options_tinh.append(OPTION(t.name ,_value=t.id,_selected='selected'))
			else:
				options_tinh.append(OPTION(t.name ,_value=t.id))
		else:
			if t.id==int(29):
				options_tinh.append(OPTION(t.name ,_value=t.id,_selected='selected'))
			else:
				options_tinh.append(OPTION(t.name ,_value=t.id))

	div = DIV()
	ajax ="ajax('%s',['di_tinh','di_huyen','di_xa'],'wr_di')"%URL(c='admin',f='di')
	div.append(SELECT(options_tinh,_name='di_tinh',_id='d_tinh',_class="select2 vantai_select2",_onchange=ajax))
	huyen_first = 0
	try:
		if v_tinh !=0:
			huyens = db((db.d_huyen.status==True)&(db.d_huyen.d_tinh==v_tinh)).select()
			# Lấy danh sách huyện
			options_huyen = []
			if len(huyens)>0: huyen_first= huyens[0].id
			for h in huyens:
				if str(h.id)==v_huyen:
					options_huyen.append(OPTION(h.name ,_value=h.id,_selected='selected'))
				else:
					options_huyen.append(OPTION(h.name ,_value=h.id))
			div.append(SELECT(options_huyen,_name='di_huyen',_id='d_huyen',_class="select2 vantai_select2",_onchange=ajax))
		else:
			huyens = db((db.d_huyen.status==True)&(db.d_huyen.d_tinh==29)).select()
			# Lấy danh sách huyện
			if len(huyens)>0: huyen_first= huyens[0].id
			options_huyen = []
			for h in huyens:
				if str(h.id)==v_huyen:
					options_huyen.append(OPTION(h.name ,_value=h.id,_selected='selected'))
				else:
					options_huyen.append(OPTION(h.name ,_value=h.id))
			div.append(SELECT(options_huyen,_name='di_huyen',_id='d_huyen',_class="select2 vantai_select2",_onchange=ajax))
			# div.append(SELECT([OPTION("Cần chọn huyện",_value=0)],_name='huyen',_id='d_huyen',_class="select2 vantai_select2",_onchange=ajax))
	except Exception,e: return e
	
	
	try:
		if v_huyen !=0:
			xas = db((db.d_xa.status==True)&(db.d_xa.d_huyen==v_huyen)).select()
			
			options_xa = []
			for x in xas:
				if str(x.id)==str(v_xa):
					options_xa.append(OPTION(x.name ,_value=x.id,_selected='selected'))
				else:
					options_xa.append(OPTION(x.name ,_value=x.id))
			div.append(SELECT(options_xa,_name='di_xa',_id='d_xa',_class="select2 vantai_select2",_onchange=ajax))
		else:
			if huyen_first!=0:
				xas = db((db.d_xa.status==True)&(db.d_xa.d_huyen==huyen_first)).select()
				options_xa = []
				for x in xas:
					if str(x.id)==v_xa:
						options_xa.append(OPTION(x.name ,_value=x.id,_selected='selected'))
					else:
						options_xa.append(OPTION(x.name ,_value=x.id))
				div.append(SELECT(options_xa,_name='di_xa',_id='d_xa',_class="select2 vantai_select2",_onchange=ajax))
			else:
				div.append(SELECT([OPTION("Cần chọn xã",_value=0)],_name='di_xa',_id='d_xa',_class="select2 vantai_select2",_onchange=ajax))
	except Exception,e: div.append(DIV(e))
	div.append(XML("""
		<script type="text/javascript">
		$(document).ready(function(){
			$(".vantai_select2").select2({
				placeholder: "Chọn dữ liệu ...",
				allowClear: true
			});
			 
		});
		</script>
	"""))

	return div
	
def den():
	v_tinh = request.vars.den_tinh or 0
	v_huyen = request.vars.den_huyen or 0
	 
	d_tinh = cms.define_table('d_tinh')
	d_huyen = cms.define_table('d_huyen')
	
	tinhs = db(db.d_tinh.status==True).select()
	options_tinh = []
	for t in tinhs:
		if v_tinh:
			if t.id==int(v_tinh):
				options_tinh.append(OPTION(t.name ,_value=t.id,_selected='selected'))
			else:
				options_tinh.append(OPTION(t.name ,_value=t.id))
		else:
			if t.id==int(29):
				options_tinh.append(OPTION(t.name ,_value=t.id,_selected='selected'))
			else:
				options_tinh.append(OPTION(t.name ,_value=t.id))

	div = DIV()
	ajax ="ajax('%s',['den_tinh','den_huyen','den_xa'],'wr_den')"%URL(c='admin',f='den')
	div.append(SELECT(options_tinh,_name='den_tinh',_id='d_tinh',_class="select2 vantai_select2",_onchange=ajax))
	huyen_first = 0
	try:
		if v_tinh !=0:
			huyens = db((db.d_huyen.status==True)&(db.d_huyen.d_tinh==v_tinh)).select()
			# Lấy danh sách huyện
			options_huyen = []
			if len(huyens)>0: huyen_first= huyens[0].id
			for h in huyens:
				if str(h.id)==v_huyen:
					options_huyen.append(OPTION(h.name ,_value=h.id,_selected='selected'))
				else:
					options_huyen.append(OPTION(h.name ,_value=h.id))
			div.append(SELECT(options_huyen,_name='den_huyen',_id='d_huyen',_class="select2 vantai_select2",_onchange=ajax))
		else:
			huyens = db((db.d_huyen.status==True)&(db.d_huyen.d_tinh==29)).select()
			# Lấy danh sách huyện
			if len(huyens)>0: huyen_first= huyens[0].id
			options_huyen = []
			for h in huyens:
				if str(h.id)==v_huyen:
					options_huyen.append(OPTION(h.name ,_value=h.id,_selected='selected'))
				else:
					options_huyen.append(OPTION(h.name ,_value=h.id))
			div.append(SELECT(options_huyen,_name='den_huyen',_id='d_huyen',_class="select2 vantai_select2",_onchange=ajax))
			# div.append(SELECT([OPTION("Cần chọn huyện",_value=0)],_name='huyen',_id='d_huyen',_class="select2 vantai_select2",_onchange=ajax))
	except Exception,e: return e
	
	
	# try:
		# if v_huyen !=0:
			# xas = db((db.d_xa.status==True)&(db.d_xa.d_huyen==v_huyen)).select()
			
			# options_xa = []
			# for x in xas:
				# if str(x.id)==v_xa:
					# options_xa.append(OPTION(x.name ,_value=x.id,_selected='selected'))
				# else:
					# options_xa.append(OPTION(x.name ,_value=x.id))
			# div.append(SELECT(options_xa,_name='den_xa',_id='d_xa',_class="select2 vantai_select2",_onchange=ajax))
		# else:
			# if huyen_first!=0:
				# xas = db((db.d_xa.status==True)&(db.d_xa.d_huyen==huyen_first)).select()
				# options_xa = []
				# for x in xas:
					# if str(x.id)==v_xa:
						# options_xa.append(OPTION(x.name ,_value=x.id,_selected='selected'))
					# else:
						# options_xa.append(OPTION(x.name ,_value=x.id))
				# div.append(SELECT(options_xa,_name='den_xa',_id='d_xa',_class="select2 vantai_select2",_onchange=ajax))
			# else:
				# div.append(SELECT([OPTION("Cần chọn xã",_value=0)],_name='den_xa',_id='d_xa',_class="select2 vantai_select2",_onchange=ajax))
	# except Exception,e: div.append(DIV(e))
	div.append(XML("""
		<script type="text/javascript">
		$(document).ready(function(){
			$(".vantai_select2").select2({
				placeholder: "Chọn dữ liệu ...",
				allowClear: true
			});
			 
		});
		</script>
	"""))

	return div
	
def re_naso():
	news = cms.define_table('news')
	rows = db(news.id>0).select()
	i = 0
	for row in rows:
		name = str(row.name).replace('NASO','BAHADI').replace('naso','bahadi').replace('Naso','Bahadi')
		description = str(row.description).replace('NASO','BAHADI').replace('naso','bahadi').replace('Naso','Bahadi')
		htmlcontent = str(row.htmlcontent).replace('NASO','BAHADI').replace('naso','bahadi').replace('Naso','Bahadi')
		db(news.id==row.id).update(name=name,description=description,htmlcontent=htmlcontent)
		
		i+=1
	return i
	