# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class Repair(models.Model):
    _name = 'repair.order'
    _description = '维修单'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        '维修单号 ',
        default=lambda self: self.env['ir.sequence'].next_by_code('repair.order'),
        copy=False, required=True,
        states={'confirmed': [('readonly', True)]})
    product_id = fields.Many2one(
        'my_equipment_maintenance.equipment', string='要维修的设备',
        readonly=True, required=True, states={'draft': [('readonly', False)]})
    fault_symptom = fields.Text('故障现象')
    technician_user_id = fields.Many2one('res.users', '维修人')
    fault_analysis = fields.Text('故障分析')
    solving_process = fields.Text('解决过程记录')
    state = fields.Selection([
        ('draft', '草稿'),
        ('cancel', '已取消'),
        ('confirmed', '已确认'),
        ('done', 'Repaired')], string='状态',
        copy=False, default='draft', readonly=True, track_visibility='onchange'
        )
    operations = fields.One2many(
        'repair.line', 'repair_id', 'Parts',
        copy=True, readonly=False, states={'done': [('readonly', True)]})
    internal_notes = fields.Text('内部备注')
    start_date_time = fields.Datetime('开始时间')
    end_date_time = fields.Datetime('结束时间')
    _sql_constraints = [
        ('name', 'unique (name)', '维修单的编号必须是唯一的。'),
    ]

    @api.multi
    def action_repair_cancel_draft(self):
        if self.filtered(lambda repair: repair.state != 'cancel'):
            raise UserError(_("Repair must be canceled in order to reset it to draft."))
        self.mapped('operations').write({'state': 'draft'})
        return self.write({'state': 'draft'})

    def action_validate(self):
        self.ensure_one()
        return self.action_repair_confirm()

    @api.multi
    def action_repair_confirm(self):
        if self.filtered(lambda repair: repair.state != 'draft'):
            raise UserError(_("只有草稿状态的为需单才能被确认。"))
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def action_repair_cancel(self):
        if self.filtered(lambda repair: repair.state == 'done'):
            raise UserError(_("不能取消已完成的维修单。"))
        self.mapped('operations').write({'state': 'cancel'})
        return self.write({'state': 'cancel'})

    @api.multi
    def action_repair_end(self):
        """ Writes repair order state to 'To be invoiced' if invoice method is
        After repair else state is set to 'Ready'.
        @return: True
        """
        if self.filtered(lambda repair: repair.state != 'confirmed'):
            raise UserError(_("维修完成前首先要确认维修单！"))
        self.write({'state': 'done'})
        return True

    @api.multi
    def action_send_mail(self):
        self.ensure_one()
        template_id = self.env.ref('repair.mail_template_repair_quotation').id
        ctx = {
            'default_model': 'repair.order',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': 'mail.mail_notification_light',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def print_repair_order(self):
        return self.env.ref('repair.action_report_repair_order').report_action(self)


class RepairLine(models.Model):
    _name = 'repair.line'
    _description = '维修用零件'

    name = fields.Text('描述')
    repair_id = fields.Many2one(
        'repair.order', '维修单编号',
        index=True, ondelete='cascade')
    product_id = fields.Many2one('equipment.parts', '产品', required=True)
    product_uom_qty = fields.Float(
        'Quantity', default=1.0, required=True)





