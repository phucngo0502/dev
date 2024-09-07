# -*- coding: utf-8 -*-
import sys

from plugin_cms import Cms

cms = Cms()


@auth.requires_login()
def call():
    return service()


# @cache(request.env.path_info, time_expire=3600, cache_model=cache.ram)
def calendar():
    try:
        response.view = 'layout/lich2/%s' % (cms.layout_folder() or 'index.html')
    except:
        response.view = 'layout/trangchu.html'
    return response.render(dict())


def index():
    redirect(URL(f='folder', args=request.args))
    
        
def phone_login():
    # response.view = 'admin/phone_login.html'
    response.view = 'site/ghephang/default/login.html'
    return dict(form=auth())

def otp_login():
    response.view = 'site/ghephang/default/login.html'
    return dict(form=auth())


#@cache(request.env.path_info, time_expire=600, cache_model=cache.ram)
def folder():
    if request.args == []:
        redirect(URL(f='folder',args=[page_home]))
    elif request.args(0) == "taiapp":
        redirect('https://ghephangkhachhang.page.link/install_app')
    try:
        
        response.view = 'site/%s/%s/%s'%(site_name,template,cms.layout_folder() or '404.html')
    except:
        response.view = 'layout/404.html'
    return response.render(dict())

# # @cache(request.env.path_info, time_expire=600, cache_model=cache.ram)
# def folder():
    # if request.args == []:
        # redirect(URL(f='folder', args=[page_home]))
    # try:

        # if cms.layout_folder():
            # if request.args(0) == "san-pham":
                # if request.args(1):
                    # response.view = 'site/%s/%s/%s' % (site_name, template, cms.layout_folder())
                # else:
                    # response.view = 'site/%s/%s/%s' % (site_name, template, 'api_folder.html')
            # else:
                # response.view = 'site/%s/%s/%s' % (site_name, template, cms.layout_folder())

        # else:
            # import requests
            # url_produc = '%s/api/v1/folder/%s.json?field=name' % (api_naso, request.args(0))
            # r1 = requests.get(url_produc).json()
            # r_produc = r1['result']
            # if len(r_produc) > 0:
                # response.view = 'site/%s/%s/%s' % (site_name, template, 'api_folder.html')
            # else:
                # response.view = 'site/%s/%s/%s' % (site_name, template, '404.html')
    # except Exception, e:
        # response.view = 'site/%s/%s/%s' % (site_name, template, '404.html')
    # return response.render(dict())


# @cache(request.env.path_info, time_expire=600, cache_model=cache.ram)
def xemtruoc():
    if request.args == []:
        redirect(URL(f='folder', args=[page_home]))
    try:
        response.view = 'site/%s/%s/%s' % (site_name, template, cms.layout_folder() or '404.html')
    except:
        response.view = 'layout/404.html'
    return response.render(dict())


# @cache(request.env.path_info, time_expire=3600, cache_model=cache.ram)
def read():
    try:
        # template = setting_config('template','')
        if template != '':
            response.view = 'site/%s/%s/%s' % (site_name, template, cms.layout() or '404.html')
        else:
            response.view = 'site/%s' % (cms.layout() or '404.html')
        cms.insert_read()
    except:
        response.view = 'layout/404.html'
    return response.render(dict())


def load_portlet():
    portlet_id = request.args(0)
    if portlet_id:
        return portlet.display(portlet_id)
    else:
        return ''


def feed():
    from plugin_cms import CmsFolder, CmsModel
    folder_id = CmsFolder().get_folder()
    ar_entries = []
    entries = CmsFolder().get_rows(folder=request.args(0))
    link_page = 'http://' + request.env.http_host
    for entry in entries:
        link = CmsFolder().url_content(entry)
        description = str(entry.description)
        if entry.avatar:
            avarta = CmsModel().get_images_content(entry.dtable, entry.avatar)
            description = '<a href="' + link_page + str(link) + '">' + str(avarta) + '</a>' + description
        ar_entries.append(dict(title=entry.name.decode('utf-8'),
                               link=link_page + str(link),
                               description=XML(description.decode('utf-8')),
                               created_on=entry.publish_on))
    return dict(title='Feed', link=link_page, description='Feed', created_on=request.now, entries=ar_entries)


# Product


def add_cart_r_number():
    kho_hang = request.vars.kho_hang
    pid = request.vars.pid
    ar_carts = []

    try:
        num_carts = int(request.vars.quantity)
    except:
        num_carts = 1
    if request.cookies.has_key('cart_shop'):
        carts = eval(request.cookies['cart_shop'].value)
        i = 0
        for cart in carts:
            cart = eval(cart)
            if cart['id'] == pid:
                ar_carts.append(str({'id': str(cart['id']), 'num': str(int(cart['num']) + num_carts), 'kho_hang': kho_hang}))
                i += 1
            else:
                ar_carts.append(str({'id': str(cart['id']), 'num': str(cart['num']), 'kho_hang': str(cart['kho_hang'])}))
        if i == 0:
            ar_carts.append(str({'id': pid, 'num': str(num_carts), 'kho_hang': kho_hang}))
    else:
        ar_carts.append(str({'id': pid, 'num': str(num_carts), 'kho_hang': kho_hang}))
    response.cookies['cart_shop'] = str(ar_carts)
    response.cookies['cart_shop']['expires'] = 24 * 3600
    response.cookies['cart_shop']['path'] = '/'
    response.flash = T("Add new cart!")

    # load view_carts() nhung ko request duoc cookies moi
    redirect(URL(c='portal', f='folder', args=['gio-hang']))


def update_cookies():
    try:
        pid = request.vars.pid
        number_so_luong = request.vars['number_so_luong_%s' % (pid)]
        ar_carts = []
        if request.args(0) == 'delete':
            carts = eval(request.cookies['cart_shop'].value)
            for cart in carts:
                cart = eval(cart)
                if cart['id'] == pid:
                    ar_carts.append(str({'id': str(cart['id']), 'num': 0}))
                else:
                    ar_carts.append(str({'id': str(cart['id']), 'num': str(cart['num'])}))
        elif request.args(0) == 'update':
            if request.cookies.has_key('cart_shop'):
                carts = eval(request.cookies['cart_shop'].value)

                for cart in carts:
                    cart = eval(cart)
                    if cart['id'] == pid:
                        ar_carts.append(str({'id': str(cart['id']), 'num': number_so_luong}))
                    else:
                        ar_carts.append(str({'id': str(cart['id']), 'num': str(cart['num'])}))
        response.cookies['cart_shop'] = str(ar_carts)
        response.cookies['cart_shop']['expires'] = 24 * 3600
        response.cookies['cart_shop']['path'] = '/'
        response.flash = T("Cập nhật thành công!")

        div = DIV()
        num_car = 0
        tong_tien = 0
        carts = ''
        from plugin_app import number_format
        table = TABLE(_class='table')

        carts = ar_carts
        from plugin_cms import CmsModel
        from plugin_cms import CmsFolder
        db = cms.db
        cms.define_table('product')

        table.append(TR(TH('Sản phẩm'), TH('Số lượng'), TH(''), TH('Giá'), TH(B('Thành tiền')), TH(B('Chức năng'))))
        for cart in carts:
            cart = eval(cart)
            if int(cart['num']) > 0:
                row = db((db.product.id == cart['id'])).select().first()
                i = 1
                if row:

                    if row.price:
                        tong_tien += int(row.price) * int(cart['num'])
                    ajax_update = "ajax('%s', ['number_so_luong_%s'],'order_view')" % (URL(f='update_cookies', args=['update'], vars=dict(pid=row.id)), row.id)
                    ajax_delete = "ajax('%s', ['number_so_luong_%s'],'order_view')" % (URL(f='update_cookies', args=['delete'], vars=dict(pid=row.id)), row.id)
                    input_num = DIV(INPUT(_type='text', _class='number_so_luong', _name='number_so_luong_%s' % (row.id), _value=cart['num']), A(SPAN(_class='glyphicon glyphicon-floppy-disk'), _title='Lưu thay đổi số lượng', _onclick=ajax_update, _style="padding: 0 10px;"))
                    if row.price:
                        table.append(TR(TD(row.name, ': '), TD(input_num), TD(' * '), TD(number_format(row.price), ' VNĐ'), TD(B(number_format(int(row.price) * int(cart['num'])), ' VNĐ'), TD(A(SPAN(_class='glyphicon glyphicon-trash'), _onclick=ajax_delete)))))
                    else:
                        table.append(TR(TD(row.name, ': '), TD(input_num), TD(' * '), TD(), TD('', TD(A(SPAN(_class='glyphicon glyphicon-trash'), _onclick=ajax_delete)))))

        div.append(table)
        # if tong_tien<300000:
        # p_tong = DIV(SPAN('Phí vận chuyển: '))
        # p_tong.append(str('30,000')+' VNĐ')
        # div.append(B(p_tong,_class='text-right'))
        # tong_tien += 30000
        p_tong = DIV(SPAN('Tổng tiền: '))
        p_tong.append(str(number_format(tong_tien)) + ' VNĐ')
        div.append(B(p_tong, _class='text-right'))

        div.append(DIV(DIV(A(I(_class='icon-backward'), ' Tiếp tục mua hàng', _href=URL(c='portal', f='folder', args=[page_home]), _class='btn'), _class='pull-left'), DIV(A('Thanh toán ', I(_class='icon-forward'), _href=URL(c='portal', f='folder', args=['thanh-toan']), _class='btn'), _class='pull-right'), _class='select_order'))

        return div
    except Exception, e:
        return e


def add_cart():
    pid = request.vars.pid
    ar_carts = []
    if request.cookies.has_key('cart_shop'):
        carts = eval(request.cookies['cart_shop'].value)
        i = 0
        for cart in carts:
            cart = eval(cart)
            if cart['id'] == pid:
                ar_carts.append(str({'id': str(cart['id']), 'num': str(int(cart['num']) + 1)}))
                i += 1
            else:
                ar_carts.append(str({'id': str(cart['id']), 'num': str(cart['num'])}))
        if i == 0:
            ar_carts.append(str({'id': pid, 'num': str(1)}))
    else:
        ar_carts.append(str({'id': pid, 'num': str(1)}))

    response.cookies['cart_shop'] = str(ar_carts)
    response.cookies['cart_shop']['expires'] = 24 * 3600
    response.cookies['cart_shop']['path'] = '/'
    response.flash = T("Add new cart!")

    # load view_carts() nhung ko request duoc cookies moi

    div = DIV()
    num_car = 0
    tong_tien = 0
    carts = ar_carts
    from plugin_cms import CmsModel
    cms = CmsModel()
    db = cms.db
    cms.define_table('san_pham')
    from plugin_app import number_format

    for cart in carts:
        cart = eval(cart)
        row = db((db.san_pham.id == cart['id'])).select().first()
        if row:
            div1 = DIV(_class='list_cart')
            ul = UL()
            ul.append(LI(row.name))
            ul.append(LI(SPAN('Số lượng: '), cart['num']))
            ul.append(LI(SPAN('Giá: '), number_format(row.gia_san_pham), ' VNĐ'))
            div1.append(DIV(IMG(_src=cms.get_avatar('san_pham', row.avatar), _class='thumbnail'), _class='col-md-4 box_ivinh'))
            div1.append(DIV(ul, _class='col-md-8 box_ivinh'))
            div.append(div1)
            div.append(HR())
            tong_tien += int(row.gia_san_pham) * int(cart['num'])
            num_car += 1
    p_tong = DIV(SPAN('Tổng tiền: '))
    p_tong.append(str(number_format(tong_tien)) + ' VNĐ')
    div.append(B(p_tong, _class='text-right'))
    div.append(A('Gửi đơn hàng', _href=URL(c='portal', f='folder', args=['checkout']), _class='btn btn-success'))
    return div


def view_carts():
    div = DIV()
    num_car = 0
    tong_tien = 0
    carts = ''
    try:
        if request.cookies.has_key('cart_shop'):
            carts = eval(request.cookies['cart_shop'].value)
            from plugin_cms import CmsModel
            from plugin_cms import CmsFolder
            db = cms.db
            cms.define_table('product')
            from plugin_app import number_format

            for cart in carts:
                cart = eval(cart)
                row = db((db.product.id == cart['id'])).select().first()
                if row:
                    div1 = DIV(_class='list_cart')
                    ul = UL()
                    ul.append(LI(row.name))
                    ul.append(LI(SPAN('Số lượng: '), cart['num']))
                    ul.append(LI(SPAN('Giá: '), number_format(row.gia_ban), ' VNĐ'))
                    div1.append(DIV(cms.get_images_content('product', row.avatar), _class='col-md-4 box_ivinh'))
                    div1.append(DIV(ul, _class='col-md-8 box_ivinh'))

                    div.append(div1)
                    div.append(HR())
                    tong_tien += int(row.gia_ban) * int(cart['num'])
                    num_car += 1
        if num_car > 0:
            p_tong = DIV(SPAN('Tổng tiền: '))
            p_tong.append(str(number_format(tong_tien)) + ' VNĐ')
            div.append(B(p_tong, _class='text-right'))
            div.append(A('Gửi đơn hàng', _href=URL(c='portal', f='folder', args=['checkout']), _class='btn btn-success'))
        else:
            div.append('Giỏ hàng trống')
    except Exception, e:
        return e
    return div


def view_order():
    div = DIV(_id="order_view")
    num_car = 0
    tong_tien = 0
    carts = ''
    from plugin_app import number_format
    table = TABLE(_class='table')
    if request.cookies.has_key('cart_shop'):
        carts = eval(request.cookies['cart_shop'].value)
        from plugin_cms import CmsModel
        from plugin_cms import CmsFolder
        db = cms.db
        cms.define_table('product')
        table.append(TR(TH('Sản phẩm'), TH('Số lượng'), TH(''), TH('Giá'), TH(B('Thành tiền')), TH(B('Hủy bỏ'))))
    for cart in carts:
        cart = eval(cart)
        if int(cart['num']) > 0:
            row = db((db.product.id == cart['id'])).select().first()
            i = 1
            if row:
                rowname = DIV(cms.get_images_content('product', row.avatar), A(row.name, _href=cms.url_content(row, table='product')), _class='produc_order')
                if row.price:
                    tong_tien += int(row.price) * int(cart['num'])
                ajax_update = "ajax('%s', ['number_so_luong_%s'],'order_view')" % (URL(f='update_cookies', args=['update'], vars=dict(pid=row.id)), row.id)
                ajax_delete = "ajax('%s', ['number_so_luong_%s'],'order_view')" % (URL(f='update_cookies', args=['delete'], vars=dict(pid=row.id)), row.id)
                input_num = DIV(INPUT(_type='text', _class='number_so_luong', _name='number_so_luong_%s' % (row.id), _value=cart['num']), A(SPAN(_class='glyphicon glyphicon-floppy-disk'), _title='Lưu thay đổi số lượng', _onclick=ajax_update, _style="padding: 0 10px;"))
                if row.price:
                    table.append(TR(TD(rowname), TD(input_num), TD(' * '), TD(number_format(row.price), ' VNĐ'), TD(B(number_format(int(row.price) * int(cart['num'])), ' VNĐ'), TD(A(SPAN(_class='glyphicon glyphicon-trash'), _onclick=ajax_delete)))))
                else:
                    table.append(TR(TD(rowname), TD(input_num), TD(' * '), TD(), TD('', TD(A(SPAN(_class='glyphicon glyphicon-trash'), _onclick=ajax_delete)))))
    div.append(table)
    # if tong_tien<300000:
    # p_tong = DIV(SPAN('Phí vận chuyển: '))
    # p_tong.append(str('30,000')+' VNĐ')
    # div.append(B(p_tong,_class='text-right'))
    # tong_tien += 30000
    p_tong = DIV(SPAN('Tổng tiền: '))
    p_tong.append(str(number_format(tong_tien)) + ' VNĐ')
    div.append(B(p_tong, _class='text-right'))

    div.append(DIV(DIV(A(I(_class='icon-backward'), ' Tiếp tục mua hàng', _href=URL(c='portal', f='folder', args=[page_home]), _class='btn'), _class='pull-left'), DIV(A('Thanh toán ', I(_class='icon-forward'), _href=URL(c='portal', f='folder', args=['thanh-toan']), _class='btn'), _class='pull-right'), _class='select_order'))
    return div


def view_wishlist():
    div = DIV(_id="order_view")
    num_car = 0
    tong_tien = 0
    carts = ''
    from plugin_app import number_format
    table = TABLE(_class='table')
    if request.cookies.has_key('cart_shop'):
        carts = eval(request.cookies['cart_shop'].value)
        from plugin_cms import CmsModel
        from plugin_cms import CmsFolder
        db = cms.db
        cms.define_table('product')
        table.append(TR(TH('Hình ảnh'), TH('Tên sản phẩm'), TH('Giá bán'), TH('Đặt hàng')))
    for cart in carts:
        cart = eval(cart)
        if int(cart['num']) > 0:
            row = db((db.product.id == cart['id'])).select().first()
            i = 1
            if row:
                rowname = DIV(cms.get_images_content('product', row.avatar), A(row.name, _href=cms.url_content(row, table='product')), _class='produc_order')
                if row.price:
                    table.append(TR(TD(rowname), TD(number_format(row.price), ' VNĐ')))
                else:
                    table.append(TR(TD(rowname), ))
    div.append(table)
    # if tong_tien<300000:
    # p_tong = DIV(SPAN('Phí vận chuyển: '))
    # p_tong.append(str('30,000')+' VNĐ')
    # div.append(B(p_tong,_class='text-right'))
    # tong_tien += 30000

    div.append(DIV(DIV(A(I(_class='icon-backward'), ' Tiếp tục mua hàng', _href=URL(c='portal', f='folder', args=[page_home]), _class='btn'), _class='pull-left'), DIV(A('Xem giỏ hàng ', I(_class='icon-forward'), _href=URL(c='portal', f='folder', args=['checkout']), _class='btn'), _class='pull-right'), _class='select_order'))
    return div


def view_thanh_toan():
    div = DIV(_id="order_view")
    num_car = 0
    tong_tien = 0
    carts = ''
    from plugin_app import number_format
    table = TABLE(_class='table')
    if request.cookies.has_key('cart_shop'):
        carts = eval(request.cookies['cart_shop'].value)
        from plugin_cms import CmsModel
        from plugin_cms import CmsFolder
        db = cms.db
        cms.define_table('product')
        table.append(TR(TH('Sản phẩm', _class='cart_name'), TH('Số lượng', _class='cart_number'), TH(B('Thành tiền'), _class='cart_price_all')))
    for cart in carts:
        cart = eval(cart)
        if int(cart['num']) > 0:
            row = db((db.product.id == cart['id'])).select().first()
            i = 1
            if row:
                if row.price:
                    tong_tien += int(row.price) * int(cart['num'])
                input_num = cart['num']
                rowname = DIV(DIV(cms.get_images_content('product', row.avatar), _class='col-lg-2'), DIV(A(row.name, _href=cms.url_content(row, table='product')), _class='col-lg-10'), _class='produc_order')
                if row.price:
                    rowname = DIV(DIV(cms.get_images_content('product', row.avatar), _class='col-lg-2'), DIV(A(row.name, _href=cms.url_content(row, table='product')), P(number_format(row.price), ' VNĐ', _class='thanh_toan_price'), P(row.supplier.name, _class='thanh_toan_supplier'), _class='col-lg-10'), _class='produc_order')
                    if row.price_old:
                        rowname = DIV(DIV(cms.get_images_content('product', row.avatar), _class='col-lg-2'), DIV(A(row.name, _href=cms.url_content(row, table='product')), P(number_format(row.price), ' VNĐ', SPAN(number_format(row.price_old), ' VNĐ', _class='thanh_toan_price_old'), _class='thanh_toan_price'), _class='col-lg-10 '), _class='produc_order')
                        table.append(TR(TD(rowname), TD(input_num), TD(B(number_format(int(row.price) * int(cart['num'])), ' VNĐ'), _class='integer')))
                    else:
                        table.append(TR(TD(rowname), TD(input_num), TD(B(number_format(int(row.price) * int(cart['num'])), ' VNĐ'), _class='integer')))
                else:

                    table.append(TR(TD(rowname), TD(input_num), TD('')))
    div.append(table)
    p_tong = DIV(SPAN('Tổng tiền: '))
    p_tong.append(str(number_format(tong_tien)) + ' VNĐ')
    div.append(B(p_tong, _class='text-right'))

    return div


def api_view_thanh_toan():
    import requests
    div = DIV(_id="order_view")
    num_car = 0
    tong_tien = 0
    carts = ''
    from plugin_app import number_format
    table = TABLE(_class='table')
    if request.cookies.has_key('cart_shop'):
        carts = eval(request.cookies['cart_shop'].value)
        table.append(TR(TH('Sản phẩm', _class='cart_name'), TH('Số lượng', _class='cart_number'), TH(B('Thành tiền'), _class='cart_price_all')))
    for cart in carts:
        cart = eval(cart)
        if int(cart['num']) > 0:
            url_produc = '%s/api/v1/product/%s.json' % (api_naso, cart['id'])
            r1 = requests.get(url_produc).json()
            r_produc = r1['result'][0]
            i = 1
            if r_produc:
                if r_produc['parent'] != None:
                    url_p = '%s/api/v1/product/%s.json' % (api_naso, r_produc['parent'])
                    rp = requests.get(url_p).json()
                    rps = rp['result'][0]

                    link_p = URL(f='san-pham', args=[r_produc['link_url']])
                    if r_produc['price'] != "":
                        tong_tien += int(r_produc['price']) * int(cart['num'])
                    input_num = cart['num']

                    if r_produc['price'] != "":
                        rowname = DIV(DIV(IMG(_src="%s/static/uploads/product/%s" % (link_naso, rps['image'])), _class='col-lg-3'), DIV(A(rps['name'], ' (', r_produc['name'], ')', _href=link_p), P(number_format(r_produc['price']), ' VNĐ', _class='thanh_toan_price'), _class='col-lg-9'), _class='produc_order')
                        table.append(TR(TD(rowname), TD(input_num), TD(B(number_format(int(r_produc['price']) * int(cart['num'])), ' VNĐ'), _class='integer')))
                    else:
                        rowname = DIV(DIV(IMG(_src="%s/static/uploads/product/%s" % (link_naso, rps['image'])), _class='col-lg-3'), DIV(A(rps['name'], ' (', r_produc['name'], ')', _href=link_p), _class='col-lg-9'), _class='produc_order')
                        table.append(TR(TD(rowname), TD(input_num), TD('')))
                else:
                    link_p = URL(f='san-pham', args=[r_produc['link_url']])
                    if r_produc['price'] != "":
                        tong_tien += int(r_produc['price']) * int(cart['num'])
                    input_num = cart['num']

                    if r_produc['price'] != "":
                        rowname = DIV(DIV(IMG(_src="%s/static/uploads/product/%s" % (link_naso, r_produc['image'])), _class='col-lg-3'), DIV(A(r_produc['name'], _href=link_p), P(number_format(r_produc['price']), ' VNĐ', _class='thanh_toan_price'), _class='col-lg-9'), _class='produc_order')
                        table.append(TR(TD(rowname), TD(input_num), TD(B(number_format(int(r_produc['price']) * int(cart['num'])), ' VNĐ'), _class='integer')))
                    else:
                        rowname = DIV(DIV(IMG(_src="%s/static/uploads/product/%s" % (link_naso, r_produc['image'])), _class='col-lg-3'), DIV(A(r_produc['name'], _href=link_p), _class='col-lg-9'), _class='produc_order')
                        table.append(TR(TD(rowname), TD(input_num), TD('')))
    div.append(table)
    p_tong = DIV(SPAN('Tổng tiền: '))
    p_tong.append(str(number_format(tong_tien)) + ' VNĐ')
    div.append(B(p_tong, _class='text-right'))

    return div


def view_gio_hang():
    import requests
    import json

    num_car = 0
    tong_tien = 0
    carts = ''
    div_wr = DIV(_id='receipt')
    
    if request.cookies.has_key('cart_shop'):

        ### Giỏ hàng
        url_produc = '%s/api/cart.json?data=%s' % (api_naso, request.cookies['cart_shop'].value)
        r1 = requests.post(url_produc).text
        r1 = json.loads(r1)
        
        url_page_view = '%s/api/salesman_web_tracking.json'%(api_naso)
        page_view = {'salesman_web':request.vars.web_id,'tablename': 'cart' ,'table_id': r1['result'] } 
        requests.post(url_page_view, json=page_view)

        divCart = DIV(_class='table titleALL')

        # Tiêu đề giỏ hàng
        divTitle = DIV(_class='titleCart')
        divTitle.append(DIV(LABEL('Tất cả (' + str(r1['count']) + ' đơn hàng)', INPUT(_type='checkbox', _onclick='toggle(this)', _class='foo'), SPAN(_class='checkmark'), _class='checkboxCss'), _class='pd-l-10', _id='areaTest', _style='width: 50%;'))
        divTitle.append(DIV('Đơn giá', _class='productPrice not_padding'))
        divTitle.append(DIV('Số lượng', _class='productQty'))
        divTitle.append(DIV('Tổng tiền', _class='totalMoney not_padding'))
        divTitle.append(DIV('Xóa', _class='titleTrash'))
        divCart.append(divTitle)
        divCart.append(DIV(_class='col-xs-12', _style='height:10px'))

        # Chi tiết giỏ hàng
        divCartRowTotal = DIV(_class='col-lg-12 not_padding')
        don = 1
        lstWarehouse = []
        count = 1
        total_price_all = 0

        for whs in r1['result']:
            divCartRow = DIV(_class='col-lg-12 cartRow')
            divCartRow.append(DIV(LABEL(IMG(_src='https://banhang.bahadi.vn/app/static/uploads/cart/shop.png', _class='iconShop'), SPAN(whs['name'], ' - ', whs['address'], ' ', whs['ward_name'], _class='titleShop'), INPUT(_class='foo', _name='selectWarehouse', _id='selectWarehouse_' + str(whs['id']), _type='checkbox', _value=whs['id'], _checked=True if len(r1['result']) == 1 else False), SPAN(_class='checkmark'), _class='checkboxCss', _style='font-size: 15px;line-height: 20px;'), _class='pd-l-10'))
            tong_tien = 0
            i = 0
            list_product = []
            countProduct = 0
            divProduct = DIV(_class='cartProduct')
            for prd in whs['list_product']:
                div_prd = DIV(_class="row rowCart rowCart" + str(whs['id']), _id='divCart' + str(prd['id']))
                # Tên sản phẩm
                div_prd.append(DIV(A(prd['name'], _href=URL(c='san-pham', f=str(prd['link_url']))), _class='productName'))
                # Đơn giá
                div_prd.append(DIV(SPAN('{:,}'.format(prd['price']), _id='price' + str(count)), _class='productPrice not_padding'))
                # Số lượng
                divQty = DIV(_class='productQty')
                urlQuantity = URL(c='plugin_app', f='add_quantity_product_to_cart', vars=dict(pid=prd['id'], count=count))
                ajaxQuantityDown = "btnQuantityDown('%s', '%s');ajax('%s', ['%s'], '_blank') " % (count, whs['id'], urlQuantity, 'fqty' + str(count))
                ajaxQuantityUp = "btnQuantityUp('%s', 100, '%s');ajax('%s', ['%s'], '_blank')" % (count, whs['id'], urlQuantity, 'fqty' + str(count))
                divQty.append(DIV(SPAN(_class='fa fa-minus'), _id='btnQuantityDown', _class='qty decrease', _onclick=ajaxQuantityDown))
                divQty.append(DIV(INPUT(_type='text', _class='inpQuantity', _name='fqty' + str(count), _id='fqty' + str(count), _value=prd['num'] if prd and prd['num'] > 0 else 1, _onkeypress='validate(event)', _onkeyup='javascript:this.value=CommaAndValidateMaxQty(this.value, ' + str(count) + ');', _oninput='handlingSum(%s,%s)' % (count, whs['id']), _maxlength='3'), _id='divQty' + str(count), _class='fieldOuter'))
                divQty.append(DIV(SPAN(_class='fa fa-plus'), _id='btnQuantityUp', _class='qty increase', _onclick=ajaxQuantityUp))
                div_prd.append(divQty)
                # Tổng tiền
                div_prd.append(DIV(SPAN('{:,}'.format(prd['sum_price']), _id='totalMoney' + str(count)), _class='totalMoney not_padding'))
                # Xóa
                div_prd.append(DIV(SPAN(SPAN(_class='fa fa-trash-o')), _class='iconTrash btn_delete_cart', _id=str(prd['id']) + '_' + str(whs['id'])))
                ajaxDeleteCart = "ajax('%s', [], '_blank')" % (URL(c='plugin_app', f='delete_product_to_cart', vars=dict(pid=prd['id'])))
                div_prd.append(DIV(_style='display:none', _onclick=ajaxDeleteCart, _id='deleteProductToCartHid' + str(prd['id'])))
                list_product.append([prd['id'], int(prd['num'])])
                tong_tien += int(prd['sum_price'])
                total_price_all += int(prd['sum_price'])
                divProduct.append(div_prd)
                divProduct.append(DIV(_style='border-bottom: 1px dotted #eee;margin-bottom: 10px;', _id='borderdivCart' + str(prd['id'])))
                i += int(prd['num'])
                count += 1
                countProduct += 1
            # Tổng tiền
            divLeft = DIV(_class='col-lg-8 not_padding')
            divLeft.append(DIV(TEXTAREA(_name='note_%s' % (whs['id']), _placeholder='Ghi chú', _style='height: 70px;', _cols='30'), _class='col-lg-5 not_padding'))
            divLeft.append(DIV(DIV(_id='text_van_chuyen_%s' % whs['id']), INPUT(_value=str(list_product), _name='list_product_%s' % whs['id'], _style='display:none;'), _class='col-lg-7 not_padding'))

            divRight = DIV(_class='col-lg-4 not_padding')
            divRight.append(DIV(DIV(LABEL('Tổng tiền (', countProduct, ' sp) : ', _id='labelTotalAmount' + str(whs['id'])), INPUT(_type='hidden', _value=countProduct, _id='totalAmountHid' + str(whs['id'])), SPAN(' ₫', _class='totalAmount'), SPAN('{:,}'.format(tong_tien), _id='totalAmount' + str(whs['id']), _class='totalAmount totalAmountOrder')), _class='', _style='text-align: right'))

            divProduct.append(DIV(divLeft, divRight, _class='col-lg-12 not_padding'))
            divProduct.append(INPUT(_type='hidden', _value='', _name='transportHidden_%s' % (whs['id']), _id='transportHidden_%s' % (whs['id'])))
            divProduct.append(INPUT(_type='hidden', _value='', _name='van_chuyen_%s' % (whs['id']), _id='van_chuyen_%s' % (whs['id'])))
            divProduct.append(INPUT(_type='hidden', _value=tong_tien, _id='temporaryPriceOrder_' + str(whs['id']), _name='temporaryPriceOrder_' + str(whs['id'])))

            divCartRow.append(DIV(divProduct, _class='rowCartProduct'))

            divCartOrder = DIV(divCartRow, DIV(_class='col-xs-12', _style='height:10px'), _class='col-lg-12 not_padding cart_warehouse_' + str(whs['id']))
            divCartRowTotal.append(divCartOrder)

            don += 1
            lstWarehouse.append(whs['id'])

        divCart.append(divCartRowTotal)
        divleft = DIV(divCart, _class='col-lg-9', _style='padding-left: 0;')

        ### Thông tin khách hàng
        # Tiêu đề
        divForm = DIV(_class='table', _style='padding-top: 20px;')
        divForm.append(DIV(_id='form_thong_tin_khach'))

        divFormInforCus = DIV(_class='cartRow')
        divFormInforCus.append(DIV(I(_class='fa fa-map-marker', _style='margin-right:7px;'), ' Thông tin khách hàng', _class='title_form', _style='justify-content: flex-start; padding-left: 10px;'))

        # Người nhận hàng
        inpName = INPUT(_type='text', _class="form-control", _name='name', _placeholder='Người nhận hàng', _required=True)
        divName = DIV(inpName, _class='form-group-cart')
        # Số điện thoại
        inpPhone = INPUT(_type='text', _class="form-control", _name='dien_thoai', _id='dien_thoai', _placeholder='Số điện thoại')
        divPhone = DIV(inpPhone, _class='form-group-cart')
        # Địa chỉ nhận hàng
        inpAddress = INPUT(_type='text', _class="form-control", _name='dia_chi', _placeholder='Địa chỉ nhận hàng', _style='width: 100%;')
        divAddress = DIV(inpAddress, _class='form-group-cart')
        # Tỉnh
        selCity = SELECT(OPTION('Chọn tỉnh thành', _value=''), _id="city", _name='city', _class='form-control')
        divCity = DIV(selCity, _class='form-group-cart')
        # Thành phố, huyện
        selDistrict = SELECT(OPTION('Chọn huyện thị', _value=''), _id='district', _name='district', _class='form-control')
        divDistrict = DIV(selDistrict, _class='form-group-cart')
        # Phường, xã
        selWard = SELECT(OPTION('Chọn phường xã', _value=""), _id="ward", _name='ward', _class='form-control')
        divWard = DIV(selWard, _class='form-group-cart', _style='padding-bottom: 10px;')

        divFormInforCus.append(DIV(divName, divPhone, divAddress, divCity, divDistrict, divWard))
        divForm.append(divFormInforCus)

        wr_check = ''
        for whs in r1['result']:
            wr_check += "ajax('%s', ['city','district','ward','dia_chi','temporaryPriceOrder_%s','list_product_%s'], 'text_van_chuyen_%s');" % (URL(c='plugin_app', f='check_van_chuyen', args=[whs['id']]), whs['id'], whs['id'], whs['id'])

        nobita_loca = "https://locations.ecrm.vn/api/locations"

        script = SCRIPT("""
            var city = document.getElementById("city");
            var district = document.getElementById("district");
            var ward = document.getElementById("ward");
            c_city = getCookie("city")
            c_district = getCookie("district")
            c_ward = getCookie("ward")

            var url_link = "%s";
            var Parameter = {
                 url: url_link + "?country=VN",
                 method: "GET",
                 headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
            };

            var promise = axios(Parameter);
            promise.then(function (result) {
              renderCity(result.data);
            });
            if (c_city!=null) {
                var p_dis = {
                    url: url_link +  "?country=VN&parentId="+c_city,
                    method: "GET",
                };
                var promise_dis = axios(p_dis);
                promise_dis.then(function (result) {
                    renderDis(result.data);
                });
            }

            if (c_district!=null) {
                var p_ward = {
                    url: url_link + "?country=VN&parentId="+c_district,
                    method: "GET",
                    headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
                };
                    var promise_ward = axios(p_ward);
                    promise_ward.then(function (result) {
                    renderWard(result.data);
                });
            }
            if (c_ward!=null) {
                $(document).ready(function () {
                %s
                });

            }

            function renderCity(data) {

              for (const x of data) {

                if (x.id==c_city) {
                    city.options[city.options.length] = new Option(x.name, x.id, false, true);
                }
                else {
                    city.options[city.options.length] = new Option(x.name, x.id);
                }
              }
              city.onchange = function () {
                document.cookie = "city="+city.value;
                district.length = 1;
                ward.length = 1;
                var p_dis = {
                  url: url_link +"?country=VN&parentId=" + city.value,
                  method: "GET",
                headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},

                };
                var promise_dis = axios(p_dis);
                promise_dis.then(function (result) {
                  renderDis(result.data);
                });
              }
            }

            function renderDis(data) {
                for (const x of data) {
                    if (x.id==c_district) {
                        district.options[district.options.length] = new Option(x.name, x.id, false, true);
                        }
                    else{
                        district.options[district.options.length] = new Option(x.name, x.id)
                        }
                }
               district.onchange = function () {
                    document.cookie = "district="+district.value;
                    ward.length = 1;
                    var p_ward = {
                    url: url_link +"?country=VN&parentId=" + district.value,
                    method: "GET",
                    headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
                };
                var promise_ward = axios(p_ward);
                 promise_ward.then(function (result) {
                  renderWard(result.data);
                });
              }
            }
            function renderWard(data) {
                for (const x of data) {
                    if (x.id==c_ward) {
                        ward.options[ward.options.length] = new Option(x.name, x.id, false, true);
                    }
                    else{
                        ward.options[ward.options.length] = new Option(x.name, x.id);
                    }
                }
                ward.onchange = function () {
                    document.cookie = "ward="+ward.value;
                    %s
                }
            }

        // Tính tổng
        function handlingTotal(id) {
            totalPrice = Number($("#tien_hang_"+id).text().replace(/[.,\s]/g, ''))
            total_vc = Number($("#van_chuyen_"+id).text().replace(/[.,\s]/g, ''))
            $("#tong_tien_"+id).text((totalPrice + total_vc).toLocaleString(""));
        }

        function getCookie(name) {

            // Split cookie string and get all individual name=value pairs in an array
            var cookieArr = document.cookie.split(";");

            // Loop through the array elements
            for(var i = 0; i < cookieArr.length; i++) {
                var cookiePair = cookieArr[i].split("=");

                /* Removing whitespace at the beginning of the cookie name
                and compare it with the given string */
                if(name == cookiePair[0].trim()) {
                    // Decode the cookie value and return
                    return decodeURIComponent(cookiePair[1]);
                }
            }

            // Return null if not found
            return null;
        }

        """ % (nobita_loca, wr_check, wr_check))
        divForm.append(script)

        # Tổng tiền
        divForm.append(DIV(_class='row', _style='height:10px'))
        divAmount = DIV(_class='col-lg-12 cartRow')

        divAmount.append(DIV(SPAN('Tạm tính', _style='font-size:13px'), DIV(B('₫'), B(0, _id='temporaryPrice'), _class='cusPay'), _class='temporaryPrice'))
        divAmount.append(DIV(SPAN('Vận chuyển', _style='font-size:13px'), DIV(B('₫'), B(0, _id='transport'), _class='cusPay'), _class='temporaryPrice'))
        divAmount.append(DIV(_style='border: 1px solid rgb(244, 244, 244);'))
        divAmount.append(DIV(SPAN('Tổng tiền', _style='font-size:13px'), DIV(B('₫'), B(0, _id='totalAmountTemp'), _class='cusPay'), _class='temporaryPrice'))
        divForm.append(divAmount)

        ### Button ĐẶT HÀNG
        warehouse = json.dumps(r1['result'])

        # Vận chuyển
        lstParam = ['name', 'dia_chi', 'dien_thoai', 'description', 'city', 'district', 'ward', 'selectWarehouse']
        for wh in lstWarehouse:
            lstParam.append('transportHidden_%s' % (wh))
            lstParam.append('note_%s' % (wh))

        ajax = "ajax('%s', %s, 'receipt')" % (URL(f='api_act_add_cart', vars=dict(warehouse=warehouse,web_id=request.vars.web_id)), lstParam)
        divOrderNow = DIV(A('ĐẶT HÀNG NGAY', _class='btn btn-success', _id='order_check'), _class='row', _style='text-align: right')
        divOrderNow.append(DIV(_id='order_submit', _style='display:none', _onclick=ajax))
        script = SCRIPT("""$('#order_check').click(function(){
                                var flagValidate = true;
                                if ($('#countProduct').val() == '' || parseInt($('#countProduct').val()) <= 0){
                                    $('h4#myModalLabel').text('Giỏ hàng của bạn đang trống. Vui lòng thêm sản phẩm');
                                    flagValidate = false;
                                    document.getElementById('id01').style.display='block'
                                } else if ($('#dien_thoai').val() == ''){
                                    $('#dien_thoai').css('border-color', '#ff0000');
                                    $('h4#myModalLabel').text('Vui lòng nhập số điện thoại khách hàng');
                                    flagValidate = false;
                                    document.getElementById('id01').style.display='block'
                                } else if (!$('input[name="selectWarehouse"]:checked').length) {
                                    $('h4#myModalLabel').text('Bạn vẫn chưa chọn sản phẩm nào để mua');
                                    flagValidate = false;
                                    document.getElementById('id01').style.display='block'
                                } else if (!$('#ward').val()) {
                                    $('h4#myModalLabel').text('Vui lòng chọn địa chỉ giao hàng');
                                    $('#city').css('border-color', '#ff0000');
                                    $('#district').css('border-color', '#ff0000');
                                    $('#ward').css('border-color', '#ff0000');
                                    flagValidate = false;
                                    document.getElementById('id01').style.display='block'
                                }
                                if (flagValidate) {
                                    $('#order_submit').click();
                                };
                            });
                            """)
        divOrderNow.append(script)

        divRight = DIV(DIV(FORM(divForm), _class='row'), DIV(_class='row', _style='height:10px'), divOrderNow, _class='col-lg-3', _style='padding-right: 0;')

        div_wr.append(divleft)
        div_wr.append(divRight)

        div_wr.append(INPUT(_type='hidden', _value=count - 1, _id='countProduct'))
    else:
        div_wr.append(H3("Giỏ hàng chưa có sản phẩm",_class='text-center'))
    return div_wr


# def view_gio_hang():
#     num_car = 0
#     tong_tien = 0
#     carts = ''
#     import requests
#     import json
#     div_wr = DIV(_id='receipt')
#
#     if request.cookies.has_key('cart_shop'):
#         div = DIV(_class='row')
#         url_produc = '%s/api/cart.json?data=%s' % (api_naso, request.cookies['cart_shop'].value)
#         r1 = requests.post(url_produc).text
#         r1 = json.loads(r1)
#         divCart = DIV(_class='table titleALL')
#
#         # # Test
#         # div.append(r1)
#         divTitle = DIV(_class='titleCart')
#
#         divTitle.append(DIV(LABEL('Tất cả (' + str(r1['count']) + ' đơn hàng)', INPUT(_type='checkbox', _onclick='toggle(this)'), SPAN(_class='checkmark'), _class='checkboxCss'), _class='pd-l-10', _id='areaTest', _style='width: 50%;'))
#         divTitle.append(DIV('Đơn giá', _class='productPrice not_padding'))
#         divTitle.append(DIV('Số lượng', _class='productQty'))
#         divTitle.append(DIV('Tổng tiền', _class='totalMoney not_padding'))
#         divTitle.append(DIV('Xóa', _class='titleTrash'))
#
#         divCart.append(DIV(divTitle))
#         divCart.append(DIV(_class='col-xs-12', _style='height:10px'))
#
#         # divCartRowTotal = DIV(_class='col-lg-12 cartRowTotal not_padding')
#         divCartRowTotal = DIV(_class='col-lg-12 not_padding')
#         don = 1
#         lstWarehouse = []
#         count = 1
#
#         for whs in r1['result']:
#             divCartRow = DIV(_class='col-xs-12 cartRow')
#             divCartRow.append(DIV(LABEL(IMG(_src='https://banhang.bahadi.vn/app/static/uploads/cart/shop.png', _class='iconShop'), SPAN(whs['name'], ' - ', whs['address'], ' ', whs['ward_name'], _class='titleShop'), INPUT(_class='foo', _name='selectWarehouse', _type='checkbox', _value=whs['id']), SPAN(_class='checkmark'), _class='checkboxCss', _style='font-size: 15px;line-height: 20px;'), _class='pd-l-10'))
#             tong_tien = 0
#             i = 0
#             list_product = []
#
#             countProduct = 0
#
#             divProduct = DIV(_class='cartProduct')
#             for prd in whs['list_product']:
#                 div_prd = DIV(_class="row rowCart rowCart" + str(whs['id']), _id='divCart' + str(prd['id']))
#
#                 # Tên sản phẩm
#                 div_prd.append(DIV(A(prd['name'], _href=URL(c='san-pham', f=str(prd['link_url']))), _class='productName'))
#                 # Đơn giá
#                 div_prd.append(DIV(SPAN('{:,}'.format(prd['price']), _id='price' + str(count)), _class='productPrice not_padding'))
#                 # Số lượng
#                 divQty = DIV(_class='productQty')
#
#                 urlQuantity = URL(c='plugin_app', f='add_quantity_product_to_cart', vars=dict(pid=prd['id'], count=count))
#                 ajaxQuantityDown = "btnQuantityDown('%s', '%s');ajax('%s', ['%s'], '_blank')" % (count, whs['id'], urlQuantity, 'fqty' + str(count))
#                 ajaxQuantityUp = "btnQuantityUp('%s', 100, '%s');ajax('%s', ['%s'], '_blank')" % (count, whs['id'], urlQuantity, 'fqty' + str(count))
#
#                 divQty.append(DIV(SPAN(_class='fa fa-minus'), _id='btnQuantityDown', _class='qty decrease', _onclick=ajaxQuantityDown))
#                 divQty.append(DIV(INPUT(_type='text', _class='inpQuantity', _name='fqty' + str(count), _id='fqty' + str(count), _value=prd['num'] if prd and prd['num'] > 0 else 1, _onkeypress='validate(event)', _onkeyup='javascript:this.value=CommaAndValidateMaxQty(this.value, ' + str(count) + ');', _oninput='handlingSum(%s,%s)' % (count, whs['id']), _maxlength='3'), _id='divQty' + str(count), _class='fieldOuter'))
#                 divQty.append(DIV(SPAN(_class='fa fa-plus'), _id='btnQuantityUp', _class='qty increase', _onclick=ajaxQuantityUp))
#                 div_prd.append(divQty)
#                 # Tổng tiền
#                 div_prd.append(DIV(SPAN('{:,}'.format(prd['sum_price']), _id='totalMoney' + str(count)), _class='totalMoney not_padding'))
#                 # Xóa
#                 div_prd.append(DIV(SPAN(SPAN(_class='fa fa-trash-o')), _class='iconTrash btn_delete_cart', _id=str(prd['id']) + '_' + str(whs['id'])))
#                 ajaxDeleteCart = "ajax('%s', [], '_blank')" % (URL(c='plugin_app', f='delete_product_to_cart', vars=dict(pid=prd['id'])))
#                 div_prd.append(DIV(_style='display:none', _onclick=ajaxDeleteCart, _id='deleteProductToCartHid' + str(prd['id'])))
#
#                 list_product.append([prd['id'], int(prd['num'])])
#                 tong_tien += int(prd['sum_price'])
#                 divProduct.append(div_prd)
#                 divProduct.append(DIV(_style='border-bottom: 1px dotted #eee;margin-bottom: 10px;', _id='borderdivCart' + str(prd['id'])))
#                 i += int(prd['num'])
#
#                 count += 1
#                 countProduct += 1
#
#             # Tổng tiền
#             divProduct.append(DIV(DIV(LABEL('Tổng số tiền (', countProduct, ' sản phẩm) : ', _id='labelTotalAmount' + str(whs['id'])), INPUT(_type='hidden', _value=countProduct, _id='totalAmountHid' + str(whs['id'])), SPAN(' ₫', _class='totalAmount'), SPAN('{:,}'.format(tong_tien), _id='totalAmount' + str(whs['id']), _class='totalAmount')), _class='col-lg-12', _style='text-align:right;padding-right: inherit;position: inherit'))
#
#             # wr_tong = TABLE(_class='table borderless')
#             # wr_tong.append(TR(TD("Phí vận chuyển:"), TD(SPAN(0, _id='van_chuyen_%s' % (whs['id'])), ' vnđ', _style='width:160px; text-align:right;')))
#             # wr_tong.append(TR(TD("Tiền hàng:"), TD(SPAN('%s' % number_format(tong_tien), _id='tien_hang_%s' % (whs['id'])), ' vnđ', _style='width:160px; text-align:right;')))
#             # wr_tong.append(TR(TD(B("TỔNG TIỀN:")), TD(B(SPAN('%s' % number_format(tong_tien), _id='tong_tien_%s' % (whs['id'])), ' vnđ'), _style='width:160px; text-align:right;')))
#             #
#             # divCartRow.append(DIV(DIV(TEXTAREA(_name='note_%s' % (whs['id']), _style="width: 100%;height: 80px;", _placeholder="Lưu ý cho người bán"), _class='col-lg-4'), DIV(DIV(_id='text_van_chuyen_%s' % whs['id']), INPUT(_value=str(list_product), _name='list_product_%s' % whs['id'], _style='display:none;'), _class='col-lg-4'), DIV(wr_tong, _class="col-lg-4", _style="text-align:right;padding-right: inherit;position: inherit"), _class="col-lg-12 wr_van_chuyen",
#             #     _style="border-top: 1px dotted #dadada;padding-top: 14px;"))
#
#             divCartRow.append(DIV(divProduct, _class='rowCartProduct'))
#
#             divCartRow.append(INPUT(_type='hidden', _value='', _name='transportHidden_%s' % (whs['id']), _id='transportHidden_%s' % (whs['id'])))
#             divCartRowTotal.append(divCartRow)
#             divCartRowTotal.append(DIV(_class='col-xs-12', _style='height:10px'))
#             don += 1
#             lstWarehouse.append(whs['id'])
#
#         divCart.append(divCartRowTotal)
#         div.append(divCart)
#         #####################
#
#         form = FORM()
#         form.append(H4(I(_class='fa fa-map-marker', _style='margin-right:7px;'), '  Thông tin khách hàng', _class='title_form'))
#         div1 = DIV(_class="form-group col-md-4")
#         div1.append(INPUT(_type='text', _class="form-control", _name='name', _placeholder="Người đặt hàng", _required=True))
#
#         div2 = DIV(_class="form-group col-md-4")
#         div2.append(INPUT(_type='text', _class="form-control", _name='dien_thoai', _placeholder="Số điện thoại"))
#         # địa chỉ
#         div3 = DIV(_class="form-group col-md-4")
#         div3.append(INPUT(_type='text', _class="form-control", _name='dia_chi', _placeholder="Địa chỉ nhận hàng", _style="width: 100%; "))
#         form.append(DIV(div1, div2, div3, _class='col-md-12'))
#
#         # Thành phố
#         div1 = DIV(_class="form-group col-md-4")
#         div1.append(SELECT(OPTION('Chọn tỉnh thành', _value=""), _id="city", _name='city', _class='form-control'))
#         # huyện
#         div2 = DIV(_class="form-group col-md-4")
#         div2.append(SELECT(OPTION('Chọn huyện thị', _value=""), _id="district", _name='district', _class='form-control'))
#
#         # Xã
#         div3 = DIV(_class="form-group col-md-4")
#         div3.append(SELECT(OPTION('Chọn phường xã', _value=""), _id="ward", _name='ward', _class='form-control'))
#         form.append(DIV(div1, div2, div3, _class='col-md-12'))
#         wr_check = ''
#         for whs in r1['result']:
#             wr_check += "ajax('%s', ['city','district','ward','dia_chi','list_product_%s'], 'text_van_chuyen_%s');" % (URL(c='plugin_app', f='check_van_chuyen', args=[whs['id']]), whs['id'], whs['id'])
#
#         nobita_loca = "https://locations.ecrm.vn/api/locations"
#
#         script = SCRIPT("""
#             var city = document.getElementById("city");
#             var district = document.getElementById("district");
#             var ward = document.getElementById("ward");
#             c_city = getCookie("city")
#             c_district = getCookie("district")
#             c_ward = getCookie("ward")
#
#             var url_link = "%s";
#             var Parameter = {
#                  url: url_link + "?country=VN",
#                  method: "GET",
#                  headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
#             };
#
#             var promise = axios(Parameter);
#             promise.then(function (result) {
#               renderCity(result.data);
#             });
#             if (c_city!=null) {
#                 var p_dis = {
#                     url: url_link +  "?country=VN&parentId="+c_city,
#                     method: "GET",
#                 };
#                 var promise_dis = axios(p_dis);
#                 promise_dis.then(function (result) {
#                     renderDis(result.data);
#                 });
#             }
#
#             if (c_district!=null) {
#                 var p_ward = {
#                     url: url_link + "?country=VN&parentId="+c_district,
#                     method: "GET",
#                     headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
#                 };
#                     var promise_ward = axios(p_ward);
#                     promise_ward.then(function (result) {
#                     renderWard(result.data);
#                 });
#             }
#             if (c_ward!=null) {
#                 $(document).ready(function () {
#                 %s
#                 });
#
#             }
#
#             function renderCity(data) {
#
#               for (const x of data) {
#
#                 if (x.id==c_city) {
#                     city.options[city.options.length] = new Option(x.name, x.id, false, true);
#                 }
#                 else {
#                     city.options[city.options.length] = new Option(x.name, x.id);
#                 }
#               }
#               city.onchange = function () {
#                 document.cookie = "city="+city.value;
#                 district.length = 1;
#                 ward.length = 1;
#                 var p_dis = {
#                   url: url_link +"?country=VN&parentId=" + city.value,
#                   method: "GET",
#                 headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
#
#                 };
#                 var promise_dis = axios(p_dis);
#                 promise_dis.then(function (result) {
#                   renderDis(result.data);
#                 });
#               }
#             }
#
#             function renderDis(data) {
#                 for (const x of data) {
#                     if (x.id==c_district) {
#                         district.options[district.options.length] = new Option(x.name, x.id, false, true);
#                         }
#                     else{
#                         district.options[district.options.length] = new Option(x.name, x.id)
#                         }
#                 }
#                district.onchange = function () {
#                     document.cookie = "district="+district.value;
#                     ward.length = 1;
#                     var p_ward = {
#                     url: url_link +"?country=VN&parentId=" + district.value,
#                     method: "GET",
#                     headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
#                 };
#                 var promise_ward = axios(p_ward);
#                  promise_ward.then(function (result) {
#                   renderWard(result.data);
#                 });
#               }
#             }
#             function renderWard(data) {
#                 for (const x of data) {
#                     if (x.id==c_ward) {
#                         ward.options[ward.options.length] = new Option(x.name, x.id, false, true);
#                     }
#                     else{
#                         ward.options[ward.options.length] = new Option(x.name, x.id);
#                     }
#                 }
#                 ward.onchange = function () {
#                     document.cookie = "ward="+ward.value;
#                     %s
#                 }
#             }
#
#         // Tính tổng
#         function handlingTotal(id) {
#             totalPrice = Number($("#tien_hang_"+id).text().replace(/[.,\s]/g, ''))
#             total_vc = Number($("#van_chuyen_"+id).text().replace(/[.,\s]/g, ''))
#             $("#tong_tien_"+id).text((totalPrice + total_vc).toLocaleString(""));
#         }
#
#
#         function getCookie(name) {
#
#             // Split cookie string and get all individual name=value pairs in an array
#             var cookieArr = document.cookie.split(";");
#
#             // Loop through the array elements
#             for(var i = 0; i < cookieArr.length; i++) {
#                 var cookiePair = cookieArr[i].split("=");
#
#                 /* Removing whitespace at the beginning of the cookie name
#                 and compare it with the given string */
#                 if(name == cookiePair[0].trim()) {
#                     // Decode the cookie value and return
#                     return decodeURIComponent(cookiePair[1]);
#                 }
#             }
#
#             // Return null if not found
#             return null;
#         }
#
#         """ % (nobita_loca, wr_check, wr_check))
#         form.append(script)
#
#         ##############################
#         div_wr.append(DIV(DIV(DIV(BR(), form, _id="form_thong_tin_khach"), _class='box_content row '), _class="col-lg-12 bg_white"))
#         warehouse = json.dumps(r1['result'])
#
#         # Vận chuyển
#         lstParam = ['name', 'dia_chi', 'dien_thoai', 'description', 'city', 'district', 'ward', 'selectWarehouse']
#         for wh in lstWarehouse:
#             lstParam.append('transportHidden_%s' % (wh))
#             lstParam.append('note_%s' % (wh))
#
#         ajax = "ajax('%s', %s, 'receipt')" % (URL(f='api_act_add_cart', vars=dict(warehouse=warehouse)), lstParam)
#         divOrderNow = DIV(A('ĐẶT HÀNG NGAY', _class='btn btn-success', _onclick=ajax), _class='col-lg-12 not_padding', _style='text-align: right;')
#         div_wr.append(DIV(div, _class='col-lg-12'))
#         div_wr.append(DIV(_class='col-lg-12', _style='height:20px'))
#         div_wr.append(divOrderNow)
#
#         div_wr.append(INPUT(_type='hidden', _value=count - 1, _id='countProduct'))
#
#     return div_wr


def api_form_thanh_toan():
    form = FORM()
    form.append(H4(I(_class='fa fa-map-marker', _style='margin-right:7px;'), '  Thông tin khách hàng', _class='title_form'))
    div1 = DIV(_class="form-group col-md-4")
    div1.append(INPUT(_type='text', _class="form-control", _name='name', _placeholder="Người đặt hàng", _required=True))

    div2 = DIV(_class="form-group col-md-4")
    div2.append(INPUT(_type='text', _class="form-control", _name='dien_thoai', _placeholder="Số điện thoại"))
    # địa chỉ
    div3 = DIV(_class="form-group col-md-4")
    div3.append(INPUT(_type='text', _class="form-control", _name='dia_chi', _placeholder="Địa chỉ nhận hàng", _style="width: 100%; "))
    form.append(DIV(div1, div2, div3, _class='col-md-12'))

    # Thành phố
    div1 = DIV(_class="form-group col-md-4")
    div1.append(SELECT(OPTION('Chọn tỉnh thành', _value=""), _id="city", _name='city', _class='form-control'))
    # huyện
    div2 = DIV(_class="form-group col-md-4")
    div2.append(SELECT(OPTION('Chọn huyện thị', _value=""), _id="district", _name='district', _class='form-control'))

    # Xã
    div3 = DIV(_class="form-group col-md-4")
    div3.append(SELECT(OPTION('Chọn phường xã', _value=""), _id="ward", _name='ward', _class='form-control'))
    form.append(DIV(div1, div2, div3, _class='col-md-12'))

    ajax_check = "ajax('%s', ['city','district','ward'], 'text_van_chuyen')" % (URL(c='plugin_app', f='check_van_chuyen', args=[1]))
    # ajax = "ajax('%s', ['name','dia_chi','dien_thoai','description'], 'form_thanh_toan')"%(URL(f='api_act_add_cart_new'))
    # # form.append(A(I(_class='icon-backward'),' Quay lại giỏ hàng',_href=URL(c='portal',f='folder',args=['checkout']), _class='pull-left'))
    # form.append(A(I(_class='fa fa-cart-arrow-down'),' ĐẶT HÀNG ',_onclick=ajax, _class='btn btn-success pull-right btn_naso'))

    nobita_loca = "https://locations.ecrm.vn/api/locations"

    script = SCRIPT("""
        var city = document.getElementById("city");
        var district = document.getElementById("district");
        var ward = document.getElementById("ward");
        var url_link = "%s";
        var Parameter = {
             url: url_link + "?country=VN",
             method: "GET",
             headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
        };

        var promise = axios(Parameter);
        promise.then(function (result) {
          renderCity(result.data);
        });
        function renderCity(data) {
          for (const x of data) {
            city.options[city.options.length] = new Option(x.name, x.id);
          }
          city.onchange = function () {
            district.length = 1;
            ward.length = 1;
            var p_dis = {
              url: url_link +"?country=VN&parentId=" + city.value,
              method: "GET",
            headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},

            };
            var promise_dis = axios(p_dis);
            promise_dis.then(function (result) {
              renderDis(result.data);
            });
          }
        }
        function renderDis(data) {
          for (const x of data) {
            district.options[district.options.length] = new Option(x.name, x.id);
          }
           district.onchange = function () {
                ward.length = 1;
            var p_ward = {
              url: url_link +"?country=VN&parentId=" + district.value,
              method: "GET",
              headers: { 'Access-Control-Allow-Origin': '*',  'Content-Type': 'application/json',},
            };
            var promise_ward = axios(p_ward);
             promise_ward.then(function (result) {
              renderWard(result.data);
            });
          }
        }
        function renderWard(data) {
            for (const x of data) {
                ward.options[ward.options.length] = new Option(x.name, x.id);
            }
            ward.onchange = function () {
                %s
            }
        }


    """ % (nobita_loca, ajax_check))
    form.append(script)
    return form


def api_act_add_cart():
    try:
        if request.vars.dien_thoai:
            if request.vars.warehouse:
                import requests
                import json

                phone = request.vars.dien_thoai
                name = request.vars.name
                address = request.vars.dia_chi
                description = request.vars.description
                city = request.vars.city
                district = request.vars.district
                ward = request.vars.ward
                warehouse = json.loads(request.vars.warehouse)
                selectWarehouse = request.vars.selectWarehouse

                if not isinstance(selectWarehouse, list):
                    selectWarehouse = [selectWarehouse]

                div = DIV(B('Đặt hàng thành công. Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất để xác nhận đơn hàng. Xin cảm ơn! '), _class='bg-info text-center')

                products = {}
                carts = eval(request.cookies['cart_shop'].value)
                for cart in carts:
                    cart = eval(cart)
                    if cart['kho_hang'] in selectWarehouse:
                        products[cart['id']] = cart['num']

                # Đại lý
                if request.cookies.has_key('umt_id'):
                    salesman_name_code = request.cookies['umt_id'].value
                else:
                    salesman_name_code = 100000010

                warehouses = []
                for wh in warehouse:

                    if str(wh['id']) in selectWarehouse:
                        # Vận chuyển
                        transport = request.vars['transportHidden_' + str(wh['id'])]
                        transportSplit = transport.split('|')
                        wh['transport_unit'] = transportSplit[0]
                        wh['transport_method'] = transportSplit[1]
                        wh['transport_fee'] = int(float(transportSplit[2]))

                        # Ghi chú
                        wh['notes'] = request.vars['note_' + str(wh['id'])]
                        warehouses.append(wh)

                data = {'salesman': salesman_name_code, 'name': name, 'phone': phone, 'address': address, 'description': description, 'city': city, 'district': district, 'ward': ward, 'warehouses': warehouses, 'products': products}
                url_order = '%s/api/order_add_from_web.json?data=%s' % (api_naso, data)
                r1 = requests.post(url_order).text
                r1 = json.loads(r1)
                
                url_page_view = '%s/api/salesman_web_tracking.json'%(api_naso)
                page_view = {'salesman_web':request.vars.web_id,'tablename': 'order' ,'table_id': r1['lstOrder'] } 
                requests.post(url_page_view, json=page_view)
                
                # div.append(DIV(r1['result'], _class='col-lg-12'))
                # div.append(DIV(r1['lstItem'], _class='col-lg-12'))
                div.append(DIV(BR(), 'Chuyển hướng về trang chủ sau 3 giây.', _class='bg-info text-center'))
                scr = '''
                 <META http-equiv="refresh" content="3;URL=%s">
                ''' % (URL(c='portal', f='folder', args=[page_home]))
                div.append(XML(scr))

                # Xóa cookie
                clear_cookie()

                return div
            else:
                div = DIV(B('Giỏ hàng chưa có sản phẩm. Vui lòng kiểm tra lại'), _class='bg-info text-center')
                div.append(DIV(BR(), 'Chuyển hướng về trang chủ sau 3 giây.', _class='bg-info text-center'))
                scr = '''
                 <META http-equiv="refresh" content="3;URL=%s">
                ''' % (URL(c='portal', f='folder', args=[page_home]))
                div.append(XML(scr))
                return div
        else:
            div = DIV(B('Đặt hàng lỗi, Bạn vui lòng nhập đầy đủ tên, số điện thoại, địa chỉ. Xin cảm ơn! '), _class='bg-info text-center')
            div.append(DIV(BR(), 'Trở lại form đặt hàng sau 1 giây.', _class='bg-info text-center'))
            scr = '''
             <META http-equiv="refresh" content="1;URL=%s">
            ''' % (URL(c='portal', f='folder', args=['thanh-toan']))
            div.append(XML(scr))
        return div
    # except Exception, e:
    #     return ('Lỗi : %s' % (e))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return ('Lỗi : %s, %s, %s' % (exc_type, exc_obj, exc_tb.tb_lineno))


def form_thanh_toan():
    form = FORM()
    form.append(H4('Thông tin người đặt hàng', _class='title_form'))
    div1 = DIV(_class="form-group col-md-6")
    div1.append(INPUT(_type='text', _class="form-control", _name='name', _placeholder="Người đặt hàng", _required=True))

    div2 = DIV(_class="form-group col-md-6")
    div2.append(INPUT(_type='text', _class="form-control", _name='dien_thoai', _placeholder="Số điện thoại"))
    form.append(DIV(div1, div2, _class='row'))

    form.append(DIV(DIV(DIV(INPUT(_type='checkbox', _onclick="check_show()", _id='check_show_nhanhang', _name='check'), _class='col-md-1 text-right'), SPAN('Người nhận hàng khác người đặt hàng', _class='col-md-11 title_form', _style="line-height: 50px;"), _class='col-md-12'), _class='row'))

    div1 = DIV(_class="form-group col-md-6")
    div1.append(INPUT(_type='text', _class="form-control", _name='name2', _id='name2', _placeholder="Người nhận hàng"))

    div2 = DIV(_class="form-group col-md-6")
    div2.append(INPUT(_type='text', _class="form-control", _name='dien_thoai2', _id='dien_thoai2', _placeholder="Số điện thoại"))
    form.append(DIV(div1, div2, _class='row hident', _id='nhan_hang'))

    div1 = DIV(_class="form-group", _style="width: 100%;  display: inline-block;")
    div1.append(H4('Địa chỉ nhận hàng', _class='title_form'))
    div1.append(INPUT(_type='text', _class="form-control", _name='dia_chi', _placeholder="Địa chỉ nhận hàng", _style="width: 100%; "))
    form.append(div1)

    div1 = DIV(_class="form-group")
    # div1.append(LABEL('Lời nhắn'))
    div1.append(TEXTAREA(_class="form-control", _rows="3", _name='description', _placeholder="Lời nhắn", _style="width: 100%; "))
    form.append(div1)

    ajax = "ajax('%s', ['name','dia_chi','dien_thoai','name2' ,'dien_thoai2','description'], 'form_thanh_toan')" % (URL(f='act_add_cart'))
    form.append(A(I(_class='icon-backward'), ' Quay lại giỏ hàng', _href=URL(c='portal', f='folder', args=['checkout']), _class='pull-left'))
    form.append(A(I(_class='fa fa-cart-arrow-down'), ' ĐẶT HÀNG ', _onclick=ajax, _class='btn btn-success pull-right btn_naso'))

    scr = '''
        <script>
            function check_show() {

                if ($('#check_show_nhanhang').is(":checked"))
                {
                    document.getElementById("nhan_hang").classList.add("show");
                }
                else
                {
                    $("#name2").val("");
                    $("#dien_thoai2").val("");
                    document.getElementById("nhan_hang").classList.remove("show");
                }
            }
        </script>
        '''
    form.append(XML(scr))
    return form


def act_add_cart():
    if request.vars.dien_thoai:
        cms.define_table('don_hang')
        cms.define_table('item_don_hang')
        import datetime
        don_hang_id = cms.db.don_hang.insert(folder=71, name=request.vars.name, dien_thoai=request.vars.dien_thoai, name2=request.vars.name2, dien_thoai2=request.vars.dien_thoai2, dia_chi=request.vars.dia_chi, description=request.vars.description, created_on=datetime.datetime.now())
        if don_hang_id:
            from plugin_process import ProcessModel
            process = ProcessModel()
            objects = process.define_objects(True)

            objects_id = objects.insert(folder=71, foldername='don-hang', tablename='don_hang', table_id=don_hang_id, auth_group=10, process=57)
            if request.cookies.has_key('cart_shop'):
                carts = eval(request.cookies['cart_shop'].value)
                for cart in carts:
                    cart = eval(cart)
                    row = db((db.product.id == cart['id'])).select().first()
                    if row:
                        item = cms.db.item_don_hang.insert(don_hang=don_hang_id, product=row.id, r_number=cart['num'], price=row.price)

        response.cookies['cart_shop'] = 'invalid'
        response.cookies['cart_shop']['expires'] = -10
        response.cookies['cart_shop']['path'] = '/'
        div = DIV(B('Đặt hàng thành công. Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất để xác nhận đơn hàng. Xin cảm ơn! '), _class='bg-info text-center')

        div.append(DIV('phone1 : ', request.vars.dien_thoai))
        div.append(DIV('phone2 : ', request.vars.dien_thoai2))
        div.append(DIV('name1 : ', request.vars.name))
        div.append(DIV('name2 : ', request.vars.name2))
        div.append(DIV('dia_chi : ', request.vars.dia_chi))
        div.append(DIV('mo ta : ', request.vars.description))

        div.append(DIV(BR(), 'Chuyển hướng về trang chủ sau 3 giây.', _class='bg-info text-center'))
        scr = '''
         <META http-equiv="refresh" content="3;URL=%s">
        ''' % (URL(c='portal', f='folder', args=[page_home]))
        div.append(XML(scr))

        return div
    else:
        div = DIV(B('Đặt hàng lỗi, Bạn vui lòng nhập đầy đủ tên, số điện thoại, địa chỉ. Xin cảm ơn! '), _class='bg-info text-center')
        div.append(DIV(BR(), 'Trở lại form đặt hàng sau 10 giây.', _class='bg-info text-center'))
        scr = '''
         <META http-equiv="refresh" content="10;URL=%s">
        ''' % (URL(c='portal', f='folder', args=['thanh-toan']))
        div.append(XML(scr))
        return div


def robots():
    return 'OK'


def sitemaps():
    dcontent = cms.define_table(tablename='dcontent', migrate=False)
    rows = cms.db(dcontent.id > 0).select()
    response.view = 'default/sitemaps.xml'
    return dict(urls=rows, languages=[])


# def search():
# try:
# dcontent = cms.define_table(tablename ='dcontent',migrate=True)
# txt = request.vars.key_search
# rows= cms.db(dcontent.textcontent.like('%'+str(txt)+'%')).select()

# div = DIV(_id='page_search')

# if len(rows)>0:
# div.append(H2(len(rows),T(' Kết quả tìm kiếm cho từ khóa: "'),request.vars.key_search,'"',_id='title_page'))
# ul=UL()
# for row in rows:
# code = '<i style=" background: yellow;">'+request.vars.key_search+'</i>'
# name =  row.name.replace(request.vars.key_search,code)

# name =  name.replace(request.vars.key_search.lower(),code)
# name =  name.replace(request.vars.key_search.upper(),code)
# li = LI(A(B(XML(name)),_href=cms.url_content(row),_class='name'))
# if row.description:
# description =  row.description.replace(request.vars.key_search,code)
# li.append(P(XML(description)))
# ul.append(li)
# div.append(ul)
# else:
# div.append(H2(T('Kết quả tìm kiếm từ khóa: "'),request.vars.key_search,'"',_id='title_page'))
# div.append(P(T('Không có kết quả nào cho từ khóa này.')))

# return div
# except Exception,e: return e

def search_ck():
    dcontent = cms.define_table(tablename='dcontent', migrate=True)
    txt = request.vars.key_anchor
    rows = cms.db(dcontent.textcontent.like('%' + str(txt) + '%')).select()
    div = DIV(_id='page_search')

    if len(rows) > 0:
        div.append(H4(len(rows), T(' Kết quả tìm kiếm cho từ khóa: "'), request.vars.key_anchor, '"', _id='title_page'))
        ul = UL()
        for row in rows:
            code = '<i style=" background: yellow;">' + request.vars.key_anchor + '</i>'
            name = row.name.replace(request.vars.key_anchor, code)

            name = name.replace(request.vars.key_anchor.lower(), code)
            name = name.replace(request.vars.key_anchor.upper(), code)
            li = LI(A(XML(name), _href=cms.url_content(row), _target="_blank", _class='name'))
            ul.append(li)
        div.append(ul)
    else:
        div.append(H2(T('Kết quả tìm kiếm từ khóa: "'), request.vars.key_anchor, '"', _id='title_page'))
        div.append(P(T('Không có kết quả nào cho từ khóa này.')))

    return div


def search():
    try:
        dcontent = cms.define_table(tablename='dcontent', migrate=False)
        txt = request.vars.key_search
        if isinstance(txt, list):
            for t in txt:
                if t != "":
                    txt = t
        rows = cms.db(dcontent.textcontent.like('%' + str(txt) + '%')).select()
        div = DIV(_id='page_search')

        if len(rows) > 0:
            div.append(H2(len(rows), T(' Kết quả tìm kiếm cho từ khóa: "'), txt, '"', _id='title_page'))
            ul = UL()
            for row in rows:
                code = '<i style=" background: yellow;">' + txt + '</i>'
                name = row.name.replace(txt, code)

                name = name.replace(txt.lower(), code)
                name = name.replace(txt.upper(), code)
                li = LI(A(B(XML(name)), _href=cms.url_content(row), _class='name'))
                if row.description:
                    description = row.description.replace(txt, code)
                    li.append(P(XML(description)))
                ul.append(li)
            div.append(ul)
        else:
            div.append(H2(T('Kết quả tìm kiếm từ khóa: "'), txt, '"', _id='title_page'))
            div.append(P(T('Không có kết quả nào cho từ khóa này.')))

        return div
    except Exception, e:
        return e


def form_salesman():
    if request.vars.doi_nhom:
        return LOAD(c='plugin_app', f='thong_tin_daily', args=request.args, vars=request.vars, ajax=False)
    else:
        return LOAD(c='plugin_app', f='form_salesman', args=request.args, vars=request.vars, ajax=False)


def check_name_code():
    auth_name = request.vars.auth_name
    if len(auth_name) < 6: return SPAN("Tên đăng nhập cần dài hơn 6 ký tự")
    user_check = db(db.auth_user.username == auth_name).count()
    ajax = "ajax('%s', ['auth_name'], 'check_auth_user')" % (URL(c='portal', f='check_auth_user'))
    if user_check > 0:
        return SPAN("Tên đăng nhập đã tồn tại")
    else:
        return SPAN("Tên đăng nhập hợp lệ")


def check_auth_user():
    auth_name = request.vars.auth_name
    if len(auth_name) < 6: return SPAN("Tên đăng nhập cần dài hơn 6 ký tự")
    user_check = db(db.auth_user.username == auth_name).count()
    ajax = "ajax('%s', ['auth_name'], 'check_auth_user')" % (URL(c='portal', f='check_auth_user'))
    if user_check > 0:
        return SPAN("Tên đăng nhập đã tồn tại")
    else:
        return SPAN("Tên đăng nhập hợp lệ")


def view_van_don():
    from plugin_app import number_format

    don_hang = cms.define_table('don_hang')
    item_don_hang = cms.define_table('item_don_hang')
    product = cms.define_table('product')
    div = DIV(_id="view_van_don")
    id_don = request.args(1)
    if not id_don: return 'Mã đơn hàng không xác định'
    row_dh = db(don_hang.id == id_don).select().first()
    if not row_dh: return "Mã đơn hàng không hợp lệ"

    div.append(DIV(SPAN('Đơn hàng: ', row_dh.id, _class='pull-left'), _class="title_page"))
    ct = DIV(H4('Thông tin mua hàng', _class='col-lg-12 p10 bb'), _class='box_content')

    ct.append(DIV(DIV(DIV('Người đặt hàng: ', B(row_dh.name), _class='col-lg-6'), DIV('Số điện thoại: ', B(row_dh.dien_thoai), _class='col-lg-6'), _class='row'), _class='col-lg-12 p10'))
    if row_dh.name2 != "":
        ct.append(DIV(DIV(DIV('Người nhận hàng: ', B(row_dh.name2), _class='col-lg-6'), DIV('Số điện thoại: ', B(row_dh.dien_thoai2), _class='col-lg-6'), _class='row'), _class='col-lg-12 p10'))
    ct.append(DIV(DIV('Địa chỉ: ', B(row_dh.dia_chi)), _class='col-lg-12 p10'))
    ct.append(DIV(DIV('Lưu ý: ', B(row_dh.description)), _class='col-lg-12 p10'))

    ct.append(H4("Chi tiết đơn hàng", _class='col-lg-12 p10'))
    table = TABLE(TR(TH("Stt"), TH('Sản phẩm'), TH('Đơn giá'), TH('Số lượng'), TH('Thành tiền')), _class='table')
    row_item = db(item_don_hang.don_hang == row_dh.id).select()
    i = 1
    tong_tien = 0
    for row in row_item:
        row_prd = db(product.id == row.product).select().first()
        table.append(TR(TD(i), TD(row_prd.name), TD(number_format(row.price), ' đ'), TD(row.r_number), TD(number_format(row.price * row.r_number), ' đ')))
        tong_tien += row.price * row.r_number
    table.append(TR(TD(B('TỔNG TIỀN'), _colspan='4', _class='text-center'), TD(B(number_format(tong_tien), ' đ'))))
    ct.append(table)

    div.append(ct)

    return div


def clear_cookie():
    response.cookies['cart_shop'] = 'invalid'
    response.cookies['cart_shop']['expires'] = -10
    response.cookies['cart_shop']['path'] = '/'
    return "Đã xoá"
