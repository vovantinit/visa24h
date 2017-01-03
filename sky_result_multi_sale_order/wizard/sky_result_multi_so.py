# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

class sky_result_multi_so(models.TransientModel):
    _name = 'sky_result_multi_so'

    ketqua = fields.Selection([('pass','Pass'), ('fall','Fall'), ('canceled','Cancelled')], string="Result")

    @api.multi
    def submit(self):
        self.ensure_one()
        if not self._context.get('active_model', False) == 'sale.order':
            return

        so_ids = self._context.get('active_ids')
        self.env['sale.order'].browse(so_ids).write({'ketqua': self.ketqua})
