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

{
    'name': 'Total Order for Company Currency',
    'version': '1.0.1',
    'category': 'Freelance ERP',
    "sequence": 5,
    'summary': 'None',
    'complexity': "easy",
    'description': """
Compute ammount total of Order and Invoice for main company currency.

Add Total (VND) field after Total field in tree view of Order and Invoice.

Sum of Total (VND) same Total.

Kanban of sales team: diagram for main company currency, sum order of sales team equal total of child's team and itself.
    """,
    'author': 'Vo Van Tin',
    'website': 'https://www.facebook.com/vovantinit',
    'images': [],
    'depends': ['visa_traketqua', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sky_template.xml',
        'wizard/sky_sale_wage_for_period_view.xml',
        'views/views.xml',
        'views/sky_report_saleorder.xml',
        'views/sky_report_invoice.xml',
        'views/sky_sale_wage_view.xml',
        'report/sky_sale_report_view.xml',
    ],
    'demo': [],
    'css': [],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'js': [],        
    'test': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
