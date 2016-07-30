import pdb

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from products.models import Product, Category, ProductImage, ProductNutrition

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
            price=10,
            offer_price=5,
            available=True)

        self.product2 = Product.objects.create(
            name='Turkey Breast',
            slug='turkey-breast',
            description='Turkey Breast. Yes, that\'s right',
            stock=42,
            price=20)

        self.product_nutrition1 = ProductNutrition.objects.create(protein=100, 
            carbs=1, fat=1, calories=413)

        self.product_nutrition2 = ProductNutrition.objects.create(protein=100,
            carbs=1, fat=1)

        self.product1.nutrition = self.product_nutrition1

        self.product1.categories.add(self.cat1)
        self.product2.categories.add(self.cat1)

        self.prod_img = ProductImage.objects.create(image=SimpleUploadedFile(
                name='product1_img.jpg',
                content=open(image_path, 'rb').read(),
                content_type='image/jpeg'),
                product=self.product1)

        self.product1.main_image = self.prod_img
        self.product1.save()

        self.product2.main_image = self.prod_img
        self.product2.save()

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

        self.assertEqual(self.product1.main_image_url, 
            self.product1.main_image.image.url,
            '\'main_image_url\' shorthand in Product model did not match the ' 
            'actual main image url')
        
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

    def test_product_nutrition(self):
        prod_nutr = self.product1.nutrition
        self.assertEqual(prod_nutr, self.product_nutrition1)

        self.assertEquals(prod_nutr.protein, self.product1.protein)
        self.assertEquals(prod_nutr.carbs, self.product1.carbs)
        self.assertEquals(prod_nutr.fat, self.product1.fat)
        self.assertEquals(prod_nutr.calories, self.product1.calories)
        
        self.assertEquals(prod_nutr.protein, 100)
        self.assertEquals(prod_nutr.carbs, 1)
        self.assertEquals(prod_nutr.fat, 1)
        self.assertEquals(prod_nutr.calories, 413)

        nutrition_dict = self.product1.nutrition_dict
        self.assertEquals(nutrition_dict['protein'], self.product1.protein)
        self.assertEquals(nutrition_dict['carbs'], self.product1.carbs)
        self.assertEquals(nutrition_dict['fat'], self.product1.fat)
        self.assertEquals(nutrition_dict['calories'], self.product1.calories)

        # Make sure that the caloric content is automatically computed, and 
        # added to the model if it's ommited during the object creation
        self.assertEquals(self.product_nutrition2.calories, 413)


    def test_product_price_and_offer(self):
        self.assertEqual(self.product1.current_price, 5, 'Offer price was '
                                                'not returned correctly.')
        self.assertEquals(self.product1.discount_percentage, 50, 'Discount'
            ' percentage was not computed correctly.')

        self.product2.discount_percentage = 20
        self.assertEquals(self.product2.discount_percentage, 20, 'Discount'
            ' percentage was not stored correctly.')
        # 20 * 0.8 = 16
        self.assertEquals(self.product2.current_price, 16, 'Offer price was '
            'not returned correctly.')
