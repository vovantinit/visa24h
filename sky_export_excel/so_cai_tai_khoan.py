# -*- coding: utf-8 -*-
from openerp import api, fields, models
from cStringIO import StringIO
import xlsxwriter

def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

class to_cash_book_s07_dn(models.Model):
    _inherit = 'to.so.cai.tk.s03b.dn'


    @api.multi
    def check_report_xls(self):
        context = self._context
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'])[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(data)

        date_from = False
        date_to = False
        if self.filter == 'filter_date':
            date_from   = self.date_from
            date_to     = self.date_to
        elif self.filter == 'filter_period':
            date_from = self.period_from and self.period_from.date_start or False
            date_to =   self.period_to and self.period_to.date_stop or False

        wizard_context = {
            'target_move': self.target_move,
            'filter': self.filter,
            'account_id': self.account.id,
        }

        obj_move = self.env['account.move.line']

        account_id = wizard_context.get('account_id', False)

        query = obj_move.with_context(used_context)._query_get(obj='l')        

        move_state = ['draft','posted']
        if wizard_context.get('target_move', False) == 'posted':
            move_state = ['posted', '']

        init_balance = 0
        amount_currency = 0
        if date_from:
            add_where = " AND l.date < '{}'".format(date_from)
        
            init_sql = """
                SELECT sum(debit-credit) balance, sum(amount_currency) amount_currency
                FROM account_move_line l 
                LEFT JOIN account_move am ON (am.id = l.move_id)
                WHERE am.state in %s and l.account_id = %s 
            """ % (tuple(move_state), account_id)

            self.env.cr.execute(init_sql + add_where)
            tmp = self.env.cr.dictfetchall()
            init_balance    = tmp and tmp[0]['balance'] or 0
            amount_currency = tmp and tmp[0]['amount_currency'] or 0

        add_where = ''
        if date_from:
            add_where += " AND l.date >= '{}'".format(date_from)
        if date_to:
            add_where += " AND l.date <= '{}'".format(date_to)

        sql = """
            SELECT l.move_id
            FROM account_move_line l
            LEFT JOIN account_move am ON (am.id = l.move_id)
            WHERE am.state IN %s AND l.account_id = %s GROUP BY l.date, l.move_id
            ORDER BY l.date ASC
        """ % (tuple(move_state), account_id)
        self.env.cr.execute(sql)
        account_moves = self.env.cr.dictfetchall()

        res_lines = []
        for item in account_moves:
            # Then select all account_move_line of this account            
            sql_sort = 'l.date, l.move_id'
            sql = """
                SELECT l.id AS lid, l.date AS ldate, m.name AS mname, j.code AS lcode, l.currency_id,l.amount_currency,l.ref AS lref, l.name AS lname, a.code AS lcode,
                    CASE 
                        WHEN (SELECT count(*) FROM account_move_line WHERE account_id <> %%s AND move_id = %%s
                            AND CASE WHEN (SELECT sum(debit) from account_move_line where account_id = %%s and move_id = %%s and (debit <> 0 or credit <> 0)) > 0 THEN credit > 0 ELSE debit > 0 END) > 1
                        THEN 
                            COALESCE(l.credit,0)
                        ELSE
                            (SELECT sum(debit) from account_move_line where account_id = %%s and move_id = %%s and (debit <> 0 or credit <> 0))
                    END AS debit,
                    CASE 
                        WHEN (SELECT count(*) FROM account_move_line WHERE account_id <> %%s AND move_id = %%s
                            AND CASE WHEN (SELECT sum(debit) from account_move_line where account_id = %%s and move_id = %%s and (debit <> 0 or credit <> 0)) > 0 THEN credit > 0 ELSE debit > 0 END) > 1 
                        THEN 
                            COALESCE(l.debit,0)
                        ELSE
                            (SELECT sum(credit) from account_move_line where account_id = %%s and move_id = %%s and (debit <> 0 or credit <> 0))
                    END AS credit,
                    l.partner_id AS lpartner_id,
                    m.name AS move_name, m.id AS mmove_id, m.ref AS move_narration,
                    i.id AS invoice_id, i.type AS invoice_type, i.number AS invoice_number,
                    p.name AS partner_name
                    FROM account_move_line l
                    JOIN account_move m on (l.move_id=m.id)
                    LEFT JOIN res_partner p on (l.partner_id=p.id)
                    LEFT JOIN account_invoice i on (m.id =i.move_id)
                    JOIN account_journal j on (l.journal_id=j.id)
                    JOIN account_account a on (l.account_id=a.id)                    
                    WHERE 1=1 %s AND m.state IN %s AND l.account_id <> %%s and l.move_id = %%s
                    AND CASE WHEN (SELECT sum(debit) from account_move_line where account_id = %%s and move_id = %%s and (debit <> 0 or credit <> 0)) > 0 THEN l.credit > 0 ELSE l.debit > 0 END                 
                    ORDER BY %s
            """ % (add_where, tuple(move_state), sql_sort)

            self.env.cr.execute(sql, (account_id, item['move_id'], 
                                  account_id, item['move_id'], 
                                  account_id, item['move_id'], 
                                  account_id, item['move_id'], 
                                  account_id, item['move_id'], 
                                  account_id, item['move_id'],
                                  account_id, item['move_id'],
                                  account_id, item['move_id']))
            res_lines += self.env.cr.dictfetchall()  
        
        return self.sky_export_excel(res_lines, init_balance, amount_currency)

    @api.model
    def sky_export_excel(self, data, init_balance, amount_currency):

        # Xu ly du lieu
        during_debit = 0
        during_credit = 0
        account_sum = 0
        amount_currency_sum = 0

        for l in data:                        
            if l['debit'] == None:
                l['debit'] = 0
            if l['credit'] == None:
                l['credit'] = 0
            l['move'] = l['move_name'] != '/' and l['move_name'] or ('*' + str(l['mmove_id']))
            l['partner'] = l['partner_name'] or ''
            l['line_corresp'] = l['mmove_id'] == '' and ' ' or l['lcode']
            l['ldate'] = fields.Date.from_string(l['ldate']).strftime('%d/%m/%Y')

            during_debit += l['debit']
            during_credit += l['credit']

            account_sum += (l['debit'] or 0.0) - (l['credit'] or 0.0)            
            l['progress'] = account_sum + init_balance

            amount_currency_sum += l['amount_currency']
            l['amount_currency_sum'] = amount_currency - amount_currency_sum

        end_balance = during_debit - during_credit + init_balance


        # Xu ly Excel 

        f_font_red      = {'font_color': 'red'}
        f_bold          = {'bold': True}
        f_italic        = {'italic': True}
        f_border        = {'border': 1}
        f_align_left    = {'align':'left'}
        f_align_right   = {'align':'right'}
        f_align_center  = {'align':'center'}
        f_num_format    = {'num_format': '#,##0.00'}
        f_background    = {'bg_color': '#f5f5f5'}


        header_value = [
            {
                'label': u'Ngày\nchứng từ',
                'size': 12,
                'field_name': 'ldate',
                'format': f_align_center,
            },
            {
                'label': u'Số phiếu thu',
                'size': 16,
                'field_name': 'mname',
                'domain': "line['debit'] > 0",
                'main_val': 'line.get(field_name)',
                'placeholder': '',
                'format': f_align_center,
            },
            {
                'label': u'Số phiếu chi',
                'size': 16,
                'field_name': 'mname',
                'domain': "line['credit'] > 0",
                'main_val': 'line.get(field_name)',
                'placeholder': '',
                'format': f_align_center,
            },
            {
                'label': u'Diễn giải',
                'size': 30,
                'field_name': 'move_narration',
            },
            {
                'label': u'TK\nđối ứng',
                'size': 8,
                'field_name': 'line_corresp',
            },
            {
                'label': u'Số phát\nsinh Nợ\nNT',
                'size': 10,
                'field_name': 'amount_currency',
                'domain': "line['debit'] > 0",
                'main_val': 'abs(line.get(field_name))',
                'placeholder': 0,
                'format': f_num_format,
            },
            {
                'label': u'Số phát sinh Nợ',
                'size': 15,
                'field_name': 'debit',                
                'format': f_num_format,
            },
            {
                'label': u'Số phát\nsinh Có\nNT',
                'size': 10,
                'field_name': 'amount_currency',
                'domain': "line['credit'] > 0",
                'main_val': 'abs(line.get(field_name))',
                'placeholder': 0,
                'format': f_num_format,
            },
            {
                'label': u'Số phát sinh Có',
                'size': 15,
                'field_name': 'credit',
                'format': f_num_format,
            },
            {
                'label': u'Số tồn\nnguyên tệ',
                'size': 10,
                'field_name': 'amount_currency_sum',
                'format': f_num_format,
            },
            {
                'label': u'Người nhận/ Người nộp',
                'size': 22,
                'field_name': 'partner',
            },
            {
                'label': u'Số tồn',
                'size': 20,
                'field_name': 'progress',
                'format': f_num_format,
            },
        ]

        rows = 0

        output = StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('So quy')

        tgl_format = workbook.add_format
        worksheet.set_row(rows, 50)

        for index, val in enumerate(header_value):
            worksheet.write(rows, index, val.get('label', ''), tgl_format(merge_dicts(f_bold, f_border, f_align_center, f_background)))
            worksheet.set_column(index, index, val.get('size', 15), tgl_format({'font_name': 'Times New Roman'}))
        
            # Ghi dau ki
            worksheet.write(rows+1, index, '', tgl_format(f_border))
            if val.get('field_name') == 'move_narration':
                worksheet.write(rows+1, index, u'Số dư đầu kỳ', tgl_format(merge_dicts(f_border, val.get('format', {}))))
            if val.get('field_name') == 'progress':
                worksheet.write(rows+1, index, init_balance, tgl_format(merge_dicts(f_border, val.get('format', {}))))
            if val.get('field_name') == 'amount_currency_sum':
                worksheet.write(rows+1, index, amount_currency, tgl_format(merge_dicts(f_border, val.get('format', {}))))



        rows += 1 


        for line in data:
            rows += 1            
            for index, val in enumerate(header_value):
                worksheet.write(rows, index, '', tgl_format(f_border))
                field_name = val.get('field_name', '')
                if field_name in line:
                    if not val.get('domain', False):
                        worksheet.write(rows, index, line.get(field_name), tgl_format(merge_dicts(f_border, val.get('format', {}))))
                    elif eval(val.get('domain', False)):
                        worksheet.write(rows, index, eval(val.get('main_val', '')), tgl_format(merge_dicts(f_border, val.get('format', {}))))
                    else:
                        worksheet.write(rows, index, val.get('placeholder', ''), tgl_format(merge_dicts(f_border, val.get('format', {}))))

        workbook.close()
        output.seek(0)

        filename = u'SoTienMat.xlsx'

        if self.filter == 'filter_date':
            filename = u'SoTienMat_{}_{}.xlsx'.format(self.date_from and fields.Date.from_string(self.date_from).strftime('%d-%m-%Y') or '', self.date_to and fields.Date.from_string(self.date_to).strftime('%d-%m-%Y') or '')
        elif self.filter == 'filter_period':
            filename = u'SoTienMat_{}_{}.xlsx'.format(self.period_from and self.period_from.name or '', self.period_to and self.period_to.name or '')

        att_id = self.env['ir.attachment'].create({
            'name': filename,
            'datas_fname': filename,
            'datas': output.read().encode('base64'),
        })

        url = u'/web/binary/saveas?model=ir.attachment&id={}&field=datas&filename_field=datas_fname'.format(att_id.id)
        return {
             'type' : 'ir.actions.act_url',
             'url': url,
             'target': 'self',
        }             