import decimal

from django.db import models
import django.core.exceptions as exceptions

from django.core.urlresolvers import reverse

from products.utils.nutrition import CAL2000


class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    parent = models.ForeignKey('Category', null=True, 
        related_name='child_categories', on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug':self.slug})

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Represents a product that's being sold.
    """
    name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, db_index=True)
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
    nutrition = models.ForeignKey('ProductNutrition', 
        on_delete=models.SET_NULL, null=True, blank=True)
    ingridients = models.ManyToManyField('Ingridient', related_name='products')
    available = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def get_all_images(self):
        """
        Get all images, including the 'main_image', if present.

        Returns an empty list if no images are found.
        """
        if not self.images:
            return []

        images = self.images.all()
        return images

    def get_images(self):
        """
        Get all images, except the 'main_image', if present.

        Return an empty list if no images are found.
        """
        images = self.get_all_images()
        return images.exclude(pk=self.main_image.pk) if self.main_image else images

    def get_all_images_urls(self):
        """
        Get all images urls, including the 'main_image', if present.

        Returns an empty list if no images are found.
        """
        return [image.image.url for image in self.get_all_images()]

    def get_images_urls(self):
        """
        Get all images urçs, except the 'main_image', if present.

        Return an empty list if no images are found.
        """
        return [image.image.url for image in self.get_images()]

    def __str__(self):
        return self.name

    @property
    def main_image_url(self):
        """
        Shorthand for the main image url
        """
        if not self.main_image:
            return None
        return self.main_image.image.url


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
        if self.has_offer:
            return self.offer_price
        return self.price

    @property
    def discount_percentage(self):
        """
        Get the discount as a percentage. 

        Note: if offer_price >= price, 0 will be returned
        """
        if self.has_offer:
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

    @property
    def has_offer(self):
        """
        Returns True if the product has a valid offer price and False
        otherwise.
        """
        return self.offer_price and self.offer_price < self.price

    @property
    def protein(self):
        if not self.nutrition:
            return None
        return self.nutrition.protein

    @property
    def carbs(self):
        if not self.nutrition:
            return None
        return self.nutrition.carbs

    @property
    def fat(self):
        if not self.nutrition:
            return None
        return self.nutrition.fat

    @property
    def calories(self):
        if not self.nutrition:
            return None
        return self.nutrition.calories

    @property
    def nutrition_dict(self):
        if not self.nutrition:
            return None
        return {'protein': self.nutrition.protein, 
                'carbs': self.nutrition.carbs,
                'fat': self.nutrition.fat,
                'calories': self.nutrition.calories,
                }

    @property
    def has_nutrition(self):
        return self.nutrition is not None

    @property
    def protein_daily_percent(self, nutr_info=CAL2000, round=True):
        if self.has_nutrition:
            res = self.protein*100/nutr_info.protein
            return self.__round(res, round)
        return 0
    
    @property
    def carbs_daily_percent(self, nutr_info=CAL2000, round=True):
        if self.has_nutrition:
            res = self.carbs*100/nutr_info.carbs
            return self.__round(res, round)
        return 0
    
    @property
    def fat_daily_percent(self, nutr_info=CAL2000, round=True):
        if self.has_nutrition:
            res = self.fat*100/nutr_info.fat
            return self.__round(res, round)
        return 0

    def __round(self, value, round=True):
        return float('{0:.1f}'.format(value)) if round else value

        
    

class ProductImage(models.Model):
    # image will be uploaded to MEDIA_ROOT/products/%Y/%m/%d/
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    product = models.ForeignKey('Product', related_name='images')
    # TODO: Order field

class ProductNutrition(models.Model):
    __PROT_CAL = __CARB_CAL = 4
    __FAT_CAL = 9

    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbs = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1)
    calories = models.DecimalField(max_digits=10, decimal_places=1, null=True, 
        blank=True)

    def save(self, *args, **kwargs):
        if self.calories is None:
            self.calories = type(self).__PROT_CAL * self.protein + type(self).__CARB_CAL * self.carbs + type(self).__FAT_CAL * self.fat
        super(ProductNutrition, self).save(*args, **kwargs)

class Ingridient(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='ingridients/%Y/%m/%d/')

    def __str__(self):
        return self.name


