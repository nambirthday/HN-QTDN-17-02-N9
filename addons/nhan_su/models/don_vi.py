from odoo import models, fields


class DonVi(models.Model):
    _name = 'don_vi'
    _description = 'Đơn vị / Phòng ban'
    _rec_name = 'ten_don_vi'

    ma_don_vi = fields.Char(
        string="Mã đơn vị",
        required=True
    )

    ten_don_vi = fields.Char(
        string="Tên đơn vị",
        required=True
    )

    mo_ta = fields.Text(
        string="Mô tả"
    )

    nhan_vien_ids = fields.One2many(
        'nhan_vien',
        'don_vi_id',
        string="Danh sách nhân viên"
    )

    _sql_constraints = [
        (
            'ma_don_vi_unique',
            'unique(ma_don_vi)',
            'Mã đơn vị đã tồn tại!'
        )
    ]