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
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField()
    categories = models.ManyToManyField('Category', related_name='products')
    stock = models.PositiveSmallIntegerField()  # range: [0, 32767]
    # TODO: set default image (replace null=True) or just use default image
    # in template rendering (decide)
    main_image = models.ForeignKey('ProductImage', 
        related_name='main_image_of', null=True, on_delete=models.SET_NULL)
    available = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    # image will be uploaded to MEDIA_ROOT/products/%Y/%m/%d/
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    product = models.ForeignKey('Product', related_name='images')
    # TODO: Order field
    