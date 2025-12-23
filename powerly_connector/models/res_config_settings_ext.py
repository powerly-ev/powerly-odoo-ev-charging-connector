from odoo import models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_sync_powerly_orders(self):
        self.env['powerly.orders'].sudo().sync_all()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Orders synced successfully!',
                'type': 'success',
            }
        }

    def action_sync_powerly_feedback(self):
        self.env['powerly.orders.feedback'].sudo().sync_all()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Orders synced successfully!',
                'type': 'success',
            }
        }

