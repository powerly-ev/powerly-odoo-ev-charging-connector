# powerly_integration/models/powerly_charger.py
from odoo import models, fields, api
from odoo.exceptions import UserError
import json

class PowerlyCharger(models.Model):
    _name = 'powerly.charger'
    _description = 'Powerly Power Source / Charger'
    _rec_name = "title"

    # Identity
    external_id = fields.Integer(string="Powerly Charger ID", index=True)
    identifier = fields.Char(string="Identifier")
    token = fields.Char(string="Token")

    # Classification
    category = fields.Selection([
        ('EV_CHARGER', 'EV Charger'),
        ('SMART_PLUG', 'Smart Plug'),
        ('SMART_METER', 'Smart Meter'),
    ], string="Category", default='EV_CHARGER')
    type = fields.Char(string="Type")
    status = fields.Selection([
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('unknown', 'Unknown'),
    ], string="Status", default='unknown')

    # Basic info
    title = fields.Char(string="Title")
    description = fields.Text(string="Description")

    # Location
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")
    listed = fields.Boolean(string="Listed")
    distance = fields.Float(string="Distance")

    # Limits / configuration
    session_limit_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('energy', 'Energy'),
    ], string="Session Limit Type", default='minutes')
    session_limit_value = fields.Float(string="Session Limit Value")
    online = fields.Boolean(string="Online")
    configured = fields.Boolean(string="Configured")
    secure = fields.Boolean(string="Secure")

    # Ratings / metrics
    rating = fields.Float(string="Rating")
    total_earnings = fields.Float(string="Total Earnings")
    total_energy = fields.Float(string="Total Energy")
    total_sessions_time = fields.Integer(string="Total Sessions Time")
    orders_count = fields.Integer(string="Orders Count")
    price = fields.Float(string="Price")
    price_usd = fields.Float(string="Price (USD)")
    reservation_fee = fields.Float(string="Reservation Fee")
    earning = fields.Float(string="Earning")

    # Availability / state
    is_external = fields.Boolean(string="Is External")
    is_in_use = fields.Boolean(string="In Use")
    is_reserved = fields.Boolean(string="Reserved")
    available = fields.Boolean(string="Available")
    next_reservation_near_now = fields.Datetime(string="Next Reservation (Near Now)")

    # Contact / schedule
    contact_number = fields.Char(string="Contact Number")
    open_time = fields.Char(string="Open Time")
    close_time = fields.Char(string="Close Time")

    # Address (flattened)
    address_line_1 = fields.Char(string="Address Line 1")
    address_line_2 = fields.Char(string="Address Line 2")
    address_line_3 = fields.Char(string="Address Line 3")
    zipcode = fields.Char(string="Zip Code")
    city = fields.Char(string="City")
    state = fields.Char(string="State")

    # Media and misc
    image_url = fields.Char(string="Image URL")
    external_details = fields.Json(string="External Details")
    media = fields.Json(string="Media")
    connectors = fields.Json(string="Connectors")
    amenities = fields.Json(string="Amenities")

    # Ownership
    owner_external_id = fields.Integer(string="Owner External ID")
    # If you have a user model, uncomment this and adjust the model name:
    # owner_id = fields.Many2one('powerly.user', string='Owner')
    owner_id = fields.Char(string='Owner')

    # Pricing unit
    price_unit = fields.Selection([
        ('minutes', 'Per Minute'),
        ('kwh', 'Per kWh'),
        ('session', 'Per Session'),
        ('unknown', 'Unknown'),
    ], string="Price Unit", default='unknown')

    get_orders_count = fields.Integer('Integer',compute='get_all_orders')

    def _vals_to_powerly_payload(self, vals):
        """Map local fields to Powerly POST payload."""
        addr = {
            'address_line_1': vals.get('address_line_1'),
            'address_line_2': vals.get('address_line_2'),
            'address_line_3': vals.get('address_line_3'),
            'zipcode': vals.get('zipcode'),
            'city': vals.get('city'),
            'state': vals.get('state'),
        }
        payload = {
            'identifier': vals.get('identifier'),
            'category': vals.get('category') or 'EV_CHARGER',
            'title': vals.get('title') or vals.get('name'),
            'description': vals.get('description'),
            'latitude': vals.get('latitude'),
            'longitude': vals.get('longitude'),
            'listed': bool(vals.get('listed')) if vals.get('listed') is not None else None,
            'type': vals.get('type'),
            'status': vals.get('status'),
            'image': vals.get('image_url'),
            'session_limit_type': vals.get('session_limit_type'),
            'session_limit_value': vals.get('session_limit_value'),
            'secure': bool(vals.get('secure')) if vals.get('secure') is not None else None,
            'configured': bool(vals.get('configured')) if vals.get('configured') is not None else None,
            # 'address': addr,
            'address_line_1': vals.get('address_line_1'),
            'address_line_2': vals.get('address_line_2'),
            'address_line_3': vals.get('address_line_3'),
            'zipcode': vals.get('zipcode'),
            'city': vals.get('city'),
            'state': vals.get('state'),
            # end here
            'price_unit': vals.get('price_unit'),
            'price': vals.get('price'),
            'reservation_fee': vals.get('reservation_fee'),
            'is_external': bool(vals.get('is_external')) if vals.get('is_external') is not None else None,
        }
        # Strip empty values to avoid API validation issues
        return {k: v for k, v in payload.items() if v not in (None, '', [])}

    @api.model
    def create(self, vals_list):
        """Create record(s) in Powerly first, then locally with returned IDs."""
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        records = self.browse()
        service = self.env['powerly.api.service'].sudo()
        skip = self.env.context.get('skip_powerly_sync')

        for vals in vals_list:
            # Skip remote create when syncing from Powerly -> Odoo to avoid loops
            if not skip:
                try:
                    payload = self._vals_to_powerly_payload(vals)
                    payload_json = json.dumps(payload)
                    results = service.create_charger(payload_json)
                except Exception as e:
                    raise UserError(f"Failed to create on Powerly: {e}")

                # Map back important fields from API response
                # Example fields returned by Powerly: id, identifier, token, status, image, latitude/longitude, listed, available, owner_id, etc.
                def _get(res, key, fallback=None):
                    return res.get(key) if isinstance(res, dict) else fallback

                vals.update({
                    'external_id': _get(results, 'id') or vals.get('external_id'),
                    'identifier': _get(results, 'identifier') or vals.get('identifier'),
                    'token': _get(results, 'token') or vals.get('token'),
                    'status': _get(results, 'status') or vals.get('status'),
                    'image_url': _get(results, 'image') or vals.get('image_url'),
                    'latitude': float(_get(results, 'latitude', vals.get('latitude'))) if _get(results,
                                                                                               'latitude') is not None else vals.get(
                        'latitude'),
                    'longitude': float(_get(results, 'longitude', vals.get('longitude'))) if _get(results,
                                                                                                  'longitude') is not None else vals.get(
                        'longitude'),
                    'listed': bool(_get(results, 'listed', vals.get('listed'))) if _get(results,
                                                                                        'listed') is not None else vals.get(
                        'listed'),
                    'available': bool(_get(results, 'available', vals.get('available'))) if _get(results,
                                                                                                 'available') is not None else vals.get(
                        'available'),
                    'owner_external_id': _get(results, 'owner_id') or vals.get('owner_external_id'),
                })

            rec = super(PowerlyCharger, self).create(vals)
            records |= rec

        return records

    def _merge_for_payload(self, rec, vals):
        """Build a dict of values reflecting post-write state for payload mapping."""
        # Only include fields that _vals_to_powerly_payload understands
        keys = [
            'identifier', 'category', 'title', 'description',
            'latitude', 'longitude', 'listed', 'type', 'status',
            'image_url', 'session_limit_type', 'session_limit_value',
            'secure', 'configured',
            'address_line_1', 'address_line_2', 'address_line_3',
            'zipcode', 'city', 'state',
            'price_unit', 'price', 'reservation_fee', 'is_external',
        ]
        merged = {}
        for k in keys:
            merged[k] = vals[k] if k in vals else rec[k]
        return merged


    def write(self, vals):
        """Update on Powerly, then persist locally."""
        # Allow skipping remote update during inbound sync to avoid loops
        if self.env.context.get('skip_powerly_sync'):
            return super(PowerlyCharger, self).write(vals)

        service = self.env['powerly.api.service'].sudo()
        for rec in self:
            # If record has never been created on Powerly, either skip or create there
            if not rec.external_id:
                # Optional: attempt remote create instead of raising
                # results = service.create_charge_point(self._vals_to_powerly_payload(self._merge_for_payload(rec, vals)))
                # vals = dict(vals, external_id=results.get('id') or rec.external_id, token=results.get('token') or rec.token)
                raise UserError("This charger has no External ID yet; create it on Powerly first.")

            try:
                to_send = self._vals_to_powerly_payload(self._merge_for_payload(rec, vals))
                to_send = json.dumps(to_send)
                # to_send = {"category":"SMART_METER"}
                # If nothing to send (e.g., only local-only fields changed), skip remote call
                if to_send:
                    results = service.update_charger(rec.external_id, to_send)

                    # Map selected fields back from API response to ensure consistency
                    def _get(res, key, fallback=None):
                        return res.get(key) if isinstance(res, dict) else fallback

                    back_vals = {}
                    if 'status' in results:
                        back_vals['status'] = results['status']
                    if 'identifier' in results:
                        back_vals['identifier'] = results['identifier']
                    if 'token' in results and not rec.token:
                        back_vals['token'] = results['token']
                    if 'image' in results:
                        back_vals['image_url'] = results['image']
                    for num_key, field_name in [
                        ('latitude', 'latitude'),
                        ('longitude', 'longitude'),
                        ('price', 'price'),
                        ('reservation_fee', 'reservation_fee'),
                    ]:
                        if results.get(num_key) is not None:
                            try:
                                back_vals[field_name] = float(results[num_key])
                            except Exception:
                                pass
                    for bool_key, field_name in [
                        ('listed', 'listed'),
                        ('available', 'available'),
                        ('configured', 'configured'),
                        ('secure', 'secure'),
                    ]:
                        if results.get(bool_key) is not None:
                            back_vals[field_name] = bool(results[bool_key])

                    # Merge API-confirmed values into vals so local write persists them
                    if back_vals:
                        # Only update current record’s write; we can’t mutate the shared vals across records safely
                        rec.with_context(skip_powerly_sync=True).write(back_vals)

            except Exception as e:
                raise UserError(f"Failed to update on Powerly for charger {rec.display_name} (ID: {rec.id}): {e}")

        # Finally write local changes
        return super(PowerlyCharger, self).write(vals)

    def unlink(self):
        """Delete chargers on Powerly before removing them locally."""
        # Skip remote deletes if coming from an inbound Powerly webhook/import
        if self.env.context.get('skip_powerly_sync'):
            return super(PowerlyCharger, self).unlink()

        service = self.env['powerly.api.service'].sudo()
        errors = []

        # Iterate per record to isolate failures
        for rec in self:
            if rec.external_id:
                try:
                    service.delete_charger(rec.external_id)
                except Exception as e:
                    # Collect errors but continue to try others
                    errors.append(f"{rec.display_name} (external_id={rec.external_id}): {e}")

        # If any remote deletes failed, stop and surface the message
        if errors:
            raise UserError("Failed to delete on Powerly:\n- " + "\n- ".join(errors))

        # Proceed with local delete
        return super(PowerlyCharger, self).unlink()



    @api.model
    def sync_all(self):
        service = self.env['powerly.api.service'].sudo()
        data = service.get_chargers()
        # docs return pagination; adapt
        # items = data.get('data') if isinstance(data, dict) and 'data' in data else data
        items = data.get('results', []) if isinstance(data, dict) and 'results' in data else []
        for it in items:
            self._create_or_update(it)

    def _create_or_update(self, payload):
        def to_int(v):
            try:
                return int(v) if v is not None and v != '' else None
            except Exception:
                return None

        def to_float(v):
            try:
                return float(v) if v is not None and v != '' else None
            except Exception:
                return None

        def to_bool(v):
            # Handles 1/0, "1"/"0", True/False
            if isinstance(v, bool):
                return v
            if v in (1, '1', 'true', 'True', 'TRUE'):
                return True
            if v in (0, '0', 'false', 'False', 'FALSE'):
                return False
            return bool(v)

        ext_id = to_int(payload.get('id'))
        token = payload.get('token')

        # Find existing record by external_id, fallback to token if needed
        domain = []
        if ext_id is not None:
            domain = ['|', ('external_id', '=', ext_id), ('token', '=', token or '')]
        elif token:
            domain = [('token', '=', token)]
        rec = self.search(domain or [], limit=1)

        addr = payload.get('address') or {}

        # Datetime field coercion (let Odoo handle common formats)
        next_res_dt = payload.get('next_reservation_near_now')
        if next_res_dt:
            try:
                next_res_dt = fields.Datetime.to_datetime(next_res_dt)
            except Exception:
                next_res_dt = None

        vals = {
            # Identity
            'external_id': ext_id,
            'identifier': payload.get('identifier'),
            'token': token,

            # Classification
            'category': payload.get('category'),
            'type': payload.get('type'),
            'status': payload.get('status') or payload.get('state') or 'unknown',

            # Basic info
            'title': payload.get('title') or payload.get('name') or (f"Charger {ext_id}" if ext_id else "Charger"),
            'description': payload.get('description'),

            # Location
            'latitude': to_float(payload.get('latitude')),
            'longitude': to_float(payload.get('longitude')),
            'listed': to_bool(payload.get('listed')),
            'distance': to_float(payload.get('distance')),

            # Limits / configuration
            'session_limit_type': payload.get('session_limit_type'),
            'session_limit_value': to_float(payload.get('session_limit_value')),
            'online': to_bool(payload.get('online_status')),
            'configured': to_bool(payload.get('configured')),
            'secure': to_bool(payload.get('secure')),

            # Ratings / metrics
            'rating': to_float(payload.get('rating')),
            'total_earnings': to_float(payload.get('total_earnings')),
            'total_energy': to_float(payload.get('total_energy')),
            'total_sessions_time': to_int(payload.get('total_sessions_time')),
            'orders_count': to_int(payload.get('orders_count')),
            'price': to_float(payload.get('price')),
            'price_usd': to_float(payload.get('price_usd')),
            'reservation_fee': to_float(payload.get('reservation_fee')),
            'earning': to_float(payload.get('earning')),

            # Availability / state
            'is_external': to_bool(payload.get('is_external')),
            'is_in_use': to_bool(payload.get('is_in_use')),
            'is_reserved': to_bool(payload.get('is_reserved')),
            'available': to_bool(payload.get('available')),
            'next_reservation_near_now': next_res_dt,

            # Contact / schedule
            'contact_number': payload.get('contact_number'),
            'open_time': payload.get('open_time'),
            'close_time': payload.get('close_time'),

            # Address
            'address_line_1': addr.get('address_line_1'),
            'address_line_2': addr.get('address_line_2'),
            'address_line_3': addr.get('address_line_3'),
            'zipcode': addr.get('zipcode') or payload.get('zipcode'),
            'city': addr.get('city') or payload.get('city'),
            'state': addr.get('state') or payload.get('state'),

            # Media and misc
            'image_url': payload.get('image'),
            'external_details': payload.get('external_details'),
            'media': payload.get('media') or [],
            'connectors': payload.get('connectors') or [],
            'amenities': payload.get('amenities') or [],

            # Ownership
            'owner_external_id': to_int(payload.get('owner_id')),

            # Pricing unit
            'price_unit': payload.get('price_unit') or 'unknown',
        }

        if rec:
            rec.with_context(skip_powerly_sync=True).write(vals)
            return rec
        return self.with_context(skip_powerly_sync=True).create(vals)






    def get_all_orders(self):
        for rec in self:
            get_orders = self.env['powerly.orders'].search([('charger_id','=',rec.id)])
            rec.get_orders_count = len(get_orders)

    def action_for_related_feedbacks(self):
        self.ensure_one()
        get_orders = self.env['powerly.orders'].search([('charger_id','=',self.id)])
        return {
            'name': 'Feedbacks',
            'type': 'ir.actions.act_window',
            'res_model': 'powerly.orders',
            'view_mode': 'list,form',
            'domain': [('id', 'in', get_orders.ids)],  # Changed from get_orders to get_orders.ids
            'context': {'default_charge_point_order_id': self.external_id},
        }




    def action_sync_single(self):
        svc = self.env['powerly.api.service'].sudo()
        data = svc.get_charger(self.external_id)
        resp = data.get('results', {}) if isinstance(data, dict) and 'results' in data else {}
        self._create_or_update(resp)
        return True

