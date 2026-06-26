from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CongViec(models.Model):
    _name = 'cong_viec'
    _description = 'Công việc'
    _rec_name = 'ten_cong_viec'
    _order = 'ngay_giao desc'

    ma_cong_viec = fields.Char(
        string='Mã công việc',
        required=True
    )
    ten_cong_viec = fields.Char(
        string='Tên công việc',
        required=True
    )
    du_an_id = fields.Many2one(
        'du_an',
        string='Dự án',
        required=True,
        ondelete='cascade'
    )
    giai_doan_id = fields.Many2one(
        'giai_doan_du_an',
        string='Giai đoạn',
        ondelete='restrict'
    )
    nguoi_giao_id = fields.Many2one(
        'nhan_vien',
        string='Người giao',
        required=True
    )
    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        required=True
    )
    ngay_giao = fields.Date(
        string='Ngày giao',
        default=fields.Date.context_today
    )
    han_hoan_thanh = fields.Date(
        string='Hạn hoàn thành'
    )
    so_ngay_con_lai = fields.Integer(
        string='Số ngày còn lại',
        compute='_compute_thoi_gian',
        store=True
    )
    do_uu_tien = fields.Selection(
        [
            ('binh_thuong', 'Bình thường'),
            ('cao', 'Cao'),
            ('khan_cap', 'Khẩn cấp')
        ],
        string='Độ ưu tiên',
        default='binh_thuong'
    )
    trang_thai = fields.Selection(
        [
            ('moi_tao', 'Mới tạo'),
            ('dang_thuc_hien', 'Đang thực hiện'),
            ('hoan_thanh', 'Hoàn thành'),
            ('tre_han', 'Trễ hạn')
        ],
        string='Trạng thái',
        default='moi_tao'
    )
    tien_do = fields.Float(
        string='Tiến độ (%)',
        compute='_compute_tien_do',
        store=True
    )
    so_nhat_ky = fields.Integer(
        string='Số nhật ký',
        compute='_compute_so_nhat_ky',
        store=True
    )
    mo_ta = fields.Text(
        string='Mô tả'
    )
    log_ids = fields.One2many(
        'cong_viec_log',
        'cong_viec_id',
        string='Nhật ký công việc'
    )

    _sql_constraints = [
        (
            'ma_cong_viec_unique',
            'unique(ma_cong_viec)',
            'Mã công việc đã tồn tại!'
        )
    ]

    @api.onchange('du_an_id')
    def _onchange_du_an_id(self):
        if self.du_an_id and self.giai_doan_id and self.giai_doan_id.du_an_id != self.du_an_id:
            self.giai_doan_id = False

    @api.depends('han_hoan_thanh', 'ngay_giao', 'trang_thai')
    def _compute_thoi_gian(self):
        for rec in self:
            if rec.trang_thai == 'hoan_thanh':
                rec.so_ngay_con_lai = 0
            elif rec.han_hoan_thanh and rec.ngay_giao:
                today = fields.Date.context_today(rec)
                rec.so_ngay_con_lai = (
                    fields.Date.from_string(rec.han_hoan_thanh)
                    - fields.Date.from_string(today)
                ).days
            else:
                rec.so_ngay_con_lai = 0

    @api.depends('trang_thai')
    def _compute_tien_do(self):
        for rec in self:
            if rec.trang_thai == 'hoan_thanh':
                rec.tien_do = 100.0
            elif rec.trang_thai == 'dang_thuc_hien':
                rec.tien_do = 50.0
            elif rec.trang_thai == 'tre_han':
                rec.tien_do = 20.0
            else:
                rec.tien_do = 0.0

    @api.depends('log_ids')
    def _compute_so_nhat_ky(self):
        for rec in self:
            rec.so_nhat_ky = len(rec.log_ids)

    @api.constrains('du_an_id', 'giai_doan_id')
    def _check_giai_doan(self):
        for rec in self:
            if rec.giai_doan_id and rec.du_an_id and rec.giai_doan_id.du_an_id != rec.du_an_id:
                raise ValidationError(
                    'Giai đoạn phải thuộc cùng dự án với công việc'
                )

    def _ensure_project_member(self):
        member_model = self.env['thanh_vien_du_an']
        for rec in self:
            if rec.du_an_id and rec.nhan_vien_id:
                exists = member_model.search_count([
                    ('du_an_id', '=', rec.du_an_id.id),
                    ('nhan_vien_id', '=', rec.nhan_vien_id.id)
                ])
                if not exists:
                    member_model.create({
                        'du_an_id': rec.du_an_id.id,
                        'nhan_vien_id': rec.nhan_vien_id.id,
                        'vai_tro': 'dev'
                    })

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._ensure_project_member()
        return rec

    def write(self, vals):
        res = super().write(vals)
        self._ensure_project_member()
        return res

    @api.constrains('ngay_giao', 'han_hoan_thanh')
    def _check_ngay(self):
        for rec in self:
            if (
                rec.ngay_giao
                and rec.han_hoan_thanh
                and rec.han_hoan_thanh < rec.ngay_giao
            ):
                raise ValidationError(
                    'Hạn hoàn thành phải lớn hơn ngày giao'
                )
