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
    'name': 'Module Biên nhận hồ sơ',
    'version': '1.0.1',
    'category': 'Freelance ERP',
    "sequence": 5,
    'summary': 'Module Biên nhận hồ sơ',
    'complexity': "easy",
    'description': """
        Module Biên nhận hồ sơ.
    """,
    'author': 'Vo Van Tin',
    'website': 'https://www.facebook.com/vovantinit',
    'images': [],
    'depends': ['sky_company_currency', 'website_quote'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/bien_nhan_ho_so_view.xml',
        'views/mau_in_bien_nhan.xml',
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
