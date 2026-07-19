from odoo import fields, models, api


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    # ---- Chapter 11: List Ordering ----
    _order = "sequence, name"

    name = fields.Char(string="Name", required=True)

    # ---- Chapter 11: Manual Ordering ----
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")

    # ---- Chapter 11: Inline Views ----
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")

    # ---- Chapter 11: Stat Buttons ----
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

        # ---- Chapter 10: SQL Constraints ----
    _unique_type_name = models.Constraint(
        "UNIQUE(name)",
        "The property type name must be unique."
    )
