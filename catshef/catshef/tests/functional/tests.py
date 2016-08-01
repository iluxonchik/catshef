"""
Functional tests. "#" is used for user story comments and "##" is used for 
notes to developers and are not actually part of the user story.
"""
import pdb
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common import exceptions

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

from products.models import Product, Category, ProductImage, ProductNutrition


# Constants. Since the name of the store is yet to be decided, it'll be stored
# in variables for easy future change
SITE_NAME = 'CatFood'

class FoodItemsTestCase(LiveServerTestCase):
    """
    Test case wich realates to the listing and detail of items.
    No user actions like adding items to the cart and checking the order
    will be tested here.
    """

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(2)
        self.__setup_database()

    def tearDown(self):
        self.browser.quit()

    def test_homepage_has_items_list_accross_pages(self):
        """
        Test that there are items in the home page and that they are split
        accross pages.
        """

        # Catherine just woke up from her nap. She's feeling hungry, but really
        # doesn't feel like coocking. She desperately wants to get some protein
        # in.

        # This is when she rememebers that her friend Kenny told her about this
        # awesome new website, called '<SITE_NAME>', located at <url>.

        # So she opens her laptop and visits the homepage of '<SITE_NAME>'
        home_page = self.browser.get(self.live_server_url + '/')

        # She knows she's on the right page because it says '<SITE_NAME>' in the
        # title and the headin
        self.assertIn(SITE_NAME, self.browser.title)
        heading = self.browser.find_element_by_tag_name('h1')
        self.assertIn(SITE_NAME, heading.text)
        
        # She is preseted a variety of foods and drinks. She notices that
        # there is a "Chicken Breast" option. There is also a picture of the 
        # product.
        products_container = self.browser.find_element_by_xpath(
                                    '//div[@id="tab1"]/div[@class="con-w3l"]')
        self.assertIsNotNone(products_container)

        products = products_container.find_elements_by_xpath(
                                    '//div[@class="col-md-3 m-wthree"]//h6/a')

        any('Chicken Breast' in product.text for product in products)

        image_container = products_container.find_element_by_xpath(
            '//a[@data-target="#myModal1"]//img[@class="img-responsive"]')

        self.assertIsNotNone(image_container)
        self.assertIsNotNone(image_container.get_attribute('src'))

        url_before_click = self.browser.current_url

        # Se notices that 'Chicken Breast' has a 50% discount on it
        offer_imgs = self.browser.find_elements_by_xpath(
            '//a[@class="offer-img"]')


        self.assertIsNotNone(offer_imgs, 'Offer images not found')
        cb_offer_img = [img for img in offer_imgs 
                            if img.find_element_by_tag_name('img').get_attribute('alt') == 'Chicken Breast']
        self.assertEqual(len(cb_offer_img), 1, 
            'Single image with alt "Chicken Breast" not found')

        cb_offer_img_parent = cb_offer_img[0].find_element_by_xpath('..')

        offer_text = cb_offer_img_parent.find_element_by_xpath('.//div[@class="offer"]').text
        self.assertEquals('-50%', offer_text)

        # "Turkey Breast" doesn't have a discount price, so it's not present
        # there

        tb_offer_img = [img for img in offer_imgs 
                            if img.find_element_by_tag_name('img').get_attribute('alt') == 'Turkey Breast']
        self.assertEqual(len(cb_offer_img), 1, 
            'Single image with alt "Turkey Breast" not found')

        tb_offer_img_parent = tb_offer_img[0].find_element_by_xpath('..')
        
        with self.assertRaises(exceptions.NoSuchElementException):
            offer_text = tb_offer_img_parent.find_element_by_xpath('.//div[@class="offer"]').text


        # Catherine knows that it has a lot of protein, but he knows exacty
        # how much.

        # She clicks on the image and after that shes's presented with a 
        # quick overview of the product, within the same page.
        image_href = image_container.find_element_by_xpath('..')
        image_href.click()

        body = self.browser.find_element_by_tag_name('body')
        body_class = body.get_attribute('class')
        self.assertEquals(body_class, 'modal-open')
        self.assertEqual(url_before_click, self.browser.current_url)

        active_modal = self.browser.find_element_by_xpath('//div[@aria-hidden="false"]')
        self.assertIsNotNone(active_modal, 'Active modal not found')

        # She notices that the product has 31g of protein, "0g" of
        # carbohydrates, 3.6g of carbs and 165 calories.
        nutr_p = active_modal.find_element_by_xpath(
            '//p[@class="in-para"]')
        self.assertIsNotNone(nutr_p, 'Nutritional info not found '
                                                        'in the modal')
        nutr_info = nutr_p.text

        self.assertIn('Protein: 31g', nutr_info)
        self.assertIn('Carbs: 0g', nutr_info)
        self.assertIn('Fat: 3.6g', nutr_info)
        self.assertIn('Calories: 165', nutr_info)

        # After that, she clicks on the 'X' to close the modal
        close_btn = active_modal.find_element_by_xpath(
            '//button[@class="close"]')

        close_btn.click()
        self.browser.implicitly_wait(3)

        ## Make sure the modal closed, by making sure that there is no open
        ## modal present
        with self.assertRaises(exceptions.NoSuchElementException):
            self.browser.find_element_by_xpath('//div[@aria-hidden="false"]')



        # So she clicks on "Chicken Breast".
        chicken_breast = [product for product in products 
                                        if 'Chicken Breast' in product.text][0]
        chicken_breast.click()
        # After that she's taken to a new page, which shows the details for
        # the product.
        self.assertEqual(self.browser.current_url,
            self.live_server_url + reverse('products:product_detail',
                kwargs={'slug': 'chicken-breast'}))

        self.fail('Finish the test')
        
        # She notices that there are a couple of images of the product and that
        # she can switch between them.

        # There is also a description of the product.

        # There is also information about the nutritional contents. She can
        # see how many protein, carbohydrates, fats and calories the product has.

        # She notices that the product has "31 g" of protein, "0g" of
        # carbohydrates, "3.6 g" of carbs and 165 calories.

        # She also notices that "Chicken Breast" belongs to the "meat" and
        # "high protein" categories. She can click on any of them.

        ## TODO: decide if we're gonna have both: "Related Products" and 
        ## "Often Bought Together" secitions or just one of them.

        ## She also notices that there are some "Related Products" at the
        ## bottom. One of the products in that list is "Chicken Breast". She
        ## clicks on it and is taken to the deatail page of that product.
        ## After that, she goes back to the previous page.

        ## She also notices that there is a "Often Bought Together" section,
        ## which contains other products. The first product on the list, is
        ## "Water". She clicks on it and is taken to the deatail page of that 
        ## product. After that, she goes back to the previous page.

        # After clicking on the "high protein" category, she is taken to another
        # page, which shows various products within that category.

        # She notices that that page has "Turkey Breast", "Tuna" and
        # "Scrambled Eggs".

        # Exited about all of that, she decides to back to the main page
        # and see what other options there are. She scrolls to the end of the
        # page and notices that there is a paginator at the bottom. Currently,
        # the page "1" is selected.

        # She wants to go to page "2", for that she notices that she has two
        # options: she can either click on "2" directly in the paginator, or
        # press the ">" symbol on the right side of the paginator.

        # Since she's on the first page, she also noties that the "<" symbol is
        # not clickable.

        # She proceeds to click on "2" and she's taken to a new page, she
        # notices that the url now changed to <url>.

        # On the new page she sees a list of more products.


    def __setup_database(self):
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


        self.product1_nutrition = ProductNutrition.objects.create(protein=31, 
            carbs=0, fat=3.6, calories=165)

        self.product1.nutrition = self.product1_nutrition

        self.product1.save()
