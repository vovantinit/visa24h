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

class hr_contract(models.Model):
    _inherit = ['mail.thread', 'hr.contract']
    _name = 'hr.contract'

    active          = fields.Boolean('Active', default=True, track_visibility='onchange')
    ngaycongthang   = fields.Float(track_visibility='onchange')
    ngaycongthucte  = fields.Float(track_visibility='onchange')
    wage            = fields.Float(track_visibility='onchange')
    struct_id       = fields.Many2one(track_visibility='onchange')
    trial_date_start= fields.Date(track_visibility='onchange')
    trial_date_end  = fields.Date(track_visibility='onchange')
    date_start      = fields.Date(track_visibility='onchange')
    date_end        = fields.Date(track_visibility='onchange')
    working_hours   = fields.Many2one(track_visibility='onchange')
    schedule_pay    = fields.Selection(track_visibility='onchange')

    # Add field

    luong_doanh_so  = fields.Float(string='Lương doanh số', digits=(20,2))
    
    thuong          = fields.Float(string='Thưởng', digits=(20,2))
    tang_ca         = fields.Float(string='Tăng ca', digits=(20,2))


    @api.onchange('active')
    def onchange_active(self):
        for record in self:
            if record.employee_id:
                record.employee_id.write({'active': record.active})




hr_contract()