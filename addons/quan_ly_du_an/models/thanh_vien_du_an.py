from odoo import models, fields, api


class ThanhVienDuAn(models.Model):
    _name = 'thanh_vien_du_an'
    _description = 'Thành viên dự án'
    _rec_name = 'nhan_vien_id'

    du_an_id = fields.Many2one(
        'du_an',
        string='Dự án',
        required=True,
        ondelete='cascade'
    )

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        required=True,
        ondelete='restrict'
    )

    vai_tro = fields.Selection(
        [
            ('leader', 'Leader'),
            ('dev', 'Developer'),
            ('tester', 'Tester'),
            ('ba', 'Business Analyst')
        ],
        string='Vai trò',
        required=True
    )

    ngay_tham_gia = fields.Date(
        string='Ngày tham gia',
        default=fields.Date.today
    )

    ghi_chu = fields.Text(
        string='Ghi chú'
    )

    ma_dinh_danh = fields.Char(
        related='nhan_vien_id.ma_dinh_danh',
        string='Mã định danh',
        store=True
    )

    email = fields.Char(
        related='nhan_vien_id.email',
        string='Email',
        store=True
    )

    so_dien_thoai = fields.Char(
        related='nhan_vien_id.so_dien_thoai',
        string='Số điện thoại',
        store=True
    )

    tong_cong_viec = fields.Integer(
        string='Tổng công việc',
        compute='_compute_tong_cong_viec'
    )

    _sql_constraints = [
        (
            'unique_member_project',
            'UNIQUE(du_an_id, nhan_vien_id)',
            'Nhân viên đã tồn tại trong dự án này!'
        )
    ]

    @api.depends(
        'du_an_id',
        'nhan_vien_id'
    )
    def _compute_tong_cong_viec(self):

        for rec in self:

            rec.tong_cong_viec = self.env[
                'cong_viec'
            ].search_count([
                ('du_an_id', '=', rec.du_an_id.id),
                ('nhan_vien_id', '=', rec.nhan_vien_id.id)
            ])
