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


class Hoso(models.Model):
    _name = 'so.loai_ho_so'

    name    = fields.Char('Tên hồ sơ')
    name_v2 = fields.Char('Tên hồ sơ (tiếng Anh)')

Hoso()

class DongHoSo(models.Model):
    _name = 'so.ho_so_line'

    order_id    = fields.Many2one('sale.order', 'Order')
    ho_so_id    = fields.Many2one('so.loai_ho_so', string='Loại hồ sơ/ chứng từ')
    goc         = fields.Boolean('Gốc')
    sl          = fields.Integer('Số lượng',default=1)
    nhan        = fields.Boolean('Nhận')
    tra         = fields.Boolean('Trả')
    ghichu      = fields.Text('Ghi chú')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    b2_customer_name    = fields.Char('Họ và tên khách hàng')
    b2_email            = fields.Char('Địa chỉ thư điện tử')
    b2_phone            = fields.Char('Số điện thoại')
    b2_address          = fields.Char('Địa chỉ liên lạc') 

    b2_ngay_nhan        = fields.Date('Ngày nhận')
    b2_thoi_gian        = fields.Float('Thời gian nhận')
    b2_loai_ho_so       = fields.Selection([('du_lich', 'Du lịch/Travel'), 
                                            ('cong_tac', 'Công tác/Business'),
                                            ('du_hoc', 'Du học/Study'),
                                            ('dinh_cu', 'Định cư/Immigrant')], string='Loại hồ sơ')
    b2_tinh_trang_ho_so = fields.Selection([('2', 'Khẩn/Urgen'),
                                            ('1', 'Bình thường/Standard')], string='Tình trạng')

    b2_note             = fields.Text('Ghi chú khác')
    ho_so_ids           = fields.One2many('so.ho_so_line', 'order_id', 'Chi tiết hồ sơ')

    @api.multi
    def lay_thong_tin_mau(self):
        for order in self:
            order.write({
                'b2_customer_name': order.partner_id.display_name,
                'b2_email': order.partner_id.email,
                'b2_phone': order.partner_id.phone or order.partner_id.mobile or False,
                'b2_address': order.partner_id.with_context(show_address_only=1).name_get()[0][1] or '',
            })

    @api.multi
    def in_mau_bien_nhan_ho_so(self):
        return self.env['report'].get_action(self, 'sky_bien_nhan_ho_so.mau_in_bien_nhan')

SaleOrder()