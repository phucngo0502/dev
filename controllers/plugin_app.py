# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
api_link = 'https://quanly.ghephang.com/gh'
import gluon.contrib.simplejson


@auth.requires_login()
def index():
	return dict(content=H2('Plugin App'))

def lead_add():
	import requests
	url = '%s/apiweb/lead_add.json' % (api_link)
	data = {
		"name": request.vars.fname,
		"phone": request.vars.fphone,
		"description": request.vars.fdes,
		"lead_type": 0,
		"lead_source": 'web',
		 
	}
	try:
		x = requests.get(url, json=data)
		return DIV(x.text,_style=" min-height: 415px;    text-align: center;    width: 100%;    display: block;    line-height: 400px;")
	except: return DIV('Không thể kết nối tới hệ thống',_style=" min-height: 415px;    text-align: center;    width: 100%;    display: block;    line-height: 400px;")
def get_orders():
    try:
        url = '%s/api_v1/get_orders.json?list_order=%s' % (api_link, request.vars.fname.replace('DH', '').replace(' ', '').replace('	', ''))
        headers = {'Content-Type': 'application/json; charset=UTF-8'}

        r_content = requests.get(url).json()

        div = DIV(_class="trackingItem")
        for item in r_content['result']:
            if item['status']:
                divt = DIV(_class="row mt-3 item")
                divt.append(H4('THÔNG TIN VẬN ĐƠN ', _class="title_box"))

                d1 = DIV(_class="col-md-6")
                d1.append(DIV(DIV(' Mã phiếu gửi: ', _class="text-left"), DIV('DH', item['order_code'], _class="text-left bold"), _class="d-flex justify-content-between"))
                d1.append(DIV(DIV(DIV('  Người gửi:  ', _class="text-left"), DIV(item['data']['customer_send']['name'], _class="text-left bold"), _class="d-flex justify-content-between")))
                d1.append(DIV(DIV('  Địa chỉ gửi:  ', _class="text-left"), DIV('*** ', item['data']['customer_send']['district_name'], ', ', item['data']['customer_send']['city_name'], _class="text-left bold"), _class="d-flex justify-content-between"))
                d1.append(DIV(DIV('  Người nhận:  ', _class="text-left"), DIV(item['data']['customer_receive']['name'], _class="text-left bold"), _class="d-flex justify-content-between"))
                d1.append(DIV(DIV('  Địa chỉ nhận:  ', _class="text-left"), DIV('*** ', item['data']['customer_receive']['district_name'], ', ', item['data']['customer_receive']['city_name'], _class="text-left bold"), _class="d-flex justify-content-between"))
                divt.append(d1)

                d2 = DIV(_class="col-md-6")
                d2.append(DIV(DIV(' Khối lượng (Kg): ', _class="text-left"), DIV(item['data']['order_mass'], _class="text-left bold"), _class="d-flex justify-content-between"))
                d2.append(DIV(DIV('  Dịch vụ:  ', _class="text-left"), DIV(item['data']['n_order_delivery_method'], _class="text-left bold"), _class="d-flex justify-content-between"))
                d2.append(DIV(DIV('  Trạng thái:  ', _class="text-left"), DIV(item['data']['n_order_status_name'], _class="text-left bold"), _class="d-flex justify-content-between"))

                divt.append(d2)

                div_log = DIV(_class='trackingItem mt-3 p-4')

                for tracking in item['data']['log_tracking']:
                    ul = UL(_class="timeline pb-3")

                    # Decode Unicode escaped sequences
                    description_decoded = tracking['description'].encode().decode('unicode_escape')

                    # Xử lý HTML trực tiếp bằng BeautifulSoup
                    soup = BeautifulSoup(description_decoded, 'html.parser')
                    html_content = soup.prettify()

                    ul.append(LI(SPAN(tracking['time_stamp'], _class='txt-color-red '), DIV(XML(html_content), _class="event")))
                    div_log.append(ul)

                divt.append(div_log)
                div.append(divt)
            else:
                div.append(DIV(H4('Không tìm được thông tin mã: %s ' % item['order_code'].encode('utf-8'), _class="title_box"), _class="row mt-3 item"))
        return div
    except Exception as e:
        return e
def get_location(id):
	try:
		import requests
		url = '%s/api_v1/location.json?list_order=%s'%(api_link,request.vars.fname)
		return requests.get(url).json()
	except:
		return {}


def location_jsadd():
	div = DIV()
	url = '%s/api_v1/locations.json'%api_link
	script = SCRIPT("""
		var citis = document.getElementById("city");
		var district = document.getElementById("district");
		var ward = document.getElementById("ward");
		var url_link = "%s";
		var Parameter = {
			 url: url_link , 
		     method: "GET", 
		     headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
		};
		
		var promise = axios(Parameter);
		promise.then(function (result) {
		  renderCity(result.data);
		});
		function renderCity(data) {
		  for (const x of data) {
			citis.options[citis.options.length] = new Option(x.name, x.id);
		  }
		  citis.onchange = function () {
		    district.length = 1;
		    ward.length = 1;
		    var p_dis = {
		      url: url_link +"?country=VN&parentId=" + citis.value,
		      method: "GET", 
		    headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
		      
		    };
		    var promise_dis = axios(p_dis);
		    promise_dis.then(function (result) {
		      renderDis(result.data);
		    });
		  }
		}
		function renderDis(data) {
		  for (const x of data) {
		    district.options[district.options.length] = new Option(x.name, x.id);
		  }
		   district.onchange = function () {
		        ward.length = 1;
		    var p_ward = {
		      url: url_link +"?country=VN&parentId=" + district.value,
		      method: "GET", 
		      headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
		    };
		    var promise_ward = axios(p_ward);
		     promise_ward.then(function (result) {
		      renderWard(result.data);
		    });
		  }
		}
		function renderWard(data) {
		  for (const x of data) {
		    ward.options[ward.options.length] = new Option(x.name, x.id);
		  }
		}
	
	$('#act_submit_ao').click(function(){
		var flagValidate = true;
		if(!$('#code').val()){$('#errcode').text('Mã kho hàng không được để trống');flagValidate = false;}
		if(!$('#name').val()){$('#errname').text('Tên kho hàng không được để trống');flagValidate = false;}
		if(!$('#address').val()){$('#erraddress').text('Địa chỉ không được để trống');flagValidate = false;}
		if(flagValidate){$("#act_submit").trigger('click');}
	});
	$('.closemodals').attr({'data-dismiss':'modal'});
	""" % (url))
	div.append(INPUT(_id='city',_name='city'))
	div.append(INPUT(_id='district',_name='district'))
	div.append(script)
	
	return div



##########################################################
# WIDGET SELECT2
##########################################################

def select2():
	content = SELECT(OPTION("Select .....", _selected=True), _name="select2", _class="select2", _id="select2")
	return dict(content=content)


def get_select2():
	try:
		q = request.vars.q
		table = cms.define_table(request.args(0))
		field = request.args(1)
		db = cms.db
		results = []
		rows = db(table[field].contains(q)).select(table.id, table[field], limitby=(0, 30), orderby=table[field])
		for row in rows:
			results.append(dict(id=row.id, text=row[field]))
		return gluon.contrib.simplejson.dumps(results)
	except Exception, e:
		print e
		return ""


def widget_select_loca():
	from plugin_app import widget_select_loca
	return widget_select_loca(city=request.vars.city, dist=request.vars.dist, street=request.vars.street)


##########################################################
# WIDGET
##########################################################

def get_signer():
	from database import define_table
	define_table(db, auth, 'signer')
	if request.vars.org:
		orgs = request.vars.org
		if isinstance(orgs, str): orgs = [orgs]
		orgs = [int(org) for org in orgs]
		rows = db(db.signer.org.belongs(orgs)).select(orderby=db.signer.position)
		options = [OPTION(row.name + ' [' + row.post.name + ']', _value=row.id) for row in rows]
	else:
		options = []
	select = SELECT(options, _name='signer', _id='archives_signer', _multiple=(len(orgs) > 1))
	return select


##########################################################
# TreeView
##########################################################
@auth.requires_login()
def treedepth():
	from plugin_app import get_tree
	attr = {}
	for key in request.vars.keys(): attr[key] = request.vars[key]
	attr['depth'] = 1
	selected = attr.get('selected', [])
	selected = [int(id) for id in selected]
	attr['selected'] = selected
	tree = get_tree(db, auth, request.args(0), parent=int(request.args(1)), **attr)
	return tree


##########################################################
# DropDown
##########################################################
@auth.requires_login()
def create_dropdown():
	table, field = request.args(0).split('.')
	cms.define_table(table)
	refereed = db[table][field].type[10:] if db[table][field].type[:9] == 'reference' else db[table][field].type[15:]
	db[table][field].requires = IS_IN_DB(db, refereed + '.id', '%(name)s')
	from gluon.tools import Crud
	crud = Crud(cms.db)
	cms.define_table(refereed)
	form = crud.create(db[refereed])
	if form.vars.id: session['_plugin_dropbox:%s' % request.args(0)] = form.vars.id
	options = UL(*[LI(v) for k, v in db[table][field].requires.options() if k == str(form.vars.id)])
	return dict(form=form, options=options)


def select_dropdown():
	if not auth.user_id or not session.get('_plugin_dropbox:%s' % request.args(0), None): raise HTTP(400)
	table, field = request.args(0).split('.')
	db = cms.db
	cms.define_table(table)
	if db[table][field].type[:9] == 'reference':
		refereed = db[table][field].type[10:]
		multiple = False
	else:
		refereed = db[table][field].type[15:]
		multiple = True
	db[table][field].requires = IS_IN_DB(db, refereed + '.id', '%(name)s', multiple=multiple)
	return TAG[''](*[OPTION(v, _value=k, _selected=(k == str(session['_plugin_dropbox:%s' % request.args(0)]))) \
		for k, v in db[table][field].requires.options()])


def get_items():
	itms = []
	if request.vars.q and request.vars.table and request.vars.field:
		q = request.vars.q
		f = request.vars.field
		t = request.vars.table
		fld = db[t][f]
		rows = db(fld.upper().like(q.upper() + "%")).select(fld, distinct=True)
		itms = [str(t[f]) for t in rows]
	return '\n'.join(itms)


def get_name():
	itms = []
	from plugin_cms import Cms
	cms = Cms()
	if request.vars.q and request.vars.table and request.vars.field:
		q = request.vars.q
		f = request.vars.field
		t = request.vars.table
		try:
			dtable = eval('cms.define_table("%s",True)' % t)

			rows = cms.db(dtable[f].upper().like("%" + q.upper() + "%")).select(dtable[f], distinct=True)
			for r in rows:
				itms.append(r[f])
		except Exception, e:
			print e
	return '\n'.join(itms)


def get_chuc_vu():
	try:
		from plugin_process import Process

		archives = Process().cms.define_table('archives')
		row = Process().cms.db(archives.user_signed == request.vars.user_signed).select().last()
		if row:
			return INPUT(_class="string form-control ac_input", _id="archives_user_office", _name="user_office", _type="text", _autocomplete="off", _value=row.user_office)
		else:
			return INPUT(_class="string form-control ac_input", _id="archives_user_office", _name="user_office", _type="text", _autocomplete="off", _value='')
	except Exception, e:
		print e


def get_co_quan():
	try:
		from plugin_process import Process

		archives = Process().cms.define_table('archives')
		row = Process().cms.db(archives.user_signed == request.vars.user_signed).select().last()
		if row:
			return INPUT(_class="string form-control ac_input", _id="archives_org_publish", _name="org_publish", _type="text", _autocomplete="off", _value=row.org_publish)
		else:
			return INPUT(_class="string form-control ac_input", _id="archives_org_publish", _name="org_publish", _type="text", _autocomplete="off", _value='')
	except Exception, e:
		print e


# def add_hoi_dap():
# from plugin_cms import Cms
# from plugin_cms import CmsFolder
# cms = Cms()
# hoi_dap = cms.define_table('hoi_dap')
# id = cms.db.hoi_dap.insert(folder=request.args(0),name=request.vars.name,description=request.vars.description,nguoi_hoi=request.vars.nguoi_hoi,dien_thoai=request.vars.dien_thoai,email=request.vars.email)
# if id:
# from plugin_process import ProcessModel
# objects = ProcessModel().define_objects()
# objects_id = objects.insert(folder=request.args(0),foldername='hoi_dap',tablename='hoi_dap',table_id=id,auth_group=7,process=21)
# print objects_id

# div = DIV(B('Gửi câu hỏi thành công!'),_class='bg-info text-center' )
# div.append(DIV(BR(),'Chuyển hướng sau 3 giây.',_class='bg-info text-center' ))
# scr ='''
# <META http-equiv="refresh" content="3;URL=%s">
# '''%(URL(c='portal',f='folder',args=['hoi-dap']))
# div.append(XML(scr))
# return div

def add_hoi_dap():
	from plugin_cms import Cms
	cms = Cms()
	hoi_dap = cms.define_table('hoi_dap')
	if not request.vars.name:
		return DIV(B('Bạn chưa nhập tiêu đề câu hỏi'), _class='bg-do text-center')
	if not request.vars.description:
		return DIV(B('Bạn chưa nhập câu hỏi'), _class='bg-do text-center')
	if not request.vars.nguoi_hoi:
		return DIV(B('Bạn chưa nhập họ tên'), _class='bg-do text-center')
	if not request.vars.dien_thoai:
		return DIV(B('Bạn chưa nhập số điện thoại'), _class='bg-do text-center')

	id = cms.db.hoi_dap.insert(folder=request.args(0), name=request.vars.name, description=request.vars.description, email=request.vars.email, dien_thoai=request.vars.dien_thoai, nguoi_hoi=request.vars.nguoi_hoi)
	if id:
		from plugin_process import ProcessModel
		objects = ProcessModel().define_objects()
		objects_id = objects.insert(folder=request.args(0), foldername='hoi-dap', tablename='hoi_dap', table_id=id, auth_group=8, process=36)
	div = DIV(B('Gửi câu hỏi thành công!'), _class='bg-info text-center')
	return div


def add_h_comment():
	from plugin_cms import Cms
	cms = Cms()
	h_comment = cms.define_table('h_comment')
	if (request.vars.name != '') & (request.vars.description != ''):
		id = cms.db.h_comment.insert(folder=15, name=request.vars.name, description=request.vars.description, email=request.vars.email, tablename=request.args(1), tableid=request.args(2))
	else:
		return DIV(B('Chưa nhập đủ các trường dữ liệu!'), _class='bg-info text-center')
	if id:
		from plugin_process import ProcessModel
		objects = ProcessModel().define_objects()
		objects_id = objects.insert(folder=15, foldername='binh-luan-tin-tuc', tablename='h_comment', table_id=id, auth_group=8, process=31)
		print objects_id
	div = DIV(B('Gửi bình luận thành công!'), _class='bg-info text-center')
	return div


def search():
	folder = "ban-nha-dat"
	if request.vars.folder:
		folder = request.vars.folder
	vars = dict()
	if request.vars.city and (request.vars.city != '0'):
		vars['city'] = request.vars.city

	if request.vars.dist and (request.vars.dist != '0'):
		vars['dist'] = request.vars.dist

	if request.vars.street and (request.vars.street != '0'):
		vars['street'] = request.vars.street

	if request.vars.trend and (request.vars.trend != '0'):
		vars['trend'] = request.vars.trend

	if request.vars.group_price and (request.vars.group_price != '0'):
		vars['group_price'] = request.vars.group_price
	redirect(URL(c=request.vars.folder, vars=vars))


def test():
	from plugin_app import mony_format
	return mony_format(request.args(0))


def update_cookies():
	if request.vars[request.args(0)]:
		response.cookies[request.args(0)] = request.vars[request.args(0)].replace('/', '')
		response.cookies[request.args(0)]['expires'] = 24 * 3600
		response.cookies[request.args(0)]['path'] = '/'
	return portlet.display(136)


def dia_ban():
	v_tinh = request.vars.tinh or 3
	v_huyen = request.vars.huyen or 0
	v_xa = request.vars.xa or 0

	d_tinh = cms.define_table('d_tinh')
	d_huyen = cms.define_table('d_huyen')
	d_xa = cms.define_table('d_xa')

	tinhs = db(db.d_tinh.status == True).select()
	options_tinh = []
	for t in tinhs:
		if v_tinh:
			if t.id == int(v_tinh):
				options_tinh.append(OPTION(t.name, _value=t.id, _selected='selected'))
			else:
				options_tinh.append(OPTION(t.name, _value=t.id))
		else:
			if t.id == int(29):
				options_tinh.append(OPTION(t.name, _value=t.id, _selected='selected'))
			else:
				options_tinh.append(OPTION(t.name, _value=t.id))

	div = DIV(_id='dia_ban')
	ajax = "ajax('%s',['tinh','huyen','xa'],'dia_ban')" % URL(c='plugin_app', f='dia_ban')
	div.append(DIV(SELECT(options_tinh, _name='tinh', _id='d_tinh', _class="select2 vantai_select2", _onchange=ajax), _class=' col-md-4'))
	huyen_first = 0
	try:
		if v_tinh != 0:
			huyens = db((db.d_huyen.status == True) & (db.d_huyen.d_tinh == v_tinh)).select()
			# Lấy danh sách huyện
			options_huyen = []
			if len(huyens) > 0: huyen_first = huyens[0].id
			for h in huyens:
				if str(h.id) == v_huyen:
					options_huyen.append(OPTION(h.name, _value=h.id, _selected='selected'))
				else:
					options_huyen.append(OPTION(h.name, _value=h.id))
			div.append(DIV(SELECT(options_huyen, _name='huyen', _id='d_huyen', _class="select2 vantai_select2", _onchange=ajax), _class=' col-md-4'))
		else:
			huyens = db((db.d_huyen.status == True) & (db.d_huyen.d_tinh == 29)).select()
			# Lấy danh sách huyện
			if len(huyens) > 0: huyen_first = huyens[0].id
			options_huyen = []
			for h in huyens:
				if str(h.id) == v_huyen:
					options_huyen.append(OPTION(h.name, _value=h.id, _selected='selected'))
				else:
					options_huyen.append(OPTION(h.name, _value=h.id))
			div.append(DIV(SELECT(options_huyen, _name='huyen', _id='d_huyen', _class="select2 vantai_select2", _onchange=ajax), _class=' col-md-4'))
	# div.append(SELECT([OPTION("Cần chọn huyện",_value=0)],_name='huyen',_id='d_huyen',_class="select2 vantai_select2",_onchange=ajax))
	except Exception, e:
		return e

	try:
		if v_huyen != 0:
			xas = db((db.d_xa.status == True) & (db.d_xa.d_huyen == v_huyen)).select()

			options_xa = []
			for x in xas:
				if str(x.id) == v_xa:
					options_xa.append(OPTION(x.name, _value=x.id, _selected='selected'))
				else:
					options_xa.append(OPTION(x.name, _value=x.id))
			div.append(DIV(SELECT(options_xa, _name='xa', _id='d_xa', _class="select2 vantai_select2"), _class=' col-md-4'))
		else:
			if huyen_first != 0:
				xas = db((db.d_xa.status == True) & (db.d_xa.d_huyen == huyen_first)).select()
				options_xa = []
				for x in xas:
					if str(x.id) == v_xa:
						options_xa.append(OPTION(x.name, _value=x.id, _selected='selected'))
					else:
						options_xa.append(OPTION(x.name, _value=x.id))
				div.append(DIV(SELECT(options_xa, _name='xa', _id='d_xa', _class="select2 vantai_select2"), _class=' col-md-4'))
			else:
				div.append(DIV(SELECT([OPTION("Cần chọn xã", _value=0)], _name='xa', _id='d_xa', _class="select2 vantai_select2"), _class=' col-md-4'))
	except Exception, e:
		div.append(DIV(e))
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


def d_tinh():
	v_tinh = request.vars.tinh or 3

	d_tinh = cms.define_table('d_tinh')

	tinhs = db(db.d_tinh.status == True).select()
	options_tinh = []
	for t in tinhs:
		if v_tinh:
			if t.id == int(v_tinh):
				options_tinh.append(OPTION(t.name, _value=t.id, _selected='selected'))
			else:
				options_tinh.append(OPTION(t.name, _value=t.id))
		else:
			if t.id == int(29):
				options_tinh.append(OPTION(t.name, _value=t.id, _selected='selected'))
			else:
				options_tinh.append(OPTION(t.name, _value=t.id))

	div = DIV(_id='dia_ban')
	div.append(DIV(SELECT(options_tinh, _name='d_tinh', _id='d_tinh', _class="select2 vantai_select2")))

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


# Form full thông tin
# def form_add_salesman():
# form = DIV(H4("THÔNG TIN ĐĂNG KÝ ĐẠI LÝ",_class='text-center'),_id='dang_ky_salesman')
# form.append(P("Vui lòng nhập thông tin chính xác để đảm bảo quyền lợi cho đại lý.",_class='text-center margin_bottom30'))

# ajax = "ajax('%s', ['doi_nhom'], 'check_code_name')"%(URL(c='plugin_app',f='check_code_name'))
# div3 = DIV(LABEL("Mã giới thiệu"),_class="form-group col-md-4")
# div3.append(DIV(INPUT(_type='text',_class="form-control",_name='doi_nhom',_placeholder=" Nhập mã  ",_id='auth_name',_onfocusout=ajax,_value=request.vars.doi_nhom if request.vars.doi_nhom else '')))
# div3.append(DIV(_id='check_code_name',_class='div_alert'))

# form.append(DIV(div3,_class='row'))

# div1 = DIV(LABEL("Họ và tên"),_class="form-group col-md-4")
# div1.append(INPUT(_type='text',_class="form-control",_name='name',_id='name'))

# div2 = DIV(LABEL("Ngày sinh"),_class="form-group col-md-6")
# div2.append(INPUT(_type='text',_class="form-control date",_name='birthday',_id='birthday',_placeholder="../../.."))

# gioi_tinh = SELECT(_name='sex',_id='sex',_class="select2 gioi_tinh_select2")
# gioi_tinh.append(OPTION("Nam" ,_value="Nam"))
# gioi_tinh.append(OPTION("Nữ" ,_value="Nữ"))

# div4 = DIV(LABEL("Giới tính"),_class="form-group col-md-6")
# div4.append(gioi_tinh)


# div_gr = DIV(DIV(div2,div4,_class='row'),_class="form-group col-md-4")

# ajax = "ajax('%s', ['auth_name'], 'check_auth_user')"%(URL(c='plugin_app',f='check_auth_user'))
# div3 = DIV(LABEL("Tên đăng nhập"),_class="form-group col-md-4")
# div3.append(DIV(INPUT(_type='text',_class="form-control",_name='auth_name',_placeholder=" Viết liền, không dấu ",_id='auth_name',_onfocusout=ajax)))
# div3.append(DIV(_id='check_auth_user',_class='div_alert'))

# form.append(DIV(div3,div1,div_gr,_class='row'))

# ajax = "ajax('%s', ['phone'], 'check_phone')"%(URL(c='plugin_app',f='check_phone'))
# div1 = DIV(LABEL("Số điện thoại"),_class="form-group col-md-4")
# div1.append(INPUT(_type='text',_class="form-control",_name='phone',_placeholder="091...",_id='phone',_onfocusout=ajax))
# div1.append(DIV(_id='check_phone',_class='div_alert'))

# div2 = DIV(LABEL("Email"),_class="form-group col-md-4")
# div2.append(INPUT(_type='text',_class="form-control",_name='email',_id='email',_placeholder="Email"))

# div3 = DIV(LABEL("Địa chỉ"),_class="form-group col-md-4")
# div3.append(d_tinh())

# form.append(DIV(div1,div2,div3,_class='row'))


# div1 = DIV(LABEL("Căn Cước/Passport"),_class="form-group col-md-4")
# div1.append(INPUT(_type='text',_class="form-control",_name='id_card',_id='id_card'))

# div2 = DIV(LABEL("Ngày cấp"),_class="form-group col-md-4")
# div2.append(INPUT(_type='text',_class="form-control date",_name='id_day',_id='id_day',_placeholder="../../...."))

# div3 = DIV(LABEL("Nơi cấp"),_class="form-group col-md-4")
# div3.append(INPUT(_type='text',_class="form-control",_name='id_by',_id='id_by'))

# form.append(DIV(div1,div2,div3,_class='row'))


# # div1 = DIV(_class="form-group")
# # div1.append(TEXTAREA(_class="form-control",_rows="3",_name='description',_placeholder="Lời nhắn",_style="width: 100%; "))
# # form.append(div1)

# div_dk = DIV("Tôi đồng ý tất cả ",A('Điều khoản đại lý'),' và ',A('Chính sách bảo mật'),' của Naso')
# form.append(DIV(INPUT(_type='checkbox',_style="float: left;margin-right: 15px;",_name='dieu_khoan',_id='dieu_khoan',_value='da_check'),div_dk,_class=" col-md-12",_style="line-height: 51px;"))

# form.append(DIV(_id='dang_ky_salesman_alert'))

# ajax = "ajax('%s', ['auth_name','name','birthday','sex','email','phone','d_tinh' ,'id_card','id_day','id_by','dieu_khoan'], 'dang_ky_salesman_alert')"%(URL(c='plugin_app',f='dang_ky_salesman',vars=request.vars))

# form.append(DIV(A(I(_class='fa fa-caret-right'),' ĐĂNG KÝ ',_onclick=ajax, _class='btn btn-success  btn_naso',_id='btn_dangky'),_class='text-center'))

# scr= '''
# <script>


# $('#auth_name').on('keypress', function (event) {
# var regex = new RegExp("^[a-zA-Z0-9]+$");
# var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
# if (!regex.test(key)) {
# event.preventDefault();
# return false;
# }
# });
# $('#phone').on('keypress', function (event) {
# var regex = new RegExp("^[0-9]+$");
# var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
# if (!regex.test(key)) {
# event.preventDefault();
# return false;
# }
# });
# </script>
# '''
# form.append(XML(scr))
# return form

def form_add_salesman():
	form = DIV(H4("THÔNG TIN ĐĂNG KÝ ĐẠI LÝ", _class='text-center'), _id='dang_ky_salesman')
	form.append(P("Vui lòng nhập thông tin chính xác để đảm bảo quyền lợi cho đại lý.", _class='text-center margin_bottom30'))

	# Mã giới thiệu
	ajax = "ajax('%s', ['doi_nhom'], 'check_code_name')" % (URL(c='plugin_app', f='check_code_name'))
	div1 = DIV(_class="form-group")
	div1.append(DIV(INPUT(_type='text', _class="form-control", _name='doi_nhom', _placeholder=" Nhập mã giới thiệu ", _id='name_code', _onfocusout=ajax, _value=request.vars.doi_nhom if request.vars.doi_nhom else '')))
	div1.append(DIV(_id='check_code_name', _class='div_alert'))

	# Họ và tên
	div2 = DIV(_class="form-group")
	div2.append(INPUT(_type='text', _class="form-control", _name='name', _id='name', _placeholder="Họ và tên"))
	div2.append(DIV(_id='check_code_name', _class='div_alert'))

	# Tên đăng nhập
	ajax = "ajax('%s', ['auth_name'], 'check_auth_user')" % (URL(c='plugin_app', f='check_auth_user'))
	div6 = DIV(_class="form-group")
	div6.append(DIV(INPUT(_type='text', _class="form-control", _name='auth_name', _placeholder="Tên đăng nhập ", _id='auth_name', _onfocusout=ajax)))
	div6.append(DIV(_id='check_auth_user', _class='div_alert'))

	# Số điện thoại
	ajax = "ajax('%s', ['phone'], 'check_phone')" % (URL(c='plugin_app', f='check_phone'))
	div7 = DIV(_class="form-group")
	div7.append(INPUT(_type='text', _class="form-control", _name='phone', _placeholder="Điện thoại", _id='phone', _onfocusout=ajax))
	div7.append(DIV(_id='check_phone', _class='div_alert'))

	# Email
	ajax = "ajax('%s', ['email'], 'check_email')" % (URL(c='plugin_app', f='check_email'))
	div8 = DIV(_class="form-group")
	div8.append(INPUT(_type='text', _class="form-control", _name='email', _id='email', _placeholder="Email", _onfocusout=ajax))
	div8.append(DIV(_id='check_email', _class='div_alert'))
	# Khu vực
	div9 = DIV(_class="form-group")
	div9.append(d_tinh())

	# Pass 1
	ajax = "ajax('%s', ['password'], 'check_pass')" % (URL(c='plugin_app', f='check_pass'))
	div10 = DIV(_class="form-group")
	div10.append(INPUT(_type='password', _class="form-control", _name='password', _id='password', _placeholder="Nhập mật khẩu", _onfocusout=ajax))
	div10.append(DIV(_id='check_pass', _class='div_alert'))
	# Pass 2
	ajax = "ajax('%s', ['password','password2'], 'check_pass2')" % (URL(c='plugin_app', f='check_pass2'))
	div11 = DIV(_class="form-group")
	div11.append(INPUT(_type='password', _class="form-control", _name='password2', _id='password2', _placeholder="Nhập lại mật khẩu", _onfocusout=ajax))
	div11.append(DIV(_id='check_pass2', _class='div_alert'))

	# form.append(DIV(div1,div2,_class='row'))
	# form.append(DIV(div6,div7,_class='row'))
	# form.append(DIV(div10,div8,_class='row'))
	# form.append(DIV(div11,div9,_class='row'))
	div_left = DIV(div1, div6, div10, div11, _class='col-md-6')
	div_right = DIV(div2, div7, div8, div9, _class='col-md-6')
	form.append(DIV(div_left, div_right, _class='row'))

	div_dk = DIV("Tôi đồng ý tất cả ", A('Điều khoản đại lý'), ' và ', A('Chính sách bảo mật'), ' của Naso')
	form.append(DIV(INPUT(_type='checkbox', _style="float: left;    margin-right: 15px;    height: 19px;", _name='dieu_khoan', _id='dieu_khoan', _value='da_check'), div_dk, _class=" col-md-12", _style="line-height: 25px;     margin-bottom: 15px;"))

	form.append(DIV(_id='dang_ky_salesman_alert'))

	ajax = "ajax('%s', ['auth_name','name','email','phone','d_tinh' ,'password','password2','dieu_khoan'], 'dang_ky_salesman_alert')" % (URL(c='plugin_app', f='dang_ky_salesman', vars=request.vars))

	form.append(DIV(A(I(_class='fa fa-caret-right'), ' ĐĂNG KÝ ', _onclick=ajax, _class='btn btn-success  btn_naso', _id='btn_dangky'), _class='text-center'))

	scr = '''
	<script>
	$('#auth_name').on('keypress', function (event) {
		var regex = new RegExp("^[a-zA-Z0-9]+$");
		var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
		if (!regex.test(key)) {
		   event.preventDefault();
		   return false;
		}
	});

	$('#email').on('keypress', function (event) {
		var regex = new RegExp("= /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;");
		var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
		if (!regex.test(key)) {
		   event.preventDefault();
		   return false;
		}
	});
	$('#phone').on('keypress', function (event) {
		var regex = new RegExp("^[0-9]+$");
		var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
		if (!regex.test(key)) {
		   event.preventDefault();
		   return false;
		}
	});
	</script>
	'''
	form.append(XML(scr))
	return form


# Không viết scrip nên bắt lỗi bằng code
def check_code_name():
	salesman = cms.define_table('salesman')
	doi_nhom = str(request.vars.doi_nhom)
	if doi_nhom == "": return SPAN("Naso sẽ tự phân nhóm nếu bạn để trống", _class='warning')
	user_check = db(salesman.name_code == doi_nhom).count()
	if user_check > 0:
		return ''
	else:
		return SPAN("Mã giới thiệu không hợp lệ", _class='warning')


def check_pass():
	password = request.vars.password
	if len(password) < 8:
		return SPAN("Mật khẩu cần trên 8 ký tự", _class='warning')
	elif password.isalpha():
		return SPAN("Mật khẩu cần chứa cả số", _class='warning')
	elif password.isdigit():
		return SPAN("Mật khẩu cần chứa cả chữ", _class='warning')
	else:
		return ""


def check_pass2():
	try:
		password = request.vars.password
		password2 = request.vars.password2
		if password == "":
			return SPAN("Bạn cần nhập mật khẩu ở trên trước", _class='warning')
		elif str(password) != str(password2):
			return SPAN("Bạn cần nhập giống mật khẩu trên", _class='warning')
		else:
			return ""
	except Exception, e:
		return e


def check_email():
	salesman = cms.define_table('salesman')
	email = request.vars.email
	try:
		if (email == "") or ('@' not in email) or ('.' not in email): return SPAN("Email không hợp lệ", _class='warning')
		user_check = db(salesman.email == email).count()
		if user_check > 0:
			return SPAN("Email đã đăng ký", _class='warning')
		else:
			return ''
	except Exception, e:
		return e


def check_phone():
	salesman = cms.define_table('salesman')
	phone = str(request.vars.phone)
	if len(phone) != 10: return SPAN("Số điện thoại không hợp lệ", _class='warning')
	user_check = db(salesman.phone == phone).count()
	if user_check > 0:
		return SPAN("Số điện thoại đã tồn tại", _class='warning')
	else:
		return ''


def check_auth_user():
	auth_name = request.vars.auth_name
	if len(auth_name) < 6: return SPAN("Tên đăng nhập cần dài hơn 6 ký tự", _class='warning')
	user_check = db(db.auth_user.username == auth_name).count()
	if user_check > 0:
		return SPAN("Tên đăng nhập đã tồn tại", _class='warning')
	else:
		return ''


# Thông tin đại lý
def thong_tin_daily():
	salesman = cms.define_table('salesman')
	form = DIV(_id='dang_ky_salesman')
	if request.vars.doi_nhom or request.vars.phone:
		row = db((salesman.name_code == request.vars.doi_nhom.replace(' ', '')) | (salesman.phone == request.vars.phone)).select().first()
		if row:

			div = DIV(H4('ĐẠI LÝ GIỚI THIỆU', _class=' margin_bottom30 text-center'), _class='col-lg-5 col-md-offset-3')
			div.append(IMG(_src=URL(c='static', f='site/naso/uploads/salesman', args=[row.avatar]), _class='col-lg-4'))
			div.append(DIV(H2(row.name), P('Điện thoại: ', row.phone), _class='col-lg-8 margin_bottom30'))
			ajax = "ajax('%s', [ ], 'dang_ky_salesman')" % (URL(c='plugin_app', f='form_add_salesman', vars=dict(doi_nhom=row.name_code)))
			div4 = DIV(A(I(_class='fa fa-caret-right'), ' Đăng ký ngay ', _onclick=ajax, _class='btn btn-success  btn_naso'), _class='text-center margin_top15')
			div.append(DIV(div4))

			form.append(DIV(div))
		else:
			form.append(H4("Thông tin đại lý giới thiệu không phù hợp. Vui lòng kiểm tra lại ", A("TẠI ĐÂY", _href="/hop-tac"), _class="text-center margin_bottom30"))

	else:
		form.append(DIV('Thiếu dữ liệu', _class="text-center"))
	return form


def form_salesman():
	form = DIV(H4("Thông tin đại lý giới thiệu", _class="text-center margin_bottom15"), _id='dang_ky_salesman')
	form.append(DIV("Nếu bạn chưa có đại lý giới thiệu, vui lòng nhập mã ", B('NASO2021'), ' để được giới thiệu đại lý', BR(), _class='margin_bottom30 text-center'))

	div1 = DIV(INPUT(_type='text', _class="form-control", _name='doi_nhom', _placeholder="Mã đại lý"))

	div2 = DIV('hoặc', _class="text-center")

	div3 = DIV(INPUT(_type='text', _class="form-control", _name='phone', _placeholder="Số điện thoại đại lý"), _class='form-group')

	ajax = "ajax('%s', ['phone','doi_nhom' ], 'dang_ky_salesman')" % (URL(c='plugin_app', f='thong_tin_daily'))
	div4 = DIV(A(I(_class='fa fa-caret-right'), ' Kiểm tra thông tin đại lý ', _onclick=ajax, _class='btn btn-success  btn_naso'), _class='text-center')

	form.append(DIV(div1, div2, div3, div4, _class='col-lg-4 col-md-offset-4'))

	return form


def input_focus(key):
	scr = '''
	<script>
		document.getElementById("%s").focus();
	</script>
	''' % key
	return XML(scr)


def test():
	salesman = cms.define_table('salesman')
	row = db(salesman.id == 7).update(birthday='2021-05-08')
	return row


def dang_ky_salesman():
	import datetime
	format = "%d/%m/%Y"

	salesman = cms.define_table('salesman')
	div = DIV()

	## Kiểm tra Mã giới thiệu hợp lệ
	doi_nhom = request.vars['doi_nhom']
	c_manager = None
	ma_code = ""
	s_manager = db(salesman.name_code == doi_nhom).select().first()
	if s_manager:
		c_manager = s_manager.id
		ma_code = doi_nhom
	# Kiểm tra có dữ liệu
	key_check = ['auth_name', 'name', 'phone', 'email']
	for key in key_check:
		if not request.vars[key]:
			div = DIV('Cần nhập %s' % (T('salesman_' + key)), _class='text-center')
			div.append(input_focus(key))
			return div

	# Kiểm tra định dạng ngày tháng
	# key_date =['birthday','id_day']
	# for key in key_date:
	# date_string = request.vars[key]
	# try:
	# datetime.datetime.strptime(date_string, format)
	# except Exception,e:
	# div =  DIV('Nhập sai định dạng ngày %s'%(T('salesman_'+key)),_class='text-center')
	# div.append(input_focus(key))
	# return div

	## Kiểm tra duy nhất của user_name
	auth_name = request.vars.auth_name
	if len(auth_name) < 6:
		div = DIV("Tên đăng nhập cần dài hơn 6 ký tự", _class='text-center')
		div.append(input_focus("auth_name"))
		return div
	user_check = db(db.auth_user.username == auth_name).count()
	if user_check > 0:
		div = DIV("Tên đăng nhập đã tồn tại. Vui lòng kiểm tra lại", _class='text-center')
		div.append(input_focus("auth_name"))
		return div

	## Kiểm tra mật khẩu
	password = request.vars.password
	password2 = request.vars.password2
	if len(password) < 8:
		div = DIV("Mật khẩu cần trên 8 ký tự", _class='text-center')
		div.append(input_focus("password"))
		return div
	if password.isalpha():
		div = DIV("Mật khẩu cần chứa cả số", _class='text-center')
		div.append(input_focus("password"))
		return div

	if password.isdigit():
		div = DIV("Mật khẩu cần chứa cả chữ", _class='text-center')
		div.append(input_focus("password"))
		return div

	if password != password2:
		div = DIV("2 mật khẩu không giống nhau", _class='text-center')
		div.append(input_focus("password2"))
		return div

	## Kiểm tra duy nhất của Điện thoại
	phone = str(request.vars.phone)
	if len(phone) != 10:
		div = DIV("Số điện thoại không hợp lệ", _class='text-center')
		div.append(input_focus("phone"))
		return div
	user_check = db(salesman.phone == phone).count()
	if user_check > 0:
		div = DIV("Số điện thoại đã tồn tại. Vui lòng kiểm tra lại", _class='text-center')
		div.append(input_focus("phone"))
		return div

	## Kiểm tra đồng ý điều khoản
	if request.vars.dieu_khoan != 'da_check':
		return DIV("Bạn cần đọc và chấp nhận Điều khoản đại lý và Chính sách bảo mật của Naso", _class='text-center')
	try:
		# birthday = datetime.datetime.strptime(request.vars.birthday, '%d/%m/%Y').strftime("%Y-%m-%d")
		# id_day = datetime.datetime.strptime(request.vars.id_day, '%d/%m/%Y').strftime("%Y-%m-%d")
		id = cms.db.salesman.insert(folder=256,
			s_manager=c_manager,
			name=request.vars.name,
			d_tinh=request.vars.d_tinh,
			phone=request.vars.phone,
			email=request.vars.email,
			created_on=datetime.datetime.now())
		if id:
			from plugin_process import ProcessModel
			process = ProcessModel()
			objects = process.define_objects(True)
			objects_id = objects.insert(folder=256, foldername='dai-ly', tablename='salesman', table_id=id, auth_group=18, process=76)

			first_name = request.vars.name.split(" ")[0]
			last_name = request.vars.name.replace(first_name, '')

			db.auth_user.insert(auth_group=18, role='Nhân viên', username=request.vars.auth_name, email=request.vars.email, password=db.auth_user.password.requires[0](password)[0], first_name=first_name, last_name=last_name)

			# Xử lý gửi email hoặc sms tại đây

			send_to = request.vars.email
			you_name = request.vars.name
			you_phone = request.vars.phone
			you_email = request.vars.email
			des = request.vars.description
			subject = "[Bahadi.vn] Thông tin đăng lý đại lý mới."
			# Nội dung gửi email
			div_email = DIV()
			div_email.append(H3("Bạn đã đăng ký đại lý tại Bahadi.vn với các thông tin:"))
			table = TABLE(TR(TD('Họ và tên'), TD(you_name), TD("Mã giới thiệu"), TD(ma_code if ma_code else '')), _style='width:700px; background:#eee; padding:10px;')
			table.append(TR(TD('Tên đăng nhập'), TD(request.vars.auth_name), TD('Mật khẩu'), TD(B(password))))
			# table.append(TR(TD('Sinh ngày'),TD(request.vars.birthday),TD('Giới tính'),TD(request.vars.sex)))
			table.append(TR(TD('Số điện thoại'), TD(request.vars.phone), TD('Email'), TD(request.vars.email)))
			# table.append(TR(TD('Tp/Tỉnh'),TD(request.vars.d_tinh),TD('Căn Cước/Passport'),TD(request.vars.id_card)))
			table.append(TR(TD('Tp/Tỉnh'), TD(request.vars.d_tinh), TD(''), TD('')))
			# table.append(TR(TD('Ngày cấp'),TD(request.vars.id_day),TD('Nơi cấp'),TD(request.vars.id_by)))
			div_email.append(table)
			# div_email.append(H4("(*) Sau khi đăng nhập bạn vui lòng đổi mật khẩu để đảm bảo an toàn cho tài khoản."))
			div_email.append(P("Mọi vấn đề sai sót, vướng mắc về tài khoản vui lòng liên hệ 0866 303 366 để được hỗ trợ."))

			mail = auth.setting_mail()
			if mail.send(to=send_to, subject=subject, message='<html>%s</html>' % str(div_email)):
				# cập nhật đã gửi tk qua email
				div.append(H4('Đăng ký thành công.', _class='text-center'))
			else:
				# cập nhật đã gửi tk qua email, cần lưu log để xử lý các email không gửi được.
				div.append(H4('Đăng ký thành công.', _class='text-center'))
			scr = '''
			 <META http-equiv="refresh" content="3;URL=%s">
			''' % (URL(c='plugin_auth', f='login'))
			div.append(XML(scr))
			return div
		else:
			div.append(H4('Đăng ký lỗi', _class='text-center'))
			scr = '''
			 <META http-equiv="refresh" content="3;URL=%s">
			''' % (URL(c='hop-tac'))
			div.append(XML(scr))
			return div
	except Exception, e:
		return e


def testmail():
	div = DIV()
	div.append(H3("Bạn đã đăng ký đại lý tại Bahadi.vn với các thông tin:"))
	table = TABLE(TR(TD('Họ và tên'), TD("Nguyễn Tuấn Anh"), TD("Mã giới thiệu"), TD('')), _style='width:700px; background:#eee; padding:10px;')
	table.append(TR(TD('Tên đăng nhập'), TD("......"), TD('Mật khẩu'), TD(B("..."))))
	table.append(TR(TD('Sinh ngày'), TD("../../.."), TD('Giới tính'), TD("...")))
	table.append(TR(TD('Số điện thoại'), TD("......"), TD('Email'), TD("...")))
	table.append(TR(TD('Tp/Tỉnh'), TD("......"), TD('Căn Cước/Passport'), TD("...")))
	table.append(TR(TD('Ngày cấp'), TD("......"), TD('Nơi cấp'), TD("...")))
	div.append(table)
	div.append(H4("(*) Sau khi đăng nhập bạn vui lòng đổi mật khẩu để đảm bảo an toàn cho tài khoản."))
	div.append(P("Mọi vấn đề sai sót, vướng mắc về tài khoản vui lòng liên hệ 0866 303 366 để được hỗ trợ."))
	return div


#############################################
### Page Liên hệ
##############################################

def form_lienhe():
	form = FORM(_id='form_lienhe')
	# form.append(H4('Thông tin người đặt hàng' ,_class='title_form'))

	div2 = DIV(_class="form-group col-md-12")
	div2.append(INPUT(_type='text', _class="form-control", _name='subject', _placeholder="Tiêu đề"))
	form.append(DIV(div2, _class='row'))

	div2 = DIV(_class="form-group col-md-12")
	div2.append(INPUT(_type='text', _class="form-control", _name='name', _placeholder="Người liên hệ"))
	form.append(DIV(div2, _class='row'))

	div1 = DIV(_class="form-group col-md-6")

	div1.append(INPUT(_type='text', _class="form-control", _name='phone', _placeholder="Số điện thoại"))

	div2 = DIV(_class="form-group col-md-6")
	div2.append(INPUT(_type='text', _class="form-control", _name='email', _placeholder="Email"))
	form.append(DIV(div1, div2, _class='row'))

	div1 = DIV(_class="form-group")
	# div1.append(LABEL('Lời nhắn'))
	div1.append(TEXTAREA(_class="form-control", _rows="3", _name='description', _placeholder="Lời nhắn", _style="width: 100%; "))
	form.append(div1)

	ajax = "ajax('%s', ['name','email','subject','phone','description'], 'form_lienhe')" % (URL(f='sendemail_lienhe'))
	form.append(DIV(A(I(_class='fa fa-mail-forward'), ' Gửi liên hệ ', _onclick=ajax, _class='btn btn-success btn_naso'), _class='text-center'))
	return form


def sendemail_lienhe():
	send_to = "nasojsc@gmail.com"
	you_name = request.vars.name
	you_phone = request.vars.phone
	you_email = request.vars.email
	you_subject = request.vars.subject
	des = request.vars.description

	subject = "Liên hệ web: %s" % you_subject
	content = "Khách hàng "
	div = DIV(_style="   background: #eee;    padding: 10px 20px;")
	div.append(H2(you_subject))
	div.append(P('Người liên hệ: %s' % (you_name)))
	div.append(P('Số điện thoại: %s' % (you_phone)))
	div.append(P('Email: %s' % (you_email)))
	div.append(P('Nội dung: %s' % (des)))
	mail = auth.setting_mail()
	# scr ='''<script type="text/javascript">
	# setInterval("window.parent.close()",3000);
	# </script>'''
	if mail.send(to=send_to, subject=subject, message='<html>%s</html>' % str(div)):
		div = DIV(H4('Chúng tôi đã nhận được liên hệ của bạn với nội dung như sau.'), div, H4('Chúng tôi sẽ liên hệ với bạn sớm nhất có thể. Xin cảm ơn.'))
	# div.append(XML(scr))

	else:
		div = DIV(H3(T('Gửi yêu cầu không thể thực hiện. ')), XML(scr), _class='notice')
	div.append(DIV(A(I(_class='fa fa-home'), ' Về trang chủ ', _href="#", _class='btn btn-success btn_naso'), _class='text-center'))
	return div


# thông tin đặt hàng
def product_shape():
	import requests
	from plugin_app import number_format
	# url_produc = '%s/api/v1/product/%s.json'%(api_naso,request.args(0))
	url_produc = '%s/api/product_by_id.json?id=%s' % (api_naso, request.args(0))
	r1 = requests.get(url_produc).json()
	row_s = r1['result']
	if not row_s: return 'Sản phẩm không hợp lệ'
	vars = request.vars
	div = DIV(_class='product_shape')
	# Sản phẩm không thuộc tính
	if row_s['isGroup']:
		div_warehouse, xnumber, house_name = list_warehouse(row_s['warehouse'])
		div.append(div_warehouse)
		p_prod = P(B("Giá bán: "), _class="prod_price jshop_price col-lg-12 row")
		p_prod.append(SPAN(str(number_format(row_s['price'])) + ' đ', _class='block_price'))
		div.append(p_prod)
		div_btn = DIV(_class='prod_buttons')
		div_btn.append(DIV(INPUT(_type="button", _value="-", _class="minus"), INPUT(_type="number", _step="1", _min="1", _max=xnumber, _name="quantity", _value="1", _title="Qty", _class="input-text qty text", _size="4", _pattern=""), INPUT(_type="button", _value="+", _class="plus"), _class="quantity buttons_added"))
		div_btn.append(BUTTON(SPAN(_class='card_now'), 'Mua ngay', _class="SP_HOT_List_BOX_text_button btn", _type='submit', _style="margin-top: -7px;margin-left: 10px;"))

		# Thêm vào giỏ hàng
		div_btn.append(DIV(SPAN(_class='card_now'), 'Thêm vào giỏ hàng', _class="btn_add_cart btn", _style="margin-top: -7px;margin-left: 10px;", _id='addProductToCart'))
		ajaxAddCart = "ajax('%s', ['kho_hang', 'quantity'], '_blank')" % (URL(c='plugin_app', f='add_product_to_cart', vars=dict(pid=row_s['id'])))
		div_btn.append(DIV(_style='display:none', _onclick=ajaxAddCart, _id='addProductToCartHid'))
		script = """$('#addProductToCart').click(function(){
						showModal();
						setTimeout(function () {
							$("#addProductToCartHid").trigger('click');
						}, 1500);
					});"""
		div_btn.append(XML(SCRIPT(script)))

		div.append(div_btn)
		div = DIV(FORM(div, _action=URL(a='cms', c='portal', f='add_cart_r_number', vars=dict(pid=row_s['id']))))

	# Sản phẩm có thuộc tính
	else:
		ajax_shape = "ajax('%s', [], 'wr_product_shape')" % (URL(a='cms', c='portal', f='product_shape', args=request.args, vars=dict(pid=row_s['id'])))

		url_p = '%s/api/product_shape.json?id=%s' % (api_naso, request.args(0))
		rp = requests.get(url_p).json()
		rps = row_s['list_product']
		# Danh sách thuộc tính
		list_shape = rp['list_shape']
		list_shape_value = rp['list_shape_value']
		trans = rp['trans']

		try:
			i = 0
			type_name = []
			for tt in list_shape:
				type_name.append(str(tt))
			for tt in list_shape:
				ul = UL(LI(trans.get(tt), _class='is_first'), _class='list_thuoc_tinh col-md-12 row')
				for va in list_shape_value[tt]:
					ajax = "ajax('%s', %s, 'wr_product_shape')" % (URL(c='plugin_app', f='product_shape', args=request.args), type_name)
					if str(va) == vars[tt]:
						ul.append(LI(INPUT(_value=va, _type='radio', _name=tt, _onchange=ajax, _checked=True), trans.get(va)))
					else:
						ul.append(LI(INPUT(_value=va, _type='radio', _name=tt, _onchange=ajax), trans.get(va)))
				div.append(ul)

			i = 0
		except Exception, e:
			return e
		price = check_product(rps, list_shape)

		if price:
			div_warehouse, xnumber, house_name = list_warehouse(price['warehouse'])
			div.append(div_warehouse)
			p_prod = P(B("Giá bán: "), _class="prod_price jshop_price col-lg-12 row")

			if price['price'] != "":
				p_prod.append(SPAN(str(number_format(price['price'])) + ' đ', _class='block_price'))
			else:
				p_prod.append(SPAN('Liên hệ'))
			div.append(p_prod)

			div_btn = DIV(_class='prod_buttons')

			div_btn.append(DIV(INPUT(_type="button", _value="-", _class="minus"), INPUT(_type="number", _step="1", _min="1", _max=100, _name="quantity", _value="1", _title="Qty", _class="input-text qty text", _size="4", _pattern=""), INPUT(_type="button", _value="+", _class="plus"), _class="quantity buttons_added"))
			div.append(div_btn)

			div_btn = DIV(_class='prod_buttons')
			div_btn.append(BUTTON(SPAN(_class='card_now'), 'Mua ngay', _class="SP_HOT_List_BOX_text_button btn", _type='submit', _style="margin-top: -7px;margin-left: 10px;"))

			# Thêm vào giỏ hàng
			div_btn.append(DIV(SPAN(_class='card_now'), 'Thêm vào giỏ hàng', _class="btn_add_cart btn", _style="margin-top: -7px;margin-left: 10px;", _id='addProductToCart'))
			ajaxAddCart = "ajax('%s', ['kho_hang', 'quantity'], '_blank')" % (URL(c='plugin_app', f='add_product_to_cart', vars=dict(pid=price['product_sub'])))
			div_btn.append(DIV(_style='display:none', _onclick=ajaxAddCart, _id='addProductToCartHid'))
			script = """$('#addProductToCart').click(function(){
							showModal();
							setTimeout(function () {
								$("#addProductToCartHid").trigger('click');
							}, 1500);
						});"""
			div_btn.append(XML(SCRIPT(script)))

			div.append(div_btn)

			div = DIV(FORM(div, _action=URL(a='cms', c='portal', f='add_cart_r_number', vars=dict(pid=price['product_sub']))))

		else:
			p_prod = P(B("Giá bán: "), _class="prod_price jshop_price col-lg-12 row")

			if row_s['price'] != "":
				if row_s['product_unit'] != "":
					p_prod.append(SPAN(str(number_format(row_s['price'])) + ' đ', _class='block_price'))
				else:
					p_prod.append(SPAN(str(number_format(row_s['price'])) + ' đ', _class='block_price'))
			else:
				p_prod.append(SPAN('Liên hệ'))
			if row_s['old_price'] != "":
				p_prod.append(SPAN(str(number_format(row_s['old_price'])) + ' đ', _class='old_price'))
			div.append(p_prod)

			div.append(DIV(_id='alert_thuoc_tinh', _class='row alert_thuoc_tinh'))

			div_btn = DIV(_class='prod_buttons')

			div_btn.append(DIV(INPUT(_type="button", _value="-", _class="minus"), INPUT(_type="number", _step="1", _min="1", _max="", _name="quantity", _value="1", _title="Qty", _class="input-text qty text", _size="4", _pattern=""), INPUT(_type="button", _value="+", _class="plus"), _class="quantity buttons_added"))
			div.append(div_btn)
			div_btn = DIV(_class='prod_buttons')
			div_btn.append(I('(*) Vui lòng chọn thuộc tính', _style='color: #f00;font-size: 12px;'))

			# div_btn.append(SPAN(A(SPAN(_class='card_now'), 'Mua hàng', _class="SP_HOT_List_BOX_text_button", _onclick="fillData()"), _class="btn_add"))
			div.append(div_btn)

	scr = '''
	<script>
	function wcqib_refresh_quantity_increments() {
		jQuery("div.quantity:not(.buttons_added), td.quantity:not(.buttons_added)").each(function(a, b) {
			var c = jQuery(b);
			c.addClass("buttons_added"), c.children().first().before('<input type="button" value="-" class="minus" />'), c.children().last().after('<input type="button" value="+" class="plus" />')
		})
	}

	String.prototype.getDecimals || (String.prototype.getDecimals = function() {
		var a = this,
			b = ("" + a).match(/(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
		return b ? Math.max(0, (b[1] ? b[1].length : 0) - (b[2] ? +b[2] : 0)) : 0
	}), jQuery(document).ready(function() {
		wcqib_refresh_quantity_increments()
	}), jQuery(document).on("updated_wc_div", function() {
		wcqib_refresh_quantity_increments()
	}), jQuery(document).on("click", ".plus, .minus", function() {
		var a = jQuery(this).closest(".quantity").find(".qty"),
			b = parseFloat(a.val()),
			c = parseFloat(a.attr("max")),
			d = parseFloat(a.attr("min")),
			e = a.attr("step");
		b && "" !== b && "NaN" !== b || (b = 0), "" !== c && "NaN" !== c || (c = ""), "" !== d && "NaN" !== d || (d = 0), "any" !== e && "" !== e && void 0 !== e && "NaN" !== parseFloat(e) || (e = 1), jQuery(this).is(".plus") ? c && b >= c ? a.val(c) : a.val((b + parseFloat(e)).toFixed(e.getDecimals())) : d && b <= d ? a.val(d) : b > 0 && a.val((b - parseFloat(e)).toFixed(e.getDecimals())), a.trigger("change")
	});

	  let fillData = () => {
        let ele = document.getElementById('alert_thuoc_tinh');
        ele.innerHTML = '<div class="bottom_10 col-lg-12"> Cần chọn thuộc tính trước khi đặt hàng </div>';
    }
	</script>
	'''
	div.append(XML(scr))
	return div


# Thông tin đặt hàng trên website đại lý
def order_information_salesman():
	import requests
	from plugin_app import number_format
	# url_produc = '%s/api/v1/product/%s.json'%(api_naso,request.args(0))
	url_produc = '%s/api/product_by_id.json?id=%s' % (api_naso, request.args(0))
	r1 = requests.get(url_produc).json()
	row_s = r1['result']
	if not row_s: return 'Sản phẩm không hợp lệ'
	vars = request.vars
	div = DIV(_class='product_shape')
	# Sản phẩm không thuộc tính
	if row_s['isGroup']:
		div_warehouse, xnumber, house_name = list_warehouse(row_s['warehouse'])
		div.append(div_warehouse)
		p_prod = P(B("Giá bán: "), _class="prod_price jshop_price col-lg-12 row")
		p_prod.append(SPAN(str(number_format(row_s['price'])) + ' đ', _class='block_price'))
		div.append(p_prod)
		div_btn = DIV(_class='prod_buttons')
		div_btn.append(DIV(INPUT(_type="button", _value="-", _class="minus"), INPUT(_type="number", _step="1", _min="1", _max=xnumber, _name="quantity", _value="1", _title="Qty", _class="input-text qty text", _size="4", _pattern=""), INPUT(_type="button", _value="+", _class="plus"), _class="quantity buttons_added"))
		div_btn.append(BUTTON(SPAN(_class='card_now'), 'Mua ngay', _class="SP_HOT_List_BOX_text_button btn", _type='submit', _style="margin-top: -7px;margin-left: 10px;"))

		# Thêm vào giỏ hàng
		div_btn.append(DIV(SPAN(_class='card_now'), 'Thêm vào giỏ hàng', _class="btn_add_cart btn", _style="margin-top: -7px;margin-left: 10px;", _id='addProductToCart'))
		ajaxAddCart = "ajax('%s', ['kho_hang', 'quantity'], 'testCart')" % (URL(c='plugin_app', f='add_product_to_cart', vars=dict(pid=row_s['id'])))
		div_btn.append(DIV(_style='display:none', _onclick=ajaxAddCart, _id='addProductToCartHid'))
		script = """$('#addProductToCart').click(function(){
						showModal();
						setTimeout(function () {
							$("#addProductToCartHid").trigger('click');
						}, 1500);
					});"""
		div_btn.append(XML(SCRIPT(script)))

		div.append(div_btn)
		div = DIV(FORM(div, _action=URL(a='cms', c='portal', f='add_cart_r_number', vars=dict(pid=row_s['id']))))

	# Sản phẩm có thuộc tính
	else:
		ajax_shape = "ajax('%s', [], 'wr_product_shape')" % (URL(a='cms', c='portal', f='product_shape', args=request.args, vars=dict(pid=row_s['id'])))

		url_p = '%s/api/product_shape.json?id=%s' % (api_naso, request.args(0))
		rp = requests.get(url_p).json()
		rps = row_s['list_product']
		# Danh sách thuộc tính
		list_shape = rp['list_shape']
		list_shape_value = rp['list_shape_value']
		trans = rp['trans']

		try:
			i = 0
			type_name = []
			for tt in list_shape:
				type_name.append(str(tt))
			for tt in list_shape:
				ul = UL(LI(trans.get(tt), _class='is_first'), _class='list_thuoc_tinh col-md-12 row')
				for va in list_shape_value[tt]:
					ajax = "ajax('%s', %s, 'wr_product_shape')" % (URL(c='plugin_app', f='product_shape', args=request.args), type_name)
					if str(va) == vars[tt]:
						ul.append(LI(INPUT(_value=va, _type='radio', _name=tt, _onchange=ajax, _checked=True), trans.get(va)))
					else:
						ul.append(LI(INPUT(_value=va, _type='radio', _name=tt, _onchange=ajax), trans.get(va)))
				div.append(ul)

			i = 0
		except Exception, e:
			return e
		price = check_product(rps, list_shape)

		if price:
			div_warehouse, xnumber, house_name = list_warehouse(price['warehouse'])
			div.append(div_warehouse)
			p_prod = P(B("Giá bán: "), _class="prod_price jshop_price col-lg-12 row")

			if price['price'] != "":
				p_prod.append(SPAN(str(number_format(price['price'])) + ' đ', _class='block_price'))
			else:
				p_prod.append(SPAN('Liên hệ'))
			div.append(p_prod)

			div_btn = DIV(_class='prod_buttons')

			div_btn.append(DIV(INPUT(_type="button", _value="-", _class="minus"), INPUT(_type="number", _step="1", _min="1", _max=100, _name="quantity", _value="1", _title="Qty", _class="input-text qty text", _size="4", _pattern=""), INPUT(_type="button", _value="+", _class="plus"), _class="quantity buttons_added"))
			div.append(div_btn)

			div_btn = DIV(_class='prod_buttons')
			div_btn.append(BUTTON(SPAN(_class='card_now'), 'Mua ngay', _class="SP_HOT_List_BOX_text_button btn", _type='submit', _style="margin-top: -7px;margin-left: 10px;"))

			# Thêm vào giỏ hàng
			div_btn.append(DIV(SPAN(_class='card_now'), 'Thêm vào giỏ hàng', _class="btn_add_cart btn", _style="margin-top: -7px;margin-left: 10px;", _id='addProductToCart'))
			ajaxAddCart = "ajax('%s', ['kho_hang', 'quantity'], '_blank')" % (URL(c='plugin_app', f='add_product_to_cart', vars=dict(pid=price['product_sub'])))
			div_btn.append(DIV(_style='display:none', _onclick=ajaxAddCart, _id='addProductToCartHid'))
			script = """$('#addProductToCart').click(function(){
							showModal();
							setTimeout(function () {
								$("#addProductToCartHid").trigger('click');
							}, 1500);
						});"""
			div_btn.append(XML(SCRIPT(script)))

			div.append(div_btn)

			div = DIV(FORM(div, _action=URL(a='cms', c='portal', f='add_cart_r_number', vars=dict(pid=price['product_sub']))))

		else:
			p_prod = P(B("Giá bán: "), _class="prod_price jshop_price col-lg-12 row")

			if row_s['price'] != "":
				if row_s['product_unit'] != "":
					p_prod.append(SPAN(str(number_format(row_s['price'])) + ' đ', _class='block_price'))
				else:
					p_prod.append(SPAN(str(number_format(row_s['price'])) + ' đ', _class='block_price'))
			else:
				p_prod.append(SPAN('Liên hệ'))
			if row_s['old_price'] != "":
				p_prod.append(SPAN(str(number_format(row_s['old_price'])) + ' đ', _class='old_price'))
			div.append(p_prod)

			div.append(DIV(_id='alert_thuoc_tinh', _class='row alert_thuoc_tinh'))

			div_btn = DIV(_class='prod_buttons')

			div_btn.append(DIV(INPUT(_type="button", _value="-", _class="minus"), INPUT(_type="number", _step="1", _min="1", _max="", _name="quantity", _value="1", _title="Qty", _class="input-text qty text", _size="4", _pattern=""), INPUT(_type="button", _value="+", _class="plus"), _class="quantity buttons_added"))
			div.append(div_btn)
			div_btn = DIV(_class='prod_buttons')
			div_btn.append(I('(*) Vui lòng chọn thuộc tính', _style='color: #f00;font-size: 12px;'))

			# div_btn.append(SPAN(A(SPAN(_class='card_now'), 'Mua hàng', _class="SP_HOT_List_BOX_text_button", _onclick="fillData()"), _class="btn_add"))
			div.append(div_btn)

	scr = '''
	<script>
	function wcqib_refresh_quantity_increments() {
		jQuery("div.quantity:not(.buttons_added), td.quantity:not(.buttons_added)").each(function(a, b) {
			var c = jQuery(b);
			c.addClass("buttons_added"), c.children().first().before('<input type="button" value="-" class="minus" />'), c.children().last().after('<input type="button" value="+" class="plus" />')
		})
	}

	String.prototype.getDecimals || (String.prototype.getDecimals = function() {
		var a = this,
			b = ("" + a).match(/(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
		return b ? Math.max(0, (b[1] ? b[1].length : 0) - (b[2] ? +b[2] : 0)) : 0
	}), jQuery(document).ready(function() {
		wcqib_refresh_quantity_increments()
	}), jQuery(document).on("updated_wc_div", function() {
		wcqib_refresh_quantity_increments()
	}), jQuery(document).on("click", ".plus, .minus", function() {
		var a = jQuery(this).closest(".quantity").find(".qty"),
			b = parseFloat(a.val()),
			c = parseFloat(a.attr("max")),
			d = parseFloat(a.attr("min")),
			e = a.attr("step");
		b && "" !== b && "NaN" !== b || (b = 0), "" !== c && "NaN" !== c || (c = ""), "" !== d && "NaN" !== d || (d = 0), "any" !== e && "" !== e && void 0 !== e && "NaN" !== parseFloat(e) || (e = 1), jQuery(this).is(".plus") ? c && b >= c ? a.val(c) : a.val((b + parseFloat(e)).toFixed(e.getDecimals())) : d && b <= d ? a.val(d) : b > 0 && a.val((b - parseFloat(e)).toFixed(e.getDecimals())), a.trigger("change")
	});

	  let fillData = () => {
        let ele = document.getElementById('alert_thuoc_tinh');
        ele.innerHTML = '<div class="bottom_10 col-lg-12"> Cần chọn thuộc tính trước khi đặt hàng </div>';
    }
	</script>
	'''
	div.append(XML(scr))
	return div


def add_product_to_cart():
	kho_hang = request.vars.kho_hang
	pid = request.vars.pid
	ar_carts = []

	try:
		num_carts = int(request.vars.quantity)
	except:
		num_carts = 1
	if request.cookies.has_key('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		i = 0
		for cart in carts:
			cart = eval(cart)
			if cart['id'] == pid:
				ar_carts.append(str({'id': str(cart['id']), 'num': str(int(cart['num']) + num_carts), 'kho_hang': kho_hang}))
				i += 1
			else:
				ar_carts.append(str({'id': str(cart['id']), 'num': str(cart['num']), 'kho_hang': str(cart['kho_hang'])}))
		if i == 0:
			ar_carts.append(str({'id': pid, 'num': str(num_carts), 'kho_hang': kho_hang}))
	else:
		ar_carts.append(str({'id': pid, 'num': str(num_carts), 'kho_hang': kho_hang}))
	response.cookies['cart_shop'] = str(ar_carts)
	response.cookies['cart_shop']['expires'] = 24 * 3600
	response.cookies['cart_shop']['path'] = '/'
	response.flash = T("Add new cart!")


def add_quantity_product_to_cart():
	pid = request.vars.pid
	count = request.vars.count
	ar_carts = []

	try:
		num_carts = int(request.vars['fqty' + str(count)])
	except:
		num_carts = 1
	if request.cookies.has_key('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		i = 0
		for cart in carts:
			cart = eval(cart)
			if cart['id'] == pid:
				ar_carts.append(str({'id': str(cart['id']), 'num': str(num_carts), 'kho_hang': str(cart['kho_hang'])}))
				i += 1
			else:
				ar_carts.append(str({'id': str(cart['id']), 'num': str(cart['num']), 'kho_hang': str(cart['kho_hang'])}))
	response.cookies['cart_shop'] = str(ar_carts)
	response.cookies['cart_shop']['expires'] = 24 * 3600
	response.cookies['cart_shop']['path'] = '/'
	response.flash = T("Add new cart!")


def delete_product_to_cart():
	pid = request.vars.pid
	ar_carts = []
	div = DIV()

	if request.cookies.has_key('cart_shop'):
		carts = eval(request.cookies['cart_shop'].value)
		i = 0
		for cart in carts:
			cart = eval(cart)
			if cart['id'] != pid:
				ar_carts.append(str({'id': str(cart['id']), 'num': str(cart['num']), 'kho_hang': str(cart['kho_hang'])}))

	response.cookies['cart_shop'] = str(ar_carts)
	response.cookies['cart_shop']['expires'] = 24 * 3600
	response.cookies['cart_shop']['path'] = '/'
	response.flash = T("Add new cart!")


def list_warehouse(warehouse, check=0):
	xnumber = 0
	house_name = '.'
	ul = UL(LI("Kho", _class='is_first'), _class='list_thuoc_tinh col-md-12 row')
	i = 1
	for house in warehouse:
		# ajax = "ajax('%s', %s, 'wr_product_shape')"%(URL(c='plugin_app',f='product_shape',args=request.args ),type_name)
		if check != 0:
			if (int(check) == house['id']):
				ul.append(LI(INPUT(_value=house['id'], _type='radio', _name='kho_hang', _checked=True), house['name']))
				xnumber = house['xnumber_order']
				house_name = house['name']
			else:
				ul.append(LI(INPUT(_value=house['id'], _type='radio', _name='kho_hang', _checked=False), house['name']))
		else:
			if (i == 1):
				ul.append(LI(INPUT(_value=house['id'], _type='radio', _name='kho_hang', _checked=True), house['name']))
				xnumber = house['xnumber_order']
				house_name = house['name']
			else:
				ul.append(LI(INPUT(_value=house['id'], _type='radio', _name='kho_hang', _checked=False), house['name']))
		i += 1
	div = DIV(ul, _class='list_warehouse')
	div.append(I("(*) Hiện còn %s sản phẩm trong kho %s" % (str(xnumber), house_name.encode('UTF-8')), _class='col-lg-12 row', _style="color: #f00;font-size: 12px;"))
	return div, xnumber, house_name


def check_product(rps, list_shape):
	vao = request.vars
	tt = list_shape
	ar = rps
	for a in ar:
		check = 0
		for t in tt:
			if str(a[t]) == str(vao[t]):
				check += 1
		if check == len(tt):
			return a
	return None


def list_menu(id):
	import requests
	url_folder = '%s/api/v1/folder/%s.json?field=parent&order=display_order' % (api_naso, id)
	rf = requests.get(url_folder).json()
	r_folder = rf['result']
	ul = UL()
	for f in r_folder:
		li = LI(A(f['label'], _href=URL(c='portal', f='folder', args=[f['name']])))
		li.append(list_menu(f['id']))
		ul.append(li)
	return ul


def menu_mobile():
	return list_menu(35)


def clear_cookie():
	response.cookies['cart_shop'] = 'invalid'
	response.cookies['cart_shop']['expires'] = -10
	response.cookies['cart_shop']['path'] = '/'
	return "Đã xoá"


def check_van_chuyen():
	try:
		warehouse = request.args(0)
		list_product = request.vars['list_product_%s' % warehouse]
		if request.vars['ward']:
			ToWardId = request.vars['ward']
		elif request.cookies['ward'].value:
			ToWardId = request.cookies['ward'].value
		else:
			ToWardId = ''

		if request.vars['district']:
			ToDistrictId = request.vars['district']
		elif request.cookies['district'].value:
			ToDistrictId = request.cookies['district'].value
		else:
			ToDistrictId = ''
		ToAddress = request.vars['dia_chi']

		# Tổng tiền
		temporaryPriceOrder = request.vars['temporaryPriceOrder_' + warehouse] or 0

		import requests
		url = '%s/api/find_services.json' % (api_naso)
		data = {
			"list_product": eval(list_product),
			"warehouse": warehouse,
			"ToDistrictId": ToDistrictId,
			"ToWardId": ToWardId,
			"ToAddress": ToAddress,
			"TotalAmount": temporaryPriceOrder,
			"ProductValue": temporaryPriceOrder,
		}
		x = requests.post(url, json=data)
		if x.status_code == 200:
			return check_transport_radio_web(x.text, warehouse)
		else:
			return x.text
	except Exception, e:
		return e


def check_transport_radio_web(text, warehouse):
	from plugin_app import number_format
	import json
	data = json.loads(text)
	div = DIV()
	i = 0
	divTransport = DIV()
	selectTransporter = SELECT(_name='ftransporter' + str(warehouse), _id='ftransporter' + str(warehouse), _class='form-control')
	for item in data:
		# item = json.loads(item)
		for sv in item['availableServices']:
			value = item['transporter'] + '|' + sv['serviceId'] + '|' + str(sv['serviceFee'])
			selectTransporter.append(OPTION(SPAN('₫', '{:,}'.format(int(sv['serviceFee']))) if sv['serviceFee'] else '', '-', item['fullName'], '(', sv['name'], ') ', _value=value))
			i += 1
	divTransport.append(selectTransporter)

	scr = """
	<script>
	$("#ftransporter%s").change(function() {
		gia = $(this).val();
		l_gia = gia.split('|')
		$("#van_chuyen_%s").val(parseInt(l_gia[2]).toLocaleString());
		$("#transportHidden_%s").val(gia);
		handlingTotal(%s);
		handlingTotalAmountAll();
	  }).trigger( "change" );
	</script>
	""" % (warehouse, warehouse, warehouse, warehouse)
	divTransport.append(XML(scr))
	return divTransport
