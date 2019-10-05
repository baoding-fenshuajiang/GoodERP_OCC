# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': '设备维修',
    'version': '1.0',
    'sequence': 200,
    'category': '设备管理',
    'summary': '设备维修记录',
    'description': """
管理设备维修
============
满足IATF16949关于设备履历的要求
""",
    'depends': ['hr','my_equipment_parts', 'my_equipment_maintenance'],
    'data': [
        'security/ir.model.access.csv',
        'security/repair_security.xml',
        'views/repair_views.xml',
        'report/repair_reports.xml',
        'report/repair_templates_repair_order.xml',
        'data/ir_sequence_data.xml',
        'data/repair_data.xml',
    ],
    'demo': ['data/repair_demo.xml'],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
