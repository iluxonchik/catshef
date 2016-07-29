import pdb

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from products.models import Product, Category, ProductImage

class ProductsModelTestCase(TestCase):
    
    def setUp(self):
        image_path = 'products/tests/resources/img/chicken_breast.jpg'
        
        self.cat1 = Category.objects.create(
            name='meat', 
            slug='meat',
            description='The meat category.', 
            parent=None)

        self.product1 = Product.objects.create(
            name='Chicken Breast',
            slug='chicken-breast',
            description='Chicken breast. Yes, chicken breast.',
            stock=120,
            available=True)

        self.product1.categories.add(self.cat1)

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
        self.assertEqual(self.cat1.description, 'The meat category.')
        self.assertIsNone(self.cat1.parent)

        self.assertEqual(len(self.product1.categories.all()), 1)
        self.assertEqual(self.product1.categories.all()[0], self.cat1)
        self.assertEqual(self.product1.name, 'Chicken Breast')
        self.assertEqual(self.product1.slug, 'chicken-breast')
        self.assertIn('product1_img', self.product1.main_image.image.name)
        self.assertEqual(self.product1.description, 
            'Chicken breast. Yes, chicken breast.')
        self.assertEqual(self.product1.stock, 120)
        self.assertTrue(self.product1.available)
        
        # Test adding multiple categories to a product        
        high_protein = self.product1.categories.create(name='high protein',
                                        slug='high-protein',
                                        description='Hight protein foods.',
                                        parent=self.cat1)

        self.assertEqual(len(self.product1.categories.all()), 2)
        self.assertIn(high_protein, self.product1.categories.all())
        self.assertEqual(high_protein.parent, self.cat1)


        # Test __str()__ returns expected name
        self.assertEqual(str(self.product1), 'Chicken Breast')
        self.assertEqual(str(self.cat1), 'meat')
