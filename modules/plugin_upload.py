# -*- coding: utf-8 -*-
###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 28/02/2012
# Version 0.2 Date: 28/02/2014
###################################################
from gluon import current, LOAD
from html import *
from gluon.dal import Field
from validators import IS_LENGTH
import os

TABLENAME	=0
TABLE_ID	=1
UPLOAD_ID 	=2 
FILENAME 	=3
from plugin_app import get_short_string

class FileUpload:
	def __init__(self,**attr):
		request = current.request
		self.db = attr.get('db',current.globalenv.get("db"))
		self.auth = attr.get('auth',current.globalenv.get('auth'))
		self.pkey = attr.get('pkey', request.vars.pkey)
		self.url = attr.get('url', request.vars.url)
		self.tablename = attr.get('tablename', request.args(TABLENAME) or 'documents')
		self.table_id = attr.get('table_id', request.args(TABLE_ID) or 1)
		self.upload_id = attr.get('upload_id', request.args(UPLOAD_ID) or 0)
		self.table = attr.get('table','file_upload')
		self.upload = self.define_table(False)
		if self.upload_id:
			temp = self.upload(self.upload_id).created_on
			self.filename = self.upload(self.upload_id).filename
		else:
			temp = request.now
			self.filename = request.args(FILENAME)
		year, month = temp.year, temp.month
		
		from plugin_config import Configsite
		self.site_name = Configsite().site_name

		self.path = '%s/static/site/%s/uploads/%s/%s/%s'%(current.request.folder,self.site_name,year,month,self.tablename)
		self.path_old = '%s/uploads/%s/%s/%s'%(current.request.folder,year,month,self.tablename)
		self.online = attr.get('online',False)
		self.convertcontent = attr.get('convertcontent',False)
		self.docx = attr.get('docx',current.request.vars.docx)
		self.pdf = attr.get('pdf',current.request.vars.pdf)
	
	def define_table(self,migrate=False):
		db = self.db
		if self.table not in db.tables:
			db.define_table(self.table,
				Field('pkey'),
				Field('tablename'),
				Field('table_id'),
				Field('name'),
				Field('filetype'),
				Field('extension'),
				Field('fileversion'),
				Field('filesize','double'),
				Field('filecomment','text',default=''),
				Field('filename','upload'),
				Field('publish','boolean',default=True),
				Field('textcontent','text',default='',requires=IS_LENGTH(16777215)),
				Field('created_by','integer',default=self.auth.user_id if self.auth else 1,writable=False,readable=False),
				Field('created_on','datetime',default=current.request.now,writable=False,readable=False),
				migrate=migrate)
		return db[self.table]

	def get_filepath(self,row):	
		temp = row.created_on
		filename = row.filename
		year, month = temp.year, temp.month
		path = '%s/static/site/%s/uploads/%s/%s/%s'%(current.request.folder,self.site_name,year,month,self.tablename,filename)
		return path
		
	def js_preview(self):	
		return SCRIPT('''
			function jspreview(url){
				var ext = url.substring(url.lastIndexOf('.') + 1).toLowerCase();
				var element=document.getElementById("content");
				if (/^(tiff|ppt|pps|doc|docx|rtf|xls|xlsx)$/.test(ext)) {
					var new_url = url.replace('preview','msdoc');
					$.ajax({
							url: new_url,
							type: "GET",
							data: '',
							cache: true,
							success: function (html) {
								if (html!='') {
									alert(html);
									$.colorbox({html:'<iframe src="http://docs.google.com/viewer?url='+html+'&embedded=true" width="90%" height="95%" style="border: none;"></iframe>'});
								}
							}
					});
				}
				else if (/^(pdf|txt)$/.test(ext)) {
					$.colorbox({href:url,width:"90%",height:"95%",iframe:true});
				}
				else if (/^(png|jpg|jpeg|bmp)$/.test(ext)) {
					$.colorbox({href:url,maxWidth:"90%",maxHeight:"95%"});
				}
				else if (/^(odt)$/.test(ext)) {
					//loadDaFun();
					//var odfcanvas = new odf.OdfCanvas(content);
					//odfcanvas.load(url);
					element.innerHTML= '<iframe src="../webodf/webodf.html?url=http://127.0.0.1:8000/app/static/plugin_viewer/webodf/test1.odt" width="600" height="700" style="border: none;"></iframe>';
				}
				else {
					$.colorbox({href:url,width:"800",height:"700"});
				}
			}''')
	
	def js_colorbox(self):
		request = current.request
		return '''<link href="%s/colorbox/colorbox.css" rel="stylesheet" type="text/css" />
		<script type="text/javascript" src="%s/colorbox/jquery.colorbox.js"></script>
		'''%(URL(r=request,c='static',f='plugin_app'),URL(r=request,c='static',f='plugin_app'))
	
	def js_upload(self,js="dragndrop",css="dragndrop"):
		request = current.request
		url = URL(r=request,c='static',f='plugin_upload') 
		return '''<link href="%s/%s.css" rel="stylesheet" type="text/css" /> 
		<script type="text/javascript" src="%s/%s.js"></script>
		'''%(url,css,url,js)
	
	def formupload(self,colorbox=True,signed=False,view=None,title="Attachment"):
		from plugin_app import ColorBox
		request = current.request
		button1 = SPAN(ColorBox(caption=current.T('Scan'),source=URL(r=request,c='plugin_scan',f='scan',args=request.args,vars=request.vars),url=URL(r=request,f='view',args=request.args,vars=request.vars),target='progress',width='100%',height='100%'),_id='button_scan')
		button2 = SPAN(A(current.T(title),_class='btn btn-danger'),_id="upfile1",style="cursor:pointer")
		button3 = INPUT(_id="data_file_file", _class="", _type="file", _name="file",_style="display:none")
		button4 = "" #SPAN(INPUT(_id="convert_pdf", _class="", _type="checkbox", _name="convert_pdf", _checked=True),current.T('PDF convert'))
		script = SCRIPT('''$("#upfile1").click(function () {$("#data_file_file").trigger('click');});''')
		# form = FORM(button1, ' ', button2, button3, button4, script)
		form = FORM(button2, button3, button4, script)
		form.attributes['_id'] = "myform"
		vars = request.vars
		if self.pkey: vars["pkey"] = self.pkey
		if self.url: vars["url"] = self.url
		if self.docx: vars["docx"] = True
		if self.pdf: vars["pdf"] = True
		form.attributes['_action'] = URL(r=request,c='plugin_upload',f="upload_file",args=[self.tablename,self.table_id],vars=vars)
		table = DIV(DIV(view or self.view(),_id="progress"),_id="filedrag")
		#table = DIV(DIV(self.view_list() if view_list else self.view(),_id="progress"),_id="filedrag")
		script = self.js_upload()
		if colorbox: script += self.js_colorbox()
		sign = LOAD(r=request,c="plugin_upload",f="sign.html",args=[self.tablename,self.table_id]) if signed else ""
		return DIV(form,table,sign,XML(script),self.js_preview(),DIV(_id='upload_content'))
		
	def formupload1(self,colorbox=True):
		from plugin_app import ColorBox
		request = current.request
		button1 = SPAN(ColorBox(caption=current.T('Scan'),source=URL(r=request,c='plugin_scan',f='scan',args=request.args,vars=request.vars),url=URL(r=request,f='view',args=request.args,vars=request.vars),target='progress',width='100%',height='100%'),_id='button_scan')
		button2 = SPAN(A(current.T('Attachment'),_class='btn btn-danger'),_id="upfile1",style="cursor:pointer")
		button3 = INPUT(_id="data_file_file", _class="", _type="file", _name="file",_style="display:none")
		button4 = SPAN(INPUT(_id="convert_pdf", _class="", _type="checkbox", _name="convert_pdf", _checked=True),current.T('PDF convert'))
		script = SCRIPT('''$("#upfile1").click(function () {$("#data_file_file").trigger('click');});''')
		# form = FORM(button1, ' ', button2, button3, button4, script)
		form = FORM( button2, button3, script)
		form.attributes['_id'] = "myform"
		form.attributes['_action'] = URL(r=request,c='plugin_upload',f="upload_file",args=[self.tablename,self.table_id],vars=request.vars)
		table = DIV(DIV(self.view_hinh_anh(),_id="progress"),_id="filedrag")
		script = self.js_upload()
		if colorbox: script += self.js_colorbox()
		return DIV(form,table,XML(script),self.js_preview(),DIV(_id='upload_content'))
		
	def formupload_media(self,colorbox=True):
		from plugin_app import ColorBox
		request = current.request
		button1 = SPAN(ColorBox(caption=current.T('Scan'),source=URL(r=request,c='plugin_scan',f='scan',args=request.args,vars=request.vars),url=URL(r=request,f='view',args=request.args,vars=request.vars),target='progress',width='100%',height='100%'),_id='button_scan')
		button2 = SPAN(A(current.T('Chọn tệp'),_class='btn btn-danger'),_id="upfile1",style="cursor:pointer")
		button3 = INPUT(_id="data_file_file", _class="", _type="file", _name="file",_style="display:none")
		button4 = SPAN(INPUT(_id="convert_pdf", _class="", _type="checkbox", _name="convert_pdf", _checked=True),current.T('PDF convert'))
		script = SCRIPT('''$("#upfile1").click(function () {$("#data_file_file").trigger('click');});''')
		# form = FORM(button1, ' ', button2, button3, button4, script)
		form = FORM( button2, button3, script)
		form.attributes['_id'] = "myform"
		form.attributes['_action'] = URL(r=request,c='plugin_upload',f="upload_file",args=[self.tablename,self.table_id],vars=request.vars)
		table = DIV(DIV(self.view_media(),_id="progress"),_id="filedrag")
		script = self.js_upload()
		if colorbox: script += self.js_colorbox()
		return DIV(H5(B('Đăng tải media')),I('Vui lòng chờ hệ thống xử lý tệp và hiện thông tin(Loại tệp, tên tệp, kích thước...) mới thực hiện thao tác tiếp theo'),form,table,XML(script),self.js_preview(),DIV(_id='upload_content'),_class='col-sm-12')

	def view_list(self):
		request = current.request
		T = current.T
		ul=UL(_class='file_attachment', _style="text-align:left;")
		if self.pkey: 
			query = (self.upload.pkey==self.pkey)
		else:
			query = (self.upload.tablename==self.tablename)&(self.upload.table_id==self.table_id)&(self.upload.publish==True)
		rows = self.db(query).select()
		for row in rows:
			args=[self.tablename,self.table_id,row.id,row.filename]
			icon = SPAN(_class='icon_'+row.extension)
			name = SPAN(icon,row.name,_class='upload_name')	
			
			td = A(name,_class='file_download',_href=URL(r=request,c='plugin_upload',f='download',args=args),_title=T('Click for download'))
			ul.append(LI(td))
		return ul					
	
	def get_row(self):
		rows = self.db((self.upload.tablename==self.tablename)&(self.upload.table_id==self.table_id)&(self.upload.publish==True)).select()
		return rows
	
	def view_publish(self,colorbox=True):
		request = current.request
		T = current.T
		table=TABLE(_class='upload_table')
		rows = self.db((self.upload.tablename==self.tablename)&(self.upload.table_id==self.table_id)&(self.upload.publish==True)).select()
		for row in rows:
			args=[self.tablename,self.table_id,row.id]
			tr = TR()
			td = SPAN(row.extension,_class='icon_'+row.extension)
			tr.append(TD(td))
			
			if os.path.isfile('%s/%s.pdf'%(self.path,row.name)):
				filename = '%s.pdf'%(row.name)
			else:
				filename = row.filename				
				
			ajax = "jspreview('%s');"%(URL(r=request,c='plugin_upload',f='preview',args=args+[filename]))
			from plugin_app import get_short_string2
			td = A(get_short_string2(row.name,30),_href='#',_onclick=ajax,_id='view_%s'%row.id,_class='icon_preview')		
			tr.append(TD(td))
			
			filesize= row.filesize or 0
			if filesize>1024*1024: filesize = str(round(filesize/1024*1024,2))+ 'Gb'
			elif filesize>1024: filesize = str(round(filesize/1024,2))+ 'Mb'
			elif filesize>1: filesize = str(int(filesize))+ 'Kb'
			else: filesize = str(round(filesize,2))+ 'Kb'
		
			td = A(T('Download'),_class='icon_download',_href=URL(r=request,c='plugin_upload',f='download',args=args+[row.filename]),_title=T('Download'))
			tr.append(TD(td))
					
			table.append(tr)
		script = ''	
		if colorbox: script += self.js_colorbox()
		return SPAN(DIV(table,_id="filedrag"),self.js_preview(),XML(script),_class='upload_publish')
		
	def view(self):
		try:
			from plugin_app import ColorBox
			request = current.request
			T = current.T
			table=TABLE(_class='table')
			if self.pkey: 
				query = (self.upload.pkey==self.pkey)
			else:
				query = (self.upload.tablename==self.tablename)&(self.upload.table_id==self.table_id)
			rows = self.db(query).select()
			for row in rows:
				args=[self.tablename,self.table_id,row.id]
				tr = TR()
				td = SPAN(row.extension,_class='icon_'+row.extension)
				tr.append(TD(td))
				
				if os.path.isfile('%s/%s.pdf'%(self.path,row.name)):
					filename = '%s.pdf'%(row.name)
				else:
					filename = row.filename				
				
				ajax = "jspreview('%s');"%(URL(r=request,c='plugin_upload',f='preview',args=args+[filename]))
				td = A(row.name,_href='#',_onclick=ajax,_id='view_%s'%row.id,_class='icon_preview')		
				tr.append(TD(td))
				
				filesize= row.filesize or 0
				if filesize>1024*1024: filesize = str(round(filesize/1024*1024,2))+ 'Gb'
				elif filesize>1024: filesize = str(round(filesize/1024,2))+ 'Mb'
				elif filesize>1: filesize = str(int(filesize))+ 'Kb'
				else: filesize = str(round(filesize,2))+ 'Kb'
				
				if self.convertcontent:
					if row.textcontent=='':
						ajax = "ajax('%s', [], 'upload_content')"%(URL(r=request,c='plugin_upload',f='extract',args=args,vars=request.vars))
						td = SPAN(A(T('Extract'),_href='#',_onclick=ajax,_class='icon_extract',_title=T('Extract')),_id='extract_%s'%row.id)
						tr.append(TD(td))
					else:
						td = SPAN(ColorBox(caption=current.T('Metadata'),source=URL(r=request,c='plugin_upload',f='textcontent',args=args),width='80%',height='80%'),_class='textcontent_view')
						tr.append(TD(td))
				
				td = A(T('Download'),_class='icon_download',_href=URL(r=request,c='plugin_upload',f='download',args=args+[row.filename]),_title=T('Download'))
				tr.append(TD(td))
			
				if self.online:
					ajax = "ajax('%s', [], 'upload_content')"%(URL(r=request,c='plugin_upload',f='applet',args=args+[row.filename]))	
					td = A(T('Edit online'),_href='#',_onclick=ajax,_id='button_edit_online',_class='icon_edit_online',_title=T('Sửa bản thảo trực tuyến'))
					tr.append(TD(td))
				
				ajax = "ajax('%s', ['checkbox_publish_%s'], 'upload_content')"%(URL(r=request,c='plugin_upload',f='publish',args=args),row.id)	
				td = SPAN(T('Publish'),' ',INPUT(_type='checkbox',_onchange=ajax,_name='checkbox_publish_%s'%row.id,_checked=row.publish,_class='icon_publish'))
				tr.append(TD(td))
				
				ajax = "ajax('%s', [], 'progress')"%(URL(r=request,c='plugin_upload',f='del_file',args=args))
				td = A(T('Delete'),_href='#',_onclick=ajax,_class='icon_delete',_title=T('Delete'))
				tr.append(TD(td))
				
				table.append(tr)
			return table
		except Exception, e:
			return e
			
	def view_hinh_anh(self):
		try:
			from plugin_app import ColorBox
			request = current.request
			T = current.T
			table=UL(_class='view_hinh_anh')
			rows = self.db((self.upload.tablename==self.tablename)&(self.upload.table_id==self.table_id)).select()
			for row in rows:
				args=[self.tablename,self.table_id,row.id]
				tr = LI(_class='item_hinh_anh')
				if os.path.isfile('%s/%s.pdf'%(self.path,row.name)):
					filename = '%s.pdf'%(row.name)
				else:
					filename = row.filename		

				ajax = "ajax('%s', [], 'progress')"%(URL(r=request,c='plugin_upload',f='del_file',args=args))
				td = A(T('Delete'),_href='#',_onclick=ajax,_class='icon_delete',_title=T('Delete'))
				tr.append(TD(td))
				
				ajax = "jspreview('%s');"%(URL(r=request,c='plugin_upload',f='preview',args=args+[filename]))
				td = A(IMG(_class='view_img thumbnail',_src=URL(r=request,c='plugin_upload',f='download',args=args+[row.filename])),_href='#',_onclick=ajax,_id='view_%s'%row.id,_class='preview')		
				tr.append(TD(td))
				
				
				table.append(tr)
			return table
		except Exception, e:
			return e
			
	def view_media(self):
		try:
			from plugin_app import ColorBox
			request = current.request
			T = current.T
			table=TABLE(_class='table')
			rows = self.db((self.upload.tablename==self.tablename)&(self.upload.table_id==self.table_id)).select()
			for row in rows:
				args=[self.tablename,self.table_id,row.id]
				tr = TR()
				td = SPAN(row.extension,_class='icon_'+row.extension)
				
				tr.append(TD(td))
				
				if os.path.isfile('%s/%s.pdf'%(self.path,row.name)):
					filename = '%s.pdf'%(row.name)
				else:
					filename = row.filename				
				ajax = "jspreview('%s');"%(URL(r=request,c='plugin_upload',f='preview',args=args+[filename]))
				td = A(row.name,_href='#',_onclick=ajax,_id='view_%s'%row.id,_class='icon_preview')		
				tr.append(TD(td))
				
				filesize= row.filesize or 0
				if filesize>1024*1024: filesize = str(round(filesize/1024*1024,2))+ 'Gb'
				elif filesize>1024: filesize = str(round(filesize/1024,2))+ 'Mb'
				elif filesize>1: filesize = str(int(filesize))+ 'Kb'
				else: filesize = str(round(filesize,2))+ 'Kb'
				td = SPAN(filesize,_class='icon_'+row.extension)
				tr.append(TD(td))
				td = A(T('Download'),_class='icon_download',_href=URL(r=request,c='plugin_upload',f='download',args=args+[row.filename]),_title=T('Download'))
				tr.append(TD(td))
			
				ajax = "ajax('%s', [], 'progress')"%(URL(r=request,c='plugin_upload',f='del_file',args=args))
				td = A(T('Delete'),_href='#',_onclick=ajax,_class='icon_delete',_title=T('Delete'))
				tr.append(TD(td,_class='view_hinh_anh'))
				
				table.append(tr)
			return table
		except Exception, e:
			return e
						
	def delete(self):
		self.db(self.upload.id==self.upload_id).delete()
		try:
			os.remove('%s/%s'%(self.path,self.filename))
			os.remove('%s/%s.pdf'%(self.path,self.name))
		except:
			pass
			
	def update(self,id,uuid):
		self.db((self.upload.tablename==self.tablename)&(self.upload.table_id==uuid)).update(table_id=id)			

	def publish(self,is_publish=True):
		self.db((self.upload.id==self.upload_id)).update(publish=is_publish)			
		
	def rename(self,old_name,new_name):
		try:
			uploadfolder=os.path.join(self.path)
			os.rename(os.path.join(uploadfolder, old_name),os.path.join(uploadfolder, new_name))
			return new_name
		except: 
			return old_name
		
	def upload_file(self,fobject):
		try:
			import shutil
			from validators import IS_SLUG
			self.upload.pkey.default = self.pkey
			self.upload.tablename.default = self.tablename
			self.upload.table_id.default = self.table_id
			self.upload.filename.uploadfolder=os.path.join(self.path)
			filename=fobject.filename			
			extension = filename.split('.')[-1].lower()
			name = filename[:-(len(extension)+1)]
			name = name.replace('đ','d').replace("Đ","D")
			name = IS_SLUG.urlify(name)
			new_name = '%s.%s'%(name,extension)
			if not os.path.exists(self.path):
				os.makedirs(self.path)
			i = 1
			while os.path.isfile(self.path+'/'+new_name):
				new_name = '%s-%s.%s'%(name,i,extension)
				i+=1
			self.filename = new_name
			pathfilename = os.path.join(self.path,new_name)
			f = open(pathfilename,"wb")
			shutil.copyfileobj(fobject.file, f)
			f.close()
			filesize= (0.0+os.path.getsize(pathfilename))/1024
			if self.docx:
				if self.doc2docx(pathfilename):
					extension = "docx"
					new_name = new_name + "x"			
					pathfilename = os.path.join(self.path,new_name)
					filesize= (0.0+os.path.getsize(pathfilename))/1024
			id = self.upload.insert(name=name,extension=extension,filename=new_name,filesize=filesize)
			if current.request.vars.convert_pdf:	
				if extension in ['doc','docx','xls','xlsx','ppt','pptx']: self.msdoc2pdf(self.path+'/'+new_name)
			return pathfilename
		except Exception, e:
			print 'Upload to server error: %s'%e
			return None
		
	def msdoc2pdf(self,msfile):
		try: 
			import subprocess
			subprocess.Popen('C:\\Windows\\System32\\cscript.exe %sstatic\\plugin_upload\\save_pdf.js %s'%(current.request.folder,msfile))
		except Exception, e:
			print 'Convert MsDoc to PDF error: %s'%e

	def doc2docx(self,path,new_path=None):
		def get_cmd():
			for hdd in ["C","D","E","F"]:
				for program in ["Program Files","Program Files (x86)"]:
					for i in range(12,18):
						cmd = '%s:\\"%s\\Microsoft Office"\\Office%s\\wordconv.exe'%(hdd,program,i)
						path = '%s:\\%s\Microsoft Office\Office%s\wordconv.exe'%(hdd,program,i)
						if os.path.isfile(path): return cmd 
			return None
			
		try:
			if str(path).split(".")[-1] == "doc":
				cmd = get_cmd()
				if cmd:
					new_path = new_path or "%sx"%path
					cmd = '%s -oice -nme "%s" "%s"'%(cmd, path,new_path)
					(fi, fo, fe) = os.popen3(cmd)
					fi.close()
					return new_path
		except Exception, e:
			print 'Convert doc to docx error: %s'%e
		return None
		
	def getcontent(self,filepath):
		try: 
			import tesseract.utils as utils	
			txt, orc = utils.file_to_text(filepath)
			return txt		
		except Exception, e:
			print 'Get text content error: %s'%e
			return ''
		
	def dropzone(self,name="file",multiple=True):
		form = FORM(_class="dropzone", _action=URL(r=current.request,f="upload"))
		form.attributes['_action'] = URL(r=current.request,f="upload")
		form.append(DIV(INPUT(_name=name,_type="file",_multiple=multiple),_class="fallback"))
		table = DIV(DIV(self.view(),_id="progress"),_id="filedrag")
		script = self.js_upload(js="dropzone")
		return DIV(form,table,XML(script),DIV(_id='upload_content'))
		
	def widget_upload(self,field,value,c):
		url = URL(r=current.request,c='static',f='plugin_upload')
		form = '''
		<form id="upload" method="post" action="#" enctype="multipart/form-data">
			<div id="drop">
				Drop Here
				<a>Browse</a>
				<input type="file" name="file" multiple />
			</div>
			<ul>
				<!-- The file uploads will be shown here -->
			</ul>
		</form>
		'''
		return XML(form)
