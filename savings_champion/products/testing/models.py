from datetime import datetime
from decimal import Decimal
from django.test import TestCase
from products.models import ProductPortfolio, Product, Provider, BestBuy, MasterProduct


class TestProvider(TestCase):

    def setUp(self):
        self.provider = Provider().save()


class TestProduct(TestCase):

    def setUp(self):
        self.product = Product(
            title="Test Product",
            publish_date=datetime.now(),
            provider=Provider.objects.all()[0],
            aer=Decimal('2.75'),
            gross_rate=Decimal('3.75'),
            bestbuy_type=BestBuy.objects.all()[0],
            master_product=MasterProduct.objects.all()[0]
        ).save()


class TestProductPortfolio(TestCase):

    def setUp(self):
        self.bestbuy_type = BestBuy()
        self.master_product = MasterProduct()
        self.product_portfolio = ProductPortfolio().save()

    def test_check_bonus(self):
        self.assertIsInstance(self.product_portfolio.has_bonus, bool)


    def test_get_is_changing(self):
        pass
