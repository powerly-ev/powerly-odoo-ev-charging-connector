# powerly_integration/models/powerly_api.py

import requests, logging, time
from odoo import models, api, _
from odoo.exceptions import UserError

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
    powerly_app_endpoint_orders,
    powerly_app_endpoint_feedbacks,
)

_logger = logging.getLogger(__name__)
import json

class PowerlyAPIService(models.AbstractModel):
    _name = "powerly.api.service"
    _description = "Powerly API Service"

    # ------------------------
    # Shared Helpers
    # ------------------------

    def _get_param(self, key, default=None):
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    def _headers(self, with_bearer=True):
        api_key = self.env.company.powerly_api_key
        if not api_key:
            raise UserError("Powerly API key is missing (powerly.api_key).")
        headers = {
            "API-KEY": api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'PostmanRuntime/7.49.0',
        }
        if with_bearer:
            token = self._get_bearer_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"

        return headers

    def _request(self, method, endpoint, params=None, json_body=None, with_bearer=True):
        base_url = self.env.company.powerly_base_url
        url = f"{base_url}{endpoint}"

        try:
            response = requests.request(
                method,
                url,
                params=params,
                data=json_body,
                headers=self._headers(with_bearer=with_bearer),
                timeout=20,
            )
            print(response.status_code)
            print(response.text)
        except Exception as e:
            _logger.exception("Powerly API request error: %s", e)
            raise UserError(f"Powerly API Error: {e}")

        if response.status_code >= 400:
            _logger.error("Powerly API error %s %s", response.status_code, response.text)
            raise UserError(f"Powerly API Error: {response.text}")

        try:
            return response.json()
        except:
            return response.text

    # ------------------------
    # Authentication
    # ------------------------

    def _get_bearer_token(self):
        company = self.env.company
        base_url = company.powerly_base_url

        token = company.powerly_bearer_token
        expires_at = company.powerly_bearer_token_expiry or 0

        if token and time.time() < expires_at - 30:
            return token

        # login credentials stored on company?
        email = company.powerly_username
        password = company._decrypt_password(company.powerly_password)
        # password = company.powerly_password

        if not email or not password:
            return None

        resp = requests.post(
            f"{base_url}{POWERLY_LOGIN_ENDPOINT}",
            data={'email': email, 'password': password},
            headers={
                'API-KEY': company.powerly_api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'User-Agent': 'PostmanRuntime/7.49.0',
            },
            timeout=20
        )

        data = resp.json()

        token = data.get('access_token') or data.get('data', {}).get('access_token')
        expires_in = data.get('expires_in') or data.get('expires') or 3600
        is_subscribed = data.get('isSubscribed') or data.get('data', {}).get('isSubscribed')
        subscription_features = data.get('subscriptionFeatures') or data.get('data', {}).get('subscriptionFeatures')
        subscription_ends = data.get('subscriptionEnds') or data.get('data', {}).get('subscriptionEnds')
        company.powerly_bearer_token = token
        company.powerly_bearer_token_expiry = int(time.time() + int(expires_in))
        company.is_subscribed = is_subscribed
        company.subscription_features = subscription_features
        company.subscription_ends = subscription_ends

        return token

    # ------------------------
    # ENDPOINT WRAPPERS
    # ------------------------

    # Chargers
    def get_chargers(self, params=None):
        return self._request("GET", POWERLY_CHARGERS_LIST, params=params)

    def create_charger(self, payload):
        return self._request("POST", POWERLY_CHARGERS_LIST, json_body=payload)

    def get_charger(self, charger_id):
        return self._request("GET", POWERLY_CHARGER_DETAIL.format(id=charger_id))

    def delete_charger(self, charger_id):
        return self._request("DELETE", POWERLY_CHARGER_DETAIL.format(id=charger_id))

    def update_charger(self, charger_id, payload):
        return self._request("PATCH", POWERLY_CHARGER_DETAIL.format(id=charger_id), json_body=payload)

    # Sessions / Orders
    def get_sessions(self, params=None):
        return self._request("GET", POWERLY_SESSIONS_LIST, params=params)

    def get_session(self, session_id):
        return self._request("GET", POWERLY_SESSION_DETAIL.format(id=session_id))

    def start_session(self, payload):
        return self._request("POST", POWERLY_SESSION_START, json_body=payload)

    def stop_session(self, session_id):
        return self._request("POST", POWERLY_SESSION_STOP.format(id=session_id))

    # Users
    def get_users(self, params=None):
        return self._request("GET", POWERLY_USERS_LIST, params=params)

    def get_user(self, user_id):
        return self._request("GET", POWERLY_USER_DETAIL.format(id=user_id))

    # Payments
    def get_payments(self, params=None):
        return self._request("GET", POWERLY_PAYMENTS_LIST, params=params)

    # Add this method to PowerlyAPIService class
    def get_orders(self, params=None):
        endpoint = powerly_app_endpoint_orders

        return self._request("GET", endpoint, params=params)

    def get_feedback(self, params=None):
        endpoint = powerly_app_endpoint_feedbacks

        return self._request("GET", endpoint, params=params)


