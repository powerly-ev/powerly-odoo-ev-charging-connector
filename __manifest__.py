{'application': True,
 'author': 'Powerly',
 'auto_install': False,
 'category': 'Industries',
 'data': ['security/powerly_security.xml',
          'security/ir.model.access.csv',
          'data/cron_data.xml',
          'views/res_company.xml',
          'views/powerly_charger_views.xml',
          'views/powerly_orders.xml',
          'views/res_config_settings_ext.xml',
          'views/powerly_orders_feedback_views.xml'],
 'depends': ['base', 'web', 'sale_management', 'sale', 'account'],
 'description': '\n'
                '            Powerly EV Charging Connector links Odoo with Powerly, an EV charging management platform '
                'used for operating public and private EV chargers. Powerly supports OCPP-compliant hardware, charging '
                'session monitoring, energy usage tracking, pricing, and user feedback.\n'
                'The connector imports EV chargers, charging sessions, OCPP-related data fields, user information, and '
                'feedback into Odoo. It supports the creation of invoices for completed sessions and maintains charger '
                'metadata across both systems.\n'
                'Key features\n'
                '    • Sync EV chargers and configuration details\n'
                '    • Sync charging sessions with timestamps, pricing, and OCPP-related fields\n'
                '    • Sync user feedback linked to chargers and sessions\n'
                '    • Create invoices for completed charging sessions in Odoo\n'
                '    • Token based authentication with automatic refresh\n'
                '    • Company level configuration for API URL, credentials, and tokens\n'
                '    • Compatible with mobile apps created through the Powerly App Builder\n'
                'Suitable for\n'
                '    • Charge Point Operators using OCPP chargers\n'
                '    • E mobility service providers\n'
                '    • Fleet and logistics companies\n'
                '    • Parking facilities and property managers\n'
                '    • Energy service providers adding EV charging services\n'
                '    • Businesses using the Powerly App Builder to deploy branded EV charging apps\n'
                'This module helps organizations unify their EV charging operations, OCPP-based charger data, and '
                'accounting workflows inside Odoo.\n'
                '    ',
 'images': ['static/description/icon.png',
            'static/description/screenshot_config.png',
            'static/description/screenshot_list_chargers.png',
            'static/description/screenshot_list_orders.png'],
 'installable': True,
 'license': 'LGPL-3',
 'name': 'Powerly EV Charging Connector',
 'summary': 'Connect Odoo with Powerly to synchronize EV chargers, OCPP-based charging data, sessions, invoices, and '
            'user feedback.',
 'version': '18.0.1.0.0',
 'website': 'https://www.powerly.app'}