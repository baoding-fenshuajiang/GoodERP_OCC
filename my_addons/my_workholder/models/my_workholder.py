# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.osv import expression


# 在产品模型中增加图号、位置、制作人、使用寿命字段
class MyWorkholder(models.Model):
    _name = "equipment.workholder"
    _description = "夹具"
    _order = "name"
    name = fields.Char('名称', index=True, required=True, translate=False)
    drawing_number = fields.Char('图号')
    location = fields.Char('位置')
    producer = fields.Many2one('hr.employee', string='制作人')
    durability =  fields.Integer('使用寿命(件)')
    description = fields.Text('备注', translate=False)
    default_code = fields.Char('编号', index=True)
    active = fields.Boolean('有效', default=True,help="如果取消勾选，可以实现隐藏这个产品而不是移除它。")

    @api.multi
    def name_get(self):
        return [(template.id, '%s%s%s' % (template.default_code and '[%s] ' % template.default_code or '', template.name
                                          , template.drawing_number and '[%s]' % template.drawing_number))
                for template in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|','|', ('default_code',  operator, name), ('name', operator, name),
                      ('drawing_number', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        product_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(product_ids).name_get()

