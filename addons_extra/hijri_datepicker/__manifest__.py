{
    "name": "Umm Al Qura(Hijri) Datepicker",
    'version': '11.1.0',
    'author': 'GYB IT SOLUTIONS',
    'summary': 'Web',
    "description":
        """
        OpenERP Web Displays Umm Al Qura(Hijri) Datepicker.
        =======================================================
        
        """,
    'website': 'www.gybitsolutions.com',
    "depends": ['web','web_rtl'],
    'category': 'web',
    'sequence': 5,
    'data': [
         "views/res_users_view.xml",
         "views/hijri_datepicker_templates.xml"
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    'images': ['images/1.jpg'],
    'installable': True,
    'auto_install': False,
}
