# -*- coding: utf-8 -*-
###################################################
# This content was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 26/02/2014
# Version 0.2 Date: 19/05/2015
# Version 1.0 Date: 22/09/2015
###################################################
from gluon import current, LOAD
from html import *
from gluon.dal import Field
from gluon.validators import *
import os
import cStringIO
from plugin_app import get_short_string
from plugin_upload import FileUpload
T = current.T

TABLENAME = 1
LINKHTML = 2

#####################################################################


def get_setting(data,key=None,default=None):
	try:
		tmp = eval(data.replace(chr(13),''))
		if not key: return tmp
		return tmp[key]
	except:
		return default
		
def setting_config(key=None,default={},path=None):
	try:
		if not path: path=os.path.join(current.request.folder,'config.py')
		file = open(path,'r')
		data = file.read().replace(chr(13),'')
		file.close()
		tmp = eval(data)
		if not key: return tmp
		return tmp[key]
	except Exception, e:
		print "setting ->", e
		return default	
		

from plugin_portlet import PortletStyle
def get_style(field,settings):
	style = ""
	for type in PortletStyle:
		key = "%s_%s"%(type[0],field)
		value = settings.get(key,"")
		if value != "":
			style += "%s:%s;"%(type[0],value)
	return style
	
class CmsModel:
	def __init__(self,**attr):
		self.init(**attr)	
	
	def init(self,**attr):
		self.db = attr.get('db',current.globalenv['db'])
		self.auth = attr.get('auth',current.globalenv.get('auth'))
		from plugin_config import Configsite
		self.site_name = Configsite().site_name
		
	def define_folder(self,migrate=False):	
		if 'folder' not in self.db.tables:
			self.db.define_table('folder',
				Field('parent','reference folder'),
				Field('name',unique=True,required=True,requires=IS_NOT_EMPTY(),length=255),
				Field('label',required=True,requires=IS_NOT_EMPTY()),
				Field('publish','boolean'),
				Field('description','text',default=''),
				Field('avatar','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/folder'%(self.site_name)) ),
				Field('avatar_bg','upload',autodelete=True,requires=IS_NULL_OR(IS_IMAGE()),uploadfolder=os.path.join(current.request.folder,'static/site/%s/uploads/avatar_bg'%(self.site_name)) ),
				# Field('meta_title',default=''),
				# Field('meta_description',default=''),
				# Field('meta_keywords',default=''),
				Field('folder_top','text',default=''),
				Field('folder_bottom','text',default=''),
				Field('setting','text'),
				Field('layout'),
				Field('url_link'),
				Field('display_order','integer',default=100),
				format='%(name)s',
				migrate=migrate)
		return self.db.folder		

	def define_dtable(self,migrate=False):	
		if 'dtable' not in self.db.tables:
			self.db.define_table('dtable',
				Field('name',unique=True,required=True,requires=IS_NOT_EMPTY(),length=255),
				Field('label',required=True,requires=IS_NOT_EMPTY()),
				Field('publish','boolean',default=False),
				Field('attachment','boolean',default=False),
				Field('is_import','boolean',default=False),
				Field('is_comment','boolean',default=False),
				Field('display_order','integer',default=100),
				Field('description','text'),
				Field('setting','text',default='{}'),
				Field('layout'),
				Field('display_row','text'),
				Field('display_rows','text'),
				Field('link_edit'),
				format='%(name)s',
				migrate=migrate)
		return self.db.dtable 
		
	def define_dcontent(self,migrate=False):	
		if 'dcontent' not in self.db.tables:
			self.define_folder(migrate)
			self.define_dtable(migrate)
			self.db.define_table('dcontent',
				Field('folder','reference folder'),
				Field('dtable'),
				Field('table_id','integer'),
				Field('link'),
				Field('name'),
				Field('avatar',"upload"),
				Field('description','text'),
				Field('publish_on','datetime'),
				Field('expired_on','datetime'),
				Field('meta_title',default=''),
				Field('meta_description',default=''),
				Field('meta_keywords',default=''),
				Field('textcontent','text',default=''),
				Field('languague',default='vie'),
				Field('publisher'),
				Field('creator'),
				Field('created_on','datetime',default=current.request.now),
				Field('modified_on','datetime',default=current.request.now),
				format='%(name)s',
				migrate=migrate)
		return self.db.dcontent
		
	def define_dfield(self,migrate=True):	
		if 'dfield' not in self.db.tables: 
			self.db.define_table('dfield',
				Field('name',required=True,requires=IS_NOT_EMPTY(),length=255),
				Field('ftype'),
				Field('fdefine','text'),
				Field('fformat'),
				Field('ckeditor','boolean',default=False),
				format='%(name)s',
				migrate=migrate,redefine=migrate)
		return self.db.dfield
		
	def define_tablefield(self,migrate=False):	
		if 'tablefield' not in self.db.tables: 
			self.define_dtable(migrate)
			self.define_dfield(migrate)
			self.db.define_table('tablefield',
				Field('dtable','reference dtable'),
				Field('dfield','reference dfield'),
				Field('dlabel'),
				Field('writable','boolean',default=True),
				Field('readable','boolean',default=True),
				Field('link_on_table','boolean',default=False),
				Field('show_on_table','boolean',default=False),
				Field('search_on','boolean',default=False),
				Field('ckeditor','boolean',default=False),
				Field('fformat'),
				Field('display_order','integer',default=100),
				migrate=migrate)
		return self.db.tablefield
		
	def define_readcontent(self,migrate=False):	
		if 'readcontent' not in self.db.tables: 
			self.db.define_table('readcontent',
				Field('foldername'),
				Field('tablename'),
				Field('link'),
				Field('clientip'),
				Field('user_agent'),
				Field('created_on','datetime',default=current.request.now),
				migrate=migrate)
		return self.db.readcontent
		
	def define_table(self,tablename,migrate=False):	
		if (migrate==False)&(tablename in self.db.tables): 
			return self.db[tablename]
		if tablename in ['folder','dtable','dcontent','dfield','tablefield']: 
			return eval('self.define_%s()'%(tablename))
		db = self.db
		self.define_tablefield()
		dtable = db(db.dtable.name==tablename).select().first()
		if dtable:
			if dtable.is_import:
				try:
					from datatables import define
					return define(db,tablename,migrate)
				except Exception, e:
					print "define_table ->", e
					return None
			fields = []
			fieldnames = []
			path = os.path.join(current.request.folder,'static/site/%s/uploads/%s'%(self.site_name,tablename))
			rows = db((db.tablefield.dtable==dtable.id)).select(db.tablefield.ALL,orderby=db.tablefield.display_order)
			TableName = tablename.capitalize()
			format = None
			if len(rows)>0:
				for row in rows:
					reftable = False
					if row.dfield.fdefine:
						field = eval(row.dfield.fdefine)
						if field.type.startswith('reference')|field.type.startswith('list:reference'):
							tname = field.type.split(' ')[-1]
							reftable = self.define_table(tname)
					else:
						label=current.T(row.dlabel or row.dfield.name)
						if row.dfield.ftype.startswith('reference')|row.dfield.ftype.startswith('list:reference'):
							tname = row.dfield.ftype.split(' ')[-1]
							reftable = self.define_table(tname)
						if row.dfield.ftype=='upload':
							field = Field(row.dfield.name,row.dfield.ftype,label=label,uploadfolder=path,writable=row.writable,readable=row.readable)
						else:
							requires = None
							fformat = row.fformat or row.dfield.fformat
							if fformat:
								if row.dfield.ftype == "date": requires = IS_EMPTY_OR(IS_DATE(format=fformat))
								elif row.dfield.ftype == "datetime": requires = IS_EMPTY_OR(IS_DATETIME(format=fformat))
							field = Field(row.dfield.name,row.dfield.ftype,label=label,writable=row.writable,readable=row.readable,requires=requires)
						if field.name=='name': format = '%(name)s'
						elif field.name=="created_by": field.default = self.auth.user_id if self.auth else 0
					if field.name not in fieldnames:
						if reftable != None: 
							fields.append(field)
							fieldnames.append(field.name)
			if len(fields)>0: 
				db.define_table(tablename,*fields,format=format,migrate=migrate,redefine=migrate)
				for row in rows:
					if row.dfield.ckeditor:
						db[tablename][row.dfield.name].represent = lambda value,row: XML(value)
				return db[tablename]
		return None
				
	def define_tables(self,migrate=False):
		self.define_folder(migrate)
		table = self.define_dtable(migrate)
		self.define_dcontent(migrate)
		self.define_dfield(migrate)
		self.define_tablefield(migrate)
		self.define_readcontent(migrate)
		rows = self.db(table.id).select()
		for row in rows: self.define_table(row.name,migrate)
				
	def get_id(self,tablename,value,field='name'):
		table = self.define_table(tablename)
		row = self.db(table[field]==value).select().first()
		return row.id if row else 0

	def get_id_project(self,tablename,value,field='name'):
		table = self.define_table(tablename)
		rows = self.db(table['id']>0).select()
		id_def = 0
		list_sam = []
		for row in rows:
			if self.check_text(row[field],value):
				id_def = row.id
		if id_def == 0:
			for row in rows:
				if self.comparestring(row[field],value)> 70:
					list_sam.append(row.id)
		return id_def,list_sam
		
	def check_text(self,string1,string2):
		if (string1.decode('utf8').lower()== string2.decode('utf8').lower()):
			return True
		else:
			return False
			
	def comparestring(self,string1,string2):
		length1 = string1.split(" ")
		length2 = string2.split(" ")

		if ((string1=='') or (string2=='')):
			return 0
		else:
			if len(length1) > len(length2):
				string  = string1
				string1 = string2
				string2 = string
			length1 = string1.split(" ")
			length2 = string2.split(" ")
			len_all = len(length1)
			i = 0
			for l2 in length2:
				for l1 in length1:
					if l2.decode('utf8').upper() == l1.decode('utf8').upper():
						i += 1
						length1.remove(l1)
						
			return  (i*100)/len_all if len_all >0 else 0
	
	def get_dtable(self,tablename):
		table = self.define_dtable()
		row = self.db(table.name==tablename).select().first()
		return row
		
	def get_avatar(self,tablename,value):
		if not value: return ''
		elif value[0:5]=='http:': return value
		else: return '//%s/%s/static/site/%s/uploads/%s/%s'%(current.request.env.http_host,current.request.application,self.site_name,tablename,value) 
	
	# def get_avatar_by_size(self,tablename,value,size_w=800,size_h=600):
		# import os, uuid
		# size_w = int(size_w)
		# size_h = int(size_h)
		# path1 = current.request.folder + '/static/site/%s/uploads/%s/%sx%s'%(self.site_name,tablename,size_w,size_h) 
		# url = current.request.folder + '/static/site/%s/uploads/%s/%s'%(self.site_name,tablename,value) 
		# url1 = current.request.folder + '/static/site/%s/uploads/%s/%sx%s/%s'%(self.site_name,tablename,size_w,size_h,value) 
		# if not os.path.exists(url1):
			# from PIL import Image
			# if os.path.exists(url):
				# if not os.path.exists(path1): os.makedirs(path1)
				
				# im=Image.open(url)
				# if size_w > size_h:
					# am = size_w - size_h
				# else:
					# am = size_h - size_w
				# size=(size_w + am,size_h + am)
				# im.thumbnail(size,Image.ANTIALIAS)
				
				
				
				# offset_x = max((size[0] - im.size[0]) / 2, 0)
				# offset_y = max((size[1] - im.size[1]) / 2, 0)
				# offset_tuple = (offset_x, offset_y) #pack x and y into a tuple

				# # create the image object to be the final product
				# final_thumb = Image.new(mode='RGBA',size=size,color=(255,255,255,255))
				# # paste the thumbnail into the full sized image
				# final_thumb.paste(im, offset_tuple)
				# # save (the PNG format will retain the alpha band unlike JPEG)
				# # final_thumb.save(url1,'PNG')
				
				# im = self.centeredCrop(final_thumb,size_h,size_w)
				# im.save(url1,'PNG')
			# else: return ''
		# return 'http://%s/%s/static/site/%s/uploads/%s/%sx%s/%s'%(current.request.env.http_host,current.request.application,self.site_name,tablename,size_w,size_h,value) 
	
	def get_avatar_webp(self,tablename,value):
		import os, uuid
		
		extension = value.split('.')[-1].lower()
		name = value[:-(len(extension)+1)]
		url = current.request.folder + '/static/site/%s/uploads/%s/%s'%(self.site_name,tablename,value) 
		url1 = url.replace(("."+extension),'.webp')
		
		if not os.path.exists(url1):
			from PIL import Image
			if os.path.exists(url):
				im=Image.open(url)
				im.save(url1,'webp')
			else: return ''
		return '//%s/%s/static/site/%s/uploads/%s/%s.webp'%(current.request.env.http_host,current.request.application,self.site_name,tablename,name) 
		
		import os, uuid
		size_w = int(size_w)
		size_h = int(size_h)
		path1 = current.request.folder + '/static/site/%s/uploads/%s/%sx%s'%(self.site_name,tablename,size_w,size_h) 
		url = current.request.folder + '/static/site/%s/uploads/%s/%s'%(self.site_name,tablename,value) 
		url1 = current.request.folder + '/static/site/%s/uploads/%s/%sx%s/%s'%(self.site_name,tablename,size_w,size_h,value) 
		if not os.path.exists(url1):
			from PIL import Image
			size=(size_w,size_h)
			if os.path.exists(url):
				im=Image.open(url)
				if size_w > size_h:
					am = size_w - size_h
				else:
					am = size_h - size_w
				size=(size_w + am,size_h + am)
				im.thumbnail(size,Image.ANTIALIAS)
				im = self.centeredCrop(im,size_h,size_w)
				if not os.path.exists(path1): os.makedirs(path1)
				im.save(url1,'jpeg')
			else: return ''
		return '//%s/%s/static/site/%s/uploads/%s/%sx%s/%s'%(current.request.env.http_host,current.request.application,self.site_name,tablename,size_w,size_h,value) 
	
	
	def get_avatar_ck_webp(self,tablename,url,value):
		import os, uuid
		
		extension = value.split('.')[-1].lower()
		name = value[:-(len(extension)+1)]
		
		url1 = url.replace(("."+extension),'.webp')
		if not os.path.exists(url1):
			from PIL import Image
			if os.path.exists(url):
				im=Image.open(url)
				im.save(url1,'webp')
			else: return ''
		return '//%s/%s/static/site/%s/uploads/ckeditor/%s.webp'%(current.request.env.http_host,current.request.application,self.site_name,name) 
	
	def get_avatar_by_size(self,tablename,value,size_w=800,size_h=600):
		import os, uuid
		size_w = int(size_w)
		size_h = int(size_h)
		path1 = current.request.folder + '/static/site/%s/uploads/%s/%sx%s'%(self.site_name,tablename,size_w,size_h) 
		url = current.request.folder + '/static/site/%s/uploads/%s/%s'%(self.site_name,tablename,value) 
		url1 = current.request.folder + '/static/site/%s/uploads/%s/%sx%s/%s'%(self.site_name,tablename,size_w,size_h,value) 
		if not os.path.exists(url1):
			from PIL import Image
			size=(size_w,size_h)
			if os.path.exists(url):
				im=Image.open(url)
				if size_w > size_h:
					am = size_w - size_h
				else:
					am = size_h - size_w
				size=(size_w + am,size_h + am)
				im.thumbnail(size,Image.ANTIALIAS)
				im = self.centeredCrop(im,size_h,size_w)
				if not os.path.exists(path1): os.makedirs(path1)
				im.save(url1,'jpeg')
			else: return ''
		return '//%s/%s/static/site/%s/uploads/%s/%sx%s/%s'%(current.request.env.http_host,current.request.application,self.site_name,tablename,size_w,size_h,value) 
	
	def get_avatar_by_url(self,tablename,url,value,size_w=800,size_h=600):
		import os, uuid
		size_w = int(size_w)
		size_h = int(size_h)
		path1 = current.request.folder + '/static/site/%s/uploads/%s/%sx%s'%(self.site_name,tablename,size_w,size_h) 
		url = url
		url1 = current.request.folder + '/static/site/%s/uploads/%s/%sx%s/%s'%(self.site_name,tablename,size_w,size_h,value) 
		if not os.path.exists(url1):
			from PIL import Image
			size=(size_w,size_h)
			if os.path.exists(url):
				im=Image.open(url)
				if size_w > size_h:
					am = size_w - size_h
				else:
					am = size_h - size_w
				size=(size_w + am,size_h + am)
				im.thumbnail(size,Image.ANTIALIAS)
				im = self.centeredCrop(im,size_h,size_w)
				if not os.path.exists(path1): os.makedirs(path1)
				im.save(url1,'jpeg')
			else: return ''
		return '//%s/%s/static/site/%s/uploads/%s/%sx%s/%s'%(current.request.env.http_host,current.request.application,self.site_name,tablename,size_w,size_h,value) 
	

	def centeredCrop(self,img, new_height, new_width):
		half_the_width = img.size[0] / 2
		half_the_height = img.size[1] / 2
		img4 = img.crop((half_the_width - (new_width/2),half_the_height - (new_height/2),half_the_width + (new_width/2),half_the_height + (new_height/2)))
		return img4

	def get_images_content(self,tablename,value, width=70, height=70):
		request = current.request
		if not value: return '' #'image_upload.file.default.png'
		elif value[0:7] == '//': return XML('<img class="thumbnail" src=%s width=%s height=%s />'%(value,width,height)) if width*height>0 else XML('<img class="thumbnail" src=%s />'%(value))
		import os
		if os.path.exists(request.folder+'/static/uploads/'+tablename+'/'+ value):
			value='//'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ value
		elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ value):
			value='//'+request.env.http_host +'/'+request.application+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ value
		elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ value):
			value='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ value
		elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/images_download/'+ value):
			value='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/images_download/'+ value
		else:
			value='//'+request.env.http_host+'/'+request.application+'/static/images/img_defautl.jpg'
			return  XML('<img class="thumbnail" src=%s />'%(value))
		return  XML('<img class="thumbnail" src=%s />'%(value))
		
	def widget_folder(self, field, value):
		from plugin_app import select_option
		dtable = self.define_dtable()
		row = self.db(dtable.name==field._tablename).select().first()
		id = get_setting(row.setting,"folder",None) if row else None
		if not value: 
			try:
				if current.request.vars.folder: 
					value = int(current.request.vars.folder) 
				if current.request.args[2]: 
					value = self.get_id('folder',current.request.args[2])
			except Exception, e:
				pass
		widget = SELECT(['']+select_option(self.db,self.auth,'folder',id=id,selected=[value],field='label'),_name=field.name,_id=field._tablename+'_'+field.name,requires=field.requires,_class="generic-widget form-control")
		return widget	
					
	def sqlform(self,tablename,id=None,addnew=True,buttons=[],showid=False,submit="ajax",default={},default_show={},default_comment={},wfields=None,attachment=False):
		from gluon.sqlhtml import SQLFORM
		from plugin_app import Dropdown, widget_multiselect2_ajax, widget_select2, widget_select, widget_mask_integer, widget_select_supplier
		from plugin_ckeditor import CKEditor
		from plugin_upload import FileUpload
		db = self.db
		dfield = self.define_dfield()
		tfield = self.define_tablefield()
		table = self.define_table(tablename)
		dtable = db(db.dtable.name==tablename).select().first()
		fields = wfields or table.fields
		for field in fields:
			row = db((tfield.dtable==dtable.id)&(tfield.dfield==dfield.id)&(dfield.ftype==table[field].type)&(dfield.name==field)).select(tfield.ALL).first()
			if row:
				table[field].label = current.T(row.dlabel or "%s %s"%(tablename.capitalize(),field))
				if (row.writable==False):
					table[field].writable = False
					table[field].readable = False
			if field in default_show.keys(): 
				table[field].default = default_show[field]	
			if field in default.keys(): 
				table[field].writable = False			
				table[field].readable = False			
				table[field].default = default[field]
			
			elif ((table[field].writable==True)|(wfields!=None))&(table[field].widget==None):
				if table[field].type.startswith('list:reference'):
					ref = table[field].type[15:]
					table[field].widget = table[field].widget or widget_multiselect2_ajax
					#table[field].requires = IS_IN_DB(db,ref+'.id','%(name)s',multiple=True)
					if addnew: 
						if self.auth:
							if self.auth.has_permission('create',ref,0,self.auth.user_id)|self.auth.has_membership(role='admin'):  
								table[field].label= Dropdown(table[field], SPAN(I(_class="fa fa-plus-circle fa-fw"),table[field].label))
				elif table[field].type == "upload":
					pass
				elif field == "folder":
					table[field].widget = self.widget_folder
				elif table[field].type.startswith('reference'):
					ref = table[field].type[10:]
					if ref =='supplier':
						table[field].widget = widget_select_supplier
					else:
						
						table[field].widget = widget_select if "parent" in db[ref].fields else widget_select2
					if addnew: 
						if self.auth:
							if self.auth.has_permission('create',ref,0,self.auth.user_id)|self.auth.has_membership(role='admin'):  
								table[field].label= Dropdown(table[field], SPAN(I(_class="fa fa-plus-circle fa-fw"),table[field].label))
				elif table[field].type == "integer":
					table[field].widget = widget_mask_integer
				elif row:
					if row.ckeditor: table[field].widget=CKEditor(db).widget_content	
					
			if field in default_comment.keys(): 
				table[field].comment = XML(default_comment[field])
		if buttons == []:
			if submit==True:
				buttons = [INPUT(_type="submit",_value=current.T("Submit"),_class="btn btn-primary submit")]
				buttons.append(INPUT(_type='button',_value=T('Back'),_onclick='javascript:history.go(-1)',_class='btn btn-default'))
			elif submit=="ajax":
				args = [tablename]
				if id: args += [id]
				ajax = "ajax('%s', %s, 'sqlform-msg')"%(URL(r=current.request,c="plugin_table",f='medit_update',args=args,vars=default),fields if id else (fields+["uuid"]))
				buttons = [INPUT(_type="button",_value=current.T("Submit"),_class="btn btn-primary",_onclick=ajax)]	
				buttons += [XML('<button type="button" class="btn btn-default btn-modal" data-dismiss="modal">%s</button>'%T("Close"))]	
				
		if attachment & dtable.attachment:
			if wfields:
				form=SQLFORM(table,id,buttons=[],showid=showid,fields=fields)
			else:
				form=SQLFORM(table,id,buttons=[],showid=showid)
			if not id:
				import uuid
				uuid = uuid.uuid1().int
				form.append(INPUT(_name='uuid',_value=uuid,_style="display:none"))
			else: uuid = id
			fileupload = FileUpload(db=db,tablename=tablename,table_id=uuid,upload_id=None)
			upload = fileupload.formupload(colorbox=False)
			form = DIV(form,upload)
			for button in buttons: form.append(button)
		elif wfields:
			form=SQLFORM(table,id,buttons=buttons,showid=showid,fields=fields)
		else:
			form=SQLFORM(table,id,buttons=buttons,showid=showid)
		form.append(DIV(_id="sqlform-msg"))	
		return form
		
	def list_folder(self):
		from plugin_app import select_option
		self.define_folder()
		auth = current.globalenv.get('auth',None)
		widget = SELECT(['']+select_option(self.db,auth,'folder',field='label'),_name='list_folder', _class='form-control')
		return widget
	
	def list_folder_by_bds(self,id):
		from plugin_app import select_option_publish
		self.define_folder()
		auth = current.globalenv.get('auth',None)
		widget = SELECT( [OPTION("Bán Nhà Đất",_value='ban-nha-dat')]+select_option_publish(db=self.db,table='folder',id=id,space="--",field='label',field_id='name'),_name='folder', _class='form-control')
		return widget
	
class CmsFolder(CmsModel):

	def get_folder(self,folder=None):
		if not folder:
			folder = current.request.args(0)
		if not str(folder).isdigit(): 
			return self.get_id('folder',folder)
		return int(folder)
		
	def get_folder_parent(self,folder_id=None):
		folder = self.define_folder()
		row = self.db(folder.id==self.get_folder(folder_id)).select(self.db.folder.ALL).first()
		if row: return int(row.parent)
		else: return None
		
	def get_folders(self,parent=None):
		folder = self.define_folder()
		id_folders = [parent]
		rows = self.db(folder.parent==parent).select(folder.id)
		for row in rows: id_folders += self.get_folders(row.id)
		return id_folders

	def get_lasttime(self,folder=None):
		folder = self.get_folder(folder)
		table = self.define_dcontent()
		row = self.db(table.folder==folder).select(orderby=table.modified_on).last()
		if not row: row = self.db(table).select(orderby=table.modified_on).last()
		if not row: return "0"
		return row.modified_on.strftime("%Y%m%d%H%M%S") if row.modified_on else "0"
		
	def get_page(self):
		try: 
			page = int(current.request.args[-1].split('.')[0])
		except: 
			page = 1
		return page
		
	def get_length(self,folder,length=10):
		return get_setting(self.db.folder(folder).setting,'length',length) if self.db.folder(folder) else length

	def get_query(self,folder=None,tablename=None):	
		dcontent = self.define_dcontent()
		folder = self.get_folder(folder)
		folders = self.get_folders(folder)
		query = dcontent.folder.belongs(folders)
		if tablename:
			if tablename != 'dcontent':
				table = self.define_table(tablename)
				query&=((dcontent.dtable==tablename)&(dcontent.table_id==table.id))
		query &=((dcontent.expired_on>=current.request.now)|(dcontent.expired_on==None))&(dcontent.publish_on<=current.request.now)
		return query
		
	def get_count(self,folder=None,tablename=None):
		query = self.get_query(folder)
		if tablename: 
			dtable = self.define_table(tablename)
			query &= (dtable.id==self.db.dcontent.table_id)&(self.db.dcontent.dtable==tablename)
		return self.db(query).count()
		
	def get_rows(self,folder=None,page=None,length=None,orderby=None,query=None,tablename=None):
		folder = folder or self.get_folder(folder)
		if query:
			q = self.get_query(folder,tablename)
			if isinstance(query,str): 
				db = self.db
				query = eval(query)
			query&=q 
		else:
			query = self.get_query(folder,tablename)
		page = page or self.get_page()
		length = length or self.get_length(folder)
		p1 = (page-1)*length
		p2 = page*length
		orderby = orderby or ~self.db.dcontent.publish_on
		table = tablename or 'dcontent'
		rows = self.db(query).select(self.db[table].ALL,limitby=(p1,p2),orderby=orderby,distinct=True)
		return rows

	def get_content(self,tablename,orderby=None,folder=None,page=None,length=None,query=None):
		dtable = self.define_table(tablename)
		folder = folder or self.get_folder(folder)
		query = self.get_query(folder)&query if query else self.get_query(folder)
		query &= (dtable.id==self.db.dcontent.table_id)&(self.db.dcontent.dtable==tablename)
		page = page or self.get_page()
		length = length or self.get_length(folder)
		p1 = (page-1)*length
		p2 = page*length
		orderby = orderby or dtable.id
		rows = self.db(query).select(dtable.ALL,limitby=(p1,p2),orderby=orderby)
		return rows
		
	def url_content(self,row,table=None):
		if table == "dcontent": 
			tablename = row.dtable
		else: 
			tablename = table or row.dtable
			if table:
				row = self.db((self.db.dcontent.dtable==tablename)&(self.db.dcontent.table_id==row.id)).select().last()
				if not row: return "#"
		return URL(r=current.request,a=row.folder.name,c=tablename,f=row.link)
		
	def url_link(self,row,table=None):
		if table == "dcontent": 
			tablename = row.dtable
		else: 
			tablename = table or row.dtable
			if table:
				row = self.db((self.db.dcontent.dtable==tablename)&(self.db.dcontent.table_id==row.id)).select().last()
				if not row: return "#"
		return row.link

	def url_folder(self,folder_name):
		return '/'+folder_name

	def layout_folder(self,folder=None):
		table = self.define_folder()
		folder = self.get_folder(folder)
		return table(folder).layout if table(folder) else None
		
	def folder_content(self,**attr):
		def get_field(table, field, row):
			value = row[field['name']]
			if field['name'] == 'avatar': 
				value = IMG(_src=self.get_avatar(table,value),_width=field.get('width',50),_height=field.get('height',50))
			elif 'length' in field.keys(): 
				value = get_short_string(value,field['length'])
			if 'link' in field.keys(): 
				value = A(value,_href=self.url_content(row,table))
			return value
		
		table = attr.get('table',False)
		folder = attr.get('folder',None)
		tablename = attr.get('tablename',None)
		orderby = attr.get('orderby',None)
		page = attr.get('page',1)
		length = attr.get('length',5)
		query = attr.get('query',None)
		fields = attr.get('fields',[{'name':'name','link':True}])
		try:
			rows = self.get_rows(folder,page,length,orderby,query,tablename)
			if table:
				content = TABLE(_class='folder_table %s_table'%tablename,_id='%s_table'%folder)
				header = TR()
				for field in fields: 
					label = field['label'] if 'label' in field.keys() else '%s %s'%(tablename,field['name']) 
					header.append(TH(current.T(label)))
				content.append(header)
			else:
				content = UL(_class='folder_list %s_list'%tablename,_id='%s_list'%folder)
			i = 0
			for row in rows:
				if not tablename: tablename = row.dtable
				lign = TR(_class='folder_detail %s_detail folder_lign_%s'%(tablename,i%2)) if table else UL(_class='folder_detail %s_detail folder_lign_%s'%(tablename,i%2))
				for field in fields:
					value = get_field(tablename,field,row)
					value = TD(value,_class='field_%s %s_%s'%(field['name'],tablename,field['name'])) if table else LI(value,_class='field_%s %s_%s'%(field['name'],tablename,field['name']))	
					lign.append(value)
				content.append(lign)	
				i+=1
			return content
		except Exception, e:
			return e
		
	def breadcrumb(self,parent=None):
		request = current.request
		path = ''
		div = DIV(_class="breadcrumb_menu")
		if request.function != 'crud':
			while parent:
				folder_id = self.get_folder(parent)
				folder = self.db.folder(folder_id)
				if folder:
					url =''
					if request.controller =='plugin_process':
						url = str(A(B(folder.label),_href=URL(r=request,c='plugin_process',f='explorer',args=[request.args(0),request.args(1),folder.name]),_class = 'folder'+str(parent),cid=request.cid))
					else:
						url = str(A(B(folder.label),_href='/%s'%(folder.name),_class = 'folder'+str(parent),cid=request.cid))
					if folder.url_link:
						url = str(A(B(folder.label),_href=folder.url_link,_class = 'folder'+str(parent),cid=request.cid))
						
					path = url + ' > ' + path if path <> '' else url
					parent = folder.parent
				else: 
					break
			div.append(XML(path))
		return div
		
	def folder_name(self,folder=None):
		folder = self.get_folder(folder)
		foldername = current.T(self.db.folder(folder).label) if self.db.folder(folder) else current.T('Home page') 
		return foldername
			
	def folder_des(self,folder=None):
		folder = self.get_folder(folder)
		from plugin_config import Configsite
		
		folderdes = Configsite().page_description
		folderdes = current.T(self.db.folder(folder).description) if self.db.folder(folder).description else Configsite().page_description
		return folderdes
		
	def folder_fname(self,folder=None):
		folder = self.get_folder(folder)
		foldername = self.db.folder(folder).name if self.db.folder(folder) else ''
		return foldername
		
	def folder_content(self,folder=None):
		folder = self.get_folder(folder)
		row = self.db.folder(folder)
		if row:
			return row.folder_top if row.folder_top else '' , row.folder_bottom if row.folder_bottom else ''
		return '',''
			
	def folder_avatar(self,folder=None):
		folder = self.get_folder(folder)
		row = self.db.folder(folder)
		if row:
			return row.avatar if row.avatar else '' , row.avatar_bg if row.avatar_bg else ''
		return '',''
		
class Cms(CmsFolder):

	def menu(self,folder,deep=1,**attr):
		# if deep>attr.get('maxdeep',1): return ""	
		if not str(folder).isdigit(): 
			folder = self.get_folder(folder)
		table = self.define_folder()
		rows = self.db((table.parent==folder)&(table.publish==True)).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class',"")),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id',"")))
		a_class = attr.get('a_class_deep') + str(deep) if attr.get('a_class_deep') else attr.get('a_class_%s'%deep,attr.get('a_class',""))
		a_id = attr.get('a_id_deep') + str(deep) if attr.get('a_id_deep') else attr.get('a_id_%s'%deep,attr.get('a_id',""))
		li_class = attr.get('li_class_deep') + str(deep) if attr.get('li_class_deep') else attr.get('li_class_%s'%deep,attr.get('li_class',""))
		li_id = attr.get('li_id_deep') + str(deep) if attr.get('li_id_deep') else attr.get('li_id_%s'%deep,attr.get('li_id',""))
		icon_class = attr.get('icon_class_deep') + str(deep) if attr.get('icon_class_deep') else attr.get('icon_class_%s'%deep,attr.get('icon_class',""))
		icon = I(_class="fa %s fa-fw"%icon_class) if icon_class else ""
		folder_name =''
		for row in rows:
			li_class_row = li_class
			a_class_row  = a_class
			if (row.display_order==0):
				pass
			else:
				p = self.db(self.db.folder.name==current.request.args(0)).select().first()
				
				if p:
					if p.parent==folder:
						folder_name = current.request.args(0)
					else:
						if p.parent:
							folder_name = p.parent.name
				if row.name == folder_name:
					li_class_row   +=' folder_act'
					a_class_row    += ' a_act'
				url = row.url_link or self.url_folder(row.name)	
				c_menu = self.menu(row.id,deep+1,**attr)
				if c_menu !='':
					link = A(icon,row.label,SPAN(_class='sub-indicator'),_href=url,_class=a_class_row,_id=a_id)
					li_class_row += " dropdown"
					a_class_row += " dropdown-toggle"
				else:
					link = A(icon,row.label,_href=url,_class=a_class_row,_id=a_id)
				content.append(LI(link,c_menu,_class=li_class_row,_id=li_id))
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
	def menu1(self,folder,deep=1,**attr):
		if deep>attr.get('maxdeep',1): return ""	
		if not str(folder).isdigit(): 
			folder = self.get_folder(folder)
		table = self.define_folder()
		rows = self.db((table.parent==folder)&(table.publish==True)).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class',"")),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id',"")))
		a_class = attr.get('a_class_deep') + str(deep) if attr.get('a_class_deep') else attr.get('a_class_%s'%deep,attr.get('a_class',""))
		a_id = attr.get('a_id_deep') + str(deep) if attr.get('a_id_deep') else attr.get('a_id_%s'%deep,attr.get('a_id',""))
		li_class = attr.get('li_class_deep') + str(deep) if attr.get('li_class_deep') else attr.get('li_class_%s'%deep,attr.get('li_class',""))
		li_id = attr.get('li_id_deep') + str(deep) if attr.get('li_id_deep') else attr.get('li_id_%s'%deep,attr.get('li_id',""))
		icon_class = attr.get('icon_class_deep') + str(deep) if attr.get('icon_class_deep') else attr.get('icon_class_%s'%deep,attr.get('icon_class',""))
		icon = I(_class="fa %s fa-fw"%icon_class) if icon_class else ""
		folder_name =''
		for row in rows:
			li_class_row = li_class
			a_class_row  = a_class
			if (row.display_order==0):
				pass
			else:
				p = self.db(self.db.folder.name==current.request.args(0)).select().first()
				
				if p:
					if p.parent==folder:
						folder_name = current.request.args(0)
					else:
						if p.parent:
							folder_name = p.parent.name
				if row.name == folder_name:
					li_class_row   +=' folder_act'
					a_class_row    += ' a_act'
				url = row.url_link or self.url_folder(row.name)	
				c_menu = self.menu1(row.id,deep+1,**attr)
				if c_menu !='':
					link = A(icon,row.label,SPAN(_class='sub-indicator'),_href=url,_class=a_class_row,_id=a_id)
				else:
					link = A(icon,row.label,_href=url,_class=a_class_row,_id=a_id)
				content.append(LI(link,c_menu,_class=li_class_row,_id=li_id))
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
	def menu_covi(self,folder,deep=1,**attr):
		if deep>attr.get('maxdeep',1): return ""	
		if not str(folder).isdigit(): 
			folder = self.get_folder(folder)
		table = self.define_folder()
		rows = self.db((table.parent==folder)&(table.publish==True)).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class',"")),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id',"")))
		a_class = attr.get('a_class_deep') + str(deep) if attr.get('a_class_deep') else attr.get('a_class_%s'%deep,attr.get('a_class',""))
		a_id = attr.get('a_id_deep') + str(deep) if attr.get('a_id_deep') else attr.get('a_id_%s'%deep,attr.get('a_id',""))
		li_class = attr.get('li_class_deep') + str(deep) if attr.get('li_class_deep') else attr.get('li_class_%s'%deep,attr.get('li_class',""))
		li_id = attr.get('li_id_deep') + str(deep) if attr.get('li_id_deep') else attr.get('li_id_%s'%deep,attr.get('li_id',""))
		icon_class = attr.get('icon_class_deep') + str(deep) if attr.get('icon_class_deep') else attr.get('icon_class_%s'%deep,attr.get('icon_class',""))
		icon = I(_class="fa %s fa-fw"%icon_class) if icon_class else ""
		folder_name =''
		for row in rows:
			li_class_row = li_class
			a_class_row  = a_class
			if (row.display_order==0):
				pass
			else:
				p = self.db(self.db.folder.name==current.request.args(0)).select().first()
				
				if p:
					if p.parent==folder:
						folder_name = current.request.args(0)
					else:
						if p.parent:
							folder_name = p.parent.name
				if row.name == folder_name:
					li_class_row   +=' folder_act'
					a_class_row    += ' a_act'
				url = row.url_link or self.url_folder(row.name)	
				c_menu = self.menu_covi(row.id,deep+1,**attr)
				link = A(row.label,_href=url,_class=a_class_row,_id=a_id)


				content.append(LI(SPAN(link),c_menu,_class=li_class_row,_id=li_id))
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
	def menu_not_link(self,folder,deep=1,**attr):
		if deep>attr.get('maxdeep',1): return ""	
		if not str(folder).isdigit(): 
			folder = self.get_folder(folder)
		table = self.define_folder()
		rows = self.db((table.parent==folder)&(table.publish==True)).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class',"")),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id',"")))
		a_class = attr.get('a_class_deep') + str(deep) if attr.get('a_class_deep') else attr.get('a_class_%s'%deep,attr.get('a_class',""))
		a_id = attr.get('a_id_deep') + str(deep) if attr.get('a_id_deep') else attr.get('a_id_%s'%deep,attr.get('a_id',""))
		li_class = attr.get('li_class_deep') + str(deep) if attr.get('li_class_deep') else attr.get('li_class_%s'%deep,attr.get('li_class',""))
		li_id = attr.get('li_id_deep') + str(deep) if attr.get('li_id_deep') else attr.get('li_id_%s'%deep,attr.get('li_id',""))
		icon_class = attr.get('icon_class_deep') + str(deep) if attr.get('icon_class_deep') else attr.get('icon_class_%s'%deep,attr.get('icon_class',""))
		icon = I(_class="fa %s fa-fw"%icon_class) if icon_class else ""
		folder_name =''
		for row in rows:
			li_class_row = li_class
			a_class_row  = a_class
			if (row.display_order==0):
				pass
			else:
				p = self.db(self.db.folder.name==current.request.args(0)).select().first()
				
				if p:
					if p.parent==folder:
						folder_name = current.request.args(0)
					else:
						if p.parent:
							folder_name = p.parent.name
				if row.name == folder_name:
					li_class_row   +=' folder_act'
					a_class_row    += ' a_act'
				url = "#"
				c_menu = self.menu1(row.id,deep+1,**attr)
				if c_menu !='':
					link = A(icon,row.label,SPAN(_class='sub-indicator'),_href=url,_class=a_class_row,_id=a_id)
				else:
					link = A(icon,row.label,_href=url,_class=a_class_row,_id=a_id)
				content.append(LI(link,c_menu,_class=li_class_row,_id=li_id))
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
	def menu_icon(self,folder,deep=1,**attr):
		# if deep>attr.get('maxdeep',1): return ""	
		if not str(folder).isdigit(): 
			folder = self.get_folder(folder)
		table = self.define_folder()
		rows = self.db((table.parent==folder)&(table.publish==True)).select(orderby=table.display_order)
		if len(rows)==0: return ''
		content = UL(_class=attr.get('ul_class_%s'%deep,attr.get('ul_class',"")),_id=attr.get('ul_id_%s'%deep,attr.get('ul_id',"")))
		a_class = attr.get('a_class_deep') + str(deep) if attr.get('a_class_deep') else attr.get('a_class_%s'%deep,attr.get('a_class',""))
		a_id = attr.get('a_id_deep') + str(deep) if attr.get('a_id_deep') else attr.get('a_id_%s'%deep,attr.get('a_id',""))
		li_class = attr.get('li_class_deep') + str(deep) if attr.get('li_class_deep') else attr.get('li_class_%s'%deep,attr.get('li_class',""))
		li_id = attr.get('li_id_deep') + str(deep) if attr.get('li_id_deep') else attr.get('li_id_%s'%deep,attr.get('li_id',""))
		icon_class = attr.get('icon_class_deep') + str(deep) if attr.get('icon_class_deep') else attr.get('icon_class_%s'%deep,attr.get('icon_class',""))
		icon = I(_class="fa %s fa-fw"%icon_class) if icon_class else ""
		folder_name =''
		for row in rows:
			avatar =''
			if row.avatar:
				avatar = IMG(_src='//%s/%s/static/site/%s/uploads/folder/%s'%(current.request.env.http_host,current.request.application,self.site_name,row.avatar))
			li_class_row = li_class
			a_class_row  = a_class
			if (row.display_order==0):
				pass
			else:
				p = self.db(self.db.folder.name==current.request.args(0)).select().first()
				
				if p:
					if p.parent==folder:
						folder_name = current.request.args(0)
					else:
						if p.parent:
							folder_name = p.parent.name
				if row.name == folder_name:
					li_class_row   +=' folder_act'
					a_class_row    += ' a_act'
				url = row.url_link or self.url_folder(row.name)	
				c_menu = self.menu_icon(row.id,deep+1,**attr)
				if c_menu !='':
					link = A(avatar,row.label,SPAN(_class='sub-indicator'),_href=url,_class=a_class_row,_id=a_id)
				else:
					link = A(avatar,row.label,_href=url,_class=a_class_row,_id=a_id)
				content.append(LI(link,c_menu,_class=li_class_row,_id=li_id))
			
		if attr.get('div_class_%s'%deep,attr.get('div_id_%s'%deep)):
			content = DIV(content,_class=attr.get('div_class_%s'%deep),_id=attr.get('div_id_%s'%deep))
		elif attr.get('div_class',attr.get('div_id')):
			content = DIV(content,_class=attr.get('div_class'),_id=attr.get('div_id'))		
		return content
		
	def render(self,boxname=None,id=None,context={}):
		try:
			import cStringIO
			self.define_box()
			box = self.box(id) if id else self.db(self.db.box.name==boxname).select().first()
			content = box.htmlcontent.replace('&quot;', "'").replace('&#39;', '"')	
			content = '%s%s'%(box.textcontent,content)
			if box.link:
				return A(IMG(_src=URL(r=current.request,c='static',f='plugin_box/avatar',args=[box.avatar]),_id=boxname,_class='ivinhcmsbox-img'),_href=box.link)
			foldercontent = ''
			try:
				settings = eval(box.setting.replace(chr(13),''))
				for key in settings.keys(): context[key] = settings[key]
				if 'folder' in settings.keys(): 
					foldercontent = self.folder_content(**settings)
					if settings.get('boxname',True): foldercontent = DIV(H2(box.label),foldercontent,_id=boxname)
			except Exception, e:
				pass
			content = '%s %s'%(foldercontent,current.response.render(cStringIO.StringIO(content), context))
			return XML(content)
		except Exception, e:
			return 'Box %s error: %s'%(boxname or id, e)
	
	def layout(self,tablename=None):
		tablename = tablename or self.get_table()
		dtable = self.define_dtable()
		row = self.db(dtable.name==tablename).select().first()
		return row.layout if row else None
	
	def get_table(self):
		return current.request.args(TABLENAME)
	
	def get_link(self):
		return current.request.args(LINKHTML)
		
	def get_row(self,tablename=None,link=None):
		
		tablename = tablename or self.get_table()
		link = link or self.get_link()
		table = self.define_table(tablename)
		
		dcontent = self.define_dcontent()
		row = self.db((dcontent.dtable==tablename)&(dcontent.link==link)).select().last()
		return table(row.table_id) if row else None

	def content(self,tablename=None,link=None):
		tablename = tablename or self.get_table()
		row = self.get_row(tablename,link)
		if row:
			dcontent = DIV(_class='content_%s'%tablename)
			dcontent.append(SPAN(row.name,_class='name-%s'%tablename))
			dcontent.append(SPAN(row.description,_class='description-%s'%tablename))
			dcontent.append(SPAN(IMG(_src=self.get_avatar(tablename,row.avatar)),_class='avatar-%s'%tablename))
		else:
			dcontent = DIV('%s %s'(link,current.T('not found!'),_class='content_%s'%tablename))
		return dcontent
	
	def box(self,boxname,folder=None,page=None,length=None,tablename=None,link=None,context={}):
		if current.request.controller=='plugin_box':
			self.define_box()
			row = self.db(self.db.box.name==boxname).select().first()
			return IMG(_src=URL(r=current.request,c='static',f='plugin_box/avatar',args=[row.avatar]),_id=boxname,_class='ivinhcmsbox-img')
		if folder:
			context['rows'] = self.get_rows(folder,page,length)
		elif tablename:
			context['row'] = self.get_row(tablename,link)
		return DIV(self.render(boxname=boxname,context=context),_id=boxname,_class='ivinhcmsbox')
		
	def pagination(self,folder=None,page=None,length=None,count=None,tablename=None):
		PAGE = 1
		T = current.T
		request = current.request
		args = request.args
		folder = folder or self.get_folder(folder)
		length = length or self.get_length(folder)
		
		if len(args) < PAGE: return ''
		elif len(args) == PAGE: args.append('1.html')
		
		count = count or self.get_count(folder,tablename)
		if count<=length: return ''
		
		page = page or self.get_page()
		
		if length>0:
			tmp = int(count/length)
			if count > tmp*length: pagecount = tmp+1
			else: pagecount = tmp
		content = DIV(_id='page')
		ul = UL(_class='page-ul pagination')
		(p1, m1) = (page - 5,'...') if page > 5 else (1, '')
		(p2, m2) = (page + 5,'...') if page + 5 < pagecount else (pagecount+1, '')
		if (p2 < 11) & (pagecount >10): p2 = 11
		if m1=='...':
			args[PAGE]='1.html'
			# url = URL(r=request,args=args,vars=request.vars)
			url ='../'+ request.args(0) +'/1.html'
			ul.append(LI(A(T('First page'),'  ',_href=url)))
			ul.append(LI(A(m1)))
		for x in xrange(p1,p2):
			args[PAGE]='%s.html'%x
			# url = URL(r=request,args=args,vars=request.vars)
			url ='../'+ request.args(0) + '%s.html'%x
			ul.append(LI(A(x,'  ',_href=url),_class='active' if x == page else ''))
		if m2=='...':
			ul.append(LI(A(m2)))
			args[PAGE]='%s.html'%pagecount
			# url = URL(r=request,args=args,vars=request.vars)
			url ='../'+ request.args(0) + '%s.html'%pagecount
			ul.append(LI(A(T('End page'),_href=url)))
		content.append(ul)
		return content			
	
	def metatile(self):
		from plugin_config import Configsite
		return Configsite().page_title
		
	def metadc(self):
		try:
			request = current.request
			tablename = self.get_table()
			table = self.define_dcontent()
			link = self.get_link()
			row = self.db((table.link==link)&(table.dtable==tablename)).select().first()
			from plugin_config import Configsite
			if not row: 
				meta ='''
					<title>%s</title>
					<link rel="shortcut icon" href="%s">
					<meta name="description" content="%s">
					<meta name="keywords" content="%s">
					<meta property="og:type"               content="article" />
					<meta property="og:title"              content="%s" />
					<meta property="og:description"              content="%s" />
					<meta property="og:image"              content="%s" />
				'''%(self.folder_name() +'  - '+Configsite().page_title,Configsite().page_icon,self.folder_des(),Configsite().page_keywords,Configsite().page_title,self.folder_des(),Configsite().page_logo)
				return XML(meta)
			indeitifier = '//%s%s'%(request.env.http_host,request.env.path_info)
			source = '//%s'%(request.env.http_host)
			# import os, uuid
			# avatar = 'http://%s/cms/static/site/%s/uploads/%s/%s'%(request.env.http_host,self.site_name,tablename,row.avatar) 
			# if not os.path.exists(avatar):
				# avatar = 'http://%s/cms/static/site/%s/uploads/%s/%s'%(request.env.http_host,self.site_name,'ckeditor',row.avatar) 
				
			import os, uuid
			avatar=Configsite().page_logo
			if row.avatar:
				if os.path.exists(request.folder+'/static/uploads/'+tablename+'/'+ row.avatar):
					avatar='//'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ row.avatar
				elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ row.avatar):
					avatar='//'+request.env.http_host +'/'+request.application+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ row.avatar
				elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ row.avatar):
					avatar='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ row.avatar
				elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/images_download/'+ row.avatar):
					avatar='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/images_download/'+ row.avatar
			else:
				table = self.define_table(tablename)
				row_c = self.db[table][row.table_id]
				if row_c.avatar:
					if os.path.exists(request.folder+'/static/uploads/'+tablename+'/'+ row_c.avatar):
						avatar='//'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ row_c.avatar
					elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ row_c.avatar):
						avatar='//'+request.env.http_host +'/'+request.application+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ row_c.avatar
					elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ row_c.avatar):
						avatar='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ row_c.avatar
					elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/images_download/'+ row_c.avatar):
						avatar='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/images_download/'+ row_c.avatar
				
				
			meta_title = row.name + '  '+Configsite().page_title
			if row.meta_title:
				meta_title= row.meta_title
			
			meta_description = row.description
			if row.meta_description:
				meta_description= row.meta_description
				
			meta = '''
			<title>%s</title>
			<link rel="shortcut icon" href="%s">
			<meta name="DC.Title" content="%s">
			<meta name="DC.Creator" content="%s">
			<meta name="DC.Date.Created" scheme="W3CDTF" content="%s" >
			<meta name="DC.Date.Modified" scheme="W3CDTF" content="%s" >
			<meta name="DC.Date.Valid" scheme="W3CDTF" content="%s" >
			<meta name="DC.Date.Issued" scheme="W3CDTF" content="%s" >
			<meta name= "DC.Publisher" content= "%s"> 
			<meta name="DC.Description" content="%s">
			<meta name="DC.Inditifier" content="%s">
			<meta name="DC.Languague" content="%s">
			<meta name= "DC.Source" content= "%s">
			<meta name="DC.Contributor" content="">
			<meta name="DC.Subject" content="%s">
			<meta name="DC.Coverage" content="Việt Nam">
			<meta name="DC.Type" content="Text">
			<meta name="DC.Format" content="text/html">
			<meta property="og:title" content="%s" />
			<meta property="og:type" content="Website" />
			<meta property="og:url" content="%s" /> 
			<meta property="og:image" content="%s" />
			<meta property="og:image:width" content="600">
			<meta property="og:image:height" content="460">
			<meta property="og:description" content="%s" />
			<meta property="og:site_name" content="%s" />
			<meta property="article:published_time" content="%s" /> 
			<meta property="article:section" content="%s" />''' %(meta_title ,Configsite().page_icon,meta_title,row.creator,row.created_on,row.modified_on,row.publish_on,row.publish_on,row.publisher,meta_description,indeitifier,row.languague,source,row.folder.label,meta_title,indeitifier,avatar,meta_description,self.metatile() ,row.publish_on,row.folder.label)
			return XML(meta)
		except Exception, e: 
			print e
			return ''
	
	def metadc_van_tai(self):
		try:
			request = current.request
			tablename = self.get_table()
			table = self.define_dcontent()
			link = self.get_link()
			row = self.db((table.link==link)&(table.dtable==tablename)).select().first()
			from plugin_config import Configsite
			if not row: 
				meta_title = self.folder_name() +' - '+Configsite().page_title
				meta_des = self.folder_des()
				meta_keywords = Configsite().page_keywords
				if request.args(1)=='vinh_di':
					d_tinh = self.define_table('d_tinh')
					d_huyen = self.define_table('d_huyen')
					d_xa = self.define_table('d_xa')
					meta_title = "Bảng giá taxi tải Vinh đi " 
					if request.vars.xa:
						r_xa = self.db.d_xa[request.vars.xa]
						if r_xa:
							meta_title += r_xa.name +", " + r_xa.d_huyen.name +", "+ r_xa.d_huyen.d_tinh.name
				
				meta ='''
					<title>%s</title>
					<link rel="shortcut icon" href="%s">
					<meta name="description" content="%s">
					<meta name="keywords" content="%s">
					<meta property="og:type"               content="article" />
					<meta property="og:title"              content="%s" />
					<meta property="og:description"              content="%s" />
					<meta property="og:image"              content="%s" />
				'''%(meta_title,Configsite().page_icon,meta_des ,meta_keywords,meta_title,self.folder_des(),Configsite().page_logo)
				return XML(meta)
			indeitifier = '//%s%s'%(request.env.http_host,request.env.path_info)
			source = '//%s'%(request.env.http_host)
			# import os, uuid
			# avatar = 'http://%s/cms/static/site/%s/uploads/%s/%s'%(request.env.http_host,self.site_name,tablename,row.avatar) 
			# if not os.path.exists(avatar):
				# avatar = 'http://%s/cms/static/site/%s/uploads/%s/%s'%(request.env.http_host,self.site_name,'ckeditor',row.avatar) 
				
			import os, uuid
			avatar=Configsite().page_logo
			if row.avatar:
				if os.path.exists(request.folder+'/static/uploads/'+tablename+'/'+ row.avatar):
					avatar='//'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ row.avatar
				elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ row.avatar):
					avatar='//'+request.env.http_host +'/'+request.application+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ row.avatar
				elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ row.avatar):
					avatar='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ row.avatar
				elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/images_download/'+ row.avatar):
					avatar='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/images_download/'+ row.avatar
			else:
				table = self.define_table(tablename)
				row_c = self.db[table][row.table_id]
				if row_c.avatar:
					if os.path.exists(request.folder+'/static/uploads/'+tablename+'/'+ row_c.avatar):
						avatar='//'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ row_c.avatar
					elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ row_c.avatar):
						avatar='//'+request.env.http_host +'/'+request.application+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ row_c.avatar
					elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ row_c.avatar):
						avatar='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ row_c.avatar
					elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/images_download/'+ row_c.avatar):
						avatar='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/images_download/'+ row_c.avatar
				
				
			meta_title = row.name + '  '+Configsite().page_title
			if row.meta_title:
				meta_title= row.meta_title
			
			meta_description = row.description
			if row.meta_description:
				meta_description= row.meta_description
				
			meta = '''
			<title>%s</title>
			<link rel="shortcut icon" href="%s">
			<meta name="DC.Title" content="%s">
			<meta name="DC.Creator" content="%s">
			<meta name="DC.Date.Created" scheme="W3CDTF" content="%s" >
			<meta name="DC.Date.Modified" scheme="W3CDTF" content="%s" >
			<meta name="DC.Date.Valid" scheme="W3CDTF" content="%s" >
			<meta name="DC.Date.Issued" scheme="W3CDTF" content="%s" >
			<meta name= "DC.Publisher" content= "%s"> 
			<meta name="DC.Description" content="%s">
			<meta name="DC.Inditifier" content="%s">
			<meta name="DC.Languague" content="%s">
			<meta name= "DC.Source" content= "%s">
			<meta name="DC.Contributor" content="">
			<meta name="DC.Subject" content="%s">
			<meta name="DC.Coverage" content="Việt Nam">
			<meta name="DC.Type" content="Text">
			<meta name="DC.Format" content="text/html">
			<meta property="og:title" content="%s" />
			<meta property="og:type" content="Website" />
			<meta property="og:url" content="%s" /> 
			<meta property="og:image" content="%s" />
			<meta property="og:image:width" content="600">
			<meta property="og:image:height" content="460">
			<meta property="og:description" content="%s" />
			<meta property="og:site_name" content="%s" />
			<meta property="article:published_time" content="%s" /> 
			<meta property="article:section" content="%s" />''' %(meta_title ,Configsite().page_icon,meta_title,row.creator,row.created_on,row.modified_on,row.publish_on,row.publish_on,row.publisher,meta_description,indeitifier,row.languague,source,row.folder.label,meta_title,indeitifier,avatar,meta_description,self.metatile() ,row.publish_on,row.folder.label)
			return XML(meta)
		except Exception, e: 
			print e
			return ''
			
	def metakopo(self,meta_title,avatar,meta_description):
		from plugin_config import Configsite
		meta = '''
			<title>%s</title>
			<link rel="shortcut icon" href="%s">
			<meta name="DC.Title" content="%s">
			<meta name="DC.Description" content="%s">
			<meta property="og:title" content="%s" />
			<meta property="og:image" content="%s" />
			<meta property="og:image:width" content="600">
			<meta property="og:image:height" content="460">
			<meta property="og:description" content="%s" />
			<meta property="article:section" content="%s" />''' %(meta_title ,Configsite().page_icon,meta_title,meta_description,meta_title,avatar,meta_description,self.metatile())
		return XML(meta)

	def field_format(self,row,field,type,settings):	
		try:
			if settings.get('reference_%s'%field,None):
				value = row[field][settings.get('reference_%s'%field,'id')]
			elif field=="PortletHeaderByName":
				return self.folder_name()
			elif field=="PortletAttachment":
				attach = FileUpload(db=self.db,tablename=settings.get('table'),table_id=row.id,upload_id=0)
				return attach.view_publish()
			elif field=="PortletComment":
				return "Comment..."
			else:
				value = row[field]
				if not value: return ""
				if field in settings.get('images',[]):		
					
					tablename = settings.get('table')
					request = current.request
					if tablename=='dcontent': tablename = row['dtable']
					browser=request.env.http_user_agent
					if value[0:7] == 'http://':
						pass
					elif os.path.exists(request.folder+'/static/uploads/'+tablename+'/'+ value):
						value='//'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ value
					elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ value):
						if  (settings.get('size_%s'%(field) ,'')!='default')&(settings.get('size_%s'%(field) ,'')!=''):
							size = (settings.get('size_%s'%(field) ,'')).split('x')
							value = self.get_avatar_by_size(tablename,value,size_w=size[0],size_h=size[1])
							# value='//'+request.env.http_host +'/'+request.application+'/static/uploads/'+tablename+'/'+ value
						else:
							if (self.site_name=="vantainamloc")&('Chrome' in browser):
								value = self.get_avatar_webp(tablename,value)
							else:
								value='//'+request.env.http_host +'/'+request.application+'/static/site/'+self.site_name+'/uploads/'+tablename+'/'+ value

					elif os.path.exists(request.folder+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ value):
						url = request.folder+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ value
						if  (settings.get('size_%s'%(field) ,'')!='default')&(settings.get('size_%s'%(field) ,'')!=''):
							size = (settings.get('size_%s'%(field) ,'')).split('x')
							value = self.get_avatar_by_url(tablename,url,value,size_w=size[0],size_h=size[1])
						else:
							if (self.site_name=="vantainamloc")&('Chrome' in browser):
								value = self.get_avatar_ck_webp(tablename,url,value)
							else:
								value='//'+request.env.http_host+'/'+request.application+'/static/site/'+self.site_name+'/uploads/ckeditor/'+ value
					else:
						value='//'+request.env.http_host+'/'+request.application+'/static/images/img_defautl.jpg'
				else:
					length = settings.get('length_%s'%field,"")
					format = settings.get('format_%s'%field,"")
					if length != "": 
						value = get_short_string(value,int(length))
					elif format != "":
						if type in ['integer','double']:
							value = format.format(value)
						elif type in ['date','datetime','time']:
							value = value.strftime(format)
					if type=="text": value = XML(value)
					style = get_style(field,settings)
					if style != "": value = SPAN(value,_style=style)
			return value
		except Exception, e:
			print "plugin_cms.field_format: ", e, field
			return ""
		
	def insert_read(self):
		foldername = current.request.args(0)
		tablename = current.request.args(1)
		link = current.request.args(2)
		if link :
			if (tablename !='img') &(tablename!='images'):
				table = self.define_readcontent()
				clientip = current.request.client
				user_agent = str(current.request.user_agent())
				table.insert(foldername=foldername,tablename=tablename,link=link,clientip=clientip,user_agent=user_agent)
	
	def count_read_product(self,link=None):
		link = link or current.request.args(2)
		table = self.define_readcontent()
		return self.db(table.link==link).count()

	def top_read_product(self,top=10,foldername=None,tablename=None):
		db = self.db
		table = self.define_readcontent()
		count = table.link.count()
		limitby = (0,top)
		query = (table.foldername==foldername) if foldername else table.id>0
		if tablename:
			query&= (table.tablename==tablename)
		rows = db(query).select(table.link, count, groupby=table.link, limitby=limitby, orderby=~count)
		return rows
		
	def top_read_new(self,top=10,foldername=None,tablename=None):
		db = self.db
		table = self.define_readcontent()
		count = table.link.count()
		limitby = (0,top)
		query = (table.foldername==foldername) if foldername else table.id>0
		if tablename:
			query&= (table.tablename==tablename)
		rows = db(query).select(groupby=table.link, limitby=limitby, orderby=~count)
		return rows

	def list_menu(self,id):
		import requests
				
		api_naso ="https://website:gkajhsafplafgalsda@banhang.bahadi.vn/app"
		# api_naso ="http://admin:123456@quanly.naso.vn/naso"
		url_folder = '%s/api/v1/folder/%s.json?field=parent&order=display_order'%(api_naso,id)
		rf = requests.get(url_folder).json()
		r_folder=rf['result']
		if len(r_folder)>0:
			ul = UL()
			for f in r_folder:
				li = LI(A(f['label'] ,_href=URL(r=current.request,c='portal',f='folder',args=[f['name'] ])))
				dq = self.list_menu(f['id'] )
				if dq !="":
					li.append(dq)
				ul.append(li)
			return ul
		else: return ""

	def menu_mobile(self):
		return self.list_menu(35)
		
###################################################
# ADMIN APPLICATION
###################################################		
			
class CmsPublish(CmsModel):

	def get_link(self,table,link):
		i = 1
		tmp = link
		while self.db(table.link==tmp).count()>0:
			tmp = '%s-%s.html'%(link.split('.')[0],i) 
			i+=1
		return tmp

	def get_content(self,tablename,table_id):
		from bs4 import BeautifulSoup
		table = self.define_table(tablename)
		row = self.db[tablename](table_id)
		content = ''
		try:
			for field in table.fields:
				if table[field].type == 'string':
					content += '%s\n'%row[field]
				elif table[field].type == 'text':
					soup = BeautifulSoup(row[field])
					content = '%s\n%s'%(content,soup.text.encode('utf-8'))
		except Exception, e:
			pass
		return content
		
	def publish(self,tablename,table_id,publish_on,expired_on):
		table = self.define_table(tablename)
		row = self.db[tablename](table_id)
		link = row.name.replace('đ','d').replace("Đ","D")
		link = '%s.html'%IS_SLUG.urlify(link)
		dcontent = self.define_dcontent()
		link = self.get_link(dcontent,link)
		content = self.get_content(tablename,table_id)
		try:
			auth = current.globalenv['auth']
			creator = '%s %s' % (auth.user.last_name, auth.user.first_name)
			publisher = auth.db.auth_group(auth.auth_org).role
		except:
			creator = ''
			publisher = ''
		value = dict(dtable=tablename,table_id=table_id,link=link,publish_on=publish_on,expired_on=expired_on,textcontent=content,publisher=publisher,creator=creator)		
		if 'publish_on' in table.fields: row.update_record(publish_on=publish_on)
		if 'expired_on' in table.fields: row.update_record(expired_on=expired_on)
		for field in ['folder','name','description','avatar']:
			if field in table.fields: value[field] = row[field]
		dcontent.insert(**value)
		return ''
		
	def publish_one(self,tablename,table_id,publish_on,expired_on,meta_title,meta_description,meta_keywords):
		table = self.define_table(tablename)
		row = self.db[tablename](table_id)
		link = row.name.replace('đ','d').replace("Đ","D")
		link = '%s.html'%IS_SLUG.urlify(link)
		dcontent = self.define_dcontent()
		link = self.get_link(dcontent,link)
		content = self.get_content(tablename,table_id)
		try:
			auth = current.globalenv['auth']
			creator = '%s %s' % (auth.user.last_name, auth.user.first_name)
			publisher = auth.db.auth_group(auth.auth_org).role
		except:
			creator = ''
			publisher = ''
		value = dict(dtable=tablename,table_id=table_id,link=link,publish_on=publish_on,expired_on=expired_on,textcontent=content,publisher=publisher,creator=creator,meta_title=meta_title,meta_description= meta_description,meta_keywords = meta_keywords)		
		if 'publish_on' in table.fields: row.update_record(publish_on=publish_on)
		if 'expired_on' in table.fields: row.update_record(expired_on=expired_on)
		for field in ['folder','name','description','avatar']:
			if field in table.fields: value[field] = row[field]
		dcontent.insert(**value)
		return ''
	
	def unpublish(self,tablename,table_id):
		table = self.define_table(tablename)
		# row = self.db[tablename](table_id)
		dcontent = self.define_dcontent()
		self.db((dcontent.dtable==tablename)&(dcontent.table_id==table_id)).delete()
		return ''
		
	def update(self,tablename,table_id):
		table = self.define_table(tablename)
		if "link" not in table.fields: return ""
		row = table(table_id)
		if not row.link: return ""
		link = row.name.replace('đ','d')
		link = '%s.html'%IS_SLUG.urlify(link)
		if link != row.link: link = self.get_link(table,link)
		elif self.db((table.id!=table_id)&(table.link==link)).count()>0: link = self.get_link(table,link)
		dcontent = self.define_dcontent()
		content = self.get_content(tablename,table_id)
		value = dict(link=link,textcontent=content,modified_on=current.request.now)		
		for field in ['folder','name','description','avatar']:
			if field in table.fields: value[field] = row[field]
		self.db((dcontent.dtable==tablename)&(dcontent.link==row.link)).update(**value)
		return ''
	
	def update_meta(self,tablename,table_id,meta_title,meta_description,meta_keywords):
		dcontent = self.define_dcontent()
		value = dict(meta_title=meta_title,meta_description= meta_description,meta_keywords = meta_keywords)		
		self.db((dcontent.dtable==tablename)&(dcontent.table_id==table_id)).update(**value)
		return ''
	
	def update_no_link(self,tablename,table_id):
		table = self.define_table(tablename)
		row = table(table_id)
		dcontent = self.define_dcontent()
		content = self.get_content(tablename,table_id)
		value = dict(textcontent=content,modified_on=current.request.now)		
		for field in ['folder','name','description','avatar']:
			if field in table.fields: value[field] = row[field]
		self.db((dcontent.dtable==tablename)&(dcontent.table_id==table_id)).update(**value)
		return ''
	
	def delete(self,tablename,table_id):
		table = self.define_table(tablename)
		dcontent = self.define_dcontent()
		self.db((dcontent.dtable==tablename)&(dcontent.table_id==table_id)).delete()
		self.db(table.id==table_id).delete()
		return ''
				
		
class CmsCrud(CmsModel):

	# def widget_layout(self, field, value):
		# files = []
		# for root, dirs, files in os.walk(current.request.folder+'/views/layout'):
			# pass
		# op = [OPTION(file,_value=file,_selected=(value==file)) for file in files]
		# widget = SELECT([""]+op,_name=field.name,_id=field._tablename+'_'+field.name,_class="form-control")
		# return widget
		
	def widget_layout(self, field, value):
		import os
		files = []
		from plugin_config import Configsite
		site_name = Configsite().site_name
		template = Configsite().template
		if template !='':
			for root, dirs, files in os.walk(current.request.folder+'/views/site/%s/%s'%(site_name,template)):
				pass
		else:
			for root, dirs, files in os.walk(current.request.folder+'/views/site'):
				pass
		op = [""]+[OPTION(file,_value=file,_selected=(value==file)) for file in files]
		widget = SELECT(op,_name=field.name,_id=field._tablename+'_'+field.name,_class="form-control")
		return widget
		
	def folder(self):	
		from sqlhtml import SQLFORM
		table = self.define_folder()
		table.parent.widget = self.widget_folder
		table.layout.widget = self.widget_layout
		return table
		
	def dtable(self):	
		class VALIDATOR_DB_KEYWORD(object):
			def __init__(self, db, error_message="SOMETHING WRONG"):
				self.error_message = error_message
				self.db = db
			def __call__(self, value):
				error = None
				try:
					table = self.db.define_table(value,Field('testfield','string'),migrate=True)
				except Exception, e:
					error = e
				return (value, error)
		table = self.define_dtable()
		table.name.requires = [VALIDATOR_DB_KEYWORD(self.db),IS_NOT_IN_DB(self.db,table.name)]
		# tablefield = self.tablefield()
		# tablefield.dtable.widget = SQLFORM.widgets.options.widget
		# table.layout.widget = self.widget_layout
		return table

	def dfield(self):	
		from sqlhtml import SQLFORM
		def widget_type(field, value):
			list_types = ['blob','boolean','date','datetime','double','integer','list:integer','list:reference','list:string','reference','string','text','time','upload']			
			op = [OPTION(name,_value=name,_selected=str(value).startswith(name)) for name in list_types]
			url = URL(r=current.request,c='plugin_cms',f='widget_type',vars=dict(value=value))
			ajax = "ajax('%s',['fieldtype'],'widget_type')"%(url)
			tables = LOAD(url=url) if value else ''
			widget = SPAN(SELECT(op,_name='fieldtype',_id="fieldtype",_onchange=ajax)," ",SPAN(tables,_id='widget_type'))
			widget.append(INPUT(_type='hidden',_value=value,_name=field.name,_id=field._tablename+'_'+field.name))
			return widget
			
		class VALIDATOR_DB_KEYWORD(object):
			def __init__(self, db, error_message="SOMETHING WRONG"):
				self.error_message = error_message
				self.db = db
			def __call__(self, value):
				error = None
				try:
					table = self.db.define_table('table_check_keyword',Field(value,'string'),migrate=True)
					self.db.table_check_keyword.drop()
				except Exception, e:
					error = e
				return (value, error)
		
		table = self.define_dfield()
		table.ftype.widget = widget_type
		table.name.requires = [VALIDATOR_DB_KEYWORD(self.db),IS_NOT_IN_DB(self.db,table.name)]
		return table
		
	def tablefield(self):	
		from sqlhtml import SQLFORM
		def widget_field(field, value):
			ftype = self.db.dfield(value).ftype if self.db.dfield(value) else 'string'
			list_types = ['blob','boolean','date','datetime','double','integer','list:integer','list:reference','list:string','reference','string','text','time','upload']			
			url = URL(r=current.request,c='plugin_cms',f='widget_field',vars=dict(value=value or 0,ftype=ftype))
			ajax = "ajax('%s',['fieldtype'],'widget_field')"%(url)
			if len(ftype.split(' '))==3: ftype = ftype.split(' ')[0] + ' ' + ftype.split(' ')[1]
			rows = self.db(self.db.dfield.ftype.startswith(ftype)).select()
			op = [OPTION(row.name,_value=row.id,_selected=(row.id==value)) for row in rows]
			dfield = SELECT(op,_name='dfield',_id='tablefield_dfield')
			
			op = [OPTION(name,_value=name,_selected=ftype.startswith(name)) for name in list_types]			
			widget = SPAN(SELECT(op,_name='fieldtype',_id="fieldtype",_onchange=ajax)," ", SPAN(dfield,_id='widget_field'))
			return widget

		def widget_table(field, value):
			if not value: return SQLFORM.widgets.options.widget(field,value)
			self.db.tablefield.dtable.default = value
			rows = self.db(self.db.tablefield.dtable==value).select(orderby=self.db.tablefield.display_order)
			widget = DIV()
			for row in rows: 
				widget.append(B(row.dfield.name))
				widget.append('(%s) '%(row.dfield.ftype))
			return widget
			
		table = self.define_tablefield()
		table.dfield.widget = widget_field
		table.dtable.widget = widget_table
		return table

	