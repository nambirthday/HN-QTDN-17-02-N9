# -*- coding: utf-8 -*-

{
    'name': 'Quản Lý Dự Án',

    'version': '1.0',

    'category': 'Project',

    'summary': 'Quản lý dự án doanh nghiệp',

    'description': '''
HỆ THỐNG QUẢN LÝ DỰ ÁN

Chức năng:
- Quản lý dự án
- Quản lý thành viên dự án
- Quản lý giai đoạn dự án
- Theo dõi tiến độ dự án
- Thống kê số lượng thành viên
- Thống kê số lượng giai đoạn
- Theo dõi trạng thái dự án
    ''',

    'author': 'Sinh Le Van',

    'website': 'https://www.example.com',

    'license': 'LGPL-3',

    'depends': [
        'base',
        'nhan_su',
        'ai_integration',
    ],

    'data': [

        'security/ir.model.access.csv',

        'views/du_an_views.xml',
        'views/giai_doan_views.xml',
        'views/thanh_vien_views.xml',

        'views/menu.xml',

    ],

    'demo': [],

    'installable': True,

    'application': True,

    'auto_install': False,
}