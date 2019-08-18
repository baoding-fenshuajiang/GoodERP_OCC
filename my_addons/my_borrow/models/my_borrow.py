# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BorrowTask(models.Model):
    _name = 'borrow.task'
    _description = "借还事项"

    name = fields.Many2one('equipment.workholder', string='夹具', required=True)
    borrower_id = fields.Many2one('hr.employee', string='借用人', required=True)
    borrow_date = fields.Date(string="借出日期", default=lambda self: self._context.get('date', fields.Date.context_today(self)), required=True)
    return_date = fields.Date(string="归还日期", compute="_compute_date_returned")
    is_returned = fields.Boolean(string="是否已归还", default=False)
    processing_quantity = fields.Integer(string="加工数量",default=0)
    left_amount = fields.Integer("剩余寿命(件)")

    @api.depends("is_returned")
    @api.multi
    def _compute_date_returned(self):
        for rec in self:
            if rec.is_returned and (not rec.return_date):
                rec.return_date = fields.Date.context_today(self)
            if (not rec.is_returned) and rec.return_date:
                rec.return_date = False

    @api.onchange('processing_quantity')
    def _on_processing_quantity(self):
        for rec in self:
            if rec.processing_quantity and (not rec.left_amount):
                rec.left_amount = rec.name.left_amount-rec.processing_quantity
                rec.name.write({'left_amount': rec.left_amount})

