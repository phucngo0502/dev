# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 13/11/2013
###################################################
from html import *
from gluon import current
from gluon.dal import Field
import re


class MEDIC_SMS():
	
	def send_now(self,id,params,mobilelist):
		db = current.globalenv.get('db')
		from plugin_cms import Cms
		cms = Cms()
		sms_vnpt = cms.define_table('sms_vnpt',False)
		sms_medic = cms.define_table('sms_medic',False)
		r_vnpt = db.sms_vnpt[id]
		mobilelist = self.convert_vn(mobilelist)
		if r_vnpt:
			import requests
			url = r_vnpt.url_port
			headers = {'Content-Type':'application/json'}	
			body  = { "RQST": {   
				"name": "send_sms_list",
				"REQID": r_vnpt.reqid ,
				"LABELID": r_vnpt.labelid,
				"CONTRACTTYPEID": r_vnpt.contracttypeid,
				"CONTRACTID":r_vnpt.contractid,
				"TEMPLATEID": r_vnpt.templateid,	
				"PARAMS": params,		
				"SCHEDULETIME": r_vnpt.scheduletime if r_vnpt.scheduletime else "",
				"MOBILELIST": mobilelist,	
				"ISTELCOSUB": r_vnpt.istelcosub,
				"AGENTID":r_vnpt.agentid,
				"APIUSER": r_vnpt.apiuser,
				"APIPASS": r_vnpt.apipass,
				"USERNAME":r_vnpt.username,
				"DATACODING":r_vnpt.datacoding
				}		
			}
			a = requests.post(url,headers=headers, json=body).json()
			return a
		else:
			return 'Id VNPT error'
			
	def send(self,id,name,params,mobilelist,send_end=None):
		db = current.globalenv.get('db')
		from plugin_cms import Cms
		cms = Cms()
		sms_vnpt = cms.define_table('sms_vnpt',False)
		sms_medic = cms.define_table('sms_medic',False)
		rows_vnpt = db.sms_vnpt[id]
		mobilelist = self.convert_vn(mobilelist)
		if rows_vnpt:
			db.sms_medic.insert(sms_vnpt=id, name=name,params=params,mobilelist=mobilelist,send_end=send_end,created_on=current.request.now)
			return "Tạo lệnh gửi tin thành công."
		else:
			return 'Id VNPT error'
			
	def send_return (self,id,status,error,error_name,error_desc):
		db = current.globalenv.get('db')
		from plugin_cms import Cms
		cms = Cms()
		sms_medic = cms.define_table('sms_medic',False)
		if status!='':
			db(sms_medic.id==id).update(status=status,error=error,error_name=error_name,error_desc=error_desc)
		else:
			db(sms_medic.id==id).update(error=error,error_name=error_name,error_desc=error_desc)
		return True
		
	def convert_vn(self,numbers):
		numbers = numbers.replace(' ','').replace('+','').replace('.','').replace(',','')
		dau_so = numbers[0:1]
		if dau_so =='0':
			return '84%s'%(numbers[1:len(numbers)])
		else:
			return numbers
		
class SMS():
	def __init__(self, **attr):
		self.db = attr.get('db',current.globalenv['db'])
		
		
	def define_sms_category(self,migrate=True):
		if 'sms_category' in self.db.tables: return self.db.sms_category 
		return self.db.define_table('sms_category',
			Field('name'),
			migrate=migrate)	
			
	def define_sms(self,migrate=False):
		if 'sms' in self.db.tables: return self.db.sms 
		self.define_sms_category()
		return self.db.define_table('sms',
			Field('sms_category','reference sms_category'),
			Field('is_user'),
			Field('receives','text'),
			Field('is_content'),
			Field('status',default='unread'),
			Field('publish','datetime'),
			Field('created',default='sms'),
			migrate=migrate)
	
	def define_log(self,migrate=False):
		if 'sms_log' in self.db.tables: return self.db.sms_log 
		return self.db.define_table('sms_log',
			Field('sms','integer'),
			Field('phone'),
			Field('sent'),
			Field('status',default='queue'),
			Field('publish','datetime'),
			migrate=migrate)
			
	def add(self,user,receives,content,publish,created='sms',log=True,sms_category=None):
		sms = self.define_sms()
		id = sms.insert(sms_category=sms_category,is_user=user,receives=receives,is_content=content,publish=publish,created=created)
		if log:
			phones = re.findall(r'(?:\d{11}|\d{10})', receives)
			for phone in phones: 
				self.addlog(id,phone)
		return id

	def addlog(self,sms,phone,sent=None):
		log = self.define_log()
		return log.insert(sms=sms,phone=phone,sent=sent)
			
	def update(self,id,status='sent'):
		sms = self.define_sms()
		return self.db(sms.id==id).update(status=status)

	def delete(self,list_id,log=True):
		sms = self.define_sms()
		if log:
			log = self.define_log()
			self.db(log.sms.belongs(list_id)).delete()
		self.db(sms.id.belongs(list_id)).delete()

	def delete_log(self,list_id):
		log = self.define_log()
		id = log[list_id[0]].sms
		self.db(log.id.belongs(list_id)).delete()
		if self.db(log.sms==id).count()==0: 
			sms = self.define_sms()
			self.db(sms.id==id).delete()
		
	def get_log(self,id):
		log = self.define_log()
		return self.db(log.sms==id).select()
		
	def get(self,status=None,orderby=None,limitby=None,user=None,phone=None,content=None,publish_start=None,publish_end=None):
		t = self.define_sms()
		request = current.request
		if not status: status = request.vars.status
		query = (t.status==status) if status else (t.id>0)
		if user: query &= (t.is_user==user)
		if phone: query &= t.is_content.contains(phone)
		if publish_start: query &= (t.publish>=publish_start)
		if publish_end: query &= (t.publish<=publish_end)
		if content: query &= t.is_content.contains(content)

		if not limitby:
			length = int(request.vars.length or 30)
			page = int(request.vars.page or 0)
			limitby=(page*length,(page+1)*length)
		if not orderby:
			field = request.vars.orderby or 'id'
			orderby=t[field] if request.vars.asc=='asc' else ~t[field]
			
		# return self.db(query).select(orderby=orderby,limitby=limitby)
		return self.db(query).select(orderby=orderby) ##Không phân trang
		
	def receives(self,txt):	
		tmp = re.findall(r'<(?:\d{10}|\d{11})>', txt)
		for s in tmp: txt = txt.replace(s,'')
		return txt
		
	################################
	##Màn hình danh sách tin nhắn
	def list_sms(self):
		db = self.db
		t = self.define_sms()
		request = current.request
		PhoneBook().define_phonebook()
		
		table = TABLE(_class='table table-striple')
		#Danh sách người gửi
		inpusersend =  SELECT(OPTION('--Chọn người gửi --',_value='0'),_class="form-control tags",_name='is_user',_style="")
		rowuser = db(db.auth_user.id>0).select()
		for r in rowuser:
			op = OPTION(SPAN(r.first_name),_value=r.username)
			inpusersend.append(op)
		##Danh sách người nhận
		inpreceived =  SELECT(OPTION('--Chọn người nhận --',_value='0'),_class="form-control tags",_name='receives',_style="")
		rowpb = db(db.phonebook.id>0).select()
		for r in rowpb:
			op = OPTION(r.name,_value=r.name)
			inpreceived.append(op)
		##Nội dung tin nhắn
		inpcontent = INPUT(_type='text',_name='is_content',_class='form-control')
		##Thời gian gửi
		inpstartdate = INPUT(_type='text',_name='startdate',_class='form-control datetime')
		inpenddate = INPUT(_type='text',_name='enddate',_class='form-control datetime')
		
		table.append(TR(TD('Người gửi'),TD(inpusersend),TD('Người nhận'),TD(inpreceived)))
		table.append(TR(TD('Thời gian từ'),TD(inpstartdate),TD('Đến'),TD(inpenddate)))
		table.append(TR(TD('Nội dung tin nhắn'),TD(inpcontent,_colspan='3')))
		
		url = URL(r=request, c='plugin_sms', f='search_sms')
		ajax = "ajax('%s', ['is_user','receives','is_content','startdate','enddate'], 'content_sms')"%(url)
		btnsearch = INPUT(_type='button',_id='btn-firstcl',_value='Tìm kiếm',_class='btn btn-primary',_onClick=ajax)
		divhd = DIV(_style="margin-bottom:30px;background:#fff;padding:0px 5px;")
		
		divhd.append(table)
		divhd.append(DIV(btnsearch,_style='margin:10px 0px;'))
		script_cl = SCRIPT('''$('#btn-firstcl').click();''')
		divhd.append(script_cl)
		divhd.append(DIV(self.write_sms('','','',request.now.strftime('%d/%m/%Y %H:%M:%S'),request.now.strftime('%d/%m/%Y %H:%M:%S'),0),_id='content_sms'))
		
		return divhd
		
	def write_sms(self,user,receives,content,startdate,enddate,page):
		t = self.define_sms()
		request = current.request
		import datetime
		query = t.id>0
		if user!='0':
			query&=(t.is_user==user)
		if receives!='0':
			query&=(t.receives.like('%'+receives+'%'))
		if (content!=''):
			query&= (t.is_content.like('%'+content+'%'))
		input,output = "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"
		if (startdate!=None)&(enddate!=None):
			# timestart= datetime.datetime.strptime(startdate,input).strftime(output)
			# timeend = datetime.datetime.strptime(enddate,input).strftime(output)
			query&=(t.publish>=startdate)&(t.publish<enddate)
		###Phân trang
		LEN_PAGE = 20
		start = 0
		end = 20
		page = int(page)
		if (page!=0):
			end = page*LEN_PAGE
			start = end-LEN_PAGE
		len = self.db(query).count()
		numbers = (len/LEN_PAGE)+1
		ul = UL(_class='page-ul pagination')
		i=1
		vars = request.vars
		while i<=numbers:
			vars['page']=i
			url = URL(r=request, vars=vars)
			ajax = "ajax('%s',[],'table_sms')"%(url)
			if (i-page<15):
				if i==page:
					ul.append(LI(A(i,_onClick=ajax),_class='active'))
				else:
					ul.append(LI(A(i,_onClick=ajax)))			
			i+=1			
		rows = self.db(query).select(orderby=~t.id,limitby=(start,end))
		table = self.write_table_sms(rows)
		div = DIV(_id='table_sms')
		div.append(table)
		div.append(ul)
		return div
		
	
	def write_table_sms(self,rows):
		table = TABLE(_class='table table-striple')
		table.append(THEAD(TR(TH('STT'),TH('Người gửi'),TH('Người nhận'),TH('Nội dung tin nhắn'),TH('Thời gian nhận'))))
		i = 1
		for r in rows:
			tr = TR(i)
			tr.append(TD(r.is_user))
			tr.append(TD(r.receives))
			tr.append(TD(r.is_content))
			tr.append(TD(r.publish))
			i+=1
			table.append(tr)
		return table
		
class PhoneBook():
	def __init__(self, **attr):
		self.db = attr.get('db',current.globalenv['db'])

	def define_group_phonebook(self,migrate=False):
		T = current.T
		if 'group_phonebook' in self.db.tables: return self.db.group_phonebook 
		return self.db.define_table('group_phonebook',
			Field('name',label=T('group_phonebook name')),
			Field('org',label=T('group_phonebook org')),
			Field('email',label=T('group_phonebook email')),
			Field('description','text',label=T('group_phonebook description')),
			Field('contact','list:integer',label=T('group_phonebook contact')),
			migrate=migrate)
		
	def define_phonebook(self,migrate=False):
		if 'phonebook' in self.db.tables: return self.db.phonebook 
		T = current.T
		return self.db.define_table('phonebook',
			Field('name',label=T('phonebook name')),
			Field('org',label=T('phonebook org')),
			Field('email',label=T('phonebook email')),
			Field('phone','text',label=T('phonebook phone')),
			migrate=migrate)
			
	def get_phone(self,email):
		pb = self.define_phonebook()
		row = self.db(pb.email==email).select().first()
		return row.phone if row else None
		
	def get_name(self,email):
		pb = self.define_phonebook()
		row = self.db(pb.email==email).select().first()
		return row.name if row else email
		
	def get_name_by_phone(self,phone):
		pb = self.define_phonebook()
		row = self.db(pb.phone==phone).select().first()
		return row.name if row else (str(phone)+' (Số chưa có trong danh bạ)')
	
	def add(self,name,email,phone):
		pb = self.define_phonebook()
		id = pk.insert(name=name,email=email,phone=phone)
		return id
		
	def update(self,id,name,email,phone):
		pb = self.define_phonebook()
		id = self.db(pk.id==id).update(name=name,email=email,phone=phone)
		return id
	
	def delete(self,list_id):
		pb = self.define_phonebook()
		self.db(pb.id.belongs(list_id)).delete()	
	
	def delete_group_contact(self, list_id):
		gr = self.define_group_phonebook()
		self.db(gr.id.belongs(list_id)).delete()
			
def get_short_string(text, length, display_order=0):
	tmp = text
	if display_order>0:
		n = tmp[display_order-1:].find(' ')
		tmp = '...'+tmp[n+1:]
	if length>=len(tmp): return tmp
	n = tmp[:length-1].rfind(' ')
	tmp = tmp[:n]
	return tmp[:n] + '...' 