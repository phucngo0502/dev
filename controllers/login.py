@auth.requires_login()	
def index():	
	 redirect(URL(c='plugin_auth',f='login'))
