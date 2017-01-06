# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

class sky_result_multi_so(models.TransientModel):
    _name = 'sky_result_multi_so'

    # ketqua = fields.Selection([('pass','Pass'), ('fall','Fall'), ('canceled','Cancelled')], string="Result")
    date_result = fields.Date('Date result', required=True)

    @api.multi
    def submit(self):
        self.ensure_one()
        if not self._context.get('active_model', False) == 'sale.order':
            return

        so_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
        has_result = so_ids.filtered(lambda so: so.x_ngaytinhdoanhso or not so.ketqua)
        if has_result:
            so_names = ','.join(has_result.mapped('name'))
            raise ValidationError(_('These orders have results or days of sales ') + so_names)
        so_ids.write({'x_ngaytinhdoanhso': self.date_result})
