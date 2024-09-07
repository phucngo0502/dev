###################################################
# This file was developed by Anhnt
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 8/03/2016
###################################################


def index():
	from plugin_app import select_option
	from plugin_process import Process
	process = Process()
	widget = DIV( process.cms.list_folder(),_style='with:30%; float:left;')
	
	div = DIV(_class="panel panel-default")
	heading = DIV(_class='panel-heading')
	heading.append(H4('Tạo báo cáo',_class='panel-title'))
	div.append(heading)
	
	wr_search = DIV(widget)
	div_time = DIV(_class='input-group',_style="width: 40%;float: left;")
	div_time.append(SPAN('Từ ngày ',_class="input-group-addon"))
	div_time.append(INPUT(_name='startday',_type='text',_class='form-control date'))
	div_time.append(SPAN(' đến ngày ',_class="input-group-addon"))
	div_time.append(INPUT(_name='endday',_type='text',_class='form-control date'))
	wr_search.append(div_time)
	ajax = "ajax('%s', ['list_folder','startday','endday'], 'content_report')"%(URL(f='act_report'))
	wr_search.append(A('Lọc dữ liệu',_onclick=ajax,_class='btn btn-primary'))
	
	content = DIV(wr_search,_class='panel-body')
	content.append(DIV(_id='content_report'))
	div.append(content)
	response.view = 'admin/report.html'	
	return dict(content=div)
	
def act_report():
	from plugin_cms import CmsFolder,CmsModel
	db = CmsModel().db
	folders = CmsFolder().get_folders(request.vars.list_folder)
	dcontent = CmsModel().define_dcontent()
	query = dcontent.folder.belongs(folders)
	if request.vars.startday:
		query &= dcontent.publish_on>=request.vars.startday
	if request.vars.endday:
		query &= dcontent.publish_on<=request.vars.endday
	rows  = db(query).select()
	table = TABLE(_class='table',_id="table2excel")
	table.append(TR(TH('Stt'),TH('Danh mục'),TH('Tiêu đề'),TH('Người biên tập'),TH('Ngày xuất bản')))
	i = 1
	for row in rows:
		table.append(TR(TD(i),TD(row.folder.label) ,TD(row.name),TD(row.creator),TD(row.publish_on.strftime("%d/%m/%Y"))))
		i+=1
	div = DIV(H4('Có tổng %s bản ghi'%(len(rows))))
	div.append(table)
	content = DIV(A('Xuất Excel',_id='export_excel',_class='btn btn-primary'))
	content.append(div)
	scr ='''
	<script>
		$("#export_excel").click(function(){
			$("#table2excel").table2excel({
				exclude: ".noExl",
				name: "Excel Document Name"

			});
		});

	</script>
	'''
	content.append(XML(scr))
	return content
	
	
	
	
	