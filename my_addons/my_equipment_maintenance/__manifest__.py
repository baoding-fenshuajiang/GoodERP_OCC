# -*- coding: utf-8 -*-

{
    'name': 'Maintenance',
    'version': '1.0',
    'sequence': 125,
    'category': 'Human Resources',
    'description': """
        Track equipments and my_equipment_maintenance requests""",
    'depends': ['mail'],
    'summary': 'Track equipment and manage my_equipment_maintenance requests',
    'website': 'https://www.odoo.com/page/tpm-my_equipment_maintenance-software',
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
