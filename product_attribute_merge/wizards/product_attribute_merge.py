# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WizardProductAttributeMerge(models.TransientModel):
    _name = "wizard.product.attribute.merge"
    _description = "Merge Product Attribute"

    product_attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Merge Attribute",
        readonly=True
    )
    into_product_attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Into Attribute"
    )
    attribute_values_merge_action_ids = fields.Many2many(
        comodel_name="product.attribute.merge.value.action",
        relation="wizard_product_attribute_merge_action_rel"
    )

    @api.model
    def default_get(self, fields_list):
        """'default_get' method overloaded."""
        res = super().default_get(fields_list)
        # active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids")
        if not active_ids:
            raise UserError(
                _("Please select at least one product attribute.")
            )
        res["product_attribute_id"] = active_ids[0]
        return res

    @api.onchange("into_product_attribute_id")
    def _onchange_merge_into_product_attribute_id(self):
        for record in self:
            actions = record._get_actions_for_values(
                record.product_attribute_id,
                record.into_product_attribute_id
            )
            record.attribute_values_merge_action_ids = [(6, 0, actions.ids)]

    @api.model
    def _get_actions_for_values(self, attribute_to_merge, attribute_merge_into):
        res = self.env["product.attribute.merge.value.action"].create(
            [
                {
                    "attribute_value_id": value.id,
                    "attribute_value_action": "delete",
                    "merge_into_attribute_value_id": attribute_merge_into.id,
                }
                for value in attribute_to_merge.value_ids
            ]
        )
        return res

    def action_merge(self):
        self.ensure_one()
        return
