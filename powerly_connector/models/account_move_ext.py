from odoo import models, fields, api



class AccountMoveExt(models.Model):
    _inherit = 'account.move'

    powerly_order_id = fields.Many2one('powerly.orders', string='Powerly Order')