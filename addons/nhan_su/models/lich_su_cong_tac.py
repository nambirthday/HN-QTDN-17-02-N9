from odoo import models, fields


class LichSuCongTac(models.Model):
    _name = 'lich_su_cong_tac'
    _description = 'Lịch sử công tác'

    nhan_vien_id = fields.Many2one(
        "nhan_vien",
        string="Nhân viên",
        required=True,
        ondelete='cascade'
    )

    chuc_vu_id = fields.Many2one(
        "chuc_vu",
        string="Chức vụ",
        required=True
    )

    don_vi_id = fields.Many2one(
        "don_vi",
        string="Đơn vị",
        required=True
    )

    loai_chuc_vu = fields.Selection([
        ("chinh", "Chính"),
        ("kiem_nhiem", "Kiêm nhiệm")
    ], string="Loại chức vụ", default="chinh")

    ngay_bat_dau = fields.Date(
        string='Ngày bắt đầu'
    )

    ngay_ket_thuc = fields.Date(
        string='Ngày kết thúc'
    )

    ghi_chu = fields.Text(
        string="Ghi chú"
    )

    _sql_constraints = [
        (
            'unique_lsu',
            'unique(nhan_vien_id, chuc_vu_id, don_vi_id, ngay_bat_dau)',
            'Lịch sử công tác bị trùng!'
        )
    ]