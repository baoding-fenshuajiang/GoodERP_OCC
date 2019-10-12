# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '夹具借还',
    'version': '1.1',
    'summary': '工装库中的夹具、检具借还',
    'description': "记录工装库中工装和检具的领用和借还，并根据加工的产品件数计算产品寿命。",
    'author':  "保定-粉刷匠，992102498@qq.com",
    'website': 'http://blog.sina.com.cn/kaiyuanlvzhou',
    'depends': ['my_workholder',
                ],
    'category': 'Warehouse',
    'sequence': 13,
    'demo': [

       ],
    'data': [
        'views/my_borrow_views.xml',
        'security/borrow_security.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
