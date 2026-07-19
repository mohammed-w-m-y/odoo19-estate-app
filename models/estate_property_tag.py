from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"

    # ---- Chapter 11: List Ordering ----
    _order = "name"

    name = fields.Char(string="Name", required=True)

    # ---- Chapter 11: Color Picker Option ----
    color = fields.Integer(string="Color")

    # ---- Chapter 10: SQL Constraints ----
    _unique_tag_name = models.Constraint(
        "UNIQUE(name)",
        "The property tag name must be unique."
    )
