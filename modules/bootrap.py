# -*- coding: utf-8 -*-
###################################################
# This content was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 0.1 Date: 18/05/2015
###################################################

from html import *

class Panel():
	def __init__(self,**attr):
		self.elements = attr.get("elements",[])
		self.id = attr.get("id","panel-group")
		self.cls = attr.get("cls","panel-default")
		pass
		
	def __str__(self):
		return str(self.xml())

	def xml(self):
		return self.panel(self.elements,self.id,self.cls)
	
	def panel(self,elements=[("title",["elem1","elem2"])],id="panel-group",cls="panel-default",collapse=True):
		content = self.panel_group(id)
		i = 1
		for e in elements:
			child = "%s-%s"%(id,i)
			heading = self.panel_heading(id, child, e[0], collapse)
			element = self.panel_element(child)
			body = DIV(_class="panel-body")
			for v in e[1]:	
				body = self.panel_body(v)
				element.append(body)
			default = self.panel_default(cls)
			default.append(heading)
			default.append(element)
			content.append(default)
			i+=1
		return content

	def panel_group(self,parent):	
		return DIV(_class="panel-group",_id=parent)
	
	def panel_default(self, cls="panel-default"):
		return DIV(_class="panel %s"%cls)
				
	def panel_heading(self, parent, child, title, collapse):
		content = DIV(_class="panel-heading")
		if collapse:
			content.append(XML('<a class="panel-title" data-toggle="collapse"  aria-expanded="false" data-parent="#%s" href="#%s">%s<span class="fa arrow"></span></a>'%(parent,child,title)))
		else:	
			content.append(XML('<a class="panel-title">%s</a>'%(title)))
		return content 

	def panel_element(self, child, status="in"):
		return DIV(_id=child, _class="panel-collapse %s"%status)
		
	def panel_body(self, content):
		return DIV(content,_class='list-group-item')
		
class Tab():
	def __init__(self,**attr):
		pass
		
	def tabs(self,elements=[("title1","elem1"),("title2","elem2")],id="tabs"):
		heading = self.ul()
		content = self.tab_content()
		i = 1
		for e in elements:
			child = "%s-%s"%(id,i)
			s = "active" if i==1 else ""
			heading.append(self.li(child,e[0],s))
			content.append(self.tab_pane(child,e[1],s))
			i+=1
		tab = self.tabbable(id)
		tab.append(heading)
		tab.append(content)
		return tab

	def ul(self):	
		return UL(_class="nav nav-tabs")		

	def li(self,id,title,status=""):	
		return LI(XML('<a href="#%s" data-toggle="tab">%s</a>'%(id,title)),_class=status)

	def tabbable(self,id="tabs"):	
		return DIV(_class="tabbable",_id=id)
		
	def tab_content(self):	
		return DIV(_class="tab-content")
		
	def tab_pane(self,id,content="",status=""):	
		return DIV(content,_class="tab-pane %s"%status,_id=id)
		
class Menu():
	def __init__(self,**attr):
		pass
		
	def vertical(self,elements=[("Menu1","#","fa-dashboard",[])],deep=1,id="menu-sf-vertical"):	
		content = UL(_class="sf-menu sf-vertical",_id=id) if deep==1 else UL()
		for e in elements:
			icon = "" if e[2]=="" else I(_class="fa %s fa-fw"%e[2])
			li = LI(A(icon,e[0],_href=e[1],_class="sf_%s"%deep))
			if len(e[3])>0: li.append(self.vertical(e[3],deep+1))
			content.append(li)
		return content
		
	# Them 1 kieu hien thi menu
	def side(self,elements=[("Menu1","#","fa-dashboard",[])],deep=1,id="side-menu"):	
		content = UL(_class="nav",_id=id) if deep==1 else UL()
		for e in elements:
			icon = "" if e[2]=="" else I(_class="fa %s fa-fw"%e[2])
			if len(e[3])>0: 
				li = LI(A(icon,SPAN(_class="fa arrow"),e[0],_href=e[1],_class="sf_%s"%deep))
				li.append(self.side(e[3],deep+1))
			else:
				li = LI(A(icon,e[0],_href=e[1],_class="sf_%s"%deep))
			content.append(li)
		return content	


class Dashboard():
	def __init__(self,**attr):
		self.href = attr.get("href","#")
		self.panel = attr.get("panel","panel-primary")
		self.icon = attr.get("icon","fa-support")
		self.title = attr.get("title","News")
		self.quantity = attr.get("quantity",0)
		self.caption = attr.get("caption","Detail")
		pass
		
	def __str__(self):
		return self.create(href=self.href,panel=self.panel,icon=self.icon,title=self.title,quantity=self.quantity,detail=self.caption)

	def create(self,href="#",panel="panel-primary",icon="fa-support",title="News",quantity=0,detail="Detail"):
		return '''<div class="col-lg-3 col-md-6">
	<div class="panel %s">
		<div class="panel-heading">
			<div class="row">
				<div class="col-xs-3">
					<i class="fa %s fa-5x"></i>
				</div>
				<div class="col-xs-9 text-right">
					<div class="huge">%s</div>
					<div>%s</div>
				</div>
			</div>
		</div>
		<a href="%s">
			<div class="panel-footer">
				<span class="pull-left">%s</span>
				<span class="pull-right"><i class="fa fa-arrow-circle-right"></i></span>
				<div class="clearfix"></div>
			</div>
		</a>
	</div>
</div>'''%(panel,icon,quantity,title,href,detail)

	def create2(self,href="#",panel="panel-primary",icon="fa-support",title="News",quantity=0,detail="Detail"):
		return '''<div class="col-lg-3 col-md-6">
	<div class="panel %s">
		<div class="panel-heading">
			<a href="%s">
			<div class="row">
				<div class="col-xs-3">
					<i class="fa %s fa-3x"></i>
				</div>
				<div class="col-xs-9 text-right">
					<div class="badge huge30">%s</div>
					<div>%s</div>
				</div>
			</div>
			</a>
		</div>
		<a href="%s">
			<div class="panel-footer">
				<span class="pull-left">%s</span>
				<span class="pull-right"><i class="fa fa-arrow-circle-right"></i></span>
				<div class="clearfix"></div>
			</div>
		</a>
	</div>
</div>'''%(panel,href,icon,quantity,title,href,detail)

		
class Modals:		
	# size: modal-lg,modal-md (Kích thước Modals)
	# id_load: Id vùng lấy dữ liệu ở trang đích.
	# reload: Chạy lại khi đóng Modals (true, false)
	# rewrite: Ghi lại các vùng dữ liệu
	
	def __init__(self,caption=('Preview'),title=None,close=("Close"),id=None,cls=None,size='modal-lg',source=None,id_load='',rewrite = None,target='',url=None,reload=False):
		import uuid
		if title==None: self.title = caption
		else: self.title=title
		self.caption=caption
		self.close=close
		self.id=id or 'modal_'+ str(uuid.uuid4())
		self.source = source
		self.size = size
		self.id_load = id_load
		self.update = ''
		if rewrite:
			for re in rewrite:
				self.update += "jQuery.ajax({url:\'%s\',success:function(data){jQuery('#%s').html(data);}});"%(re[0],re[1])
		if reload:
			self.update += 'location.reload();'
	def xml(self):
		script = '''
			<script type="text/javascript">
				var id = '#%s';
				$(id).on('show.bs.modal', function (event) {
					$("#w_content_%s").load( "%s %s" );
				});
				$(id).on('hidden.bs.modal', function (event) {
					$("#w_content_%s").empty();
					%s
				});
			</script>'''%(self.id,self.id,self.source,self.id_load,self.id,self.update)
			
		content = '''<a data-toggle="modal" data-target="#%s" data-backdrop="static">%s</a>
		<div class="modal fade" id="%s" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
			<div class="modal-dialog %s">
				<div class="modal-content">
					<div class="modal-header">
						<button type="button" class="close" data-dismiss="modal" aria-label="Close" id="button_close"><span aria-hidden="true">&times;</span></button>
						<h4 class="modal-title" id="myModalLabel">%s</h4>
					</div>
					<div class="modal-body">
						<div id="w_content_%s"></div>
					</div>
				</div>
			</div>
		</div>'''%(self.id,self.caption,self.id,self.size,self.title,self.id)
		return content + script
			
class Modals2:		
	# size: modal-lg,modal-md (Kích thước Modals)
	# id_load: Id vùng lấy dữ liệu ở trang đích.
	# reload: Chạy lại khi đóng Modals (true, false)
	# rewrite: Ghi lại các vùng dữ liệu
	
	def __init__(self,caption=('Preview'),close=("Close"),id=None,cls=None,size='mo-lg',source=None,id_load='',rewrite = None,target='',url=None,reload=False):
		import uuid
		self.caption=caption
		self.close=close
		self.id=id or 'modal_'+ str(uuid.uuid4())
		self.source = source
		self.size = size
		self.id_load = id_load
		self.update = ''
		if rewrite:
			for re in rewrite:
				self.update += "jQuery.ajax({url:\'%s\',success:function(data){jQuery('#%s').html(data);}});"%(re[0],re[1])
		if reload:
			self.update += 'location.reload();'
	def xml(self):
		script = '''
			<script type="text/javascript">
				var id = '#%s';
				jQuery(id).on('show', function () {
					jQuery("#w_content_%s").load( "%s %s" );
				});
				jQuery(id).on('hide', function () {%s});
			</script>'''%(self.id,self.id,self.source,self.id_load,self.update)
			
		content = '''<a data-toggle="modal" data-target="#%s" data-backdrop="static">%s</a>
		<div id="%s"  class="modal fade %s" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal" aria-label="Close" id="button_close"><span aria-hidden="true">&times;</span></button>
				<h4 class="modal-title" id="myModalLabel">%s</h4>
			</div>
			<div class="modal-body">
				<div id="w_content_%s"></div>
			</div>
		</div>'''%(self.id,self.caption,self.id,self.size,"",self.id)
		return content + script
		
class AnchorLink():
	def __init__(self,titles,contents,**attr):
		self.titles = titles
		self.contents = contents
		self.ul_class = attr.get("ul_class","nav bs-docs-sidenav")
		self.ul_style = attr.get("ul_style","position:fixed;top:40%;right:0;margin-right:10%;")
		pass
		
	def link(self):	
		i = 0		
		content = UL(_class=self.ul_class,_style=self.ul_style)
		for title in self.titles:
			content.append(LI(A(title,_href="#link%s"%i)))
			i+=1
		return content
		
	def page(self):	
		content = SPAN()
		i = 0		
		for e in self.contents:
			content.append(H2(A(self.titles[i],_name="link%s"%i,_class="anchorjs-link"),_class="page-header"))
			content.append(DIV(e,_class="bs-docs-section"))
			i+=1
		return content
