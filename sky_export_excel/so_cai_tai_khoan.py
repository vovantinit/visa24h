# -*- coding: utf-8 -*-
from openerp import api, fields, models
from cStringIO import StringIO
import xlsxwriter
from datetime import datetime

def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def tgl_check_report_xls(self, data, account):
    res = self[account].get_report_move_lines(data)

    # Xu ly Excel 

    f_font_red      = {'font_color': 'red'}
    f_bold          = {'bold': True}
    f_italic        = {'italic': True}
    f_border        = {'border': 1}
    f_align_left    = {'align':'left'}
    f_align_right   = {'align':'right'}
    f_align_center  = {'align':'center'}
    f_wrap    = {'text_wrap': True}
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
            'field_name': 'lref',
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
            'size': 20,
            'field_name': 'amount_currency_sum',
            'format': merge_dicts(f_num_format, f_font_red),
        },
        {
            'label': u'Người nhận/ Người nộp',
            'size': 22,
            'field_name': 'partner_v2',
        },
        {
            'label': u'Số tồn',
            'size': 20,
            'field_name': 'progress_v2',
            'format': merge_dicts(f_num_format, f_font_red),
        },
    ]

    rows = 0
    amount_currency = 0

    currency_obj = self.env['res.currency']
    from_currency             = currency_obj.browse(24)
    to_currency           = self[account].currency_id or from_currency

    init_balance = self[account].get_report_opening_balance(data)
    amount_currency_sum = from_currency.with_context(date=data['form']['used_context']['date_from']).compute(init_balance, to_currency, round=True)
    # self.cash_account.get_report_opening_balance_nt(data)


    output = StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(u'Sổ quỹ')

    tgl_format = workbook.add_format
    worksheet.set_row(rows, 50)

    for index, val in enumerate(header_value):
        worksheet.write(rows, index, val.get('label', ''), tgl_format(merge_dicts(f_bold, f_border, f_align_center, f_background)))
        worksheet.set_column(index, index, val.get('size', 15), tgl_format({'font_name': 'Times New Roman'}))
    
        # Ghi dau ki
        worksheet.write(rows+1, index, '', tgl_format(f_border))
        if val.get('field_name') == 'move_narration':
            worksheet.write(rows+1, index, u'Số dư đầu kỳ', tgl_format(merge_dicts(f_border, val.get('format', {}))))
        if val.get('field_name') == 'progress_v2':
            worksheet.write(rows+1, index, init_balance, tgl_format(merge_dicts(f_border, val.get('format', {}))))
        if val.get('field_name') == 'amount_currency_sum':
            worksheet.write(rows+1, index, amount_currency_sum, tgl_format(merge_dicts(f_border, val.get('format', {}))))

    rows += 1 

    i = -1

    Payment = self.env['account.voucher']
    MoveLine = self.env['account.move.line']

    for line in res:
        i += 1
        line['progress_v2'] = ''
        line['amount_currency_sum'] = ''
        if i == len(res)-1 or line['ldate'] != res[i+1]['ldate']:
            line['progress_v2'] = self[account].get_current_balance(data['form']['date_from'], line['ldate'], data, self.target_move)
            line['amount_currency_sum'] = from_currency.with_context(date=line['ldate']).compute(line['progress_v2'], to_currency, round=True)
            # self.cash_account.get_current_balance_nt(data['form']['date_from'], line['ldate'], data, self.target_move)
        line['ldate'] = datetime.strptime(line['ldate'], '%Y-%m-%d').strftime('%d/%m/%Y')
        p_id = Payment.search([('move_ids','in',line['lid'])], limit=1)
        line['partner_v2'] = p_id and p_id.recipient_payer or line['partner']
        # line['move_narration'] = p_id and p_id.reference or line['move_narration']

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


class to_cash_book_s03_dn(models.Model):
    _inherit = 'to.so.cai.tk.s03b.dn'

    @api.model
    def check_report_xls(self, data):
        return tgl_check_report_xls(self, data, 'account')

    @api.multi
    def _print_report(self, data):
        if self._context.get('print_excel', False):
            data = self.pre_print_report(data)
            return self.check_report_xls(data)
        else:
            return super(to_cash_book_s03_dn, self)._print_report(data)


class to_cash_book_s07_dn(models.Model):
    _inherit = 'to.cash.book.s07dn'

    @api.model
    def check_report_xls(self, data):
        return tgl_check_report_xls(self, data, 'cash_account')

    @api.multi
    def _print_report(self, data):
        data = self.pre_print_report(data)
        if self._context.get('print_excel', False):
            return self.check_report_xls(data)
        else:
            return super(to_cash_book_s07_dn, self)._print_report(data)
            # return self.env['report'].with_context(landscape=True).get_action(self, 'sky_export_excel.report_cashbook_s07_dn', data=data)