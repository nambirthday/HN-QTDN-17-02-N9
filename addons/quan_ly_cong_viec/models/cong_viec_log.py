from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CongViecLog(models.Model):
    _name = 'cong_viec_log'
    _description = 'Nhật ký công việc'
    _rec_name = 'cong_viec_id'
    _order = 'ngay_cap_nhat desc'

    cong_viec_id = fields.Many2one(
        'cong_viec',
        string='Công việc',
        required=True,
        ondelete='cascade'
    )

    ghi_chu = fields.Char(
        string='Tiêu đề cập nhật'
    )

    ngay_cap_nhat = fields.Datetime(
        string='Ngày cập nhật',
        default=fields.Datetime.now,
        readonly=True
    )

    noi_dung = fields.Text(
        string='Nội dung cập nhật',
        required=True
    )

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Người cập nhật',
        required=True
    )

    @api.constrains('noi_dung')
    def _check_noi_dung(self):

        for rec in self:

            if not rec.noi_dung:

                raise ValidationError(
                    'Nội dung cập nhật không được để trống!'
                )
