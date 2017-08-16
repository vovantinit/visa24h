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

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    @api.multi
    @api.depends('move_line_id')
    def _sky_compute_purchase_id(self):
        Invoice = self.env['account.invoice']
        for record in self:
            if not record.move_line_id:
                record.sky_purchase_id = False
            else:
                invoices = Invoice.search([('origin', 'ilike', 'PO%%'), ('move_id', '=', record.move_line_id.move_id.id)])
                record.sky_purchase_id = invoices and invoices.mapped('origin')[0] or ''

    sky_purchase_id = fields.Char(string='PO#', compute='_sky_compute_purchase_id')

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def sky_uncheck_line_dr_ids(self):
        self.mapped('line_dr_ids').write({
            'reconcile': False,
            'amount': 0,
        })

    @api.multi
    def sky_del_line_dr_ids(self):
        self.mapped('line_dr_ids').filtered(lambda r: not r.reconcile).unlink()

    @api.multi
    def sky_uncheck_line_cr_ids(self):
        self.mapped('line_cr_ids').write({
            'reconcile': False,
            'amount': 0,

        })

    @api.multi
    def sky_del_line_cr_ids(self):
        self.mapped('line_cr_ids').filtered(lambda r: not r.reconcile).unlink()