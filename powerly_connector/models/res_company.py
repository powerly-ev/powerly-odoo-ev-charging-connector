from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
from cryptography.fernet import Fernet
import base64
from ..const import (
    POWERLY_LOGIN_ENDPOINT,
    POWERLY_CHARGERS_LIST,
    POWERLY_CHARGER_DETAIL,
    POWERLY_SESSIONS_LIST,
    POWERLY_SESSION_DETAIL,
    POWERLY_SESSION_START,
    POWERLY_SESSION_STOP,
    POWERLY_USERS_LIST,
    POWERLY_USER_DETAIL,
    POWERLY_PAYMENTS_LIST,
)

class ResCompany(models.Model):
    _inherit = 'res.company'

    powerly_username = fields.Char(string='Powerly Username')
    powerly_password = fields.Char(string='powerly Password')
    powerly_api_key = fields.Char(string='Powerly API Key')
    powerly_webhook_secret_key = fields.Char(string='Powerly Webhook Secret Key')
    powerly_bearer_token = fields.Char(string="Powerly Bearer Token")
    is_subscribed = fields.Boolean(string="Is Subscribed")
    subscription_features = fields.Char(string="Subscription Features")
    subscription_ends = fields.Date(string="Subscription Ends")
    powerly_bearer_token_expiry = fields.Integer(string="Powerly Token Expiry")
    powerly_base_url = fields.Char(string="Powerly Base URL")
    powerly_partner_id = fields.Many2one('res.partner', string='Powerly Partner')

    def _get_encryption_key(self):
        """
        Get or create encryption key from ir.config_parameter.
        This key should be stored securely and backed up.
        """
        ICP = self.env['ir.config_parameter'].sudo()
        key = ICP.get_param('powerly.encryption.key')

        if not key:
            # Generate a new key if it doesn't exist
            key = Fernet.generate_key().decode()
            ICP.set_param('powerly.encryption.key', key)

        return key.encode()

    def _encrypt_password(self, password):
        """Encrypt the password before storing"""
        if not password:
            return False

        key = self._get_encryption_key()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(password.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt_password(self, encrypted_password):
        """Decrypt the password when needed"""
        if not encrypted_password:
            return False

        try:
            key = self._get_encryption_key()
            cipher = Fernet(key)
            decrypted = cipher.decrypt(base64.b64decode(encrypted_password))
            return decrypted.decode()
        except Exception as e:
            raise UserError(f"Failed to decrypt password: {str(e)}")

    @api.model
    def create(self, vals):
        """Override create to encrypt password"""
        if vals.get('powerly_password'):
            vals['powerly_password'] = self._encrypt_password(vals['powerly_password'])
        return super(ResCompany, self).create(vals)

    def write(self, vals):
        """Override write to encrypt password"""
        if vals.get('powerly_password'):
            vals['powerly_password'] = self._encrypt_password(vals['powerly_password'])
        return super(ResCompany, self).write(vals)

    # member function to set the powerly_bearer_token and subscription details
    def set_powerly_details(self):
        if not self.powerly_username:
            raise UserError("Powerly Username is required")
        if not self.powerly_password:
            raise UserError("Powerly Password is required")
        if not self.powerly_base_url:
            raise UserError("Please provide Powerly Base URL")

        decrypted_password = self._decrypt_password(self.powerly_password)

        data = self.get_access_token(self.powerly_username, decrypted_password)
        if not data:
            raise UserError("Failed to get authentication data from Powerly")
        if not data.get('access_token'):
            raise UserError("Access token not received from Powerly")

        self.powerly_bearer_token = data.get('access_token')
        self.is_subscribed = data.get('isSubscribed')
        self.subscription_features = data.get('subscriptionFeatures', '[]')
        self.subscription_ends = data.get('subscriptionEnds', None)

    def get_access_token(self, email, password):
        if self.powerly_api_key:
            base_url = self.powerly_base_url
            url = f"{base_url}{POWERLY_LOGIN_ENDPOINT}"
            data = {
                'email': email,
                'password': password
            }

            headers = {
                'api-key': self.powerly_api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'User-Agent': 'PostmanRuntime/7.49.0',
            }

            try:
                response = requests.post(url, headers=headers, data=data)
                response.raise_for_status()
                return response.json().get('data')
            except requests.exceptions.RequestException as e:
                raise UserError(f'User Error (There is a problem in authenticating with powerly) :  {e}')

    def get_powerly_config(self):
        return {
            'api_key': self.powerly_api_key,
            'access': self.powerly_bearer_token,
            'webhook_secret': self.powerly_webhook_secret_key,
        }

