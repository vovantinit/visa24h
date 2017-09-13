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