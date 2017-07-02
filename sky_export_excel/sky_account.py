# -*- coding: utf-8 -*-
from openerp import api, fields, models
from cStringIO import StringIO

class Account(models.Model):
    _inherit = 'account.account'

    @api.model
    def get_current_balance(self, date_from, date_to, data, target_move):
        ids_acc = self._get_children_and_consol()
        obj_move = self.env['account.move.line']

        opening_balance = self.get_report_opening_balance(data)

        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted', '']

        query = " AND l.date >= '{}' AND l.date <= '{}'".format(date_from, date_to)


        self._cr.execute('''SELECT sum(l.debit-l.credit) sum_balance
                FROM account_move_line l 
                JOIN account_move m ON (m.id = l.move_id) 
                JOIN account_period p ON (p.id=l.period_id) 
                WHERE (l.account_id IN %s) 
                AND (m.state IN %s) \
                AND p.special = FALSE ''' + query, (tuple(ids_acc), tuple(move_state)))
        sum_balance = self._cr.fetchone()[0] or 0.0
        return opening_balance + sum_balance

    @api.model
    def _report_opening_balance_nt(self, account, data):        
        move_state = ['draft', 'posted']
        fiscalyear_obj = self.env['account.fiscalyear']
        fiscalperiod_obj = self.env['account.period']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted', '']
        
        if data['form']['fiscalyear_id']:
            fiscalyear_ids = [data['form']['fiscalyear_id']]
        else:
            fiscalyear_ids = fiscalyear_obj.search([])
        fiscalyear_clause = (','.join([str(x) for x in fiscalyear_ids])) or '0'
            
        sum_balance = 0
        sql = """
                SELECT sum(amount_currency) as tot_balance
                    FROM account_move_line l
                    JOIN account_move am ON (am.id = l.move_id)
                    JOIN account_period p ON (l.period_id = p.id)
                    WHERE (l.account_id = %s)
                    AND (am.state IN %s)
                    AND (p.special = TRUE)
                    AND (p.fiscalyear_id IN (%s))
            """
        self._cr.execute(sql, (account.id, tuple(move_state), fiscalyear_clause))
        sum_balance = self._cr.fetchone()[0] or 0.0
            
        if data['form']['filter'] == 'filter_date':
            sql = """
                SELECT sum(amount_currency) as tot_balance
                    FROM account_move_line l
                    JOIN account_move am ON (am.id = l.move_id)
                    JOIN account_period p ON (l.period_id = p.id)
                    WHERE (l.account_id = %s)
                    AND (am.state IN %s)
                    AND (p.special = FALSE)
                    AND (l.date < %s)
                    AND (p.fiscalyear_id IN (%s))
            """
            self._cr.execute(sql, (account.id, tuple(move_state), data['form']['date_from'], fiscalyear_clause))        
            sum_balance += self._cr.fetchone()[0] or 0.0        
        
        if data['form']['filter'] == 'filter_period':            
            period_company_id = fiscalperiod_obj.browse(data['form']['period_from']).company_id.id
            first_period = fiscalperiod_obj.search([('company_id', '=', period_company_id)], order='date_start', limit=1)[0]            
            periods = fiscalperiod_obj.build_ctx_periods(first_period.id, data['form']['period_from'])
            
            if len(periods) > 2:
                del periods[-1]
                sql = """
                    SELECT sum(amount_currency) as tot_balance
                        FROM account_move_line l
                        JOIN account_move am ON (am.id = l.move_id)
                        JOIN account_period p ON (l.period_id = p.id)
                        WHERE (l.account_id = %s)
                        AND (am.state IN %s)
                        AND (p.special = FALSE)
                        AND (l.period_id IN %s)
                        AND (p.fiscalyear_id IN (%s))
                """
                self._cr.execute(sql, (account.id, tuple(move_state), tuple(periods), fiscalyear_clause))
                sum_balance += self._cr.fetchone()[0] or 0.0              
                 
        return sum_balance


    @api.model
    def get_report_opening_balance_nt(self, data):
        value = 0
        for item in self.get_report_children_account():
            value += self._report_opening_balance_nt(item, data)
        return value

    @api.model
    def get_current_balance_nt(self, date_from, date_to, data, target_move):
        ids_acc = self._get_children_and_consol()
        obj_move = self.env['account.move.line']

        opening_balance = self.get_report_opening_balance_nt(data)

        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted', '']

        query = " AND l.date >= '{}' AND l.date <= '{}'".format(date_from, date_to)


        self._cr.execute('''SELECT sum(l.amount_currency) sum_balance
                FROM account_move_line l 
                JOIN account_move m ON (m.id = l.move_id) 
                JOIN account_period p ON (p.id=l.period_id) 
                WHERE (l.account_id IN %s) 
                AND (m.state IN %s) \
                AND p.special = FALSE ''' + query, (tuple(ids_acc), tuple(move_state)))
        sum_balance = self._cr.fetchone()[0] or 0.0
        return opening_balance + sum_balance