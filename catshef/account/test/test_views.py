from django.test import TestCase, RequestFactory
from products.views import index, product_detail, category, product_related
from django.core.urlresolvers import reverse
from products.models import Product, Category

class AccountBaseTestCase(TestCase):
    """
    Base test case that sets up the data shared by all test cases.
    """
    def setUp(self):
        self.factroy = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        super(AccountBaseTestCase, cls).setUpTestData()
        # TODO: setup database or use fixtures



