# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WizardProductAttributeMerge(models.TransientModel):
    _name = "wizard.product.attribute.merge"
    _description = "Merge Product Attribute"

    # product_attribute_value_id = fields.Many2one(comodel_name="product.attribute.value", string="Merge Attribute", readonly=True)

    product_attribute_id = fields.Many2one(comodel_name="product.attribute", string="Merge Attribute", readonly=True)
    into_product_attribute_id = fields.Many2one(comodel_name="product.attribute", string="Into Attribute")


    @api.model
    def default_get(self, fields_list):
        """'default_get' method overloaded."""
        res = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids")
        if not active_ids:
            raise UserError(
                _("Please select at least one product attribute.")
            )
        res["product_attribute_id"] = active_ids[0]
        return res

    def action_merge(self):
        self.ensure_one()
        return
