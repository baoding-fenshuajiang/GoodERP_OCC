# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class MaintenanceStage(models.Model):
    """ Model for case stages. This models the main stages of a Maintenance Request management flow. """

    _name = 'my_equipment_maintenance.stage'
    _description = '维护阶段'
    _order = 'sequence, id'

    name = fields.Char('名称', required=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('在维护中折叠！')
    done = fields.Boolean('请求完成')


class MaintenanceEquipmentCategory(models.Model):
    _name = 'my_equipment_maintenance.equipment.category'
    _inherit = ['mail.alias.mixin', 'mail.thread']
    _description = '设备维护分类'

    @api.one
    @api.depends('equipment_ids')
    def _compute_fold(self):
        self.fold = False if self.equipment_count else True

    name = fields.Char('分类名称', required=True)
    color = fields.Integer('Color Index')
    note = fields.Text('备注')
    equipment_ids = fields.One2many('my_equipment_maintenance.equipment', 'category_id', string='设备',
                                    copy=False)
    equipment_count = fields.Integer(string="设备", compute='_compute_equipment_count')
    my_equipment_maintenance_ids = fields.One2many('my_equipment_maintenance.request', 'category_id', copy=False)
    my_equipment_maintenance_count = fields.Integer(string="维护个数",
                                                    compute='_compute_my_equipment_maintenance_count')
    alias_id = fields.Many2one(
        'mail.alias', 'Alias', ondelete='restrict', required=True,
        help="Email alias for this equipment category. New emails will automatically "
        "create new my_equipment_maintenance request for this equipment category.")
    fold = fields.Boolean(string='在维护中折叠', compute='_compute_fold', store=True)

    @api.multi
    def _compute_equipment_count(self):
        equipment_data = self.env['my_equipment_maintenance.equipment'].read_group([('category_id', 'in', self.ids)],
                                                                                   ['category_id'], ['category_id'])
        mapped_data = dict([(m['category_id'][0], m['category_id_count']) for m in equipment_data])
        for category in self:
            category.equipment_count = mapped_data.get(category.id, 0)

    @api.multi
    def _compute_my_equipment_maintenance_count(self):
        my_equipment_maintenance_data = self.env['my_equipment_maintenance.request'].read_group([('category_id', 'in', self.ids)],
                                                                                   ['category_id'], ['category_id'])
        mapped_data = dict([(m['category_id'][0], m['category_id_count']) for m in my_equipment_maintenance_data])
        for category in self:
            category.my_equipment_maintenance_count = mapped_data.get(category.id, 0)

    @api.model
    def create(self, vals):
        self = self.with_context(alias_model_name='my_equipment_maintenance.request',
                                 alias_parent_model_name=self._name)
        if not vals.get('alias_name'):
            vals['alias_name'] = vals.get('name')
        category_id = super(MaintenanceEquipmentCategory, self).create(vals)
        category_id.alias_id.write({'alias_parent_thread_id': category_id.id, 'alias_defaults':
            {'category_id': category_id.id}})
        return category_id

    @api.multi
    def unlink(self):
        MailAlias = self.env['mail.alias']
        for category in self:
            if category.equipment_ids or category.my_equipment_maintenance_ids:
                raise UserError(_("你不能删除一个包含设备维护请求或设备的分类！"))
            MailAlias += category.alias_id
        res = super(MaintenanceEquipmentCategory, self).unlink()
        MailAlias.unlink()
        return res

    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'my_equipment_maintenance.equipment')

    def get_alias_values(self):
        values = super(MaintenanceEquipmentCategory, self).get_alias_values()
        values['alias_defaults'] = {'category_id': self.id}
        return values


class MaintenanceEquipment(models.Model):
    _name = 'my_equipment_maintenance.equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '设备'

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'owner_user_id' in init_values and self.owner_user_id:
            return 'my_equipment_maintenance.mt_mat_assign'
        return super(MaintenanceEquipment, self)._track_subtype(init_values)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.serial_no:
                result.append((record.id, record.name + '/' + record.serial_no))
            if record.name and not record.serial_no:
                result.append((record.id, record.name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        equipment_ids = []
        if name:
            equipment_ids = self._search([('name', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not equipment_ids:
            equipment_ids = self._search([('name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(equipment_ids).name_get()

    name = fields.Char('设备名称', required=True)
    active = fields.Boolean(default=True)
    technician_user_id = fields.Many2one('res.users', string='维护人', track_visibility='onchange',
                                         oldname='user_id')
    owner_user_id = fields.Many2one('res.users', string='操作者', track_visibility='onchange')
    category_id = fields.Many2one('my_equipment_maintenance.equipment.category', string='设备分类',
                                  track_visibility='onchange', group_expand='_read_group_category_ids')
    is_environmental_protecting_equipment = fields.Boolean('是否环保设备', default=False)
    partner_id = fields.Many2one('res.partner', string='供应商', domain="[('supplier', '=', 1)]")
    location = fields.Char('安装位置')
    model = fields.Char('型号')
    serial_no = fields.Char('设备编号', copy=False)
    production_date = fields.Date('生产日期')
    equipment_power = fields.Integer('设备功率(KW)')
    effective_date = fields.Date('投入使用日期', default=fields.Date.context_today, required=True,
                                 help="设备投入使用日期，用于按维护频次计算维护时间")
    cost = fields.Float('价格（元）')
    note = fields.Text('备注')
    warranty_date = fields.Date('质保期失效日期', oldname='warranty')
    color = fields.Integer('颜色索引')
    scrap_date = fields.Date('报废日期')
    my_equipment_maintenance_ids = fields.One2many('my_equipment_maintenance.request', 'equipment_id')
    my_equipment_maintenance_count = fields.Integer(compute='_compute_my_equipment_maintenance_count',
                                                    string="维护次数", store=True)
    my_equipment_maintenance_open_count = fields.Integer(compute='_compute_my_equipment_maintenance_count',
                                                         string="当前维护", store=True)
    period = fields.Integer('预防性维护之间的天数')
    next_action_date = fields.Date(compute='_compute_next_my_equipment_maintenance', string='预防性设备维护', store=True)
    my_equipment_maintenance_duration = fields.Float('维护用时', help="维护用时")

    @api.depends('effective_date', 'period', 'my_equipment_maintenance_ids.request_date',
                 'my_equipment_maintenance_ids.close_date')
    def _compute_next_my_equipment_maintenance(self):
        date_now = fields.Date.context_today(self)
        for equipment in self.filtered(lambda x: x.period > 0):
            next_my_equipment_maintenance_todo = self.env['my_equipment_maintenance.request'].search([
                ('equipment_id', '=', equipment.id),
                ('my_equipment_maintenance_type', '=', 'preventive'),
                ('stage_id.done', '!=', True),
                ('close_date', '=', False)], order="request_date asc", limit=1)
            last_my_equipment_maintenance_done = self.env['my_equipment_maintenance.request'].search([
                ('equipment_id', '=', equipment.id),
                ('my_equipment_maintenance_type', '=', 'preventive'),
                ('stage_id.done', '=', True),
                ('close_date', '!=', False)], order="close_date desc", limit=1)
            if next_my_equipment_maintenance_todo and last_my_equipment_maintenance_done:
                next_date = next_my_equipment_maintenance_todo.request_date
                date_gap = next_my_equipment_maintenance_todo.request_date - last_my_equipment_maintenance_done.\
                    close_date
                # If the gap between the last_my_equipment_maintenance_done and
                # the next_my_equipment_maintenance_todo one is bigger than 2 times the period and next
                # request is in the future
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=equipment.period) * 2 and \
                        next_my_equipment_maintenance_todo.request_date > date_now:
                    # If the new date still in the past, we set it for today
                    if last_my_equipment_maintenance_done.close_date + timedelta(days=equipment.period) < date_now:
                        next_date = date_now
                    else:
                        next_date = last_my_equipment_maintenance_done.close_date + timedelta(days=equipment.period)
            elif next_my_equipment_maintenance_todo:
                next_date = next_my_equipment_maintenance_todo.request_date
                date_gap = next_my_equipment_maintenance_todo.request_date - date_now
                # If next my_equipment_maintenance to do is in the future, and in more than 2 times the period,
                # we insert an new request
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=equipment.period) * 2:
                    next_date = date_now + timedelta(days=equipment.period)
            elif last_my_equipment_maintenance_done:
                next_date = last_my_equipment_maintenance_done.close_date + timedelta(days=equipment.period)
                # If when we add the period to the last my_equipment_maintenance done and we still in past,
                # we plan it for today
                if next_date < date_now:
                    next_date = date_now
            else:
                next_date = self.effective_date + timedelta(days=equipment.period)
            equipment.next_action_date = next_date

    @api.one
    @api.depends('my_equipment_maintenance_ids.stage_id.done')
    def _compute_my_equipment_maintenance_count(self):
        self.my_equipment_maintenance_count = len(self.my_equipment_maintenance_ids)
        self.my_equipment_maintenance_open_count = len(self.my_equipment_maintenance_ids.filtered(lambda x:
                                                                                                  not x.stage_id.done))

    _sql_constraints = [
        ('serial_no', 'unique(serial_no)', "其它设备已经使用了这个设备编号"),
    ]

    @api.model
    def create(self, vals):
        equipment = super(MaintenanceEquipment, self).create(vals)
        if equipment.owner_user_id:
            equipment.message_subscribe(partner_ids=[equipment.owner_user_id.partner_id.id])
        return equipment

    @api.multi
    def write(self, vals):
        if vals.get('owner_user_id'):
            self.message_subscribe(partner_ids=self.env['res.users'].browse(vals['owner_user_id']).partner_id.ids)
        return super(MaintenanceEquipment, self).write(vals)

    @api.model
    def _read_group_category_ids(self, categories, domain, order):
        """ Read group customization in order to display all the categories in
            the kanban view, even if they are empty.
        """
        category_ids = categories._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)

    def _create_new_request(self, date):
        self.ensure_one()
        self.env['my_equipment_maintenance.request'].create({
            'name': _('预防性维护 - %s') % self.id,
            'request_date': date,
            'schedule_date': date,
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'my_equipment_maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.technician_user_id.id,
            'duration': self.my_equipment_maintenance_duration,
            })

    @api.model
    def _cron_generate_requests(self):
        """
            Generates my_equipment_maintenance request on the next_action_date or today if none exists
        """
        for equipment in self.search([('period', '>', 0)]):
            next_requests = self.env['my_equipment_maintenance.request'].search([('stage_id.done', '=', False),
                                                    ('equipment_id', '=', equipment.id),
                                                    ('my_equipment_maintenance_type', '=', 'preventive'),
                                                    ('request_date', '=', equipment.next_action_date)])
            if not next_requests:
                equipment._create_new_request(equipment.next_action_date)


class MaintenanceRequest(models.Model):
    _name = 'my_equipment_maintenance.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '维护请求'
    _order = "id desc"

    @api.returns('self')
    def _default_stage(self):
        return self.env['my_equipment_maintenance.stage'].search([], limit=1)

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'stage_id' in init_values and self.stage_id.sequence <= 1:
            return 'my_equipment_maintenance.mt_req_created'
        elif 'stage_id' in init_values and self.stage_id.sequence > 1:
            return 'my_equipment_maintenance.mt_req_status'
        return super(MaintenanceRequest, self)._track_subtype(init_values)

    name = fields.Char('维修单编号')
    description = fields.Text('描述')
    internal_notes = fields.Text('备注')
    request_date = fields.Date('请求日期', track_visibility='onchange', default=fields.Date.context_today,
                               help="要求维修实施的时间。")
    owner_user_id = fields.Many2one('res.users', string='创建人', default=lambda s: s.env.uid)
    category_id = fields.Many2one('my_equipment_maintenance.equipment.category', related='equipment_id.category_id',
                                  string='分类', store=True, readonly=True)
    equipment_id = fields.Many2one('my_equipment_maintenance.equipment', string='设备',
                                   ondelete='restrict', index=True, required=True)
    user_id = fields.Many2one('res.users', string='技术员', track_visibility='onchange',
                              oldname='technician_user_id')
    stage_id = fields.Many2one('my_equipment_maintenance.stage', string='阶段', ondelete='restrict',
                               track_visibility='onchange',
                               group_expand='_read_group_stage_ids', default=_default_stage)
    priority = fields.Selection([('0', '很低'), ('1', '低'), ('2', '一般'), ('3', '高')], string='优先级')
    color = fields.Integer('颜色索引')
    close_date = fields.Date('关闭日期', help="Date the my_equipment_maintenance was finished. ")
    kanban_state = fields.Selection([('normal', '进行中'), ('blocked', '受阻'), ('done','已为下阶段准备好')],
                                    string='看板状态', required=True, default='normal', track_visibility='onchange')
    # active = fields.Boolean(default=True, help="Set active to false to hide the my_equipment_maintenance request
    # without deleting it.")
    archive = fields.Boolean(default=False, help="使用存档来讲维护请求在不删除的情况下不可见。")
    my_equipment_maintenance_type = fields.Selection([('corrective', '纠正'), ('preventive', '预防')],
                                                     string='维护类型', default="preventive")
    schedule_date = fields.Date('计划日期', help="维护团队期望的实施日期")
    duration = fields.Float('用时', help="用小时和分钟表示的时间")
    operations = fields.One2many(
        'maintenance.line', 'maintenance_id', 'Parts',
        copy=True, readonly=False)

    @api.multi
    def archive_equipment_request(self):
        self.write({'archive': True})

    @api.multi
    def reset_equipment_request(self):
        """ Reinsert the my_equipment_maintenance request into the my_equipment_maintenance pipe in the first stage"""
        first_stage_obj = self.env['my_equipment_maintenance.stage'].search([], order="sequence asc", limit=1)
        # self.write({'active': True, 'stage_id': first_stage_obj.id})
        self.write({'archive': False, 'stage_id': first_stage_obj.id})

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            self.user_id = self.equipment_id.technician_user_id

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        self = self.with_context(mail_create_nolog=True)
        request = super(MaintenanceRequest, self).create(vals)
        if request.owner_user_id or request.user_id:
            request._add_followers()
        request.activity_update()
        return request

    @api.multi
    def write(self, vals):
        # Overridden to reset the kanban_state to normal whenever
        # the stage (stage_id) of the Maintenance Request changes.
        if vals and 'kanban_state' not in vals and 'stage_id' in vals:
            vals['kanban_state'] = 'normal'
        res = super(MaintenanceRequest, self).write(vals)
        if vals.get('owner_user_id') or vals.get('user_id'):
            self._add_followers()
        if 'stage_id' in vals:
            self.filtered(lambda m: m.stage_id.done).write({'close_date': fields.Date.today()})
            self.activity_feedback(['my_equipment_maintenance.mail_act_my_equipment_maintenance_request'])
        if vals.get('user_id') or vals.get('schedule_date'):
            self.activity_update()
        if vals.get('equipment_id'):
            # need to change description of activity also so unlink old and create new activity
            self.activity_unlink(['my_equipment_maintenance.mail_act_my_equipment_maintenance_request'])
            self.activity_update()
        return res

    def activity_update(self):
        """ Update my_equipment_maintenance activities based on current record set state.
        It reschedule, unlink or create my_equipment_maintenance request activities. """
        self.filtered(lambda request: not request.schedule_date).activity_unlink(['my_equipment_maintenance.'
                                                                    'mail_act_my_equipment_maintenance_request'])
        for request in self.filtered(lambda request: request.schedule_date):
            date_dl = fields.Datetime.from_string(request.schedule_date).date()
            updated = request.activity_reschedule(
                ['my_equipment_maintenance.mail_act_my_equipment_maintenance_request'],
                date_deadline=date_dl,
                new_user_id=request.user_id.id or request.owner_user_id.id or self.env.uid)
            if not updated:
                if request.equipment_id:
                    note = _('Request planned for <a href="#" data-oe-model="%s" data-oe-id="%s">%s</a>') % (
                        request.equipment_id._name, request.equipment_id.id, request.equipment_id.display_name)
                else:
                    note = False
                request.activity_schedule(
                    'my_equipment_maintenance.mail_act_my_equipment_maintenance_request',
                    fields.Datetime.from_string(request.schedule_date).date(),
                    note=note, user_id=request.user_id.id or request.owner_user_id.id or self.env.uid)

    def _add_followers(self):
        for request in self:
            partner_ids = (request.owner_user_id.partner_id + request.user_id.partner_id).ids
            request.message_subscribe(partner_ids=partner_ids)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


class RepairLine(models.Model):
    _name = 'maintenance.line'
    _description = '维护用零件'
    name = fields.Text('描述')
    maintenance_id = fields.Many2one(
            'my_equipment_maintenance.request', '维护单编号',
            index=True, ondelete='cascade')
    product_id = fields.Many2one('equipment.parts', '产品', required=True)
    product_uom_qty = fields.Integer(
            '数量', default=1, required=True)


