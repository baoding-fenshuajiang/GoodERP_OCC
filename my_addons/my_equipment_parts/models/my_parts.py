# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import _, api, fields, models
from odoo.osv import expression


# 备件模型
class MyEquipmentParts(models.Model):
    _name = "equipment.parts"
    _description = "设备备件"
    _order = "name"
    name = fields.Char('名称', index=True, required=True, translate=False)
    description = fields.Text('备注', translate=False)
    default_code = fields.Char('编号', index=True)
    active = fields.Boolean('有效', default=True, help="如果取消勾选，可以实现隐藏这个产品而不是移除它。")

    @api.multi
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            self.read(['name', 'default_code'])
            return [
                (template.id, '%s%s' % (template.default_code and '[%s] ' % template.default_code or '', template.name))
                for template in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('default_code',  operator, name), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        product_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(product_ids).name_get()

    @api.multi
    @api.constrains('default_code')
    def check_unique_default_code(self):
        if self.default_code:
            filters = [('default_code', '=', self.default_code)]
            workholder_ids = self.search(filters)
            if len(workholder_ids) > 1:
                raise Warning(
                    _('重复的备件编号，请确认编号的唯一性！'))


