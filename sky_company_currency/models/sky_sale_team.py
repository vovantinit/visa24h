# -*- coding: utf-8 -*-
import json
import calendar
from openerp import models, fields, api
from openerp.osv import osv, fields as osv_fields
from datetime import date
from dateutil import relativedelta
from openerp import tools
from openerp.tools.float_utils import float_repr
import openerp.addons.decimal_precision as dp
from lxml import etree
from openerp.exceptions import ValidationError

class crm_case_section(models.Model):
    _inherit = 'crm.case.section'

    @api.multi
    def _get_sale_orders_data(self):
        obj = self.pool['sale.order']

        month_begin = date.today().replace(day=1)
        date_begin  = (month_begin - relativedelta.relativedelta(months=self._period_number - 1)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        date_end    = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

        for sale_team in self:
            created_domain      = [('section_id', 'child_of', sale_team.id), ('state', 'in', ['draft', 'sent']), ('date_order', '>=', date_begin), ('date_order', '<=', date_end)]
            validated_domain    = [('section_id', 'child_of', sale_team.id), ('state', 'not in', ['draft', 'sent', 'cancel']), ('date_order', '>=', str(date.today().replace(day=1))), ('date_order', '<=', date_end)]

            sale_team.monthly_quoted    = json.dumps(self.__get_bar_values(obj, created_domain, ['vnd_amount_total', 'date_order'], 'vnd_amount_total', 'date_order'))
            #sale_team.monthly_confirmed = json.dumps(self.__get_bar_values(obj, validated_domain, ['vnd_amount_untaxed', 'date_order'], 'vnd_amount_untaxed', 'date_order'))
            sale_team.monthly_confirmed = self.env['sale.order'].read_group(validated_domain, ['vnd_amount_untaxed'], [])[0]['vnd_amount_untaxed'] or 0

    def _get_invoices_data(self, cr, uid, ids, field_name, arg, context=None):
        obj = self.pool['account.invoice.report']
        month_begin = date.today().replace(day=1)
        date_begin = (month_begin - relativedelta.relativedelta(months=self._period_number - 1)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        date_end = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

        res = {}
        for id in ids:
            section_ids = [id] + self.browse(cr, uid, id, context=context).child_ids.ids
            created_domain = [('type', 'in', ['out_invoice', 'out_refund']), ('section_id', 'in', section_ids), ('state', 'not in', ['draft', 'cancel']), ('date', '>=', date_begin), ('date', '<=', date_end)]
            values = self.__get_bar_values(cr, uid, obj, created_domain, ['price_total', 'date'], 'price_total', 'date', context=context)
            for value in values:
                value['value'] = float_repr(value.get('value', 0), precision_digits=self.pool['decimal.precision'].precision_get(cr, uid, 'Account'))
            res[id] = json.dumps(values)
        return res


    monthly_quoted      = fields.Char(compute='_get_sale_orders_data', readonly=True, string='Rate of created quotation per duration')
    monthly_confirmed   = fields.Char(compute='_get_sale_orders_data', readonly=True, string='Rate of validate sales orders per duration')
    _columns = {
        'monthly_invoiced': osv_fields.function(_get_invoices_data,
            type='char', readonly=True,
            string='Rate of sent invoices per duration'),
        'invoiced_target': osv_fields.float(string='Invoice Target', digits=(20, 0),
            help="Target of invoice revenue for the current month. This is the amount the sales \n"
                    "team estimates to be able to invoice this month."),
        'invoiced_forecast': osv_fields.float(string='Invoice Forecast', digits=(20, 0),
            help="Forecast of the invoice revenue for the current month. This is the amount the sales \n"
                    "team should invoice this month. It is used to compute the progression ratio \n"
                    " of the current and forecast revenue on the kanban view."),
    }

crm_case_section()
