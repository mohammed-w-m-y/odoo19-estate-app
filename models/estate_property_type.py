from odoo import fields, models, api


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    # ---- Chapter 11: List Ordering ----
    _order = "sequence, name"

    name = fields.Char(string="Name", required=True)