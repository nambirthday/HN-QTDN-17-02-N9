# -*- coding: utf-8 -*-
{
    'name': 'Quản Lý Nhân Sự',

    'version': '1.0',

    'category': 'Human Resources',

    'summary': 'Quản lý nhân viên, đơn vị, chức vụ và chứng chỉ',

    'description': """
Module Quản Lý Nhân Sự

Chức năng:
- Quản lý nhân viên
- Quản lý đơn vị
- Quản lý chức vụ
- Quản lý lịch sử công tác
- Quản lý chứng chỉ, bằng cấp
- Thống kê KPI nhân viên
- Theo dõi thông tin nhân sự doanh nghiệp
    """,

    'author': 'LeeSjn',

    'website': 'http://www.yourcompany.com',

    'license': 'LGPL-3',

    'depends': [
        'base'
    ],

    'data': [

        'security/ir.model.access.csv',

        'views/chuc_vu.xml',
        'views/don_vi.xml',
        'views/nhan_vien.xml',
        'views/lich_su_cong_tac.xml',
        'views/chung_chi_bang_cap.xml',
        'views/danh_sach_chung_chi_bang_cap.xml',

        'views/menu.xml',

    ],

    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,

    'application': True,

    'auto_install': False,
}