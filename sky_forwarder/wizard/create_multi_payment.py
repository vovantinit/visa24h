# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from lxml import etree
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import time
import datetime

class CreateMultiPayment(models.TransientModel):
    _name = 'sky.create.multi.payment'

    @api.model 
    def default_get(self, fields):
        res = super(CreateMultiPayment, self).default_get(fields)
        ship_ids = self._context.get('active_ids', [])
        ship_ids = self.env['sky.forwarder'].search([('id','in',ship_ids),('forwarder_id','!=',False),('delivered','=',True),('invoice_id','=',False)])
        res['ship_ids'] = ship_ids.mapped('id')
        return res

    ship_ids = fields.Many2many('sky.forwarder', string='Giao nhận')

    @api.multi
    def submit(self):
        self.ensure_one()
        self.ship_ids.create_multi_invoice()
            