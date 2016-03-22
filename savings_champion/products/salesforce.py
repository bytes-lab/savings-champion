from collections import Iterable
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import simple_salesforce
import pytz
import datetime
from api.v1.models import ApiExcludedItem
from common.models import Profile
from products.models import Provider, MasterProduct, ProductTier, BestBuy, FSCSLimitType, InterestPaidFrequency, \
    Product, \
    ProductPortfolio, RatetrackerReminder
from time import sleep
from django.db.models.fields import NOT_PROVIDED, FieldDoesNotExist
from stats.client import StatsDClient
from common.tasks import send_email

User = get_user_model()

BASE_API_LIMIT_TIME = 0


def get_chunks(input_list, n):
    # Splits a list into a set of lists of length n
    return [input_list[x:x + n] for x in range(0, len(input_list), n)]


def get_chunks_generator(input_list, n):
    i = 0
    while True:
        try:
            yield input_list[i:i + n]
        except IndexError:
            output = input_list[i:]
            if output == []:
                raise StopIteration
        i = i + n + 1


SALESFORCE_TO_DJANGO_MAPPING = {

    'provider': {
        'Id': 'sf_provider_id',
        'IsDeleted': 'deleted',
        'Name': 'title',
        'Phone': 'phone',
        'Website': 'website',
        'CreatedDate': 'created_date',
        'LastModifiedDate': 'last_updated',
        'Financial_Services_Compensation_Scheme__c': 'Financial_Services_Compensation_Scheme__c',
        'Other_Reason_Compliance_Checked__c': 'compliance_checked',
        'Other_Reason_To_Exclude_This_Provider__c': 'reason_to_exclude',
        'Provider_Does_Not_Meet_Service_Standards__c': 'meets_service_standard',
        'FSCS_Licence_Owner_c__c': 'fscs_licence_holder',
        'Parent_Licence_Owner__c': 'fscs_parent',
        'Ethical__c': 'ethical',
        'Ethical_Rating__c': 'ethical_rating',
        'Moody_s_Rating__c': 'moodys_rating',
        'Fitch_s_Rating__c': 'fitchs_rating',
        'Building_Society__c': 'building_society',
        'Mutual__c': 'mutual',
        'Bank__c': 'bank',
        'High_Street__c': 'high_street',
        'Provider_Maximum__c': 'provider_maximum',
    },
    'product': {
        'Id': 'sf_product_id',
        'Name': 'title',
        'Access_Branch__c': 'is_branch_access',
        'Access_Cash_Card__c': 'is_cc_access',
        'Access_Internet__c': 'is_internet_access',
        'Access_Post__c': 'is_post_access',
        'Access_Telephone__c': 'is_phone_access',
        'Bonus_Term_Months__c': 'bonus_term',
        'Bonus_Term_Fixed_Date__c': 'bonus_end_date',
        'ISA_Transfers_In__c': 'is_isa_transfers_in',
        'Is_Fixed_Rate__c': 'is_fixed',
        'Open_Branch__c': 'is_open_branch',
        'Open_Cash_Card__c': 'is_open_cc',
        'Open_Internet__c': 'is_open_internet',
        'Open_Post__c': 'is_open_post',
        'Open_Telephone__c': 'is_open_telephone',
        'Status__c': 'status',
        'Product_Facts__c': 'facts',
        'Product_Available_From__c': 'available_from',
        'Product_Available_To__c': 'available_to',
        'Term_Fixed_Date__c': 'term_fixed_date',
        'Term_Months__c': 'term',
        'Notice_Period__c': 'notice',
        'Sharia_a__c': 'shariaa',
        'Type__c': 'account_type',
        'Category__c': 'Category__c',
        'Existing_Customers_Only__c': 'existing_only',
        'Local_Customers_Only__c': 'locals_only',
        'Operating_Balance__c': 'operating_balance',
        'Operating_Balance_Rate__c': 'operating_balance_rate',
        'Other_Reason_To_Exclude_This_Product__c': 'other_reason_to_exclude_this_product',
        'Other_Reason_Compliance_Checked__c': 'other_reason_compliance_checked',
        'Trust_Funds_Accepted__c': 'trust_funds_accepted',
        'Trust_Types_Excluded__c': 'Trust_Types_Excluded__c',
        'Interest_Paid_Frequency__c': 'Interest_Paid_Frequency__c',
        'Maximum_Age__c': 'maximum_age',
        'Minimum_Age__c': 'minimum_age',
        'Minimum_Monthly__c': 'minimum_monthly',
        'Maximum_Monthly__c': 'maximum_monthly',
        'Open_Limit_Total__c': 'open_limit_total',
        'Open_Limit_Own_Name__c': 'open_limit_own_name',
        'Open_Limit_Joint_Name__c': 'open_limit_joint_name',
        'Exclude_from_API_for__c': 'exclude_from_api',
        'Verdict__c': 'verdict',
        'Website__c': 'url',
        'Is_Paid__c': 'is_paid',
        'Reason_for_removal_from_Rate_Tracker__c': 'removal_reason',
        'Bonus_End_Product_Switch__c': 'revert_on_bonus_end',
        'revert_on_maturity': 'revert_on_maturity'
    },
    'old_product_tier': {
        'ProductTier__title': 'title',
        'SCCode__c': 'sc_code',
        'With_Effect_From__c': 'publish_after',
        'Type__c': 'account_type',
        'Provider__c': 'provider',
        'Minimum_Deposit__c': 'minimum',
        'Maximum_Deposit__c': 'maximum',
        'Minimum_Monthly__c': 'minimum_monthly',
        # 'ProductTier__maximum_monthly':'maximum_monthly',
        'AER__c': 'aer',
        'Gross_Rate__c': 'gross_rate',
        'Monthly_Gross_Rate__c': 'monthly_gross',
        'Net_20__c': 'net_20',
        'Net_40__c': 'net_40',
        'ProductTier__bestbuy_type': 'bestbuy_type',
        # 'ProductTier_':'ratetracker_type',
        'ProductTier__is_internet_access': 'is_internet_access',
        'ProductTier__is_phone_access': 'is_phone_access',
        'ProductTier__is_post_access': 'is_post_access',
        'ProductTier__is_branch_access': 'is_branch_access',
        'ProductTier__is_cc_access': 'is_cc_access',
        'ProductTier__is_open_internet': 'is_open_internet',
        'ProductTier__is_open_telephone': 'is_open_telephone',
        'ProductTier__is_open_post': 'is_open_post',
        'ProductTier__is_open_branch': 'is_open_branch',
        'ProductTier__is_open_cc': 'is_open_cc',
        'ProductTier__is_isa_transfers_in': 'is_isa_transfers_in',
        # 'ProductTier__withdrawls':'withdrawls',
        'ProductTier__term': 'term',
        # 'ProductTier_':'fscs_licence',
        # 'ProductTier__Is_Paid__c':'is_paid',
        'ProductTier__minimum_age': 'minimum_age',
        'ProductTier__maximum_age': 'maximum_age',
        'Bonus__c': 'bonus_amount',
        'Underlying_Gross__c': 'underlying_gross_rate',
        'ProductTier__notice': 'notice',
        'Website__c': 'url',
        'Id': 'sf_product_id',
        'ProductTier__is_fixed': 'is_fixed',
        'Savings_Product__c': 'master_product',

    },
    'product_tier': {
        'Id': 'sf_product_tier_id',
        'SCCode__c': 'sc_code',
        'With_Effect_From__c': 'publish_after',
        'AER__c': 'aer',
        'Bonus__c': 'bonus_amount',
        'Gross_Rate__c': 'gross_rate',
        # 'Is_Current_Tier__c': '',
        'Maximum_Deposit__c': 'maximum',
        'Minimum_Deposit__c': 'minimum',
        'Monthly_Gross_Rate__c': 'monthly_gross',
        'Net_20__c': 'net_20',
        'Net_40__c': 'net_40',
        'Underlying_Gross__c': 'underlying_gross_rate',
        'With_Effect_To__c': 'available_until',
        'Name': 'title',
        'Joint_Account_Only__c': 'joint_account_only',
        'Type__c': 'tier_type',
        'Split_Interest_Tier__c': 'split_interest',
    },
    'salesforce_user': {
        'User_Id__c': 'user_id',
        'Date_Of_Birth__c': 'dob',
        'Telephone__c': 'telephone',
        'Salutation__c': 'salutation',
        'Post_Code__c': 'postcode',
        # '':'newsletter',
        'Date_Joined__c': 'created_date',
        # '':'last_updated',
        # '':'is_synched',
        # '':'ip_address',
        'Source__c': 'source',
        # '':'skeleton_user',
        # '':'filled_in_name',

        'User__User_Id__c': 'pk',
        'User__Username__c': 'username',
        'User__Email__c': 'email',
        'User__First_Name__c': 'first_name',
        'User__Last_Name__c': 'last_name',
        # '':'is_staff',
        # '':'is_active',
        'User__Date_Joined__c': 'date_joined',

    },
    'salesforce_user_product': {

        'Balance__c': 'balance',
        'Deleted__c': 'is_deleted',
        'Opening_Date__c': 'opening_date',
        'Maturity_Date__c': 'maturity_date',
        'Gross_Rate__c': 'rate',
        'Bonus_Term_Months__c': 'bonus_term',
        'Product__notice': 'notice',
        'Product__bestbuy_type': 'account_type',
    }
}


class SCSalesforce(simple_salesforce.Salesforce):
    def __init__(self, *args, **kwargs):
        super(SCSalesforce, self).__init__(*args, **kwargs)

    def query_all(self, query, **kwargs):
        """Returns the full set of results for the `query`. This is a
        convenience wrapper around `query(...)` and `query_more(...)`.

        The returned dict is the decoded JSON payload from the final call to
        Salesforce, but with the `totalSize` field representing the full
        number of results retrieved and the `records` list representing the
        full list of records retrieved.

        Arguments

        * query -- the SOQL query to send to Salesforce, e.g.
                   `SELECT Id FROM Lead WHERE Email = "waldo@somewhere.com"`
        """

        def get_all_results(previous_result, **kwargs):
            """Inner function for recursing until there are no more results.

            Returns the full set of results that will be the return value for
            `query_all(...)`

            Arguments:

            * previous_result -- the modified result of previous calls to
                                 Salesforce for this query
            """
            if previous_result['done']:
                return previous_result
            else:
                statsd_client = StatsDClient().get_counter_client(
                    client_name='salesforce.SCSalesforce_get_all_results.attempted'
                )
                statsd_client += 1
                result = self.query_more(previous_result['nextRecordsUrl'],
                                         identifier_is_url=True, **kwargs)
                result['totalSize'] += previous_result['totalSize']
                # Include the new list of records with the previous list
                previous_result['records'].extend(result['records'])
                result['records'] = previous_result['records']
                # Continue the recursion
                return get_all_results(result, **kwargs)

        # Make the initial query to Salesforce
        statsd_client = StatsDClient().get_counter_client(
            client_name='salesforce.SCSalesforce_get_all_results.attempted'
        )
        statsd_client += 1
        result = self.query(query, **kwargs)
        # The number of results might have exceeded the Salesforce batch limit
        # so check whether there are more results and retrieve them if so.
        return get_all_results(result, **kwargs)


class SalesforceAPI(object):
    SALESFORCE_USER = getattr(settings, 'SALESFORCE_USER',
                              'savingschampion.co.uk.sfdc@silverlinedsolutions.com.djangoapi')
    SALESFORCE_PASS = getattr(settings, 'SALESFORCE_PASS', 'DjANGO123456')
    SALESFORCE_TOKEN = getattr(settings, 'SALESFORCE_TOKEN', 'MNEeYIkCiryhiy1z2rTshDKR8')

    def __init__(self):
        self.salesforce = SCSalesforce(instance='eu1.salesforce.com',
                                       username=self.SALESFORCE_USER,
                                       password=self.SALESFORCE_PASS,
                                       security_token=self.SALESFORCE_TOKEN)
        self.object_description = {}

        self.log = []

    def get_log(self):
        return self.log

    def reset_log(self):
        self.log = []


class SalesforceProvider(SalesforceAPI):
    def get_by_id(self, provider_ids):
        if 'Account' not in self.object_description:
            sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.SalesforceProvider_get_by_id.attempted'
            )
            statsd_client += 1
            self.object_description['Account'] = self.salesforce.Account.describe()
        provider_fields = ", ".join([x['name'] for x in self.object_description['Account']['fields']])

        # todo: start using developername
        provider_query = "SELECT %s from Account where Id in ('%s') and RecordTypeID in (select id from RecordType where name = 'Provider')" % (
            provider_fields, "', '".join(provider_ids))
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits

        providers = self.salesforce.query_all(
            provider_query
        )

        return providers['totalSize'], providers['records']

    def update_multiple_providers_by_id(self, updated_providers_list):
        for chunk in get_chunks(updated_providers_list, 10):
            result = self.get_by_id(chunk)
            if result[0] > 0:
                for provider in result[1]:
                    self.update(provider)

    def _save_salesforce_data(self, salesforce_data, django_object, mapping):
        for key, value in salesforce_data.iteritems():
            if key in SALESFORCE_TO_DJANGO_MAPPING[mapping]:
                key = SALESFORCE_TO_DJANGO_MAPPING[mapping][key]
                if key == 'account_type':
                    value = value[:1]
                if key == 'Financial_Services_Compensation_Scheme__c':
                    fscs_limit_type, fscs_limit_type_created = FSCSLimitType.objects.get_or_create(name__iexact=value)
                    key = 'fscs_limit_type'
                    value = fscs_limit_type

                if key in ['Exclude_from_API_for__c', 'exclude_from_api'] and value is not None:
                    value = value.split(';')
                    exclusions = []
                    for item in value:
                        api_excluded_object, _ = ApiExcludedItem.objects.get_or_create(name=value,
                                                                                       email='api@{value}.com'.format(
                                                                                           value=item.lower()))
                    value = exclusions

                if value is None and not Provider._meta.get_field_by_name(key)[0].null:
                    if Provider._meta.get_field_by_name(key)[0].default is not NOT_PROVIDED:
                        value = Provider._meta.get_field_by_name(key)[0].default

                self.log.append(u" - Saving %s:%s to %s" % (key, value, django_object))
                setattr(django_object, key, value)
        return django_object

    def create(self, provider):
        provider_object = Provider()
        provider_object = self._save_salesforce_data(provider, provider_object, 'provider')
        provider_object.save()
        return provider_object

    def update(self, provider):
        try:
            provider_object = Provider.objects.get(sf_provider_id=provider['Id'])
        except Provider.DoesNotExist:
            try:
                provider_object = Provider.objects.get(title=provider['Name'])
            except Provider.DoesNotExist:
                # Not using get or create because this may not be all the required data.
                return self.create(provider)

        self.log.append(u"Provider: %s" % provider_object)
        provider_object = self._save_salesforce_data(provider, provider_object, 'provider')
        provider_object.save()
        return provider_object

    def update_recent(self, days=10):
        # First check for providers that need to be updated
        end = datetime.datetime.now(pytz.UTC)  # we need to use UTC as salesforce API requires this
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        updated_accounts = self.salesforce.Account.updated(end - datetime.timedelta(days=int(days)), end)
        for chunk in get_chunks(updated_accounts['ids'], 10):
            result = self.get_by_id(chunk)
            if result[0] > 0:
                for provider in result[1]:
                    self.update(provider)

    def update_all(self):
        # First check for providers that need to be updated
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        providers = self.salesforce.query_all(
            'SELECT Id FROM Account WHERE RecordTypeID IN '
            "(SELECT id FROM RecordType WHERE name = 'Provider')"
        )

        provider_list = []
        for provider in providers['records']:
            provider_list.append(provider['Id'])

        for chunk in get_chunks(provider_list, 10):
            result = self.get_by_id(chunk)
            if result[0] > 0:
                for provider in result[1]:
                    self.update(provider)


class SalesforceProduct(SalesforceAPI):
    def __init__(self):
        super(SalesforceProduct, self).__init__()
        self.provider = SalesforceProvider()

    def get_by_id(self, product_ids):
        if 'Product' not in self.object_description:
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.SalesforceProducts_get_by_id.attempted'
            )
            statsd_client += 1
            self.object_description['Product'] = self.salesforce.Savings_Product__c.describe()
        product_fields = ", ".join([x['name'] for x in self.object_description['Product']['fields']])
        product_query = "SELECT %s from Savings_Product__c where Id in ('%s')" % (
            product_fields, "', '".join(product_ids))
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        products = self.salesforce.query_all(
            product_query
        )
        return products['totalSize'], products['records']

    def _save_salesforce_data(self, salesforce_data, django_object, mapping):
        # Required due to calling products which the base class doesn't have.
        for key, value in salesforce_data.iteritems():
            if key in SALESFORCE_TO_DJANGO_MAPPING[mapping]:
                key = SALESFORCE_TO_DJANGO_MAPPING[mapping][key]
                # This needs to be done ASAP and so is inside the loop, but is terminated with the None check
                # to stop excess work
                if django_object.provider_id is None and 'ProviderId__c' in salesforce_data:
                    try:
                        provider = Provider.objects.get(sf_provider_id=salesforce_data['Provider__c'])
                    except Provider.DoesNotExist:
                        provider_data = self.provider.get_by_id([salesforce_data['Provider__c']])
                        provider = self.provider.update(provider_data[1][0])
                    django_object.provider = provider

                if key == 'is_fixed':
                    value = True if value == u'Yes' else False

                if key == 'account_type' and value is not None:
                    value = value[:1]
                if key == 'Financial_Services_Compensation_Scheme__c':
                    if FSCSLimitType.objects.filter(name__icontains=value).exists():
                        fscs_limit_type = FSCSLimitType.objects.get(name=value)
                        setattr(django_object, 'fscs_limit_type', fscs_limit_type)
                        continue
                if key == 'Category__c':
                    best_buy, created = BestBuy.objects.get_or_create(title__icontains=value, client_type=salesforce_data['Type__c'][:1].lower())
                    if created:
                        send_email.delay(u'New Bestbuy Created Automatically',
                                         u'A new bestbuy has been created on the website automatically, It is the {type} {name}'.format(type=salesforce_data['Type__c'].lower(), name=value),
                                         u'savings.champion@savingschampion.co.uk',
                                         [u'data.team@savingschampion.co.uk', u'admin@savingschampion.co.uk'])
                    self.log.append(u" -- Saving %s:%s to %s" % (key, value, django_object))
                    django_object.save()
                    django_object.bestbuy_type = [best_buy]
                    continue

                if key == 'Trust_Types_Excluded__c':
                    continue

                if key in ['Term_Months__c', 'Notice_Period__c', 'term', 'notice', 'operating_balance']:
                    value = int(value) if value is not None else MasterProduct._meta.get_field_by_name(key)[
                        0].default

                if key in ['open_limit_total', 'open_limit_own', 'open_limit_joint']:
                    value = -1 if value is None else int(value)

                if key == 'Interest_Paid_Frequency__c':
                    try:
                        ipf, _ = InterestPaidFrequency.objects.get_or_create(title=value)
                    except IntegrityError:
                        ipf, _ = InterestPaidFrequency.objects.get_or_create(title='')
                    django_object.interest_paid_frequency.add(ipf)

                if key in ['Exclude_from_API_for__c', 'exclude_from_api'] and value is not None:
                    value = value.split(';')
                    exclusions = []
                    for item in value:
                        api_excluded_object, _ = ApiExcludedItem.objects.get_or_create(name=value,
                                                                                       email='api@{value}.com'.format(
                                                                                           value=item.lower()))
                    value = exclusions

                try:
                    if value is None and not MasterProduct._meta.get_field_by_name(key)[0].null:
                        if MasterProduct._meta.get_field_by_name(key)[0].default is not NOT_PROVIDED:
                            value = MasterProduct._meta.get_field_by_name(key)[0].default
                except FieldDoesNotExist:
                    #  If I can't translate the label into a field, then I can't get that default from the field. so skip for now
                    pass

                self.log.append(u" -- Saving %s:%s to %s" % (key, value, django_object))
                setattr(django_object, key, value)
        return django_object

    def create(self, product, provider):
        product_object = MasterProduct(provider=provider)
        product_object = self._save_salesforce_data(product, product_object, 'product')
        product_object.save()
        return product_object

    def update(self, product):
        product_sf_id = product['Id']
        try:
            product_object = MasterProduct.objects.get(sf_product_id=product_sf_id)
        except MasterProduct.DoesNotExist:
            product_sf_id = product_sf_id[:15]
            try:
                product_object = MasterProduct.objects.get(sf_product_id=product_sf_id)
            except MasterProduct.DoesNotExist:
                try:
                    provider = Provider.objects.get(sf_provider_id=product['Provider__c'])
                except Provider.DoesNotExist:
                    count, provider_data = self.provider.get_by_id([product['Provider__c']])
                    provider = self.provider.update(provider_data[0])
                product_object = self.create(product, provider)

        self.log.append(u"Product: %s" % product_object)
        product_object = self._save_salesforce_data(product, product_object, 'product')

        product_object.save()
        return product_object

    def update_multiple_products_by_id(self, updated_products_list):
        for chunk in get_chunks(updated_products_list, 10):
            result = self.get_by_id(chunk)
            if result[0] > 0:
                for product in result[1]:
                    self.update(product)

    def update_recent(self, days=10):
        # First check for providers that need to be updated
        end = datetime.datetime.now(pytz.UTC)  # we need to use UTC as salesforce API requires this
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        updated_products = self.salesforce.Savings_Product__c.updated(end - datetime.timedelta(days=int(days)), end)
        self.update_multiple_products_by_id(updated_products['ids'])

    def update_all(self):
        product_tier_query = "SELECT Id FROM Savings_Product__c"
        sleep(BASE_API_LIMIT_TIME * 10)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.query_all(
            product_tier_query
        )

        updated_products_list = []
        for product_tier in updated_product_tiers['records']:
            updated_products_list.append(product_tier['Id'])

        self.update_multiple_products_by_id(updated_products_list)


class SalesforceProductTier(SalesforceAPI):
    def __init__(self):
        super(SalesforceProductTier, self).__init__()
        self.provider = SalesforceProvider()
        self.product = SalesforceProduct()

    def get_by_id(self, product_tier_ids):
        if 'ProductTier' not in self.object_description:
            sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.SalesforceProductTier_get_by_id.attempted'
            )
            statsd_client += 1
            self.object_description['ProductTier'] = self.salesforce.Savings_Product_Tier__c.describe()

        product_fields = ", ".join([x['name'] for x in self.object_description['ProductTier']['fields']])
        product_tier_query = "SELECT %s from Savings_Product_Tier__c where Id in ('%s')" % (
            product_fields, "', '".join(product_tier_ids))
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        product_tiers = self.salesforce.query_all(
            product_tier_query
        )
        return product_tiers['totalSize'], product_tiers['records']

    def _save_salesforce_data(self, salesforce_data, django_object, mapping):
        # Required due to calling products which the base class doesn't have.

        for key, value in salesforce_data.iteritems():
            if key in SALESFORCE_TO_DJANGO_MAPPING[mapping]:
                key = SALESFORCE_TO_DJANGO_MAPPING[mapping][key]

                # This needs to be done ASAP and so is inside the loop, but is terminated with the None check
                # to stop excess work
                if django_object.product_id is None and 'Savings_Product__c' in salesforce_data:
                    try:
                        product = MasterProduct.objects.get(sf_product_id=salesforce_data['Savings_Product__c'])
                    except MasterProduct.DoesNotExist:
                        product_data = self.product.get_by_id([salesforce_data['Savings_Product__c']])
                        product = self.product.update(product_data[1][0])
                    django_object.product = product

                # This needs to be done ASAP and so is inside the loop, but is terminated with the None check
                # to stop excess work
                if django_object.provider_id is None and 'ProviderId__c' in salesforce_data:
                    try:
                        provider = Provider.objects.get(sf_provider_id=salesforce_data['ProviderId__c'])
                    except Provider.DoesNotExist:
                        provider_data = self.provider.get_by_id([salesforce_data['ProviderId__c']])
                        provider = self.provider.update(provider_data[1][0])
                    django_object.provider = provider

                if key == 'account_type':
                    value = value[:1]

                if key == 'Financial_Services_Compensation_Scheme__c':
                    if FSCSLimitType.objects.filter(name__icontains=value).exists():
                        fscs_limit_type = FSCSLimitType.objects.get(name=value)
                        setattr(django_object, 'fscs_limit_type', fscs_limit_type)
                        continue

                if key in ['Exclude_from_API_for__c', 'exclude_from_api'] and value is not None:
                    value = value.split(';')
                    exclusions = []
                    for item in value:
                        api_excluded_object, _ = ApiExcludedItem.objects.get_or_create(name=value,
                                                                                       email='api@{value}.com'.format(
                                                                                           value=item.lower()))
                    value = exclusions

                try:
                    if value is None and not ProductTier._meta.get_field_by_name(key)[0].null:
                        if ProductTier._meta.get_field_by_name(key)[0].default is not NOT_PROVIDED:
                            value = ProductTier._meta.get_field_by_name(key)[0].default
                except FieldDoesNotExist:
                    # If i can't translate the label into a field, then i can't get that default from the field. so skip for now
                    pass

                self.log.append(u" --- Saving %s:%s to %s" % (key, value, django_object))
                setattr(django_object, key, value)
        return django_object

    def create(self, product_tier):
        product_tier_object = ProductTier()
        product_tier_object = self._save_salesforce_data(product_tier, product_tier_object, 'product_tier')
        product_tier_object.save()
        return product_tier_object

    def update(self, product_tier):
        if 'Id' in product_tier and 'SCCode__c' in product_tier:
            try:
                product_tier_object = ProductTier.objects.get(sf_product_tier_id=product_tier['Id'])
            except ProductTier.DoesNotExist:
                # This may happen during the migration to sf_product_tier_id, fallback to the SC_Code
                try:
                    product_tier_object = ProductTier.objects.get(sc_code=product_tier['SCCode__c'])
                except ProductTier.DoesNotExist:
                    product_tier_object = self.create(product_tier)
        else:
            self.log.append(u"Product Tier ID does not exist in response: \n%s" % product_tier)
            return
        self.log.append(u"Product Tier: %s" % product_tier_object)
        product_tier_object = self._save_salesforce_data(product_tier, product_tier_object, 'product_tier')
        product_tier_object.save()
        return product_tier_object

    def update_recent(self, days=10):
        # First check for providers that need to be updated
        end = datetime.datetime.now(pytz.UTC)  # we need to use UTC as salesforce API requires this
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.Savings_Product_Tier__c.updated(
            end - datetime.timedelta(days=int(days)),
            end)
        self.update_multiple_products_by_id(updated_product_tiers['ids'])

    def update_multiple_products_by_id(self, updated_product_tiers_list):
        for chunk in get_chunks(updated_product_tiers_list, 10):
            result = self.get_by_id(chunk)
            if result[0] > 0:
                for product_tier in result[1]:
                    self.update(product_tier)

    def update_all(self):
        product_tier_query = "SELECT Id FROM Savings_Product_Tier__c"
        sleep(BASE_API_LIMIT_TIME * 10)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.query_all(
            product_tier_query
        )

        updated_product_tiers_list = []
        for product_tier in updated_product_tiers['records']:
            updated_product_tiers_list.append(product_tier['Id'])

        self.update_multiple_products_by_id(updated_product_tiers_list)

        del updated_product_tiers_list
        del updated_product_tiers

    def update_by_product_id(self, product_ids):
        for chunk in get_chunks(product_ids, 10):
            product_tier_query = u"SELECT Id FROM Savings_Product_Tier__c WHERE Savings_Product__c in ('%s')" % (
                "','".join(chunk)
            )
            sleep(BASE_API_LIMIT_TIME * 10)  # Respect Salesforce API Limits
            updated_product_tiers = self.salesforce.query_all(
                product_tier_query
            )

            updated_product_tiers_list = []
            for product_tier in updated_product_tiers['records']:
                updated_product_tiers_list.append(product_tier['Id'])

            self.update_multiple_products_by_id(updated_product_tiers_list)

            del updated_product_tiers_list
            del updated_product_tiers


class SalesforceOldProductTier(SalesforceAPI):
    def __init__(self):
        super(SalesforceOldProductTier, self).__init__()
        self.provider = SalesforceProvider()
        self.product = SalesforceProduct()

    def get_by_id(self, product_tier_ids):
        if 'ProductTier' not in self.object_description:
            sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.SalesforceOldProductTier_get_by_id.attempted'
            )
            statsd_client += 1
            self.object_description['ProductTier'] = self.salesforce.Savings_Product_Tier__c.describe()
        product_fields = ", ".join([x['name'] for x in self.object_description['ProductTier']['fields']])
        product_tier_query = "SELECT %s from Savings_Product_Tier__c where Id in ('%s')" % (
            product_fields, "', '".join(product_tier_ids))
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        product_tiers = self.salesforce.query_all(
            product_tier_query
        )
        return product_tiers['totalSize'], product_tiers['records']

    def _save_salesforce_data(self, salesforce_data, django_object, mapping):
        # Required due to calling products which the base class doesn't have.
        for key, value in salesforce_data.iteritems():
            if key in SALESFORCE_TO_DJANGO_MAPPING[mapping]:
                key = SALESFORCE_TO_DJANGO_MAPPING[mapping][key]
                if key == 'account_type' and value is not None:
                    value = value[:1]
                if key == 'facts' and value is None:
                    value = ''
                if key == 'Financial_Services_Compensation_Scheme__c':
                    if FSCSLimitType.objects.filter(name__icontains=value).exists():
                        fscs_limit_type = FSCSLimitType.objects.get(name=value)
                        setattr(django_object, 'fscs_limit_type', fscs_limit_type)
                        continue

                # This needs to be done ASAP and so is inside the loop, but is terminated with the None check
                # to stop excess work
                if django_object.master_product_id is None and 'Savings_Product__c' in salesforce_data:
                    try:
                        product = MasterProduct.objects.get(sf_product_id=salesforce_data['Savings_Product__c'])
                    except MasterProduct.DoesNotExist:
                        product_data = self.product.get_by_id([salesforce_data['Savings_Product__c']])
                        product = self.product.update(product_data[1][0])
                    django_object.master_product = product

                # This needs to be done ASAP and so is inside the loop, but is terminated with the None check
                # to stop excess work
                if django_object.provider_id is None and 'ProviderId__c' in salesforce_data:
                    try:
                        provider = Provider.objects.get(sf_provider_id=salesforce_data['ProviderId__c'])
                    except Provider.DoesNotExist:
                        provider_data = self.provider.get_by_id([salesforce_data['ProviderId__c']])
                        provider = self.provider.update(provider_data[1][0])
                    django_object.provider = provider

                if key == 'master_product' or key == 'provider':
                    continue

                if key in ['Exclude_from_API_for__c', 'exclude_from_api'] and value is not None:
                    value = value.split(';')
                    exclusions = []
                    for item in value:
                        api_excluded_object, _ = ApiExcludedItem.objects.get_or_create(name=value,
                                                                                       email='api@{value}.com'.format(
                                                                                           value=item.lower()))
                    value = exclusions

                if value is None and not Product._meta.get_field_by_name(key)[0].null:
                    if Product._meta.get_field_by_name(key)[0].default is not NOT_PROVIDED:
                        value = Product._meta.get_field_by_name(key)[0].default

                self.log.append(u" --- Saving %s:%s to %s" % (key, value, django_object))
                setattr(django_object, key, value)

        for key, value in SALESFORCE_TO_DJANGO_MAPPING[mapping].iteritems():
            if key.startswith('ProductTier__'):
                if key == 'ProductTier__bestbuy_type':
                    try:
                        django_object.save()
                    except AttributeError:  # Here because Markdown fields are not initialised until a value is written in the first place
                        django_object.facts = ''
                        django_object.save()
                    best_buys = django_object.master_product.bestbuy_type.all()
                    for best_buy in best_buys:
                        django_object.bestbuy_type.add(best_buy)
                        self.log.append(u" --- Saving %s:%s to %s" % ('best_buy', best_buy, django_object))
                    continue

                key = key[13:]
                value = getattr(django_object.master_product, key)
                self.log.append(u" --- Saving %s:%s to %s" % (key, value, django_object))
                setattr(django_object, key, value)
        return django_object

    def create(self, product_tier):
        product_tier_object = Product()
        product_tier_object = self._save_salesforce_data(product_tier, product_tier_object, 'old_product_tier')
        product_tier_object.save()
        return product_tier_object

    def update(self, product_tier):
        if 'Id' in product_tier and 'SCCode__c' in product_tier:
            try:
                product_tier_object = Product.objects.get(sf_product_id=product_tier['Id'])
            except Product.DoesNotExist:
                # This may happen during the migration to sf_product_tier_id, fallback to the SC_Code
                try:
                    product_tier_object = Product.objects.get(sc_code=product_tier['SCCode__c'])
                except Product.DoesNotExist:
                    product_tier_object = self.create(product_tier)
        else:
            self.log.append(u"Product Tier ID does not exist in response: \n%s" % product_tier)
            return
        self.log.append(u"Old Product Tier: %s" % product_tier_object)
        product_tier_object = self._save_salesforce_data(product_tier, product_tier_object, 'old_product_tier')
        product_tier_object.save()
        return product_tier_object

    def update_recent(self, days=10):
        # First check for providers that need to be updated
        end = datetime.datetime.now(pytz.UTC)  # we need to use UTC as salesforce API requires this
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.Savings_Product_Tier__c.updated(
            end - datetime.timedelta(days=int(days)),
            end)
        self.update_multiple_products_by_id(updated_product_tiers['ids'])

    def update_multiple_products_by_id(self, updated_product_tiers_list):
        for chunk in get_chunks(updated_product_tiers_list, 10):
            result = self.get_by_id(chunk)
            if result[0] > 0:
                for product_tier in result[1]:
                    self.update(product_tier)

    def update_all(self):
        product_tier_query = "SELECT Id FROM Savings_Product_Tier__c"
        sleep(BASE_API_LIMIT_TIME * 10)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.query_all(
            product_tier_query
        )

        updated_product_tiers_list = []
        for product_tier in updated_product_tiers['records']:
            updated_product_tiers_list.append(product_tier['Id'])

        self.update_multiple_products_by_id(updated_product_tiers_list)

        del updated_product_tiers_list
        del updated_product_tiers


class SalesforceUser(SalesforceAPI):
    def __init__(self):
        super(SalesforceUser, self).__init__()

    def get_by_id(self, product_tier_ids):
        if 'DjangoUser' not in self.object_description:
            sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.SalesforceUser_get_by_id.attempted'
            )
            statsd_client += 1
            self.object_description['DjangoUser'] = self.salesforce.dJango_User__c.describe()
        product_fields = ", ".join([x['name'] for x in self.object_description['DjangoUser']['fields']])
        product_tier_query = "SELECT %s from dJango_User__c where Id in ('%s')" % (
            product_fields, "', '".join(product_tier_ids))
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        product_tiers = self.salesforce.query_all(
            product_tier_query
        )
        return product_tiers['totalSize'], product_tiers['records']

    def _save_salesforce_data(self, salesforce_data, django_object, mapping):
        # Required due to calling products which the base class doesn't have.
        import re

        re1 = '(\\d)'  # Any Single Digit 1
        re2 = '(\\d)'  # Any Single Digit 2
        re3 = '(\\/)'  # Any Single Character 1
        re4 = '(\\d)'  # Any Single Digit 3
        re5 = '(\\d)'  # Any Single Digit 4
        re6 = '(\\/)'  # Any Single Character 2
        re7 = '((?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d])'  # Year 1
        re8 = '(\\s+)'  # White Space 1
        re9 = '((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'  # HourMinuteSec 1

        rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6 + re7 + re8 + re9, re.IGNORECASE | re.DOTALL)

        for key, value in salesforce_data.iteritems():
            if key in SALESFORCE_TO_DJANGO_MAPPING[mapping] and value not in ['', None]:
                key = SALESFORCE_TO_DJANGO_MAPPING[mapping][key]

                m = rg.search(value)
                if m:
                    d1 = m.group(1)
                    d2 = m.group(2)
                    c1 = m.group(3)
                    d3 = m.group(4)
                    d4 = m.group(5)
                    c2 = m.group(6)
                    year1 = m.group(7)
                    ws1 = m.group(8)
                    time1 = m.group(9)

                    value = "%s-%s%s-%s%s %s" % (year1, d3, d4, d1, d2, time1)

                self.log.append(u" -- Saving %s:%s to %s" % (key, value, django_object))

                setattr(django_object, key, value)

        for key, value in SALESFORCE_TO_DJANGO_MAPPING[mapping].iteritems():
            if key.startswith('User__'):
                sf_key = key[6:]
                key = value
                value = salesforce_data[sf_key]
                self.log.append(u" -- Saving %s:%s to %s" % (key, value, django_object.user))
                setattr(django_object.user, key, value)

        return django_object

    def create(self, product_tier):
        product_tier_object = Profile()
        product_tier_object.user = User()
        product_tier_object = self._save_salesforce_data(product_tier, product_tier_object, 'salesforce_user')
        product_tier_object.user.save()
        product_tier_object.save()
        return product_tier_object

    def update(self, product_tier):
        if 'User_Id__c' in product_tier:
            try:
                self.log.append(product_tier['User_Id__c'])
                product_tier_object = Profile.objects.get(user_id=product_tier['User_Id__c'])
            except Profile.DoesNotExist:
                product_tier_object = self.create(product_tier)
        else:
            self.log.append(u"Product Tier ID does not exist in response: \n%s" % product_tier)
            return
        self.log.append(u"Product Tier: %s" % product_tier_object)
        product_tier_object = self._save_salesforce_data(product_tier, product_tier_object, 'salesforce_user')
        product_tier_object.save()
        return product_tier_object

    def update_recent(self, days=10):
        # First check for providers that need to be updated
        end = datetime.datetime.now(pytz.UTC)  # we need to use UTC as salesforce API requires this
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.dJango_User__c.updated(end - datetime.timedelta(days=int(days)),
                                                                       end)
        self.update_multiple_products_by_id(updated_product_tiers['ids'])

    def update_multiple_products_by_id(self, updated_product_tiers_list):
        for chunk in get_chunks(updated_product_tiers_list, 10):
            result = self.get_by_id(chunk)
            if result[0] > 0:
                for product_tier in result[1]:
                    self.update(product_tier)

    def update_all(self):
        product_tier_query = "SELECT Id FROM dJango_User__c"
        sleep(BASE_API_LIMIT_TIME * 10)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.query_all(
            product_tier_query
        )

        updated_product_tiers_list = []
        for product_tier in updated_product_tiers['records']:
            updated_product_tiers_list.append(product_tier['Id'])

        self.update_multiple_products_by_id(updated_product_tiers_list)

        del updated_product_tiers_list
        del updated_product_tiers


class SalesforceUserProducts(SalesforceAPI):
    def __init__(self):
        super(SalesforceUserProducts, self).__init__()
        self.user = SalesforceUser()

    def get_by_id(self, product_tier_ids):
        if 'DjangoUserProducts' not in self.object_description:
            sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.SalesforceUserProducts_get_by_id.attempted'
            )
            statsd_client += 1
            self.object_description['DjangoUserProducts'] = self.salesforce.Savings_Account__c.describe()
        product_fields = ", ".join([x['name'] for x in self.object_description['DjangoUserProducts']['fields']])
        product_tier_query = "SELECT %s from Savings_Account__c where Id in ('%s')" % (
            product_fields, "', '".join(product_tier_ids))
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        product_tiers = self.salesforce.query_all(
            product_tier_query
        )
        return product_tiers['totalSize'], product_tiers['records']

    def _save_salesforce_data(self, salesforce_data, django_object, mapping):
        # Required due to calling products which the base class doesn't have.
        for key, value in salesforce_data.iteritems():
            if key in SALESFORCE_TO_DJANGO_MAPPING[mapping]:
                key = SALESFORCE_TO_DJANGO_MAPPING[mapping][key]

                # This needs to be done ASAP and so is inside the loop, but is terminated with the None check
                # to stop excess work

                if 'Deleted__c' in salesforce_data and salesforce_data['Deleted__c']:
                    return None

                if 'Product_Portfolio_Id__c' in salesforce_data:
                    django_object.pk = salesforce_data['Product_Portfolio_Id__c'][2:]

                if 'Savings_Product_Tier__c' in salesforce_data:
                    master_product = MasterProduct.objects.get(sf_product_id=salesforce_data['Savings_Product__c'])
                    try:
                        product = master_product.return_product_from_balance(salesforce_data['Balance__c'])
                    except:
                        return None
                    django_object.product = product

                # This needs to be done ASAP and so is inside the loop, but is terminated with the None check
                # to stop excess work
                if 'Django_User_ID__c' in salesforce_data:
                    try:
                        user = User.objects.get(pk=salesforce_data['Django_User_ID__c'])
                    except User.DoesNotExist:
                        return None
                    django_object.user = user

                if 'Provider__c' in salesforce_data:
                    provider = Provider.objects.get(title=salesforce_data['Provider__c'])
                    django_object.provider = provider

                if key == 'product' or key == 'provider':
                    continue
                try:
                    self.log.append(u" -- Saving %s:%s to %s" % (key, value, django_object))
                except AttributeError:
                    pass
                setattr(django_object, key, value)
        for key, value in SALESFORCE_TO_DJANGO_MAPPING[mapping].iteritems():
            if key.startswith('Product__'):
                sf_key = key[9:]
                key = value
                if sf_key == 'bestbuy_type' and django_object.product is not None:
                    value = django_object.product.bestbuy_type.all()
                    for val in value:
                        django_object.account_type = val
                        print val
                        break
                    else:
                        value = django_object.product.master_product.bestbuy_type.all()
                        for val in value:
                            django_object.account_type = val
                            print val
                            break
                    print 'No account type?!?!?!'
                    continue
                elif django_object.product is not None:
                    value = getattr(django_object.product, sf_key)
                else:
                    print 'No Product!'
                    continue

                try:
                    print " -- Saving %s:%s to %s" % (key, value, django_object)
                except AttributeError:
                    pass
                setattr(django_object, key, value)

        return django_object

    def create(self, product_tier, portfolio_instance):
        product_tier_object = portfolio_instance(is_synched=True)
        product_tier_object = self._save_salesforce_data(product_tier, product_tier_object, 'salesforce_user_product')
        if product_tier_object is not None:
            print product_tier
            if not product_tier['Deleted__c'] or product_tier['Deleted__c'] is None:
                product_tier_object.save()
        return product_tier_object

    def update(self, product_tier):
        if 'Product_Portfolio_Id__c' in product_tier:
            if product_tier['Product_Portfolio_Id__c'].startswith('pp'):
                print('Product Portfolio')
                try:
                    product_tier_object = ProductPortfolio.objects.get(pk=product_tier['Product_Portfolio_Id__c'][2:])
                except ProductPortfolio.DoesNotExist:
                    product_tier_object = self.create(product_tier, ProductPortfolio)
                    return product_tier_object
            else:
                print('Ratetracker Reminder')
                try:
                    product_tier_object = RatetrackerReminder.objects.get(
                        pk=product_tier['Product_Portfolio_Id__c'][2:])
                except RatetrackerReminder.DoesNotExist:
                    product_tier_object = self.create(product_tier, RatetrackerReminder)
                    return product_tier_object
                except ValueError as ve:
                    print product_tier
                    raise ve
        else:
            print "Product Tier ID does not exist in response: \n%s" % product_tier
            return
        try:
            print "Product Tier: %s" % product_tier_object
        except AttributeError:
            pass
        product_tier_object = self._save_salesforce_data(product_tier, product_tier_object, 'salesforce_user_product')
        if product_tier_object is not None:
            product_tier_object.save()
        return product_tier_object

    def update_recent(self, days=10):
        # First check for providers that need to be updated
        end = datetime.datetime.now(pytz.UTC)  # we need to use UTC as salesforce API requires this
        sleep(BASE_API_LIMIT_TIME)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.Savings_Account__c.updated(end - datetime.timedelta(days=int(days)),
                                                                           end)
        self.update_multiple_products_by_id(updated_product_tiers['ids'])

    def update_multiple_products_by_id(self, updated_product_tiers_list):
        for chunk in get_chunks(updated_product_tiers_list, 10):
            result = self.get_by_id(chunk)
            if result[0] > 0:
                for product_tier in result[1]:
                    self.update(product_tier)

    def update_all(self):
        product_portfolio_query = "SELECT Id FROM Savings_Account__c"
        django_product_portfolio_query = "SELECT Id FROM Savings_Account__c"
        sleep(BASE_API_LIMIT_TIME * 10)  # Respect Salesforce API Limits
        updated_product_tiers = self.salesforce.query_all(
            product_portfolio_query
        )

        updated_product_tiers_list = []
        for product_tier in updated_product_tiers['records']:
            updated_product_tiers_list.append(product_tier['Id'])

        self.update_multiple_products_by_id(updated_product_tiers_list)

        del updated_product_tiers_list
        del updated_product_tiers
