# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class HRPhieuLuong(models.Model):
    _name = 'hr_phieu_luong'
    _description = 'Phiếu lương tháng nhân viên'
    _rec_name = 'nhan_vien_id'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    thang = fields.Integer("Tháng", required=True, default=lambda self: datetime.now().month)
    nam = fields.Integer("Năm", required=True, default=lambda self: datetime.now().year)
    
    so_ngay_cong = fields.Float("Số ngày đi làm thực tế", compute="_compute_du_lieu_luong", store=True)
    luong_thuc_linh = fields.Float("Thực lĩnh (VND)", compute="_compute_du_lieu_luong", store=True)

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_du_lieu_luong(self):
        for rec in self:
            if not rec.nhan_vien_id or not rec.thang or not rec.nam:
                rec.so_ngay_cong = 0.0
                rec.luong_thuc_linh = 0.0
                continue

            # 1. Tính tổng số ngày công từ bảng chấm công hằng ngày
            cham_cong_records = self.env['hr_cham_cong'].search([
                ('nhan_vien_id', '=', rec.nhan_vien_id.id)
            ])
            
            tong_cong = 0.0
            for cc in cham_cong_records:
                if cc.ngay_cham_cong.month == rec.thang and cc.ngay_cham_cong.year == rec.nam:
                    if cc.trang_thai == 'di_lam':
                        tong_cong += 1.0
                    elif cc.trang_thai == 'nua_ngay':
                        tong_cong += 0.5
            rec.so_ngay_cong = tong_cong

            # 2. Lấy cấu hình lương gốc từ bảng cấu hình lương
            luong_base = self.env['hr_luong_co_ban'].search([('nhan_vien_id', '=', rec.nhan_vien_id.id)], limit=1)
            luong_cb = luong_base.luong_co_ban if luong_base else 0.0
            phu_cap = (luong_base.phu_cap_an_trua + luong_base.phu_cap_trach_nhiem) if luong_base else 0.0

            # 3. Tính tổng thưởng/phạt trong tháng
            bien_dong_records = self.env['hr_khen_thuong_ky_luat'].search([
                ('nhan_vien_id', '=', rec.nhan_vien_id.id)
            ])
            
            tong_thuong = 0.0
            tong_phat = 0.0
            for bd in bien_dong_records:
                if bd.ngay_ap_dung.month == rec.thang and bd.ngay_ap_dung.year == rec.nam:
                    if bd.loai_quyet_dinh == 'khen_thuong':
                        tong_thuong += bd.so_tien
                    elif bd.loai_quyet_dinh == 'ky_luat':
                        tong_phat += bd.so_tien

            # 4. Tính toán theo công thức đề bài yêu cầu
            rec.luong_thuc_linh = (luong_cb / 26) * rec.so_ngay_cong + phu_cap + tong_thuong - tong_phat