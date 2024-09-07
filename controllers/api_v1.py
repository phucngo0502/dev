
@request.restful()
def login():
	response.view = 'generic.' + request.extension

	def GET(user_name, password):
		from datatables import define_equipment_token, define_salesman_web
		define_equipment_token(db, False)
		define_salesman_web(db, False)

		if user_name == None or user_name == "":
			raise HTTP(400, 'Chưa nhập tên đăng nhập')
		if password == None or password == "":
			raise HTTP(400, 'Chưa nhập mật khẩu')
		user_name = user_name.lower()
		user = auth.login_bare(user_name, password)
		if not user:
			raise HTTP(401, 'Tên đăng nhập hoặc mật khẩu không đúng')
		mem = auth.get_list_auth_membership(user.id)
		myjwt.verify_expiration = False
		token = myjwt.jwt_token_manager()

		data = {'status': "success", 'auth_user_id': user.id, 'auth_user_name': auth.get_name(user.id),
		        "auth_user_images": user.image, 'auth_user_email': user.email, 'auth_user_phone': user.phone, 'user_name': user.username, 'is_password': user_pass, 'mem': mem, }
		from itertools import chain
		dest = dict(chain(data.items(), eval(token).items()))

		return dest

	return locals()


@request.restful()
def reset_password():
	response.view = 'generic.' + request.extension

	def POST(user_name):
		user = db(db.auth_user.username == user_name).select().first()
		if not user:
			raise HTTP(400, 'Tên đăng nhập không tồn tại.')
		if auth.email_reset_password(user):
			raise HTTP(200, 'Kiểm tra email đã đăng ký để lấy lại mật khẩu.')
		else:
			raise HTTP(400, 'Không thể gửi email. Vui lòng liên hệ quản trị hệ thống.')

	return locals()
