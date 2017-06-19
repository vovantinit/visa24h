# -*- coding: utf-8 -*-
from openerp import http
from datetime import datetime, date, timedelta
import xlwt
from openerp.http import request

class GiaoNhanModule(http.Controller):

    # def tgl_write_excel(self, worksheet, rows, col, value, so_style_v2=None):
    #     if so_style_v2:
    #         worksheet.write(rows, col, value, so_style_v2)
    #     else:
    #         worksheet.write(rows, col, value)
    #     return col + 1


    # @http.route(['/skyerp/excel_report/giao_nhan'], type='http', auth="user")
    # def sky_account_tax_report(self, date_from, date_to, debug=None):
    #     filename = u'Bao cao giao nhan'

    #     workbook    = xlwt.Workbook()
    #     worksheet   = workbook.add_sheet('%s - %s' % (date_from, date_to))

    #     datas = request.env['sky.forwarder'].search([('s_date','>=',date_from),('s_date','<=',date_to)])

    #     trang_thai = {
    #         'new': u'Mới',
    #         'set_forwarder': u'Đã phân bổ',
    #         'delivered': u'Đã giao',
    #         'to_invoice': u'Đã xuất hóa đơn',
    #         'done': u'Hoàn thành',
    #         'cancel': u'Hủy',
    #     }

    #     header_names = [
    #         u'Giao nhận',
    #         u'Trạng thái',
    #         u'Người đề nghị',
    #         u'Nhân viên giao nhận',
    #         u'Đơn hàng',
    #         u'Ngày cần giao',
    #         u'Thời gian giao nhận',
    #         u'Hệ số',
    #         u'Số tiền thu hộ',
    #         u'Chi phí giao nhận',
    #         u'Từ địa điểm',
    #         u'Khách hàng',
    #         u'',
    #         u'',
    #         u'',
    #         u'',
    #         u'',
    #         u'',
    #     ]

    #     rows = 0
    #     for data in datas:
    #         rows += 1
    #         col = 0
    #         col = self.tgl_write_excel(worksheet, rows, col, data.name or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, trang_thai[data.state])
    #         col = self.tgl_write_excel(worksheet, rows, col, data.user_id.name or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.forwarder_id.name or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, ','.join(data.order_ids.mapped('name')) or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.s_date or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.s_datetime or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.he_so or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.value or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.forwarder_cost or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.from_location_id.name or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.partner_id.name or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.phone or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.address or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.to_location_id.name or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.delivered or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.real_time or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.note or '')
    #         col = self.tgl_write_excel(worksheet, rows, col, data.note_v2 or '')

    #     response = request.make_response(None,
    #         headers=[('Content-Type', 'application/vnd.ms-excel'),
    #                 ('Content-Disposition', 'attachment; filename=%s.xls' % filename)])
    #     workbook.save(response.stream)
    #     return response

    @http.route('/giao_nhan', auth='user', website=True)
    def giao_nhan(self, **post):

        order = 'sequence, s_date desc, write_date desc'
        if not http.request.env.user or http.request.env.user and http.request.env.user.id == 3:
            return http.request.redirect("/web/login?redirect=giao_nhan")

        filter_d = post.get('filter_d', 'all')

        Models = http.request.env['sky.forwarder']
        UserModel = http.request.env['res.users']
        is_manager = UserModel.has_group('sky_forwarder.group_forwarder_user')
        user_ids = http.request.env.ref('sky_forwarder.group_forwarder_nhan_vien').users.filtered(lambda r: not UserModel.sudo(r.id).has_group('sky_forwarder.group_forwarder_manager'))

        # domain = ['|', ('forwarder_id', 'in', (False, http.request.env.user.id)), (is_manager, '=', True)]
        # domain = [('forwarder_id', 'in', (False, http.request.env.user.id))]

        # Chi xem hom nay, hom qua va hom kia
        domain = ['|', ('state', 'in', ('new', 'set_forwarder')), 
                        '&', ('s_date', '>=', str(date.today())), 
                        ('s_date', '<', str(date.today() + timedelta(days=3)))]

        if filter_d == 'my':
            domain.append(('forwarder_id','=',http.request.env.user.id))
        elif filter_d == 'avaiable':
            domain.append(('forwarder_id','=',False))            


        thong_ke = []
        for nv in user_ids:
            thong_ke.append({
                'name': nv.name,
                'sl_nhan': Models.search_count([('s_date','=',str(date.today())),('forwarder_id','=',nv.id)]),
                'sl_giao': Models.search_count([('s_date','=',str(date.today())),('forwarder_id','=',nv.id),('delivered','=',True)]),
            })

        offset = (int(post.get('page', 1)) - 1) * 20

        return http.request.render('sky_forwarder.index', {
            'user': http.request.env.user.id,
            'user_ids': user_ids,
            'datas': Models.search(domain, order=order, limit=20, offset=offset),
            'is_manager': is_manager,
            'thong_ke': thong_ke,
            'page': post.get('page', 1),
            'error': post.get('error', False),
            'success': post.get('success', False),
            'filter_d': filter_d,
        })


    @http.route('/gan_giao_nhan', auth='user', website=True)
    def gan_giao_nhan(self, **post):
        try:
            if not http.request.env.user:
                return http.request.redirect("/web/login?redirect=giao_nhan")

            Models = http.request.env['sky.forwarder']

            if post.get('record_id', False):
                res = Models.browse(int(post.get('record_id', False)))
                record_type = post.get('record_type', False)
                delivered   = post.get('delivered', False)
               
                if record_type == 'set':
                    res.write({'forwarder_id': int(post.get('to_id', False))} )

                if record_type == 'del':
                    res.write({'forwarder_id': False})            

                if delivered == 't':
                    res.write({'delivered': True})

                if delivered == 'f':
                    res.write({'delivered': False})

            return http.request.redirect("/giao_nhan?success=1")

        except Exception as e:
            return http.request.redirect("/giao_nhan?error=1")

    @http.route('/ghichu', auth='user', website=True)
    def ghichu(self, **post):

        if not http.request.env.user:
            return http.request.redirect("/web/login?redirect=giao_nhan")

        # if post.get('comment', False):
        Models = http.request.env['sky.forwarder']
        res = Models.browse(int(post.get('record_id', False)))
        res.write({
            'note_v2': u'{}'.format(post.get('comment', '')),
            'he_so': int(post.get('he_so', 1)),
        })

        return http.request.redirect("/giao_nhan")