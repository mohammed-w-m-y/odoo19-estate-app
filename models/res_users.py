from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # ---- Chapter 12: Model Inheritance ----
    # Link salesperson to their properties with a domain strictly filtering available properties
    property_ids = fields.One2many(
        "estate.property",
        "seller_id",
        string="Properties",
        domain="[('state', 'in', ['new', 'offer_received'])]"
    )
