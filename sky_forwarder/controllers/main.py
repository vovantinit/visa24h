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
        UserModel = http.request.env['res.users']
        is_manager = UserModel.has_group('sky_forwarder.group_forwarder_user')
        user_ids = http.request.env.ref('sky_forwarder.group_forwarder_nhan_vien').users.filtered(lambda r: not UserModel.sudo(r.id).has_group('sky_forwarder.group_forwarder_manager'))

        # domain = ['|', ('forwarder_id', 'in', (False, http.request.env.user.id)), (is_manager, '=', True)]
        # domain = [('forwarder_id', 'in', (False, http.request.env.user.id))]

        domain = []

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
        })


    @http.route('/gan_giao_nhan', auth='user', website=True)
    def gan_giao_nhan(self, **post):
        try:
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

            return http.request.redirect("/giao_nhan?success=1")

        except Exception as e:
            return http.request.redirect("/giao_nhan?error=1")

    @http.route('/ghichu', auth='user', website=True)
    def ghichu(self, **post):

        if not http.request.env.user:
            return http.request.redirect("/web/login")

        if post.get('comment', False):
            Models = http.request.env['sky.forwarder']
            res = Models.browse(int(post.get('record_id', False)))
            res.write({
                'note_v2': u'{}'.format(post.get('comment', '')),
                'he_so': int(post.get('he_so', 1)),
            })

        return http.request.redirect("/giao_nhan")