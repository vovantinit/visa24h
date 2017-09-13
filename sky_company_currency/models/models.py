# -*- coding: utf-8 -*-
#/#############################################################################
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################

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

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    def _compute_vnd_price_subtotal(self):
        to_currency             = self.order_id.main_currency_id
        from_currency           = self.order_id.pricelist_id and self.order_id.pricelist_id.currency_id or to_currency
        self.vnd_price_subtotal = from_currency.with_context(date=self.order_id.date_order).compute(self.price_subtotal, to_currency, round=True)
        self.vnd_price_unit     = from_currency.with_context(date=self.order_id.date_order).compute(self.price_unit, to_currency, round=True)

    show_vnd_footer     = fields.Boolean('Show Footer (VND)', related='order_id.show_vnd_footer')
    vnd_price_subtotal  = fields.Float(string='Subtotal (VND)', compute='_compute_vnd_price_subtotal', digits_compute= dp.get_precision('Account'))
    vnd_price_unit      = fields.Float(string='Unit Price (VND)', compute='_compute_vnd_price_subtotal', digits_compute= dp.get_precision('Account'))

SaleOrderLine()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.depends('order_line.price_unit', 'order_line.tax_id', 'order_line.discount', 'order_line.product_uom_qty')
    def _amount_vnd_all(self):
        currency_id = self.env.ref('base.main_company').currency_id
        for order in self:
            order.main_currency_id      = currency_id.id
            order.show_vnd_footer       = order.currency_id and order.currency_id != currency_id
            if order.currency_id:
                order.exchange_rate             = order.currency_id.with_context(date=order.date_order or order.create_date).compute(1.00, currency_id, round=True)
                order.vnd_amount_untaxed    = order.currency_id.with_context(date=order.date_order or order.create_date).compute(sum(line.price_subtotal for line in order.order_line), currency_id, round=True)
                order.vnd_amount_tax        = order.currency_id.with_context(date=order.date_order or order.create_date).compute(sum(self._amount_line_tax(line) for line in order.order_line), currency_id, round=True)
                order.vnd_amount_total      = order.vnd_amount_tax + order.vnd_amount_untaxed

    exchange_rate       = fields.Float('Exchange rate (VND)', compute='_amount_vnd_all', store=True, readonly=True)
    show_vnd_footer     = fields.Boolean('Show Footer (VND)', compute='_amount_vnd_all', store=True)
    main_currency_id    = fields.Many2one('res.currency', 'Main Currency', compute='_amount_vnd_all', store=True)
    vnd_amount_untaxed  = fields.Float(string='Untaxed Amount (VND)', compute='_amount_vnd_all', store=True)
    vnd_amount_tax      = fields.Float(string='Taxes (VND)', compute='_amount_vnd_all', store=True)
    vnd_amount_total    = fields.Float(string='Total (VND)', compute='_amount_vnd_all', store=True)

    @api.multi
    @api.depends('analytic_account_id', 'analytic_account_id.balance', 'analytic_account_id.line_ids', 
        'analytic_account_id.line_ids.journal_id.name', 'analytic_account_id.line_ids.amount')
    def _compute_transactions_amount(self):
        for record in self:
            acc_analytic_credit = sum(line.amount for line in record.analytic_account_id.line_ids if line.journal_id.name == 'Purchases')
            acc_analytic_debit  = sum(line.amount for line in record.analytic_account_id.line_ids if line.journal_id.name == 'Sales')
            # acc_analytic_balance = acc_analytic_debit + acc_analytic_credit
            acc_analytic_balance = sum(line.amount for line in record.analytic_account_id.line_ids)
            acc_analytic_gm = '' if acc_analytic_debit == 0 else str(round(acc_analytic_balance / acc_analytic_debit * 100, 2))
            record.write({
                'acc_analytic_credit': acc_analytic_credit,
                'acc_analytic_debit': acc_analytic_debit,
                'acc_analytic_balance': acc_analytic_balance,
                'acc_analytic_gm': acc_analytic_gm,
            })
            

    @api.depends('invoice_ids', 'invoice_ids.residual', 'invoice_ids.state')
    def _compute_customer_residual(self):
        for rec in self:
            if rec.invoice_ids:
                sum_residual = 0
                for invoice in rec.invoice_ids:
                    if invoice.state != 'cancel':
                        sum_residual += invoice.residual
                rec.customer_residual = sum_residual
            else:
                rec.customer_residual = 0


    acc_analytic_debit      = fields.Float('Analytic Sales', compute='_compute_transactions_amount', store=True)
    acc_analytic_credit     = fields.Float('Analyctic Purchase', compute='_compute_transactions_amount', store=True)
    acc_analytic_balance    = fields.Float('Analyctic Balance', compute='_compute_transactions_amount', store=True)
    acc_analytic_gm         = fields.Char('% GM',
                                    compute='_compute_transactions_amount')

    customer_residual = fields.Float(
        string='Customer Balance', store=True,
        compute='_compute_customer_residual'
    )

    @api.depends('order_line', 'order_line.product_id')
    def _compute_product_category_id(self):
        for rec in self:
            if rec.order_line:
                rec.product_category_id = len(rec.order_line[0].product_id) and \
                    rec.order_line[0].product_id.product_tmpl_id.categ_id or False
                rec.product_product_id = rec.order_line[0].product_id

    product_category_id = fields.Many2one(
        comodel_name='product.category', store=True,
        string='Product Category',
        compute='_compute_product_category_id'
    )

    product_product_id = fields.Many2one(
        comodel_name='product.product', store=True,
        string='Product',
        compute='_compute_product_category_id'
    )


SaleOrder()

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _compute_vnd_price(self):
        for inv in self:
            if not inv.invoice_id: continue
            inv.vnd_price_subtotal = inv.invoice_id.currency_id.with_context(date=inv.invoice_id.date_invoice).compute(inv.price_subtotal, inv.invoice_id.main_currency_id, round=True)

    show_vnd_footer     = fields.Boolean(related='invoice_id.show_vnd_footer')
    vnd_price_subtotal = fields.Float(string='Amount (VND)', digits= dp.get_precision('Account'), readonly=True, compute='_compute_vnd_price')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_vnd_amount(self):
        to_currency = self.env.ref('base.main_company').currency_id
        for invoice in self:
            invoice.main_currency_id = to_currency.id
            if invoice.currency_id:
                invoice.exchange_rate      = invoice.currency_id.with_context(date=invoice.date_invoice or invoice.create_date).compute(1.00, to_currency, round=True)
                invoice.vnd_amount_untaxed = invoice.currency_id.with_context(date=invoice.date_invoice or invoice.create_date).compute(sum(line.price_subtotal for line in invoice.invoice_line), to_currency, round=True)
                invoice.vnd_amount_tax     = invoice.currency_id.with_context(date=invoice.date_invoice or invoice.create_date).compute(sum(line.amount for line in invoice.tax_line), to_currency, round=True)
                invoice.vnd_amount_total   = invoice.vnd_amount_untaxed + invoice.vnd_amount_tax

    @api.multi
    def _compute_show_vnd_footer(self):
        for invoice in self:
            invoice.show_vnd_footer = invoice.currency_id and invoice.currency_id != invoice.company_id.currency_id

    exchange_rate       = fields.Float('Exchange rate (VND)', compute='_compute_vnd_amount', store=True, readonly=True)
    main_currency_id    = fields.Many2one('res.currency', 'Main Currency', compute='_compute_vnd_amount', store=True)
    show_vnd_footer     = fields.Boolean('Show Footer (VND)', compute='_compute_show_vnd_footer')
    vnd_amount_untaxed  = fields.Float(string='Untaxed Amount (VND)', compute='_compute_vnd_amount', store=True)
    vnd_amount_tax      = fields.Float(string='Taxes (VND)', compute='_compute_vnd_amount', store=True)
    vnd_amount_total    = fields.Float(string='Total (VND)', compute='_compute_vnd_amount', store=True)

AccountInvoice()

class crm_case_section(models.Model):
    _inherit = 'crm.case.section'

    @api.multi
    def _get_sale_orders_data(self):
        obj = self.pool['sale.order']

        month_begin = date.today().replace(day=1)
        date_begin  = (month_begin - relativedelta.relativedelta(months=self._period_number - 1)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        date_end    = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        
        for sale_team in self:
            created_domain      = [('section_id', 'in', (sale_team + sale_team.child_ids).mapped('id')), ('state', 'in', ['draft', 'sent']), ('date_order', '>=', date_begin), ('date_order', '<=', date_end)]
            validated_domain    = [('section_id', 'in', (sale_team + sale_team.child_ids).mapped('id')), ('state', 'not in', ['draft', 'sent', 'cancel']), ('date_order', '>=', date_begin), ('date_order', '<=', date_end)]

            sale_team.monthly_quoted    = json.dumps(self.__get_bar_values(obj, created_domain, ['vnd_amount_total', 'date_order'], 'vnd_amount_total', 'date_order'))
            sale_team.monthly_confirmed = json.dumps(self.__get_bar_values(obj, validated_domain, ['vnd_amount_untaxed', 'date_order'], 'vnd_amount_untaxed', 'date_order'))

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

class sale_report(models.Model):
    _inherit = 'sale.report'

    product_category_id = fields.Many2one('product.category', string='Product Category',)
    product_product_id = fields.Many2one('product.product', string='Product')
    acc_analytic_debit      = fields.Float('Analytic Sales')
    acc_analytic_credit     = fields.Float('Analyctic Purchase')
    acc_analytic_balance    = fields.Float('Analyctic Balance')

    def _select(self):
        select_str = super(sale_report, self)._select()
        add_fields = '''
            ,s.product_category_id,
            s.product_product_id,
            s.acc_analytic_debit,
            s.acc_analytic_credit,
            s.acc_analytic_balance
        '''
        return select_str + add_fields

    def _group_by(self):
        group_by_str = super(sale_report, self)._group_by()
        add_groups = '''
            ,s.product_category_id,
            s.product_product_id,
            s.acc_analytic_debit,
            s.acc_analytic_credit,
            s.acc_analytic_balance
        '''
        return group_by_str + add_groups


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: