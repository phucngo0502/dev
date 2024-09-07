from gluon import current, HTTP
from html import *
import datetime, os

def get_start_end_week(datenow=None):
	import datetime;
	if datenow==None:
		datenow = datetime.datetime.now()
	date = datenow.ctime()
	thu = date[0:3]
	start = 0
	end   = 0
	if thu == 'Mon':
		start = 0
		end = 6
	elif thu == 'Tue':
		start = 1
		end = 5
	elif thu == 'Wed':
		start = 2
		end = 4
	elif thu == 'Thu':
		start = 3
		end = 3
	elif thu == 'Fri':
		start = 4
		end = 2
	elif thu == 'Sat':
		start = 5
		end = 1
	elif thu == 'Sun':
		start = 6
		end = 0
	return start,end
	