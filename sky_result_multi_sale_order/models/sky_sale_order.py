# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ketqua = fields.Selection(selection_add=[('delay', 'Treo')])