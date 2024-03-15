# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductAttributeMergeValueAction(models.TransientModel):
    _name = "product.attribute.merge.value.action"
    _description = "Wizard action to merge variant attribute value"
    _order = "attribute_value_id"

    attribute_value_id = fields.Many2one(
        comodel_name="product.attribute.value" #, ondelete="cascade"
    )
    attribute_value_action = fields.Selection(
        selection="_selection_action",
        default="do_nothing",
        required=True,
    )
    merge_into_attribute_id = fields.Many2one(
        comodel_name="product.attribute"
    )
    available_attribute_value_ids = fields.One2many(related="merge_into_attribute_id.value_ids")
    merge_into_attribute_value_id = fields.Many2one(
        comodel_name="product.attribute.value", # , ondelete="cascade"
        domain="[('id', 'in', available_attribute_value_ids)]"
    )

    def _selection_action(self):
        return [
            ("merge", "Merge"),
            ("move", "Move"),
            ("delete", "Delete"),
        ]
