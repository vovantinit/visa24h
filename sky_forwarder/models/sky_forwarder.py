# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from lxml import etree
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import time
import datetime


class ResUsers(models.Model):
    _inherit = 'res.users'

    location_ids = fields.Many2many('sky.location', 'sky_users_location_rel', 'user_id', 'location_id', string='Địa điểm')

class SkyLocation(models.Model):
    _name = 'sky.location'

    name        = fields.Char('Location name', required=True)
    is_start    = fields.Boolean('Là địa điểm bắt đầu')
    user_ids    = fields.Many2many('res.users', 'sky_users_location_rel', 'location_id', 'user_id', string='Nhân viên')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name must be unique!')
    ]

class LocationCost(models.Model):
    _name = 'sky.location.cost'
    _order = 'from_location_id asc'


    from_location_id    = fields.Many2one('sky.location', string='From location', required=True)
    to_location_id      = fields.Many2one('sky.location', string='To location', required=True)
    value               = fields.Float(string='Cost', digit=(6, 2), required=True)


    _sql_constraints = [
        ('location_uniq', 'unique (from_location_id, to_location_id)', 'The location to location must be distinct!')
    ]

class Forwarder(models.Model):
    _name = 'sky.forwarder'
    _description = "Giao nhận"
    _inherit = ['mail.thread']
    _order = 's_date desc'

    @api.depends('from_location_id', 'to_location_id')
    def compute_forwarder_cost(self):
        if self.from_location_id and self.to_location_id:
            location_cost = self.env['sky.location.cost'].search([('from_location_id', '=', self.from_location_id.id), ('to_location_id', '=', self.to_location_id.id)], limit=1)
            if not location_cost:
                raise ValidationError(_('Chi phí chưa được thiết lập!'))
            if location_cost:
                self.forwarder_cost = location_cost.value
        else:
            self.forwarder_cost = 0

    # @api.model
    # def create(self, vals):
    #     if vals.get('forwarder_id', False):
    #         vals['state'] = 'set_forwarder'
    #     return super(Forwarder, self).create(vals)

    # @api.multi
    # def write(self, vals):
    #     if vals.get('forwarder_id', False) and len(self) == 1:
    #         if self.state == 'new':
    #             vals['state'] = 'set_forwarder'
    #     return super(Forwarder, self).write(vals)


    @api.multi
    @api.depends('forwarder_id', 'payment_id.state', 'invoice_id.state', 'cancel', 'delivered', 'value')
    def _compute_state(self):
        for record in self:
            state = 'new'
            if record.cancel:
                state = 'cancel'
            elif record.forwarder_id:
                state = 'set_forwarder'
                if record.delivered:
                    state = 'delivered'
                    if record.value < 10 or (record.payment_id and record.payment_id.state == 'posted'):
                        state = 'get_money'
                        if record.invoice_id and record.invoice_id.state == 'paid':
                            state = 'done'
            record.state = state

    # @api.multi
    # @api.depends('order_ids.partner_id')
    # def _compute_partner_id(self):
    #     for record in self:
    #         if len(record.order_ids.mapped('partner_id')) > 1:
    #             raise ValidationError(_('All orders must have the same partner!'))
    #         if len(record.order_ids.mapped('partner_id')):
    #             if record.partner_id != record.order_ids[0].partner_id:
    #                 record.address = record.order_ids[0].partner_id.with_context(show_address_only=1).name_get()[0][1] or ''
    #             record.partner_id = record.order_ids[0].partner_id
    #         else:
    #             record.partner_id = False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.address    = self.partner_id.with_context(show_address_only=1).name_get()[0][1] or ''
            if self.partner_id.phone:
                self.phone = self.partner_id.phone
            elif self.partner_id.mobile:
                self.phone = self.partner_id.mobile

    state           = fields.Selection([('new', 'New'),
                                        ('set_forwarder', 'Set forwarder user'),
                                        ('delivered', 'Delivered'),
                                        ('get_money', 'Payment paid'), 
                                        ('done', 'Done'),
                                        ('cancel', 'Cancel'),], 'State', compute='_compute_state', store=True)

    @api.onchange('user_id')
    def onchange_forwarder_id(self):
        if self.user_id and self.user_id.location_ids:
            self.from_location_id = self.user_id.location_ids[0].id

    name            = fields.Char('Name', required=True, copy=False, readonly=True, size=10)
    # partner_id      = fields.Many2one('res.partner',string='Customer', domain=[('customer','=',True)], compute='_compute_partner_id', store=True)
    partner_id      = fields.Many2one('res.partner',string='Customer', domain=[('customer','=',True)])
    user_id         = fields.Many2one('res.users', 'User offer', required=True, track_visibility='onchange')
    forwarder_id    = fields.Many2one('res.users', 'Forwarder user', track_visibility='onchange')
    order_ids       = fields.Many2many('sale.order', 'sky_forwarder_sale_order_ref', 'forwarder_id', 'order_id', string='Orders')
    
    address         = fields.Text('Số nhà, đường', size=256, track_visibility='onchange')
    value           = fields.Float('Money amount', digit=(20, 2), track_visibility='onchange')    

    from_location_id    = fields.Many2one('sky.location', 'From location', domain=[('is_start','=',True)], track_visibility='onchange')
    to_location_id      = fields.Many2one('sky.location', 'To location', domain=[('is_start','=',False)], track_visibility='onchange')
    forwarder_cost      = fields.Float('Forwarder cost', digit=(6, 2), compute='compute_forwarder_cost', store=True)

    payment_id      = fields.Many2one('account.voucher', string='Customer payment')
    invoice_id      = fields.Many2one('account.invoice', string='Invoice')

    note            = fields.Text('Note', track_visibility='onchange')
    cancel          = fields.Boolean('Cancel', track_visibility='onchange')
    delivered       = fields.Boolean('Delivered', track_visibility='onchange')

    s_date          = fields.Date('Ngày đề nghị')
    s_datetime      = fields.Char('Thời gian giao nhận', track_visibility='onchange')
    real_time       = fields.Datetime('Thời gian thực tế', track_visibility='onchange')
    phone           = fields.Char('Số điện thoại')

    _defaults = {
        'name': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'sky.forwarder.code'),
    }

    @api.model
    def default_get(self, fields):
        res = super(Forwarder, self).default_get(fields)
        res['s_date'] = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        return res

    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'new' or record.payment_id or record.invoice_id:
                raise ValidationError(_("Only delete with new status!"))
        return super(Forwarder, self).unlink()

    @api.multi
    def view_payment(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.voucher",
            "views": [[self.env.ref('account_voucher.view_vendor_receipt_form').id, "form"]],
            "context": {
                'default_partner_id':   self.partner_id and self.partner_id.id or False,
                'default_reference':    self.name,
                'default_amount':       self.value,
                'default_recipient_payer':  self.forwarder_id.name,
                'no_create':               False,
            },
            "res_id": self.payment_id and self.payment_id.id or False,
        }

    @api.multi
    def view_invoice(self):
        self.ensure_one()
        if not self.forwarder_id:
            raise ValidationError(_('The forwarder user have been not setup!'))
        if not self.order_ids:
            raise ValidationError(_('Not found SO!'))
        if not self.forwarder_cost:
            raise ValidationError(_('Forwarder cost have been not setup!'))
        product_id = self.env.ref('__export__.product_template_72')
        price_unit = self.forwarder_cost / len(self.order_ids)
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "views": [[self.env.ref('account.invoice_supplier_form').id, "form"]],
            "context": {
                'default_type': 'in_invoice', 
                'type': 'in_invoice', 
                'journal_type': 'purchase',
                'default_partner_id': self.forwarder_id.partner_id.id,
                'default_origin': self.name,
                'default_invoice_line': [(0, 0, {
                    'name': self.name + ' ' + order.name,
                    'product_id': product_id.id,
                    'order_id': order.id,
                    'account_analytic_id': order.analytic_account_id and order.analytic_account_id.id or False,
                    'quantity': 1,
                    'price_unit': price_unit,
                    'account_id': product_id.property_account_expense and product_id.property_account_expense.id or False,
                }) for order in self.order_ids] if not self.invoice_id else [],
            },
            "res_id": self.invoice_id and self.invoice_id.id or False,
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Forwarder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type in ('form', 'tree') and not self.env['res.users'].has_group('sky_forwarder.group_forwarder_user') :
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='forwarder_id']"):
                node.set('modifiers', '{"readonly": "1"}')
            for node in doc.xpath("//field[@name='delivered']"):
                node.set('modifiers', '{"readonly": "1"}')
            res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def button_cancel(self):
        self.write({'cancel': True})


Forwarder()


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.model
    def create(self, vals):
        res = super(AccountVoucher, self).create(vals)
        if self._context.get('active_model', False) == 'sky.forwarder':
            forwarder = self.env['sky.forwarder'].browse(self._context.get('active_id'))
            if forwarder.payment_id:
                raise ValidationError(_('Have been payment'))
            forwarder.write({'payment_id': res.id})
        return res

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if self._context.get('active_model', False) == 'sky.forwarder':
            forwarder = self.env['sky.forwarder'].browse(self._context.get('active_id'))
            if forwarder.invoice_id:
                raise ValidationError(_('Have been invoice!'))
            forwarder.write({'invoice_id': res.id})
        return res