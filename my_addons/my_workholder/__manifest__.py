# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '夹具',
    'version': '1.1',
    'summary': '记录夹具的名称、图号、内部编号、存放位置、夹具制作人、夹具寿命',
    'description': 'E-Mail:992102498@qq.com',
    'author':  '保定-粉刷匠',
    'website': 'http://blog.sina.com.cn/kaiyuanlvzhou',
    'depends':  [
        'hr',
       ],
    'sequence': 13,
    'demo': [],
    'data': [
        'views/my_workholder_views.xml'
    ],
    'qweb': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
