{
    'name' : 'SkyERP PO# for Payment Supplier',
    'version': '1.0',
    'summary': 'SkyERP PO# for Payment Supplier',
    'category': 'ERP',
    'description':
        """
        Add PO# to payment line
        Add button uncheck credit, debit in form view 
        """,
    'data': [
        'sky_view.xml',
    ],
    'depends' : ['sky_company_currency'],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
