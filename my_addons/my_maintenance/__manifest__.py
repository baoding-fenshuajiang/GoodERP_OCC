# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '夹具维护',
    'version': '1.1',
    'summary': '工装库中的夹具维护',
    'description': "记录工装库中夹具的维护，维护完成后重置夹具的剩余寿命。",
    'author':  "保定-粉刷匠，992102498@qq.com",
    'website': 'http://blog.sina.com.cn/kaiyuanlvzhou',
    'depends': ['my_workholder',
                'hr',
                'my_borrow',
                ],
    'category': 'Warehouse',
    'sequence': 13,
    'demo': [

       ],
    'data': [
        'views/my_maintenance_views.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
