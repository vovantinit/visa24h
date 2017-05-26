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
    'name': 'Sky HR Contract',
    'version': '1.0.1',
    'category': 'Freelance ERP',
    "sequence": 5,
    'summary': 'None',
    'complexity': "easy",
    'description': """
        Termination contract.
    """,
    'author': 'Vo Van Tin',
    'website': 'https://www.facebook.com/vovantinit',
    'images': [],
    'depends': ['visa_tinhluong', 'sky_company_currency'],
    'data': [
        'views/sky_hr_contract_view.xml',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],        
    'test': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
