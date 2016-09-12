from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.http.request import QueryDict

from cart.tests.test_cart import SessionDict
from catshef.exceptions import ArgumentError

from cart.cart import Cart
from products.models import (Product, ProductOption, ProductOptionGroup,
    Membership)
from cart.utils import add_item_build_json_response, parse_POST

class RequestMock(object):
    """
    Mocked request object.
    """
    def __init__(self):
        self.session = SessionDict()
        self.user = AnonymousUser()
        self.POST = QueryDict(mutable=True)

class UtilsTestCase(TestCase):
    def setUp(self):
        self.request = RequestMock()
        self.cart = Cart(self.request)

    @classmethod
    def setUpTestData(cls):
        cls.p1 = Product.objects.create(
            name='Chicken Breast',
            slug='chicken-breast',
            description='Chicken breast. Yes, chicken breast.',
            stock=120,
            price=10,
            offer_price=5,
            available=True)        

        cls.p2 = Product.objects.create(
            name='Whiskas',
            slug='whiskas',
            description='That cat food.',
            stock=120,
            price=3,
            offer_price=2,
            available=True)

        cls.po1 = ProductOption.objects.create(name='option_3', price=1)
        cls.po2 = ProductOption.objects.create(name='option_4', price=2)

    def test_add_item_json_response(self):
        # Test getting product which is in cart
        self.cart.add(self.p1, quantity=3)
        
        expected = {
            'quantity': 3,
            'total_options_price': 0,
            'total_final_price': 15,
        }

        item = add_item_build_json_response(self.cart, self.p1)
        self.assertEqual(item, expected)

        # Test getting product with options which is in cart
        self.cart.add(self.p1, quantity=2, options=[self.po1, self.po2])
        
        expected = {
            'quantity': 2,
            'total_options_price': 3,
            'total_final_price': 16,
        }

        item = add_item_build_json_response(self.cart, product=self.p1,
            options=[self.po1, self.po2])
        self.assertEqual(item, expected)

        # Test getting a product not in cart
        item = add_item_build_json_response(self.cart, product=self.p2)

        expected = {
            'quantity': 0,
            'total_options_price': 0,
            'total_final_price': 0,
        }
        self.assertEqual(expected, item)
        
        item = add_item_build_json_response(self.cart, product=self.p1, 
            options=[self.po1])
        self.assertEqual(expected, item)

    def test_parse_POST(self):
        self.request.POST['product_pk'] = 1
        self.request.POST.setlist('options_pks', [1,2])
        self.request.POST['quantity'] = 22
        self.request.POST['update_quantity'] = True

        res = parse_POST(self.request)
        self.assertEqual(res['product'], self.p1)
        self.assertCountEqual(res['options'], [self.po1, self.po2])
        self.assertEqual(res['quantity'], 22)
        self.assertEqual(res['update_quantity'], True)
        self.assertEqual(res['add_with_default_options'], False)

        self.request.POST = QueryDict(mutable=True)
        self.request.POST['product_pk'] = 1
        self.request.POST.setlist('options_pks', [])
        self.request.POST['quantity'] = 22

        res = parse_POST(self.request)
        self.assertEqual(res['product'], self.p1)
        self.assertCountEqual(res['options'], [])
        self.assertEqual(res['quantity'], 22)
        self.assertEqual(res['update_quantity'], False)
        self.assertEqual(res['add_with_default_options'], False)

        self.request.POST = QueryDict(mutable=True)
        self.request.POST['product_pk'] = 1

        res = parse_POST(self.request)
        self.assertEqual(res['product'], self.p1)
        
        self.assertIsNone(res['options'])

        self.assertEqual(res['quantity'], 1)
        self.assertEqual(res['update_quantity'], False)
        self.assertEqual(res['add_with_default_options'], True)

    def test_parse_POST_errors(self):
        with self.assertRaises(Http404):
            self.request.POST['product_pk'] = 22
            self.request.POST.setlist('options_pks', [1,2])
            self.request.POST['quantity'] = 22
            self.request.POST['update_quantity'] = True

            res = parse_POST(self.request)
        
        with self.assertRaises(Http404):
            self.request.POST['product_pk'] = 22
            self.request.POST.setlist('options_pks', [99,2])
            self.request.POST['quantity'] = 22
            self.request.POST['update_quantity'] = True

            res = parse_POST(self.request)

