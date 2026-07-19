{
    'name': 'Estate',
    'author': 'Mohamed Wallid',
    'category': 'Real Estate',
    'version': '19.0.1.0.1',
    'summary': 'Manage real estate advertisements',
    'depends': ['base','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
    ],
    'installable': True,
    'application': True,
}


