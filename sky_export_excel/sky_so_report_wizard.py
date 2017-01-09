# -*- coding: utf-8 -*-
from openerp import fields,models,api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

class SoExcelReport(models.TransientModel):
    _name = 'sky.so.excel.report'

    date_from   = fields.Date('Date from', required=True, default=fields.Date.today())
    date_to     = fields.Date('Date to', required=True, default=fields.Date.today())

    @api.multi
    def submit(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/skyerp/excel_report/so?date_from=%s&date_to=%s' % (self.date_from, self.date_to),
            'target': 'new',
            'destroy': True,
        }