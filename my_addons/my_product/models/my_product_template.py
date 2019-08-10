# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.osv import expression


# 在产品模型中增加图号、位置、制作人字段
class MyProductTemplate(models.Model):
    _inherit = "product.template"
    x_tuhao = fields.Char(string=u'图号')
    x_weizhi = fields.Char(string=u'位置')
    x_zhizuoren_id = fields.Many2one('hr.employee', string=u'制作人')

    @api.multi
    def name_get(self):
        return [(template.id, '%s%s%s' % (template.default_code and '[%s] ' % template.default_code or '', template.name
                                          , template.x_tuhao and '[%s]' % template.x_tuhao))
                for template in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|','|', ('default_code',  operator, name), ('name', operator, name),
                      ('x_tuhao', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        product_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(product_ids).name_get()

