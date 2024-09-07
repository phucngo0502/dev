# -*- coding: utf-8 -*-
import time, os
import urllib2
			
def restart(service):
	try:
		os.popen3('net stop %s'%(service))
		os.popen3('net start %s'%(service))
	except:
		pass

import time
import datetime
		
def sendmail(service):
	mail = auth.settings.mailer
	mail.settings.server = 'smtp.gmail.com:587'
	mail.settings.sender = 'hscvhatinh@gmail.com'
	mail.settings.login = '%s:%s'%('hscvhatinh','khanhnguyen123')
	subject = 'Service %s down at time %s'%(service,datetime.datetime.now())
	emails = ['toan75@gmail.com','manhct.it@gmail.com','it.longhh@gmail.com','anhnt8688@gmail.com']
	# emails = ['toan75@gmail.com','manhct.it@gmail.com']
	emails = ['toan75@gmail.com']
	mail.send(to=emails,subject=subject,message='')

services = [ ('http://127.0.0.1:86/ivinh/static/index.html','www-ivinh86'),
			('http://127.0.0.1:90/dbnd/static/index.html','www-hdnd90'),
			('http://127.0.0.1:85/home/static/index.html','www-capso85'),
			('http://127.0.0.1:91/sxd/static/index.html','www-capso91'),
			('http://127.0.0.1:88/ductho/static/index.html','www-caphuyen88'),
			('http://127.0.0.1:82/dhtn/static/index.html','www-ubht82'),
			('http://127.0.0.1:100/vuquang/static/index.htm','www-master100'),
			# ('http://127.0.0.1:99/profileth/static/index.html','www-thachha99'),
			('http://127.0.0.1:106/sgd/static/index.htm','www-demo106'),
			('http://127.0.0.1:105/soyte/static/index.htm','www-master105'),
			('http://127.0.0.1:93/mctnmt/static/index.htm','www-mysql93'),
			('http://127.0.0.1:108/ict/static/index.html','www-ict108'),
			('http://127.0.0.1:83/hdnd/static/index.html','www-na83')]

services = []			
fname = '%s/private/server_log.txt'%(request.folder)
if not os.path.isfile(fname):
	file = open(os.path.join(fname),'w+')
	file.close()		

import psutil	
while True:

	for id in psutil.pids():
		try:
			p = psutil.Process(id)
			if p.name()=="python.exe": 
				i = 0
				while i<30:
					cpu = p.cpu_percent(interval=10)
					print i, id, cpu
					if cpu<13: break
					time.sleep(20)
					i+=1
				mem = p.memory_percent()	
				if (i==30)|(mem>30): 
					print "Kill", id, cpu
					p.kill()
					fname = '%s/private/server_log.txt'%(request.folder)
					with open(os.path.join(fname), "a") as file:
						file.write('%s %s: %s --- %s\n'%(datetime.datetime.now(),id,cpu,mem))
						file.close()			
		except Exception, e:
			print e
			pass

	for i in range(len(services)):
		print 'Check %s at '%services[i][1], datetime.datetime.now()
		try:
			code = urllib2.urlopen(services[i][0],timeout=10).getcode()
			fname = '%s/private/%s.txt'%(request.folder,services[i][1])
			file = open(os.path.join(fname),'w+')
			tmp = '%s: %s code=%s'%(datetime.datetime.now(),services[i][1],code)
			file.write(tmp)
			file.close()		
		except Exception, e:
			print e
			try:
				restart(services[i][1])
				# sendmail(services[i][1])
				fname = '%s/private/server_log.txt'%(request.folder)
				with open(os.path.join(fname), "a") as file:
					file.write('%s %s: %s\n'%(datetime.datetime.now(),services[i][1],e))
					file.close()				
			except:
				pass
			pass
	time.sleep(30) # check every second	