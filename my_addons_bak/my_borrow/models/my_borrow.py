# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BorrowTask(models.Model):
    _name = 'borrow.task'
    _description=u"借还事项"

    name = fields.Many2one('product.template', string='工装', required=True)
    jieyongren_id = fields.Many2one('hr.employee', string='借用人', required=True)
    jiechuriqi = fields.Date(string="借出日期", default=lambda self: self._context.get('date', fields.Date.context_today(self)), required=True)
    guihuanriqi = fields.Date(string="归还日期", compute="_compute_date_returned")
    is_returned = fields.Boolean(string=u"是否已归还", default=False)

    @api.depends("is_returned")
    @api.multi
    def _compute_date_returned(self):
        for rec in self:
            if rec.is_returned and (not rec.guihuanriqi):
                rec.guihuanriqi = fields.Date.context_today(self)
            if (not rec.is_returned) and rec.guihuanriqi:
                rec.guihuanriqi = False

