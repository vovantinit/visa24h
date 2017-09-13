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
    @api.depends('amount_total', 'pricelist_id', 'order_line.price_unit', 'order_line.tax_id', 'order_line.discount', 'order_line.product_uom_qty')
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

    # @api.multi
    # @api.depends('analytic_account_id', 'analytic_account_id.balance', 'analytic_account_id.line_ids', 
    #     'analytic_account_id.line_ids.journal_id.name', 'analytic_account_id.line_ids.amount')
    # def _compute_transactions_amount(self):
    #     for record in self:
    #         acc_analytic_credit = sum(line.amount for line in record.analytic_account_id.line_ids if line.journal_id.name == 'Purchases')
    #         acc_analytic_debit  = sum(line.amount for line in record.analytic_account_id.line_ids if line.journal_id.name == 'Sales')
    #         # acc_analytic_balance = acc_analytic_debit + acc_analytic_credit
    #         acc_analytic_balance = sum(line.amount for line in record.analytic_account_id.line_ids)
    #         acc_analytic_gm = '' if acc_analytic_debit == 0 else str(round(acc_analytic_balance / acc_analytic_debit * 100, 2))
    #         record.write({
    #             'acc_analytic_credit': acc_analytic_credit,
    #             'acc_analytic_debit': acc_analytic_debit,
    #             'acc_analytic_balance': acc_analytic_balance,
    #             'acc_analytic_gm': acc_analytic_gm,
    #         })
            
    # @api.multi
    # # @api.depends('invoice_ids', 'invoice_ids.residual', 'invoice_ids.state')
    # def _compute_customer_residual(self):
    #     for rec in self:
    #         if rec.invoice_ids:
    #             customer_residual = 0
    #             for invoice in rec.invoice_ids:
    #                 if invoice.state != 'cancel':
    #                     customer_residual += invoice.currency_id.with_context(date=invoice.date_invoice or invoice.create_date).compute(invoice.residual, invoice.main_currency_id, round=True)
    #             # rec.customer_residual = customer_residual
    #             rec.write({'customer_residual': customer_residual})
    #         else:
    #             # rec.customer_residual = 0
    #             rec.write({'customer_residual': 0})


    # acc_analytic_debit      = fields.Float('Analytic Sales', compute='_compute_transactions_amount', store=True)
    # acc_analytic_credit     = fields.Float('Analyctic Purchase', compute='_compute_transactions_amount', store=True)
    # acc_analytic_balance    = fields.Float('Analyctic Balance', compute='_compute_transactions_amount', store=True)
    # acc_analytic_gm         = fields.Char('% GM', compute='_compute_transactions_amount')

    # customer_residual = fields.Float(string='Customer Balance', store=True, compute='_compute_customer_residual')
    @api.multi
    def _compute_transactions_amount(self):
        for record in self:
            acc_analytic_credit = sum(line.amount for line in record.analytic_account_id.line_ids if line.journal_id.name == 'Purchases')
            acc_analytic_debit  = sum(line.amount for line in record.analytic_account_id.line_ids if line.journal_id.name == 'Sales')
            acc_analytic_balance = sum(line.amount for line in record.analytic_account_id.line_ids)
            acc_analytic_gm     = '' if acc_analytic_debit == 0 else str(round(acc_analytic_balance / acc_analytic_debit * 100, 2))
            
            vals = {}
            if acc_analytic_credit != record.acc_analytic_credit:
                vals.update({'acc_analytic_credit': acc_analytic_credit})

            if acc_analytic_debit != record.acc_analytic_debit:
                vals.update({'acc_analytic_debit': acc_analytic_debit})

            if acc_analytic_balance != record.acc_analytic_balance:
                vals.update({'acc_analytic_balance': acc_analytic_balance})

            if acc_analytic_gm != record.acc_analytic_gm:
                vals.update({'acc_analytic_gm': acc_analytic_gm})

            customer_residual = 0
            if record.invoice_ids:
                for invoice in record.invoice_ids:
                    if invoice.state != 'cancel':
                        #customer_residual += invoice.currency_id.with_context(date=invoice.date_invoice or invoice.create_date).compute(invoice.residual, invoice.main_currency_id, round=True)
                        customer_residual = invoice.payment_ids and abs(invoice.payment_ids[0].amount_residual) or 0
                        break
            if customer_residual != (record.customer_residual or 0):
                vals.update({'customer_residual': customer_residual})
            record.sky_compute = ''
            record.write(vals)

    sky_compute             = fields.Char(compute='_compute_transactions_amount')

    acc_analytic_debit      = fields.Float('Analytic Sales', store=True)
    acc_analytic_credit     = fields.Float('Analyctic Purchase', store=True)
    acc_analytic_balance    = fields.Float('Analyctic Balance', store=True)
    acc_analytic_gm         = fields.Char('% GM')

    customer_residual       = fields.Float(string='Customer Balance', store=True)

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

class ResUsers(models.Model):
    _inherit = 'res.users'

    team_ids = fields.Many2many('crm.case.section', 'sale_member_rel', 'member_id', 'section_id', 'Teams')
    manager_team_ids = fields.One2many('crm.case.section',  'user_id', string='Teams manager')
ResUsers()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
