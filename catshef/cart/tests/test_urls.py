from django.test import TestCase, SimpleTestCase
from django.core.urlresolvers import resolve

from cart.views import add_to_cart, remove_from_cart, clear_cart

class CartURLsTestCase(TestCase):

    def test_add_to_cart_url(self):
        add_to_cart = resolve('/cart/add/')
        self.assertEqual(add_to_cart.view_name, 'cart:cart_add')
        self.assertEqual(add_to_cart.func.__name__, 'add_to_cart')
    
    def test_remove_form_cart_url(self):
        add_to_cart = resolve('/cart/remove/')
        self.assertEqual(add_to_cart.view_name, 'cart:cart_remove')
        self.assertEqual(add_to_cart.func.__name__, 'remove_from_cart')

    def test_cart_clear_url(self):
        cart_clear = resolve('/cart/clear/')
        self.assertEqual(cart_clear.view_name, 'cart:cart_clear')
        self.assertEqual(cart_clear.func.__name__, 'clear_cart')

