# -*- coding: utf-8 -*-
import json
import calendar
from openerp import models, fields, api
from openerp.osv import osv, fields as osv_fields
from datetime import date
from dateutil import relativedelta
from openerp import tools
from openerp.tools.float_utils import float_repr
import openerp.addons.decimal_precision as dp
from lxml import etree
from openerp.exceptions import ValidationError

class sale_report(models.Model):
    _inherit = 'sale.report'

    product_category_id     = fields.Many2one('product.category', string='Nhóm sản phẩm',)
    product_product_id      = fields.Many2one('product.product', string='Sản phẩm')
    acc_analytic_debit      = fields.Float('Doanh thu')
    acc_analytic_credit     = fields.Float('Chi Phí')
    acc_analytic_balance    = fields.Float('Lợi nhuận ròng')
    x_ngaytinhdoanhso       = fields.Date('Ngày tính doanh số')
    sale_wage               = fields.Float('Thưởng doanh số')
    block                   = fields.Selection([('y', 'Đã tính doanh số'), ('n', 'Chưa tính doanh số')], 'Chốt doanh số')

    def list_periods(self, cr, uid, context=None):
        ids = self.pool.get('account.period').search_read(cr,uid,[],['date_start', 'date_stop', 'name'])
        return ids

    def _select(self):
        select_str = super(sale_report, self)._select()
        add_fields = '''
            ,s.product_category_id,
            s.product_product_id,
            s.acc_analytic_debit,
            s.acc_analytic_credit,
            s.acc_analytic_balance,
            s.x_ngaytinhdoanhso,
            0 sale_wage,            
            CASE WHEN s.block THEN 'y' ELSE 'n' END AS block
        '''
        return select_str + add_fields

    def _group_by(self):
        group_by_str = super(sale_report, self)._group_by()
        add_groups = '''
            ,s.product_category_id,
            s.product_product_id,
            s.acc_analytic_debit,
            s.acc_analytic_credit,
            s.acc_analytic_balance,
            s.x_ngaytinhdoanhso,
            sale_wage,
            block
        '''
        return group_by_str + add_groups
        
    def _get_sale_wage_of_manager(self, res, domain):
        domain = [d for d in domain if d[0] != 'user_id']
        result = 0
        for r in res:
            d = [d for d in r['__domain'] if d[0] != 'user_id']
            if domain == d:
                result += r['acc_analytic_balance']
        return result

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False,lazy=True):
        # print 
        # print 'domain', domain
        # print 'fields', fields
        # print 'groupby', groupby
        # print 'orderby', orderby
        # print 'context', context
        res = super(sale_report, self).read_group(cr, uid, domain, fields, groupby, offset, limit, context, orderby,lazy)
        if 'user_id' in groupby and len(groupby) > 2:
            Team = self.pool['crm.case.section']
            Wage = self.pool['sky.sale.wage']
            for r in res:
                if 'user_id' not in r: 
                    continue
                if 'section_id' in r:
                    section_id = r['section_id'] and r['section_id'][0]
                else:
                    section_id = [i for i in r['__domain'] if i[0] == 'section_id']
                    section_id = section_id and section_id[0][2] or False
                if not section_id:
                    continue
                sale_team   = Team.browse(cr, uid, section_id)
                wage        = False
                sale_wage   = 0
                if sale_team.user_id and sale_team.user_id.id == r['user_id'][0]:
                    wage = sale_team.wage_for_manager_id
                    sale_wage = self._get_sale_wage_of_manager(res, r['__domain'])
                else:
                    wage = sale_team.wage_for_saleperson_id
                    if 'acc_analytic_balance' in r:
                        sale_wage   = r['acc_analytic_balance']

                
                r['sale_wage'] = wage and wage.get_sale_wage(sale_wage) or 0
        return res
