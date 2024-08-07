# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests.common import Form, SavepointCase


class TestProductAttributeMerge(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.wizard_model = cls.env["wizard.product.attribute.merge"]

        # ----
        cls.setUpClassTemplate()
        cls.setUpClassAttribute()
        cls.setUpClassProduct()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.setUpClassCommon()

    @classmethod
    def setUpClassTemplate(cls):
        cls.template_model = cls.env["product.template"]
        cls.pen = cls.template_model.create({"name": "pen"})
        cls.car = cls.template_model.create({"name": "car"})

    @classmethod
    def setUpAttributes(cls):
        # create from_attribute with one color
        cls.from_attribute = cls.env["product.attribute"].create({"name": "Old color"})
        cls.from_attribute_value = cls.env["product.attribute.value"].create(
            {"name": "Red", "attribute_id": cls.from_attribute.id}
        )
        # create into_attribute with one color
        cls.into_attribute = cls.env["product.attribute"].create({"name": "New color"})
        cls.into_attribute_value = cls.env["product.attribute.value"].create(
            {"name": "Red", "attribute_id": cls.into_attribute.id}
        )


    @classmethod
    def setUpClassAttribute(cls):
        cls.attribute_model = cls.env["product.attribute"]
        cls.attribute_value_model = cls.env["product.attribute.value"]
        cls.template_attribute_line_model = cls.env["product.template.attribute.line"]
        cls.template_attribute_value_model = cls.env["product.template.attribute.value"]
        cls.color_attribute = cls.attribute_model.create({"name": "color"})
        cls.values = cls.env["product.attribute.value"]
        for color in ["red", "blue", "green", "black"]:
            value = cls.attribute_value_model.create(
                {"attribute_id": cls.color_attribute.id, "name": color}
            )
            setattr(cls, color, value)
            cls.values |= value

    @classmethod
    def setUpClassProduct(cls):
        cls.product_model = cls.env["product.product"]
        cls.pen_attribute_line = cls.template_attribute_line_model.create(
            {
                "product_tmpl_id": cls.pen.id,
                "attribute_id": cls.color_attribute.id,
                "value_ids": [(6, 0, cls.values.ids)],
            }
        )
        cls.car_attribute_line = cls.template_attribute_line_model.create(
            {
                "product_tmpl_id": cls.car.id,
                "attribute_id": cls.color_attribute.id,
                "value_ids": [(6, 0, cls.values.ids)],
            }
        )
        cls.attribute_lines = cls.pen_attribute_line | cls.car_attribute_line

    @classmethod
    def setUpClassCommon(cls):
        cls.red_template_values = cls.template_attribute_value_model.search(
            [("product_attribute_value_id", "=", cls.red.id)]
        )
        cls.red_products = cls.red_template_values.ptav_product_variant_ids
        cls.red_templates = cls.red_products.mapped("product_tmpl_id")
        # Probably a way to do better
        pen_template_value = cls.template_attribute_value_model.search(
            [
                ("product_attribute_value_id", "=", cls.red.id),
                ("attribute_line_id", "=", cls.pen_attribute_line.id),
            ]
        )
        cls.red_pen = pen_template_value.ptav_product_variant_ids

    @classmethod
    def _get_template_line_from_templates(cls, product_tmpls):
        return cls.template_attribute_line_model.search(
            [
                "|",
                ("active", "=", True),
                ("active", "=", False),
                ("product_tmpl_id", "in", product_tmpls.ids),
            ]
        )

    def assertNone(self, iterable):
        return self.assertFalse(any(iterable))

    def assertAll(self, iterable):
        return self.assertTrue(all(iterable))

    #------------------------------------------

    def _get_wizard(self, product_attribute):
        context = {
            "active_model": self.env["product.attribute"], 
            "active_ids": product_attribute.ids
        }
        return self.env["wizard.product.attribute.merge"].with_context(context)


    #------------------------------------------


    def test_merge(self):
        # create from_attribute with one color
        from_attribute = self.color_attribute

        from_attribute = self.color_attribute

        into_attribute = self.env.ref("product.product_attribute_2")
        # wizard_model = self.env["wizard.product.attribute.merge"].with_context(
        #     active_model=self.env["product.attribute"],
        #     active_ids=from_attribute.ids,
        # )
        wizard_model = self._get_wizard(from_attribute)
        # wiz = wiz_model.create({"product_attribute_id": self.color_attribute.id})
        with Form(wizard_model) as form:
            # assert correct attribute is selected
            self.assertTrue(form.product_attribute_id == from_attribute)

            # select the into_attribute
            form.into_product_attribute_id = into_attribute     
            self.assertTrue(form.into_product_attribute_id == into_attribute)

            # assert only one action
            breakpoint()
            self.assertTrue(len(form.attribute_values_merge_action_ids) == 1)

            # check action is marked as merge
            action_line = form.attribute_values_merge_action_ids[0]
            self.assertTrue(action_line.attribute_value_action == "merge")

            # apply merge (clicking VALIDATE button)
            form.action_merge()

        # assert the old attribute has been removed

        # assert the into_attribute has the color attribute added


    def test_merge_one(self):
        """ """
        # Has White, Black
        color= self.env.ref("product.product_attribute_2")
        colour = self.env.ref("product_attribute_merge.attribute_colour")
        wizard = self._get_wizard(color)
        wizard.into_product_attribute_id = colour
        wizard._onchange_merge_into_product_attribute_id()
        # Fix me there is 4 actions I am not sure why ?
        # actions = wizard.attribute_values_merge_action_ids.mapped("attribute_value_action")
        wizard.action_merge()
        # Not sure how to call the action_merge method ?
        # with Form(wizard) as form: 
        #     form.into_product_attribute_id = colour

    def _get_value_related_variant(self, value):
        return value.pav_attribute_line_ids.product_template_value_ids.filtered(
            lambda ptv: ptv.product_attribute_value_id == value
        ).ptav_product_variant_ids

    def test_move_value_attribute_not_used_on_product(self):
        # Has White, Black
        color= self.env.ref("product.product_attribute_2")
        # Has Black, Pink, Orange
        colour = self.env.ref("product_attribute_merge.attribute_colour")
        # Move White to colour
        value_to_move = self.env.ref("product.product_attribute_value_3")
        related_variant_before = self._get_value_related_variant(value_to_move)
        wizard = self._get_wizard(colour)
        wizard._move_attribute_value(value_to_move, colour)
        self.assertTrue(value_to_move not in color.value_ids)
        self.assertTrue(value_to_move in colour.value_ids)
        # TODO check same products have the attribute
        related_variant_after = self._get_value_related_variant(value_to_move)
        self.assertEqual(related_variant_before, related_variant_after)

    def test_move_value_attribute_used_on_product(self):
        product_4 =  self.env.ref("product.product_product_4")
        # Has White, Black
        color= self.env.ref("product.product_attribute_2")
        # Has Black, Pink, Orange
        colour = self.env.ref("product_attribute_merge.attribute_colour")
        pink = self.env.ref("product_attribute_merge.attribute_value_pink")
        # Add Pink to the variant we will move White
        ptal = self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": product_4.product_tmpl_id.id,
                "attribute_id": colour.id,
                "value_ids": [(6, 0, pink.ids)]

            }
        )
        # Move White to colour
        value_to_move = self.env.ref("product.product_attribute_value_3")
        related_variant_before = self._get_value_related_variant(value_to_move)
        wizard = self._get_wizard(colour)
        wizard._move_attribute_value(value_to_move, colour)
        self.assertTrue(value_to_move not in color.value_ids)
        self.assertTrue(value_to_move in colour.value_ids)
        # TODO check same products have the attribute
        related_variant_after = self._get_value_related_variant(value_to_move)
        self.assertEqual(related_variant_before, related_variant_after)

    def test_move_value_attribute_only_one_value_on_ptal(self):
        # Has White, Black
        colour = self.env.ref("product.product_attribute_2")
        # Has Black, Pink, Orange
        colour = self.env.ref("product_attribute_merge.attribute_colour")
        # Remove the black from the ptal
        black = self.env.ref("product.product_attribute_value_4")
        colour.attribute_line_ids.value_ids = [(2, black.id, 0)]
        # Move White to colour
        value_to_move = self.env.ref("product.product_attribute_value_3")
        related_variant_before = self._get_value_related_variant(value_to_move)
        wizard = self._get_wizard(colour)
        wizard._move_attribute_value(value_to_move, colour)
        self.assertTrue(value_to_move not in colour.value_ids)
        self.assertTrue(value_to_move in colour.value_ids)
        # TODO check same products have the attribute
        related_variant_after = self._get_value_related_variant(value_to_move)
        self.assertEqual(related_variant_before, related_variant_after)

    def test_delete_value_unused(self):
        colour = self.env.ref("product.product_attribute_2")
        colour = self.env.ref("product_attribute_merge.attribute_colour")
        value_to_delete = self.env.ref("product_attribute_merge.attribute_value_orange")
        self.assertTrue(value_to_delete in colour.value_ids)
        wizard = self._get_wizard(colour)
        wizard._delete_attribute_value(value_to_delete)
        self.assertTrue(value_to_delete not in colour.value_ids)
