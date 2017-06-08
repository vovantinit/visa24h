# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################

from openerp.osv import fields, osv
from openerp import api
import json


class account_partner_balance(osv.osv_memory):
    
    _inherit = 'account.partner.balance'

    @api.multi
    def check_report(self):
        context = self._context
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'])[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(data)

        min_date = ''
        if self.filter == 'filter_date':
            min_date = self.date_from
        elif self.filter == 'filter_period':
            min_date = self.period_from.date_start

        w_context = {
            'result_selection': self.result_selection,
            'target_move': self.target_move,
            'display_partner': self.display_partner,
            'filter': self.filter,
            'min_date': min_date,
        }

        return {
            'type': 'ir.actions.act_url',
            'url': '/skyerp/account_report_partner_balance?context={}&w_context={}'.format(json.dumps(used_context), json.dumps(w_context)),
            'target': 'new',
            'destroy': True,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
