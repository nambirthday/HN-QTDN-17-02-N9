from odoo import models, fields


class DanhSachChungChiBangCap(models.Model):
    _name = 'danh_sach_chung_chi_bang_cap'
    _description = 'Danh sách chứng chỉ - bằng cấp'

    chung_chi_bang_cap_id = fields.Many2one(
        "chung_chi_bang_cap",
        string="Chứng chỉ / Bằng cấp",
        required=True,
        ondelete='cascade'
    )

    nhan_vien_id = fields.Many2one(
        "nhan_vien",
        string="Nhân viên",
        required=True,
        ondelete='cascade'
    )

    ghi_chu = fields.Char(string="Ghi chú")

    ma_dinh_danh = fields.Char(
        string="Mã định danh",
        related='nhan_vien_id.ma_dinh_danh',
        store=True
    )

    tuoi = fields.Integer(
        string="Tuổi",
        related='nhan_vien_id.tuoi',
        store=True
    )

    _sql_constraints = [
        (
            'unique_nhan_vien_cc',
            'unique(nhan_vien_id, chung_chi_bang_cap_id)',
            'Nhân viên đã có chứng chỉ này!'
        )
    ]