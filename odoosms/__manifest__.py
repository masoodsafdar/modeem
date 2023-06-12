# -*- coding: utf-8 -*-
{
    'name': "SMS Client V11",

    'summary': """
        This module is about SMS CLient""",

    'description': """
        This module allowed to manage SMS through gateway
    """,

    'author': "Masa Technology",
    "description": """
SMS Client module provides:
-------------
Sending SMSs very easily, individually or collectively.

    """,
    "website": "http://masa.technology",
    "category": "custom",
    'images': ['images/sms.jpeg', 'images/gateway.jpeg', 'images/gateway_access.jpeg','images/client.jpeg','images/send_sms.jpeg'],
    'version': '3.0',
    'depends': ['mail'],
    'data': [
        "views/smsclient_view.xml", 
        "views/smsclient_data.xml",
        "wizard/mass_sms_view.xml",
        "views/partner_sms_send_view.xml",
        "views/smstemplate_view.xml"
    ],    
    'demo': [
        #'demo.xml',
    ],
    'installable':True,
    'auto_install':True,
    'application':True,
}
