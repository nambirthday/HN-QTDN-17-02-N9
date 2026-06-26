from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Nhân viên'
    _rec_name = 'ho_va_ten'
    _order = 'ten asc, tuoi desc'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)

    ho_ten_dem = fields.Char("Họ tên đệm", required=True)
    ten = fields.Char("Tên", required=True)

    ho_va_ten = fields.Char(
        compute="_compute_ho_va_ten",
        store=True
    )

    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("SĐT")
    telegram_chat_id = fields.Char("Telegram Chat ID", help="Chat ID của nhân viên để nhận thông báo Telegram.")
    anh = fields.Binary("Ảnh")

    don_vi_id = fields.Many2one(
        "don_vi",
        string="Đơn vị"
    )

    tuoi = fields.Integer(
        compute="_compute_tuoi",
        store=True
    )

    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac",
        "nhan_vien_id"
    )

    danh_sach_chung_chi_bang_cap_ids = fields.One2many(
        "danh_sach_chung_chi_bang_cap",
        "nhan_vien_id"
    )

    so_nguoi_bang_tuoi = fields.Integer(
        compute="_compute_so_nguoi_bang_tuoi",
        store=True
    )

    _sql_constraints = [
        (
            'ma_dinh_danh_unique',
            'unique(ma_dinh_danh)',
            'Mã định danh phải duy nhất!'
        )
    ]

    # ================= COMPUTE =================

    @api.depends('ho_ten_dem', 'ten')
    def _compute_ho_va_ten(self):
        for r in self:
            r.ho_va_ten = f"{r.ho_ten_dem or ''} {r.ten or ''}".strip()

    @api.depends('ngay_sinh')
    def _compute_tuoi(self):
        for r in self:
            if r.ngay_sinh:
                # ngay_sinh can be a string or date; use Odoo helper to parse safely
                dob = fields.Date.from_string(r.ngay_sinh)
                r.tuoi = date.today().year - dob.year
            else:
                r.tuoi = 0

    @api.depends('tuoi')
    def _compute_so_nguoi_bang_tuoi(self):
        for r in self:
            if r.tuoi:
                # When record is new (client NewId like 'NewId_...'), r.id may be a string
                # which causes SQL type errors when compared to integer id column.
                # Only include the id != filter for persisted records with integer ids.
                filters = [('tuoi', '=', r.tuoi)]
                if isinstance(r.id, int):
                    filters.append(('id', '!=', r.id))
                r.so_nguoi_bang_tuoi = self.search_count(filters)
            else:
                r.so_nguoi_bang_tuoi = 0

    # ================= VALIDATION =================

    @api.constrains('tuoi')
    def _check_tuoi(self):
        for r in self:
            if r.tuoi and r.tuoi < 18:
                raise ValidationError("Tuổi không được bé hơn 18")