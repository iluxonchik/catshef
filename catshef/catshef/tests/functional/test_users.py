from django.test import LiveServerTestCase, override_settings

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
# TODO: move to a serparate, shared file
from catshef.tests.functional.tests import SITE_NAME 


class UserAccountsTestCase(LiveServerTestCase):

    fixtures = ['allauth_site_fixture.json',]

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(2)
        self.browser.wait = WebDriverWait(self.browser, 10)
        self.__setup_database()

    def tearDown(self):
        self.browser.quit()

    @override_settings(DEBUG=True)
    def test_basic_user_accounts(self):
        """
        Tests the basic user account functionality. Includes: local site 
        registration, login, profile view and change.
        """

        # It's a sunny Sunday morning and John decides to check out the
        # <SITE_NAME> website and order something to drink. He visits the
        # home page and notices that there is a 'register' link at the top of
        # the page. He clicks on the link and is taken to a page where a
        # registration form is presented. He's asked to enter the following
        # details: # name(required), email(required), password(required) and
        # phone number(optional)
        # He has to enter the password twice, in separate fields.

        ## For now, the phone number field will be very simple, later on
        ## make it pretty (like a flag selector for country, etc).

        # He enters the following values for each: {'name': 'John Terry',
        # 'email':'john@rules.com', # 'password':'johnisthebest'}

        # After that, he clicks on the 'Register' button at the bottom.
        # He's redirected to the page he was on before, and there is a message
        # asking him to confirm his email address.

        # He notices that there is no more "Login/Register" links at the top,
        # instead, he finds two new links at the top: "Profile" and "Logout".

        # He notices that he has recieved a new email with a link to confirm his
        # email address, he clicks on that link, after which he's taken
        # to his profile page. 

        # At the top, there is a green success message stating that his email
        # address has been successfully confirmed and there is a "(Confirmed)"
        # green text next to his email address on his profile page.

        ## The "unconfirmed email address" won't change much, except when he
        ## tries to proceed with the order form the cart,the user will be
        ## presented with a page asking him to confim his email address or,
        ## in case he's not logged in, to create an account.

        # He goes to his profile, by clicking on the "Profile" link at the top, 
        # where he's presented with his current profile
        # information (name, email), he clicks on "Edit" and sees that he can:
        # (##TODO) specify some additonal info
        # or update his existing info. He decides to update his email address
        # to 'john_terry@rules.com', leaving the other fields inact.
        # He edits his existing email address to the desired one and clicks on
        # "Update" button at the bottom of the page. He also notices that there
        # is a "Cancel" button.

        # After clicking on the "Update" button, he's taken to the "Profile"
        # page (from where he's clicked on "Edit") and notices that the
        # presented email address has changed. He notices that his new email
        # address is marked as "unconfirmed" and there is a
        # "Resend Activation Email" link next to it. 
        # He also notices that there is a success message at the top
        # that asks him to confirm his email address.

        # He notices that he's recieved a new email, asking him to confirm his
        # account.

        # He clicks on the "Resend Activation Email" link
        # and notices that he's recieved a new email, asking him to confirm his
        # account.

        # He clicks on the "Logout" link at the top, after which he's redirected
        # to a page asking him to confirm his logout. He clicks on the "Logout"
        # button, after which he's redirected to the home page, with a message
        # at the top stating that he's been logged out successfully.

        # He notices that the "Profile" and "Logout" links at the top of the
        # page are gone, instead the "Login/Register" link is there back again.

    def test_facebook_auth(self):
        # TODO
        pass

    
    def __setup_database(self):
        pass