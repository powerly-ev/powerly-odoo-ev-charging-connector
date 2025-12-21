# Powerly EV Charging Connector for Odoo

## Overview
The Powerly EV Charging Connector integrates Odoo with the Powerly EV charging platform.
It allows businesses to connect Odoo to a Powerly account, view EV chargers, and work with selected charging-related records inside Odoo.

## Prerequisites
- An active Powerly account
- A valid Powerly API key
- Odoo access rights for the "Powerly Connector Manager" group

## Installation
1. Install the module from the Odoo Apps Store (or from your addons path during development).
2. Ensure Odoo installs all declared dependencies.

## Configuration
1. Open **Settings** in Odoo.
2. Navigate to the **Powerly** section.
3. Enter your Powerly API key and connection settings (Base URL if applicable).
4. Save.

## Usage
After configuration, Powerly-related menus should be available in Odoo.

Typical workflow:
- Open the Powerly menus in Odoo.
- Review chargers and orders available for the connected Powerly account.
- If scheduled synchronization is enabled, data will refresh automatically based on configured cron jobs.

## Permissions
This module restricts access to Powerly-related models using the **Powerly Connector Manager** group.
Add trusted users to this group to allow them to view and manage connector data.

## Branded mobile app using Powerly App Builder (optional)
You can create a custom branded EV charging mobile app using Powerly App Builder and connect it to your Powerly account.

Important notes:
- The App Builder is provided by Powerly as an external service.
- App generation may be subject to separate terms or pricing.
- The generated mobile app UI is not part of Odoo and should not be considered an Odoo screen.

## Data scope and limitations
- The connector displays data provided by the Powerly API.
- Data availability depends on the Powerly account configuration and enabled features.
- This module does not manage charger firmware or real-time charging control unless explicitly supported by Powerly and enabled in your deployment.

## Troubleshooting
- Confirm the API key is valid and active.
- Verify outbound connectivity from the Odoo server to the Powerly API endpoints.
- Check Odoo server logs for connection or API errors.

## Additional documentation
Powerly documentation (including EV charger setup and platform features):
- https://www.powerly.app/docs/

## Support
Use your standard Powerly support channel for help with the connector and Powerly services.
