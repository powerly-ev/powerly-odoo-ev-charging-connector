from odoo import models, fields, api
from odoo.exceptions import UserError


class PowerlyOrdersFeedback(models.Model):
    _name = 'powerly.orders.feedback'
    _description = 'Powerly Orders Feedback'
    _rec_name = 'message'

    title = fields.Char(string="Title")
    feedback_id = fields.Char(string="Feedback ID", index=True)
    charge_point_order_id = fields.Integer(string="Charge Point Order ID")
    message = fields.Text(string="Message", required=True)
    rating = fields.Char(string="Rating")
    feedback_date = fields.Char(string="Date")
    charger_id = fields.Many2one('powerly.charger', string="Charger")

    @api.model
    def sync_all(self):
        service = self.env['powerly.api.service'].sudo()
        data = service.get_feedback()
        items = data.get('results', {}).get('data', [])

        for item in items:
            self._create_or_update(item)

    def _create_or_update(self, payload):
        feedback_id = payload.get('id')
        rec = self.search([('feedback_id', '=', feedback_id)], limit=1)

        charger = self.env['powerly.charger'].search([
            ('external_id', '=', payload.get('charge_point')['id'])
        ], limit=1)

        vals = {
            'feedback_id': feedback_id,
            'charge_point_order_id': payload.get('charge_point_order_id'),
            'title': payload.get('charge_point')['title'],
            'message': payload.get('feedback_msg', ''),
            'rating': payload.get('rating'),
            'feedback_date': payload.get('insert_date'),
            'charger_id': charger.id if charger else False,
        }

        if rec:
            rec.write(vals)
        else:
            self.create(vals)