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

from openerp import http, fields
import json
from openerp.http import request, serialize_exception as _serialize_exception
from cStringIO import StringIO
from collections import deque
from datetime import datetime, timedelta
from dateutil import tz

import SimpleHTTPServer

try:
    import xlwt
except ImportError:
    xlwt = None
from xlwt import *

import xlsxwriter

class AdvanceExport(http.Controller, SimpleHTTPServer.SimpleHTTPRequestHandler):

    def tgl_write_excel(self, worksheet, rows, col, value, so_style_v2=None):
        if so_style_v2:
            worksheet.write(rows, col, value, so_style_v2)
        else:
            worksheet.write(rows, col, value)
        return col + 1


    @http.route(['/skyerp/excel_report/so'], type='http', auth="user")
    def sky_account_tax_report(self, date_from, date_to, debug=None):
        filename = u'Bao cao tong hop ban hang'

        workbook    = xlwt.Workbook()
        worksheet   = workbook.add_sheet('%s - %s' % (date_from, date_to))

        header_style = xlwt.easyxf("font: bold on, height 200; alignment: horizontal centre, vertical centre;")
        # date_style  = xlwt.easyxf(num_format_str='DD/MM/YYYY')
        # text_center = xlwt.easyxf("alignment: horizontal centre, vertical centre;")

        # bold        = xlwt.easyxf("font: bold on, height 200;")
        # title       = xlwt.easyxf("alignment: horizontal centre, vertical centre; font: bold on, height 300;")


        header_title = [u'SỐ ĐƠN HÀNG', u'NGÀY TÍNH \nDOANH SỐ', u'KẾT QUẢ', u'NGÀY \nXÁC NHẬN', \
            u'THAM CHIẾU\n/MÔ TẢ', u'KHÁCH HÀNG', u'NHÂN VIÊN', \
            # u'GIÁ HÀNG BÁN', u'TỔNG TIỀN', u'TỶ GIÁ', \            
            u'GIÁ BÁN \nQUY ĐỔI (TK 511)', u'VAT', u'TỔNG CỘNG', \
            u'TT LẦN 1', u'NGÀY', u'CHỨNG TỪ', u'TT LẦN 2', u'NGÀY', u'CHỨNG TỪ', \
            u'TT LẦN 3', u'NGÀY', u'CHỨNG TỪ', u'PHẢI THU \nCÒN LẠI', u'NHÀ CC (632)', u'PHÍ ĐỐI TÁC \n(6322)', \
            u'VẬN CHUYỂN \n(6213)', u'KHẨN (6217)', u'RỬA HÌNH \n(6219A)', u'KSK,DKTT \n(6212)', u'CHỨNG NHẬN DẤU, \nLLTP, HỢP PHÁP HÓA \n(6214)', \
            u'DỊCH THUẬT \n(6216)', u'SAO Y, \nCÔNG CHỨNG \n(6219B)', u'GIẢM TRỪ DT \n(5212+5213)', u'CHÊNH LỆCH TỶ \nGIÁ, PHÍ CK, \nTHU THIẾU (6218)', \
            u'HOA HỒNG, \nLOBBY (6219)', u'CHI PHÍ KHÁC', u'TỔNG CHI PHÍ', u'LỢI NHUẬN']
        
        worksheet.row(0).height_mismatch = True
        worksheet.row(0).height = 256 * 3
        

        for header_index, header_value in enumerate(header_title):
            worksheet.col(header_index).width_mismatch = True
            if header_index in (5, 6):
                worksheet.col(header_index).width = 256 * 20
            else:
                worksheet.col(header_index).width = 256 * 15
            worksheet.write(0, header_index, header_value, header_style)

        rows = 0
        so_ids = request.env['sale.order'].search([('x_ngaytinhdoanhso', '>=',  date_from), ('x_ngaytinhdoanhso', '<=', date_to)])

        print 

        kq = {
            'pass': u'Đạt',
            'fall': u'Không đạt',
            'canceled': u'Không làm nữa',
            'delay': u'Treo',
        }

        for so in so_ids:
            col = 0
            rows += 1
            ncc = ','.join(list(set([line.move_id.partner_id.name for line in so.analytic_lines if line.general_account_id.code=='6322'])))
            payment_ids = so.invoice_ids.mapped('payment_ids').sorted(lambda r: (r.date, r.debit - r.credit))
            col = self.tgl_write_excel(worksheet, rows, col, so.name)
            col = self.tgl_write_excel(worksheet, rows, col, so.x_ngaytinhdoanhso)
            col = self.tgl_write_excel(worksheet, rows, col, so.ketqua and kq[so.ketqua] or '')
            col = self.tgl_write_excel(worksheet, rows, col, so.date_confirm)
            col = self.tgl_write_excel(worksheet, rows, col, so.client_order_ref_2)
            col = self.tgl_write_excel(worksheet, rows, col, so.partner_id.name)
            col = self.tgl_write_excel(worksheet, rows, col, so.user_id and so.user_id.name or '')
            # col = self.tgl_write_excel(worksheet, rows, col, so.amount_untaxed)
            # col = self.tgl_write_excel(worksheet, rows, col, so.amount_total)
            # col = self.tgl_write_excel(worksheet, rows, col, so.exchange_rate)
            col = self.tgl_write_excel(worksheet, rows, col, sum(line.amount for line in so.analytic_lines if line.general_account_id.code.startswith('511')))
            col = self.tgl_write_excel(worksheet, rows, col, sum(inv.vnd_amount_tax for inv in so.invoice_ids))
            # col = self.tgl_write_excel(worksheet, rows, col, so.vnd_amount_total)
            # col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code in ('5111', '5118'))))
            col = self.tgl_write_excel(worksheet, rows, col, sum(inv.vnd_amount_total for inv in so.invoice_ids))
            col = self.tgl_write_excel(worksheet, rows, col, payment_ids and payment_ids[0].credit - payment_ids[0].debit or '')
            col = self.tgl_write_excel(worksheet, rows, col, payment_ids and payment_ids[0].date or '')
            col = self.tgl_write_excel(worksheet, rows, col, payment_ids and payment_ids[0].move_id.name or '')
            col = self.tgl_write_excel(worksheet, rows, col, len(payment_ids) > 1 and payment_ids[1].credit - payment_ids[1].debit or '')
            col = self.tgl_write_excel(worksheet, rows, col, len(payment_ids) > 1 and payment_ids[1].date or '')
            col = self.tgl_write_excel(worksheet, rows, col, len(payment_ids) > 1 and payment_ids[1].move_id.name or '')
            col = self.tgl_write_excel(worksheet, rows, col, len(payment_ids) > 2 and payment_ids[2].credit - payment_ids[2].debit or '')
            col = self.tgl_write_excel(worksheet, rows, col, len(payment_ids) > 2 and payment_ids[2].date or '')
            col = self.tgl_write_excel(worksheet, rows, col, len(payment_ids) > 2 and payment_ids[2].move_id.name or '')
            col = self.tgl_write_excel(worksheet, rows, col, so.customer_residual)
            col = self.tgl_write_excel(worksheet, rows, col, ncc)
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6322')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6213')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6217')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6219A')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6212')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6214')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6216')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6219B')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code in ('5212', '5213'))))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6218')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.general_account_id and line.general_account_id.code=='6219')))
            col = self.tgl_write_excel(worksheet, rows, col, abs(sum(line.amount for line in so.analytic_lines if line.journal_id.name=='Purchases' and line.general_account_id and line.general_account_id.code not in ('6322', '6213', '6217', '6219A', '6212', '6214', '6216', '6219B', '6218', '6219', '5212', '5213'))))
            col = self.tgl_write_excel(worksheet, rows, col, abs(so.acc_analytic_credit))
            col = self.tgl_write_excel(worksheet, rows, col, so.acc_analytic_balance)

        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=%s.xls' % filename)])
        workbook.save(response.stream)
        return response

    @http.route(['/skyerp/account_report_partner_balance'], type='http', auth="user")
    def sky_account_report_partner_balance(self, context, w_context, debug=None):        

        obj_move = request.env['account.move.line']
        used_context = json.loads(context)        

        wizard_context = json.loads(w_context)

        query = obj_move.with_context(used_context)._query_get(obj='l')        

        ACCOUNT_TYPE = []
        result_selection = wizard_context.get('result_selection', False)

        if ( result_selection== 'customer' ):
            ACCOUNT_TYPE = ('receivable',)
        elif (result_selection == 'supplier'):
            ACCOUNT_TYPE = ('payable',)
        else:
            ACCOUNT_TYPE = ('payable', 'receivable')

        move_state = ['draft','posted']
        if wizard_context.get('target_move', False) == 'posted':
            move_state = ['posted']

        request._cr.execute(
            "SELECT p.ref,l.account_id,ac.name AS account_name,ac.code AS code,p.name, p.id p_id, sum(debit) AS debit, sum(credit) AS credit, " \
                    "CASE WHEN sum(debit) > sum(credit) " \
                        "THEN sum(debit) - sum(credit) " \
                        "ELSE 0 " \
                    "END AS sdebit, " \
                    "CASE WHEN sum(debit) < sum(credit) " \
                        "THEN sum(credit) - sum(debit) " \
                        "ELSE 0 " \
                    "END AS scredit, " \
                    "(SELECT sum(debit-credit) " \
                        "FROM account_move_line l " \
                        "WHERE partner_id = p.id " \
                            "AND " + query + " " \
                            "AND blocked = TRUE " \
                    ") AS enlitige " \
            "FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) " \
            "JOIN account_account ac ON (l.account_id = ac.id)" \
            "JOIN account_move am ON (am.id = l.move_id)" \
            "WHERE ac.type IN %s " \
            "AND am.state IN %s " \
            "AND " + query + "" \
            "GROUP BY p.id, p.ref, p.name,l.account_id,ac.name,ac.code " \
            "ORDER BY l.account_id,p.name",
            (ACCOUNT_TYPE, tuple(move_state)))
        res = request._cr.dictfetchall()

        full_account = []

        if wizard_context.get('display_partner', False) == 'non-zero_balance':
            full_account = [r for r in res if r['sdebit'] > 0 or r['scredit'] > 0]
        else:
            full_account = [r for r in res]        

        ll = []
        w_filter = wizard_context.get('filter', False)
        if w_filter != 'filter_no':
            min_date = wizard_context.get('min_date', False)
            
            new_context = {
                'journal_ids': used_context['journal_ids'],
                'state': used_context['state'],
            }

            new_query = obj_move.with_context(new_context)._query_get(obj='l')
            
            request._cr.execute(
                "SELECT p.ref,l.account_id,ac.name AS account_name,ac.code AS code,p.id p_id,p.name, sum(debit) AS debit, sum(credit) AS credit " \

                "FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) " \
                "JOIN account_account ac ON (l.account_id = ac.id)" \
                "JOIN account_move am ON (am.id = l.move_id)" \
                "WHERE ac.type IN %s " \
                "AND am.state IN %s " \
                "AND l.date < %s " \
                "AND " + new_query + "" \
                "GROUP BY p.id, p.ref, p.name,l.account_id,ac.name,ac.code " \
                "ORDER BY l.account_id,p.name",
                (ACCOUNT_TYPE, tuple(move_state), min_date))
            res2 = request._cr.dictfetchall()

            ll = {i['p_id']: i for i in res2}
        for rec in full_account:
            rec.update({
                'old_credit': 0 if rec['p_id'] not in ll else ll[rec['p_id']]['credit'],  
                'old_debit': 0 if rec['p_id'] not in ll else ll[rec['p_id']]['debit']    
            })
            if not rec.get('name', False):
                rec.update({'name': 'Unknown Partner'})

        # Xu ly Excel 
        filename = u'So du cua doi tac'

        workbook    = xlwt.Workbook()
        worksheet   = workbook.add_sheet(filename)
        header_style = xlwt.easyxf("font: bold on, height 200;")
        center_style = xlwt.easyxf("alignment: horizontal centre, vertical centre;")
        bold_center = xlwt.easyxf("font: bold on, height 200; alignment: horizontal centre, vertical centre;")

        date_range = ''
        if w_filter == 'filter_date':
            date_from = used_context.get('date_from', '')
            date_to = used_context.get('date_to', '')
            if len(date_from):
                date_from = u'{}-{}-{}'.format(date_from[-2:], date_from[-5:-3], date_from[:4])
            if date_to:
                date_to = u'{}-{}-{}'.format(date_to[-2:], date_to[-5:-3], date_to[:4])
            date_range = u'{} - {}'.format(date_from, date_to)
        elif w_filter == 'filter_period':
            Period = request.env['account.period']
            period_from = used_context.get('period_from', 0)
            period_to = used_context.get('period_to', 0)
            if period_from:
                period_from = Period.browse(period_from).display_name
            else:
                period_from = ''
            if period_to:
                period_to = Period.browse(period_to).display_name
            else:
                period_to = ''
            date_range = u'{} - {}'.format(period_from, period_to)

        loai_tai_khoan = {
            'customer': u'Phải thu',
            'supplier': u'Phải trả',
            'customer_supplier': u'Phải thu và phải trả'
        }

        target_move = u'Tất cả bút toán'

        if wizard_context.get('target_move', False) == 'posted':
            target_move = u'Tất cả bút toán đã vào sổ'

        worksheet.write(1, 1, u'Đối tượng : {}'.format(target_move))
        worksheet.write(2, 1, u'Loại tài khoản: {}'.format(loai_tai_khoan[result_selection]))
        worksheet.write(3, 1, u'Thời gian: ' + date_range)

        for header_index in xrange(11):
            worksheet.col(header_index).width_mismatch = True
            if header_index == 0:
                worksheet.col(header_index).width = 256 * 7
            elif header_index == 1:
                worksheet.col(header_index).width = 256 * 50
            else:
                worksheet.col(header_index).width = 256 * 20

        rows = 5
        codes = []

        worksheet.write_merge(rows-1, rows-1, 2, 4, u'Đầu kì', bold_center)
        worksheet.write_merge(rows-1, rows-1, 5, 7, u'Phát sinh', bold_center)
        worksheet.write_merge(rows-1, rows-1, 8, 10, u'Cuối kì', bold_center)

        headers = [u'Mã', u'Tên (Tài khoản/Đối tác) ', u'Nợ', u'Có', u'Số dư', u'Nợ', u'Có', u'Số dư', u'Nợ', u'Có', u'Số dư']
        for header_index, header_name in enumerate(headers):
            worksheet.write(rows, header_index, header_name, header_style)

        so_style = XFStyle()
        so_style.num_format_str = '#,##0.00'
        font = Font()
        font.bold = True
        so_style.num_format_str = '#,##0.00'
        so_style.font = font

        so_style_v2 = XFStyle()
        so_style_v2.num_format_str = '#,##0.00'

        # Tong cua tat ca
        rows += 1
        worksheet.write(rows, 0, u'Tổng', header_style)
        c_old_debit = sum(r['old_debit'] for r in full_account)
        c_old_credit = sum(r['old_credit'] for r in full_account)

        c_debit = sum(r['debit'] for r in full_account)
        c_credit = sum(r['credit'] for r in full_account)

        worksheet.write(rows, 2, c_old_debit, so_style)
        worksheet.write(rows, 3, c_old_credit, so_style)
        worksheet.write(rows, 4, c_old_debit - c_old_credit, so_style)

        worksheet.write(rows, 5, c_debit, so_style)
        worksheet.write(rows, 6, c_credit, so_style)
        worksheet.write(rows, 7, c_debit - c_credit, so_style)

        worksheet.write(rows, 8, c_old_debit + c_debit, so_style)
        worksheet.write(rows, 9, c_old_credit + c_credit, so_style)
        worksheet.write(rows, 10, c_old_debit - c_old_credit + c_debit - c_credit, so_style)

        for rec in full_account:
            if rec['code'] not in codes:
                rows += 1
                if len(codes):
                    rows += 2
                worksheet.write(rows, 0, rec['code'])
                worksheet.write(rows, 1, rec['account_name'], header_style)
                c_old_debit = sum(r['old_debit'] for r in full_account if r['code'] == rec['code'])
                c_old_credit = sum(r['old_credit'] for r in full_account if r['code'] == rec['code'])

                c_debit = sum(r['debit'] for r in full_account if r['code'] == rec['code'])
                c_credit = sum(r['credit'] for r in full_account if r['code'] == rec['code'])

                worksheet.write(rows, 2, c_old_debit, so_style)
                worksheet.write(rows, 3, c_old_credit, so_style)
                worksheet.write(rows, 4, c_old_debit - c_old_credit, so_style)

                worksheet.write(rows, 5, c_debit, so_style)
                worksheet.write(rows, 6, c_credit, so_style)
                worksheet.write(rows, 7, c_debit - c_credit, so_style)

                worksheet.write(rows, 8, c_old_debit + c_debit, so_style)
                worksheet.write(rows, 9, c_old_credit + c_credit, so_style)
                worksheet.write(rows, 10, c_old_debit - c_old_credit + c_debit - c_credit, so_style)

                codes.append(rec['code'])                


            col = 1
            rows += 1
            col = self.tgl_write_excel(worksheet, rows, col, rec['name'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['old_debit'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['old_credit'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['old_debit'] - rec['old_credit'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['debit'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['credit'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['debit'] - rec['credit'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['old_debit'] + rec['debit'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['old_credit'] + rec['credit'], so_style_v2)
            col = self.tgl_write_excel(worksheet, rows, col, rec['old_debit'] + rec['debit'] - rec['old_credit'] - rec['credit'], so_style_v2)
            # col = self.tgl_write_excel(worksheet, rows, col, rec['enlitige'])

        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=%s.xls' % filename)])
        workbook.save(response.stream)
        return response

