import pdb

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
import django.core.exceptions as exceptions

from products.models import Product, Category, ProductImage, ProductNutrition, Ingridient

class ProductsModelTestCase(TestCase):

    def __setUpIngridients(self):
        tomato_path = 'products/tests/resources/img/tomato.jpg'
        tuna_path = 'products/tests/resources/img/tuna.jpg'
        salad_path = 'products/tests/resources/img/salad.jpg'
        cucumber_path = 'products/tests/resources/img/cucumber.jpg'

        tomato_img = SimpleUploadedFile(
                name='tomato_img.jpg',
                content=open(tomato_path, 'rb').read(),
                content_type='image/jpeg')


        self.tuna_img = SimpleUploadedFile(
                name='tuna_img.jpg',
                content=open(tuna_path, 'rb').read(),
                content_type='image/jpeg')


        salad_img = SimpleUploadedFile(
                name='salad_img.jpg',
                content=open(salad_path, 'rb').read(),
                content_type='image/jpeg')


        cucumber_img = SimpleUploadedFile(
                name='cocumber_img.jpg',
                content=open(cucumber_path, 'rb').read(),
                content_type='image/jpeg')
        
        self.igr1 = Ingridient.objects.create(name='Tomato', slug='tomato',
            image=tomato_img)
        self.igr2 = Ingridient.objects.create(name='Tuna', slug='tuna',
            image=self.tuna_img)
        self.igr3 = Ingridient.objects.create(name='Salad', slug='salad',
            image=salad_img)
        self.igr4 = Ingridient.objects.create(name='Cocumber', slug='cocumber',
            image=cucumber_img)
        

    def __setUpCategories(self):
        self.cat1 = Category.objects.create(
        name='meat', 
        slug='meat',
        description='The meat category.', 
        parent=None)

    def __setUpProducts(self):
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

        # Product without image or nutrition or offer_price
        self.product3 = Product.objects.create(
            name='Entire Chicken',
            slug='entire-chicken',
            description=('An entire chicken. This product does not have a main '
                'image'),
            stock=123,
            price=321)

        self.product4 = Product.objects.create(
            name='Another Chicken Breast',
            slug='another-chicken-breast',
            description='Just another chicken breast',
            stock=999,
            price=23)

    def __setUpNutrition(self):
        self.product_nutrition1 = ProductNutrition.objects.create(protein=100, 
            carbs=1, fat=1, calories=413)


        self.product_nutrition2 = ProductNutrition.objects.create(protein=100,
            carbs=1, fat=1)

        self.product_nutrition4 = ProductNutrition.objects.create(protein=31, 
            carbs=0, fat=3.6, calories=165)

    def __link_product_nutrition(self):
        self.product1.nutrition = self.product_nutrition1
        self.product1.save()
        self.product4.nutrition = self.product_nutrition4
        self.product4.save()

    def __link_product_category(self):
        self.product1.categories.add(self.cat1)
        self.product2.categories.add(self.cat1)

    def __link_product_productimage(self):
        image_path = 'products/tests/resources/img/chicken_breast.jpg'
        another_image_path = 'products/tests/resources/img/chicken_breast2.jpg'


        self.prod_img = ProductImage.objects.create(image=SimpleUploadedFile(
                name='product1_img.jpg',
                content=open(image_path, 'rb').read(),
                content_type='image/jpeg'),
                product=self.product1)        

        self.another_product_image = ProductImage.objects.create(
                image=SimpleUploadedFile(
                name='product1_img2.jpg',
                content=open(image_path, 'rb').read(),
                content_type='image/jpeg'),
                product=self.product1)

        self.product1.main_image = self.prod_img
        self.product1.save()

        self.product2.main_image = self.prod_img
        self.product2.save()

    def __link_product_ingridient(self): 
        self.product1.ingridients.set([self.igr1, self.igr2,
            self.igr3, self.igr4])

    
    
    def setUp(self):
        self.__setUpIngridients()
        self.__setUpCategories()
        self.__setUpProducts()
        self.__setUpNutrition()
        self.__link_product_nutrition()
        self.__link_product_category()
        self.__link_product_productimage()
        self.__link_product_ingridient()
        # TODO: test OrderField (when/if needed in FT)

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

        # Make sure the urls are returned correctly
        self.assertEqual(self.product1.get_absolute_url(), 
            reverse('products:product_detail', 
                kwargs= {'slug': self.product1.slug}))

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

        with self.assertRaises(exceptions.ValidationError):
             ProductNutrition.objects.create(protein=-1, carbs=0,
                fat=0, calories=0)

        with self.assertRaises(exceptions.ValidationError):
             ProductNutrition.objects.create(protein=100, carbs=-1,
                fat=0, calories=0)
        with self.assertRaises(exceptions.ValidationError):
             ProductNutrition.objects.create(protein=200, carbs=1,
                fat=-1, calories=0)

        with self.assertRaises(exceptions.ValidationError):
             ProductNutrition.objects.create(protein=300, carbs=0,
                fat=0, calories=-42)



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

    def test_product_nullables(self):
        """
        Tests the helpers behaviour when facint with null values. Basically
        tests the field that have 'null=True'
        """
        self.assertIsNone(self.product3.main_image)
        self.assertIsNone(self.product3.protein)
        self.assertIsNone(self.product3.fat)
        self.assertIsNone(self.product3.carbs)
        self.assertIsNone(self.product3.calories)

    def test_product_helpers(self):
        """
        Test various helper methods of the Product model.
        """
        # get_all_images() testing
        images = self.product1.get_all_images()
        self.assertGreater(len(images), 0, 'Image list is empty')
        self.assertEqual(len(images), 2)
        self.assertIn(self.another_product_image, images)
        self.assertIn(self.prod_img, images)
        self.assertEqual(len(self.product2.get_all_images()), 0)
                
        # get_images() testing
        images = self.product1.get_images()
        self.assertGreater(len(images), 0, 'Image list is empty')
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0], self.another_product_image)
        self.assertEqual(len(self.product2.get_images()), 0)


        # get_all_images_urls() testing
        images_urls = self.product1.get_all_images_urls()
        self.assertGreater(len(images_urls), 0, 'Image list is empty')
        self.assertEqual(len(images_urls), 2)
        self.assertIn(self.another_product_image.image.url, images_urls)
        self.assertIn(self.prod_img.image.url, images_urls)
        self.assertEqual(len(self.product2.get_all_images()), 0)

        # get_images_urls() testing
        images_urls = self.product1.get_images_urls()
        self.assertGreater(len(images_urls), 0, 'Image list is empty')
        self.assertEqual(len(images_urls), 1)
        self.assertEqual(images_urls[0], self.another_product_image.image.url)
        self.assertEqual(len(self.product2.get_images_urls()), 0)

    def test_nutrition_facts(self):
        self.assertTrue(self.product4.has_nutrition)
        self.assertEqual(self.product4.protein_daily_percent, 62)
        self.assertEqual(self.product4.carbs_daily_percent, 0)
        self.assertEqual(self.product4.fat_daily_percent, 5.5)

        # Product with no nutrition
        self.assertFalse(self.product3.has_nutrition)
        self.assertEqual(self.product3.protein_daily_percent, 0)
        self.assertEqual(self.product3.carbs_daily_percent, 0)
        self.assertEqual(self.product3.fat_daily_percent, 0)

        # Product with some tricky values
        product_nutrition = ProductNutrition.objects.create(
            protein=3.14159265359, carbs=0, fat=0)
        self.product4.nutrition = product_nutrition
        self.product4.save()
        self.assertEqual(self.product4.protein_daily_percent, 6.3)


    def test_categories(self):
        self.assertEqual(self.cat1.get_absolute_url(), reverse('products:category',
            kwargs={'slug':self.cat1.slug}))

    def test_ingridients(self):
        tomato = Ingridient.objects.get(slug='tomato')
        self.assertEqual(self.igr1, tomato)

        prod_igr = self.product1.ingridients.all()
        self.assertIn(self.igr1, prod_igr)

        # Test ingridients to Product addtions from the Ingridient object
        igr5 = Ingridient.objects.create(name='Fake Chicken',
            slug='fake-chicken', image=self.tuna_img)
        igr5.products.add(self.product1)
        igr5.save()

        prod_igr = self.product1.ingridients.all()
        self.assertIn(igr5, prod_igr, 'New ingridient not found in Product')
        self.assertIn(self.product1, igr5.products.all())
