import collections
from decimal import Decimal

from catshef.exceptions import ArgumentError
from cart.exceptions import (NegativeQuantityException,
    ProductUnavailableException, ProductStockZeroException)
from products.utils.conversion import round_decimal, to_decimal

from django.conf import settings
from products.models import Product, ProductOption

class Cart(object):
    SESSION_ID = getattr(settings, 'CART_SESSION_ID', 'catshef.cart')
    # minimum total order price to qualify for free shipping
    FREE_SHIPPING_MIN_PRICE = to_decimal(getattr(settings, 
        'MIN_FREE_SHIPPING_PRICE', 30))
    # default price of shipping if MIN_FREE_SHIPPING_PRICE has not yet been 
    # reached
    DEFAULT_SHIPPING_PRICE = to_decimal(getattr(settings,
        'DEFAULT_SHIPPING_PRICE', 10))

    KEY_SEPARATOR = ':'

    def __init__(self, request):
        """
        Initialize cart from a request instance. Internally the cart is stored
        in the session. All of the Cart internals work with Decimals.
        All of the Cart methods return a Decimal (except for 
        magic methods).
        """
        self.session = request.session
        cart = self.session.get(Cart.SESSION_ID)
        if not cart:
            # init empty cart in session
            cart = self.session[Cart.SESSION_ID] = {}
        self._cart = cart

    def add(self, product, options=None, quantity=1, update_quantity=False):
        if quantity < 0:
            raise NegativeQuantityException('\'quantity\' cannot be negative. '
                'The passed in value was {}'.format(quantity))
        if quantity == 0:
            # if the added quantity is zero, just ignore the addition(no effect)
            return

        if not product.available:
            raise ProductUnavailableException('"{}" product (pk={}) is not'
                'avaiable and can\'t be added to the cart.'.format(product.name,
                    product.pk))

        if product.stock < 1:
            raise ProductStockZeroException('The stock for product "{}" (pk={})'
                ' is zero. It can\'t be added to the cart.'.format(product.name,
                    product.pk))

        if product.stock < quantity:
            # only add up to the available stock
            quantity = product.stock


        final_price_needs_update = True
        product_id = str(product.pk)

        # let's build the key
        key = self._get_product_key(options)
        
        if product_id not in self._cart:
            # it's the first time that product is being added to the cart
            self._cart[product_id] = {}

        cart_product = self._cart[product_id]
        if key not in cart_product:
            # it's the first time the product with such options (or without 
            # them) is being added to the cart
            cart_product[key] = self._init_cart_product(product,
                options, quantity)
            final_price_needs_update = False

        if update_quantity:
            cart_product[key]['quantity'] = quantity
        else:
            cart_product[key]['quantity'] += quantity

        if final_price_needs_update:
            self._update_product_total_final_price(product, options)

        self.save()

    def remove(self, product, options=None):
        key = self._get_product_key(options)
        cart_product = self._cart.get(str(product.pk))
        if cart_product:
            if cart_product.get(key):
                del cart_product[key]
                self.save()

    def clear(self):
        self._cart = {}
        self.save()

    def save(self):
        """
        Save the cart in session.
        """
        self.session[Cart.SESSION_ID] = self._cart
        self.session.modified = True

    # price related methods
    def get_final_price(self):
        """
        Get the cart's final price, with all of the discounts and coupons.
        """
        return sum(item['total_final_price'] for item in self)

    def get_offer_discount(self):
        """
        Get the cart's total discount from prouct offer prices.
        """
        discount_price_total = Decimal(0)
        for item in self:
            product = item['product']
            if product.has_offer:
                discount_price_total += ((product.price - 
                    product.offer_price) * item['quantity'])
        return discount_price_total

    def get_total_discount(self):
        """
        Get hte cart's total discount, this includes offer prices and coupons.
        """
        # TODO: alter when coupons are added
        return self.get_offer_discount()

    def get_original_price(self):
        """
        Get the cart's total original price (without offers or coupons).
        """
        original_price = Decimal(0)
        for item in self:
            original_price += ((item['product'].price) + 
                item['total_options_price']) * item['quantity']
        return round_decimal(original_price)

    def get_total_discount_percentage(self):
        """
        Get the total discount percentage of the cart.
        It's basically 100 - (final_price * 100 / original_price) 
        """
        if self.get_original_price() == 0:
            # we don't want to divide by zero, this happens when the carts
            # total price is 0 (like when it's empty)
            return 0
        res = Decimal(100) - (Decimal(self.get_final_price()) * Decimal(100) / 
            Decimal(self.get_original_price()))
        return round_decimal(res)

    def get_shipping_price(self):
        """
        Get the shipping price, considering the total price of the cart.
        """
        if len(self) < 1:
            return Decimal(0)

        final_price = self.get_final_price()

        return (0 if final_price >= Cart.FREE_SHIPPING_MIN_PRICE 
                 else Cart.DEFAULT_SHIPPING_PRICE)

    def get_final_price_with_shipping(self):
        """
        Get the total price of the cart, including possible shipping costs. 
        """
        return self.get_final_price() + self.get_shipping_price()

    def _update_product_total_final_price(self, product, options=None):
        """
        Updates the passed in product's (with possible options) item in cart
        context. NOTE: THIS METHOD MODIFIES THE CART DICTIONARY. It does NOT
        save the cart.
        """
        item = self._get_item(product, options)
        item['total_final_price'] = self._compute_total_final_price(product,
                                                                        item)

    def _compute_total_final_price(self, product, item):
        return round_decimal((product.current_price 
                                    + item['total_options_price'])
                                    * item['quantity'])

    def _get_product_with_options_key(self, options):
        option_ids = sorted([option.pk for option in options])
        option_ids = [str(option) for option in option_ids]
        return Cart.KEY_SEPARATOR.join(option_ids)

    def _init_cart_product(self, product, options, quantity):
        """
        Initialize cart product with the minimal information requried to display
        it in the cart.
        """
        context = {}
        context['quantity'] = Decimal(0)  # this is not a typo, it will be updated later
        total_opt_price = sum(option.price for option in options) if options else Decimal(0)
        context['total_options_price'] = to_decimal(total_opt_price)
        total_final_price = round_decimal((Decimal(product.current_price) 
                                    + context['total_options_price'])
                                    * Decimal(quantity))

        context['total_final_price'] = total_final_price
        return context


    def _complete_cart_product(self, product, key, context):
        """
        Compelete the cart's context with more info, as well as product and
        options objects (if present). This should be called in __iter__().

        This function does not alter the passed in context.
        """
        new_context = {}
        
        new_context['product'] = product

        if key:
            # init options if needed
            option_ids = key.split(Cart.KEY_SEPARATOR)
            option_ids = [int(id) for id in option_ids]
            options = ProductOption.objects.filter(pk__in=option_ids)
            new_context['options'] = options
        
        total_original_price = round_decimal((product.price 
                                    + context['total_options_price'])
                                    * context['quantity'])
        new_context['total_original_price'] = total_original_price
        
        if product.has_offer:
            discount = round_decimal((context['total_final_price']
                * Decimal(100)) / new_context['total_original_price'])
            new_context['total_discount_percentage'] = Decimal(100) - discount

        return {**context, **new_context}

    def _get_product_key(self, options):
        """
        Build the product key.
        """
        if options:
            if not isinstance(options, collections.Iterable):
                raise ArgumentError('\'options\' argument must be an iterable')
            key = self._get_product_with_options_key(options)
        else:
            key = ''
        return key

    def _get_product(self, product):
        """
        Return the product cart entry, if it's found in Cart or None, otherwise.
        """
        return self._raw_cart.get(str(product.pk))

    def _get_item(self, product, options=None):
        """
        Retrieve an item from the Cart, given the product and its options.

        Returns:
            * raw item representation, if item is found in Cart
            * None, if item is not found in Cart
        """
        key = self._get_product_key(options)
        product_cart = self._get_product(product)
        return product_cart if product_cart is None else product_cart.get(key)

    @property    
    def _raw_cart(self):
        """
        Return the raw underlying Cart representaion (dictionary).

        WARNING: this should not be acessed directly. This is useful
        for testing.
        """
        return self._cart

    def __len__(self):
        return int(sum(item['quantity'] for item in self))


    def __iter__(self):
        # TODO: complete context
        for product_pk in self._raw_cart:
            product_cart = self._raw_cart[product_pk]
            product = Product.objects.get(pk=product_pk)
            for key in product_cart:
                item = product_cart[key]
                item = self._complete_cart_product(product, key, item)
                # import pdb; pdb.set_trace()
                yield item