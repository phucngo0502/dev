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
	
def crawler_rss(link,records=10):
	try:
		from gluon.contrib import feedparser
		from bs4 import BeautifulSoup
		url = link
		d = feedparser.parse(url)
		if len(d.entries) == 0: return T("No rss entry")
		rows = []
		i = 0
		for entry in d.entries:
			if i == int(records or 10): break
			i+=1
			keys = entry.keys()
			row = {}
			for key in ["link","title","image","description","published"]:
				row[key] = entry[key] if entry.has_key(key) else None
			if entry.has_key("summary"):
				soup = BeautifulSoup(entry["summary"])
				tag = soup.find("img")
				if tag: 
					if not row["image"]: row["image"] = tag["src"]
					tag.replace_with("")
				tag = soup.find("a")
				if tag: 
					if not row["link"]: row["link"] = tag["href"]
					tag.replace_with("")
				row["description"] = soup.get_text()
			rows.append(row)
		content = UL()	
		for row in rows:
			div_img = DIV(_class='img')
			if row.has_key("image"): div_img.append(IMG(_src=row["image"],_class="rss-image"))		
			div_img.append(BR())
			if row.has_key('title'): div_img.append(row['title'])
			content.append(LI(div_img))
		div = DIV(_class='slider')
		div.append(content)
		return DIV(div,_class='nonImageContent')
	except Exception, e:
		return e
		