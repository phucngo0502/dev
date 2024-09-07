 
from gluon import current, HTTP
from html import *
import datetime, os

	
def show_product(rows,is_class='col-lg-2 col-md-3'):

	from plugin_cms import Cms
	cms = Cms()
	
	div = DIV(_class=is_class)
	div1 = DIV(_class='folder_product')
	div_sale = DIV(_class='col-md-12 col-sm-12 col-xs-12 not_padding ')
	for row in rows:
	
		a_img = A(IMG(_src=cms.field_format(row,"avatar","upload",settings)),_href=cms.url_content(row,"product"))
		div_sale.append(a_img)
		div1.append(div_sale)
		div.append(div1)
	return div	
	
