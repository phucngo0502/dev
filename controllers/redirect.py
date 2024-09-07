@auth.requires(auth.has_membership(role='admin'))
def table():
	tablename = request.args(0)
	eval('processmodel.define_%s(True)'%tablename)
	content = SQLFORM.grid(db[tablename],args=request.args)
	response.view = 'plugin_process/content.html'
	return dict(content=content)
