###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 22/02/2012
###################################################
from plugin_comment import Comment
comment = Comment()


@auth.requires_login()
def view():
	return comment.view()
		
@auth.requires_login()
def edit():
	table = comment.define_comment()	
	form = SQLFORM(table,comment.id,fields=['txtcontent'],showid=False,labels = {'txtcontent':''},deletable=True)
	if form.process().accepted:
		return SCRIPT('parent.$.colorbox.close();')
	return dict(content=form)	
	
@auth.requires_login()
def draw():
	content = ''
	if request.vars.comment_id: content = comment.define_comment()(request.vars.comment_id).txtcontent
	return dict(content=content)
	
@auth.requires_login()
def update():
	content = request.vars.data
	id = int(request.vars.comment_id) if request.vars.comment_id else None
	comment.update(content,id)
	return 1
	
@auth.requires_login()
def delete():
	table = comment.define_comment()
	db(table.id==request.vars.comment_id).delete()
		

		