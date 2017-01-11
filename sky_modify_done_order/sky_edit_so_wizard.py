# -*- coding: utf-8 -*-
from openerp import fields,models,api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

class EditSO(models.TransientModel):
    _name = 'sky.edit.sale.order'

    pricelist_id    = fields.Many2one('product.pricelist', 'Pricelist')
    price_unit      = fields.Float('Price unit', digits=(6,2))

    @api.multi
    def submit(self):
        if self._context.get('active_model', False) != 'sale.order':
            raise ValidationError(_('Active model just as Sale Order!'))
        order = self.env['sale.order'].browse(self._context.get('active_id'))
        if len(order.order_line) > 1:
            raise ValidationError(_('This SO have more than one line!'))

        if self.pricelist_id:
            order.write({'pricelist_id': self.pricelist_id.id})

        if self.price_unit:
            order.order_line.write({'price_unit': self.price_unit})
