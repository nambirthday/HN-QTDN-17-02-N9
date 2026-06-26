from odoo import models, fields, api


class NhanVien(models.Model):
    _inherit = 'nhan_vien'

    cong_viec_ids = fields.One2many(
        'cong_viec',
        'nhan_vien_id',
        string='Công việc'
    )

    tong_task = fields.Integer(
        compute='_compute_kpi',
        store=True
    )
    task_hoan_thanh = fields.Integer(
        compute='_compute_kpi',
        store=True
    )
    kpi = fields.Float(
        compute='_compute_kpi',
        store=True,
        search='_search_kpi'
    )

    @api.model
    def _search_kpi(self, operator, value):
        """
        Custom search for KPI field based on computed value
        Search for employees with KPI matching the condition
        """
        # Get all employees and calculate their KPI
        employees = self.search([])
        matched_ids = []
        
        for emp in employees:
            kpi_val = emp.kpi
            # Apply the operator to check if this KPI matches
            if operator == '=' and kpi_val == value:
                matched_ids.append(emp.id)
            elif operator == '!=' and kpi_val != value:
                matched_ids.append(emp.id)
            elif operator == '<' and kpi_val < value:
                matched_ids.append(emp.id)
            elif operator == '>' and kpi_val > value:
                matched_ids.append(emp.id)
            elif operator == '<=' and kpi_val <= value:
                matched_ids.append(emp.id)
            elif operator == '>=' and kpi_val >= value:
                matched_ids.append(emp.id)
        
        return [('id', 'in', matched_ids)]

    @api.depends('cong_viec_ids.du_an_id', 'cong_viec_ids.trang_thai')
    def _compute_kpi(self):
        for rec in self:
            total = self.env['cong_viec'].search_count([
                ('nhan_vien_id', '=', rec.id)
            ])
            done = self.env['cong_viec'].search_count([
                ('nhan_vien_id', '=', rec.id),
                ('trang_thai', '=', 'hoan_thanh')
            ])
            rec.tong_task = total
            rec.task_hoan_thanh = done
            rec.kpi = (done / total * 100) if total else 0
