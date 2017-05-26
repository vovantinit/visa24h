# -*- coding: utf-8 -*-
from openerp import fields,models,api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_round

class close_analytic_account(models.TransientModel):
    _inherit = 'close.analytic.account'

    @api.multi
    def action_close_period(self):
        super(close_analytic_account, self).action_close_period()
        Order       = self.env['sale.report']
        domain      =  [# ('block', '=', True),
                        ('x_ngaytinhdoanhso', '!=', False), 
                        ('x_ngaytinhdoanhso', '>=', self.period_id.date_start),
                        ('x_ngaytinhdoanhso', '<=', self.period_id.date_stop)]

        # For Employee

        contract_ids    = []

        groupby     = ['user_id']
        fields      = ['user_id', 'acc_analytic_balance', 'sale_wage']
        res         = Order.read_group(domain=domain, fields=fields, groupby=groupby, offset=0, limit=None, context=self._context, orderby=False, lazy=True)
        
        Team        = self.env['crm.case.section']
        Contract    = self.env['hr.contract']

        for order in res:
            if not order['user_id']: continue
            contract    = Contract.search([('employee_id.user_id', '=', order['user_id'][0])])
            section     = Team.search([('member_ids', 'in', order['user_id'][0])], limit=1)
            wage        = 0
            if contract and section and section.user_id and section.user_id.id != order['user_id'][0]:
                wage    = section.get_sale_wage_for_sale_person(order['acc_analytic_balance'])
                wage    = float_round(wage, 2)
                contract.write({'luong_doanh_so': wage})
                contract_ids.append(contract.mapped('id'))
                body    = u'Lương doanh số {} - {}'.format(self.period_id.name, wage) 
                contract.message_post(body=body)
            # print order['user_id'], order['acc_analytic_balance'], wage

        # For manager
        groupby     = ['section_id']
        fields      = ['section_id', 'acc_analytic_balance']
        res         = Order.read_group(domain=domain, fields=fields, groupby=groupby, offset=0, limit=None, context=self._context, orderby=False, lazy=True)

        for order in res:
            if not order['section_id']: continue
            section = Team.browse(order['section_id'][0])
            if not section.user_id: continue
            wage        = section.get_sale_wage_for_manager(order['acc_analytic_balance'])
            wage        = float_round(wage, 2)
            contract    = Contract.search([('employee_id.user_id', '=', section.user_id.id)])
            if contract:
                contract.write({'luong_doanh_so': wage})
                contract_ids.append(contract.mapped('id'))
                body    = u'Lương doanh số {} - {}'.format(self.period_id.name, wage) 
                contract.message_post(body=body)

            # print order['section_id'], order['acc_analytic_balance'], wage

        contract_ids = Contract.search([('id', 'not in', contract_ids)])
        contract_ids.write({'luong_doanh_so': 0})
        body    = u'Lương doanh số {} - {}'.format(self.period_id.name, 0) 
        for contract in contract_ids:
            contract.message_post(body=body)


