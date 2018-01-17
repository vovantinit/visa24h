# -*- coding: utf-8 -*-
##############################################################################
#
#    @package sky_xxx Ten Module Odoo 10.0
#    @copyright Copyright (C) 2016 Sky ERP Company Limited. All rights reserved.#
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
{
    'name': 'Quick search in List view',
    'version': '8.0.0.1',
    'category': 'web',
    "sequence": 5,
    'summary': 'Quick search in List view',
    'description': """
Quick search in List view
=============================
    """,
    'author': 'SkyERP team',
    'website': 'https://www.skyerp.net',
    'images': [],
    'depends': ['web'],
    'data': [
        'views/sky_template.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
