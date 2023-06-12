{
    "name": "Dashboard",
    "version": "1.0",
    "author" : 'Helmi Dhaoui',
    'website' : 'http://globalservicescompany.net',
    "depends": [
        'base'
    ],
    "category": "Management",
    "data": [
        "data/dashboard_data.xml",
        "security/dashboard_security.xml",
        "security/ir.model.access.csv",
        "views/dashboard_view.xml",
        "views/res_config_view.xml",
        "views/assets.xml",
    ],
    'installable': True,
    'images': ['static/description/logo.png'],
    'currency': 'EUR',
    'live_test_url': 'https://www.youtube.com/embed/v1wx9yJFpHA',
    'price': 30,
    'licence':'OPL-1',
}
