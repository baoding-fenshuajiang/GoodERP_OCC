# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class my_product_template(models.Model):
    _inherit = "product.template"

    name = fields.Char(translate=False)
    description = fields.Text(translate=False)
