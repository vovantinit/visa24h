{
    'name' : 'SkyERP Export Excel',
    'version': '1.0',
    'summary': 'SkyERP Export Excel',
    'category': 'ERP',
    'description':
        """
        SkyERP Export Excel
        SO excel report
        """,
    'data': [
        'sky_so_report_wizard_view.xml',
        'so_cai_tk_view.xml',
        'report/report_cashbook_s07_dn.xml',
    ],
    'depends' : ['sky_company_currency', 'to_vn_legal_financial_reports'],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
