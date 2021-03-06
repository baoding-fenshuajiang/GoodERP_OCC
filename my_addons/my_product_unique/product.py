# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import api,models, _
from odoo.exceptions import Warning


class product_product(models.Model):
    _inherit = "product.product"

    @api.multi
    @api.constrains('company_id', 'default_code', 'active')
    def check_unique_company_and_default_code(self):
        if self.active and self.default_code and self.company_id:
            filters = [('company_id', '=', self.company_id.id),
                       ('default_code', '=', self.default_code),
                       ('active', '=', True)]
            prod_ids = self.search(filters)
            if len(prod_ids) > 1:
                raise Warning(
                    _('There can not be two active products with the same Reference ode in the same company.'))
