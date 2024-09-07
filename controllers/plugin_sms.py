###################################################
# This file was developed by IVINH
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2013
###################################################

from plugin_sms import SMS, PhoneBook
sms = SMS()

@auth.requires(auth.has_membership(role='admin'))
def index():
	redirect(URL(c='plugin_sms',f='inbox',vars=dict(orderby='id',asc='des')))
	response.view = 'plugin_sms/content.%s'%request.extension
	return dict(content=inbox())
	
@auth.requires(auth.has_membership(role='admin'))
def compose():
	content = create()
	return dict(content=content)

@auth.requires(auth.has_membership(role='admin'))
def new():
	content = create()
	return dict(content=content)

	
@auth.requires(auth.has_membership(role='admin'))
def reply():
	content = create()
	response.view = 'plugin_sms/compose.html'
	return dict(content=content)
	
@auth.requires(auth.has_membership(role='admin'))
def forward():
	content = create()
	response.view = 'plugin_sms/compose.html'
	return dict(content=content)
	
@auth.requires(auth.has_membership(role='admin'))
def create():
	type= request.vars.type or 'compose'
	div = DIV(_id='new_ivinh',_class="panel-primary box_news")
	url_send = URL(f='act_send')
	url_drafts = URL(f='act_drafts')
	if type =='reply':
		h3 = H3(T('Trả lời thư'),_class="panel-title")
		div.append(DIV(h3,_class="panel-heading"))
		panel_body = DIV(_class="panel-body")
		
	elif type =='forward':
		h3 = H3(T('Chuyển tiếp thư'),_class="panel-title")
		div.append(DIV(h3,_class="panel-heading"))
		panel_body = DIV(_class="panel-body")
	else:
		h3 = H3(T('Tin nhắn mới'),_class="panel-title")
		div.append(DIV(h3,_class="panel-heading"))
		panel_body = DIV(_class="panel-body")
		
	to = request.vars.to or ''
	content = request.vars.content or ''
		
	# panel_body.append(INPUT(_name='send_to',_autocomplete="off",_class="string ac_input input-email",_placeholder=T("Gửi tới"),_id="send_to",_value=to))
	panel_body.append(TEXTAREA(content,_class="ac_input input-email",_style='height:100px;',_autocomplete="off",_id='send_to',_name='send_to',_placeholder=T("Gửi tới")))
	panel_body.append(TEXTAREA(content,_class="content-email",_id='send_content',_name='send_content',_placeholder=T("Nội dung"),_onkeyup="locdau(this);"))
	panel_body.append(T("Vào lúc"))
	panel_body.append(INPUT(_name='publish',_autocomplete="off",_class="string ac_input input-email datetime",_id="publish",_value=request.now.strftime('%Y-%m-%d %H:%M:%S')))
	div.append(panel_body)
	panel_footer = DIV(_class="panel-footer")
	panel_footer.append(BUTTON(T('Gửi đi'),_type="submit",_class="btn btn-primary",_id='btn_send'))
	div.append(panel_footer)
	
	url_send = URL(f='act_send',args=request.args)
	list_email = URL(c='plugin_sms',f='list_email.json')
	scr ='''
	<script>
	$(function() {
		window.onbeforeunload = function(e) {  
        return 'You are going to close this window.';  
      };  
	
		function split( val ) {
			return val.split( /,\s*/ );
		}
		function extractLast( term ) {
			return split( term ).pop();
		}
		var url_search = "%s";
		$( "#send_to" ).autocomplete({
			source: function( request, response ) {
				$.ajax({
					url: url_search,
					dataType: "json",
					data: {
						maxRows: 15,
						name_startsWith: extractLast( request.term )
					},
					success: function(data) {
						response( $.map( data.add_email, function( item ) {
							return {
								label: item.name + ' <'+item.phone +'>',
								value: item.name + ' <'+item.phone +'>'
							}
						}));
					}
				});
			},
			minLength: 0,
			select: function( event, ui ) {
				var terms = split( this.value );
					terms.pop();
					terms.push( ui.item.value );
					terms.push( "" );
					this.value = terms.join( ", " );
					return false;
			},
		});
	});
	$("#btn_send").click(function () {
			$.ajax({
				url: "%s",
				data: { 
					'send_to': document.getElementById('send_to').value , 
					'send_content':  document.getElementById('send_content').value , 
					'publish':  document.getElementById('publish').value , 
				},
				type: "GET",
				cache: false,
				success: function (html) {
					window.opener.location.reload();
					window.close();
				}});
		});
		
	</script>'''%(list_email,url_send)
	srclocdau = SCRIPT('''function locdau(obj) { 
						var str;
						if (eval(obj)) {
							str = eval(obj).value;
							}
						else {
							str = obj; 
						}
						
						str = str.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, "a");
						str = str.replace(/À|Á|Ạ|Ả|Ã|Â|Ầ|Ấ|Ậ|Ẩ|Ẫ|Ă|Ằ|Ắ|Ặ|Ẳ|Ẵ/g, "A");
						str = str.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, "e"); 
						str = str.replace(/È|É|Ẹ|Ẻ|Ẽ|Ê|Ề|Ế|Ệ|Ể|Ễ/g, "E"); 
						str = str.replace(/ì|í|ị|ỉ|ĩ/g, "i");
						str = str.replace(/Ì|Í|Ị|Ỉ|Ĩ/g, "I");
						str = str.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, "o"); 
						str = str.replace(/Ò|Ó|Ọ|Ỏ|Õ|Ô|Ồ|Ố|Ộ|Ổ|Ỗ|Ơ|Ờ|Ớ|Ợ|Ở|Ỡ/g, "O"); 
						str = str.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, "u");
						str = str.replace(/Ù|Ú|Ụ|Ủ|Ũ|Ư|Ừ|Ứ|Ự|Ử|Ữ/g, "U");
						str = str.replace(/ỳ|ý|ỵ|ỷ|ỹ/g, "y"); 
						str = str.replace(/Ỳ|Ý|Y|Ỷ|Ỹ/g, "Y"); 
						str = str.replace(/đ/g, "d"); 
						str = str.replace(/Đ/g, "D"); 
						eval(obj).value = str; 
						}
				''')
	div.append(XML(scr))
	div.append(XML(srclocdau))
	return div

## Add by Longhh
## Sent multipe phonebook, group_phonebook

@auth.requires(auth.has_membership(role='admin'))
def create2():
	div = DIV(_id='new_ivinh',_class="panel-primary box_news")
	h3 = H3(T('Tin nhắn mới'),_class="panel-title")
	div.append(DIV(h3,_class="panel-heading"))
	panel_body = DIV(_class="panel-body")
		
	content = request.vars.content or ''
	check_box_select = request.vars.check_box_select
	if not isinstance(check_box_select,list): check_box_select = [check_box_select]
	list_sent = ''
	if check_box_select!=None:
		if request.args(0)=='phonebook':
			PhoneBook().define_phonebook()
			pbs = db(db.phonebook.id.belongs(check_box_select)).select()
			for pb in pbs:
				list_sent+= pb.name + '<'+ pb.phone +'>,'
		else:
			PhoneBook().define_group_phonebook()
			PhoneBook().define_phonebook()
			grs = db(db.group_phonebook.id.belongs(check_box_select)).select()
			for gr in grs:
				for c in gr.contact:
					pb = db.phonebook(c)
					list_sent+= pb.name + '<'+ pb.phone +'>,'
	# panel_body.append(INPUT(_name='send_to',_class="string ac_input input-email",_placeholder=T("Gửi tới"),_id="send_to",_value=list_sent))
	panel_body.append(TEXTAREA(list_sent,_class="content-email",_id='send_content',_name='send_to',_placeholder=T("Gửi tới")))
	panel_body.append(TEXTAREA(content,_class="content-email",_id='send_content',_name='send_content',_placeholder=T("Nội dung"),_onkeyup="locdau(this);"))
	panel_body.append(P("Vào lúc"))
	panel_body.append(INPUT(_name='publish',_autocomplete="off",_class="string ac_input input-email datetime",_id="publish",_value=request.now.strftime('%Y-%m-%d %H:%M:%S')))
	div.append(panel_body)
	panel_footer = DIV(_class="panel-footer")
	panel_footer.append(BUTTON(T('Gửi đi'),_type="submit",_class="btn btn-primary",_id='btn_send'))
	div.append(panel_footer)
	srclocdau = SCRIPT('''function locdau(obj) { 
						var str;
						if (eval(obj)) {
							str = eval(obj).value;
							}
						else {
							str = obj; 
						}
						str = str.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, "a");
						str = str.replace(/À|Á|Ạ|Ả|Ã|Â|Ầ|Ấ|Ậ|Ẩ|Ẫ|Ă|Ằ|Ắ|Ặ|Ẳ|Ẵ/g, "A");
						str = str.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, "e"); 
						str = str.replace(/È|É|Ẹ|Ẻ|Ẽ|Ê|Ề|Ế|Ệ|Ể|Ễ/g, "E"); 
						str = str.replace(/ì|í|ị|ỉ|ĩ/g, "i");
						str = str.replace(/Ì|Í|Ị|Ỉ|Ĩ/g, "I");
						str = str.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, "o"); 
						str = str.replace(/Ò|Ó|Ọ|Ỏ|Õ|Ô|Ồ|Ố|Ộ|Ổ|Ỗ|Ơ|Ờ|Ớ|Ợ|Ở|Ỡ/g, "O"); 
						str = str.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, "u");
						str = str.replace(/Ù|Ú|Ụ|Ủ|Ũ|Ư|Ừ|Ứ|Ự|Ử|Ữ/g, "U");
						str = str.replace(/ỳ|ý|ỵ|ỷ|ỹ/g, "y"); 
						str = str.replace(/Ỳ|Ý|Y|Ỷ|Ỹ/g, "Y"); 
						str = str.replace(/đ/g, "d"); 
						str = str.replace(/Đ/g, "D"); 
						eval(obj).value = str; 
						}
				''')
	div.append(XML(srclocdau))
	form = FORM(div,_action=URL(f='ac_sent2', args=request.args,vars=request.vars))
	response.view = 'plugin_sms/content.%s'%request.extension
	return dict(content=form)

@auth.requires(auth.has_membership(role='admin'))	
def ac_sent2():
	receives = request.vars.send_to or ''
	if receives[-1]==' ': receives = receives[:-1]
	if receives[-1]==',': receives = receives[:-1]
	content = request.vars.send_content or ''
	publish = request.vars.publish or request.now
	sms.add(db.auth_user(auth.user_id).username,receives,content,publish)
	redirect(URL(f='inbox'))
		
# @auth.requires(auth.has_membership(role='admin'))		
# def inbox():
	# div = DIV(_class="panel panel-primary")
	# div_s = DIV(_class="input-group",_id='wrap_search')
	# div_s.append(INPUT(type='text',_class="form-control"))
	# div_s.append(SPAN(BUTTON("Search",_type="button",_class="btn btn-default"),_class="input-group-btn"))
	# div.append(DIV(B(T('Quản lý tin nhắn')),_class="panel-heading"))
	# body = DIV(_class="panel-body")
	
	# body.append(DIV(_class='clearfix'))
	# div_title = DIV(_class="list-group-item",_id='title_list')	
	# # pull_left = DIV(INPUT(_type="checkbox",_id='ivinh_check_all'),_class='pull-left')
	# # div_title.append(pull_left)
	# div_title.append(menu_top())
	# body.append(div_title)
	# # list_group = UL(_class="list-group")
	# table = TABLE(_class='table table-bodered')
	# pb = PhoneBook()
	
	# try:
		# rows = sms.get()
		# if len(rows)>0:
			# i=0
			# if request.vars.asc=='des': 
				# sort = 'asc'
			# else:
				# sort = 'des'
			# span = SPAN(_class="glyphicon glyphicon-sort-by-alphabet")
			
			# ajax="ajax('%s', [], 'ivinh_wrap_content')"%(URL(r=request,c='plugin_sms',f='inbox.load',vars=dict(orderby='publish',asc=sort,type='inbox')))
			
			# pull_right =  DIV(A(B(T('Vào lúc ')),span,_onclick=ajax),_class='')
			# ajax = "ajax('%s', [], 'ivinh_wrap_box')"%(URL(f='search_user',args=request.args,vars=request.vars,extension='load'))
			
			# tr = TR(_class='')
			# # li = LI(_class="list-group-item is_title")
			
			# ajax="ajax('%s', [], 'ivinh_wrap_content')"%(URL(r=request,c='plugin_sms',f='inbox.load',vars=dict(orderby='user',asc=sort,type='inbox')))
			
			# icon ='''<a href="#" data-toggle="popover" data-placement="top" data-original-title="" title=""><span class="glyphicon glyphicon-collapse-down"></span></a>'''
			# scr ='''
			# <script>
				# $(function () {
					# $(".popover-examples a").popover({
						# title : 'Lọc theo người gửi',
						# content:'%s',
						# html:true
					# });
				# });
				# </script> 
			# '''%(div_s)
			# pull_left = INPUT(_type="checkbox",_id='ivinh_check_all')
			# search = SPAN(XML(icon),_class="popover-examples")
			# search.append(XML(scr))
			# tr.append(TD(pull_left))
			# tr.append(TD(search,A(B(T('Người gửi ')),span,_onclick=ajax),_style='width:130px;'))
			
			# ajax="ajax('%s', [], 'ivinh_wrap_content')"%(URL(r=request,c='plugin_sms',f='inbox.load',vars=dict(orderby='receives',asc=sort,type='inbox')))
			
			# tr.append(TD(A(B(T('Người nhận ')),span,_onclick=ajax)))
			
			# ajax="ajax('%s', [], 'ivinh_wrap_content')"%(URL(r=request,c='plugin_sms',f='inbox.load',vars=dict(orderby='content',asc=sort,type='inbox')))
			
			# tr.append(TD(A(B(T('Nội dung ')),span,_onclick=ajax)))
			
			# tr.append(TD(pull_right))
			# thead = THEAD(tr)
			# # table.append(tr)
			# # list_group.append(tr)
			# from plugin_sms import get_short_string
			# tbody = TBODY()
			# for row in rows:
				# tr = TR(_class="")		
				# pull_left = DIV(INPUT(_type="checkbox",_name='check_box_select',_value=row.id),_class='list-group')
				
				# # content = A(SPAN(pb.get_name(row.user)),SPAN(sms.receives(get_short_string(text=row.receives,length=150) or'')),row.content,_class='title_ivinh',_href=URL(f='detail.html',args=[row.id]))
			
				# pull_right = DIV(_class='')
				# if row.publish > request.now:
					# pull_right.append(SPAN(B(row.publish.strftime('%d-%m-%Y %H:%M')),_title=row.publish,_class='list-group'))
				# else:	
					# pull_right.append(SPAN((row.publish).strftime('%d-%m-%Y %H:%M'),_title=row.publish,_class='list-group'))
				# tr.append(TD(pull_left))
				# # tr.append(TD(content))
				# tr.append(TD(A(SPAN(pb.get_name(row.user))),_href=URL(f='detail.html',args=[row.id])))
				# tr.append(TD(A(sms.receives(get_short_string(text=row.receives,length=150) or'')),_href=URL(f='detail.html',args=[row.id])))
				# tr.append(TD(A(row.content),_href=URL(f='detail.html',args=[row.id])))
				# tr.append(TD(pull_right))
				# i+=1
				# tbody.append(tr)
			# table.append(thead)
			# table.append(tbody)
			# body.append(table)
	# except Exception, e:
		# body.append(e)
				
	# div.append(body)
	# scr ='''
	# <script type="text/javascript">
		# $(document).ready(function(){
			# $('#example').popover(content='ok');
			# $('#ivinh_check_all').click(function(){
				# if ($(this).is(':checked')) {
					# $(".list-group").find('input:checkbox').attr('checked', true);
				# }
				# else{
					# $(".list-group").find('input:checkbox').attr('checked', false);
				# }
			   
			# });
		# });
	# </script>
	# '''
	# div.append(XML(scr))
	# if request.extension =='load':
		# return div
	# else:
		# response.view = 'plugin_sms/content.%s'%request.extension
		# return dict(content=div)

@auth.requires(auth.has_membership(role='admin'))		
def inbox():
	div = DIV(_class="panel panel-primary")
	div_s = DIV(_class="input-group",_id='wrap_search')
	div_s.append(INPUT(type='text',_class="form-control"))
	div_s.append(SPAN(BUTTON("Search",_type="button",_class="btn btn-default"),_class="input-group-btn"))
	div.append(DIV(B(T('Quản lý tin nhắn')),_class="panel-heading"))
	body = DIV(_class="panel-body")
	
	body.append(DIV(_class='clearfix'))
	div_title = DIV(_class="list-group-item",_id='title_list')	
	# pull_left = DIV(INPUT(_type="checkbox",_id='ivinh_check_all'),_class='pull-left')
	# div_title.append(pull_left)
	div_title.append(menu_top())
	body.append(div_title)
	# list_group = UL(_class="list-group")
	table = TABLE(_class='table table-bodered',_id='paging')
	pb = PhoneBook()
	try:
		rows = sms.get()
		if len(rows)>0:
			i=1
			pull_left = INPUT(_type="checkbox",_id='ivinh_check_all')
			tr = TR(TH(pull_left),TH('STT'),TH('Người gửi'),TH('Người nhận'),TH('Nội dung'),TH('Vào lúc'))
			thead = THEAD(tr)
			from plugin_sms import get_short_string
			tbody = TBODY()
			for row in rows:
				tr = TR(_class="")		
				pull_left = DIV(INPUT(_type="checkbox",_name='check_box_select',_value=row.id),_class='list-group')			
				pull_right = DIV(_class='')
				if row.publish > request.now:
					pull_right.append(SPAN(B(row.publish.strftime('%d-%m-%Y %H:%M')),_title=row.publish,_class=''))
				else:	
					pull_right.append(SPAN((row.publish).strftime('%d-%m-%Y %H:%M'),_title=row.publish,_class=''))
				tr.append(TD(pull_left))
				tr.append(TD(i))
				tr.append(TD(A(SPAN(pb.get_name(row.user)),_href=URL(f='detail.html',args=[row.id]))))
				tr.append(TD(A(sms.receives(get_short_string(text=row.receives,length=150) or''),_href=URL(f='detail.html',args=[row.id]))))
				tr.append(TD(A(row.content,_href=URL(f='detail.html',args=[row.id]))))
				tr.append(TD(pull_right))
				i+=1
				tbody.append(tr)
			table.append(thead)
			table.append(tbody)
			body.append(table)
	except Exception, e:
		body.append(e)
				
	div.append(body)
	scr ='''
	<script type="text/javascript">
		$(document).ready(function(){
			$('#example').popover(content='ok');
			$('#ivinh_check_all').click(function(){
				if ($(this).is(':checked')) {
					$(".list-group").find('input:checkbox').attr('checked', true);
				}
				else{
					$(".list-group").find('input:checkbox').attr('checked', false);
				}
			   
			});
		});
	</script>
	'''
	div.append(XML(scr))
	if request.extension =='load':
		return div
	else:
		response.view = 'plugin_sms/content.%s'%request.extension
		return dict(content=div)		
		
@auth.requires(auth.has_membership(role='admin'))		
def detail():
	div = DIV(_class="panel panel-primary")
	div_s = DIV(_class="input-group",_id='wrap_search')
	div_s.append(INPUT(type='text',_class="form-control"))
	div_s.append(SPAN(BUTTON("Search",_type="button",_class="btn btn-default"),_class="input-group-btn"))
	div.append(DIV(B(T('Danh sách người nhận')),_class="panel-heading"))
	body = DIV(_class="panel-body")
	
	body.append(DIV(_class='clearfix'))
	div_title = DIV(_class="list-group-item",_id='title_list')	
	pull_left = DIV(INPUT(_type="checkbox",_id='ivinh_check_all'),_class='pull-left')
	div_title.append(menu_top())
	body.append(div_title)
	table = TABLE(_class='table table-striple')
	try:
		rows = sms.get_log(request.args(0))
		if len(rows)>0:
			i=1
			tr = TR()
			tr.append(TH(pull_left))
			tr.append(TH('STT'))
			tr.append(TH(T('Người nhận ')))
			tr.append(TH(T('Trạng thái ')))
			tr.append(TH(T('Vào lúc ')))
			thead = THEAD(tr)
			table.append(thead)
			for row in rows:
				tr = TR()
				pull_left = DIV(INPUT(_type="checkbox",_name='check_box_select',_value=row.id,_class='ivinhcheck'))
				tr.append(TD(pull_left))
				tr.append(TD(i))
				tr.append(TD(PhoneBook().get_name_by_phone(row.phone)))
				tr.append(TD(row.status))
				tr.append(TD((row.publish).strftime('%H:%M %d-%m-%Y') if row.publish else ''))
				i+=1
				table.append(tr)
			body.append(table)
	except Exception, e:
		body.append(e)
				
	div.append(body)
	scr ='''<script type="text/javascript">
		$(document).ready(function(){
			 $('#example').popover(content='ok');
			$('#ivinh_check_all').click(function(){
				if ($(this).is(':checked')) {
					$(".ivinhcheck").attr('checked', true);
				}
				else{
					$(".ivinhcheck").attr('checked', false);
				}
			   
			});
		});
	</script>'''
	div.append(XML(scr))	
	if request.extension =='load': return div
	return dict(content=div)

		
@auth.requires(auth.has_membership(role='admin'))
def contact():
	div = DIV(_class="panel panel-primary read")
	h3 = H3(B(T('Danh bạ')),_class="panel-title")
	div.append(DIV(h3,_class="panel-heading"))
	body = DIV(_class='panel-body')
	
	title_body = DIV(A(),_class='title_body')
	compose = URL(f='created_contact.html')
	title_body.append(A(SPAN(_class='glyphicon  glyphicon-edit'),T(' Thêm danh bạ'),_href=compose,_class='btn btn-primary'))
	title_body.append(A(SPAN(_class='glyphicon glyphicon-trash'),T(' Xóa'),_id='act_delete',_class='btn btn-primary'))
	# title_body.append(page())
	
	title_body.append(BUTTON(T(' Gửi tin nhắn'),_type='submit',_class='btn btn-primary', _style='margin-left:15px;'))
	
	group = DIV(_class='input-group',_style=" margin-top: 15px;")
	
	group.append(INPUT(_type='text',_class='string form-control',_name='key_search'))
	group.append(SPAN(BUTTON("Lọc dữ liệu",_class='btn btn-primary ',_type="submit"),_class='input-group-btn'))
	
	# title_body.append(group)
	
	scr ='''
	<script type="text/javascript">
	function hideMessage() {
			$(".ivinh_mesage").remove();
		}
	$("#act_delete").click(function () {
		if($('.list-gr input:checkbox').is(':checked')) {
			
				ajax('%s', ['check_box_select'], 'ivinh_wrap_content');
			}
		else{
				$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Chưa chọn tin nhắn để xóa.</b></div>" );
				window.setTimeout("hideMessage()", 3000);
			}
	});
		
	</script>
	'''%(URL(f='delete_contact',vars=dict(f_from=request.function)))
	title_body.append(XML(scr))
	
	
	body.append(DIV(title_body,_id='title_list',_class='list-group-item'))
	content = TABLE(THEAD(TR(TH(INPUT(_type="checkbox",_name='check_box_select_all',_id='ivinh_check_all'),_style=" width: 26px; "),TH('STT',_style=" width: 50px; text-align: center; "),TH('Tên'),TH('Đơn vị'),TH('Điện thoại'),TH('Thư điện tử'),_class='title_top')),_class='table',_id='paging')
		
	PhoneBook().define_phonebook()
	query = db.phonebook.id>0
	if request.vars.key_search:
		query =((db.phonebook.phone.upper().like('%'+request.vars.key_search+"%"))|(db.phonebook.name.upper().like('%'+request.vars.key_search+"%")))
	rows = db(query).select(orderby=db.phonebook.name)
	i = 1
	for row in rows:
		compose = 'window.open("%s","%s","width=1200,height=550,toolbar=no,location=no,directories=no,status=no,menubar=no,left=600,top=0")'%(URL(f='compose.html',vars=dict(to=row.phone)),T('Compose'))
		pull_left = DIV(INPUT(_type="checkbox",_name='check_box_select',_value=row.id),_class='list-gr')
		
		read_contact=URL(r=request,c='plugin_sms',f='read_contact.html',args=['contact',row.id],vars=request.vars)
		
		tr = TR(TD(pull_left),TD(i,_style=" width: 50px; text-align: center; "),TD(A(row['name'],_href=read_contact)),TD(row['org'] or ''),TD(A(row['phone'].replace(',',', '),_href='#',_onclick=compose)),TD(row['email']))
		content.append(tr)
		i+=1
	body.append(content)
	div.append(body)
	scr ='''
	<script type="text/javascript">
		$(document).ready(function(){
			$('#ivinh_check_all').click(function(){
				if ($(this).is(':checked')) {
					$(".list-gr").find('input:checkbox').attr('checked', true);
				}
				else{
					$(".list-gr").find('input:checkbox').attr('checked', false);
				}
			   
			});
		});
	</script>
	'''
	div.append(XML(scr))
	div = FORM(div,_action=URL(f='create2',args=['phonebook'], vars=request.vars))
	if request.extension =='load':
		return div
	else:
		response.view = 'plugin_sms/content.%s'%request.extension
		return dict(content=div)
		
def read_contact():
	PhoneBook().define_phonebook()
	row = db(db.phonebook.id==request.args(1)).select().first()
	
	div = DIV(_class="panel panel-primary read")
	contact = URL(f='contact.html')
	h3 = H3(A('',_class='glyphicon glyphicon-step-backward',_href=contact),B(row.name),_class="panel-title")
	div.append(DIV(h3,_class="panel-heading"))
	body = DIV(_class='panel-body')
	from gluon.tools import Crud
	crud = Crud(db)
	form =  crud.update(db.phonebook,request.args(1))
	if form.process().accepted:
		scr ='''
		<script type="text/javascript">
		function hideMessage() {
				$(".ivinh_mesage").remove();
			}
		$(document).ready(function(){
			$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Cập nhật thành công.</b></div>" );
			window.setTimeout("hideMessage()", 2000);
		});
			
		</script>
		'''
		body.append(XML(scr))
	body.append(DIV(form,_id='read_contact'))
	div.append(body)
	if request.extension =='load':
		return div
	else:
		response.view = 'plugin_sms/content.%s'%request.extension
		return dict(content=div)
		
def created_contact():
	PhoneBook().define_phonebook()
	div = DIV(_class="panel panel-default read")
	contact = URL(f='contact.html')
	h3 = H3(A('',_class='glyphicon glyphicon-step-backward',_href=contact),B(' Tạo danh bạ'),_class="panel-title")
	div.append(DIV(h3,_class="panel-heading"))
	body = DIV(_class='panel-body')
	from gluon.tools import Crud
	crud = Crud(db)
	form =  crud.create(db.phonebook)
	if form.process().accepted:
		scr ='''
		<script type="text/javascript">
		function hideMessage() {
				$(".ivinh_mesage").remove();
			}
		$(document).ready(function(){
			$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Thêm mới thành công.</b></div>" );
			window.setTimeout("hideMessage()", 2000);
		});
			
		</script>
		'''
		body.append(XML(scr))
	body.append(DIV(form,_id='read_contact'))
	div.append(body)
	if request.extension =='load':
		return div
	else:
		response.view = 'plugin_sms/content.%s'%request.extension
		return dict(content=div)
		
def delete_contact():
	list_check = request.vars.check_box_select
	if isinstance(list_check,str): list_check = [list_check]
	list_check = [int(uid) for uid in list_check]
	PhoneBook().delete(list_check )
	f = request.vars.f_from.split('.')[0]
	div = DIV(LOAD(f='%s.load'%f))
	scr ='''<script type="text/javascript">
		function hideMessage() {
			$(".ivinh_mesage").remove();
		}
		$(document).ready(function(){
			$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Xóa thành công %s danh bạ.</b></div>" );
			window.setTimeout("hideMessage()", 2000);
		});
	</script>'''%(len(request.vars.check_box_select))
	div.append(XML(scr))
	return div

@auth.requires(auth.has_membership(role='admin'))
def group_contact():
	div = DIV(_class="panel panel-primary read")
	h3 = H3(B(T('Nhóm danh bạ')),_class="panel-title")
	div.append(DIV(h3,_class="panel-heading"))
	body = DIV(_class='panel-body')
	
	title_body = DIV(A(),_class='title_body')
	compose = URL(f='created_group_contact.html')
	title_body.append(A(SPAN(_class='glyphicon  glyphicon-edit'),T(' Thêm nhóm danh bạ'),_href=compose,_class='btn btn-primary'))
	
	title_body.append(A(SPAN(_class='glyphicon glyphicon-trash'),T(' Xóa'),_id='act_delete',_class='btn btn-primary'))
	# title_body.append(page())
	
	title_body.append(BUTTON(T(' Gửi tin nhắn'),_type='submit',_class='btn btn-primary', _style='margin-left:15px;'))
	
	scr ='''
	<script type="text/javascript">
	function hideMessage() {
			$(".ivinh_mesage").remove();
		}
	$("#act_delete").click(function () {
		if($('.list-gr input:checkbox').is(':checked')) {
			
				ajax('%s', ['check_box_select'], 'ivinh_wrap_content');
			}
		else{
				$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Chưa chọn nhóm để xóa.</b></div>" );
				window.setTimeout("hideMessage()", 3000);
			}
	});
		
	</script>
	'''%(URL(f='delete_group_contact',vars=dict(f_from=request.function)))
	title_body.append(XML(scr))
	
	
	body.append(DIV(title_body,_id='title_list',_class='list-group-item'))
	content = TABLE(THEAD(TR(TH(INPUT(_type="checkbox",_name='check_box_select_all',_id='ivinh_check_all'),_style=" width: 26px; "),TH('STT',_style=" width: 50px; text-align: center; "),TH('Tên'),TH('Đơn vị'),TH('Người dùng thuộc nhóm'),_class='title_top')),_class='table',_id='paging')
		
	PhoneBook().define_group_phonebook()
	PhoneBook().define_phonebook()
	rows = db(db.group_phonebook.id>0).select(orderby=db.group_phonebook.name)
	i = 1
	for row in rows:
		compose = 'window.open("%s","%s","width=1200,height=550,toolbar=no,location=no,directories=no,status=no,menubar=no,left=600,top=0")'%(URL(f='compose.html',vars=dict(to=row.description)),T('Compose'))
		pull_left = DIV(INPUT(_type="checkbox",_name='check_box_select',_value=row.id),_class='list-gr')
		
		read_contact=URL(r=request,c='plugin_sms',f='read_group_contact.html',args=['contact',row.id],vars=request.vars)
		
		list_contact =''
		if row.contact:
			rowcs = db(db.phonebook.id.belongs(row.contact)).select()
			for rc in rowcs:
				list_contact+= rc.name + ', '
			list_contact = list_contact[0:len(list_contact)-2]
		tr = TR(TD(pull_left),TD(i,_style=" width: 50px; text-align: center; "),TD(A(row['name'],_href=read_contact)),TD(row['org'] or ''),TD(list_contact))
		content.append(tr)
		i+=1
	body.append(content)
	div.append(body)
	scr ='''
	<script type="text/javascript">
		$(document).ready(function(){
			$('#ivinh_check_all').click(function(){
				if ($(this).is(':checked')) {
					$(".list-gr").find('input:checkbox').attr('checked', true);
				}
				else{
					$(".list-gr").find('input:checkbox').attr('checked', false);
				}
			   
			});
		});
	</script>
	'''
	div.append(XML(scr))
	div = form = FORM(div,_action=URL(f='create2',args=['group_phonebook'], vars=request.vars))
	if request.extension =='load':
		return div
	else:
		response.view = 'plugin_sms/content.%s'%request.extension
		return dict(content=div)
			
def created_group_contact():
	PhoneBook().define_group_phonebook()
	div = DIV(_class="panel panel-default read")
	group_contact = URL(f='group_contact.html')
	h3 = H3(A('',_class='glyphicon glyphicon-step-backward',_href=group_contact),B(' Tạo nhóm danh bạ'),_class="panel-title")
	div.append(DIV(h3,_class="panel-heading"))
	body = DIV(_class='panel-body')
	from gluon.tools import Crud
	crud = Crud(db)
	db.group_phonebook.contact.writable = False
	db.group_phonebook.contact.readable = False

	form =  crud.create(db.group_phonebook)
	if form.process().accepted:
		scr ='''
		<script type="text/javascript">
		function hideMessage() {
				$(".ivinh_mesage").remove();
			}
		$(document).ready(function(){
			$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Thêm mới thành công.</b></div>" );
			window.setTimeout("hideMessage()", 2000);
		});
			
		</script>
		'''
		body.append(XML(scr))
	body.append(DIV(form,_id='read_group_contact'))
	div.append(body)
	if request.extension =='load':
		return div
	else:
		response.view = 'plugin_sms/content.%s'%request.extension
		return dict(content=div)

def read_group_contact():
	PhoneBook().define_group_phonebook()
	row = db(db.group_phonebook.id==request.args(1)).select().first()
	
	div = DIV(_class="panel panel-default read")
	group_contact = URL(f='group_contact.html')
	h3 = H3(A('',_class='glyphicon glyphicon-step-backward',_href=group_contact),B(row.name),_class="panel-title")
	div.append(DIV(h3,_class="panel-heading"))
	body = DIV(_class='panel-body')
	from gluon.tools import Crud
	crud = Crud(db)
	db.group_phonebook.contact.writable = False
	db.group_phonebook.contact.readable = False
	form =  crud.update(db.group_phonebook,request.args(1))
	if form.process().accepted:
		scr ='''
		<script type="text/javascript">
		function hideMessage() {
				$(".ivinh_mesage").remove();
			}
		$(document).ready(function(){
			$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Cập nhật thành công.</b></div>" );
			window.setTimeout("hideMessage()", 2000);
		});
			
		</script>
		'''
		body.append(XML(scr))
	body.append(DIV(form,_id='read_contact'))
	
	PhoneBook().define_phonebook()
	rows = db(db.phonebook.id>0).select()
	
	
	ul = TABLE(THEAD(TR(TH('STT'),TH(''),TH('Tên'),TH('Cơ quan'),TH('Số điện thoại'))),_class='table')
	ajax = ''
	#print request.args(1)
	i = 1
	for r in rows:
		tr = TR(TD(i))
		ajax = 'ajax("%s", ["check_box_contact"], "")'%(URL(f='add_contactto_group',vars=dict(cid=r.id, grid= row.id)))
		if row.contact!=None:
			if r.id in row.contact:
				tr.append(TD(INPUT(_type='checkbox',_onclick=ajax, _checked='CHECKED')))
			else:
				tr.append(TD(INPUT(_type='checkbox',_onclick=ajax)))
		else:
			tr.append(TD(INPUT(_type='checkbox',_onclick=ajax)))
		tr.append(TD(r.name))
		tr.append(TD(r.org))
		tr.append(TD(r.phone))
		ul.append(tr)
		i+=1
	div.append(body)
	
	h3 = H3(B('Danh sách người thuộc nhóm'),_class="panel-title")
	div.append(DIV(h3,_class="panel-heading"))
	div.append(ul)
	if request.extension =='load':
		return div
	else:
		response.view = 'plugin_sms/content.%s'%request.extension
		return dict(content=div)

def delete_group_contact():
	list_check = request.vars.check_box_select
	if isinstance(list_check,str): list_check = [list_check]
	list_check = [int(uid) for uid in list_check]
	PhoneBook().delete_group_contact(list_check )
	f = request.vars.f_from.split('.')[0]
	div = DIV(LOAD(f='%s.load'%f))
	scr ='''<script type="text/javascript">
		function hideMessage() {
			$(".ivinh_mesage").remove();
		}
		$(document).ready(function(){
			$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Xóa thành công %s nhóm danh bạ.</b></div>" );
			window.setTimeout("hideMessage()", 2000);
		});
	</script>'''%(len(request.vars.check_box_select))
	div.append(XML(scr))
	return div		

def add_contactto_group():
	cid = int(request.vars.cid)
	grid = request.vars.grid
	
	PhoneBook().define_group_phonebook()
	group = db.group_phonebook(grid)
	#print group,grid
	list_contact = group.contact if group.contact!= None else []
	if cid in list_contact: list_contact.remove(cid)
	else: list_contact.append(cid)
	#update
	db(db.group_phonebook.id==grid).update(contact=list_contact)
	redirect(URL(f='read_group_contact',args=['contact', grid]))
	
	
def logout():
	session.password = None
	redirect(URL(f='user.html'))
	
def act_send():
	receives = request.vars.send_to or ''
	if receives[-1]==' ': receives = receives[:-1]
	if receives[-1]==',': receives = receives[:-1]
	content = request.vars.send_content or ''
	publish = request.vars.publish or request.now
	sms.add(db.auth_user(auth.user_id).username,receives,content,publish)
	return 1

def remove_htmltag(text):
	import re
	x = re.compile(r'<[^<]*?/?>')
	tmp = x.sub('', text)
	return tmp	
	
def get_short_string(text, length, display_order=0):
	tmp = remove_htmltag(text)
	if display_order>0:
		n = tmp[display_order-1:].find(' ')
		tmp = '...'+tmp[n+1:]
	if length>=len(tmp): return tmp
	n = tmp[:length-1].rfind(' ')
	tmp = tmp[:n]
	return tmp[:n] + '...'
	
def act_delete():
	list_check = request.vars.check_box_select
	if isinstance(list_check,str): list_check = [list_check]
	list_check = [int(uid) for uid in list_check]
	f = request.vars.f_from.split('.')[0]
	if f == 'inbox':
		sms.delete(list_check)
	elif f== 'detail': 
		sms.delete_log(list_check)
	
	div = DIV(LOAD(f='%s.load'%f))
	scr ='''<script type="text/javascript">
		function hideMessage() {
			$(".ivinh_mesage").remove();
		}
		$(document).ready(function(){
			$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Xóa thành công %s tin nhắn.</b></div>" );
			window.setTimeout("hideMessage()", 2000);
		});
	</script>'''%(len(list_check))
	div.append(XML(scr))
	return div
	
	
def page():
	length = int(request.vars.length or 30)
	page = int(request.vars.page or 0)
	vars = {}
	for key in request.vars.keys(): vars[key] = request.vars[key]
	vars['page'] = page + 1
	ajax = "ajax('%s', [], 'ivinh_wrap_content')"%(URL(args=request.args,vars=vars,extension='load'))
	next = A(SPAN(_class='glyphicon glyphicon-chevron-right'),_onclick=ajax,_id='next',_class="btn btn-inverse")
	vars['page'] = page - 1 if page > 1 else 0
	ajax = "ajax('%s', [], 'ivinh_wrap_content')"%(URL(args=request.args,vars=vars,extension='load'))
	prev = A(SPAN(_class='glyphicon glyphicon-chevron-left'),_onclick=ajax,_id='prev',_class="btn btn-inverse")
	div = DIV(prev, next, _id='page',_class='event_page')
	return div	
	
def menu_top():
	title_body = DIV(_class='title_body')
	compose = 'window.open("%s","%s","width=1200,height=550,toolbar=no,location=no,directories=no,status=no,menubar=no,left=600,top=0")'%(URL(f='compose.html'),T('Compose'))
	title_body.append(A(SPAN(_class='glyphicon  glyphicon-edit'),T(' Soạn tin'),_onclick=compose,_class='btn btn-primary'))
	title_body.append(A(SPAN(_class='glyphicon glyphicon-trash'),T(' Xóa'),_id='act_delete',_class='btn btn-primary'))
	# title_body.append(page()) ##2 Nút tiến lùi trong phân trang
	scr ='''
	<script type="text/javascript">
	function hideMessage() {
			$(".ivinh_mesage").remove();
		}
	$("#act_delete").click(function () {
		if($('.list-group input:checkbox').is(':checked')) {
			var r=confirm("Bạn thực sự muốn xóa?");
			if (r==true)
			{
				ajax('%s', ['check_box_select'], 'ivinh_wrap_content');
			}
		
			}
		else{
				$("#ivinh_wrap_alert").append( "<div class='ivinh_mesage'> <b>Chưa chọn tin nhắn để xóa.</b></div>" );
				window.setTimeout("hideMessage()", 3000);
			
			}
	});
		
	</script>
	'''%(URL(f='act_delete',vars=dict(f_from=request.function)))
	title_body.append(XML(scr))
	return title_body
	
def get_items():
	itms = []
	if request.vars.q and request.vars.table and request.vars.field:
		q = request.vars.q
		f = request.vars.field
		t = request.vars.table
		query =(db.auth_user.last_name.upper().like('%'+q.upper()+"%"))|(db.auth_user.first_name.upper().like('%'+q.upper()+"%"))
		rows = db(query).select(distinct=True) 
		itms = [str(t['last_name']) for t in rows]
	return '\n'.join(itms)

def list_email():
	max_rows = request.vars.maxRows
	key_search = request.vars.name_startsWith
	emails = []
	PhoneBook().define_phonebook()
	contacts = db((db.phonebook.phone.upper().like('%'+key_search+"%"))|(db.phonebook.name.upper().like('%'+key_search+"%"))).select()
	for row in contacts:
		cont = {"name":row.name,'phone':row.phone}
		emails.append(cont)
	return dict(add_email=emails)
	
def search_user():
	div = DIV()
	div.append(INPUT(_name='key_user',_id='key_user',_autocomplete="off",_class="string ac_input input-email"))
	div.append(BUTTON(SPAN(_class="glyphicon glyphicon-user"),_type="submit",_class="btn btn-primary",_id='btn_send'))
	list_email = URL(c='plugin_sms',f='list_email.json')
	scr ='''
	<script>
	$(function() {
		function split( val ) {
			return val.split( /,\s*/ );
		}
		function extractLast( term ) {
			return split( term ).pop();
		}
		var url_search = "%s";
		$( "#key_user" ).autocomplete({
			source: function( request, response ) {
			
				$.ajax({
					url: url_search,
					dataType: "json",
					data: {
						maxRows: 15,
						name_startsWith: extractLast( request.term )
					},
					success: function(data) {
						response( $.map( data.add_email, function( item ) {
							return {
								label: item.name + ' <'+item.phone +'>',
								value: item.name + ' <'+item.phone +'>'
							}
						}));
					}

				});
			},
			minLength: 0,
			select: function( event, ui ) {
				var terms = split( this.value );
					terms.pop();
					terms.push( ui.item.value );
					terms.push( "" );
					this.value = terms.join( ", " );
					return false;
			},
		});
		
		
	});

	</script>'''%(list_email)
	
	div.append(XML(scr))
	return dict(content=div)
		
####Hiển thị Log đăng nhập
def log_event():
	import datetime
	divp = DIV(_class='panel panel-primary')
	divhd = DIV('Lịch sử sử dụng hệ thống',_class='panel-heading')
	divbd = DIV(_class='panel-body')
	divp.append(divhd)
	
	table = TABLE(_class='table',_id='paging')
	table.append(THEAD(TR(TD('STT'),TD('UserID'),TD('IP Address'),TD('Time stamp'),TD('Decription'))))
	i = 1
	rows = db(db.auth_event.id>0).select(orderby=~db.auth_event.id)
	for r in rows:
		tr = TR(i)
		tr.append(TD(r.user_id))
		tr.append(TD(r.client_ip))
		tr.append(TD(r.time_stamp.strftime('%H:%M %d-%m-%Y') if r.time_stamp else ''))
		tr.append(TD(r.description))
		table.append(tr)
		i+=1
	divbd.append(table)
	divp.append(divbd)
	response.view ='plugin_sms/content.html'
	return dict(content = divp)
	
####################################
##Màn hình danh sách tin nhắn
def list_sms():
	content = sms.list_sms()	
	return dict(content = content)
	
##Tìm kiếm tin nhắn
def search_sms():
	page = request.vars.page if request.vars.page else 1
	user = request.vars.user if request.vars.user else '0'
	receives = request.vars.receives if request.vars.receives else '0'
	content = request.vars.content if request.vars.content else ''
	startdate = request.vars.startdate if request.vars.startdate else None
	enddate = request.vars.enddate if request.vars.enddate else None
	content = sms.write_sms(user,receives,content,startdate,enddate,page)
	return content
	
##############################
##Biểu đồ số lượng tin nhắn trong 12 tháng
def chart_sms_month():
	SMS().define_sms()
	rows = db(db.sms.id>0).select()
	today = request.now
	nowmonth = request.now.month
	
	
	list_thang = [1,2,3,4,5,6,7,8,9,10,11,12]
	spm = list_thang.index(nowmonth) ##Xác định vị trí của tháng hiện tại trong list
	list2 = list_thang[0:spm+1] ##Cắt list thành 2 list
	list1 = list_thang[spm+1:len(list_thang)] 
	list_month = list1 +list2 ##nối 2 list lại với nhau (Lấy danh sách 12 tháng trong tròn 1 năm)
	print list_month,92
	div = DIV(_style='display:none;')
	i = 1
	for t in list_month:
		nowyear = request.now.year
		nowy = request.now.year
		if t>nowmonth:
			nowy = nowyear - 1 
		dt = today.replace(day=1, month=t,year=nowy)
		if(t==2):
			ct = today.replace(day=28,month=t,year=nowy)
		elif((t==4)|(t==6)|(t==9)|(t==11)):
			ct = today.replace(day=30,month=t,year=nowy)
		else:
			ct = today.replace(day=31,month=t,year=nowy)
		co = db((db.sms.publish>dt)&(db.sms.publish<ct)).count()
		p = P(co)
		span = SPAN(str(t) +'/'+str(nowy))
		divm = DIV(p,span,_id='month'+str(i))
		div.append(divm)
		i+=1
	return dict(content=div)
	
	
	