# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '产品增加字段',
    'version': '1.1',
    'summary': '产品增加图号、存放位置、工装制作人字段',
    'description': 'E-Mail:992102498@qq.com',
    'author':  '保定-粉刷匠',
    'website': 'http://blog.sina.com.cn/kaiyuanlvzhou',
    'depends': ['product',
                'hr',
                ],
    'category': 'Warehouse',
    'sequence': 13,
    'demo': [

       ],
    'data': [
        'views/my_product_template_views.xml'
    ],
    'qweb': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
