# -*- coding: utf-8 -*-
from openerp import http
from datetime import datetime, date

class GiaoNhanModule(http.Controller):


    @http.route('/giao_nhan', auth='user', website=True)
    def giao_nhan(self, **post):

        order = 'sequence, write_date desc, s_date desc'
        if not http.request.env.user or http.request.env.user and http.request.env.user.id == 3:
            return http.request.redirect("/web/login?redirect=giao_nhan")

        Models = http.request.env['sky.forwarder']
        is_manager = http.request.env['res.users'].has_group('sky_forwarder.group_forwarder_user')

        user_ids = http.request.env.ref('sky_forwarder.group_forwarder_nhan_vien').users

        domain = ['|', ('forwarder_id', 'in', (False, http.request.env.user.id)), (is_manager, '=', True)]
        # domain = [('forwarder_id', 'in', (False, http.request.env.user.id))]

        thong_ke = []
        for nv in user_ids:
            thong_ke.append({
                'name': nv.name,
                'sl_nhan': Models.search_count([('s_date','=',str(date.today())),('forwarder_id','=',nv.id)]),
                'sl_giao': Models.search_count([('s_date','=',str(date.today())),('forwarder_id','=',nv.id),('delivered','=',True)]),
            })

        return http.request.render('sky_forwarder.index', {
            'user': http.request.env.user.id,
            'user_ids': user_ids,
            'datas': Models.search(domain, order=order, limit=20),
            'is_manager': is_manager,
            'thong_ke': thong_ke,
        })


    @http.route('/gan_giao_nhan', auth='user', website=True)
    def gan_giao_nhan(self, **post):

        if not http.request.env.user:
            return http.request.redirect("/web/login")

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

        return http.request.redirect("/giao_nhan")

    @http.route('/ghichu', auth='user', website=True)
    def ghichu(self, **post):

        if not http.request.env.user:
            return http.request.redirect("/web/login")

        if post.get('comment', False):
            Models = http.request.env['sky.forwarder']
            res = Models.browse(int(post.get('record_id', False)))
            res.write({'note_v2': u'{}'.format(post.get('comment', ''))})

        return http.request.redirect("/giao_nhan")