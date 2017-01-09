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

try:
    import xlwt
except ImportError:
    xlwt = None



class AdvanceExport(http.Controller):

    def tgl_write_excel(self, worksheet, rows, col, value):
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
            u'GIÁ BÁN \nQUY ĐỔI', u'VAT', u'TỔNG CỘNG', \
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

        kq = {
            'pass': u'Đạt',
            'fall': u'Không đạt',
            'canceled': u'Không làm nữa',
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
            col = self.tgl_write_excel(worksheet, rows, col, sum(inv.vnd_amount_untaxed for inv in so.invoice_ids))
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