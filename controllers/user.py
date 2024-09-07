# -*- coding: utf-8 -*-

from plugin_cms import Cms
cms = Cms()


#@cache(request.env.path_info, time_expire=3600, cache_model=cache.ram)
def calendar():
	try:
		response.view = 'layout/lich2/%s'%(cms.layout_folder() or 'index.html')
	except:
		response.view = 'layout/trangchu.html'
	return response.render(dict())
	
def index():
	redirect(URL(f='folder',args=request.args))


# @cache(request.env.path_info, time_expire=3600, cache_model=cache.ram)
def folder():
	if request.args == []:
		redirect(URL(f='folder',args=['trang-chu']))
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
	
def search():
	dcontent = cms.define_table(tablename ='dcontent',migrate=True)
	txt = request.vars.key_search
	rows= cms.db(dcontent.textcontent.like('%'+str(txt)+'%')).select()
	
	div = DIV(_id='page_search')
	
	if len(rows)>0:
		div.append(H2(len(rows),T(' Kết quả tìm kiếm cho từ khóa: "'),request.vars.key_search,'"',_id='title_page'))
		ul=UL()
		for row in rows:
			code = '<i style=" background: yellow;">'+request.vars.key_search+'</i>'
			name =  row.name.replace(request.vars.key_search,code)

			name =  name.replace(request.vars.key_search.lower(),code)
			name =  name.replace(request.vars.key_search.upper(),code)
			li = LI(A(XML(name),_href=cms.url_content(row),_class='name'))
			description =  row.description.replace(request.vars.key_search,code)
			li.append(P(XML(description)))
			ul.append(li)
		div.append(ul)
	else:
		div.append(H2(T('Kết quả tìm kiếm từ khóa: "'),request.vars.key_search,'"',_id='title_page'))
		div.append(P(T('Không có kết quả nào cho từ khóa này.')))
		
	return div
	
def load_portlet():
	portlet_id = request.args(0)
	if portlet_id:
		return portlet.display(portlet_id)
	else: return ''
	
	
def get_html():
	# url = 'https://track.aftership.com/viettelpost/BRAVO10041606'
	# url = 'http://dantri.com.vn/'
	# url = 'http://hatinhtrade.com.vn/sgd/portal/folder/home'
	# import requests
	# # r = requests.post("http://www.viettelpost.com.vn/Default.aspx?tabid=208", data={'dnn$ctr2039$TrakingNumberWeb$TXT_TIMKIEM': 'BRAVO10041601'})
	# # return r.text
	
	# import httplib
	# data={}
	# httpServ = httplib.HTTPConnection("www.viettelpost.com.vn")
	# httpServ.connect()
	# httpServ.request('POST', '/Default.aspx?tabid=208',"'dnn$ctr2039$TrakingNumberWeb$TXT_TIMKIEM': 'BRAVO10041601','dnn$ctr2039$TrakingNumberWeb$cmd_timkiem':'Theo dõi'")

	# response = httpServ.getresponse()
	# return response.read()
	# # if response.status == httplib.OK:
		# # print "Output from CGI request"
		# # printText (response.read())

	# httpServ.close()
	
	import httplib, urllib
	params = urllib.urlencode({'dnn$ctr2039$TrakingNumberWeb$TXT_TIMKIEM': 'BRAVO10041601','dnn$ctr2039$TrakingNumberWeb$cmd_timkiem':'Theo dõi'})
	headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
	conn = httplib.HTTPConnection("www.viettelpost.com.vn")
	conn.request("POST", "/Default.aspx?tabid=208", params, headers)
	response = conn.getresponse()
	return response.read()
	
	

def printText(txt):
    lines = txt.split('\n')
    for line in lines:
        print line.strip()


	
def get_html1():
	import requests
	import http.client
	import urllib, urllib2, os
	from bs4 import BeautifulSoup
	id= 601
	j = 0
	ul = UL()
	while j <10:
		url = 'https://track.aftership.com/viettelpost/BRAVO10041%s'%(id)
		r = requests.get(url)
		
		soup = BeautifulSoup(r.text)
		
		i = 0
		for row in soup.findAll("div", {"class":"checkpoint__content"}):
			if i<1:
				ul.append(LI(B(id),row))
			else: break
		id +=1
		j+=1
		
	response.view = 'layout/get_html.html'
	return dict(content=ul)
	
	# import requests
	# id= request.args(0)
	# url = 'https://track.aftership.com/viettelpost/%s'%(id)
	# payload = {"dnn_ctr2039_TrakingNumberWeb_TXT_TIMKIEM":id}

	# r = requests.get("http://viettelpost.com.vn/Default.aspx?tabid=208")
	
	# return r.text
	
	# import urllib, urllib2, os
	# from bs4 import BeautifulSoup
	# url = 'http://www.viettelpost.com.vn/default.aspx?tabid=208'
	# import http.client
	# import re

	# # specify we're sending parameters that are url encoded
	# headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }

	# # our parameters
	# params = {"dnn$ctr2039$TrakingNumberWeb$TXT_TIMKIEM":'BRAVO10041601'}

	# # establish connection with the webpage
	# h = http.client.HTTPConnection('viettelpost.com.vn')

	# # url encode the parameters
	# url_params = urllib.parse.urlencode(params)

	# # send out the POST request
	# h.request('POST', 'Default.aspx?tabid=208', url_params, headers)

	# # get the response
	# r = h.getresponse()
	# return r
	# # analyse the response
	# if re.search("Error", r.read.decode()):
		# print("Not found")
	# else:
		# print("Probably found")
	# h.close()
