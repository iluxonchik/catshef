from django.test import TestCase
from django.core.urlresolvers import resolve

from products.views import index

class ProductsURLsTestCase(TestCase):
    
    def test_root_url_uses_index_view(self):
        """
        Test that the root of the site resolves to the correct view function.
        """
        root = resolve('/')
        self.assertEqual(root.func, index)

    def test_product_details_url(self):
        """
        Test that the URL for product detail resolves to the correct view
        function.
        """
        product_detail = resolve('/product/chicken-breast/')
        self.assertEqual(product_detail.view_name, 'product_detail')
        self.assertEqual(product_detail.func.__name__, 'product_detail')
        self.assertEqual(product_detail.kwargs['slug'], 'chicken-breast')



