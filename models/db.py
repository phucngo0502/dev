# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

try:
	from plugin_config import Configsite
	db = DAL(Configsite().database_name, fake_migrate=False,migrate = True, pool_size=Configsite().pool_size or 1, check_reserved=['all'],folder=request.folder + Configsite().database_folder)
	site_name =Configsite().site_name
	template =Configsite().template
	page_home =Configsite().page_home
	static_default = 'site/%s/template/%s'%(site_name,template)
	site_default = 'site/%s'%(site_name)
	
except Exception, e:
	db = DAL('sqlite://cms.db3', fake_migrate=False,migrate = True, pool_size=1, check_reserved=['all'],folder=request.folder +'/databases/site/doanhnghiep')
	site_name ='doanhnghiep'
	template = 'green'
	static_default = 'site/%s/template/%s'%(site_name,template)
	site_default = 'site/%s'%(site_name)
	page_home='trang-chu'
	
from gluon import current		
if current.request.env.http_host=="admin.ivinh.com":
	from plugin_config import Configsite
	cf= Configsite()
	cf.define_config_site(True)
	admin = cf.db	

## choose a style for forms

from gluon.contrib.appconfig import AppConfig
PortalConfig = AppConfig(reload=True)
response.formstyle = PortalConfig.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = PortalConfig.take('forms.separator')
	
	
from plugin_cms import Cms
cms = Cms()
from plugin_portlet import Portlet
portlet = Portlet(cms=cms)
portlet.define_portlet()

T.force('vn')

import cStringIO
from gluon.tools import Service, Auth
auth = Auth(db)
service = Service()
	
	

if request.controller=='portal':
	session.forget(response)
	from plugin_auth import ProcessAuth
	cas_provider = 'http://%s/%s/default/user/cas'%(request.env.http_host,PortalConfig.take('auth.provider')) if PortalConfig.take('auth.provider') else None
	auth = ProcessAuth(db, hmac_key=Auth.get_or_create_key(), cas_provider=cas_provider) 
	auth.init(True)
	cms.auth= auth
else:
	session.connect(request, response, separate=True)

	portlet.define_portletview()	
	from plugin_ckeditor import CKEditor
	CKEditor(db).define_tables()

	from plugin_auth import ProcessAuth
	cas_provider = 'http://%s/%s/default/user/cas'%(request.env.http_host,PortalConfig.take('auth.provider')) if PortalConfig.take('auth.provider') else None
	auth = ProcessAuth(db, hmac_key=Auth.get_or_create_key(), cas_provider=cas_provider) 
	auth.init(True)
	cms.auth= auth

	from plugin_process import ProcessModel
	if request.controller in ['appadmin','plugin_tools']:
		cms = Cms(db=db)
		cmsdb = cms.db
		cms.define_tables(True)
		processmodel = ProcessModel()
		processmodel.define_process(True)
		processmodel.define_procedures(True)
		processmodel.define_process_log(True)
		processmodel.define_process_lock(True)
		processmodel.define_isread(True)
		from plugin_upload import FileUpload
		FileUpload(db=cmsdb,upload_id=None).define_table(True)	
		portlet.define_portlet(True)
		portlet.define_portletview(True)		
		from plugin_crawler import Crawler
		c = Crawler()
		c.define_crawler(True)
		c.define_crawlerdata(True)
		crawler = c.db
	elif request.controller in ['plugin_process','plugin_comment','plugin_auth']:
		cms = Cms(db=db)
		processmodel = ProcessModel()
		processmodel.define_process()
		processmodel.define_procedures()
		processmodel.define_process_log()
		processmodel.define_process_lock()

import os
def setting_config(key=None,default={},path=None):
	try:
		if not path: path=os.path.join(request.folder,'config.py')
		file = open(path,'r')
		data = file.read().replace(chr(13),'')
		file.close()
		tmp = eval(data)
		if not key: return tmp
		return tmp[key]
	except:
		return default
		
api_naso ="https://website:gkajhsafplafgalsda@banhang.bahadi.vn/app"
link_naso ="https://banhang.bahadi.vn/app"
domain_naso ="https://banhang.bahadi.vn/app"