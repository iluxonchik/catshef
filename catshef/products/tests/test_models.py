from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from products.models import Product, Category, ProductImage


class ProductsModelTestCase(TestCase):
    
    def setUp(self):
        image_path = 'catshef/products/tests/resources/img/chicken_breast.jpg'
        
        self.cat1 = Category.objects.create(
            name='meat', 
            slug='meat', 
            parent=None)

        self.product1 = Product.objects.create(
            category=self.cat1,
            name='Chicken Breast',
            slug='chicken-breast',
            description='Chicken breast. Yes, chicken breast',
            stock=120,
            available=True)

        self.prod_img = ProductImage.objects.create(image=SimpleUploadedFile(
                name='product1_img.jpg',
                content=open(image_path, 'rb').read(),
                content_type='image/jpeg'),
                product=self.product1)

        self.product1.main_image = self.prod_img
        self.product1.save()

        # TODO: test OrderField (when needed in FT)

    def test_products_basic(self):
        """
        Test the basic funcitonality of the Product's models.
        """
        self.assertEqual(self.cat1.name, 'meat')
        self.assertEqual(self.cat1.slug, 'meat')
        self.assertIsNone(self.cat1.parent)

        self.assertEqual(self.product1.category, self.cat1)
        self.assertEqual(self.product1.name, 'Chicken Breast')
        self.assertEqual(self.product1.slug, 'chicken-breast')
        self.assertEqual('product1_img.jpg', self.product1.main_image.name)
        self.assertEqual(self.product1.description, 
            'Chicken breast. Yes, chicken breast')
        self.assertEqual(self.product1.stock, 120)
        self.assertTrue(self.product1.available)
