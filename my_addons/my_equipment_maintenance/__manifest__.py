# -*- coding: utf-8 -*-

{
    'name': '设备维护',
    'version': '1.0',
    'sequence': 125,
    'category': '设备管理',
    'description': """
        设备维护""",
    'depends': ['my_equipment_parts', 'mail'],
    'summary': '管理设备维护',
    'website': 'http://blog.sina.com.cn/kaiyuanlvzhou',
    'data': [
        'security/mymaintenance.xml',
        'security/ir.model.access.csv',
        'data/mymaintenance_data.xml',
        'data/mail_data.xml',
        'views/mymaintenance_views.xml',
        'views/mymaintenance_templates.xml',
        'views/mail_activity_views.xml',
        'data/mymaintenance_cron.xml',
    ],
    'demo': ['data/mymaintenance_demo.xml'],
    'installable': True,
    'application': True,
}
