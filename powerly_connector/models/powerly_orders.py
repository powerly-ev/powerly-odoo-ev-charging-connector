from odoo import models, fields, api
from odoo.exceptions import UserError


class PowerlyOrders(models.Model):
    _name = 'powerly.orders'
    _description = 'Powerly Orders'
    _rec_name = 'id'

    # Core fields from API response
    external_id = fields.Integer(string="Powerly Orders ID", index=True)
    charge_point_id = fields.Integer(string="Charge Point ID")
    charge_point_connector_id = fields.Integer(string="Connector ID")
    charging_session_time = fields.Float(string="Session Time")
    charging_session_energy = fields.Float(string="Session Energy")
    unit = fields.Char(string="Unit")
    requested_quantity = fields.Float(string="Requested Quantity")
    status = fields.Integer(string="Status")
    delivery_date = fields.Datetime(string="Delivery Date")
    user_id = fields.Integer(string="User ID")
    fleet_id = fields.Integer(string="Fleet ID")
    quantity = fields.Float(string="Quantity")
    price = fields.Float(string="Price")
    fees = fields.Float(string="Fees")
    earning = fields.Float(string="Earning")
    unit_price = fields.Float(string="Unit Price")
    connector_number = fields.Integer(string="Connector Number")

    # Relations
    charger_id = fields.Many2one('powerly.charger', string="Charger")
    feedback_ids = fields.Many2many('powerly.orders.feedback',string="Feedback")
    invoice_id = fields.Many2one('account.move',string="Invoice")

    @api.model
    def sync_all(self):
        service = self.env['powerly.api.service'].sudo()
        data = service.get_orders()
        items = data.get('results', {}).get('data', [])
        # Add dummy data if items is empty
        if not items:
            items = [{
                'id': 426,
                'charge_point_id': 16,
                'charge_point_connector_id': 16,
                'charging_session_time': '27.0000',
                'charging_session_energy': '1661.0000',
                'unit': 'minutes',
                'requested_quantity': '8',
                'status': 1,
                'delivery_date': '2024-09-16 07:33:27',
                'user_id': 11,
                'fleet_id': 64,
                'quantity': '6.0000',
                'price': '0.00',
                'fees': '8.00',
                'earning': '953.47',
                'unit_price': '2587.98',
                'connector_number': 1,
            }]
        for item in items:
            self._create_or_update(item)

    def _create_or_update(self, payload):
        ext_id = payload.get('id')
        rec = self.search([('external_id', '=', ext_id)], limit=1)

        # Find related charger
        charger = self.env['powerly.charger'].search([
            ('external_id', '=', payload.get('charge_point')['id'])
        ], limit=1)
        # Create charger if not found
        if not charger and payload.get('charge_point')['id']:
            charger = self.env['powerly.charger'].with_context(skip_powerly_sync=True).create({
                'external_id': payload.get('charge_point')['id'],
                'title': f"Charger {payload.get('charge_point')['title']}",
                'identifier': f"charger_{payload.get('charge_point')['identifier']}",
                'latitude': payload.get('charge_point')['latitude'],
                'longitude': payload.get('charge_point')['longitude'],
                'address_line_1': payload.get('charge_point')['address']['address_line_1'],
                'address_line_2': payload.get('charge_point')['address']['address_line_2'],
                'address_line_3': payload.get('charge_point')['address']['address_line_3'],
                'zipcode': payload.get('charge_point')['address']['zipcode'],
                'city': payload.get('charge_point')['address']['city'],
                'state': payload.get('charge_point')['address']['state'],
            })
        vals = {
            'external_id': ext_id,
            'charge_point_id': payload.get('charge_point_id'),
            'charge_point_connector_id': payload.get('charge_point_connector_id'),
            'charging_session_time': float(payload.get('charging_session_time', 0)),
            'charging_session_energy': float(payload.get('charging_session_energy', 0)),
            'unit': payload.get('unit'),
            'requested_quantity': float(payload.get('requested_quantity', 0)),
            'status': payload.get('status'),
            'delivery_date': payload.get('delivery_date'),
            'user_id': payload.get('user_id'),
            'fleet_id': payload.get('fleet_id'),
            'quantity': float(payload.get('quantity', 0)),
            'price': float(payload.get('price', 0)),
            'fees': float(payload.get('fees', 0)),
            'earning': float(payload.get('earning', 0)),
            'unit_price': float(payload.get('unit_price', 0)),
            'connector_number': payload.get('connector_number'),
            'charger_id': charger.id if charger else False,
        }

        if rec:
            rec.write(vals)
        else:
            self.create(vals)

    def action_sync_single(self):
        if not self.external_id:
            raise UserError("Cannot sync order without external ID")

        service = self.env['powerly.api.service'].sudo()
        data = service.get_orders()
        items = data.get('results', {}).get('data', [])

        for item in items:
            if item.get('id') == self.external_id:
                self._create_or_update(item)
                return

        raise UserError(f"Order with ID {self.external_id} not found in API response")

    def action_update_feedback(self):
        for record in self:
            get_feedback = self.env['powerly.orders.feedback'].search([
                ('charge_point_order_id', '=', record.external_id)
            ])
            if get_feedback:
                record.write({
                    'feedback_ids': [(6, 0, get_feedback.ids)]
                })
            else:
                record.write({
                    'feedback_ids': [(5, 0, 0)]
                })

    def create_invoice(self):

        for record in self:
            if record.charger_id:
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'powerly_order_id': self.id,
                    'partner_id': self.env.company.partner_id.id,
                    'invoice_date': fields.Date.today(),
                    'invoice_line_ids': [
                        (0, 0, {
                            'name': record.charger_id.title,
                            'quantity': 1,
                            'price_unit': record.earning,
                        }),
                    ],
                })
                record.write({
                    'invoice_id': invoice.id,
                })
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'account.move',
                    'res_id': invoice.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
            else:
                raise UserError("Charger not found for this order")

