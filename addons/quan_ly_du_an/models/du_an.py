import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DuAn(models.Model):
    _name = 'du_an'
    _description = 'Dự án'
    _rec_name = 'ten_du_an'

    ma_du_an = fields.Char(
        string='Mã dự án',
        required=True
    )

    ten_du_an = fields.Char(
        string='Tên dự án',
        required=True
    )

    mo_ta = fields.Text(
        string='Mô tả'
    )

    ngay_bat_dau = fields.Date(
        string='Ngày bắt đầu'
    )

    ngay_ket_thuc = fields.Date(
        string='Ngày kết thúc'
    )

    quan_ly_du_an_id = fields.Many2one(
        'nhan_vien',
        string='Quản lý dự án'
    )

    thanh_vien_ids = fields.One2many(
        'thanh_vien_du_an',
        'du_an_id',
        string='Thành viên'
    )

    giai_doan_ids = fields.One2many(
        'giai_doan_du_an',
        'du_an_id',
        string='Giai đoạn'
    )

    trang_thai = fields.Selection(
        [
            ('moi_tao', 'Mới tạo'),
            ('dang_thuc_hien', 'Đang thực hiện'),
            ('hoan_thanh', 'Hoàn thành')
        ],
        string='Trạng thái',
        compute='_compute_trang_thai',
        store=True
    )

    tien_do = fields.Float(
        string='Tiến độ (%)',
        compute='_compute_tien_do',
        store=True
    )

    tong_thanh_vien = fields.Integer(
        string='Tổng thành viên',
        compute='_compute_thong_ke',
        store=True
    )

    tong_giai_doan = fields.Integer(
        string='Tổng giai đoạn',
        compute='_compute_thong_ke',
        store=True
    )

    tong_cong_viec = fields.Integer(
        string='Tổng công việc',
        compute='_compute_tong_cong_viec',
        store=True
    )

    ai_goi_y_cong_viec = fields.Text(
        string='Gợi ý phân chia công việc',
        compute='_compute_ai_goi_y_cong_viec',
        store=False
    )

    _sql_constraints = [
        (
            'ma_du_an_unique',
            'unique(ma_du_an)',
            'Mã dự án phải là duy nhất!'
        )
    ]

    @api.depends('thanh_vien_ids', 'giai_doan_ids')
    def _compute_thong_ke(self):
        for rec in self:
            rec.tong_thanh_vien = len(rec.thanh_vien_ids)
            rec.tong_giai_doan = len(rec.giai_doan_ids)

    @api.depends('giai_doan_ids.tong_cong_viec')
    def _compute_tong_cong_viec(self):
        for rec in self:
            rec.tong_cong_viec = sum(rec.giai_doan_ids.mapped('tong_cong_viec'))

    @api.depends('giai_doan_ids.tien_do', 'giai_doan_ids')
    def _compute_tien_do(self):
        for rec in self:
            if not rec.giai_doan_ids:
                rec.tien_do = 0
                continue
            total = sum(rec.giai_doan_ids.mapped('tien_do'))
            rec.tien_do = total / len(rec.giai_doan_ids)

    @api.depends('tien_do')
    def _compute_trang_thai(self):
        for rec in self:
            if rec.tien_do == 0:
                rec.trang_thai = 'moi_tao'
            elif rec.tien_do < 100:
                rec.trang_thai = 'dang_thuc_hien'
            else:
                rec.trang_thai = 'hoan_thanh'

    def _ensure_manager_member(self):
        member_obj = self.env['thanh_vien_du_an']
        for rec in self:
            if rec.quan_ly_du_an_id:
                exists = member_obj.search_count([
                    ('du_an_id', '=', rec.id),
                    ('nhan_vien_id', '=', rec.quan_ly_du_an_id.id)
                ])
                if not exists:
                    member_obj.create({
                        'du_an_id': rec.id,
                        'nhan_vien_id': rec.quan_ly_du_an_id.id,
                        'vai_tro': 'leader'
                    })

    def _get_ai_text(self, prompt):
        try:
            ai = self.env['ai.gemini']
            return ai.generate_text(prompt) or ''
        except Exception:
            return ''

    def _generate_ai_project_description(self):
        for rec in self:
            if not rec.ten_du_an or not rec.ma_du_an:
                continue
            prompt = (
                f"Viết một mô tả ngắn gọn cho dự án '{rec.ten_du_an}' "
                f"(mã {rec.ma_du_an}). Nêu mục tiêu chính và phương pháp phân chia công việc hợp lý "
                "trong dự án. Chỉ trả về tối đa 3 câu."
            )
            description = self._get_ai_text(prompt).strip()
            if description:
                rec.mo_ta = description

    def _get_project_notification_recipients(self):
        self.ensure_one()
        employees = self.env['nhan_vien']
        if self.quan_ly_du_an_id:
            employees |= self.quan_ly_du_an_id
        employees |= self.thanh_vien_ids.mapped('nhan_vien_id')
        return employees.filtered(lambda employee: employee.telegram_chat_id)

    def _build_project_assignment_message(self):
        self.ensure_one()
        manager = self.quan_ly_du_an_id
        manager_name = manager.ho_va_ten or manager.ten if manager else _('Ch?a ph?n c?ng')
        return (
            f"D? ?n m?i ???c giao: <b>{self.ten_du_an}</b>\n"
            f"M? d? ?n: <code>{self.ma_du_an}</code>\n"
            f"Ng??i qu?n l?: {manager_name}\n"
            f"Ng?y b?t ??u: {self.ngay_bat_dau or 'ch?a x?c ??nh'}\n"
            f"Ng?y k?t th?c: {self.ngay_ket_thuc or 'ch?a x?c ??nh'}\n"
            "Vui l?ng ki?m tra v? c?p nh?t ti?n ?? trong h? th?ng."
        )

    def _notify_project_assignment_via_telegram(self):
        sent_count = 0
        for rec in self:
            recipients = rec._get_project_notification_recipients()
            if not recipients:
                _logger.warning(
                    'Telegram notification skipped for project %s: no employee has telegram_chat_id',
                    rec.id,
                )
                continue

            message = rec._build_project_assignment_message()
            for employee in recipients:
                try:
                    sent = self.env['ai.gemini'].send_telegram_message(
                        employee.telegram_chat_id,
                        message,
                    )
                    if sent:
                        sent_count += 1
                    else:
                        _logger.warning(
                            'Telegram notification not sent for project %s to employee %s',
                            rec.id,
                            employee.id,
                        )
                except Exception:
                    _logger.exception(
                        'Failed to send Telegram assignment notification for project %s to employee %s',
                        rec.id,
                        employee.id,
                    )
        return sent_count

    def _generate_ai_task_suggestions(self, rec):
        if not rec.ten_du_an or not rec.ma_du_an or not rec.giai_doan_ids:
            return ''
        stage_count = len(rec.giai_doan_ids)
        prompt = (
            f"Dự án '{rec.ten_du_an}' (mã {rec.ma_du_an}) gồm {stage_count} giai đoạn chính. "
            "Hãy đề xuất một cách phân chia công việc hợp lý cho từng giai đoạn, "
            "trả về danh sách các công việc theo định dạng mỗi dòng một nhiệm vụ, "
            "kèm mô tả ngắn gọn cho từng nhiệm vụ."
        )
        suggestion = self._get_ai_text(prompt).strip()
        if suggestion:
            return suggestion
        # Fallback text when AI is not configured
        fallback_lines = []
        for idx, stage in enumerate(rec.giai_doan_ids, start=1):
            stage_name = getattr(stage, 'ten_giai_doan', False) or _('Giai đoạn %d' % idx)
            fallback_lines.append(
                f"- Giai đoạn {idx} ({stage_name}): lập kế hoạch, triển khai và kiểm thử chức năng của giai đoạn này."
            )
        return '\n'.join(fallback_lines)

    @api.depends('ten_du_an', 'ma_du_an', 'giai_doan_ids')
    def _compute_ai_goi_y_cong_viec(self):
        for rec in self:
            rec.ai_goi_y_cong_viec = self._generate_ai_task_suggestions(rec)

    def _parse_ai_task_lines(self, suggestion):
        lines = []
        for line in suggestion.splitlines():
            if not line or not line.strip():
                continue
            cleaned = line.strip().lstrip('-•* ').strip()
            if cleaned:
                lines.append(cleaned)
        return lines

    def _create_default_tasks(self):
        """Create default `cong_viec` tasks for each stage when a project
        has a manager assigned. Tasks are generated by AI if available.
        """
        task_obj = self.env['cong_viec']
        for rec in self:
            if not rec.id or not rec.quan_ly_du_an_id:
                continue

            suggestion = self._generate_ai_task_suggestions(rec)
            task_lines = self._parse_ai_task_lines(suggestion)
            if not task_lines:
                task_lines = [
                    f"Thực hiện giai đoạn {stage.ten_giai_doan} cho dự án {rec.ten_du_an}."
                    for stage in rec.giai_doan_ids
                ]

            for idx, stage in enumerate(rec.giai_doan_ids, start=1):
                if idx > len(task_lines):
                    break
                task_line = task_lines[idx - 1]
                code = f"{rec.ma_du_an}-{idx}"
                if task_obj.search_count([
                    ('ma_cong_viec', '=', code),
                    ('du_an_id', '=', rec.id)
                ]):
                    continue
                task_obj.create({
                    'ma_cong_viec': code,
                    'ten_cong_viec': task_line[:64],
                    'du_an_id': rec.id,
                    'giai_doan_id': rec.giai_doan_ids[idx - 1].id if idx - 1 < len(rec.giai_doan_ids) else False,
                    'nguoi_giao_id': rec.quan_ly_du_an_id.id,
                    'nhan_vien_id': rec.quan_ly_du_an_id.id,
                    'mo_ta': task_line,
                })

    @api.model
    def create(self, vals):
        du_an = super().create(vals)
        ds_giai_doan = [
            'Khảo sát yêu cầu',
            'Phân tích',
            'Thiết kế',
            'Lập trình',
            'Kiểm thử',
            'Triển khai'
        ]
        for ten in ds_giai_doan:
            self.env['giai_doan_du_an'].create({
                'ten_giai_doan': ten,
                'du_an_id': du_an.id
            })
        du_an._ensure_manager_member()
        du_an._generate_ai_project_description()
        # create default tasks for stages if a manager was set
        du_an._create_default_tasks()
        du_an._notify_project_assignment_via_telegram()
        return du_an

    def write(self, vals):
        res = super().write(vals)
        self._ensure_manager_member()
        if 'ten_du_an' in vals or 'ma_du_an' in vals or 'giai_doan_ids' in vals:
            self._generate_ai_project_description()
        # if manager was assigned or stages updated, ensure tasks exist
        if 'quan_ly_du_an_id' in vals or 'giai_doan_ids' in vals:
            self._create_default_tasks()
        if 'quan_ly_du_an_id' in vals:
            self._notify_project_assignment_via_telegram()
        return res

    def action_generate_ai_suggestions(self):
        for rec in self:
            rec._generate_ai_project_description()
        return True

    def action_send_telegram_notification(self):
        token = self.env['ai.gemini']._get_telegram_bot_token()
        if not token:
            raise UserError(_(
                'Ch?a c?u h?nh Telegram Bot Token. V?o C?i ??t > AI Integration ?? nh?p token.'
            ))

        missing_projects = self.filtered(lambda rec: not rec._get_project_notification_recipients())
        if missing_projects:
            raise UserError(_(
                'Kh?ng c? nh?n vi?n n?o trong d? ?n c? Telegram Chat ID. '
                'H?y nh?p Telegram Chat ID trong h? s? nh?n vi?n tr??c.'
            ))

        sent_count = self._notify_project_assignment_via_telegram()
        if not sent_count:
            raise UserError(_(
                'Telegram ch?a g?i ???c tin. Ki?m tra Bot Token, Chat ID v? vi?c nh?n vi?n ?? nh?n /start cho bot.'
            ))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Telegram'),
                'message': _('?? g?i %s tin nh?n Telegram.') % sent_count,
                'type': 'success',
                'sticky': False,
            }
        }

    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_ngay(self):
        for rec in self:
            if (
                rec.ngay_bat_dau
                and rec.ngay_ket_thuc
                and rec.ngay_ket_thuc < rec.ngay_bat_dau
            ):
                raise ValidationError(
                    'Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu!'
                )
