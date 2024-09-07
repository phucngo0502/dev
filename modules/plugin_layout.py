###################################################
# This file was developed by ToanLK
# It is released under BSD, MIT and GPL2 licenses
# Version 1.0 Date: 10/03/2015
###################################################
# -*- coding: utf-8 -*-

import os
import cStringIO
import re
import urllib2
from gluon import current
from html import *
from bs4 import BeautifulSoup
T = current.T
request = current.request


def get_portlets(db):
	title = T('Portlet')
	id = 'Two'
	content = pannel_ul()
	content.append(panel_title(title,'Setting',A('Portlet',_href=URL(r=current.request,c='plugin_portlet',f='index'))))
	li = panel_li()
	rows = db(db.portlet).select()
	for row in rows:
		preview = row.name
		view = portlet.display(row.id)
		li.append(panel_drag(row.id, preview, view))
	content.append(li)
	return content

def panel_title(title,help='Help',content=''):
	return XML('''
	<li class="nav-header">
	<div class="pull-right popover-info">
	 <i class="glyphicon glyphicon-question-sign">
	 </i>
	 <div class="popover fade right">
	  <div class="arrow">
	  </div>
	  <h3 class="popover-title">
	   %s
	  </h3>
	  <div class="popover-content">
	   %s
	  </div>
	 </div>
	</div>
	<i class="glyphicon-plus glyphicon"></i>
	 %s
	</li>'''%(help, content, title))

def panel_drag(id, preview, view, remove='remove',drag='drag'):
	return XML('''
	<div class="lyrow ui-draggable">
	<a class="remove label label-danger" href="#close">
	<i class="glyphicon-remove glyphicon">
	</i>
	%s
	</a>
	<span class="drag label label-default">
	<i class="glyphicon glyphicon-move">
	</i>
	%s
	</span>
	%s
	</div>
	'''%(remove,drag,panel_content(id, preview, view)))

def panel_content(id, preview, view):
	return XML('''
	<div class="preview">
		%s
	</div>         
	<div class="view" id="%s">
		%s
	</div>'''%(preview, id, view))
	
def panel_ul():
	return UL(_class="nav nav-list accordion-group")

def panel_li():
	return LI(_class="rows",_id="estRows",_style="display: none;")