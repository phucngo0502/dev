# -*- coding: utf-8 -*-

from plugin_cms import Cms
cms = Cms()
@auth.requires_login()
def call():
    return service()
	
	
def demo():
	return 'ok'

#@cache(request.env.path_info, time_expire=3600, cache_model=cache.ram)
def calendar():
	try:
		response.view = 'layout/lich2/%s'%(cms.layout_folder() or 'index.html')
	except:
		response.view = 'layout/trangchu.html'
	return response.render(dict())
	
def index():
	redirect(URL(f='folder',args=request.args))


#@cache(request.env.path_info, time_expire=600, cache_model=cache.ram)
def folder():
	if request.args == []:
		redirect(URL(f='folder',args=[page_home]))
	try:
		response.view = 'site/%s/%s/%s'%(site_name,template,cms.layout_folder() or '404.html')
	except:
		response.view = 'layout/404.html'
	return response.render(dict())
	

#@cache(request.env.path_info, time_expire=600, cache_model=cache.ram)
def xemtruoc():
	if request.args == []:
		redirect(URL(f='folder',args=[page_home]))
	try:
		response.view = 'site/%s/%s/%s'%(site_name,template,cms.layout_folder() or '404.html')
	except:
		response.view = 'layout/404.html'
	return response.render(dict())
	 
	

	
# @cache(request.env.path_info, time_expire=3600, cache_model=cache.ram)
def read():
	try:
		# template = setting_config('template','')
		if template !='':
			response.view = 'site/%s/%s/%s'%(site_name,template,cms.layout() or '404.html')
		else:
			response.view = 'site/%s'%(cms.layout() or '404.html')
		cms.insert_read()
	except:
		response.view = 'layout/404.html'
	return response.render(dict())
	
def load_portlet():
	portlet_id = request.args(0)
	if portlet_id:
		return portlet.display(portlet_id)
	else: return ''
	

def feed():
	from plugin_cms import CmsFolder,CmsModel
	folder_id = CmsFolder().get_folder()
	ar_entries =[]
	entries =  CmsFolder().get_rows(folder=request.args(0))
	link_page='http://'+request.env.http_host
	for entry in entries:
		link = CmsFolder().url_content(entry)
		description = str(entry.description)
		if entry.avatar:
			avarta = CmsModel().get_images_content(entry.dtable,entry.avatar)
			description = '<a href="'+link_page + str(link)+'">'+str(avarta) +'</a>'+ description
		ar_entries.append(dict(title = entry.name.decode('utf-8'),
			link = link_page + str(link),
			description=XML(description.decode('utf-8')),
			created_on = entry.publish_on))
	return dict(title='Feed',link=link_page,description='Feed', created_on = request.now,entries=ar_entries )
	
#Product


def add_cart_r_number():
	pid = request.vars.pid
	ar_carts =[]
	num_carts = 0
	if request.cookies.has_key ('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		i=0
		
		for cart in carts:
			num_carts +=1
			cart = eval(cart)
			if cart['id']==pid:
				ar_carts.append(str({'id':str(cart['id']) ,'num':str(int(cart['num'])+1)}))
				i+=1
			else:
				ar_carts.append(str({'id':str(cart['id']) ,'num':str(cart['num'])}))
		if i==0:
			num_carts +=1
			ar_carts.append(str({'id':pid ,'num':str(1)}))
	else:
		ar_carts.append(str({'id':pid ,'num':str(1)}))
		num_carts +=1
		
	response.cookies['cart_shop'] = str(ar_carts) 
	response.cookies['cart_shop']['expires'] = 24 * 3600
	response.cookies['cart_shop']['path'] = '/'
	response.flash = T("Add new cart!")
	
	# load view_carts() nhung ko request duoc cookies moi
	redirect(URL(c='portal',f='folder',args=['thanh-toan']))
	if num_carts !=0:
		return num_carts
	else: return ''
	
def update_cookies():
	try:
		pid = request.vars.pid
		number_so_luong = request.vars['number_so_luong_%s'%(pid)]
		ar_carts =[]
		if request.args(0)=='delete':
			carts = eval(request.cookies['cart_shop'].value)
			for cart in carts:
				cart = eval(cart)
				if cart['id']==pid:
					ar_carts.append(str({'id':str(cart['id']) ,'num':0}))
				else:
					ar_carts.append(str({'id':str(cart['id']) ,'num':str(cart['num'])}))
		elif request.args(0)=='update':	
			if request.cookies.has_key ('cart_shop'):
				carts = eval(request.cookies['cart_shop'].value)
				
				for cart in carts:
					cart = eval(cart)
					if cart['id']==pid:
						ar_carts.append(str({'id':str(cart['id']) ,'num':number_so_luong}))
					else:
						ar_carts.append(str({'id':str(cart['id']) ,'num':str(cart['num'])}))
		response.cookies['cart_shop'] = str(ar_carts) 
		response.cookies['cart_shop']['expires'] = 24 * 3600
		response.cookies['cart_shop']['path'] = '/'
		response.flash = T("Cập nhật thành công!")
		
		div = DIV()
		num_car = 0
		tong_tien = 0
		carts =''
		from plugin_app import number_format
		table = TABLE(_class='table')
		
		carts = ar_carts
		from plugin_cms import CmsModel
		from plugin_cms import CmsFolder
		db = cms.db
		cms.define_table('product')
		
		table.append(TR(TH('Sản phẩm'),TH('Số lượng'),TH(''),TH('Giá'),TH(B('Thành tiền')),TH(B('Chức năng'))))
		for cart in carts:
			cart = eval(cart)
			if int(cart['num'])>0:
				row  = db((db.product.id==cart['id'])).select().first()
				i=1
				if row:
				
					if row.price:
						tong_tien += int(row.price)* int(cart['num'])
					ajax_update = "ajax('%s', ['number_so_luong_%s'],'order_view')" %(URL(f='update_cookies',args=['update'],vars=dict(pid=row.id)),row.id)
					ajax_delete = "ajax('%s', ['number_so_luong_%s'],'order_view')" %(URL(f='update_cookies',args=['delete'],vars=dict(pid=row.id)),row.id)
					input_num = DIV(INPUT(_type='text',_class='number_so_luong',_name='number_so_luong_%s'%(row.id),_value=cart['num']),A(SPAN(_class='glyphicon glyphicon-floppy-disk'),_title='Lưu thay đổi số lượng',_onclick=ajax_update,_style="padding: 0 10px;"))
					if row.price:
						table.append(TR(TD(row.name,': '),TD(input_num),TD(' * '),TD(number_format(row.price),' VNĐ'),TD(B(number_format(int(row.price)* int(cart['num'])),' VNĐ'),TD(A(SPAN(_class='glyphicon glyphicon-trash'),_onclick=ajax_delete) ))))
					else:
						table.append(TR(TD(row.name,': '),TD(input_num),TD(' * '),TD(),TD('',TD(A(SPAN(_class='glyphicon glyphicon-trash'),_onclick=ajax_delete) ))))
				
		div.append(table)
		# if tong_tien<300000:
			# p_tong = DIV(SPAN('Phí vận chuyển: '))
			# p_tong.append(str('30,000')+' VNĐ')
			# div.append(B(p_tong,_class='text-right'))
			# tong_tien += 30000
		p_tong = DIV(SPAN('Tổng tiền: '))
		p_tong.append(str(number_format(tong_tien))+' VNĐ')
		div.append(B(p_tong,_class='text-right'))
		
		div.append(DIV(DIV(A(I(_class='icon-backward'),' Tiếp tục mua hàng',_href=URL(c='portal',f='folder',args=[page_home]),_class='btn'),_class='pull-left'),DIV(A('Thanh toán ',I(_class='icon-forward'),_href=URL(c='portal',f='folder',args=['thanh-toan']),_class='btn'),_class='pull-right'),_class='select_order'))
		
		return div
	except Exception,e: 
		return e
	
def add_cart():
	pid = request.vars.pid
	ar_carts =[]
	if request.cookies.has_key ('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		i=0
		for cart in carts:
			cart = eval(cart)
			if cart['id']==pid:
				ar_carts.append(str({'id':str(cart['id']) ,'num':str(int(cart['num'])+1)}))
				i+=1
			else:
				ar_carts.append(str({'id':str(cart['id']) ,'num':str(cart['num'])}))
		if i==0:
			ar_carts.append(str({'id':pid ,'num':str(1)}))
	else:
		ar_carts.append(str({'id':pid ,'num':str(1)}))
		
	response.cookies['cart_shop'] = str(ar_carts) 
	response.cookies['cart_shop']['expires'] = 24 * 3600
	response.cookies['cart_shop']['path'] = '/'
	response.flash = T("Add new cart!")
	
	# load view_carts() nhung ko request duoc cookies moi
	
	div = DIV()
	num_car = 0
	tong_tien = 0
	carts = ar_carts
	from plugin_cms import CmsModel
	from plugin_cms import CmsFolder
	cms = CmsModel()
	db = cms.db
	cms.define_table('san_pham')
	from plugin_app import number_format
	
	for cart in carts:
		cart = eval(cart)
		row  = db((db.san_pham.id==cart['id'])).select().first()
		if row:
			div1 = DIV(_class='list_cart')
			ul = UL()
			ul.append(LI(row.name))
			ul.append(LI(SPAN('Số lượng: '),cart['num']))
			ul.append(LI(SPAN('Giá: '),number_format(row.gia_san_pham),' VNĐ'))
			div1.append(DIV(IMG(_src=cms.get_avatar('san_pham',row.avatar),_class='thumbnail'),_class='col-md-4 box_ivinh'))
			div1.append(DIV(ul,_class='col-md-8 box_ivinh'))
			div.append(div1)
			div.append(HR())
			tong_tien += int(row.gia_san_pham)* int(cart['num'])
			num_car +=1
	p_tong = DIV(SPAN('Tổng tiền: '))
	p_tong.append(str(number_format(tong_tien))+' VNĐ')
	div.append(B(p_tong,_class='text-right'))
	div.append(A('Gửi đơn hàng',_href=URL(c='portal',f='folder',args=['checkout']),_class='btn btn-success'))
	return div
	
	
def view_carts():
	div = DIV()
	num_car = 0
	tong_tien = 0
	carts =''
	try:
		if request.cookies.has_key('cart_shop'):
			carts = eval(request.cookies['cart_shop'].value)
			from plugin_cms import CmsModel
			from plugin_cms import CmsFolder
			db = cms.db
			cms.define_table('product')
			from plugin_app import number_format
			
			for cart in carts:
				cart = eval(cart)
				row  = db((db.product.id==cart['id'])).select().first()
				if row:
					div1 = DIV(_class='list_cart')
					ul = UL()
					ul.append(LI(row.name))
					ul.append(LI(SPAN('Số lượng: '),cart['num']))
					ul.append(LI(SPAN('Giá: '),number_format(row.gia_ban),' VNĐ'))
					div1.append(DIV(cms.get_images_content('product',row.avatar),_class='col-md-4 box_ivinh'))
					div1.append(DIV(ul,_class='col-md-8 box_ivinh'))
					
					div.append(div1)
					div.append(HR())
					tong_tien += int(row.gia_ban)* int(cart['num'])
					num_car +=1
		if num_car>0:			
			p_tong = DIV(SPAN('Tổng tiền: '))
			p_tong.append(str(number_format(tong_tien))+' VNĐ')
			div.append(B(p_tong,_class='text-right'))
			div.append(A('Gửi đơn hàng',_href=URL(c='portal',f='folder',args=['checkout']),_class='btn btn-success'))
		else:
			div.append('Giỏ hàng trống')
	except Exception,e: 
		return e
	return div
	
def view_order():
	div = DIV(_id="order_view")
	num_car = 0
	tong_tien = 0
	carts =''
	from plugin_app import number_format
	table = TABLE(_class='table')
	if request.cookies.has_key('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		from plugin_cms import CmsModel
		from plugin_cms import CmsFolder
		db = cms.db
		cms.define_table('product')
		table.append(TR(TH('Sản phẩm'),TH('Số lượng'),TH(''),TH('Giá'),TH(B('Thành tiền')),TH(B('Hủy bỏ'))))
        for cart in carts:
			cart = eval(cart)
			if int(cart['num'])>0:
				row  = db((db.product.id==cart['id'])).select().first()
				i=1
				if row:
					rowname = DIV(cms.get_images_content('product', row.avatar),A(row.name,_href=cms.url_content(row,table='product') ),_class='produc_order')
					if row.price:
						tong_tien += int(row.price)* int(cart['num'])
					ajax_update = "ajax('%s', ['number_so_luong_%s'],'order_view')" %(URL(f='update_cookies',args=['update'],vars=dict(pid=row.id)),row.id)
					ajax_delete = "ajax('%s', ['number_so_luong_%s'],'order_view')" %(URL(f='update_cookies',args=['delete'],vars=dict(pid=row.id)),row.id)
					input_num = DIV(INPUT(_type='text',_class='number_so_luong',_name='number_so_luong_%s'%(row.id),_value=cart['num']),A(SPAN(_class='glyphicon glyphicon-floppy-disk'),_title='Lưu thay đổi số lượng',_onclick=ajax_update,_style="padding: 0 10px;"))
					if row.price:
						table.append(TR(TD(rowname),TD(input_num),TD(' * '),TD(number_format(row.price),' VNĐ'),TD(B(number_format(int(row.price)* int(cart['num'])),' VNĐ'),TD(A(SPAN(_class='glyphicon glyphicon-trash'),_onclick=ajax_delete) ))))
					else:
						table.append(TR(TD(rowname),TD(input_num),TD(' * '),TD(),TD('',TD(A(SPAN(_class='glyphicon glyphicon-trash'),_onclick=ajax_delete) ))))
	div.append(table)
	# if tong_tien<300000:
		# p_tong = DIV(SPAN('Phí vận chuyển: '))
		# p_tong.append(str('30,000')+' VNĐ')
		# div.append(B(p_tong,_class='text-right'))
		# tong_tien += 30000
	p_tong = DIV(SPAN('Tổng tiền: '))
	p_tong.append(str(number_format(tong_tien))+' VNĐ')
	div.append(B(p_tong,_class='text-right'))
	
	div.append(DIV(DIV(A(I(_class='icon-backward'),' Tiếp tục mua hàng',_href=URL(c='portal',f='folder',args=[page_home]),_class='btn'),_class='pull-left'),DIV(A('Thanh toán ',I(_class='icon-forward'),_href=URL(c='portal',f='folder',args=['thanh-toan']),_class='btn'),_class='pull-right'),_class='select_order'))
	return div 

def view_wishlist():
	div = DIV(_id="order_view")
	num_car = 0
	tong_tien = 0
	carts =''
	from plugin_app import number_format
	table = TABLE(_class='table')
	if request.cookies.has_key('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		from plugin_cms import CmsModel
		from plugin_cms import CmsFolder
		db = cms.db
		cms.define_table('product')
		table.append(TR(TH('Hình ảnh'),TH('Tên sản phẩm'),TH('Giá bán'),TH('Đặt hàng')))
        for cart in carts:
			cart = eval(cart)
			if int(cart['num'])>0:
				row  = db((db.product.id==cart['id'])).select().first()
				i=1
				if row:
					rowname = DIV(cms.get_images_content('product', row.avatar),A(row.name,_href=cms.url_content(row,table='product') ),_class='produc_order')
					if row.price:
						table.append(TR(TD(rowname),TD(number_format(row.price),' VNĐ')))
					else:
						table.append(TR(TD(rowname), ))
	div.append(table)
	# if tong_tien<300000:
		# p_tong = DIV(SPAN('Phí vận chuyển: '))
		# p_tong.append(str('30,000')+' VNĐ')
		# div.append(B(p_tong,_class='text-right'))
		# tong_tien += 30000

	
	div.append(DIV(DIV(A(I(_class='icon-backward'),' Tiếp tục mua hàng',_href=URL(c='portal',f='folder',args=[page_home]),_class='btn'),_class='pull-left'),DIV(A('Xem giỏ hàng ',I(_class='icon-forward'),_href=URL(c='portal',f='folder',args=['checkout']),_class='btn'),_class='pull-right'),_class='select_order'))
	return div
	
def view_thanh_toan():
	div = DIV(_id="order_view")
	num_car = 0
	tong_tien = 0
	carts =''
	from plugin_app import number_format
	table = TABLE(_class='table')
	if request.cookies.has_key('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		from plugin_cms import CmsModel
		from plugin_cms import CmsFolder
		db = cms.db
		cms.define_table('product')
		table.append(TR(TH('Sản phẩm',_class='cart_name'),TH('Số lượng',_class='cart_number'),TH('',_class='cart_*'),TH('Giá',_class='cart_price'),TH(B('Thành tiền'),_class='cart_price_all')))
        for cart in carts:
			cart = eval(cart)
			if int(cart['num'])>0:
				row  = db((db.product.id==cart['id'])).select().first()
				i=1
				if row:
					if row.price:
						tong_tien += int(row.price)* int(cart['num'])
					input_num = cart['num']
					rowname = DIV(cms.get_images_content('product', row.avatar),A(row.name,_href=cms.url_content(row,table='product') ),_class='produc_order')
					if row.price:
						table.append(TR(TD(rowname ),TD(input_num),TD(' * '),TD(number_format(row.price),' VNĐ'),TD(B(number_format(int(row.price)* int(cart['num'])),' VNĐ'))))
					else:
						table.append(TR(TD(rowname ),TD(input_num),TD(' * '),TD(),TD('')))
	div.append(table)
	p_tong = DIV(SPAN('Tổng tiền: '))
	p_tong.append(str(number_format(tong_tien))+' VNĐ')
	div.append(B(p_tong,_class='text-right'))
	
	return div 
	
def form_thanh_toan():
	form = FORM()
	form.append(H4('Thông tin người đặt hàng' ,_class='title_form'))
	div1 = DIV(_class="form-group col-md-6")
	div1.append(INPUT(_type='text',_class="form-control",_name='name',_placeholder="Người đặt hàng",_required=True))
	
	div2 = DIV(_class="form-group col-md-6")
	div2.append(INPUT(_type='text',_class="form-control",_name='dien_thoai',_placeholder="Số điện thoại"))
	form.append(DIV(div1,div2,_class='row'))
	
	form.append(DIV(DIV(DIV(INPUT(_type='checkbox',_onclick=" check_show()"),_class='col-md-1'),SPAN('Người nhận hàng khác người đặt hàng',_class='col-md-11 title_form',_style="line-height: 50px;"),_class='col-md-12'),_class='row'))
	
	div1 = DIV(_class="form-group col-md-6")
	div1.append(INPUT(_type='text',_class="form-control",_name='name2',_placeholder="Người nhận hàng"))
	
	div2 = DIV(_class="form-group col-md-6")
	div2.append(INPUT(_type='text',_class="form-control",_name='dien_thoai2',_placeholder="Số điện thoại"))
	form.append(DIV(div1,div2,_class='row hident',_id='nhan_hang'))
	
	div1 = DIV(_class="form-group",_style="width: 100%;  display: inline-block;")
	div1.append(H4('Địa chỉ nhận hàng' ,_class='title_form'))
	div1.append(INPUT(_type='text',_class="form-control",_name='dia_chi',_placeholder="Địa chỉ nhận hàng",_style="width: 100%; "))
	form.append(div1)
	
	div1 = DIV(_class="form-group")
	# div1.append(LABEL('Lời nhắn'))
	div1.append(TEXTAREA(_class="form-control",_rows="3",_name='description',_placeholder="Lời nhắn",_style="width: 100%; "))
	form.append(div1)
	
	ajax = "ajax('%s', ['name','dia_chi','dien_thoai','name2' ,'dien_thoai2','description'], 'form_thanh_toan')"%(URL(f='act_add_cart'))
	form.append(A(I(_class='icon-backward'),' Quay lại giỏ hàng',_href=URL(c='portal',f='folder',args=['checkout']), _class='pull-left'))
	form.append(A(I(_class='fa fa-cart-arrow-down'),' ĐẶT HÀNG ',_onclick=ajax, _class='btn btn-success pull-right btn_naso'))
	
	scr ='''
		<script>
			function check_show() {
			  document.getElementById("nhan_hang").classList.add("show");
			}
		</script>
		''' 
	form.append(XML(scr))
	return form

def act_add_cart():
	if request.vars.dien_thoai:
		cms.define_table('don_hang')
		cms.define_table('item_don_hang')
		import datetime
		don_hang_id = cms.db.don_hang.insert(folder=71,name=request.vars.name,dien_thoai=request.vars.dien_thoai,name2=request.vars.name2,dien_thoai2=request.vars.dien_thoai2,dia_chi=request.vars.dia_chi,description=request.vars.description,created_on=datetime.datetime.now())
		if don_hang_id:
			from plugin_process import ProcessModel
			process = ProcessModel()
			objects = process.define_objects(True)
			
			objects_id =objects.insert(folder=71,foldername='don-hang' ,tablename='don_hang',table_id=don_hang_id ,auth_group=10,process=57)
			if request.cookies.has_key('cart_shop'):
				carts = eval(request.cookies['cart_shop'].value)
				for cart in carts:
					cart = eval(cart)
					row = db((db.product.id==cart['id'])).select().first()	
					if row:
						item = cms.db.item_don_hang.insert(don_hang=don_hang_id,product=row.id,r_number=cart['num'],price=row.price)
					
			
		response.cookies['cart_shop'] = 'invalid' 
		response.cookies['cart_shop']['expires'] = -10 
		response.cookies['cart_shop']['path'] = '/' 
		div = DIV(B('Đặt hàng thành công. Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất để xác nhận đơn hàng. Xin cảm ơn! '),_class='bg-info text-center' )
		div.append(DIV(BR(),'Chuyển hướng về trang chủ sau 3 giây.',_class='bg-info text-center' ))
		scr ='''
		 <META http-equiv="refresh" content="3;URL=%s">
		'''%(URL(c='portal',f='folder',args=[page_home]))
		div.append(XML(scr))
		
		return div
	else:
		div = DIV(B('Đặt hàng lỗi, Bạn vui lòng nhập đầy đủ tên, số điện thoại, địa chỉ. Xin cảm ơn! '),_class='bg-info text-center' )
		div.append(DIV(BR(),'Trở lại form đặt hàng sau 10 giây.',_class='bg-info text-center' ))
		scr ='''
		 <META http-equiv="refresh" content="10;URL=%s">
		'''%(URL(c='portal',f='folder',args=['thanh-toan']))
		div.append(XML(scr))
		return div
	

	
def robots():
	return 'OK'
	
def sitemaps():
	dcontent = cms.define_table(tablename ='dcontent',migrate=False)
	rows= cms.db(dcontent.id>0).select()
	response.view = 'default/sitemaps.xml'
	return dict(urls=rows,languages = [])

# def search():
	# try:
		# dcontent = cms.define_table(tablename ='dcontent',migrate=True)
		# txt = request.vars.key_search
		# rows= cms.db(dcontent.textcontent.like('%'+str(txt)+'%')).select()
		
		# div = DIV(_id='page_search')
		
		# if len(rows)>0:
			# div.append(H2(len(rows),T(' Kết quả tìm kiếm cho từ khóa: "'),request.vars.key_search,'"',_id='title_page'))
			# ul=UL()
			# for row in rows:
				# code = '<i style=" background: yellow;">'+request.vars.key_search+'</i>'
				# name =  row.name.replace(request.vars.key_search,code)

				# name =  name.replace(request.vars.key_search.lower(),code)
				# name =  name.replace(request.vars.key_search.upper(),code)
				# li = LI(A(B(XML(name)),_href=cms.url_content(row),_class='name'))
				# if row.description:
					# description =  row.description.replace(request.vars.key_search,code)
					# li.append(P(XML(description)))
				# ul.append(li)
			# div.append(ul)
		# else:
			# div.append(H2(T('Kết quả tìm kiếm từ khóa: "'),request.vars.key_search,'"',_id='title_page'))
			# div.append(P(T('Không có kết quả nào cho từ khóa này.')))
			
		# return div
	# except Exception,e: return e
	
def search_ck():

	dcontent = cms.define_table(tablename ='dcontent',migrate=True)
	txt = request.vars.key_anchor
	rows = cms.db(dcontent.textcontent.like('%'+str(txt)+'%')).select()
	div = DIV(_id='page_search')
	
	if len(rows)>0:
		div.append(H4(len(rows),T(' Kết quả tìm kiếm cho từ khóa: "'),request.vars.key_anchor,'"',_id='title_page'))
		ul=UL()
		for row in rows:
			code = '<i style=" background: yellow;">'+request.vars.key_anchor+'</i>'
			name =  row.name.replace(request.vars.key_anchor,code)

			name =  name.replace(request.vars.key_anchor.lower(),code)
			name =  name.replace(request.vars.key_anchor.upper(),code)
			li = LI(A(XML(name),_href=cms.url_content(row),_target="_blank",_class='name'))
			ul.append(li)
		div.append(ul)
	else:
		div.append(H2(T('Kết quả tìm kiếm từ khóa: "'),request.vars.key_anchor,'"',_id='title_page'))
		div.append(P(T('Không có kết quả nào cho từ khóa này.')))
		
	return div
	

def search():
	try:
		dcontent = cms.define_table(tablename ='dcontent',migrate=False)
		txt = request.vars.key_search
		if isinstance(txt,list):
			for t in txt:
				if t!="":
					txt = t
		rows= cms.db(dcontent.textcontent.like('%'+str(txt)+'%')).select()
		div = DIV(_id='page_search')
		
		if len(rows)>0:
			div.append(H2(len(rows),T(' Kết quả tìm kiếm cho từ khóa: "'),txt,'"',_id='title_page'))
			ul=UL()
			for row in rows:
				code = '<i style=" background: yellow;">'+txt+'</i>'
				name =  row.name.replace(txt,code)

				name =  name.replace(txt.lower(),code)
				name =  name.replace(txt.upper(),code)
				li = LI(A(B(XML(name)),_href=cms.url_content(row),_class='name'))
				if row.description:
					description =  row.description.replace(txt,code)
					li.append(P(XML(description)))
				ul.append(li)
			div.append(ul)
		else:
			div.append(H2(T('Kết quả tìm kiếm từ khóa: "'),txt,'"',_id='title_page'))
			div.append(P(T('Không có kết quả nào cho từ khóa này.')))
			
		return div
	except Exception,e: return e
	

def form_salesman():
	if request.vars.doi_nhom:
		return LOAD(c='plugin_app',f='thong_tin_daily',args=request.args,vars=request.vars,ajax=False)
	else:
		return LOAD(c='plugin_app',f='form_salesman',args=request.args,vars=request.vars,ajax=False)
	
	

def check_name_code():
	auth_name = request.vars.auth_name
	if len(auth_name)<6: return  SPAN("Tên đăng nhập cần dài hơn 6 ký tự")
	user_check = db(db.auth_user.username==auth_name).count()
	ajax = "ajax('%s', ['auth_name'], 'check_auth_user')"%(URL(c='portal',f='check_auth_user'))
	if user_check>0:
		return SPAN("Tên đăng nhập đã tồn tại")
	else:
		return SPAN("Tên đăng nhập hợp lệ")
		
def check_auth_user():
	auth_name = request.vars.auth_name
	if len(auth_name)<6: return  SPAN("Tên đăng nhập cần dài hơn 6 ký tự")
	user_check = db(db.auth_user.username==auth_name).count()
	ajax = "ajax('%s', ['auth_name'], 'check_auth_user')"%(URL(c='portal',f='check_auth_user'))
	if user_check>0:
		return SPAN("Tên đăng nhập đã tồn tại")
	else:
		return SPAN("Tên đăng nhập hợp lệ")

def view_van_don():
	from plugin_app import number_format
	
	don_hang= cms.define_table('don_hang')
	item_don_hang= cms.define_table('item_don_hang')
	product= cms.define_table('product')
	div = DIV(_id="view_van_don")
	id_don = request.args(1)
	if not id_don: return 'Mã đơn hàng không xác định'
	row_dh = db(don_hang.id==id_don).select().first()
	if not row_dh: return "Mã đơn hàng không hợp lệ"
	
	div.append(DIV(SPAN('Đơn hàng: ',row_dh.id,_class='pull-left'),_class="title_page"))
	ct = DIV(H4('Thông tin mua hàng',_class='col-lg-12 p10 bb'),_class='box_content')
	
	ct.append(DIV(DIV(DIV('Người đặt hàng: ',B(row_dh.name),_class='col-lg-6'),DIV('Số điện thoại: ',B(row_dh.dien_thoai),_class='col-lg-6'),_class='row'),_class='col-lg-12 p10'))
	if row_dh.name2 !="":
		ct.append(DIV(DIV(DIV('Người nhận hàng: ',B(row_dh.name2),_class='col-lg-6'),DIV('Số điện thoại: ',B(row_dh.dien_thoai2),_class='col-lg-6'),_class='row'),_class='col-lg-12 p10'))
	ct.append(DIV(DIV('Địa chỉ: ',B(row_dh.dia_chi)),_class='col-lg-12 p10'))
	ct.append(DIV(DIV('Lưu ý: ',B(row_dh.description)),_class='col-lg-12 p10'))
	
	ct.append(H4("Chi tiết đơn hàng",_class='col-lg-12 p10'))
	table= TABLE(TR(TH("Stt"),TH('Sản phẩm'),TH('Đơn giá'),TH('Số lượng'),TH('Thành tiền')),_class='table')
	row_item = db(item_don_hang.don_hang==row_dh.id).select()
	i = 1
	tong_tien = 0
	for row in row_item:
		row_prd = db(product.id==row.product).select().first()
		table.append(TR(TD(i),TD(row_prd.name),TD(number_format(row.price),' đ'), TD(row.r_number ),TD(number_format(row.price*row.r_number),' đ' )))
		tong_tien +=row.price*row.r_number
	table.append(TR(TD(B('TỔNG TIỀN'),_colspan='4',_class='text-center'),TD(B(number_format(tong_tien),' đ' ))))
	ct.append(table)
	
	div.append(ct)
	
	
	
	
	return div 


