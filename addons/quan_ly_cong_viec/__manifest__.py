# -*- coding: utf-8 -*-
{
    'name': 'Quản Lý Công Việc',

    'version': '1.0',

    'category': 'Project',

    'summary': 'Quản lý công việc và theo dõi tiến độ thực hiện',

    'description': '''
Module Quản Lý Công Việc

Chức năng chính:
- Quản lý danh sách công việc
- Phân công công việc cho nhân viên
- Theo dõi tiến độ thực hiện
- Theo dõi thời hạn hoàn thành
- Quản lý trạng thái công việc
- Quản lý nhật ký công việc
- Thống kê số lượng nhật ký
- Hỗ trợ quản lý dự án doanh nghiệp
    ''',

    'author': 'Sinh Le Van',

    'website': 'https://www.odoo.com',

    'license': 'LGPL-3',

    'depends': [
        'base',
        'nhan_su',
        'quan_ly_du_an'
    ],

    'data': [

        'security/ir.model.access.csv',

        'views/cong_viec_views.xml',
        'views/cong_viec_log_views.xml',
        'views/nhan_vien_kpi_views.xml',

        'views/menu.xml',
    ],

    'installable': True,

    'application': True,

    'auto_install': False,
}