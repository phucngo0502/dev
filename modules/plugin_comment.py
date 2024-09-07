###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
###################################################
from gluon import current
from html import *

class Comment:
	def __init__(self,**attr):
		try:
			request = current.request
			self.db = attr.get('db',current.globalenv['db'])
			self.auth = attr.get('auth',current.globalenv['auth'])
			self.id = attr.get('id',request.vars.comment_id)
			self.tablename = attr.get('tablename',request.args(0) or 'document')
			self.table_id = attr.get('table_id',request.args(1) or 1)
			self.objects_id = attr.get('objects_id',request.vars.objects_id) or 0
			self.procedures = attr.get('procedures',request.vars.procedure_id or 1)
			self.process = attr.get('process',request.vars.process_id or 1)
			self.message = attr.get('message',request.vars.message or '')
			self.vars = {}
			self.vars['objects_id'] = self.objects_id
			if self.procedures: self.vars['procedure_id'] = self.procedures
			if self.process: self.vars['process_id'] = self.process
			self.auth_groups = attr.get('auth_groups',request.vars.auth_groups or [])
			if self.auth_groups: 
				if not isinstance(self.auth_groups,list): self.auth_groups = [self.auth_groups]
				self.auth_groups = [int(id if id else 0) for id in self.auth_groups]
				if request.vars.auth_group: self.auth_groups.append(int(request.vars.auth_group))
				self.vars['auth_groups'] = self.auth_groups
			self.define_comment(True)
		except Exception, e:
			print 'plugin comment: init error:', e
			
			
		
	def define_comment(self,migrate=False):	
		if 'tcomment' in self.db.tables: return self.db.tcomment
		from gluon.dal import Field
		from plugin_ckeditor import CKEditor
		ckeditor = CKEditor(self.db)
		return self.db.define_table('tcomment',
			Field('tablename'),
			Field('table_id','integer'),
			Field('objects_id','integer'),
			Field('procedures','integer'),
			Field('process','integer'),
			Field('auth_group','list:integer'),
			Field('txtcontent','text',length=16777215,widget=ckeditor.widget),
			Field('created_by','integer',default=self.auth.user_id or 1,writable=False,readable=False),
			Field('created_on','datetime',default=current.request.now,writable=False,readable=False),
			migrate=migrate)

	def update(self,content,id=None):
		db = self.db
		auth = self.auth
		request = current.request
		comment = self.define_comment()
		if id: db(comment.id==id).update(txtcontent=content,created_on=request.now)
		else: comment.insert(txtcontent=content,tablename=self.tablename,table_id=self.table_id,objects_id=self.objects_id,procedures=self.procedures,process=self.process,auth_group=self.auth_groups)
			
	def view(self):
		from gluon.tools import prettydate
		db = self.db
		auth = self.auth
		T = current.T
		request = current.request
		comment = self.define_comment()
		content = TABLE()
		value = None
		args = [self.tablename,self.table_id]
		if request.vars.comment_delete: db(comment.id==request.vars.comment_id).delete()
		elif request.vars.comment_update: db(comment.id==self.id).update(txtcontent=request.vars.txtcontent,created_on=request.now)
		elif self.id: value = comment(self.id).txtcontent
		elif request.vars.txtcontent: 
			comment.insert(txtcontent=request.vars.txtcontent,tablename=self.tablename,table_id=self.table_id,objects_id=self.objects_id,procedures=self.procedures,process=self.process,auth_group=self.auth_groups)
		form = TABLE(TR(TD(TEXTAREA(_name='txtcontent',value=value),_id='table_comment_edit')),_id='form_add_comment')
		ajax =  "ajax('%s', ['txtcontent'], '%s_comment')"%(URL(r=request,c='plugin_comment',f='view',args=args,vars=self.vars),self.tablename)
		td = TD(INPUT(_type='button',_name='submit',_class='btn btn-primary',_value=T('Add comment'),_onclick=ajax))
		if value:
			self.vars['comment_id']=self.id
			self.vars['comment_update']=True
			ajax =  "ajax('%s', ['txtcontent'], '%s_comment')"%(URL(r=request,c='plugin_comment',f='view',args=args,vars=self.vars),self.tablename)
			td.append(INPUT(_type='button',_name='submit',_class='btn btn-primary',_value=T('Edit'),_onclick=ajax))
			del self.vars['comment_update']
			self.vars['comment_delete']=True
			ajax =  "ajax('%s', [], '%s_comment')"%(URL(r=request,c='plugin_comment',f='view',args=args,vars=self.vars),self.tablename)
			td.append(INPUT(_type='button',_name='submit',_class='btn btn-danger',_value=T('Delete'),_onclick=ajax))
		from plugin_app import ColorBox
		td.append(DIV(SPAN(ColorBox(caption=T('Pencil'),iframe='true',source=URL(r=request,c='plugin_comment',f='draw.html',args=args,vars=self.vars),reload=True,width='850px',height='380px'),_id='button_cb',_class='glyphicon glyphicon-pencil'),_class='btn btn-primary pencil'))
		form.append(TR(td))
		query = (comment.tablename==self.tablename)&(comment.table_id==self.table_id)
		#if self.objects_id: query &= (comment.objects_id==self.objects_id)
		#if self.procedures: query &= (comment.procedures==self.procedures)
		#if self.process: query &= (comment.process==self.process)
		if self.auth_groups: query &= (comment.auth_group.contains(self.auth_groups,all=False))
		
		rows = db(query).select(orderby=~comment.created_on)
		for row in rows:
			user = self.db.auth_user(row.created_by)
			tr = TR(TD(row.created_on,' (',prettydate(row.created_on,T),')'),TD('%s %s'%(user.last_name,user.first_name),':'))
			comment = row.txtcontent
			if (comment[:5] == 'data:'): 
				comment = IMG(_src='%s'%comment, _width='600', _height='150', _style='border: 1px solid #000;')
				tr.append(TD(''))
				content.append(tr)
				if self.auth.user_id==row.created_by:
					self.vars['comment_id']=row.id
					comment=SPAN(ColorBox(caption=comment,iframe='true',source=URL(r=request,c='plugin_comment',f='draw.html',args=args,vars=self.vars),reload=True,width='850px',height='380px',onCleanup="$('#savebutton').trigger('click');"),_id='button_cb')
				tr = TR(TD(comment,_colspan='3'))
				content.append(tr)
			else:
				comment = XML(comment)
				if self.auth.user_id==row.created_by:
					self.vars['comment_id']=row.id
					ajax =  "ajax('%s', [], '%s_comment')"%(URL(r=request,c='plugin_comment',f='edit',args=args,vars=self.vars),self.tablename)
					comment=SPAN(ColorBox(caption=comment,iframe='true',source=URL(r=request,c='plugin_comment',f='edit.html',args=args,vars=self.vars),reload=True,width='800px',height='600px',onCleanup="$('#savebutton').trigger('click');"),_id='button_cb')
					#tr.append(TD(A(comment,_href='#',_onclick=ajax)))
					tr.append(TD(comment))
				else: tr.append(TD(comment))
				content.append(tr)
		content = DIV(self.message,content,form,_id='%s_comment'%self.tablename, _class='object_comment')
		return XML(content)
		
	def content(self):
		comment = self.define_comment()
		query = (comment.tablename==self.tablename)&(comment.table_id==self.table_id)&(comment.process==self.process)
		row = self.db(query).select(orderby=comment.created_on).first()
		return row.txtcontent if row else ''