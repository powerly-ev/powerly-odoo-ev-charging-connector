# powerly_integration/const.py

# -------------------------------
# Powerly API Constants
# -------------------------------


# Authentication
POWERLY_LOGIN_ENDPOINT = "/api/v3/auth/login"

# Power Sources / Chargers
POWERLY_CHARGERS_LIST = "/api/charge-points"
POWERLY_CHARGER_DETAIL = "/api/charge-points/{id}"

# Sessions / Orders
POWERLY_SESSIONS_LIST = "/api/v1/orders"
POWERLY_SESSION_DETAIL = "/api/v1/orders/{id}"
POWERLY_SESSION_START = "/api/v1/orders"       # POST
POWERLY_SESSION_STOP = "/api/v1/orders/{id}/stop"

# Users
POWERLY_USERS_LIST = "/api/v1/users"
POWERLY_USER_DETAIL = "/api/v1/users/{id}"

# Payments
POWERLY_PAYMENTS_LIST = "/api/v1/payments"
POWERLY_PAYMENT_DETAIL = "/api/v1/payments/{id}"

# Webhook Signature Defaults
WEBHOOK_SIGNATURE_HEADER = "Powerly-Signature"
WEBHOOK_SIGNATURE_FORMAT = "hex"  # or 'base64'
powerly_app_endpoint_orders = "/api/orders"
powerly_app_endpoint_feedbacks = "/api/feedback"