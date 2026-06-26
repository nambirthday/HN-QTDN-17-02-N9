from odoo import models, fields


class GiaiDoanDuAn(models.Model):
    _inherit = 'giai_doan_du_an'

    cong_viec_ids = fields.One2many(
        'cong_viec',
        'giai_doan_id',
        string='Công việc'
    )
