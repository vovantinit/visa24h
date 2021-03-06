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
    'name': 'Check result for multi SO',
    'version': '1.0.1',
    'category': 'SkyERP',
    "sequence": 5,
    'summary': 'Check result for multi SO',
    'complexity': "easy",
    'description': """
        Check result for multi SO
    """,
    'author': 'SkyERP Team',
    'website': 'https://www.skyerp.net',
    'images': [],
    'depends': ['sky_company_currency'],
    'data': [
        'wizard/sky_result_multi_so_view.xml',
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
