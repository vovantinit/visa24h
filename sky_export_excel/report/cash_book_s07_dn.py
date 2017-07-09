# -*- coding: utf-8 -*-
##############################################################################
#
#    @package to_vn_legal_financial_reports TO Vietnam Legal Financial Reports for Odoo 8.0
#    @copyright Copyright (C) 2015 T.V.T Marine Automation (aka TVTMA). All rights reserved.#
#    @license http://www.gnu.org/licenses GNU Affero General Public License version 3 or later; see LICENSE.txt
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
from openerp.osv import osv
from openerp import api
from openerp.report import report_sxw
    
class report_cashbook_s07_dn(osv.AbstractModel):
    _name = 'report.sky_export_excel.report_cashbook_s07_dn'
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        account_obj = self.env['account.account']    
        report = report_obj._get_report_from_name('sky_export_excel.report_cashbook_s07_dn')
        docargs = {
            'doc_ids': data['ids'],
            'report': self.env[report.model],
            'docs': account_obj.browse(data['ids']),
            'data': data,
            'rml_parser': report_sxw.rml_parse(self._cr, self._uid, 'report_cashbook_s07_dn', context=self._context),
        }
        return report_obj.render('sky_export_excel.report_cashbook_s07_dn', docargs)
