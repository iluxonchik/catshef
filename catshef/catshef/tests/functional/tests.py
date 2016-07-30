"""
Functional tests. "#" is used for user story comments and "##" is used for 
notes to developers and are not actually part of the user story.
"""
import pdb
from django.test import LiveServerTestCase
from selenium import webdriver

from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import Product, Category, ProductImage


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
            '//img[@class="img-responsive"]')

        self.assertIsNotNone(image_container)
        self.assertIsNotNone(image_container.get_attribute('src'))

        # pdb.set_trace()

        # Catherine knows that it has a lot of protein, but he knows exacty
        # how much. So she clicks on "Chicken Breast".
        chicken_breast = [product for product in products 
                                        if 'Chicken Breast' in product.text][0]
        chicken_breast.click()
        self.fail('Finish the test')
        # After that she's taken to a new page, which shows the details for
        # the product.

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
