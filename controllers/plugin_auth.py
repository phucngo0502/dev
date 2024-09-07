###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 15/03/2011
# Version 0.2 Date: 20/03/2011
#	Update permission on group, user, table, record
#	Use ajax on set_level
###################################################

auth_group=db[auth.settings.table_group_name]
auth_user = db[auth.settings.table_user_name]
auth_membership = db[auth.settings.table_membership_name]
auth_permission = db[auth.settings.table_permission_name]
auth_event = db[auth.settings.table_event_name]

from gluon.tools import Crud
crud = Crud(db)

def login():
	if auth.user:
		redirect(URL(c='admin',f='index'))	
	
	if site_name=='naso':	
		response.view = 'site/naso/default/login.html'
	else:
		response.view = 'admin/login.html'
	return dict(form=auth())

def user():
	if site_name=='sale_medicbaclieu':	
		response.view = 'site/sale_medicbaclieu/default/login.html'
		return dict(form=auth())
	else:
		response.view = 'plugin_process/user.html'	
		return dict(content=auth())
	
	
    	
def phone_login():
	response.view = 'admin/phone_login.html'
	return dict()
    
def otp_login():
	response.view = 'admin/otp_login.html'
	return dict()


def profile():
	user = db.auth_user(auth.user_id)
	db.auth_user.id.writable=False
	db.auth_user.id.readable=False
	db.auth_user.role.writable=False
	db.auth_user.role.readable=False
	db.auth_user.auth_group.writable=False
	db.auth_user.auth_group.readable=False
	db.auth_user.password.writable=False
	db.auth_user.password.readable=False
	db.auth_user.display_order.writable=False
	db.auth_user.display_order.readable=False
	db.auth_user.username.writable=False
	#db.auth_user.password.readable=False
	crud.settings.update_deletable = False
	#form = SQLFORM(db.auth_user, auth.user_id)
	form = crud.update(db.auth_user, auth.user_id)
	response.view = 'plugin_auth/user.html'
	return dict(content=DIV(form,_class='panel'))


@auth.requires_login()		
def index():
	if (db(auth_user.id>0).count()==0): init() 
	return dict()
	
@auth.requires_login()	
def init():
	if (db(auth_user.id>0).count()==0) | auth.has_membership(role='admin') | auth.has_membership(role='manager'):
		permission = {}
		permission['user'] = ['create','edit','delete','explorer','read']
		permission['manager'] = ['publish']
		permission['editor'] = ['editor']
		
		for key in permission.keys():
			for name in permission[key]:
				row = db(db.permission.name==name).select().first()
				id = row.id if row else db.permission.insert(name=name, description='User can ' + name)

		role = 'Auth'		
		row = db(auth_group.role==role).select().first()
		parent = row.id if row else auth_group.insert(role=role,atype='auth',description=role+' group')
		role = 'public'		
		if db(auth_group.role==role).count()==0: auth_group.insert(role=role,atype='auth',description=role+' group')
			
		for role in ['admin','manager','user','editor']:
			row = db(auth_group.role==role).select().first()
			group = row.id if row else auth_group.insert(parent=parent,role=role,atype='auth',description=role+' group')

			username = role
			row = db(auth_user.username==username).select().first()
			user = row.id if row else auth_user.insert(first_name=role,last_name='user',username=username,password=auth_user.password.requires[0](request.application+role.capitalize())[0])
			if auth.has_membership(auth.id_group(role),user)==False: auth.add_membership(group, user)
				
		rows = db(auth_user).select()
		user = auth.id_group('user')
		for row in rows: 
			if not auth.has_membership(user,row.id): auth.add_membership(user, row.id)
		
		set_group_permission(user,permissions=['explorer'],tables=db.tables,delete=False)
		
		response.flash = T('Successfully updated')	
	return dict()

@auth.requires_login()	
def set_group_permission(group,permissions=[],tables=[],delete=False):
	for table in tables:
		for name in permissions: 
			if (delete==False): 
				if db((auth_permission.group_id==group)&(auth_permission.name==name)&(auth_permission.table_name==table)&(auth_permission.record_id==0)).count()==0: 
					auth.add_permission(group, name, table, 0)
			else: auth.del_permission(group, name, table, 0)			

@auth.requires(auth.has_membership(role='admin') | auth.has_membership(role='manager'))
def set_table():

	#groups = db(auth.accessible_query('explorer',auth_group, auth.user_id)).select(auth_group.ALL,orderby=auth_group.role)
	groups = db(auth_group).select(auth_group.ALL,orderby=auth_group.role)
	#permissions = db(auth.accessible_query('explorer',db.permission, auth.user_id)).select(db.permission.ALL,orderby=db.permission.display_order)
	permissions = db(db.permission).select(db.permission.ALL,orderby=db.permission.display_order)
	tables = []
	if (request.args(0)<>None) & (request.vars.group<>None) & (request.vars.permission<>None):
		group_id =  int(request.vars.group) or 0
		permission = request.vars.permission or ''
		rows = db((auth_permission.group_id==group_id)&(auth_permission.name==permission)&(auth_permission.record_id==0)).select(auth_permission.table_name,orderby=auth_permission.table_name)
		lists = [row.table_name for row in rows]
		for key in request.vars.keys():
			if key[:3] == 't__': 
				table = key.split('__')[1]
				if table not in lists: auth.add_permission(group_id,permission,table,0)
				else: lists.remove(table)
		for table in lists: auth.del_permission(group_id,permission,table,0)
		redirect(URL(args=[]))
	return dict(groups=groups,permissions=permissions)

	
@auth.requires(auth.has_membership('admin') | auth.has_membership('system') | auth.has_membership(role='manager'))
def set_password():
	rowus = db(db.auth_user.id>4).select()
	form = FORM(_action=URL(c='plugin_auth', f='save_set_password'),_onSubmit="return kiemtra();",_id='set_pass',_name='set_pass')
	select = SELECT(_name='select_auth_user', _id='select_auth_user')
	for rowu in rowus:
		select.append(OPTION(rowu.first_name+' '+rowu.last_name, _value=rowu.id))
	txtpass1 = INPUT(_type='password', _name='txtpass1',_id='txtpass1')
	txtpass2 = INPUT(_type='password', _name='txtpass2',_id='txtpass2')
	table = TABLE()
	table.append(TR(TD(T('Username')),TD(select)))
	table.append(TR(TD(T('New password')),TD(txtpass1)))
	table.append(TR(TD(T('Re new password')),TD(txtpass2)))
	btnsubmit = INPUT(_type='submit', _value='submit')
	table.append(TR(TD(btnsubmit, _colspan='2')))
	table.append(TR(TD()))
	form.append(table)
	return dict(form=form)

@auth.requires(auth.has_membership('admin') | auth.has_membership('system') | auth.has_membership(role='manager'))	
def save_set_password():
	auth_user = request.vars.select_auth_user
	txtpass = request.vars.txtpass1
	db(db.auth_user.id==int(auth_user)).update(password=db.auth_user.password.requires[0](txtpass)[0])
	redirect(URL(f='set_password'))	
	
	
@auth.requires(auth.has_membership(role='admin') | auth.has_membership(role='manager'))
def set_level():
	groups = db(auth_group).select(auth_group.ALL,orderby=auth_group.role)
	permissions = db(db.permission).select(db.permission.ALL,orderby=db.permission.display_order)
	tables = ['folder','portlet',"procedures","process",'dtable']
	group_id = 0
	level = []
	permission = ''
	table = ''
	for key in request.vars.keys():
		if key == 'group': group_id =  int(request.vars.group)
		elif key == 'table': table = request.vars.table
		elif key == 'permission': permission = request.vars.permission
		elif key[:3] == 'l__': level.append(int(key.split('__')[1]))
	if (table <> '') & (group_id>0) & (permission<>''):
		if (level<>[]):
			lists = get_group_permission(group_id,permission,table)
			for record_id in level: 
				if record_id not in lists: auth.add_permission(group_id,permission,table,record_id)
				else: lists.remove(record_id)
			lists.append(0)
			for record_id in lists: auth.del_permission(group_id,permission,table,record_id)
		else: db((db.auth_permission.group_id==group_id)&(db.auth_permission.name==permission)&(db.auth_permission.table_name==table)).delete() 
		response.flash = T('Successfully updated')
	return dict(tables=tables,groups=groups,permissions=permissions)

@auth.requires_login()	
def get_group_permission(group_id,permission,table):
	query = ((auth_permission.group_id==group_id)&(auth_permission.name==permission)&(auth_permission.table_name==table))
	if db(query&(auth_permission.record_id==0)).count()>0:
		order = 'parent' if 'parent' in cms.db[table].fields else None
		rows = cms.db(cms.db[table].id>0).select(orderby=order)
		return [row.id for row in rows]
	else: 
		rows = db(query).select()
		return [row.record_id for row in rows]

@auth.requires_login()	
def get_records():
	try:
		from plugin_app import get_represent
		group_id = 0
		permission = ''
		table = ''
		group_id =  int(request.vars.group) or 0
		table = request.vars.table or ''
		permission = request.vars.permission or ''
		if (table <> '') & (group_id>0) & (permission<>''):
			cms.define_table(table)
			lists = get_group_permission(group_id,permission,table)
			db = cms.db
			if 'parent' in db[table].fields:
				script = '''<script>
								$(document).ready(function(){
									$("#tree_view").treeview({
										animated: "fast",
										collapsed: true,
										control:"#sidetreecontrol",
										persist: "cookie",
										toggle: function() {
											window.console && console.log("%o was toggled", this);
										}
									});
								});
							</script>'''			
				return XML(str(script)+str(MENU(table_tree(db,table,None,lists),_id='tree_view',_class='treeview-red')))
			else: 
				rows = db(~db[table].id.belongs(lists)).select()
				records = db(db[table].id.belongs(lists)).select()
				table_records = TABLE(_cellpadding="0",_cellspacing="0",_border="0",_class="display",_id="table_table")
				thead = THEAD(TR(TH(INPUT(_type="checkbox",_id="tcheck_all")),TH(T('Name')),TH(T('Parent'))))
				tbody = TBODY()
				for row in records:
					td0 = XML('<input type="checkbox" name="l__'+str(row.id)+'" checked="checked" />')
					td1 = row.name if 'name' in db[table].fields else row[db[table].fields[1]]
					td2 = get_represent(table,'parent',row.parent) if 'parent' in db[table].fields else ''
					tbody.append(TR(TD(td0),TD(td1),TD(td2)))
				for row in rows:
					td0 = INPUT(_type="checkbox",_name="l__"+str(row.id))
					td1 = row.name if 'name' in db[table].fields else row[db[table].fields[1]]
					td2 = get_represent(table,'parent',row.parent) if 'parent' in db[table].fields else ''
					tbody.append(TR(TD(td0),TD(td1),TD(td2)))
				tfoot = TFOOT(TR())
				table_records = TABLE(thead,tbody,tfoot,_cellpadding="0",_cellspacing="0",_border="0",_class="display",_id="table_table")
				
				script = SCRIPT('''$(document).ready(function(){
						var table;
						table = $('#table_table').dataTable({
							"iDisplayLength": 25,
						});
						$('#tcheck_all').click( function() {
						$('input', table.fnGetNodes()).attr('checked',this.checked);
						} );		
					});''')		
				return XML(str(script)+str(table_records))
		return '...'
	except Exception, e:
		return e

@auth.requires_login()	
def get_table():
	group_id =  int(request.vars.group) or 0
	permission = request.vars.permission or ''
	
	if (group_id>0)&(permission<>''):
		rows = db((auth_permission.group_id==group_id)&(auth_permission.name==permission)&(auth_permission.record_id==0)).select(auth_permission.table_name,orderby=auth_permission.table_name)
		lists = []
		#tables = db.tables
		#tables = ['folder','process','procedures']
		cms.define_tables()
		tables = ['process','procedures'] + cms.db.tables
		
		for row in rows:
			if row.table_name not in lists: lists.append(row.table_name)
			if row.table_name in tables: tables.remove(row.table_name)
		table_records = TABLE(_cellpadding="0",_cellspacing="0",_border="0",_class="display",_id="table_table")
		thead = THEAD(TR(TH(INPUT(_type="checkbox",_id="tcheck_all")),TH(T('Table name'))))
		tbody = TBODY()
		for table in lists:
			td0 = XML('<input type="checkbox" name="t__'+table+'" checked="checked" />')
			tbody.append(TR(TD(td0),TD(table)))
		for table in tables:
			td0 = INPUT(_type="checkbox",_name="t__"+table)
			tbody.append(TR(TD(td0),TD(table)))
		tfoot = TFOOT(TR(TH(),TH()))
		table_records = TABLE(thead,tbody,tfoot,_cellpadding="0",_cellspacing="0",_border="0",_class="display",_id="table_table")

		script = SCRIPT('''$(document).ready(function(){
				var table;
				table = $('#table_table').dataTable({
					"iDisplayLength": 100,
				});
				$('#tcheck_all').click( function() {
				$('input', table.fnGetNodes()).attr('checked',this.checked);
				} );		
			});''')		
		return XML(str(script)+str(table_records))
	return '...'
	
@auth.requires(auth.has_membership(role='admin') | auth.has_membership(role='manager'))
def group():
	form = crud.update(auth_group,request.args(0))	
	rows = db(auth_group.id>0).select(orderby=auth_group.role)
	script = '''<script>
								$(document).ready(function(){
									$("#tree_view").treeview({
										animated: "fast",
										collapsed: true,
										control:"#sidetreecontrol",
										persist: "cookie",
										toggle: function() {
											window.console && console.log("%o was toggled", this);
										}
									});
								});
							</script>'''
	table = XML(str(script)+str(MENU(table_tree_group(db,db.auth_group),_id='tree_view',_class='treeview-red')))
	# table = TABLE(TR(TH(T('No'),_width=30),TH(T('Role'),_width=100),TH(T('Description'))))
	# i = 1
	# for row in rows:
		# table.append(TR(TD(i),TD(A(row.role,_href=URL(args=row.id))),TD(row.description)))
		# i+=1
	return dict(form=form,table=table)

@auth.requires(auth.has_membership(role='admin') | auth.has_membership(role='manager'))
def permission():
	form = crud.update(db.permission,request.args(0))	
	rows = db(db.permission.id>0).select(orderby=db.permission.display_order)
	table = TABLE(TR(TH(T('No'),_width=30),TH(T('Name'),_width=100),TH(T('Description'))))
	i = 1
	for row in rows:
		table.append(TR(TD(i),TD(A(row.name,_href=URL(args=row.id))),TD(row.description)))
		i+=1
	return dict(form=form,table=table)
	
@auth.requires(auth.has_membership(role='admin') | auth.has_membership(role='manager'))
def users():
	user_id = request.args(0)
	if request.args(1)=='group':
		user_group = db((auth_group.id==auth_membership.group_id)&(auth_membership.user_id==user_id)).select(auth_group.ALL,orderby=auth_group.role)
		lists = [row.id for row in user_group]
		for key in request.vars.keys():
			if request.vars[key] == 'on': 
				group_id = int(key)
				if group_id not in lists: auth.add_membership(group_id, user_id)
				else: lists.remove(group_id)
		for group_id in lists: auth.del_membership(group_id, user_id)
		redirect(URL(args=[user_id]))
	elif request.args(1)=='delete':
		for key in request.vars.keys():
			if request.vars[key] == 'on': db(auth_user.id==int(key)).delete()
		redirect(URL(args=[]))
	
	fields = []	
	for field in [auth_user.auth_group,auth_user.role,auth_user.first_name,auth_user.last_name,Field('username')]:
		if auth_user(user_id): field.default = auth_user(user_id)[field.name] 
		fields.append(field)
	if auth_user(user_id): 
		fields.append(Field('blocked','boolean',default=True if auth_user(user_id).registration_key=='blocked' else False))
	else:	
		fields.append(auth_user.password)
		fields.append(Field('blocked','boolean',default=False))
	form = SQLFORM.factory(*fields)
	if form.accepts(request.vars, session):
		if db((auth_user.id<>user_id)&(auth_user.username==request.vars.username)).count()==0:
			blocked = 'blocked' if request.vars.has_key('blocked') else ''
			if user_id: 
				db(auth_user.id == user_id).update(auth_group=request.vars.auth_group,role=request.vars.role,first_name=request.vars.first_name,last_name=request.vars.last_name,username=request.vars.username,registration_key = blocked)	
			else:	
				auth_user.insert(auth_group=request.vars.auth_group,role=request.vars.role,first_name=request.vars.first_name,last_name=request.vars.last_name,username=request.vars.username,registration_key=blocked,password=auth_user.password.requires[0](request.vars.password)[0])	
			redirect(URL(args=[]))
		else: response.flash = T('Username existed!')

	#users = db(auth.accessible_query('explorer',auth_user, auth.user_id)).select(auth_user.ALL,orderby=auth_user.username)
	users = db(auth_user).select(auth_user.ALL,orderby=auth_user.username)
		
	user_group = db((auth_group.id==auth_membership.group_id)&(auth_membership.user_id==user_id)).select(auth_group.ALL,orderby=auth_group.role)
	lists = [row.id for row in user_group]
	#group = db(~auth_group.id.belongs(lists)&auth.accessible_query('explorer',auth_group, auth.user_id)).select(auth_group.ALL,orderby=auth_group.role)
	group = db(~auth_group.id.belongs(lists)).select(auth_group.ALL,orderby=auth_group.role)
	
	permissions = db(auth_permission.group_id.belongs(lists)).select(auth_permission.ALL,distinct=True)
	
	return dict(form=form, users=users, user_group = user_group, group=group, permissions=permissions)
	
def table_tree(db,table,parent=None,lists=[]):
	tree = []
	rows=db(db[table].parent==parent).select()
	for row in rows:
		check = '<input type="checkbox" name="l__'+str(row.id)+'" checked="checked" />' if row.id in lists else '<input type="checkbox" name="l__'+str(row.id)+'" />'
		if "label" in db[table].fields: field = "label"
		elif "name" in db[table].fields: field = "name"
		elif "role" in db[table].fields: field = "role"
		else: field = db[table].fields[1]
		tree += [(None, False, DIV(XML(check),' ', row[field]), table_tree(db,table,row.id,lists))]
	return tree	
	
def table_tree_group(db,table,parent=None,lists=[],link='#'):
	tree = []
	rows=db(db[table].parent==parent).select()
	
	for row in rows:
		check = '<input type="checkbox" name="l__'+str(row.id)+'" checked="checked" />' if row.id in lists else '<input type="checkbox" name="l__'+str(row.id)+'" />'
		if "label" in db[table].fields: field = "label"
		elif "name" in db[table].fields: field = "name"
		elif "role" in db[table].fields: field = "role"
		else: field = db[table].fields[1]
		tree += [(None, False, DIV(A(row[field],_href=URL(args=row.id))), table_tree_group(db,table,row.id,lists))]
	return tree		

