# -*- coding: utf-8 -*-
from openerp import models, fields, api
import time

class SkyForeCast(models.Model):
    _name = 'sky.crm.team.forecast'

    _order = 'date_start desc'

    _sql_constraints = [
        ('period_uniq', 'unique (team_id,period_id)', 'Các khoảng thời gian dự báo không được trùng nhau!')
    ]

    @api.multi
    def _sky_compute_all_value(self):
        Invoice_obj = self.env['account.invoice.report']
        Sale_obj    = self.env['sale.order']
        for record in self:
            section_ids     = (record.team_id + record.team_id.child_ids).mapped('id')
            invoice_domain  = [('type', 'in', ['out_invoice', 'out_refund']), 
                                ('section_id', 'in', section_ids), 
                                ('state', 'not in', ['draft', 'cancel']), 
                                ('date', '>=', record.date_start), 
                                ('date', '<=', record.date_stop)]
            invoice_real = Invoice_obj.read_group(invoice_domain, ['price_total', 'date'], ['date'])
            if invoice_real:
                record.monthly_invoiced = invoice_real[0]['price_total']

            quoted_domain   = [('section_id', 'in', section_ids), 
                                ('state', 'in', ['draft', 'sent']), 
                                ('date_order', '>=', record.date_start), 
                                ('date_order', '<=', record.date_stop)]

            quoted_real = Sale_obj.read_group(quoted_domain, ['vnd_amount_total', 'date_order'], ['date_order'])
            if quoted_real:
                record.monthly_quoted = quoted_real[0]['vnd_amount_total']

            confirm_domain  = [('section_id', 'in', section_ids), 
                                ('state', 'not in', ['draft', 'sent', 'cancel']), 
                                ('date_order', '>=', record.date_start), 
                                ('date_order', '<=', record.date_stop)]

            confirm_real = Sale_obj.read_group(confirm_domain, ['vnd_amount_untaxed', 'date_order'], ['date_order'])
            if confirm_real:
                record.monthly_confirmed = confirm_real[0]['vnd_amount_untaxed']


    team_id     = fields.Many2one('crm.case.section', 'Đội bán hàng')
    period_id   = fields.Many2one('account.period', 'Tháng')
    date_start  = fields.Date(related='period_id.date_start', store=True, readonly=True)
    date_stop   = fields.Date(related='period_id.date_stop', store=True, readonly=True)

    invoiced_target     = fields.Float('Mục tiêu đơn hàng', digits=(20, 0))
    invoiced_forecast   = fields.Float('Đơn hàng dự kiến', digits=(20, 0))

    monthly_quoted      = fields.Float('Báo gía thực tế', digits=(20, 0), compute='_sky_compute_all_value')
    monthly_confirmed   = fields.Float('Đơn hàng thực tế', digits=(20, 0), compute='_sky_compute_all_value')
    monthly_invoiced    = fields.Float('Hóa đơn thực tế', digits=(20, 0), compute='_sky_compute_all_value')

SkyForeCast()


class crm_case_section(models.Model):
    _inherit = 'crm.case.section'

    @api.multi
    def _sky_compute_all_value(self):
        Invoice_obj = self.env['account.invoice.report']
        Sale_obj    = self.env['sale.order']
        date_start  = time.strftime('%Y-%m-01')
        for record in self:
            section_ids     = (record + record.child_ids).mapped('id')
            invoice_domain  = [('type', 'in', ['out_invoice', 'out_refund']), 
                                ('section_id', 'in', section_ids), 
                                ('state', 'not in', ['draft', 'cancel']), 
                                ('date', '>=', date_start)]
            invoice_real = Invoice_obj.read_group(invoice_domain, ['price_total', 'date'], ['date'])
            record.real_monthly_invoiced = invoice_real and invoice_real[0]['price_total'] or 0

            confirm_domain  = [('section_id', 'in', section_ids), 
                                ('state', 'not in', ['draft', 'sent', 'cancel']), 
                                ('date_order', '>=', date_start)]

            confirm_real = Sale_obj.read_group(confirm_domain, ['vnd_amount_untaxed', 'date_order'], ['date_order'])
            record.real_monthly_confirmed = confirm_real and confirm_real[0]['vnd_amount_untaxed'] or 0

    real_monthly_confirmed   = fields.Float('Đơn hàng thực tế', digits=(20, 0), compute='_sky_compute_all_value')
    real_monthly_invoiced    = fields.Float('Hóa đơn thực tế', digits=(20, 0), compute='_sky_compute_all_value')

    forecast_ids = fields.One2many('sky.crm.team.forecast', 'team_id')


crm_case_section()