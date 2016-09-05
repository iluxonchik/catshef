from copy import deepcopy

from cart.cart import Cart
from cart.exceptions import (ProductUnavailableException,
    NegativeQuantityException, ProductStockZeroException)
from products.models import Product, ProductOption

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

class SessionDict(dict):
    """
    Used to mock the session. It's a dict with an additional 'modified' bool 
    attribute
    """
    modified = False

class CartTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self._setup_request()
        self.cart = Cart(self.request)
        self._setup_products()
        self._setup_product_options()

    def _setup_request(self, path='/'):
        request = self.factory.get(path)
        # request.session = self.client.session
        request.session = SessionDict()  # mock SESSION
        request.user = AnonymousUser()
        return request

    def _setup_products(self):
        self.p1 = Product.objects.create(
            name='Chicken Breast',
            slug='chicken-breast',
            description='Chicken breast. Yes, chicken breast.',
            stock=120,
            price=10,
            offer_price=5,
            available=True)

        self.p2 = Product.objects.create(
            name='Turkey Breast',
            slug='turkey-breast',
            description='Turkey breast. Yes, turkey breast.',
            stock=12,
            price=0.34,
            offer_price=0.12,
            available=True)

        self.p3_unav = Product.objects.create(
            name='p3',
            slug='p3',
            stock=120,
            price=22.1,
            available=False)

        self.p4 = Product.objects.create(
            name='p4',
            slug='p4',
            stock=2,
            price=14.21,
            offer_price=5,
            available=True)

        self.p5 = Product.objects.create(
            name='p5',
            slug='p5',
            stock=10,
            price=3.14,
            available=True)

        self.p6 = Product.objects.create(
            name= 'p6',
            slug='p6',
            stock=0,
            price=9.23,
            offer_price=5.42,
            available=True)

        self.p7 = Product.objects.create(
            name='p7',
            slug='p7',
            stock=21,
            price=14.21,
            offer_price=5,
            available=True)

    def _setup_product_options(self):
        self.po1 = ProductOption.objects.create(name='option_1', price=12.31)
        self.po2 = ProductOption.objects.create(name='option_2', price=3.14)
        self.po3 = ProductOption.objects.create(name='option_3', price=10)
        self.po4 = ProductOption.objects.create(name='option_4', price=4.1)


    def test_product_addition(self):
        self.assertEqual(len(self.cart), 0)
        
        self.cart.add(product=self.p1, quantity=3)
        self.assertEqual(len(self.cart), 3)
        self.assertIn(str(self.p1.pk), self.cart._raw_cart)

        self.cart.add(product=self.p2)  # quantity defaults to 1
        self.assertEqual(len(self.cart), 4)
        self.assertIn(str(self.p2.pk), self.cart._raw_cart)

        # make sure adding existing items to cart is working
        self.cart.add(product=self.p1, quantity=1)
        self.assertEqual(len(self.cart), 5)
        p1_item = self.cart._get_item(product=self.p1)
        self.assertEqual(p1_item['quantity'], 4)

        # make sure update_quantity parameter is working as expected
        self.cart.add(product=self.p1, quantity=99, update_quantity=True)
        self.assertEqual(len(self.cart), 100)
        p1_item = self.cart._get_item(product=self.p1)
        self.assertEqual(p1_item['quantity'], 99)

    def test_product_with_options_addition(self):
        self.assertEqual(len(self.cart), 0)
        self.cart.add(product=self.p1, options=(self.po1, self.po2),
            quantity=2)
        self.assertEqual(len(self.cart), 2)
        self.cart.add(product=self.p2, quantity=3)
        self.assertEqual(len(self.cart), 5)

        # make sure same product, but without options is treated separately
        self.cart.add(product=self.p1, quantity=1)
        self.assertEqual(len(self.cart), 6)

        item_no_opt = self.cart._get_item(product=self.p1)
        item_opt = self.cart._get_item(product=self.p1, options=[self.po1,
            self.po2])
        self.assertNotEqual(item_no_opt, item_opt)
        self.assertEqual(item_no_opt['quantity'], 1)
        self.assertEqual(item_opt['quantity'], 2)

        # make sure products with options are updated, this time the
        # options are presented in the reverse order
        self.cart.add(product=self.p1, options=(self.po2, self.po1))
        self.assertEqual(len(self.cart), 7)
        item_opt = self.cart._get_item(product=self.p1, options=[self.po1,
            self.po2])
        self.assertEqual(item_opt['quantity'], 3)

        # make sure update_quantity works when used on products with options
        self.cart.add(product=self.p1, options=(self.po1, self.po2),
            update_quantity=True)
        self.assertEqual(len(self.cart), 5)
        item_opt = self.cart._get_item(product=self.p1, options=[self.po1,
            self.po2])
        self.assertEqual(item_opt['quantity'], 1)

    def test_negative_quantity_addition(self):
        with self.assertRaises(NegativeQuantityException):
            self.cart.add(product=self.p1, quantity=-1)

    def test_zero_quantity_ignored(self):
        self.cart.add(product=self.p1, quantity=4)
        prev_len = len(self.cart)
        self.cart.add(product=self.p2, quantity=0)
        self.assertEqual(len(self.cart), prev_len)
        self.assertNotIn(str(self.p2), self.cart._raw_cart)

    def test_unavailable_product_not_added(self):
        self.cart.add(product=self.p1, quantity=3)
        prev_len = len(self.cart)
        
        with self.assertRaises(ProductUnavailableException):
            self.cart.add(self.p3_unav, quantity=1)

        self.assertEqual(len(self.cart), prev_len)

    def test_product_removal(self):
        self.cart.add(product=self.p1, quantity=3)
        self.cart.add(product=self.p2, quantity=6)
        self.cart.add(product=self.p7, options=(self.po1,), quantity=8)
        self.assertEqual(len(self.cart), 17)
        
        self.cart.remove(self.p2)
        self.assertEqual(len(self.cart), 11)

        # make sure the correct item is removed
        self.assertIsNone(self.cart._get_item(product=self.p2))
        self.assertIsNotNone(self.cart._get_item(product=self.p1))
        self.assertIsNotNone(self.cart._get_item(product=self.p7,
            options=(self.po1,)))

    def test_product_with_options_removal(self):
        self.cart.add(product=self.p1, quantity=3)
        self.cart.add(product=self.p2, quantity=6)
        self.cart.add(product=self.p7, options=(self.po1,), quantity=8)
        self.assertEqual(len(self.cart), 17)
        
        self.cart.remove(self.p7, options=(self.po1,))
        self.assertEqual(len(self.cart), 9)

        # make sure the correct item is removed
        self.assertIsNone(self.cart._get_item(product=self.p7))
        self.assertIsNotNone(self.cart._get_item(product=self.p1))
        self.assertIsNotNone(self.cart._get_item(product=self.p2))

    def test_non_existent_product_removal_ignored(self):
        """
        Test that the removal of a non-existent product/options combination
        is ignored (i.e.) nothing is done.
        """
        self.cart.add(product=self.p1, options=(self.po1,), quantity=3)
        self.cart.add(product=self.p2, quantity=6)
        prev_raw_cart = deepcopy(self.cart._raw_cart)
        self.cart.remove(product=self.p1)
        self.assertEqual(prev_raw_cart, self.cart._raw_cart)
        
        self.cart.remove(product=self.p1, options=(self.po1, self.po2))
        self.assertEqual(prev_raw_cart, self.cart._raw_cart)
        
        self.cart.remove(product=self.p4)
        self.assertEqual(prev_raw_cart, self.cart._raw_cart)

    def test_over_stock_additon(self):
        """
        Test the follwoing behaviour:

        * If the stock is more than 0, but the added quantity exceeds the stock,
        add only UP TO THE AVAILABLE STOCK.

        * If the stock is 0 and an addition is made, make sure an exception is
        thrown.
        """
        self.cart.add(product=self.p5, quantity=25)
        self.assertEqual(len(self.cart), 10)

        with self.assertRaises(ProductStockZeroException):
            self.cart.add(product=self.p6)
        self.assertEqual(len(self.cart), 10)

    def test_cart_clear(self):
        # make sure cleaning an empty cart works
        self.assertEqual(len(self.cart), 0)
        self.cart.clear()
        self.assertEqual(len(self.cart), 0)

        self.cart.add(product=self.p1, options=(self.po1, self.po4, self.po3))
        self.cart.add(product=self.p2, options=(self.po1,), quantity=3)
        self.cart.add(product=self.p4, quantity=1)
        self.assertEqual(len(self.cart), 5)
        
        self.cart.clear()
        self.assertEqual(len(self.cart), 0)

    # Price testing
    # TODO: complete and change when coupon functionality is added
    def test_final_price(self):
        """
        Test that the final price (with all discounts and coupons) is correct.
        """
        price = self.cart.get_final_price()
        self.assertEqual(price, 0)

        self._price_prod_1()
        price = self.cart.get_final_price()
        self.assertEqual(price, 15)
        self.cart.clear()

        self._price_prod_2()
        price = self.cart.get_final_price()
        self.assertEqual(price, 30.57)
        self.cart.clear()
        
        self._price_prod_3()
        price = self.cart.get_final_price()
        self.assertEqual(price, 33.71)
        self.cart.clear()

        self._price_prod_4()
        price = self.cart.get_final_price()
        self.assertEqual(price, 62.67)

    def test_offer_discount(self):
        """
        Test that the total discounted price from offers is correct.
        """
        discount = self.cart.get_offer_discount()
        self.assertEqual(discount, 0)

        self._price_prod_1()
        discount = self.cart.get_offer_discount()
        self.assertEqual(discount, 15)
        self.cart.clear()

        self._price_prod_2()
        discount = self.cart.get_offer_discount()
        self.assertEqual(discount, 15.22)
        self.cart.clear()
        
        self._price_prod_3()
        discount = self.cart.get_offer_discount()
        self.assertEqual(discount, 15.22)
        self.cart.clear()

        self._price_prod_4()
        discount = self.cart.get_offer_discount()
        self.assertEqual(discount, 15.22)

    def test_total_discount(self):
        """
        Test the total discounted price (coupons + offers).
        """
        # TODO: complete when coupons are implemented, right now it's just a
        # copy of test_offer_discount()
        discount = self.cart.get_total_discount()
        self.assertEqual(discount, 0)

        self._price_prod_1()
        discount = self.cart.get_total_discount()
        self.assertEqual(discount, 15)
        self.cart.clear()

        self._price_prod_2()
        discount = self.cart.get_total_discount()
        self.assertEqual(discount, 15.22)
        self.cart.clear()
        
        self._price_prod_3()
        discount = self.cart.get_total_discount()
        self.assertEqual(discount, 15.22)
        self.cart.clear()

        self._price_prod_4()
        discount = self.cart.get_total_discount()
        self.assertEqual(discount, 15.22)

    def test_original_price(self):
        """
        Test that the original price (without offers or coupons) is correct.
        """
        price = self.cart.get_original_price()
        self.assertEqual(price, 0)

        self._price_prod_1()
        price = self.cart.get_original_price()
        self.assertEqual(price, 30)
        self.cart.clear()

        self._price_prod_2()
        price = self.cart.get_original_price()
        self.assertEqual(price, 45.79)
        self.cart.clear()
        
        self._price_prod_3()
        price = self.cart.get_original_price()
        self.assertEqual(price, 48.93)
        self.cart.clear()

        self._price_prod_4()
        price = self.cart.get_original_price()
        self.assertEqual(price, 77.89)

    def test_total_discount_percentage(self):
        """
        Test that the total discount percentage (includes everything:
        coupons, offer prices) is as expected.

        It's basically 100 - (final_price * 100 / original_price) 
        """
        discount = self.cart.get_total_discount_percentage()
        self.assertEqual(discount, 0)

        self._price_prod_1()
        discount = self.cart.get_total_discount_percentage()
        self.assertEqual(discount, 50)
        self.cart.clear()

        self._price_prod_2()
        discount = self.cart.get_total_discount_percentage()
        self.assertEqual(discount, 33.24)
        self.cart.clear()
        
        self._price_prod_3()
        discount = self.cart.get_total_discount_percentage()
        self.assertEqual(discount, 31.11)
        self.cart.clear()

        self._price_prod_4()
        discount = self.cart.get_total_discount_percentage()
        self.assertEqual(discount, 19.54)

    def test_cart_item_context(self):
        """
        Test that the items in cart return the expected "context" when iterated.

        This "context" includes:
            * quantity - item's quantity
            * total_options_price - price of all options, summed up (if present)
            * total_original_price = (original_price + options_price) * quantity
            * total_final_price - item's final price
            * total_discount_percentage - total discount percentage, unlike
            Product.price, this also includes the price of the options

        NOTE: this is a "low-level" test, any chages to the internal cart
        representation will likely require adjusting it.
        """
        # This test will use the _price_prod_*() methods, since some of the
        # values for those are already computed
        self._price_prod_1(call_previous=False)
        
        for item in self.cart:
            self.assertEqual(item['product'], self.p1)
            self.assertEqual(item['product'].price, 10)
            self.assertEqual(item['quantity'], 3)
            self.assertEqual(item['total_original_price'], 30)
            self.assertEqual(item['total_discount_percentage'], 50)
            self.assertEqual(item['total_final_price'], 15)
            self.assertEqual(item['total_options_price'], 0)

            with self.assertRaises(KeyError):
                item['options']

        self.cart.clear()

        self._price_prod_2(call_previous=False)
        for item in self.cart:
            self.assertEqual(item['product'], self.p2)
            self.assertEqual(item['quantity'], 1)
            self.assertEqual(item['total_original_price'], 15.79)
            self.assertEqual(item['total_discount_percentage'], 1.39)
            self.assertEqual(item['total_final_price'], 15.57)
            self.assertCountEqual(item['options'], [self.po1, self.po2])
            self.assertEqual(item['total_options_price'], 15.45)
        

    
    def test_coupon_discount(self):
        # TODO: when coupons are implemented
        # test savings from coupon
        pass

    # Helper methods for price testing (one builds up on the previous ones,
    # making sure that they all work in combinaiton).
    def _price_prod_1(self, call_previous=True):
        self.cart.add(product=self.p1, quantity=3)

    def _price_prod_2(self, call_previous=True):
        if call_previous:
            self._price_prod_1()
        self.cart.add(product=self.p2, options=(self.po1, self.po2),
            quantity=1)  # adds 15.57

    def _price_prod_3(self, call_previous=True):
        if call_previous:
            self._price_prod_2()
        self.cart.add(product=self.p5)  # adds 3.14

    def _price_prod_4(self, call_previous=True):
        if call_previous:
            self._price_prod_3()
        self.cart.add(product=self.p5,
            options=(self.po4,), quantity=4)  # adds 28.96