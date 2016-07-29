from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    parent = models.ForeignKey('Category', null=True, 
        related_name='child_categories', on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Represents a product that's being sold.
    """
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    categories = models.ManyToManyField('Category', related_name='products')
    stock = models.PositiveSmallIntegerField()  # range: [0, 32767]
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, 
                                         decimal_places=2, null=True)
    # TODO: set default image (replace null=True) or just use default image
    # in template rendering (decide)
    main_image = models.ForeignKey('ProductImage', 
        related_name='main_image_of', null=True, on_delete=models.SET_NULL)
    available = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        """
        If there is an 'offer_price' set and it's less than 'price',
        'product.current_price' will return 'product.offer_price', 
        otherwise product.price will be returned.

        This should make the price access in templates and order price 
        computation less verbose (basically avoiding many if's, which can cause 
        bugs, if it's ommited in some place by mistake).
        """
        if self.offer_price and self.offer_price < self.price:
            return self.offer_price
        return self.price

    @property
    def discount_percentage(self):
        """
        Get the discount as a percentage. 

        Note: if offer_price >= price, 0 will be returned
        """
        if self.offer_price and self.offer_price < self.price:
            return 100 - (self.offer_price * 100 / self.price)

    @discount_percentage.setter
    def discount_percentage(self, percent):
        """
        Set the 'offer_price' as a percentage of the 'price'.

        Args:
            precent (int): how much percent to discount. A percentual value has 
            to be passed. For example, if you want the discount to be of 30%, 
            youcwould write: 'product.discount_percentage=30'.
        """
        self.offer_price = self.price * (100 - percent)/100
    

class ProductImage(models.Model):
    # image will be uploaded to MEDIA_ROOT/products/%Y/%m/%d/
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    product = models.ForeignKey('Product', related_name='images')
    # TODO: Order field
