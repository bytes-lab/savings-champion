from __future__ import absolute_import
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import ModelField
from common.models import UserReferral, Referrer, Profile

from products.models import MasterProduct, ProductTier, Provider, Product, ProductPortfolio, RatetrackerReminder, \
    BestBuy

__author__ = 'josh'

class ProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Provider
        fields = (
        'id', 'title', 'slug', 'created_date', 'last_updated', 'deleted', 'fscs_parent', 'fscs_licence_holder',
        'ethical', 'ethical_rating', 'moodys_rating', 'fitchs_rating', 'building_society', 'mutual', 'bank',
        'high_street', 'phone', 'website', 'meets_service_standard', 'reason_to_exclude', 'compliance_checked',
        'provider_maximum', 'get_shared_licence_providers'
        )


    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(ProviderSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProductSerializer(serializers.ModelSerializer):
    facts = serializers.SerializerMethodField()

    def get_facts(self, obj):
        return obj.facts.rendered

    class Meta:
        model = MasterProduct
        fields = ('id', 'title', 'slug', 'created_date', 'last_updated', 'deleted', 'sf_product_id', 'provider',
                  'status', 'bestbuy_type', 'account_type', 'available_from', 'available_to',
                  'is_internet_access', 'is_phone_access', 'is_post_access', 'is_branch_access', 'is_cc_access',
                  'is_open_internet', 'is_open_telephone', 'is_open_post', 'is_open_branch', 'is_open_cc',
                  'is_isa_transfers_in', 'is_fixed', 'facts', 'fscs_licence', 'term', 'term_fixed_date', 'notice',
                  'shariaa', 'existing_only', 'locals_only', 'operating_balance', 'operating_balance_rate',
                  'other_reason_to_exclude_this_product', 'other_reason_compliance_checked', 'trust_funds_accepted',
                  'trust_types_excluded', 'interest_paid_frequency', 'minimum_age', 'maximum_age', 'open_limit_total',
                  'open_limit_own_name', 'open_limit_joint_name', 'bonus_term', 'bonus_end_date'
        )

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(ProductSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class OldProductTierSerializer(serializers.ModelSerializer):

    facts = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug', 'created_date', 'last_updated', 'deleted', 'sc_code', 'publish_after',
            'account_type', 'provider', 'minimum', 'maximum', 'minimum_monthly',
            'maximum_monthly', 'aer', 'gross_rate', 'monthly_gross', 'net_20', 'net_40', 'bestbuy_type',
            'ratetracker_type', 'is_internet_access', 'is_phone_access', 'is_post_access', 'is_branch_access',
            'is_cc_access',
            'is_open_internet', 'is_open_telephone', 'is_open_post', 'is_open_branch', 'is_open_cc',
            'is_isa_transfers_in', 'withdrawals', 'term', 'facts', 'fscs_licence', 'is_sc_stamp', 'is_paid',
            'minimum_age', 'maximum_age',
            'bonus_amount', 'underlying_gross_rate', 'notice', 'url',
            'is_fixed', 'master_product', 'verdict', 'status'
        )

    def get_facts(self, obj):
        return obj.facts.rendered

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(OldProductTierSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProductTierSerializer(serializers.ModelSerializer):

    facts = serializers.SerializerMethodField()

    bonus_term = serializers.SerializerMethodField()
    bonus_end_date = serializers.SerializerMethodField()

    class Meta:
        model = ProductTier
        fields = (
            'uuid', 'title', 'slug', 'created_date', 'last_updated', 'deleted', 'sc_code', 'publish_after',
            'available_until', 'account_type', 'provider', 'minimum', 'maximum', 'minimum_monthly',
            'maximum_monthly', 'aer', 'gross_rate', 'monthly_gross', 'net_20', 'net_40', 'ratetracker_type',
            'is_internet_access', 'is_phone_access', 'is_post_access', 'is_branch_access', 'is_cc_access',
            'is_open_internet', 'is_open_telephone', 'is_open_post', 'is_open_branch', 'is_open_cc',
            'is_isa_transfers_in', 'facts', 'fscs_licence', 'is_sc_stamp', 'is_paid',
            'status', 'bonus_amount', 'underlying_gross_rate', 'url',
            'sf_product_tier_id', 'is_fixed', 'product', 'verdict', 'joint_account_only', 'tier_type', 'bonus_term',
            'bonus_end_date'
        )

    def get_facts(self, obj):
        return obj.facts.rendered

    def get_bonus_term(self, obj):
        return obj.bonus_term

    def get_bonus_end_date(self, obj):
        return obj.bonus_end_date

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(ProductTierSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProductPortfolioSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductPortfolio
        fields = (
            'id', 'product', 'opening_date', 'provider', 'bonus_term', 'notice', 'get_latest_rate', 'user',
            'account_type', 'balance', 'is_deleted', 'created_date', 'last_updated'
        )



class RatetrackerReminderSerializer(serializers.ModelSerializer):

    class Meta:
        model = RatetrackerReminder
        fields = (
            'id', 'maturity_date', 'provider', 'term', 'get_latest_rate', 'user',
            'account_type', 'balance', 'is_deleted', 'created_date', 'last_updated'
        )


class BestBuySerializer(serializers.ModelSerializer):
    class Meta:
        model = BestBuy
        fields = (
            'id', 'title', 'client_type'
        )


class ConciergeReferrerReportingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReferral


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name'
        )


class ReferrerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referrer
        fields = (
            'uuid', 'name'
        )


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'uuid', 'user', 'dob', 'telephone', 'salutation', 'postcode', 'newsletter', 'ratealerts', 'created_date',
            'last_updated', 'is_synched', 'ip_address', 'source', 'skeleton_user', 'filled_in_name',
            'ratetracker_threshold', 'ratetracker_threshold_set'
        )


