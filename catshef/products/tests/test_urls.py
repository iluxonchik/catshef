from django.test import TestCase, SimpleTestCase
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
        self.assertEqual(product_detail.view_name,
            'products:product_detail')
        self.assertEqual(product_detail.func.__name__, 'product_detail')
        self.assertEqual(product_detail.kwargs['slug'], 'chicken-breast')

    def test_category_url(self):
        """
        Test that the URL for category resolvese to the correct view function.
        """
        category = resolve('/category/meat/')
        self.assertEqual(category.view_name, 'products:category')
        self.assertEqual(category.func.__name__, 'category')
        self.assertEqual(category.kwargs['slug'], 'meat')

    def test_product_related_url(self):
        """
        Test that the URL for related products resolvese to the correct view function.
        """
        related = resolve('/product/related/chicken-breast/')
        self.assertEqual(related.view_name, 'products:product_related')
        self.assertEqual(related.func.__name__, 'product_related')
        self.assertEqual(related.kwargs['slug'], 'chicken-breast')
