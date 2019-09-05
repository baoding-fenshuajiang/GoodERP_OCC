# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': '夹具内部编号唯一性',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'sequence': 14,
    'summary': '夹具内部编号唯一性验证',
    'description': """
产品编号唯一性验证
==============
在同一个公司中检查"内部编号"字段唯一性的模块。
    """,
    'author':  '保定-粉刷匠,992102498@qq.com',
    'website': 'http://blog.sina.com.cn/kaiyuanlvzhou',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'my_workholder',
    ],
    'data': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: