import pdb

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
import django.core.exceptions as exceptions

from decimal import Decimal, ROUND_UP

from products.models import (Product, Category, ProductImage, ProductNutrition, 
    Ingridient, ProductOption, ProductOptionGroup, Membership)

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

        self.product5 = Product.objects.create(
            name='Unavailable',
            slug='unavailable',
            description='Just an unavailable product',
            stock=999,
            price=23,
            available=False)

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


    def test_available_manager(self):
        products = Product.active.all()
        unavailable_products_num = len(Product.objects.filter(available=False))
        all_products_num = len(Product.objects.all())
        self.assertEqual(len(products), all_products_num - unavailable_products_num)

    def test_similar_products(self):
        product1 = Product.objects.create(
            name='Turkey',
            slug='turkey',
            description='Just a turkey',
            stock=120,
            price=15,
            offer_price=9,
            available=True)

        product2 = Product.objects.create(
            name='Protein Powder',
            slug='protein-powder',
            description='Protein powder.',
            stock=120,
            price=10,
            offer_price=5,
            available=True)        

        product3 = Product.objects.create(
            name='Worm',
            slug='worm',
            description='Uhhh, yeah, it\'s a worm...',
            stock=120,
            price=19,
            offer_price=9.7,
            available=True)        

        product4 = Product.objects.create(
            name='Chicken Breast',
            slug='chicken-breast-new',
            description='Chicken breast',
            stock=120,
            price=19,
            offer_price=9.7,
            available=True)

        product5 = Product.objects.create(
            name='Chicken Breast 2',
            slug='chicken-breast-new2',
            description='Chicken breast 2',
            stock=120,
            price=19,
            offer_price=9.7,
            available=False)

        cat1 = Category.objects.create(
        name='meat', 
        slug='meat',
        description='The meat category.', 
        parent=None)

        cat2 = Category.objects.create(
        name='Hig Protein', 
        slug='high-protein',
        description='High protein category.', 
        parent=None)

        cat3 = Category.objects.create(
        name='Things With Wings', 
        slug='thigns-with-wings',
        description='If it got wings, you can find it here!', 
        parent=None)

        product1.categories.set((cat1, cat2, cat3))
        product2.categories.add(cat2)
        product4.categories.set((cat1, cat2))
        product5.categories.add(cat1)

        sim_prod = product1.similar_products()
        self.assertEqual(len(sim_prod), 2)
        self.assertEqual(sim_prod[0], product4, 'First product is not '
                                                'Chicken Breast')
        self.assertEqual(sim_prod[1], product2, 'Second product is not Protein '
                                                'Powder')

        sim_prod = product1.similar_products(limit=1)
        self.assertEqual(len(sim_prod), 1)
        self.assertEqual(sim_prod[0], product4, 'First product is not '
                                                'Chicken Breast')

        sim_prod = product1.similar_products(manager=Product.objects)
        self.assertEqual(len(sim_prod), 3)
        self.assertEqual(sim_prod[0], product4, 'First product is not '
                                                'Chicken Breast')
        self.assertEqual(sim_prod[2], product2, 'Second product is not Protein '
                                                'Powder')

class ProductOptionTestCase(TestCase):

    def setUp(self):
        self.po_1 = ProductOption.objects.create(name='option_1', price=12)
        self.po_2 = ProductOption.objects.create(name='option_2', price=3.14159)
        self.po_3 = ProductOption.objects.create(name='option_3', price=2.678,
            description='Option 3')

    def test_product_option_basic(self):
        self.assertEqual(self.po_1.name, 'option_1')
        self.assertEqual(self.po_1.price, 12)
        self.assertEqual(self.po_3.description, 'Option 3')
        self.assertIsNone(self.po_1.description)

    def test_product_option_price_rounding(self):
        self.assertEqual(self.po_2.rounded_price(), 3.14)
        self.assertEqual(self.po_3.rounded_price(), 2.68)

        self.assertEqual(self.po_2.rounded_price(precision=3), 3.142)
        self.assertEqual(self.po_2.rounded_price(precision=3, 
            rounding=ROUND_UP), 3.142)        
        self.assertEqual(self.po_2.rounded_price(rounding=ROUND_UP), 3.15)

    def test_str(self):
        string_repr = self.po_2.__str__()
        self.assertEqual(string_repr, 'option_2')

class ProductOptionGroupTestCase(TestCase):

    def setUp(self):
        self._setup_product_option_groups()

    def _setup_product_option_groups(self):
        self.g1 = ProductOptionGroup.objects.create(name='group_1',
            type=ProductOptionGroup.RADIO)
        self.g2 = ProductOptionGroup.objects.create(name='group_2',
            type=ProductOptionGroup.CHECKBOX)
        self.g3 = ProductOptionGroup.objects.create(name='group_3',
            type=ProductOptionGroup.DROPDOWN, description='Group 3')

    def test_product_option_group_basic(self):
        self.assertEqual(self.g3.name, 'group_3')
        self.assertEqual(self.g3.type, ProductOptionGroup.DROPDOWN)
        self.assertEqual(self.g3.description, 'Group 3')
        self.assertIsNone(self.g1.description)


    def test_types(self):
        self.assertEqual(self.g1.type, ProductOptionGroup.RADIO)
        self.assertEqual(self.g2.type, ProductOptionGroup.CHECKBOX)
        self.assertEqual(self.g3.type, ProductOptionGroup.DROPDOWN)

    def test_str(self):
        self.assertEqual(self.g1.__str__(), 'group_1')

class ProductOptionProductMembershipTestCase(TestCase):

    def setUp(self):
        self._setup_product_options()
        self._setup_product_option_groups()
        self._setup_memberships()

    def _setup_product_options(self):
        self.po_1 = ProductOption.objects.create(name='option_1', price=12)
        self.po_2 = ProductOption.objects.create(name='option_2', price=3.14159)
        self.po_3 = ProductOption.objects.create(name='option_3',
            price=2.678, description='Option 3')

    def _setup_product_option_groups(self):
        self.g1 = ProductOptionGroup.objects.create(name='group_1',
            type=ProductOptionGroup.RADIO)
        self.g2 = ProductOptionGroup.objects.create(name='group_2',
            type=ProductOptionGroup.CHECKBOX)
        self.g3 = ProductOptionGroup.objects.create(name='group_3',
            type=ProductOptionGroup.DROPDOWN, description='Group 3')
        self.g4 = ProductOptionGroup.objects.create(name='group_4',
            type=ProductOptionGroup.RADIO)

        self.g5 = ProductOptionGroup.objects.create(name='group_5',
            type=ProductOptionGroup.RADIO)
        self.g6 = ProductOptionGroup.objects.create(name='group_6',
            type=ProductOptionGroup.DROPDOWN)

    def _setup_memberships(self):
        self.m1 = Membership.objects.create(option=self.po_3, group=self.g4, default=False)
        self.m2 = Membership.objects.create(option=self.po_1, group=self.g1, default=True)
        self.m3 = Membership.objects.create(option=self.po_2, group=self.g1)


    def test_from_product_option_retrival(self):
        po = ProductOption.objects.filter(groups__name='group_1')
        self.assertEqual(len(po), 2)
        self.assertIn(self.po_1, po)
        self.assertIn(self.po_2, po)

    def test_from_product_group_retrival(self):
        opt = ProductOptionGroup.objects.filter(options__name='option_1')
        self.assertEqual(len(opt), 1)
        self.assertEqual(opt[0], self.g1)

    def test_membership_retrival(self):
        m1 = Membership.objects.filter(option=self.po_3, group=self.g4)
        self.assertIn(self.m1, m1)
        self.assertEqual(len(m1), 1)
        self.assertEqual(m1[0].default, False)

        m2 = Membership.objects.filter(option=self.po_1, group=self.g1)
        self.assertIn(self.m2, m2)
        self.assertEqual(len(m2), 1)
        self.assertEqual(m2[0].default, True)

        m3 = Membership.objects.filter(option=self.po_2, group=self.g1)
        self.assertIn(self.m3, m3)
        self.assertEqual(len(m3), 1)
        self.assertEqual(m3[0].default, False)

    def test_radio_default_restrictions(self):
        Membership.objects.create(group=self.g5, option=self.po_1)
        Membership.objects.create(group=self.g5, 
            option=self.po_2, default=True)
        prev_count = len(Membership.objects.all())
        
        with self.assertRaises(exceptions.ValidationError):
            Membership.objects.create(group=self.g5, 
                option=self.po_3, default=True)
        
        count = len(Membership.objects.all())
        self.assertEqual(prev_count, count)

    def test_dropdown_default_restrictions(self):
        Membership.objects.create(group=self.g6, option=self.po_1)
        Membership.objects.create(group=self.g6,
            option=self.po_2, default=True)
        prev_count = len(Membership.objects.all())

        with self.assertRaises(exceptions.ValidationError):
            Membership.objects.create(group=self.g6, 
                option=self.po_3, default=True)
        
        count = len(Membership.objects.all())
        self.assertEqual(prev_count, count)