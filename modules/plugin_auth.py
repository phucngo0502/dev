# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 11/03/2012
###################################################
from gluon import current
from gluon.dal import Field
from html import *
from validators import IS_IN_SET, IS_NULL_OR, IS_IN_DB, IS_NOT_IN_DB, IS_IMAGE
from gluon.tools import Auth
import os

###################################################	

class ProcessAuth(Auth):
	def init(self,migrate=False):
		self.define_auth(migrate)
		self.define_permission(migrate)
		self.auth_org = self.get_group(atype='org')
		self.user_groups = None
		self.setting_auth()
		self.members = None
		
	def auth_groups(self):	
		if not self.user_groups:
			db = self.db
			rows = db(db.auth_membership.user_id==self.user_id).select(db.auth_membership.group_id,distinct=True)
			self.user_groups = [row.group_id for row in rows]
		return self.user_groups or [] 
		
	def define_auth(self,migrate=False):
		db = self.db
		if 'auth_group' in db.tables: return True 
		from plugin_app import widget_select

		self.db.define_table(self.settings.table_group_name,
			Field('parent','reference auth_group',widget=widget_select),
			Field('role',requires=IS_NOT_IN_DB(db, '%s.role' % self.settings.table_group_name)),
			Field('email'),
			Field('description','text'),
			Field('display_order','integer',default=100),
			Field('atype',default='org',requires=IS_IN_SET(['auth','org','group','group_org','sub_org','staff'])),
			Field('created_by','integer',default=self.user_id or 1,writable=False,readable=False),
			Field('created_on','datetime',default=current.request.now,writable=False,readable=False),
			migrate=migrate,
			format='%(role)s (%(id)s)')
			
		self.settings.extra_fields['auth_user']= [
			#Field('auth_group','integer',widget=widget_select),
			Field('auth_group','reference auth_group',widget=widget_select),
			Field('role',requires=IS_IN_SET(['Naso','Đại lý','Nhà cung cấp']),default="Đại lý"),
			Field('image','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/uploads/user')),
			Field('display_order','integer',default=100),
			Field('created_by','integer',default=self.user_id or 1,writable=False,readable=False),
			Field('created_on','datetime',default=current.request.now,writable=False,readable=False)]

		self.define_tables(username=True,migrate=migrate)
		db[self.settings.table_user_name].username.requires = IS_NOT_IN_DB(db, db[self.settings.table_user_name].username)
		return True

			
	def define_permission(self,migrate=False):
		if 'permission' in self.db.tables: return self.db.permission 
		return self.db.define_table('permission',
				Field('name',unique=True),
				Field('description','text'),
				Field('display_order','integer',default=100),
				Field('created_by','integer',default=self.user_id or 1,writable=False,readable=False),
				Field('created_on','datetime',default=current.request.now,writable=False,readable=False),
				migrate=migrate)

	def setting_mail(self):
		## configure email
		db = self.db
		# mail=self.settings.mailer
		# mail.settings.server = 'smtp.gmail.com:587'
		# mail.settings.sender = 'nasojsc@gmail.com'
		# mail.settings.login = '%s:%s'%('nasojsc','@Naso130821')

		mail=self.settings.mailer
		mail.settings.server = 'smtp.gmail.com:587'
		mail.settings.sender = 'webngheanchuanseo@gmail.com'
		mail.settings.login = '%s:%s'%('webngheanchuanseo','khanhchi@123')

		return mail
			
	def setting_auth(self):	
		## configure auth policy
		self.settings.registration_requires_verification = False
		self.settings.registration_requires_approval = False
		self.settings.reset_password_requires_verification = True

		self.settings.actions_disabled.append('request_reset_password')
		self.settings.actions_disabled.append('retrieve_username')
		self.settings.actions_disabled.append('register')
		self.settings.actions_disabled.append('profile')

		self.settings.create_user_groups = False
		
		self.settings.controller = 'plugin_auth'
		self.settings.login_url = URL(r=current.request,c='plugin_auth',f='login',args='login')
		
		self.settings.logout_next = URL(r=current.request,c='default',f='index')
		
		## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
		## register with janrain.com, write your domain:api_key in private/janrain.key
		#from gluon.contrib.login_methods.rpx_account import use_janrain
		#use_janrain(auth,filename='private/janrain.key')
		
		#self.settings.login_next = URL(r=current.request,c='plugin_app',f='index')
		if self.has_membership(role='public'): 
			self.settings.login_next = URL(r=current.request,c='home')
		else:
			self.settings.login_next = URL(r=current.request,c='admin',f='index')
		# elif self.has_membership(role='Chuyên viên'): 
			# self.settings.login_next = URL(r=current.request,c='plugin_app',f='explorer',vars=dict(procedure_id=5))

		self.messages.logged_in = ''	
		self.messages.logged_out = ''	

		# from gluon.contrib.login_methods.ldap_auth import ldap_auth 
		#self.settings.login_methods.append(ldap_auth(server='mail1.ivinh.com',base_dn='ou=people,dc=mail1,dc=ivinh,dc=com',custom_scope='subtree'))
   
	def get_group(self,user=None,atype='org'):	
		db = self.db
		user = user or self.user_id
		if not user: return None
		if not db.auth_user(user): return None
		group_id = db.auth_user(user).auth_group
		row = db.auth_group(group_id)
		while row:
			if row.atype==atype: break
			group_id = row.parent
			row = db.auth_group(group_id)
		return group_id	

	def get_members(self,group_id):	
		if not self.members: 
			db = self.db
			rows = db((db.auth_membership.group_id.belongs(group_id))&(db.auth_user.auth_group.belongs(self.user_groups))&(db.auth_user.id==db.auth_membership.user_id)).select(db.auth_user.id,distinct=True)
			self.members = [row.id for row in rows] or []
		return self.members

	def get_name(self,user_id):
		row =self.db.auth_user[user_id]
		if row:
			name = row.last_name+' ' + row.first_name
			return name
		else: return ''
	