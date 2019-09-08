# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class Repair(models.Model):
    _name = 'repair.order'
    _description = 'Repair Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        'Repair Reference',
        default=lambda self: self.env['ir.sequence'].next_by_code('repair.order'),
        copy=False, required=True,
        states={'confirmed': [('readonly', True)]})
    product_id = fields.Many2one(
        'maintenance.equipment', string='要维修的设备',
        readonly=True, required=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('cancel', 'Cancelled'),
        ('confirmed', 'Confirmed'),
        ('under_repair', 'Under Repair'),
        ('done', 'Repaired')], string='Status',
        copy=False, default='draft', readonly=True, track_visibility='onchange',
        help="* The \'Draft\' status is used when a user is encoding a new and unconfirmed repair order.\n"
        )
    operations = fields.One2many(
        'repair.line', 'repair_id', 'Parts',
        copy=True, readonly=True, states={'draft': [('readonly', False)]})
    internal_notes = fields.Text('Internal Notes')
    _sql_constraints = [
        ('name', 'unique (name)', 'The name of the Repair Order must be unique!'),
    ]

    @api.multi
    def action_repair_cancel_draft(self):
        if self.filtered(lambda repair: repair.state != 'cancel'):
            raise UserError(_("Repair must be canceled in order to reset it to draft."))
        self.mapped('operations').write({'state': 'draft'})
        return self.write({'state': 'draft'})

    @api.multi
    def action_repair_confirm(self):
        """ Repair order state is set to 'To be invoiced' when invoice method
        is 'Before repair' else state becomes 'Confirmed'.
        @param *arg: Arguments
        @return: True
        """
        if self.filtered(lambda repair: repair.state != 'draft'):
            raise UserError(_("Only draft repairs can be confirmed."))
        to_confirm = self - before_repair
        to_confirm_operations = to_confirm.mapped('operations')
        to_confirm_operations.write({'state': 'confirmed'})
        to_confirm.write({'state': 'confirmed'})
        return True

    @api.multi
    def action_repair_cancel(self):
        if self.filtered(lambda repair: repair.state == 'done'):
            raise UserError(_("Cannot cancel completed repairs."))
        self.mapped('operations').write({'state': 'cancel'})
        return self.write({'state': 'cancel'})

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

    def action_repair_ready(self):
        self.mapped('operations').write({'state': 'confirmed'})
        return self.write({'state': 'ready'})

    @api.multi
    def action_repair_start(self):
        """ Writes repair order state to 'Under Repair'
        @return: True
        """
        if self.filtered(lambda repair: repair.state not in ['confirmed', 'ready']):
            raise UserError(_("Repair must be confirmed before starting reparation."))
        self.mapped('operations').write({'state': 'confirmed'})
        return self.write({'state': 'under_repair'})


class RepairLine(models.Model):
    _name = 'repair.line'
    _description = 'Repair Line (parts)'

    name = fields.Text('Description', required=True)
    repair_id = fields.Many2one(
        'repair.order', 'Repair Order Reference',
        index=True, ondelete='cascade')
    type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove')], 'Type', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'))
    product_uom_qty = fields.Float(
        'Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], 'Status', default='draft',
        copy=False, readonly=True, required=True,
        help='The status of a repair line is set automatically to the one of the linked repair order.')




