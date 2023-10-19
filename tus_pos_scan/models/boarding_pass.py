from odoo import api, fields, models

class BoardingPass(models.Model):
    _name = 'boarding.pass'
    _description = 'BoardingPass'

    passenger_name = fields.Char(
        string='Passenger Name',
    )

    departure = fields.Char(
        string='Departure',
    )

    destination = fields.Char(
        string='Destination',
    )

    flight_company = fields.Char(
        string='Flight Company',
    )

    flight_number = fields.Char(
        string='Flight Number',
    )

    pos_id = fields.Many2one(
        comodel_name='pos.order',
        string='Pos Order',
        required=False
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=False
    )