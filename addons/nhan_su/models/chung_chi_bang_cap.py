from odoo import models, fields, api


class ChungChiBangCap(models.Model):
    _name = 'chung_chi_bang_cap'
    _description = 'Chứng chỉ - Bằng cấp'
    _rec_name = 'ten_chung_chi_bang_cap'
    _order = 'ma_chung_chi_bang_cap asc'

    ma_chung_chi_bang_cap = fields.Char(
        string="Mã chứng chỉ/bằng cấp",
        required=True
    )

    ten_chung_chi_bang_cap = fields.Char(
        string="Tên chứng chỉ/bằng cấp",
        required=True
    )

    loai = fields.Selection([
        ('chung_chi', 'Chứng chỉ'),
        ('bang_cap', 'Bằng cấp'),
        ('chung_nhan', 'Chứng nhận')
    ], string="Loại", default='chung_chi')

    cap_do = fields.Selection([
        ('co_ban', 'Cơ bản'),
        ('nang_cao', 'Nâng cao'),
        ('chuyen_sau', 'Chuyên sâu')
    ], string="Cấp độ", default='co_ban')

    mo_ta = fields.Text(string="Mô tả")

    active = fields.Boolean(default=True, string="Trạng thái")

    _sql_constraints = [
        (
            'ma_ccbc_unique',
            'unique(ma_chung_chi_bang_cap)',
            'Mã chứng chỉ đã tồn tại!'
        )
    ]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|',
                  ('ma_chung_chi_bang_cap', operator, name),
                  ('ten_chung_chi_bang_cap', operator, name)]
        return self.search(domain + args, limit=limit).name_get()