# coding=utf-8
from csv import DictWriter
from importer.models import FileImport

__author__ = 'josh'

import unittest


class MyTestCase(unittest.TestCase):
    def setUp(self):
        if not FileImport.objects.all().exists():
            csv_dict = {
                'ID': 'SC99999999',
                'field_provider': 'Santander',
                'field_account_name': 'Import Test Account - Not Valid',
                'field_publish_after': '01/01/2013',
                'field_min_deposit': '£1.0',
                'field_aer': '0.0123',
                'field_gross_rate': '0.0206',
                'field_monthly_gross': '4.17%',
                'field_net_20': '0.013',
                'field_net_40': '0.011',
                'field_bestbuy': 'Variable Rate ISA',
                'field_ratetracker': 'Variable',
                'field_access_internet': '1',
                'field_access_telephone': '1',
                'field_access_post': '1',
                'field_access_branch': '1',
                'field_access_cashcard': '1',
                'field_open_internet': '1',
                'field_open_telephone': '1',
                'field_open_post': '1',
                'field_open_branch': '1',
                'field_open_cashcard': '1',
                'field_facts': 'This is a Test Account to test the CSV import.',
                'field_term': '',
                'field_isatransfers_in': '',
                'field_withdrawals': '',
                'field_min_age': '',
                'field_max_age': '',
                'field_sc_stamp': '',
                'field_bbrating_easyaccess': '',
                'field_bbrating_fixedrate_bonds': '',
                'field_bbrating_variable_isa': '',
                'field_bbrating_fixed_isa': '',
                'field_bbrating_notice': '',
                'field_bbrating_over50': '',
                'field_bbrating_monthly_income': '',
                'field_bbrating_regularsavings': '',
                'field_bbrating_childrenssavings': '',
                'field_bbrating_variable_bond': '',
                'field_fscs_licence': '',
                'field_status': '',
                'field_bonus_amount': '',
                'field_bonus_term': '',
                'field_underlying_gross_rate': '',
                'field_max_deposit': '',
                'field_notice': '',
                'field_web_address': '',
                'field_min_monthly': '',
                'field_max_monthly': '',
                'Date_Modified': '',
                'FixedRateProduct': '',
                'ProductId': '',
                'field_account_type': '',
                'field_bonus_fixed_date': '',
                'field_verdict': '',
                'field_verdict_date': '',
                'field_is_paid': '',
            }
            DictWriter(f=[csv_dict],
                       fieldnames=['ID', 'field_provider', 'field_account_name', 'field_publish_after',
                                   'field_min_deposit', 'field_aer', 'field_gross_rate', 'field_monthly_gross',
                                   'field_net_20', 'field_net_40', 'field_bestbuy', 'field_ratetracker',
                                   'field_access_internet', 'field_access_telephone', 'field_access_post',
                                   'field_access_branch', 'field_access_cashcard', 'field_open_internet',
                                   'field_open_telephone', 'field_open_post', 'field_open_branch',
                                   'field_open_cashcard', 'field_facts', 'field_term', 'field_isatransfers_in',
                                   'field_withdrawals', 'field_min_age', 'field_max_age', 'field_sc_stamp',
                                   'field_bbrating_easyaccess', 'field_bbrating_fixedrate_bonds',
                                   'field_bbrating_variable_isa', 'field_bbrating_fixed_isa',
                                   'field_bbrating_notice', 'field_bbrating_over50',
                                   'field_bbrating_monthly_income', 'field_bbrating_regularsavings',
                                   'field_bbrating_childrenssavings', 'field_bbrating_variable_bond',
                                   'field_fscs_licence', 'field_status', 'field_bonus_amount', 'field_bonus_term',
                                   'field_underlying_gross_rate', 'field_max_deposit', 'field_notice',
                                   'field_web_address', 'field_min_monthly', 'field_max_monthly', 'Date_Modified',
                                   'FixedRateProduct', 'ProductId', 'field_account_type',
                                   'field_bonus_fixed_date', 'field_verdict', 'field_verdict_date',
                                   'field_is_paid'
                       ])

    def test_something(self):
        self.assertEqual(True, False)
