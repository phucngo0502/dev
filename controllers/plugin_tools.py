###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 	Date: 27/04/2011
# Version 1.0 	Date: 24/09/2015
###################################################

###################################################
# required parameters set by default if not set
# Need xlrd module in site_parkages
###################################################
import os,datetime
DATA_DATETIME_FORMAT = '%d/%m/%Y,%H:%M'
DATA_DATE_FORMAT = '%d/%m/%Y'
	
	
from plugin_cms import CmsModel
cms = CmsModel()	
db = cms.db

def index():
	return dict()	
	
###################################################
# restore database from zip file
###################################################	
def restore():
	table_imports = {}
	if request.vars.filename != None: 
		import zipfile26 as zipfile 
		file = zipfile.ZipFile(request.vars.filename.file)
		backup_dir = request.folder+'/static/backup'
		file.extractall(backup_dir)
		d={}
		i = 0
		for name in file.namelist():
			path = name.split('/')
			table = path[len(path)-1]
			f = open(backup_dir+'/'+name, 'r')
			if table in db.tables: 
				if 'truncate' in request.vars.keys():
					db[table].truncate()
				import_from_csv_file2(table,f,d) 
				table_imports[table]= db(db[table].id>0).count()
			f.close()
			os.unlink(backup_dir+'/'+name) 
			i+=1
		file.close()
	return dict(table = table_imports)

def import_from_csv_file2(
	tablename,
	csvfile,
	id_map=None,
	null='<NULL>',
	unique='uuid',
	*args, **kwargs
	):
	"""
	import records from csv file. Column headers must have same names as
	table fields. field 'id' is ignored. If column names read 'table.file'
	the 'table.' prefix is ignored.
	'unique' argument is a field which must be unique
	(typically a uuid field)
	"""
	import csv
	delimiter = kwargs.get('delimiter', ',')
	quotechar = kwargs.get('quotechar', '"')
	quoting = kwargs.get('quoting', csv.QUOTE_MINIMAL)

	reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
	colnames = None
	if isinstance(id_map, dict):
		if not tablename in id_map:
			id_map[tablename] = {}
		id_map_self = id_map[tablename]

	def fix(field, value, id_map):
		if value == null:
			value = None
		elif id_map and field.type[:10] == 'reference ':
			try:
				value = id_map[field.type[9:].strip()][value]
			except KeyError:
				pass
		return (field.name, value)

	for line in reader:
		if not line:
			break
		if not colnames:
			colnames = [x[x.find('.') + 1:] for x in line]
			c = [i for i in xrange(len(line)) if colnames[i] != 'id']
			cid = [i for i in xrange(len(line)) if colnames[i] == 'id']
			if cid:
				cid = cid[0]
		else:
			items = [fix(db[tablename][colnames[i]], line[i], id_map) for i in c]
			query = None
			for i in c:
				if line[i] <> '<NULL>':
					if query ==None: query = (db[tablename][colnames[i]]==line[i])
					else: query = query & (db[tablename][colnames[i]]==line[i])					
			if db(query).count()==0:
				new_id = db[tablename].insert(**dict(items))
				if id_map and cid != []:
					id_map_self[line[cid]] = new_id		


def delete(tables):
	for t in tables:
		db[t].truncate()
	
def define(tables):
	for t in tables: cms.define_table(t,True)

	
###################################################
# backup database to zip file
###################################################	
def select_table():
	table_exports = []
	for key in request.vars.keys():
		if request.vars[key] == 'on': table_exports.append(key)
	if table_exports <> []: 
		if request.args(0)=='backup': backup(table_exports)		
		elif request.args(0)=='xls': redirect(URL(f='export.xls',args=['xls'],vars=request.vars))		
		elif request.args(0)=='delete': return dict(tables=table_exports,delete=True)
		elif request.args(0)=='del_confirm': 
			delete(table_exports)
			redirect(URL(f="index"))
	return dict(tables=db.tables,delete=False) 

def backup(table_exports):
	import zipfile26 as zipfile 
	import glob, os, datetime
	backup_dir = request.folder+'/static/backup'
	if not os.path.exists(backup_dir): os.makedirs(backup_dir)	
	filename = 'backup_' + str(datetime.date.today())
	file = zipfile.ZipFile(backup_dir+ '/'+ filename, "w")
	
	for f in table_exports:
		path=os.path.join(request.folder,'static/backup', f) 	
		f1 = open(path,'w')
		f1.write(str(db(db[f].id>0).select()))
		f1.close()
		file.write(path)
		os.unlink(path) 
	file.close()
	
	response.flash = T('Successfully backuped')
	return 1	
	
###################################################
# Excel fuctions
###################################################		
def open_xls_book():
	if request.vars.filename != None: 
		import xlrd as xlrd
		import shutil, uuid 
		path=os.path.join(request.folder,'private','%s.xls' % uuid.uuid4()) 	
		shutil.copyfileobj(request.vars.filename.file,open(path,'wb')) 
		book = xlrd.open_workbook(path) 
		os.unlink(path)
		return book
	return None	
	
def read_xls():
	if request.vars.filename != None: 
		import xlrd as xlrd
		import shutil 
		path=os.path.join (request.folder,'private','a_dummy_file_name.xls') 
		shutil.copyfileobj(request.vars.filename.file,open(path,'wb')) 
		book = xlrd.open_workbook(path) 
		sh = book.sheet_by_index(0) 
		os.unlink(path)
		return sh
	return None	
	
def insert():
	book = open_xls_book()
	if book:
		for i in range(book.nsheets):
			insert_sheet(book.sheet_by_index(i))
	return dict()

def insert_sheet(sheet, tablename = None):
	table = tablename if tablename else sheet.name
	if table not in db.tables: return 0
	fields = {}
	uniques = []
	for i in range(sheet.nrows):
		if sheet.cell_value(rowx=i, colx=0) == '{{}}':
			for col in range(1,sheet.ncols):
				key = str(sheet.cell_value(rowx=i, colx=col))
				if key <> '':
					f = key.split(',')
					key = f[0]
					if len(f)>1: uniques.append(key.split(':')[0])
					fields[key] = col
			for k in range(i+1, sheet.nrows):
				vars = {}
				for key in fields.keys():
					value = sheet.cell_value(rowx=k, colx=fields[key])
					if (isinstance(value,unicode)==True) | (isinstance(value,str)==True): 
						value = value.strip()
						value = value.encode("utf-8")
					if value<>'':
						tf = key.split(':')
						if len(tf)==3: 
							key = tf[0]
							if db[table][key].type[:14]=='list:reference':
								list_v = value.split('|')
								value = []
								for v in list_v:
									v = v.strip()
									row = db(db[tf[1]][tf[2]]==v).select().last()
									if row: value.append(row.id) 
									elif request.vars.reference_insert: 
										tmp = {tf[2]:v}
										value.append(db[tf[1]].insert(**tmp))
							elif db[table][key].type[:9]=='reference':
								row = db(db[tf[1]][tf[2]]==value).select().last()
								if row: value = row.id 
								elif request.vars.reference_insert: 
									tmp = {tf[2]:value}
									value = db[tf[1]].insert(**tmp)
								else: value = None
							else: 
								row = db(db[tf[1]][tf[2]]==value).select().last()
								value = row.id if row else None 
						if key in db[table].fields:
							if db[table][key].type=='date': value = datetime.datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")
							vars[key] = value
				insert = False
				for key in vars.keys():
					if vars[key] <> None: 
						insert=True
						break
				query = None
				if insert==True:
					if table=='auth_user': insert_auth_user(vars)
					else:
						for field in uniques:
							if field not in vars.keys(): vars[field]=None
							query = query&(db[table][field]==vars[field]) if query else (db[table][field]==vars[field])
						if query:
							row = db(query).select().first()
							if row: db(db[table].id==row.id).update(**vars) 
							else: db[table].insert(**vars)
						else: db[table].insert(**vars)
			break	

def insert_auth_user(vars):	
	row = db(db.auth_user.username==vars['username']).select().first()
	pwd = str(vars['password'])
	if pwd.isdigit(): pwd = str(int(pwd))
	vars['password']=db.auth_user.password.requires[0](pwd)[0]
	return db(db.auth_user.id==row.id).update(**vars) if row else db.auth_user.insert(**vars)
					
def export():
	tables = []
	for key in request.vars.keys():
		if request.vars[key] == 'on': tables.append(key)
	pages =[]
	for table in tables:
		if pages == []: pages = [table2xls(table)]
		else: pages += [table2xls(table)]
	response.view = 'plugin_tools/generic.xls'
	return dict(pages=pages)
		
def table2xls(table, query=None):
	from plugin_app import get_represent
	if not query: query = db[table]['id']>0
	rows = db(query).select()
	fields = db[table].fields
	lign1 = ['STT']
	lign2 = ['{{}}']
	for field in fields:			
		name = field
		if (db[table][name].type[:9] == 'reference'): name = name+':'+db[table][name].type[10:]+':name'
		elif db[table][name].type.startswith('list:reference'): name = name+':'+db[table][name].type[15:]+':name'
		if db[table][field].unique: name += ',unique'
		lign1.append(field)
		lign2.append(name)
	sheet = [lign1,lign2]	
	i = 1
	for row in rows:
		lign = [i]
		for field in fields:
			cell = row[field]
			if cell: 
				if (db[table][field].type == 'datetime'): cell = cell.strftime(DATA_DATETIME_FORMAT) 
				elif (db[table][field].type == 'date'): cell = cell.strftime(DATA_DATE_FORMAT) 
				elif (db[table][field].type[:9] == 'reference'): cell = get_represent(table,field,row[field])
				elif db[table][field].type.startswith('list:reference'): cell = get_represent(table,field,row[field])
			else: cell=''
			lign = lign + [cell]
		sheet = [lign] if sheet == [[]] else sheet + [lign]
		i += 1
	return (table, sheet)

def restore_xls():
	table = {}
	book = open_xls_file()
	if book <> None:
		table = restore_data(book, request.args[0])
	return dict(table = table)
	
def restore_data(book, arg):
	tables = data_tables(arg)
	table = {}
	for i in range(book.nsheets):
		if tables[i]==book.sheet_names()[i]:
			sheet = book.sheet_by_index(i)
			if sheet<>None:
				n = insert_from_sheet(tables[i], sheet)
				table[tables[i]] = n
	return table


	
def process():
	from plugin_table import DataTable
	from plugin_process import ProcessCrud
	p = ProcessCrud()
	objects = p.define_objects()
	field1 = p.process().pnext
	field2 = p.procedures().user_group
	field3 = Field("all_data","boolean",default=False,label=T("Chọn tất cả dữ liệu trong bảng"))
	tablename = request.args(0)
	if not tablename:
		db = p.db
		rows = db(db.procedures).select()
		tables = []
		for row in rows:
			if row.tablename not in tables: tables.append(row.tablename)
		
		ops = [OPTION(table,_value=URL(args=[table])) for table in tables]
		form = SELECT([""]+ops,_name="table_select",_class='form-control', _onchange="this.options[this.selectedIndex].value && (window.location = this.options[this.selectedIndex].value);")
		content = DIV(H3(T("Chọn bảng dữ liệu cần chuyển vào qui trình")),form)
	else:
		data = DataTable(tablename=tablename)
		settings = {"check_on":True,"read_on":False,"edit_on":False,"delete_on":False,"index_on":True,"link_modal":True,"orderby":~data.table.id}
		view = data.view(settings=settings)
		form = SQLFORM.factory(field1,field2,field3,keepvalues=True)
		form.append(view)
		msg = H3(T("Chọn Qui trình và Nhóm sử dụng:"))
		if form.process().accepted:
			if request.vars.pnext:
				if request.vars.user_group:
					auth_group = request.vars.user_group
					if request.vars.all_data:
						rows = data.db(data.table).select()
						i = 0
						for row in rows:
							if p.db((objects.tablename==data.tablename)&(objects.table_id==row.id)&(objects.process==request.vars.pnext)).count()==0:
								foldername = data.db.folder(row.folder).name
								objects.insert(folder=row.folder,foldername=foldername,tablename=data.tablename,table_id=row.id,process=request.vars.pnext,auth_group=auth_group)
								i+=1
						msg = H3(T("Đã cập nhật thành công %(name)s bản ghi."%dict(name=i)))		
					elif request.vars.table_id:
						ids = request.vars.table_id
						if isinstance(ids,str): ids = [ids]
						i = 0
						for id in ids:
							if p.db((objects.tablename==data.tablename)&(objects.table_id==id)&(objects.process==request.vars.pnext)).count()==0:
								row = data.table(id)
								foldername = data.db.folder(row.folder).name
								objects.insert(folder=row.folder,foldername=foldername,tablename=data.tablename,table_id=id,process=request.vars.pnext,auth_group=auth_group)
								i+=1
						msg = H3(T("Đã cập nhật thành công %(name)s bản ghi."%dict(name=i)))
					else:	
						msg = H3(T("Chưa chọn dữ liệu cần chuyển."))		
		content = DIV(msg,form)
	response.view = 'plugin_table/table.html'	
	return dict(content=content)
		
	
			
##########################################################
# REPORT
##########################################################		
	
def table_option(table, id=None, order=None, space='', selected=None):
	option = []
	if not order:
		order = db[table].name
		if 'position' in db[table].fields: order = db[table].position | order
	if 'parent' in db[table].fields:
		rows = db(db[table].parent==id).select(orderby=order)
		if (space =='') & (id !=None):
			row = db(db[table].id==id).select().first()
			option = [OPTION(row.name,_value=row.id)]
			if row.id==selected:
				option = [OPTION(row.name,_value=row.id,_selected='selected')]
			space = '---'
		for row in rows:
			op = [OPTION(space+row.name,_value=row.id)]
			if row.id==selected:
				op = [OPTION(space+row.name,_value=row.id,_selected='selected')]
			option += op + table_option(table, row.id, order, space+'---',selected) 	
	else:
		rows = db(db[table].id>0).select(orderby=order)
		for row in rows:
			op = [OPTION(space+row.name,_value=row.id)]
			if row.id==selected:
				op = [OPTION(space+row.name,_value=row.id,_selected='selected')]
			option += op + table_option(table, row.id, order, space+'---',selected) 	
	return option		
