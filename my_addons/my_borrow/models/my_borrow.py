# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BorrowTask(models.Model):
    _name = 'borrow.task'
    _description = "借还事项"

    equipment_workholder_id = fields.Many2one('equipment.workholder', string='夹具', required=True)
    borrower_id = fields.Many2one('hr.employee', string='借用人', required=True)
    borrow_date = fields.Date(string="借出日期",
                              default=lambda self: self._context.get('date', fields.Date.context_today(self)),
                              required=True)
    return_date = fields.Date(string="归还日期")
    is_returned = fields.Boolean(string="是否已归还", default=False)
    processing_quantity = fields.Integer(string="加工数量", default=0)
    left_amount = fields.Integer("剩余寿命(件)")

    @api.onchange("is_returned")
    def _on_is_returned(self):
        for rec in self:
            if rec.is_returned and (not rec.return_date):
                rec.return_date = fields.Date.context_today(self)
            if (not rec.is_returned) and rec.return_date:
                rec.return_date = False

    @api.onchange('processing_quantity')
    def _on_processing_quantity(self):
        for rec in self:
            if rec.is_returned and rec.processing_quantity and (not rec.left_amount):
                rec.left_amount = rec.equipment_workholder_id.left_amount-rec.processing_quantity
                rec.equipment_workholder_id.write({'left_amount': rec.left_amount})
                if rec.left_amount <= 0:
                    next_maintenance = self.env['maintenance.task'].search([
                        ('equipment_workholder_id', '=', rec.equipment_workholder_id.name),('is_returned', '=', False)
                    ])
                    if not next_maintenance:
                        self.ensure_one()
                        self.env['maintenance.task'].create({
                            'equipment_workholder_id': rec.equipment_workholder_id.id,
                        })


class StockRegister(models.Model):
    _name = 'stock.register'
    _description = "夹具入库登记"

    equipment_workholder_id = fields.Many2one('equipment.workholder', string='夹具', required=True)
    register_date = fields.Date(string="入库日期", default=lambda self: self._context.get('date',
                                fields.Date.context_today(self)), required=True)
    note = fields.Text('备注')


class MaintenanceTask(models.Model):
        _name = 'maintenance.task'
        _description = "维护事项"

        equipment_workholder_id = fields.Many2one('equipment.workholder', string='夹具', required=True)
        serviceman_id = fields.Many2one('hr.employee', string='维护人', required=False)
        maintenance_date = fields.Date(string="维护日期",
                                       default=lambda self: self._context.get('date', fields.Date.context_today(self)))
        return_date = fields.Date(string="完成日期")
        is_returned = fields.Boolean(string="是否已完成", default=False)
        description = fields.Text('备注')

        @api.onchange("is_returned")
        def _on_is_returned(self):
            for rec in self:
                if rec.is_returned and (not rec.return_date):
                    rec.return_date = fields.Date.context_today(self)
                    rec.equipment_workholder_id.write({'left_amount': rec.equipment_workholder_id.durability})
                if (not rec.is_returned) and rec.return_date:
                    rec.return_date = False


