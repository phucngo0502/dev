###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 28/07/2014
###################################################


from plugin_upload import FileUpload
fileupload = FileUpload(db=cms.db)

def index():
	form = fileupload.formupload()
	#form = fileupload.view_publish()
	return dict(form=form)

def preview(): 
	import os 
	path=os.path.join(fileupload.path,request.args(3))
	if not os.path.exists(path):
		path =os.path.join(fileupload.path_old,request.args(3))
	return response.stream(path)

@cache.action()	
def download():
	from gluon.contenttype import contenttype
	import os 
	path=os.path.join(fileupload.path,fileupload.filename) 
	if not os.path.exists(path):
		path =os.path.join(fileupload.path_old,fileupload.filename) 
	headers = response.headers
	headers['Content-Type'] = contenttype(fileupload.filename)
	headers['Content-Disposition'] = 'attachment; filename="%s"' % fileupload.filename
	return response.stream(path)
	
def upload_file():
	# inserts file and associated form data.
	fileupload.upload_file(request.vars.multi_file)
	if request.vars.url: 
		redirect(request.vars.url,client_side=True)
	return fileupload.view()

def msdoc():
	import os
	import shutil
	try:
		src = '%s/%s'%(fileupload.path,fileupload.filename)
		dest = '%s/static/uploads'%(request.folder)
		if not os.path.exists(dest):
			os.makedirs(dest)
		dest += '/googledoc'
		if not os.path.exists(dest):
			os.makedirs(dest)
		extension = fileupload.filename.split('.')[-1].lower()
		name = fileupload.filename[:-(len(extension)+1)]			
		newname = '%s.%s'%(IS_SLUG.urlify(name),extension)
		dest = '%s/%s'%(dest,newname)
		if not os.path.exists(dest):
			shutil.copy(src,dest)
		return 'http://%s/%s/static/uploads/googledoc/%s'%(request.env.http_host,request.application,newname)
	except Exception, e:
		print e
		return ""
	
def view():
	return fileupload.view()
	
def del_file():
	try:
		fileupload.delete()
		return fileupload.view()		
	except Exception, e:
		return e	

def publish():
	try:
		fileupload.publish(is_publish=('checkbox_publish_%s'%fileupload.upload_id in request.vars.keys()))
		return ''		
	except Exception, e:
		return e	
		
def textcontent():
	form = SQLFORM(fileupload.upload,fileupload.upload_id,fields=['textcontent'],showid=False,labels = {'textcontent':''})
	if form.process().accepted:
		return SCRIPT('parent.$.colorbox.close();')
	return dict(content=form)
		
def applet():
	#filepath = msdoc()
	#filepath = 'http://sonoivu.hatinh.gov.vn/vbsnv/static/test.docx'
	filepath = 'http://113.191.248.231/vendor/server.php/Decuong-TT21-2010.doc'
	script = '''<APPLET CODE="EditOnline.class" WIDTH=1 HEIGHT=0 ARCHIVE="EditOnline.jar" codebase="%s">
	  <param name="filename" value="%s"></APPLET>'''%(URL(r=request,c='static',f='plugin_upload'),filepath)
	return XML(script)

def basic2():
	return dict(content=fileupload.widget_upload(1,1,1))
	
def upload():
		# if type(fieldStorage) is unicode:
			# pass
	print request.vars.file
	
def sign():
	return dict()
	
def upload_sign():
	import os
	try:
		from plugin_upload import FileUpload
		fileupload = FileUpload(db=db,upload_id=None)
		upload = fileupload.upload
		upload.tablename.default = fileupload.tablename
		upload.table_id.default = fileupload.table_id or 1
		#upload.filename.uploadfolder=os.path.join(fileupload.path)
		filename=request.vars.filename
		extension = filename.split('.')[-1].lower()
		name = filename[:-(len(extension)+1)]
		new_name = '%s.%s'%(name,extension)
		d = os.path.dirname(fileupload.path)
		if not os.path.exists(d):
			os.makedirs(d)
		i = 1
		while os.path.isfile(fileupload.path+'/'+new_name):
			new_name = '%s(%s).%s'%(name,i,extension)
			i+=1
		f = open(fileupload.path+'/'+new_name,"wb")
		content = request.vars.file
		content = content.decode("base64")
		f.write(content)
		f.close()
		filesize= (0.0+os.path.getsize(fileupload.path+'/'+new_name))/1024
		id = upload.insert(name=name,extension=extension,filename=new_name)
		return fileupload.view() 
	except Exception, e:
		return e
	
	
	
	
####################################################################################	
def extract():
	try:
		a = fileupload.upload
		txt = a(fileupload.upload_id).textcontent or ''
		folder = T(request.vars.folder) if request.vars.folder else ''
		if txt == '':
			import tesseract.utils as utils	
			filename = '%s/%s'%(fileupload.path,fileupload.filename)
			txt, archives = utils.extract(filename,folder)
			fileupload.db(a.id==fileupload.upload_id).update(textcontent=txt)
		else:
			import tesseract.archives as arc
			if len(txt.split('\n'))<20: archives = arc.get_ocr(txt,folder)
			else: archives = arc.ArchivesText(txt,folder).extract()
		script=""
		if archives['name']:
			script += "$('#number').val('%s');$('#name').val('%s');$('#archives_name').val('%s/%s');"%(archives['name'][0],archives['name'][1],archives['name'][0],archives['name'][1])
		if archives['title']: 
			script+= "$('#archives_title').val('%s');"%(archives['title'].replace("'",'"'))
		if archives['publish']:
			script+= "$('#archives_publish_date').val('%s/%s/%s');"%(archives['publish'][0],archives['publish'][1],archives['publish'][2])
		if archives['org']:
			script+= "$('#archives_org').val('%s');"%(archives['org'])
		if archives['signer']:
			tmp = archives['signer'].split('|')
			script+= "$('#archives_competance').val('%s');$('#archives_position').val('%s');$('#archives_signer').val('%s');"%(tmp[0],tmp[1],tmp[2])
		if archives['receive']:
			script+= "$('#archives_receive').val('%s');"%(archives['receive'])
		from plugin_app import ColorBox
		txt = A(T('Metadata'),href='#',_onclick='$.colorbox({href:"%s",width:"800",height:"600"});'%URL(r=request,c='plugin_upload',f='textcontent',args=request.args))
		script+= "$('#extract_%s').html('%s');"%(fileupload.upload_id,txt)
	except Exception, e:
		script = 'alert(%s);'%e
	return SCRIPT(script)
	

def get_ocr():
	import re	
	def clean(txt,expr):
		for exp in expr:
			tmp = re.findall(exp, txt, re.U)	
			if len(tmp)>0: txt = txt.replace(tmp[0],'')
		return txt
	def clean_text(txt):
		text = txt
		for key in ['\t','\n','\r']: text = text.replace(key,' ')
		while text.find('  ')>=0: text = text.replace('  ',' ')
		return text.lstrip().rstrip()
	
	txt = request.vars.content.decode('utf-8')
	
	expr = [ur"C\w+ H.+NAM",ur"\w{2}c l.+p\w+c"]
	txt = clean(txt,expr)
	name, title, publish, org = '', '', '', ''

	expr = [ur"H.+ng.+th.+n.+\d{4}", ur"[A-Z].+ng.+th.+n.+\d{4}"]
	for exp in expr:
		tmp = re.findall(exp, txt)
		if len(tmp)>0: 
			txt = txt.replace(tmp[0],'')
			tmp = re.findall(r"\d+", tmp[0].encode('utf-8'))
			if len(tmp)==3: publish = tmp
			break
				
	expr = [ur"(?:S|s)ố:.+\S",ur"(?:S|s)\w+.+\S",ur".+:.+/[A-Z|-]+\w+"]
	for exp in expr:
		tmp = re.findall(exp, txt, re.U)	
		if len(tmp)>0: 
			name = tmp[0]
			org = txt[:txt.find(name)]
			txt = txt.replace(tmp[0],'')
			txt = txt.replace(org,'')
			org = clean_text(org).encode('utf-8')
			tmp = re.findall(r"\d+", name)
			number = tmp[0] if len(tmp)>0 else ''
			tmp = re.findall(r"[A-Z|-]+\w+", name)
			symbol = tmp[-1] if len(tmp)>0 else ''
			name = [number.encode('utf-8'),symbol.encode('utf-8')]
			break
	type = u'Quyết định'
	type = u'Công văn'
	type = u'CHỈ THỊ'
	type = type.upper() 		
	if type==u'Công văn'.upper():
		expr = [ur"K\w+ g\w+:",ur"(?:K|k).+:\s",ur".+:\s"]
		for exp in expr:
			tmp = re.findall(exp, txt, re.U)	
			if len(tmp)>0: 
				title = txt[:txt.find(tmp[0])]
				title = clean_text(title).encode('utf-8')
				break
	else:		
		expr = [ur"\w+ \w+\S",ur"\w+ \w+ \w+\S"]
		for exp in expr:
			tmp = re.findall(exp, txt, re.U)
			if len(tmp)>0:
				tmp = txt[txt.find(tmp[0])+len(tmp[0]):].split('\n')
				i = 0
				while i < len(tmp):
					if clean_text(tmp[i]).lstrip().rstrip()=='': pass
					elif title=='': title = tmp[i]
					elif tmp[i].lstrip()[0].isupper(): break
					else: title += ' ' +tmp[i]
					i+=1
				title = clean_text(title).encode('utf-8')
				break
			
	archives = dict(name=name,title=title,publish=publish,org=org)
	content = 'Result:\n' +'\nName:'+ str(name) +'\nTitle:'+ title +'\nPublish:'+ str(publish) +'\nOrg:'+ org +'\n\n'+ txt.encode('utf-8')
	#for txt in tmp: content += txt +'\n'
	content = TEXTAREA(value=content)
	return content
	