import json
from decimal import Decimal

from cart.tests.test_cart import SessionDict

from cart.cart import Cart
from cart.views import add_to_cart, remove_from_cart, clear_cart
from products.models import (Product, Category, ProductOption,
    ProductOptionGroup, Membership)

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse, resolve
from django.conf import settings

class BaseTestCase(TestCase):
    """
    Base test case that sets up the data shared by all test cases in this
    module.
    """
    AJAX_KWARG = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}

    def post_ajax(self, func, path, data):
        request = self.factory.post(path, data=data, 
            **BaseTestCase.AJAX_KWARG)
        request.session = self.last_session_dict
        ret = func(request)
        self.last_request = request
        self.last_session_dict = request.session
        return ret

    def get_cart(self):
        return Cart(self.last_request)

    def setUp(self):
        self.factory = RequestFactory()
        self.last_request = None
        self.last_session_dict = SessionDict()

    @classmethod
    def setUpTestData(cls):
        super(BaseTestCase, cls).setUpTestData()
        cls._setup_products()
        cls._setup_product_options()
        cls._setup_product_option_groups()
        cls._setup_product_opitons_product_option_group_membership()

        cls.CART_ADD_URL = reverse('cart:cart_add')
        cls.CART_REMOVE_URL = reverse('cart:cart_remove')
        cls.CART_CLEAR_URL = reverse('cart:cart_clear')

    @classmethod
    def _setup_products(cls):
        cls.p1 = Product.objects.create(
            name='Chicken Breast',
            slug='chicken-breast',
            description='Chicken breast. Yes, chicken breast.',
            stock=120,
            price=10,
            offer_price=5,
            available=True)

        cls.p2 = Product.objects.create(
            name='Turkey Breast',
            slug='turkey-breast',
            description='Turkey breast. Yes, turkey breast.',
            stock=12,
            price=0.34,
            offer_price=0.12,
            available=True)

        cls.p3_unav = Product.objects.create(
            name='p3',
            slug='p3',
            stock=120,
            price=22.1,
            available=False)

        cls.p4 = Product.objects.create(
            name='p4',
            slug='p4',
            stock=23,
            price=14.21,
            offer_price=4,
            available=True)

        cls.p5 = Product.objects.create(
            name='p5',
            slug='p5',
            stock=10,
            price=3.14,
            available=True)

        cls.p6 = Product.objects.create(
            name='p6',
            slug='p6',
            stock=0,
            price=9.23,
            offer_price=5.42,
            available=True)

        cls.p7 = Product.objects.create(
            name='p7',
            slug='p7',
            stock=21,
            price=14.21,
            offer_price=5,
            available=True)

    @classmethod
    def _setup_product_options(cls):
        cls.po1 = ProductOption.objects.create(name='option_1', price=12.31)
        cls.po2 = ProductOption.objects.create(name='option_2', price=3.14)
        cls.po3 = ProductOption.objects.create(name='option_3', price=10)
        cls.po4 = ProductOption.objects.create(name='option_4', price=4.1)

    @classmethod
    def _setup_product_option_groups(cls):
        cls.g1 = ProductOptionGroup.objects.create(name='SomeGroup1', 
            type=ProductOptionGroup.RADIO)
        cls.g2 = ProductOptionGroup.objects.create(name='SomeGroup2', 
            type=ProductOptionGroup.DROPDOWN)
        cls.g3 = ProductOptionGroup.objects.create(name='SomeGroup3', 
            type=ProductOptionGroup.CHECKBOX)
        cls.g4 = ProductOptionGroup.objects.create(name='SomeGroup4',
            type=ProductOptionGroup.CHECKBOX)

    @classmethod
    def _setup_product_opitons_product_option_group_membership(cls):
        """
        Sets up the Membership relaitons.

        Cheatsheet:
        self.p1-> | defaults: po1, po4 | groups: g1, g2, g3
        self.p2-> | defualts: None     | groups: g2  
        self.p4-> | defaults: po1, po1  | groups: g1, g4
        """
        Membership.objects.create(group=cls.g1, option=cls.po1, default=True)
        Membership.objects.create(group=cls.g1, option=cls.po2, default=False)
        cls.g1.products.add(cls.p1)
        cls.g1.products.add(cls.p4)

        Membership.objects.create(group=cls.g2, option=cls.po3, default=False)
        Membership.objects.create(group=cls.g2, option=cls.po1, default=False)
        cls.g2.products.add(cls.p1)
        cls.g2.products.add(cls.p2)

        Membership.objects.create(group=cls.g3, option=cls.po4, default=True)
        cls.g3.products.add(cls.p1)

        # just to test a repeated option in g1 and g4 (po1)
        Membership.objects.create(group=cls.g4, option=cls.po1, default=True)
        cls.g3.products.add(cls.p4)



class AddToCartViewTestCase(BaseTestCase):

    def test_add_product(self):
        # Adding an availabe item: all good case
        post_data = { 'product_pk' : self.p1.pk, 'options_pks' : '', 
        'quantity' : 2, 'update_quantity' : False }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 2)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 2,
            'total_options_price': 0,
            'total_final_price': 10,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), 
            expected, 'Unexpected JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal(10))

        # Adding more of the same product
        post_data = { 'product_pk' : self.p1.pk, 'options_pks' : '', 
        'quantity' : 4, 'update_quantity' : False }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 6)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 6,
            'total_options_price': 0,
            'total_final_price': 30,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal(30))

        # Add with quantity update
        post_data = { 'product_pk' : self.p1.pk, 'options_pks' : '', 
        'quantity' : 5, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 5)
        
        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 5,
            'total_options_price': 0,
            'total_final_price': 25,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal(25))

        # Add another product
        post_data = { 'product_pk' : self.p2.pk, 'options_pks' : '', 
        'quantity' : 3, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 8)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 3,
            'total_options_price': 0,
            'total_final_price': 0.36,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('25.36'))

        # Adding zero quantity of an item
        prev_price = cart.get_final_price()
        post_data = { 'product_pk' : self.p2.pk, 'options_pks' : '', 
        'quantity' : 0, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 304)  # 304 - Unchanged
        cart = self.get_cart()
        self.assertEqual(len(cart), 8)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 0,
            'total_options_price': 0,
            'total_final_price': 0,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(prev_price, cart.get_final_price())

        # Adding unavailable item
        prev_price = cart.get_final_price()
        post_data = { 'product_pk' : self.p3_unav, 'options_pks' : [self.po1.pk], 
        'quantity' : 2, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 400)  # 400 - Bad Request
        cart = self.get_cart()
        self.assertEqual(len(cart), 8)

        # make sure the response content has the expected JSON in it
        expected = {
            'message' : 'Failed: the item you tried to add is unavailable.'
        }
        response_dict = json.loads(str(response.content, 'utf-8'))
        self.assertIsNotNone(response_dict['message'], '"message" not found in '
            'response JSON')
        self.assertIn('unavailable', response_dict['message'], 'Unexpected '
            'content of "message" in response JSON.')
        self.assertEqual(prev_price, cart.get_final_price())

    def test_add_product_with_options(self):
        """
        Same as test_add_product(), but now with options.
        """

        # self.po1.price + sel.po2.price = 15.45

        # Adding an availabe item: all good case
        post_data = { 'product_pk' : self.p1.pk, 'options_pks' : [self.po1.pk, 
        self.po2.pk], 
        'quantity' : 2, 'update_quantity' : False }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 2)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 2,
            'total_options_price': 15.45,
            'total_final_price': 40.9,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('40.9'))

        # Adding more of the same product
        post_data = { 'product_pk' : self.p1.pk, 'options_pks' : [self.po1.pk, 
        self.po2.pk], 
        'quantity' : 4, 'update_quantity' : False }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 6)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 6,
            'total_options_price': 15.45,
            'total_final_price': 122.7,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('122.7'))

        # Add with quantity update
        post_data = { 'product_pk' : self.p1.pk, 'options_pks' : [self.po1.pk, 
        self.po2.pk], 
        'quantity' : 5, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 5)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 5,
            'total_options_price': 15.45,
            'total_final_price': 102.25,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('102.25'))

        # Add another product
        post_data = { 'product_pk' : self.p2.pk, 'options_pks' : [self.po3.pk], 
        'quantity' : 3, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 8)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 3,
            'total_options_price': 0.12,
            'total_final_price': 30.36,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('132.61'))

        # Adding zero quantity of an item
        prev_price = cart.get_final_price()
        post_data = { 'product_pk' : self.p2.pk, 'options_pks' : [self.po3.pk], 
        'quantity' : 0, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 304)  # 304 - Unchanged
        cart = self.get_cart()
        self.assertEqual(len(cart), 8)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 0,
            'total_options_price': 0,
            'total_final_price': 0,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(prev_price, cart.get_final_price())

        # Adding unavailable item
        prev_price = cart.get_final_price()
        post_data = { 'product_pk' : self.p3_unav, 'options_pks' : [self.po1.pk], 
        'quantity' : 2, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 400)  # 400 - Bad Request
        cart = self.get_cart()
        self.assertEqual(len(cart), 8)

        # make sure the response content has the expected JSON in it
        expected = {
            'message' : 'Failed: the item you tried to add is unavailable.'
        }
        response_dict = json.loads(str(response.content, 'utf-8'))
        self.assertIsNotNone(response_dict['message'], '"message" not found in '
            'response JSON')
        self.assertIn('unavailable', response_dict['message'], 'Unexpected '
            'content of "message" in response JSON.')
        self.assertEqual(prev_price, cart.get_final_price())

    def test_add_product_with_default_options(self):
        """
        Test that when a product is added without any options passed (not even
        an empty list), its added with its default options.
        """
        # Adding product which does not have any defaults & is not in any group
        post_data = { 'product_pk' : self.p5.pk, 
        'quantity' : 1, 'update_quantity' : False }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 1)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 1,
            'total_options_price': 0,
            'total_final_price': 3.14,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('3.14'))

        # make sure the item was added
        item = cart._get_item(product=self.p5)
        self.assertIsNotNone(item)
        self.assertEqual(item['quantity'], Decimal(expected['quantity']))
        self.assertEqual(item['total_final_price'], 
            Decimal(str(expected['total_final_price'])))

        # Adding a product which does not have any defaults, but is in a group
        post_data = { 'product_pk' : self.p2.pk,
        'quantity' : 2, 'update_quantity' : False }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 3)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 2,
            'total_options_price': 0,
            'total_final_price': 0.24,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('3.38'))

        # Adding a product which has defaults
        post_data = { 'product_pk' : self.p1.pk,
        'quantity' : 2, 'update_quantity' : False }

        # make sure the item wasn't there before
        item = cart._get_item(product=self.p1, options=(self.po1, self.po4))
        self.assertIsNone(item)

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 5)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 2,
            'total_options_price': 16.41,
            'total_final_price': 42.82,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('46.20'))

        # make sure the item was added
        item = cart._get_item(product=self.p1, options=(self.po1, self.po4))
        self.assertIsNotNone(item)
        self.assertEqual(item['quantity'], Decimal(expected['quantity']))
        self.assertEqual(item['total_final_price'], 
            Decimal(str(expected['total_final_price'])))

        # Adding a product which has repeated defaults
        post_data = { 'product_pk' : self.p4.pk,
        'quantity' : 2, 'update_quantity' : False }

        # make sure the item wasn't there before
        item = cart._get_item(product=self.p4, options=(self.po1, self.po1))
        self.assertIsNone(item)

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 7)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 2,
            'total_options_price': 24.62,
            'total_final_price': 57.44,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('103.64'))

        # make sure the item was added
        item = cart._get_item(product=self.p4, options=(self.po1, self.po1))
        self.assertIsNotNone(item)
        self.assertEqual(item['quantity'], Decimal(expected['quantity']))
        self.assertEqual(item['total_final_price'], 
            Decimal(str(expected['total_final_price'])))

        # And now let's update the quantity of product with defaults
        post_data = { 'product_pk' : self.p4.pk,
        'quantity' : 1, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 6)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 1,
            'total_options_price': 24.62,
            'total_final_price': 28.62,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('71.44'))

        # make sure the item was added
        item = cart._get_item(product=self.p4, options=(self.po1, self.po1))
        self.assertIsNotNone(item)
        self.assertEqual(item['quantity'], Decimal(expected['quantity']))
        self.assertEqual(item['total_final_price'], 
            Decimal(str(expected['total_final_price'])))

        # Now, let's make sure that if quantity=0 and update_quantity=Ture,
        # the item gets removed from the cart
        post_data = { 'product_pk' : self.p4.pk,
        'quantity' : 0, 'update_quantity' : True }

        response = self.post_ajax(add_to_cart, self.CART_ADD_URL, post_data)
        self.assertEqual(response.status_code, 201)
        cart = self.get_cart()
        self.assertEqual(len(cart), 5)

        # make sure the response content has the expected JSON in it
        expected = {
            'quantity': 0,
            'total_options_price': 0,
            'total_final_price': 0,
        }
        self.assertEqual(json.loads(str(response.content, 'utf-8')), expected, 'Unexpected '
            ' JSON returned')
        self.assertEqual(cart.get_final_price(), Decimal('42.82'))

        # make sure the item was removed
        item = cart._get_item(product=self.p4, options=(self.po1, self.po1))
        self.assertIsNone(item)

    def test_add_to_cart_GET_refused(self):
        """
        Make sure that GET requests are refused.
        """
        pass