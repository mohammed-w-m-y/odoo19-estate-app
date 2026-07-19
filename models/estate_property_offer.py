from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from datetime import timedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    # ---- Chapter 11: List Ordering ----
    _order = "price desc"

    price = fields.Float(string="Price")
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused')],
        string="Status",
        copy=False
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)

    # ---- Chapter 11: Stat Buttons (Related Field) ----
    property_type_id = fields.Many2one(
        "estate.property.type",
        related="property_id.property_type_id",
        string="Property Type",
        store=True
    )

    # ---- Chapter 8: Offer Validity Fields ----
    validity = fields.Integer(string="Validity (Days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    # ---- Chapter 10: SQL Constraints ----
    _check_offer_price = models.Constraint(
        "CHECK(price > 0)",
        "The offer price must be strictly positive."
    )

    # Compute deadline date based on creation date and validity days
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            base_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = base_date + timedelta(days=record.validity)

    # Recalculate validity days inversely when deadline date is manually updated
    def _inverse_date_deadline(self):
        for record in self:
            base_date = record.create_date.date() if record.create_date else fields.Date.today()
            if record.date_deadline:
                delta = record.date_deadline - base_date
                record.validity = delta.days
            else:
                record.validity = 7

    # ---- Chapter 9: Offer Actions ----

    def action_accept_offer(self):
        """Accept the offer, set buyer and selling price on the property, and change its state"""
        for record in self:
            accepted_offers = record.property_id.offer_ids.filtered(lambda o: o.status == 'accepted')
            if accepted_offers:
                raise UserError("An offer has already been accepted for this property!")

            record.status = 'accepted'
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = 'offer_accepted'
        return True

    def action_refuse_offer(self):
        """Refuse the current offer"""
        for record in self:
            record.status = 'refused'
        return True

    # ---- Chapter 12: Override Create Method ----
    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to check offer price logic and update property state"""
        for vals in vals_list:
            property_id = self.env['estate.property'].browse(vals['property_id'])

            # Check if the new offer price is lower than any existing offer for this property
            if property_id.offer_ids:
                max_existing_price = max(property_id.offer_ids.mapped('price'))
                if float_compare(vals['price'], max_existing_price, precision_rounding=0.01) <= 0:
                    raise UserError("You cannot create an offer with a price lower than or equal to an existing offer!")

            # Automatically change property state to offer_received when a valid new offer is made
            property_id.state = 'offer_received'

        return super(EstatePropertyOffer, self).create(vals_list)
