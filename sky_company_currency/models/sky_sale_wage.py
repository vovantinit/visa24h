# -*- coding: utf-8 -*-
import json
import calendar
from openerp import models, fields, api, _
from openerp.osv import osv, fields as osv_fields
from datetime import date
from dateutil import relativedelta
from openerp import tools
from openerp.tools.float_utils import float_repr
import openerp.addons.decimal_precision as dp
from lxml import etree
from openerp.exceptions import ValidationError

class sky_sale_wage(models.Model):
    _name = 'sky.sale.wage'
    _order = 'create_date desc'

    name        = fields.Char('Name')
    line_ids    = fields.One2many('sky.sale.wage.line', 'sale_wage_id', 'Wage lines')

    @api.multi
    def get_sale_wage(self, value):
        self.ensure_one()
        for line in self.line_ids:
            if value >= line.wage_from and (not line.wage_to or value < line.wage_to):
                return line.wage_value * value / 100.00
        return 0

sky_sale_wage()

class sky_sale_wage_line(models.Model):
    _name = 'sky.sale.wage.line'
    _order = 'wage_from asc, wage_to asc'

    # @api.onchange('wage_from', 'wage_to') 
    # def check_time_range(self):
    #     line_ids = self.search_read([('sale_wage_id', '=', self.sale_wage_id.id)], ['wage_from', 'wage_to'])
    #     for line in line_ids:
    #         if self.wage_from >= line['wage_from'] and self.wage_from < line['wage_to']: 
    #             raise ValidationError(_('Overlap period!'))
    #         if self.wage_to > line['wage_from'] and self.wage_to < line['wage_to']: 
    #             raise ValidationError(_('Overlap period!'))

    sale_wage_id    = fields.Many2one('sky.sale.wage', 'Sale wage')
    wage_from       = fields.Float('Từ lớn hơn hoặc bằng', digits=(20, 0))
    wage_to         = fields.Float('Đến nhỏ hơn', digits=(20, 0))
    wage_value      = fields.Float('Được hưởng (%)', digits=(3, 2))

sky_sale_wage_line()

class crm_case_section(models.Model):
    _inherit = 'crm.case.section'

    wage_for_manager_id     = fields.Many2one('sky.sale.wage', 'Cho trưởng phòng')
    wage_for_saleperson_id  = fields.Many2one('sky.sale.wage', 'Cho nhân viên')

    @api.multi
    def get_sale_wage_for_sale_person(self, wage):
        self.ensure_one()
        if not self.wage_for_saleperson_id:
            return 0
        return self.wage_for_saleperson_id.get_sale_wage(wage)

    @api.multi
    def get_sale_wage_for_manager(self, wage):
        self.ensure_one()
        if not self.wage_for_manager_id:
            return 0
        return self.wage_for_manager_id.get_sale_wage(wage)

crm_case_section()
