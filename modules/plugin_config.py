###################################################
from gluon import current, LOAD
from html import *
from gluon.dal import Field
from validators import IS_LENGTH
import os

class Configsite:
	def __init__(self,**attr):
		import os
		from gluon.contrib.appconfig import AppConfig
		PortalConfig = AppConfig(reload=True)
		domain_name = (current.request.env.http_host).replace('.','_')

		path_name = "ghephang"
		path=os.path.join(current.request.folder,'static/site/%s/appconfig.ini'%(path_name))
		
		my_site = AppConfig(path,reload=True)
		self.site_name = my_site.take('site.site_name')
		self.pool_size = my_site.take('site.pool_size') or 1
		self.template = my_site.take('site.template')
		self.database_folder = my_site.take('site.folder')
		self.database_name = my_site.take('site.uri')
		self.page_home = my_site.take('site.page_home') or 'home'
		
		self.page_title = my_site.take('metadata.title')
		self.page_description = my_site.take('metadata.description')
		self.page_keywords = my_site.take('metadata.keywords')
		self.page_logo =  "https://"+ current.request.env.http_host +'/'+current.request.application+'/static/site/%s/template/%s/%s'%(self.site_name,self.template,my_site.take('metadata.logo'))
		self.page_icon =  "https://"+current.request.env.http_host +'/'+current.request.application+'/static/site/%s/template/%s/%s'%(self.site_name,self.template,my_site.take('metadata.icon'))
		self.page_fb = my_site.take('metadata.fb')
		self.page_copyright = my_site.take('metadata.copyright')
		self.page_author = my_site.take('metadata.author')
		
		
		
		from gluon import DAL
		self.db = DAL('sqlite://config.db3', fake_migrate=False,migrate = True, pool_size=1, check_reserved=['all'],folder=current.request.folder +'/databases/admin/config')
			
	def define_config_site(self,migrate=False):	
		if 'config_site' not in self.db.tables:
			self.db.define_table('config_site',
				Field('site_name'),
				Field('url_site'),
				Field('is_template'),
				Field('database_folder'),
				Field('database_name'),
				Field('created_by','integer',writable=False,readable=False),
				Field('created_on','datetime',default=current.request.now,writable=False,readable=False),
				migrate=migrate)
		return self.db.config_site
		
	# def get_row(self):
		# table = self.define_config_site(True)
		# domain_name = current.request.env.http_host
		# return self.db(table.url_site==domain_name).select().first()