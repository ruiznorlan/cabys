{
    'name': "Catálogo de bienes y servicios para uso tributario y Cuentas Nacionales",

    'summary': "Catálogo de bienes y servicios para uso tributario y Cuentas Nacionales",
    'author': 'info@fakturacion.com',
    'website': "https://github.com/odoocr/cabys",
    'category': 'Account',
    'version': '12.0.0.0.1',
    'license': 'OPL-1',
    'depends': [
        'base', 'product',
    ],
    'data': [
        'views/cabys_producto_views.xml',
        'views/cabys_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/product_category_views.xml',
        'views/assets.xml',
        'views/res_company_views.xml',

        'security/ir.model.access.csv',

    ],
    'qweb': [
        "static/src/xml/cabys_templates.xml",
    ],
    'installable': True,
}
