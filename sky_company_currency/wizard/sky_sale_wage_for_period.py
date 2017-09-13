# -*- coding: utf-8 -*-
from openerp import fields,models,api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

class open_sale_wage_for_period(models.TransientModel):
    _name = 'sky.open.sale.wage'

    period_from = fields.Many2one('account.period', 'Tháng bắt đầu')
    period_to   = fields.Many2one('account.period', 'Tháng kết thúc')

    @api.multi
    def action_view(self):
        domain = []
        if self.period_from:
            domain += [('x_ngaytinhdoanhso', '>=', self.period_from.date_start)]
        if self.period_to:
            domain += [('x_ngaytinhdoanhso', '<=', self.period_to.date_stop)]

        view_id = self.env.ref('sky_company_currency.view_sky_sale_wage_graph', False)

        return {
            'name': _('Lương doanh số'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'graph',
            'res_model': 'sale.report',
            'view_id': view_id and view_id.id or False,
            'domain': domain,
            'context': {'close_so': True, 'search_disable_custom_filters': False},
        }