
def read():
	link = request.args(2)
	from plugin_process import Process
	process = Process()
	db = process.cms.db
	process.cms.define_dcontent()
	dcontent = db(db.dcontent.link==link).select().first()
	tablename = request.args(1)
	table = process.cms.define_table(dcontent.dtable)
	
	row = table[dcontent.table_id]
	
	
	div =DIV(_class='read_de_tai panel-body')
	table = TABLE(_class='table-bordered')
	if row.budget:
		table.append(TR(TH(1,_class='th_number'),TD(B('Tên nhiệm vụ:'), row.name)))
		
		projectlevel = process.cms.define_table("projectlevel")
		row_level = db(projectlevel.id>0).select(orderby=~db.projectlevel.display_order)
		tr= TR(TD(B('Cấp quản lý nhiệm vụ: ')),_class='td_5')
		for row_l in row_level:
			if row.projectlevel==row_l.id:
				tr.append(TD(INPUT(_type='checkbox',_checked=True,_disabled=True),row_l.name))
			else:
				tr.append(TD(INPUT(_type='checkbox',_disabled=True),row_l.name))
		# table_cap =TABLE(TR(TD(B('Cấp quản lý nhiệm vụ: ')),TD(INPUT(_type='checkbox',_checked=True if row.projectlevel=='Quốc gia' else ''),'Quốc gia'),TD(INPUT(_type='checkbox'),'Bộ'),TD(INPUT(_type='checkbox'),'Tỉnh'),TD(INPUT(_type='checkbox'),'Cơ sở')),_class='td_5')
		table.append(TR(TH(2,_class='th_number'),TD(TABLE(tr))))
		
		table_bao_mat =TABLE(TR(TD(B('Mức độ bảo mật: ')),TD(INPUT(_type='checkbox',_checked=True,_disabled=True),'Bình thường'),TD(INPUT(_type='checkbox',_disabled=True),'Mật'),TD(INPUT(_type='checkbox',_disabled=True),'Tối mật'),TD(INPUT(_type='checkbox',_disabled=True),'Tuyệt mật')),_class='td_5')
		table.append(TR(TH(3,_class='th_number'),TD(table_bao_mat)))
		
		table.append(TR(TH(4,_class='th_number'),TD(B('Mã số nhiệm vụ (nếu có): '), row.code)))
		
		org = process.cms.define_table("org")
		row_org = db(org.id==row.org_master).select().first()
		table1 = TABLE()
		if row_org:
			table1.append(P(B('Tên tổ chức chủ trì đề tài: '),row_org.name))
			table1.append(P(SPAN('Điện thoại: '),row_org.phone or ''))
			table1.append(P(SPAN('Email: '),row_org.email or ''))
			table1.append(P(SPAN('Địa chỉ: '),row_org.adress or ''))
		table.append(TR(TH(5,_class='th_number'),TD(table1)))
		
		org = process.cms.define_table("org")
		row_org = db(org.id==row.org_manager).select().first()
		table.append(TR(TH(6,_class='th_number'),TD(B('Cơ quan chủ quản: '), row_org.name)))
		
		# Phan chu de tai
		person = process.cms.define_table("person")
		post = process.cms.define_table("post")
		row_person = db((person.project==row.id)&(person.post == post.id)&(post.name.contains('Chủ nhiệm') )).select(db.person.ALL).first()
		table1 = TABLE()
		if row_person:
			table1.append(TR(TD(P(B('Chủ nhiệm nhiệm vụ'))),TD()))
			table1.append(TR(TD(P(SPAN('Họ và tên: '),row_person.name if row_person else '...')),TD( P(SPAN('Giới tính: '),row_person.sex if row_person else '...' ))))
			table1.append(TR(TD(P(SPAN('Trình độ học vấn: '),row_person.education.name if row_person.education !=None else '...' )),TD( P(SPAN('Chức vụ: '),row_person.postoffice.name  if row_person.postoffice !=None else '...'))))
			table1.append(TR(TD(P(SPAN('Điện thoại: '),row_person.phone  if row_person.phone !=None else '...')),TD(P(SPAN('Fax: '), row_person.fax if row_person.fax !=None else '...'))))
			table1.append(TR(TD(P(SPAN('Email: '),row_person.email  if row_person.email != None else '...')),TD()))
		else:
			table1.append(TR(TD(P(B('Chủ nhiệm nhiệm vụ'))),TD()))
			table1.append(TR(TD(P(SPAN('Họ và tên: '),'...')),TD( P(SPAN('Giới tính: '), '...' ))))
			table1.append(TR(TD(P(SPAN('Trình độ học vấn: '), '...' )),TD( P(SPAN('Chức vụ: '),'...'))))
			table1.append(TR(TD(P(SPAN('Điện thoại: '),'...')),TD(P(SPAN('Fax: '), '...'))))
			table1.append(TR(TD(P(SPAN('Email: '), '...')),TD()))
		table.append(TR(TH(7,_class='th_number'),TD(table1)))
		# End:Phan chu de tai
		
		
		
		#Can bo thuc hien
		row_person = db((person.project==row.id)).select()
		tb_can_bo = TABLE(TR(TH('Stt'),TH('Họ và tên,học hàm học vị'),TH('Tổ chức công tác'),TH('Nội dung, công việc chính tham gia'),TH('Thời gian làm việc cho đề tài')),_class='table can_bo')
		i = 1
		for r in row_person:
			tb_can_bo.append(TR(TD(i,_class='title_person'),TD(r.name),TD(r.org.name if r.org else ''),TD(),TD()))
			i+=1
		table.append(TR(TH(8,_class='th_number'),TD(P(B('Danh sách cá nhân tham gia nhiệm vụ (ghi họ tên, chức danh khoa học và học vị): ')),tb_can_bo)))
		#End: Can bo thuc hien
		
		table.append(TR(TH(9,_class='th_number'),TD(P(B('Mục tiêu nghiên cứu: ')),XML(row.research_object or ""))))
		table.append(TR(TH(10,_class='th_number'),TD(P(B('Tóm tắt nội dung nghiên cứu chính: ')),XML(row.research_content or ""))))
		table.append(TR(TH(11,_class='th_number'),TD((B('Lĩnh vực nghiên cứu: '),row.folder.label or ''))))
		table.append(TR(TH(12,_class='th_number'),TD(P(B('Mục tiêu kinh tế xã hội của nhiệm vụ: ')),XML("..."))))
		table.append(TR(TH(13,_class='th_number'),TD(P(B('Phương pháp nghiên cứu: ')),XML("..."))))
		table.append(TR(TH(14,_class='th_number'),TD(P(B('Sản phẩm khoa học và công nghệ dự kiến: ')),XML("..."))))
		table.append(TR(TH(15,_class='th_number'),TD(P(B('Địa chỉ và quy mô ứng dụng dự kiến: ')),XML("..."))))
			
		table.append(TR(TH(16,_class='th_number'),TD((B('Thời gian thực hiện: '),str(row.nbmonth)+' tháng' if row.nbmonth != None else '...'))))
			
			
		count = 0
		table_b = TABLE(_class='table')
		for field in [  "budget","budget_self", "budget_diff"]:
			count += (row[field] or 0)
			table_b.append(TR(TD(T(field)),TD(str("{:,d}".format(row[field])) if row[field] else '')))
		count = "{:,d}".format(count).replace(",",".")
		table.append(TR(TH(17,_class='th_number'),TD(P(B('Kinh phí được phê duyệt: '),count,' đồng'),table_b)))
		
		table.append(TR(TH(18,_class='th_number'),TD((B('Quyết định phê duyệt: số……………… ngày... tháng… năm... ')))))
		table.append(TR(TH(19,_class='th_number'),TD((B('Hợp đồng thực hiện: số……………… ngày... tháng… năm...  ')))))
	else:
		table.append(TR(TH(1,_class='th_number'),TD(B('Tên nhiệm vụ:'), row.name)))
		org = process.cms.define_table("org")
		row_org = db(org.id==row.org_master).select().first()
		table1 = TABLE()
		if row_org:
			table1.append(P(B('Tên tổ chức chủ trì đề tài: '),row_org.name))
			table1.append(P(SPAN('Điện thoại: '),row_org.phone or ''))
			table1.append(P(SPAN('Email: '),row_org.email or ''))
			table1.append(P(SPAN('Địa chỉ: '),row_org.adress or ''))
		table.append(TR(TH(2,_class='th_number'),TD(table1)))
		
		org = process.cms.define_table("org")
		row_org = db(org.id==row.org_manager).select().first()
		table.append(TR(TH(3,_class='th_number'),TD(B('Cơ quan chủ quản: '), row_org.name)))
		
		# Phan chu de tai
		person = process.cms.define_table("person")
		post = process.cms.define_table("post")
		row_person = db((person.project==row.id)&(person.post == post.id)&(post.name.contains('Chủ nhiệm') )).select(db.person.ALL).first()
		table1 = TABLE()
		if row_person:
			table1.append(TR(TD(P(B('Chủ nhiệm nhiệm vụ'))),TD()))
			table1.append(TR(TD(P(SPAN('Họ và tên: '),row_person.name if row_person else '...')),TD( P(SPAN('Giới tính: '),row_person.sex if row_person else '...' ))))
			table1.append(TR(TD(P(SPAN('Trình độ học vấn: '),row_person.education.name if row_person.education !=None else '...' )),TD( P(SPAN('Chức vụ: '),row_person.postoffice.name  if row_person.postoffice !=None else '...'))))
			table1.append(TR(TD(P(SPAN('Điện thoại: '),row_person.phone  if row_person.phone !=None else '...')),TD(P(SPAN('Fax: '), row_person.fax if row_person.fax !=None else '...'))))
			table1.append(TR(TD(P(SPAN('Email: '),row_person.email  if row_person.email != None else '...')),TD()))
		else:
			table1.append(TR(TD(P(B('Chủ nhiệm nhiệm vụ'))),TD()))
			table1.append(TR(TD(P(SPAN('Họ và tên: '),'...')),TD( P(SPAN('Giới tính: '), '...' ))))
			table1.append(TR(TD(P(SPAN('Trình độ học vấn: '), '...' )),TD( P(SPAN('Chức vụ: '),'...'))))
			table1.append(TR(TD(P(SPAN('Điện thoại: '),'...')),TD(P(SPAN('Fax: '), '...'))))
			table1.append(TR(TD(P(SPAN('Email: '), '...')),TD()))
		table.append(TR(TH(4,_class='th_number'),TD(table1)))
		# End:Phan chu de tai
		
		
		
		#Can bo thuc hien
		row_person = db((person.project==row.id)).select()
		tb_can_bo = TABLE(TR(TH('Stt'),TH('Họ và tên,học hàm học vị'),TH('Tổ chức công tác'),TH('Nội dung, công việc chính tham gia'),TH('Thời gian làm việc cho đề tài')),_class='table can_bo')
		i = 1
		for r in row_person:
			tb_can_bo.append(TR(TD(i,_class='title_person'),TD(r.name),TD(r.org.name if r.org else ''),TD(),TD()))
			i+=1
		table.append(TR(TH(5,_class='th_number'),TD(P(B('Danh sách cá nhân tham gia nhiệm vụ (ghi họ tên, chức danh khoa học và học vị): ')),tb_can_bo)))
		#End: Can bo thuc hien
		
		table.append(TR(TH(6,_class='th_number'),TD(P(B('Mục tiêu nghiên cứu: ')),XML(row.research_object or ""))))
		table.append(TR(TH(7,_class='th_number'),TD(P(B('Tóm tắt nội dung nghiên cứu chính: ')),XML(row.research_content or ""))))
		table.append(TR(TH(8,_class='th_number'),TD((B('Lĩnh vực nghiên cứu: '),row.folder.label or ''))))
		table.append(TR(TH(9,_class='th_number'),TD(P(B('Mục tiêu kinh tế xã hội của nhiệm vụ: ')),XML("..."))))
		table.append(TR(TH(10,_class='th_number'),TD(P(B('Phương pháp nghiên cứu: ')),XML("..."))))
		table.append(TR(TH(11,_class='th_number'),TD(P(B('Sản phẩm khoa học và công nghệ dự kiến: ')),XML("..."))))
		table.append(TR(TH(12,_class='th_number'),TD(P(B('Địa chỉ và quy mô ứng dụng dự kiến: ')),XML("..."))))
			
		table.append(TR(TH(13,_class='th_number'),TD((B('Thời gian thực hiện: '),str(row.nbmonth)+' tháng' or ''))))
			
			
		count = 0
		table_b = TABLE(_class='table')
		for field in [  "budget","budget_self", "budget_diff"]:
			count += (row[field] or 0)
			table_b.append(TR(TD(T(field)),TD(str("{:,d}".format(row[field])) if row[field] else '')))
		count = "{:,d}".format(count)
		table.append(TR(TH(14,_class='th_number'),TD(P(B('Kinh phí được phê duyệt: '),count,' VNĐ'),table_b)))
		
	div.append(table)
	return div
	
	
def box_diem_bao():
	from plugin_public import Crawler
	plugin_public=Crawler()
	return plugin_public.crawler_rss('http://www.baohatinh.vn/news/rss/xa-hoi',10)
	
def edit():
	from plugin_app import Dropdown
	from plugin_ckeditor import CKEditor
	from plugin_process import Process
	
	process = Process()
	db = process.cms.db
	process.cms.define_dtable()
	tablename = process.tablename
	table_id = process.get_table_id()
	dtable = db(db.dtable.name==tablename).select().first()
	if not dtable: return dict(content='Table %s not existe'%tablename)		
	table = process.cms.define_table(tablename)
	if not table: return dict(content='Can not define %s'%tablename)		
	
	
	for field in table.fields:
		if table[field].type[:9]=='reference':
			ref = table[field].type[10:]
			if auth.has_permission('create',ref,0,auth.user_id):  
				table[field].comment=Dropdown(table[field], T('Add new'))
		else:
			row = db(db.dfield.name==field).select().first()
			if row:
				if row.ckeditor: table[field].widget=CKEditor(db).widget		
		if field == 'folder':
			table[field].widget = process.widget_folder
			table[field].label=T("Danh mục")

		
		
		
	form=SQLFORM(table,table_id,buttons=[],showid=False)
	
	if dtable.attachment:
		if not table_id: 
			if not request.vars.uuid:
				import uuid
				redirect(URL(args=request.args,vars=dict(uuid=uuid.uuid1().int)))

		from plugin_upload import FileUpload
		fileupload = FileUpload(db=db,tablename=tablename,table_id=table_id or request.vars.uuid,upload_id=None)
		if tablename =='hinh_anh':
			upload = fileupload.formupload1(colorbox=False)
		if (tablename=='videos') or (tablename=='audio'):
			upload = fileupload.formupload_media(colorbox=False)
		else:
			upload = fileupload.formupload(colorbox=False)
	else: 
		upload = ''

	form[0][-1].append(TR(TD(),TD(INPUT(_type='submit',_value=T('Submit'),_style="display: none;",_id='act_submit'))))
	
	if form.process().accepted:
		if form.vars.htmlcontent: 
			new_content=''
			row = table(form.vars.id)
			new_content = change_img(form.vars.htmlcontent)
			row.update_record(htmlcontent=new_content)
			if not form.vars.avatar:
				update_imageURL_in_content(table,form.vars.id)
			else:
				size_img(row,tablename)
					
		if dtable.attachment:
			if request.vars.uuid:
				fileupload.update(form.vars.id,request.vars.uuid)
		if not table_id: process.create_objects(form.vars.folder,tablename,form.vars.id)
		else: 
			process.update_folder(form.vars.folder,tablename,table_id)
			if dtable.publish:
				from plugin_cms import CmsPublish
				cms = CmsPublish(db=db)
				cms.update(tablename,table_id)
		args = request.args[:4]
		args[2] = db.folder(form.vars.folder).name
		redirect(URL(c='plugin_process',f='explorer',args=args))
		
	if table_id:
		msg = T("Update table")+ dtable.label
	else:
		msg = T("Create table")+ dtable.label
		
	div = DIV(H3(msg,_class='title_edit'),form,_class='edit',_id='edit_%s'%(tablename))
	div.append(upload)
	div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_onclick='javascript:history.go(-1)',_class='btn btn-primary')))
	script = SCRIPT('''$("#act_submit_ao").click(function () {$("#act_submit").trigger('click');});''')
	div.append(script)
	
	response.view = 'plugin_process/edit.html'	
	return dict(content=div)
	
def size_img(row,tablename):
	value = row.avatar
	if not value[0:5]=='http:': url = request.folder + '/static/uploads/%s/%s'%(tablename,value) 
	import os, uuid
	from PIL import Image
	size=(600,400)
	if os.path.exists(url):
		im=Image.open(url)
		im.thumbnail(size,Image.ANTIALIAS)
		im.save(url,'jpeg')
	return ''
	
def add_new_dvc():
	from plugin_app import Dropdown
	from plugin_ckeditor import CKEditor
	from plugin_process import Process
	
	process = Process()
	db = process.cms.db
	process.cms.define_dtable()
	tablename = process.tablename
	table_id = process.get_table_id()
	dtable = db(db.dtable.name==tablename).select().first()
	if not dtable: return dict(content='Table %s not existe'%tablename)		
	table = process.cms.define_table(tablename)
	if not table: return dict(content='Can not define %s'%tablename)		
	
	
	for field in table.fields:
		if table[field].type[:9]=='reference':
			ref = table[field].type[10:]
			if auth.has_permission('create',ref,0,auth.user_id):  
				table[field].comment=Dropdown(table[field], T('Add new'))
		else:
			row = db(db.dfield.name==field).select().first()
			if row:
				if row.ckeditor: table[field].widget=CKEditor(db).widget		
		if field == 'folder':
			table[field].widget = process.widget_folder
			table[field].label=T("Danh mục")
			
		if field == 'name':
			table[field].label=T("Tên dịch vụ công")
		elif field=='url_run':
			from plugin_app import widget_url
			table[field].widget = widget_url
			
		if field=='publich_on':
			table[field].default= request.now
			table[field].writable= False
			table[field].readable= False
		
		
		
	form=SQLFORM(table,table_id,buttons=[],showid=False)
	
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
		if form.vars.htmlcontent: 
			new_content=''
			row = table(form.vars.id)
			new_content = change_img(form.vars.htmlcontent)
			row.update_record(htmlcontent=new_content)
			if form.vars.avatar:
				print 'co'
			else:
				link =''
				content = new_content.replace(' ', '')
				n1 = content.find('<img')
				if n1>-1: 
					n1 = content.find('src=', n1)
					if n1>-1: 
						n1 = content.find('"', n1)
						if n1>-1:
							n1+=1
							n2 = content.find('"', n1)
							link = content[n1:n2]
						else:
							n1 = content.find("'", n1)
							if n1>-1:
								n1+=1
								n2 = content.find("'", n1)
								link = content[n1:n2]	
				row.update_record(avatar=link)
		if dtable.attachment:
			if request.vars.uuid:
				fileupload.update(form.vars.id,request.vars.uuid)
		if not table_id: process.create_objects(form.vars.folder,tablename,form.vars.id)
		else: 
			process.update_folder(form.vars.folder,tablename,table_id)
			if dtable.publish:
				from plugin_cms import CmsPublish
				cms = CmsPublish(db=db)
				cms.update(tablename,table_id)
		args = request.args[:4]
		args[2] = db.folder(form.vars.folder).name
		redirect(URL(c='plugin_process',f='explorer',args=args))
		
	if table_id:
		msg = T("Update table")+ dtable.label
	else:
		msg = T("Create table")+ dtable.label
		
	div = DIV(H3(msg,_class='title_edit'),form,_class='edit',_id='edit_%s'%(tablename))
	div.append(upload)
	div.append(DIV(INPUT(_type='submit',_value=T('Submit'),_class='btn btn-primary',_id='act_submit_ao'),INPUT(_type='button',_value=T('Cancel'),_onclick='javascript:history.go(-1)',_class='btn btn-primary')))
	script = SCRIPT('''$("#act_submit_ao").click(function () {$("#act_submit").trigger('click');});''')
	div.append(script)
	
	response.view = 'plugin_process/edit.html'	
	return dict(content=div)

def update_imageURL_in_content(table,id):	
	if request.vars.htmlcontent:
		row= table(id)
		new_content= row.htmlcontent
		link =''
		content = new_content.replace(' ', '')
		
		n1 = content.find('<img')
		if n1>-1: 
			n1 = content.find('src=', n1)
			if n1>-1: 
				n1 = content.find('"', n1)
				if n1>-1:
					n1+=1
					n2 = content.find('"', n1)
					link = content[n1:n2]
				else:
					n1 = content.find("'", n1)
					if n1>-1:
						n1+=1
						n2 = content.find("'", n1)
						link = content[n1:n2]	
		if (link <>'') & (link[0:7] <> 'http://'):
			ns = link.split('/')
			link = ns[len(ns)-1]
		row.update_record(avatar=link)
	return 		
	
def save_img(url,filename=None,dir='static/uploads/images_download'):
	import urllib
	import os
	path = '%s/%s'%(request.folder,dir)
	if not os.path.exists(path): os.makedirs(path)
	filename = filename or url.split('/')[-1]
	while os.path.exists('%s/%s/%s'%(request.folder,dir,filename)): 
		filename = '1_%s'%filename
	urllib.urlretrieve(url, '%s/%s'%(path,filename))
	return "/%s/%s/%s"%(request.application,dir,filename)

def change_img(html):
	from bs4 import BeautifulSoup
	soup = BeautifulSoup(html)
	imgs = []
	dir = 'static/uploads/images_download'
	for link in soup.find_all('img'):
		url = link.get('src')
		
		try:
			path = save_img(url,dir=dir)
			link['src']=path
		except Exception, e:
			print e
			pass
	#for img in imgs: html = html.replace(img[0],img[1])		
	return soup.prettify().replace('<html>','').replace('</html>','')

def sendmail_hainguong_datban():
	you_name  = request.vars.name
	you_phone = request.vars.phone
	number_table = request.vars.number_table
	datetime = request.vars.datetime
	gop_y = request.vars.gop_y
	send_to = "hainguong.hn@gmail.com"
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu đặt bàn'
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>)'  +"<br/>Đã đặt bàn với Số người: " + number_table +' vào thời gian '+ datetime
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H4(T('Đặt bàn thành công. Chúng tôi sẽ liên lạc với quý vị trong thời gian sớm nhất. Xin chân thành cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H4(T('Yêu cầu có lỗi, vui lòng liên hệ  Hotline: 088 876 97 00 . Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	
def sendmail_hachi_datban():
	you_name  = request.vars.name
	you_phone = request.vars.phone
	number_table = request.vars.number_table
	datetime = request.vars.datetime
	gop_y = request.vars.gop_y
	send_to = "hachijuhachivn@gmail.com"
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu đặt bàn'
	content   = "Email thông báo của hệ thống website. Vui lòng không trả lời tại đây.<br/> Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>)'  +"<br/>Đã đặt bàn với Số người: " + number_table +' vào thời gian '+ datetime
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H4(T('Đặt bàn thành công. Chúng tôi sẽ liên lạc với quý vị trong thời gian sớm nhất. Xin chân thành cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H4(T('Yêu cầu có lỗi, vui lòng liên hệ  Hotline: 02463 263 529  . Xin cảm ơn ')),XML(scr),_class='notice')
	return div
		
def sendmail_happyschool_dang_ky_hoc():
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_email = request.vars.email
	send_to = "hainguyen.happyschool@gmail.com"
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu tư vấn'
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>)'  +"<br/> Email: " + you_email +" đã yêu cầu được tư vấn"
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H4(T('Yêu cầu thành công. Chúng tôi sẽ liên lạc với quý vị trong thời gian sớm nhất. Xin chân thành cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H4(T('Yêu cầu có lỗi, vui lòng liên hệ số điện thoại  02383 99 22 99. Xin cảm ơn ')),XML(scr),_class='notice')
	return div


		
def sendmail_happykids_dang_ky():
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_email = request.vars.email
	you_content = request.vars.gop_y
	send_to = "quynhnhudang2295@gmail.com"
	
	subject   = "Phụ huynh " + you_name +" số điện thoại (" + you_phone +') đã đăng ký học'
	content   = "Phụ huynh " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>)'  +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address +' đã đăng ký học:' + you_content
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H4(T('Đăng ký thành công. Chúng tôi sẽ liên lạc với quý vị trong thời gian sớm nhất. Xin chân thành cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H4(T('Đăng ký học có lỗi, vui lòng liên hệ số điện thoại 02383 866 886. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
		
def sendmail_happykids_lien_he():
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_email = request.vars.email
	you_content = request.vars.gop_y
	send_to = "quynhnhudang2295@gmail.com"
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã góp ý'
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>)'  +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address +' đã góp ý như sau:' + you_content
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Đã gửi Liên hệ thành công. Chúng tôi sẽ liên lạc với quý vị trong thời gian sớm nhất. Xin chân thành cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 02383 866 886. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
		
def sendmail_otohondavinh():
	#otohondavinh.net
	title=request.args(0)
	if title =="dang-ky-lai-thu":
		title=" đăng ký lái thử"
	elif title =="yeu-cau-bao-gia":
		title=" yêu cầu báo giá"
	elif title =="uoc-tinh-tra-gop":
		title=" ước tính trả góp"
	else:
		title=request.args(0)
	send_to = "duonghondavinh@gmail.com"
	
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_email = request.vars.email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu ' + title
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu ' + title +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0949 068 282 . Xin cảm ơn ')),XML(scr),_class='notice')
	return div	
	
	
def sendmail_xuanan():
	#ladingpage xuan an
	
	send_to = ["anhnt8688@gmail.com","khudothixuanan@gmail.com"]
	you_name  = request.vars.tendaydu
	you_phone = request.vars.dienthoai
	you_noidung = request.vars.noidung or "."
	you_email = request.vars.email or "."
	
	subject   = "Xuanangreenpark.vn :Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu báo giá' 
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu tư vấn' +"<br/> Email: " + you_email +"<br/> Lời nhắn: " + you_noidung
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại  0981.37.82.37 . Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	
def sendmail_hondavinh():
	title=request.args(0)
	if title =="dang-ky-lai-thu":
		title=" đăng ký lái thử"
	elif title =="yeu-cau-bao-gia":
		title=" yêu cầu báo giá"
	elif title =="uoc-tinh-tra-gop":
		title=" ước tính trả góp"
	else:
		title=request.args(0)
	send_to = "dungntl.fpt@gmail.com"
	
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_email = request.vars.email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu ' + title
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu ' + title +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0911472233. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	
		
def sendmail_dailyhondavinh():
	title=request.args(0)
	if title =="dang-ky-lai-thu":
		title=" đăng ký lái thử"
	elif title =="yeu-cau-bao-gia":
		title=" yêu cầu báo giá"
	elif title =="uoc-tinh-tra-gop":
		title=" ước tính trả góp"
	else:
		title=request.args(0)
	send_to = "quangphuc.hondavinh@gmail.com"
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_email = request.vars.email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu ' + title
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu ' + title +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0916 740 990. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	

		
def sendmail_giaxehondavinh():
	title=request.args(0)
	if title =="dang-ky-lai-thu":
		title=" đăng ký lái thử"
	elif title =="yeu-cau-bao-gia":
		title=" yêu cầu báo giá"
	elif title =="uoc-tinh-tra-gop":
		title=" ước tính trả góp"
	else:
		title=request.args(0)
	send_to = "giaxehondavinh@gmail.com"
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_email = request.vars.email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu ' + title
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu ' + title +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 097 833 2204. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	
		
def sendmail_hondanghean():
	title=request.args(0)
	if title =="dang-ky-lai-thu":
		title=" đăng ký lái thử"
	elif title =="yeu-cau-bao-gia":
		title=" yêu cầu báo giá"
	elif title =="uoc-tinh-tra-gop":
		title=" ước tính trả góp"
	elif title =="trang-chu":
		title=" tư vấn"
	else:
		title=request.args(0)
	send_to = "khanhlamdhv@gmail.com"
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_email = request.vars.email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu ' + title
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu ' + title +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0944 697 117. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
			
def sendmail_huyndaivinh():
	title=request.args(0)
	if title =="dang-ky-lai-thu":
		title=" đăng ký lái thử"
	elif title =="yeu-cau-bao-gia":
		title=" yêu cầu báo giá"
	elif title =="uoc-tinh-tra-gop":
		title=" ước tính trả góp"
	elif title =="trang-chu":
		title=" tư vấn"
	else:
		title=request.args(0)
	send_to = "ngothihien0303@gmail.com"
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_email = request.vars.email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu ' + title
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu ' + title +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0915452666. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	
		
def sendmail_fordvinh():
	title=request.args(0)
	if title =="dang-ky-lai-thu":
		title=" đăng ký lái thử"
	elif title =="yeu-cau-bao-gia":
		title=" yêu cầu báo giá"
	elif title =="uoc-tinh-tra-gop":
		title=" ước tính trả góp"
	else:
		title=request.args(0)
	# send_to = "giaxehondavinh@gmail.com"
	send_to = "lhngoc@vinhford.com.vn"
	you_name  = request.vars.ford_name
	you_phone = request.vars.ford_phone
	you_address = request.vars.ford_address
	you_email = request.vars.ford_email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu ' + title
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu ' + title +"<br/> Email: " + you_email +"<br/> Địa chỉ: " + you_address
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H2(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn')),XML(scr),_class='notice')
	else: 
		div = DIV(H2(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0916153777 hoặc 0964943222. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	


		
def sendmail_medichatinh():
	send_to = "anhnt8688@gmail.com"
	you_name  = request.vars.hoten
	you_phone = request.vars.dienthoai
	you_address = request.vars.address
	you_email = request.vars.email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã đặt lịch hẹn khám' 
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu đặt lịch hẹn khám' +"<br/> Email: " + you_email 
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H3(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),H2("Tư vấn nhanh: 01656 656 777",_style='text-align: center; color: #d50c0c;'),XML(scr),_class='notice')
	else: 
		div = DIV(H3(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 01656 656 777. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
		
def sendmail_xuanvinh():
	send_to = "vinhnguyenxuan1212@gmail.com"
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_gop_y = request.vars.gop_y
	
	subject   = "Khách hàng " + you_name +') đã đặt hàng tại rangmiengxuanvinh.com' 
	content   = "<b style='color:#F00;'>Đây Email thông báo của hệ thống website. Vui lòng không trả lời lại thư này .</b><br/><br/> Khách hàng "  + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã đặt hàng tại RangmiengXuanVinh.com' +"<br/> Nội dung yêu cầu: " + you_gop_y  +"<br/> Địa chỉ: " + you_address 
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H3(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),H2("Tư vấn nhanh:   0983.907.138 ",_style='text-align: center; color: #d50c0c;'),XML(scr),_class='notice')
	else: 
		div = DIV(H3(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại   0983.907.138 Xin cảm ơn ')),XML(scr),_class='notice')
	return div	
		
def sendmail_onghutviet():
	send_to = "onghutviet@gmail.com"
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_address = request.vars.address
	you_gop_y = request.vars.gop_y
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã đặt hàng Ống Hút Tre' 
	content   = "Email thông báo của hệ thống website. Vui lòng không trả lời tại đây.<br/> Khách hàng "  + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã đặt hàng Ống Hút Tre' +"<br/> Nội dung yêu cầu: " + you_gop_y 
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H3(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),H2("Tư vấn nhanh: 0989.666.944",_style='text-align: center; color: #d50c0c;'),XML(scr),_class='notice')
	else: 
		div = DIV(H3(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0989.666.944. Xin cảm ơn ')),XML(scr),_class='notice')
	return div	
	
def sendmail_ngheanbatdongsan():
	send_to = "thuhiennguyen268@gmail.com"
	you_name  = request.vars.hoten
	you_phone = request.vars.dienthoai
	you_address = request.vars.address
	you_email = request.vars.email
	
	subject   = "Khách hàng " + you_name +" số điện thoại (" + you_phone +') đã yêu cầu tư vấn' 
	content   = "Khách hàng " + you_name +" số điện thoại (<a href='tel:" + you_phone + "'> <B>"+ you_phone +'</B></a>) đã yêu cầu tư vấn' +"<br/> Email: " + you_email 
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H3(T('Gửi yêu cầu thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),H2("Tư vấn nhanh: 0941 35 81 86",_style='text-align: center; color: #d50c0c;'),XML(scr),_class='notice')
	else: 
		div = DIV(H3(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0941 35 81 86. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
		
def sendmail_tuanlinhhotel():
	send_to = "tuanlinhhotels@gmail.com"
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_email = request.vars.email
	
	start_time = request.vars.start_time
	end_time = request.vars.end_time

	number_phong = request.vars.number_phong
	number_lon = request.vars.number_lon
	number_be = request.vars.number_be
	
	subject   = "Khách hàng "
	content   = "Khách hàng "
	if you_name:	
		subject += 	you_name
		content += 	you_name
	if you_phone:	
		subject += 	" số điện thoại (" + you_phone +') đã gửi thông tin đặt phòng '
		content += 	" số điện thoại (<a href='tel:"+you_phone +"'>" + you_phone +'</a>) đã gửi thông tin đặt phòng '
	
		
	if you_email:	
		content += 	"<br/> Email : "+ you_email	
	if start_time:	
		content += 	"<br/> Ngày nhận: "+ start_time	
		
	if start_time:	
		content += 	"<br/> Ngày nhận: "+ start_time
	if end_time:	
		content += 	"<br/> Ngày trả: "+ end_time	
	if number_phong:	
		content += 	"<br/> Số phòng: "+ number_lon
	if number_lon:	
		content += 	"<br/> Số người lớn: "+ number_lon
	if number_be:	
		content += 	"<br/> Số người lớn: "+ number_be
		
	mail = auth.setting_mail()
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		div = DIV(H3(T('Đặt phòng thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),XML(scr),_class='notice')
	else: 
		div = DIV(H3(T('Gửi yêu cầu có lỗi. ')),XML(scr),_class='notice')
	return div	
	
	
def sendmail_hongminh():

	from plugin_process import Process
	
	process = Process()
	db = process.cms.db
	dat_xe = process.cms.define_table('dat_xe')
	if not dat_xe: return 'Can not define dat_xe'
	from datetime import datetime
	
	you_name  = request.vars.name
	you_phone = request.vars.phone
	you_email = request.vars.email
	startday=None
	endday=None
	if request.vars.start_time:
		startday = datetime.strptime(request.vars.start_time ,'%d/%m/%Y %H:%M:%S').strftime("%Y-%m-%d %H:%M:%S")
	else:
		div = DIV(H3(T('Định dạng ngày lỗi. ')),_class='notice')
	if request.vars.end_time:
		endday = datetime.strptime(request.vars.end_time ,'%d/%m/%Y %H:%M:%S').strftime("%Y-%m-%d %H:%M:%S")
	des = request.vars.des
	id = db.dat_xe.insert(name=you_name,description=des,startday=startday,endday=endday,dien_thoai=you_phone,email=you_email,is_update=False,created_on=request.now)

	if id:
		div = DIV(H3(T('Đặt xe thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),_class='notice')
	else: 
		div = DIV(H3(T('Gửi yêu cầu có lỗi. ')),_class='notice')
	return div
	

@service.jsonrpc
@service.jsonrpc2
def list_dat_xe():
	try:
		from plugin_process import Process

		process = Process()
		db = process.cms.db
		dat_xe = process.cms.define_table('dat_xe')
		if not dat_xe: return []
		list = []
		rows = db(dat_xe.is_update==False).select()
		# rows = db(dat_xe.id>0).select()
		for row in rows:
			list.append(row.id)

		return list
	except Exception,e: return e
	
@service.jsonrpc
@service.jsonrpc2	
def dat_xe(id):
	from plugin_process import Process

	process = Process()
	db = process.cms.db
	dat_xe = process.cms.define_table('dat_xe')
	if not dat_xe: return []
	list = []
	row = db(dat_xe.id==id).select().first()
	db(dat_xe.id==id).update(is_update=True)
	return row
	


def call():
	return service()
	
	

	
def insert_dat_lich():
	from datatables import define_register,define_doctor
	define_doctor(db, False)
	register = define_register(db, False)
	# register.doctor.default=request.args(0)
	# form = cms.sqlform('register')
	# return  DIV(form,_class='row insert_dat_lich')
	l_v =[]
	try:
		div = DIV(_class='col-md-12 ')
		div_select = DIV(_class='col-md-6')
		div_select.append(DIV(INPUT(_type='radio',_name='f_check',_id="banthan",_checked='checked',_value='banthan'),' Bản thân',_class='bg_select'))
		div.append(div_select)
		div_select = DIV(_class='col-md-6')
		div_select.append(DIV(INPUT(_type='radio',_name='f_check',_id="nguoithan",_checked=False,_value='nguoithan'),' Người thân'))
		
		l_v.append('f_check')
		div.append(div_select)
		
		
		div_bd = DIV(_class='div_body')
		
		dai_lich = DIV(_id='nguoi_dat',_class='display_none')
		dai_lich.append(H4('Thông tin người đặt lịch',_class='col-md-12 title'))
		div_name = DIV(_class='col-md-6')
		div_name.append(P('Họ và tên'))
		div_name.append(INPUT(_class='form-control string',_type='text',_name='ten_nguoi_dang_ky'))
		l_v.append('ten_nguoi_dang_ky')
		dai_lich.append(div_name)
		div_phone = DIV(_class='col-md-6')
		div_phone.append(P('Điện thoại'))
		div_phone.append(INPUT(_class='form-control string',_type='text',_name='dien_thoai_nguoi_dang_ky'))
		l_v.append('dien_thoai_nguoi_dang_ky')
		dai_lich.append(div_phone)
		div_bd.append(dai_lich)
		
		div_bd.append(H4('Thông tin bệnh nhân',_class='col-md-12 title'))
		
		div_name = DIV(_class='col-md-6')
		div_name.append(P('Họ và tên'))
		div_name.append(INPUT(_class='form-control string',_type='text',_name='ten_benh_nhan',_id="benhnhan_name"))
		l_v.append('ten_benh_nhan')
		div_bd.append(div_name)
		
		div_phone = DIV(_class='col-md-6')
		div_phone.append(P('Điện thoại'))
		div_phone.append(INPUT(_class='form-control string',_type='text',_name='dien_thoai_benh_nhan'))
		l_v.append('dien_thoai_benh_nhan')
		div_bd.append(div_phone)
		
		div_tuoi = DIV(_class='col-md-6')
		div_tuoi.append(P('Giới tính'))
		select = SELECT([OPTION('Nam',_value='sex_male'),OPTION('Nữ',_value='sex_female')],_name='f_sex',_class='form-control')
		l_v.append('f_sex')
		div_tuoi.append(select)
		div_bd.append(div_tuoi)
		
		div_phone = DIV(_class='col-md-6')
		div_phone.append(P('Độ tuổi'))
		select = SELECT([OPTION('< 1 tuổi',_value='0')],_class='form-control',_name='f_year')
		l_v.append('f_year')
		i =1
		while i <101:
			select.append(OPTION('%s tuổi'%(i),_value=i))
			i+=1
		
		div_phone.append(select)
		div_bd.append(div_phone)
		
		
		div_bd.append(H4('Thông tin lịch hẹn',_class='col-md-12 title'))
		div_name = DIV(_class='col-md-6')
		
		dt = db(db.doctor.id==request.args(0)).select().first()
		if dt:	
			div_name.append(H6("Khoa ",dt.folder.label,BR(),B(dt.name),_class='bac_sy_ten'))
			div_bd.append(div_name)
						
			div_name = DIV(_class='col-md-6')
			div_name.append(P('Ngày hẹn'))
			div_name.append(INPUT(_class='form-control datepicker',_type='text',_name='f_date',_id='datepicker'))
			l_v.append('f_date')
			div_bd.append(div_name)

		else:
			
			rows = db(db.folder.parent==170).select()
			ops = []
			ops.append(OPTION("Lựa chọn khoa", _value=0, _selected=True))
			for row in rows:
				v =  DIV(row.label)
				ops.append(OPTION(v, _value=row.id, _selected=False))	
				
			ajax = "ajax('%s', ['folder'], 'wp_bac_sy')"%(URL( c='plugin_public',f='fint_doctor'))
			widget = SELECT(ops,_name="folder",_id="%s_%s"%("folder",'name'),_multiple=False,_class="form-control tags",_onchange=ajax)
			
			script = SCRIPT('''
			sc = '<script>'
				sc+='$(".tags").chosen({no_results_text: "No data!"}); '
				sc+='</script>'
				$('body').append(sc);
			''')
			
			widget.append(script)
			div_name.append(widget)
			l_v.append('folder')
			div_bd.append(div_name)
			
			div_name = DIV(_class='col-md-6')
			
			ops = []
			ops.append(OPTION("Lựa chọn bác sỹ", _value=0, _selected=True))
		
			widget = SELECT(ops,_name="bac_sy",_id="%s_%s"%("bac_sy",'name'),_multiple=False,_class="form-control tags")
			
			div_name.append(DIV(widget,_id='wp_bac_sy'))
			l_v.append('bac_sy')
			div_bd.append(div_name)
		
			
			div_name = DIV(_class='col-md-12')
			div_name.append(P('Ngày hẹn'))
			div_name.append(INPUT(_class='form-control datepicker',_type='text',_name='f_date',_id='datepicker'))
			l_v.append('f_date')
			div_bd.append(div_name)
		
		div_name = DIV(_class='col-md-12')
		div_name.append(P('Ghi chú'))
		div_name.append(TEXTAREA(_class='form-control',_name='f_des',_rows="1"))
		l_v.append('f_des')
		div_bd.append(div_name)
		
		div.append(div_bd)
		
		ajax = "ajax('%s',%s, 'alert_insert_dat_lich')"%(URL(r=request,c='plugin_public',f='act_insert_dat_lich',args=request.args),l_v)
		
		div.append(DIV(_class='clearfix'))
		div.append(DIV(_id='alert_insert_dat_lich'))
		div.append(DIV(A('Đặt lịch ngay',_class='btn btn-primary',_id="datlich",_onclick=ajax),_class='col-md-12 btn_dat_lich'))
		div.append(DIV(_class='clearfix'))
		scr ='''
		<script type="text/javascript">
			$(document).ready(function(){
				$('.datepicker').datepicker({
					autoclose: true,
					format: 'dd/mm/yyyy',
				});
			});
			$('input[type=radio]').change( function() {
				$('#banthan').parent().removeClass( "bg_select" )
				$('#nguoithan').parent().removeClass( "bg_select" )

				if($(this).val() == "banthan"){
					$("#nguoi_dat").hide();
					
				}
				else {
					$("#nguoi_dat").show();
				  }
			  
				$(this).parent().addClass("bg_select");
			});

		</script>
		'''
		div.append(XML(scr))
		response.view ='admin/form_patient.html'
		return dict(content = DIV(div,_class='row insert_dat_lich'))
	except Exception,e: return e
	
def fint_doctor():
	from datatables import define_register,define_doctor
	define_doctor(db, False)
	rows = db(db.doctor.folder==request.vars.folder).select()
	if len(rows)==0:
		return DIV('Chưa có thông tin bác sỹ trong khoa',_class='bac_sy_ten')
	ops = []
	ops.append(OPTION(" Lựa chọn bác sỹ", _value=0, _selected=True))
	for row in rows:
		v =  DIV(row.name)
		ops.append(OPTION(v, _value=row.id, _selected=False))	
	widget = SELECT(ops,_name="bac_sy",_id="%s_%s"%("doctor",'name'),_multiple=False,_class="form-control tags")
	
	script = SCRIPT('''
	sc = '<script>'
		sc+='$(".tags").chosen({no_results_text: "No data!"}); '
		sc+='</script>'
		$('body').append(sc);
	''')
	
	widget.append(script)
	return widget
	
	
def act_insert_dat_lich():
	try:
		import datetime
		div = DIV()
		from datatables import define_register,define_doctor
		from plugin_process import ProcessModel,Process
		obj = ProcessModel().define_objects()
		define_doctor(db, False)
		register = define_register(db, False)
		
		ten_benh_nhan = request.vars.ten_benh_nhan
		dien_thoai_benh_nhan = request.vars.dien_thoai_benh_nhan
		dien_thoai_nguoi_dang_ky = request.vars.dien_thoai_nguoi_dang_ky
		f_sex = request.vars.f_sex
		f_year = request.vars.f_year
		f_date = request.vars.f_date
		f_des = request.vars.f_des
		bac_sy = request.vars.bac_sy
		
		
		if ten_benh_nhan =="":
			return P("Cần nhập họ và tên",_style=" color: #f00;")
		if dien_thoai_nguoi_dang_ky =="":
			if dien_thoai_benh_nhan =="":
				return P("Cần nhập số điện thoại",_style=" color: #f00;")
		if request.args(0)==None:
			if bac_sy=="0":
				return P("Cần lựa chọn bác sĩ hẹn khám",_style=" color: #f00;")
				
		else: bac_sy = request.args(0)
		
		folder = request.vars.folder if request.vars.folder else db.doctor[bac_sy].folder
		
		if f_date =="":
			return P("Cần nhập thời gian hẹn khám",_style=" color: #f00;")
			
		f_date_new = datetime.datetime.strptime(f_date, '%d/%m/%Y').strftime("%Y-%m-%d")
		
		if request.vars.f_check =='banthan':
			id = db.register.insert(folder=folder,name=ten_benh_nhan,sex=f_sex,year_old=f_year,phone=dien_thoai_benh_nhan,doctor=bac_sy,start_date=f_date_new,htmlcontent=f_des)
			if id:
				Process().create_objects_work(folder,'register',id,57,10)
		elif request.vars.f_check =='nguoithan':
			dien_thoai_nguoi_dang_ky = request.vars.dien_thoai_nguoi_dang_ky
			ten_nguoi_dang_ky = request.vars.ten_nguoi_dang_ky
			if ten_nguoi_dang_ky =="":
				return P("Cần nhập họ và tên người đăng ký",_style=" color: #f00;")
			if dien_thoai_nguoi_dang_ky =="":
				return P("Cần nhập số điện thoại người đăng ký",_style=" color: #f00;")
			id = db.register.insert(folder=folder,name=ten_benh_nhan,sex=f_sex,year_old=f_year,phone=dien_thoai_benh_nhan,doctor=bac_sy,start_date=f_date_new,htmlcontent=f_des,homie=ten_nguoi_dang_ky,phone1=dien_thoai_nguoi_dang_ky)
			if id:
				Process().create_objects_work(folder,'register',id,57,10)
			
		scr ='''
		<script type="text/javascript">
			setTimeout(function(){
				$("#button_close").click();
			}, 2000);
			
		</script>
		'''
		div.append(P('Cập nhật thành công'))
		div.append(XML(scr))
		return div
	except Exception,e: return e
		
	
	
	
	
def insert_hoi_dap():
	l_v =[]
	try:
		folder_id = request.vars.folder
		div_bd = DIV(_id='wr_page_hoi_dap')
		
		div_name = DIV(_class='col-md-4')
		div_name.append(P('Họ và tên'))
		div_name.append(INPUT(_class='form-control string',_type='text',_name='ten_nguoi_hoi'))
		l_v.append('ten_nguoi_hoi')
		
		div_bd.append(div_name)
		
		div_name = DIV(_class='col-md-4')
		div_name.append(P('Số điện thoại'))
		div_name.append(INPUT(_class='form-control string',_type='text',_name='dt_nguoi_hoi'))
		l_v.append('dt_nguoi_hoi')
		
		div_bd.append(div_name)
		
		div_name = DIV(_class='col-md-4')
		div_name.append(P('Email'))
		div_name.append(INPUT(_class='form-control string',_type='text',_name='email_nguoi_hoi'))
		l_v.append('email_nguoi_hoi')
		
		div_bd.append(div_name)
		
		if folder_id == None:
			
			div_name = DIV(_class='col-md-8')
			div_name.append(P('Tóm tắt câu hỏi'))
			div_name.append(INPUT(_class='form-control string',_type='text',_name='name_cau_hoi'))
			l_v.append('name_cau_hoi')
			
			div_bd.append(div_name)
			
			div_name = DIV(_class='col-md-4')
			div_name.append(P('Lĩnh vực cần hỏi'))
			cms.define_folder()
			
			# from plugin_process import Process
			# process = Process()
			# db = process.cms.db
			
			rows = db(db.folder.parent==85).select()
			ops = []
			ops.append(OPTION("Lựa chọn danh mục", _value=0, _selected=True))
			for row in rows:
				v =  DIV(row.label)
				ops.append(OPTION(v, _value=row.id, _selected=False))	
			widget = SELECT(ops,_name="folder",_id="%s_%s"%("folder",'name'),_multiple=False,_class="form-control tags")
			
			script = SCRIPT('''
			sc = '<script>'
				sc+='$(".tags").chosen({no_results_text: "No data!"}); '
				sc+='</script>'
				$('body').append(sc);
			''')
			
			widget.append(script)
			div_name.append(widget)
			l_v.append('folder')
			div_bd.append(div_name)
		
		else:
			div_name = DIV(_class='col-md-12')
			div_name.append(P('Tóm tắt câu hỏi'))
			div_name.append(INPUT(_class='form-control string',_type='text',_name='name_cau_hoi'))
			l_v.append('name_cau_hoi')
			
			div_bd.append(div_name)
			
		div_name = DIV(_class='col-md-12')
		div_name.append(P('Nội dung câu hỏi'))
		div_name.append(TEXTAREA(_class='form-control string',_id="hoi_dap_description" ,_name='des_cau_hoi'))
		l_v.append('des_cau_hoi')
		
		div_bd.append(div_name)
		
		div_name = DIV(_class='col-md-12')
		div_name.append(BR())
		div_name.append(DIV(_id='page_hoi_dap_message'))
		
		ajax = "ajax('%s', %s, 'page_hoi_dap_message')"%(URL( c='plugin_public',f='add_hoi_dap'),l_v)
		div_name.append(INPUT(_type='button',_value='Gửi câu hỏi',_onclick=ajax,_class='btn'))
		response.view ='admin/form_patient.html'
		div_bd.append(div_name)
		
		return div_bd
	except Exception,e: return e
	

def add_hoi_dap():	
	from plugin_cms import Cms
	from plugin_cms import CmsFolder
	cms = Cms()
	folder_id= 228
	hoi_dap = cms.define_table('hoi_dap')
	if not request.vars.name_cau_hoi:
		return  DIV(B('Bạn chưa nhập tiêu đề câu hỏi'),_class='bg-do text-center' )
	if not request.vars.des_cau_hoi:
		return  DIV(B('Bạn chưa nhập câu hỏi'),_class='bg-do text-center' )
	if not request.vars.ten_nguoi_hoi:
		return  DIV(B('Bạn chưa nhập họ tên'),_class='bg-do text-center' )
	if not request.vars.dt_nguoi_hoi:
		return  DIV(B('Bạn chưa nhập số điện thoại'),_class='bg-do text-center' )
	if request.vars.folder:
		folder_id = request.vars.folder
		
	from plugin_cms import CmsFolder
	
		
	id = cms.db.hoi_dap.insert(folder=folder_id ,name=request.vars.name_cau_hoi,description=request.vars.des_cau_hoi,email=request.vars.email_nguoi_hoi,dien_thoai=request.vars.dt_nguoi_hoi,nguoi_hoi=request.vars.ten_nguoi_hoi)
	if id:
		from plugin_process import ProcessModel
		objects = ProcessModel().define_objects()
		
		objects_id = objects.insert(folder=folder_id ,foldername= CmsFolder().folder_fname(folder_id), tablename='hoi_dap',table_id=id,auth_group=10,process=36)
	div = DIV(B('Gửi câu hỏi thành công!'),_class='bg-info text-center' )
	script = '''
	<script>
		setTimeout("ajax('%s', [], 'wr_page_hoi_dap')",3000);
	</script>
	'''%(URL( c='plugin_public',f='insert_hoi_dap',vars=dict(folder=folder_id)))
	div.append(XML(script))
	
	return div
	
	

def send_sms():
	import datetime
	import requests
	from datatables import define_sms_vnpt,define_sms_medic
	from plugin_process import ProcessModel
	obj = ProcessModel().define_objects()
	sms_vnpt = define_sms_vnpt(db, False)
	sms_medic = define_sms_medic(db, False)
	rows_send = db(sms_medic.status=='queue').select(limitby=(0,5))
	ul = UL()
	for row in rows_send:
		r_vnpt = db.sms_vnpt[row.sms_vnpt]
		url = r_vnpt.url_port
		headers = {'Content-Type':'application/json'}	
		body  = { "RQST": {   
			"name": "send_sms_list",
			"REQID": r_vnpt.reqid ,
			"LABELID": r_vnpt.labelid,
			"CONTRACTTYPEID": r_vnpt.contracttypeid,
			"CONTRACTID":r_vnpt.contractid,
			"TEMPLATEID": r_vnpt.templateid,	
			"PARAMS":row.params,		
			"SCHEDULETIME": r_vnpt.scheduletime if r_vnpt.scheduletime else "",
			"MOBILELIST": row.mobilelist,	
			"ISTELCOSUB": r_vnpt.istelcosub,
			"AGENTID":r_vnpt.agentid,
			"APIUSER": r_vnpt.apiuser,
			"APIPASS": r_vnpt.apipass,
			"USERNAME":r_vnpt.username,
			"DATACODING":r_vnpt.datacoding
			}		
		}
		a = requests.post(url,headers=headers, json=body).json()
		from plugin_sms import MEDIC_SMS
		if a['RPLY']['ERROR']==0:
			MEDIC_SMS().send_return(row.id,status='sent',error=a['RPLY']['ERROR'],error_name=a['RPLY']['name'],error_desc=a['RPLY']['ERROR_DESC'])
		else:
			MEDIC_SMS().send_return(row.id,status='pending',error=a['RPLY']['ERROR'],error_name=a['RPLY']['name'],error_desc=a['RPLY']['ERROR_DESC'])
	return True
	
	
	
def form_so_dt_bravo():
	form = FORM(_class="col-md-12")
	
	div1 = DIV(_class="form-group")
	# div1.append(LABEL('Điện thoại'))
	div1.append(INPUT(_type='text',_class="form-control string mask mask-integer",_name='dien_thoai3',_id='phone-number', _placeholder="Số điện thoại của bạn" ,_style="height: 35px; width: 93%;",**{"_maxlength":"15"}))
	
	# scr ='''
		# <script>
			# $('#phone-number')

	# .keydown(function (e) {
		# var key = e.which || e.charCode || e.keyCode || 0;
		# $phone = $(this);

    # // Don't let them remove the starting '('
    # if ($phone.val().length === 1 && (key === 8 || key === 46)) {
			# $phone.val('('); 
      # return false;
		# } 
    # // Reset if they highlight and type over first char.
    # else if ($phone.val().charAt(0) !== '(') {
			# $phone.val('('+String.fromCharCode(e.keyCode)+''); 
		# }

		# // Auto-format- do not expose the mask as the user begins to type
		# if (key !== 8 && key !== 9) {
			# if ($phone.val().length === 4) {
				# $phone.val($phone.val() + ')');
			# }
			# if ($phone.val().length === 5) {
				# $phone.val($phone.val() + ' ');
			# }			
			# if ($phone.val().length === 9) {
				# $phone.val($phone.val() + '-');
			# }
		# }

		# // Allow numeric (and tab, backspace, delete) keys only
		# return (key == 8 || 
				# key == 9 ||
				# key == 46 ||
				# (key >= 48 && key <= 57) ||
				# (key >= 96 && key <= 105));	
	# })
	
	# .bind('focus click', function () {
		# $phone = $(this);
		
		# if ($phone.val().length === 0) {
			# $phone.val('(');
		# }
		# else {
			# var val = $phone.val();
			# $phone.val('').val(val); // Ensure cursor remains at the end
		# }
	# })
	
	# .blur(function () {
		# $phone = $(this);
		
		# if ($phone.val() === '(') {
			# $phone.val('');
		# }
	# });
		# </script>
	# '''
	# div1.append(XML(scr))
	form.append(div1)
	
	ajax = "ajax('%s', ['dien_thoai3'], 'wr_ung_tuyen3')"%(URL(f='act_add_so_dt_bravo'))
	form.append(A('Yêu cầu báo giá ',I(_class='icon-forward'),_onclick=ajax, _class='btn btn-primary  pull-left'))
	return DIV(form,_class="form_so_dt",_id='wr_ung_tuyen3')
	

def act_add_so_dt_bravo():
	send_to = ["kimcuong136@gmail.com","anhnt8688@gmail.com"]
	you_phone = request.vars.dien_thoai3
	
	if you_phone=="":
		return DIV(H4(T('Chưa nhập số điện thoại')),_class='notice')
		
	subject   = "Thời trang Bravo: Khách hàng có số điện thoại " + you_phone +' đã yêu cầu báo giá' 
	content   = "Khách hàng có số điện thoại (<a href='tel:" + you_phone.replace("(",'').replace(")",'') + "'> <B>"+ you_phone +'</B></a>) đã để lại số điện thoại yêu cầu báo giá'
	
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	mail = auth.setting_mail()
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		response.cookies['de_lai_dt'] = True
		response.cookies['de_lai_dt']['path'] = '/'
		div = DIV(H4(T('Gửi số thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),H4("Tư vấn nhanh:",A("0941.6666.37 ",_href="tel:0941666637 "),_style='text-align: center; color: #d50c0c;'),XML(scr),_class='notice')
	else: 
		div = DIV(H4(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0941.6666.37. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	
	
def form_so_dt_advbravo():
	form = FORM(_class="col-md-12")
	
	div1 = DIV(_class="form-group")
	# div1.append(LABEL('Điện thoại'))
	div1.append(INPUT(_type='text',_class="form-control string mask mask-integer",_name='dien_thoai3',_id='phone-number', _placeholder="(XXX) XXX-XXXX" ,_style="height: 35px; width: 93%;",**{"_maxlength":"15"}))
	
	scr ='''
		<script>
			$('#phone-number')

	.keydown(function (e) {
		var key = e.which || e.charCode || e.keyCode || 0;
		$phone = $(this);

    // Don't let them remove the starting '('
    if ($phone.val().length === 1 && (key === 8 || key === 46)) {
			$phone.val('('); 
      return false;
		} 
    // Reset if they highlight and type over first char.
    else if ($phone.val().charAt(0) !== '(') {
			$phone.val('('+String.fromCharCode(e.keyCode)+''); 
		}

		// Auto-format- do not expose the mask as the user begins to type
		if (key !== 8 && key !== 9) {
			if ($phone.val().length === 4) {
				$phone.val($phone.val() + ')');
			}
			if ($phone.val().length === 5) {
				$phone.val($phone.val() + ' ');
			}			
			if ($phone.val().length === 9) {
				$phone.val($phone.val() + '-');
			}
		}

		// Allow numeric (and tab, backspace, delete) keys only
		return (key == 8 || 
				key == 9 ||
				key == 46 ||
				(key >= 48 && key <= 57) ||
				(key >= 96 && key <= 105));	
	})
	
	.bind('focus click', function () {
		$phone = $(this);
		
		if ($phone.val().length === 0) {
			$phone.val('(');
		}
		else {
			var val = $phone.val();
			$phone.val('').val(val); // Ensure cursor remains at the end
		}
	})
	
	.blur(function () {
		$phone = $(this);
		
		if ($phone.val() === '(') {
			$phone.val('');
		}
	});
		</script>
	'''
	div1.append(XML(scr))
	form.append(div1)
	
	ajax = "ajax('%s', ['dien_thoai3'], 'wr_ung_tuyen3')"%(URL(f='act_add_so_dt_advbravo'))
	form.append(A('Yêu cầu báo giá ',I(_class='icon-forward'),_onclick=ajax, _class='btn btn-primary  pull-left'))
	return DIV(form,_class="form_so_dt",_id='wr_ung_tuyen3')
	

def act_add_so_dt_advbravo():
	send_to = ["kimcuong136@gmail.com","anhnt8688@gmail.com"]
	you_phone = request.vars.dien_thoai3
	
	if you_phone=="":
		return DIV(H4(T('Chưa nhập số điện thoại')),_class='notice')
		
	subject   = "ADVBravo: Khách hàng có số điện thoại " + you_phone +' đã yêu cầu báo giá' 
	content   = "Khách hàng có số điện thoại (<a href='tel:" + you_phone.replace("(",'').replace(")",'') + "'> <B>"+ you_phone +'</B></a>) đã để lại số điện thoại yêu cầu báo giá'
	
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	mail = auth.setting_mail()
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		response.cookies['de_lai_dt'] = True
		response.cookies['de_lai_dt']['path'] = '/'
		div = DIV(H4(T('Gửi số thành công, chúng tôi sẽ liên lạc với quý khách trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),H4("Tư vấn nhanh:",A("0932 388 933 ",_href="tel:0932388933 "),_style='text-align: center; color: #d50c0c;'),XML(scr),_class='notice')
	else: 
		div = DIV(H4(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0932 388 933. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	
	
def form_so_dt_maomeo():
	form = FORM(_class="col-md-12")
	
	div1 = DIV(_class="form-group")
	# div1.append(LABEL('Điện thoại'))
	div1.append(INPUT(_type='text',_class="form-control string mask mask-integer",_name='dien_thoai3',_id='phone-number', _placeholder="(XXX) XXX-XXXX" ,_style="height: 35px; width: 93%;",**{"_maxlength":"15"}))
	
	scr ='''
		<script>
			$('#phone-number')

	.keydown(function (e) {
		var key = e.which || e.charCode || e.keyCode || 0;
		$phone = $(this);

    // Don't let them remove the starting '('
    if ($phone.val().length === 1 && (key === 8 || key === 46)) {
			$phone.val('('); 
      return false;
		} 
    // Reset if they highlight and type over first char.
    else if ($phone.val().charAt(0) !== '(') {
			$phone.val('('+String.fromCharCode(e.keyCode)+''); 
		}

		// Auto-format- do not expose the mask as the user begins to type
		if (key !== 8 && key !== 9) {
			if ($phone.val().length === 4) {
				$phone.val($phone.val() + ')');
			}
			if ($phone.val().length === 5) {
				$phone.val($phone.val() + ' ');
			}			
			if ($phone.val().length === 9) {
				$phone.val($phone.val() + '-');
			}
		}

		// Allow numeric (and tab, backspace, delete) keys only
		return (key == 8 || 
				key == 9 ||
				key == 46 ||
				(key >= 48 && key <= 57) ||
				(key >= 96 && key <= 105));	
	})
	
	.bind('focus click', function () {
		$phone = $(this);
		
		if ($phone.val().length === 0) {
			$phone.val('(');
		}
		else {
			var val = $phone.val();
			$phone.val('').val(val); // Ensure cursor remains at the end
		}
	})
	
	.blur(function () {
		$phone = $(this);
		
		if ($phone.val() === '(') {
			$phone.val('');
		}
	});
		</script>
	'''
	div1.append(XML(scr))
	form.append(div1)
	
	ajax = "ajax('%s', ['dien_thoai3'], 'wr_ung_tuyen3')"%(URL(f='act_add_so_dt_maomeo'))
	form.append(A('Yêu cầu báo giá ',I(_class='icon-forward'),_onclick=ajax, _class='btn btn-primary  pull-left'))
	return DIV(form,_class="form_so_dt",_id='wr_ung_tuyen3')
	

def act_add_so_dt_maomeo():
	send_to = ["anhnt8688@gmail.com"]
	you_phone = request.vars.dien_thoai3
	
	if you_phone=="":
		return DIV(H4(T('Chưa nhập số điện thoại')),_class='notice')
		
	subject   = "Khách hàng có số điện thoại " + you_phone +' đã yêu cầu báo giá' 
	content   = "Khách hàng có số điện thoại (<a href='tel:" + you_phone.replace("(",'').replace(")",'') + "'> <B>"+ you_phone +'</B></a>) đã để lại số điện thoại yêu cầu báo giá'
	
	scr ='''<script type="text/javascript"> 
   				setInterval("window.parent.close()",3000);
			</script>'''
	mail = auth.setting_mail()
	if mail.send(to=send_to,subject=subject,message='<html>%s</html>'%content):
		response.cookies['de_lai_dt'] = True
		response.cookies['de_lai_dt']['path'] = '/'
		div = DIV(H4(T('Gửi số thành công, Mão sẽ liên lạc với bạn trong thời gian sớm nhất. Xin cảm ơn'),_style='text-align: center;font-size: 16px;  margin-bottom: 0;'),BR(),H4("Liên hệ ngay:",A("0989666944",_href="tel:0989666944"),_style='text-align: center; color: #d50c0c;'),XML(scr),_class='notice')
	else: 
		div = DIV(H4(T('Gửi yêu cầu có lỗi, vui lòng liên hệ số điện thoại 0989666944. Xin cảm ơn ')),XML(scr),_class='notice')
	return div
	
def obj_product():
	from plugin_process import Process
	process = Process()
	db = process.cms.db
	product = process.cms.define_table('product')
	
	from plugin_process import ProcessModel
	from plugin_cms import CmsFolder
	objects = ProcessModel().define_objects()
	rows = db(product.id>0).select()
	i =0
	for row in rows:
		objects_id = objects.insert(folder=row.folder ,foldername=row.folder.name , tablename='product',table_id=row.id,auth_group=10,process=53)
		i+=1
	return i
	
