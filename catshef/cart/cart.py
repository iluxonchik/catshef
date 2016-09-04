import collections
from decimal import Decimal

from catshef.exceptions import ArgumentError
from cart.exceptions import (NegativeQuantityException,
    ProductUnavailableException)
from products.utils.conversion import round_decimal

from django.conf import settings
from products.models import Product, ProductOption

class Cart(object):
    SESSION_ID = getattr(settings, 'CART_SESSION_ID', 'catshef.cart')

    KEY_SEPARATOR = ':'

    def __init__(self, request):
        """
        Initialize cart from a request instance. Internally the cart is stored
        in the session.
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
            pass

        if not product.available:
            raise ProductUnavailableException('"{}" product (pk={}) is not'
                'avaiable and can\'t be added to the cart.'.format(product.name,
                    product.pk))

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

        if update_quantity:
            cart_product[key]['quantity'] = quantity
        else:
            cart_product[key]['quantity'] += quantity
        self.save()

    def save(self):
        """
        Save the cart in session.
        """
        self.session[Cart.SESSION_ID] = self._cart
        self.session.modified = True

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
        context['quantity'] = 0  # this is not a typo, it will be updated later
        context['total_options_price'] = (sum (option.price for option in options)
            if options else 0)
        context['total_final_price'] = (product.current_price + 
                                    context['total_options_price']) * quantity
        return context


    def _complete_cart_product(self, product_id, key, context):
        """
        Compelete the cart's context with more info, as well as product and
        options objects (if present). This should be called in __iter__().

        This function does not alter the passed in context.
        """
        new_context = {}
        product = Product.active.get(pk=int(product_id))
        
        if key:
            # init options if needed
            option_ids = key.split(Cart.KEY_SEPARATOR)
            option_ids = [int(id) for id in option_ids]
            options = ProductOption.objects.filter(pk__in=option_ids)
            new_context['options'] = options
        new_context['total_original_price'] = (product.price + 
            context['total_options_price']) * context['quantity']
        if product.has_offer:
            discount = ((context['total_final_price'] 
                * 100) / context['total_original_price'])
            discount = round_decimal(Decimal(discount))
            new_context['total_discount_percentage'] = float(100 - discount)

        return {**context, **new_context}

    def _get_product_key(self, options):
        """
        Build the product key.
        """
        if options:
            if not isinstance(options, collections.Iterable):
                raise ArgumentError('\'optons\' argument must be an iterable')
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
        num_items = 0
        for cart_item in self._cart.values():
            for item_value in cart_item.values():
                num_items += item_value['quantity']
        return num_items


