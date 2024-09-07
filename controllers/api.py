# -*- coding: utf-8 -*-

from plugin_cms import Cms
cms = Cms()


@service.jsonrpc
@service.jsonrpc2
def add(a, b):
    return (a + b)*2
	
@service.jsonrpc
@service.jsonrpc2
def Get_ResultByLABCONN(ngaychidinh,sid,stt,mabenhnhan,mayte,sophieuyeucau,tenbenhnhan,diachi,namsinh,gioitinh,chandoan,tendoituong,tennoichidinh,tenbacsi,maxetnghiem,tenxetnghiem,ketqua,chisobinhthuong,donvi,batthuong,tennhomxn,thutunhomxn,sdt):
	# from plugin_cms import CmsModel
	# cms = CmsModel()
	import time
	db = cms.db
	ket_qua = cms.define_table('ket_qua')
	chi_tiet = cms.define_table('chi_tiet')
	check_ket_qua = db(ket_qua.sid==sid).select()
	if not time.strptime(ngaychidinh,"%Y-%m-%d %H:%M:%S"): return 'Ngay chi dinh khong dung dinh dang'
	try:
		if len(check_ket_qua)>0:
			db(ket_qua.sid==sid).update(ngaychidinh=ngaychidinh,
				stt=stt,
				mabenhnhan=mabenhnhan,
				mayte=mayte,
				tenbenhnhan=tenbenhnhan,
				diachi=diachi,
				namsinh=namsinh,
				gioitinh=gioitinh,
				chandoan=chandoan,
				tendoituong=tendoituong,
				tennoichidinh=tennoichidinh,
				tenbacsi=tenbacsi,
				sdt=sdt)
		else:
			db.ket_qua.insert(ngaychidinh=ngaychidinh,
				sid=sid,
				stt=stt,
				mabenhnhan=mabenhnhan,
				mayte=mayte,
				tenbenhnhan=tenbenhnhan,
				diachi=diachi,
				namsinh=namsinh,
				gioitinh=gioitinh,
				chandoan=chandoan,
				tendoituong=tendoituong,
				tennoichidinh=tennoichidinh,
				tenbacsi=tenbacsi,
				sdt=sdt)
			
		check_chi_tiet = db((chi_tiet.sid==sid)&(chi_tiet.maxetnghiem==maxetnghiem)).select()
		if len(check_chi_tiet)>0:
			db((chi_tiet.sid==sid)&(chi_tiet.maxetnghiem==maxetnghiem)).update(
				sophieuyeucau=sophieuyeucau,
				tenxetnghiem=tenxetnghiem,
				ketqua=ketqua,
				chisobinhthong=chisobinhthuong,
				donvi=donvi,
				batthuong=batthuong,
				tennhomxn=tennhomxn,
				thutunhomxn=thutunhomxn)
		else:
			db.chi_tiet.insert(sid=sid,
				maxetnghiem=maxetnghiem,
				sophieuyeucau=sophieuyeucau,
				tenxetnghiem=tenxetnghiem,
				ketqua=ketqua,
				chisobinhthong=chisobinhthuong,
				donvi=donvi,
				batthuong=batthuong,
				tennhomxn=tennhomxn,
				thutunhomxn=thutunhomxn)
		return True
	except Exception,e: return False
	
# @auth.requires_login()
def call():
    return service()
	
def get_data():
	from datetime import datetime

	ngaychidinh = datetime.strptime(request.vars.date_lay, '%d/%m/%Y')
	mabenhnhan = request.vars.sid
	ma_xac_nhan = request.vars.ma_xac_nhan
	
	db = cms.db
	ket_qua = cms.define_table('ket_qua')
	chi_tiet = cms.define_table('chi_tiet')
	
	check_ket_qua = db((ket_qua.mabenhnhan==mabenhnhan)&(ket_qua.ngaychidinh==ngaychidinh)).select().first()
	if check_ket_qua:
		div = DIV(_class='get_data')
		if check_ket_qua.code_sms == ma_xac_nhan:
			div.append(H2('Phiếu kết quả xét nghiệm'))
			table = TABLE(_class='table')
			table.append(TR(TD("Bệnh nhân:"),TD(B(check_ket_qua.tenbenhnhan)),TD("Năm sinh"),TD(B(check_ket_qua.namsinh))))
			table.append(TR(TD("Địa chỉ:"),TD(B(check_ket_qua.diachi),_colspan=3)))
			table.append(TR(TD("Mã bệnh nhân:"),TD(B(check_ket_qua.mabenhnhan)),TD("Mã y tế"),TD(B(check_ket_qua.mayte))))
			div.append(table)
			div.append(H3("Kết quả"))
			
			rows = db((chi_tiet.sid==check_ket_qua.sid)).select()
			
			table = TABLE(_class='table')
			table.append(TR(TH("Nhóm xét nghiệm"),TH("Tên xét nghiệm"),TH("Kết quả"),TH("Chỉ số bình thường"),TH("Đơn vị"),TH("Bất thường")))
			for row in rows:
				batthuong = row.batthuong
				if row.batthuong:
					batthuong="Có"
				else:
					batthuong="Không"
				table.append(TR(TD(row.tennhomxn),TD(row.tenxetnghiem),TD(row.ketqua),TD(row.chisobinhthong),TD(row.donvi),TD(batthuong)))
			
			div.append(table)
		else:
			div.append(P("Mã xác nhận không đúng, vui lòng kiểm tra lại"))
		return div
	else:
		return "Không có kết quả phù hợp"
		
def check_send_sms():
	
	from datetime import datetime
	import uuid
	if  request.vars.sid =="":
		return  'Chưa nhập mã bệnh nhân.' 
	if  request.vars.date_lay =="":
		return  'Chưa nhập ngày chỉ định.' 
	
	ngaychidinh = datetime.strptime(request.vars.date_lay, '%d/%m/%Y')
	mabenhnhan = "821502." + request.vars.sid
	
	db = cms.db
	ket_qua = cms.define_table('ket_qua')
	chi_tiet = cms.define_table('chi_tiet')
	
	check_ket_qua = db((ket_qua.mabenhnhan==mabenhnhan)&(ket_qua.ngaychidinh==ngaychidinh)).select().first()
	try:
		if check_ket_qua:
			div = DIV(_class='col-md-12 col-xs-12 text-center margin-mid-5')
			if check_ket_qua.code_sms =="":
				uuid= str(uuid.uuid1().int)
				
				import requests
				from datatables import define_sms_vnpt,define_sms_medic
				from plugin_process import ProcessModel
				sms_vnpt = define_sms_vnpt(db, False)
				r_vnpt = db.sms_vnpt[2]
				url = r_vnpt.url_port
				headers = {'Content-Type':'application/json'}	
				body  = { "RQST": {   
					"name": "send_sms_list",
					"REQID": r_vnpt.reqid ,
					"LABELID": r_vnpt.labelid,
					"CONTRACTTYPEID": r_vnpt.contracttypeid,
					"CONTRACTID":r_vnpt.contractid,
					"TEMPLATEID": r_vnpt.templateid,	
					"PARAMS": [{"NUM":"1","CONTENT":uuid[0:6]}],		
					"SCHEDULETIME": r_vnpt.scheduletime if r_vnpt.scheduletime else "",
					"MOBILELIST": '84916235221',	
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
				if a['RPLY']['ERROR']=='0':
					db((ket_qua.mabenhnhan==mabenhnhan)&(ket_qua.ngaychidinh==ngaychidinh)).update(code_sms=uuid[0:6])
					div.append(P("Đã gửi mã xác nhận. Vui lòng kiểm tra số điện thoại bạn đã đăng ký khám bệnh để lấy mã."))
					ajax = "ajax('%s', ['sid','date_lay','ma_xac_nhan'], 'wr_ket_qua')"%(URL(c='api',f='get_data'))
					div.append(A("Xem kết quả",_class='btn btn-success',_onclick=ajax,_id="xemketqua"))
				else:
					div.append(P("Hệ thống gửi tin lỗi. Vui lòng liên hệ bộ phận CSKH để kiểm tra kết quả."))
				
				
			else:
				div.append(P("Bạn đã có mã xác nhận, vui lòng kiểm tra lại tin nhắn và nhập mã."))
				ajax = "ajax('%s', ['sid','date_lay','ma_xac_nhan'], 'wr_ket_qua')"%(URL(c='api',f='get_data'))
				div.append(A("Xem kết quả",_class='btn btn-success',_onclick=ajax,_id="xemketqua"))
			return div
		else: return'Chưa có kết quả xét nghiệm'
	
	except Exception,e: return e


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