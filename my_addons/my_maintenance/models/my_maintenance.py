# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceTask(models.Model):
    _name = 'maintenance.task'
    _description = "维护事项"

    name = fields.Many2one('equipment.workholder', string='夹具', required=True)
    serviceman_id = fields.Many2one('hr.employee', string='维护人', required=True)
    maintenance_date = fields.Date(string="维护日期", default=lambda self: self._context.get('date', fields.Date.context_today(self)), required=True)
    return_date = fields.Date(string="完成日期")
    is_returned = fields.Boolean(string="是否已完成", default=False)
    description = fields.Text('备注')

    @api.onchange("is_returned")
    def _on_is_returned(self):
        for rec in self:
            if rec.is_returned and (not rec.return_date):
                rec.return_date = fields.Date.context_today(self)
                rec.name.write({'left_amount': rec.name.durability})
            if (not rec.is_returned) and rec.return_date:
                rec.return_date = False

