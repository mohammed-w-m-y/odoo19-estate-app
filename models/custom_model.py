from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    # ---- Chapter 11: List Ordering ----
    _order = "id desc"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")

    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: fields.Date.add(fields.Date.today(), months=3)
    )

    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area")
    garage = fields.Boolean(string="Garage")

    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string="Garden Orientation")

    active = fields.Boolean(string="Active", default=True)

    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], string="Status", required=True, copy=False, default='new')

    # ---- Chapter 7: Relational Fields ----
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    seller_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # ---- Chapter 8: Computed Fields ----
    total_area = fields.Integer(string="Total Area", compute="_compute_total_area")
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")

    # ---- Chapter 10: SQL Constraints (The Modern Way for Odoo 19) ----
    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'The expected price must be strictly positive.'
    )
    _check_selling_price = models.Constraint(
        'CHECK(selling_price >=0)',
        'The selling price must be positive.'
    )

    # Calculate total area as the sum of living area and garden area
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    # Calculate the highest offer price received using mapped()
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else 0.0

    # Auto-fill garden features when garden field is toggled
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # ---- Chapter 9: Action Buttons ----

    def action_set_sold(self):
        """Set the property state as Sold unless it is Canceled"""
        for record in self:
            if record.state == 'canceled':
                raise UserError("A canceled property cannot be set as sold!")
            record.state = 'sold'
        return True

    def action_set_canceled(self):
        """Set the property state as Canceled unless it is Sold"""
        for record in self:
            if record.state == 'sold':
                raise UserError("A sold property cannot be canceled!")
            record.state = 'canceled'
        return True

    # ---- Chapter 10: Python Constraints ----
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price_positive(self):
        """Ensure selling price is at least 90% of expected price (only when selling price is set)"""
        for record in self:
            if not float_is_zero(record.selling_price, precision_rounding=0.01):
                limit_price = record.expected_price * 0.90
                if float_compare(record.selling_price, limit_price, precision_rounding=0.01) < 0:
                    raise ValidationError("The selling price cannot be lower than 90% of the expected price!")

    # ---- Chapter 12: CRUD Methods Override ----
    @api.ondelete(at_uninstall=False)
    def _check_property_deletion(self):
        """Prevent deletion of a property if its state is not 'New' or 'Canceled'"""
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise UserError("You cannot delete a property that is not New or Canceled!")
