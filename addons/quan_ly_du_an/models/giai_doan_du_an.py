from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GiaiDoanDuAn(models.Model):
    _name = 'giai_doan_du_an'
    _description = 'Giai đoạn dự án'
    _rec_name = 'ten_giai_doan'

    ten_giai_doan = fields.Char(
        string='Tên giai đoạn',
        required=True
    )

    mo_ta = fields.Text(
        string='Mô tả'
    )

    du_an_id = fields.Many2one(
        'du_an',
        string='Dự án',
        required=True,
        ondelete='cascade'
    )

    ngay_bat_dau = fields.Date(
        string='Ngày bắt đầu'
    )

    ngay_ket_thuc = fields.Date(
        string='Ngày kết thúc'
    )

    trang_thai = fields.Selection(
        [
            ('chua_bat_dau', 'Chưa bắt đầu'),
            ('dang_thuc_hien', 'Đang thực hiện'),
            ('hoan_thanh', 'Hoàn thành')
        ],
        string='Trạng thái',
        compute='_compute_trang_thai',
        store=True
    )

    tong_cong_viec = fields.Integer(
        string='Tổng công việc',
        compute='_compute_thong_ke',
        store=False
    )

    tien_do = fields.Float(
        string='Tiến độ (%)',
        compute='_compute_thong_ke',
        store=False
    )

    _sql_constraints = [
        (
            'unique_stage_project',
            'unique(ten_giai_doan, du_an_id)',
            'Tên giai đoạn đã tồn tại trong dự án!'
        )
    ]

    # ==========================
    # THỐNG KÊ
    # ==========================

    def _compute_thong_ke(self):
        """
        Tính toán tổng số công việc và tiến độ của giai đoạn
        Sử dụng One2many `cong_viec_ids` (được khai báo trong module công việc) để
        đảm bảo dependency đúng và giảm số truy vấn.
        """
        for rec in self:
            total_tasks = len(rec.cong_viec_ids)
            rec.tong_cong_viec = total_tasks

            completed_tasks = 0
            for t in rec.cong_viec_ids:
                if t.trang_thai == 'hoan_thanh':
                    completed_tasks += 1

            rec.tien_do = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # ==========================
    # TRẠNG THÁI
    # ==========================

    @api.depends('tien_do')
    def _compute_trang_thai(self):

        for rec in self:

            if rec.tien_do == 0:
                rec.trang_thai = 'chua_bat_dau'

            elif rec.tien_do < 100:
                rec.trang_thai = 'dang_thuc_hien'

            else:
                rec.trang_thai = 'hoan_thanh'

    # ==========================
    # VALIDATION
    # ==========================

    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_ngay(self):

        for rec in self:

            if (
                rec.ngay_bat_dau
                and rec.ngay_ket_thuc
                and rec.ngay_ket_thuc < rec.ngay_bat_dau
            ):
                raise ValidationError(
                    'Ngày kết thúc phải lớn hơn ngày bắt đầu!'
                )

