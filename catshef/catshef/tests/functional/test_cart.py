from time import sleep

from .utils import find_urls

from django.test import LiveServerTestCase, override_settings
from django.core import mail

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
# TODO: move to a serparate, shared file
from catshef.tests.functional.tests import SITE_NAME

class CartTestCase(LiveServerTestCase):

    fixtures = ['allauth_site_fixture.json',]

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(2)
        self.browser.wait = WebDriverWait(self.browser, 5)
        self._setup_database()

    def tearDown(self):
        self.browser.quit()

    @override_settings(DEBUG=True)
    def test_cart_basic(self):
        """
        Test the basic functionality of the cart.
        """
        ### NOTE: the functionality realted to the cart pop-up will not be
        ### tested or implemented now, it will be done a later time (if needed).

        # It's 7:46 AM and Jaceon just woke up. He's sad that Lakers lost by 30
        # last night, but he has a day in front of him and he wants to order
        # some food to start off the day.
        # He begins by going to the home page of <SITE_NAME>, where he notices
        # an array of products. He knows exactly what he wants, so he goes
        # straight to the "meat" category, where he's presented with an
        # array of products. He notices "Chicken Breast" in that list, and
        # he sure wants that, so he clicks on "Add To Cart". There is a message
        # notifying him that the item has been successfully added to the cart.
        # He also notices that there is a "1" displayed in the cart logo at the
        # top of the page.
        # He clicks on the cart logo at the top, and all of the products in
        # the cart pop up. He sees "View Cart" at the top right corner of that
        # popup and a "Checkout" button right at the bottom of it.
        # He notices that the current ptice of $9.34 is displayed, there is no
        # sign of original, non-discounted price or any product options there.
        # There is also a total of his order displayed: $9.34.

        # He goes back to the meat category page and notices "Turkey Breast".
        # He clicks on the product image, which brings up the fast view.
        # He notices that there are radio button options for "Salad": 
        # Lettuce ($0), Tomatoes ($0.23) and Cucumber ($1.79). "Lettuce" is
        # currently selected. He clicks on "Tomatoes". Under the "Extras"
        # options he notices a checkbox for "Extra Ketchup", he clicks on that.

        # Next to the "Add To Cart" button, he notices two arrows, which he can
        # use to alter the count of the number of products ordered. He clicks
        # on the right button twice, which increments his order number to 3.
        # After that, he cliks on "Add To Cart". The modal closes. 
        # He notices that the number
        # next to the cart icon at the top changed to 4. He clicks on the cart
        # and now the popup window dispays the following:
        # 4 items, $45.66
        # 1 x $9.34
        # 3 x $15.22

        # After that, he decides to click on the "Chicken Breast", which takes
        # him to the product's page. He clicks on "Add To Cart" straight away
        # and notices that the number next to the cart icon at the top has now
        # changed to 5. He clicks on it and the popup window displays the
        # following:
        # 5 items, $55.00
        # 2 x $9.34
        # 3 x $15.22

        # He then gets a call from his friend Adre and he discovers that he'll
        # be joining him. Actually, it was Jayceon who called him and invited
        # himself to his friends house, but that's beyond the point.
        # He decies to order some more Chicken Breast, this time with the 
        # "Extra Ketchup" option, as well as Velouté sauce. He sets the
        # quantity to "2" and clicks on "Add To Cart" .

        # The cart now displays the number 7 next to it. He clicks on the cart
        # to find the following content:
        # 5 items, $73.52
        # 2 x $9.34
        # 3 x $15.22
        # 2 x $11.76

        # He thinks he's ready to go so, he clicks on "View Cart". This takes
        # him to the carts url, where he's presented with the cart and the items
        # in it.

        # He finds there the following:

        # 2 x <s>12.32</s> $9.34 | Subtotal: $18.68
        # 3 x $15.22 | Subtotal: $45.66
        #    Tomatoes ($0.23), Extra Ketchup(FREE)
        # 2 x <s>14.74</s> $11.76 | Subtotal: $23.52
        #     Velouté($2.42), Extra Ketchup(FREE)
        # Shipping: 0$
        # Total: $73.52

        # He deciced to update the number of the first item to 2. Instantly,
        # the counter near the cart at the top updates to now show 6.
        # The cart page also updates, and now looks like the following:

        # 1 x <s>12.32</s> $9.34 | Subtotal: $9.34
        # 3 x $15.22 | Subtotal: $45.66
        #    Tomatoes ($0.23), Extra Ketchup(FREE)
        # 2 x <s>14.74</s> $11.76 | Subtotal: $23.52
        #     Velouté($2.42), Extra Ketchup(FREE)
        # Shipping: 0$
        # Total: $64.18

        # He then updates the second item count to 4, the counter next to the
        # cart at the top now shows 7 and the cart page looks like the following:

        # 1 x <s>12.32</s> $9.34 | Subtotal: $9.34
        # 4 x $15.22 | Subtotal: $60.88
        #    Tomatoes ($0.23), Extra Ketchup(FREE)
        # 2 x <s>14.74</s> $11.76 | Subtotal: $23.52
        #     Velouté($2.42), Extra Ketchup(FREE)
        # Shipping: 0$
        # Total: $79.40

        # He then decies that the doesn't need the last item, so he removes it.
        # The change is instantly reflected: the counter at the top, next to
        # the cart now shows 5. The cart page now looks like the following:

        # 1 x <s>12.32</s> $9.34 | Subtotal: $9.34
        # 4 x $15.22 | Subtotal: $45.66
        #    Tomatoes ($0.23), Extra Ketchup(FREE)
        # Shipping: 0$
        # Total: $55.88

        # He then decides to remove the second item too. The cart at the top
        # now shows the number 1 next to it, and the cart page now looks like
        # the following:

        # 1 x <s>12.32</s> $9.34 | Subtotal: $9.34
        # Shipping: $10.00
        # Total: $19.34

        # Jayceon notices that now he has to pay for shipping.
        self.fail('Finish the test!')

    # TODO: remove duplacates below
    def get_element_by_xpath(self, xpath):
        return self.browser.wait.until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    
    def get_element_by_id(self, id):
        return self.browser.wait.until(
            EC.presence_of_element_located((By.ID, id)))

    def get_button_by_xpath(self, xpath):
        return self.browser.wait.until(
            EC.element_to_be_clickable((By.XPATH, xpath)))

    def get_button_by_id(self, element_id):
        return self.browser.wait.until(EC.element_to_be_clickable((By.ID, id)))

    def is_element_present(self, by, selector):
        """
        Check if an element is present on the current page. Allows to be tested
        with self.assertTrue()/self.assertFalse().
        """
        try:
            self.browser.wait.until(
                EC.presence_of_element_located((by, selector)))
            return True
        except (NoSuchElementException, TimeoutException):
            return False

    def _login_from_modal(self, email, password):
        login_btn = self.get_element_by_id('login-reg-modal-btn')
        login_btn.click()

        login_input = self.get_element_by_id('id_login')
        pwd_input = self.get_element_by_id('id_password')
        login_btn = self.get_element_by_xpath('//input[@value="Sign In"]')

        login_input.send_keys(email)
        pwd_input.send_keys(password)
        login_btn.click()

    def _setup_database(self):
        pass