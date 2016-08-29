import re
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

class UserAccountsTestCase(LiveServerTestCase):

    fixtures = ['allauth_site_fixture.json',]

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(2)
        self.browser.wait = WebDriverWait(self.browser, 5)
        self.__setup_database()

    def tearDown(self):
        self.browser.quit()

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

    def _assert_is_logged_in_menu(self):
        """
        Tests whether the menu displays the correct info when the user is logged
        in.

        Assert that:
            * There is a "Profile" button
            * There is a "Logout" button
            * There is no "Login/Register" button
        """
        self.assertTrue(self.is_element_present(By.ID, 'profile-header-menu'))
        self.assertTrue(self.is_element_present(By.ID, 'logout-header-menu'))
        self.assertFalse(self.is_element_present(By.ID, 'login-reg-modal-btn'))


    def _assert_is_logged_out_menu(self):
        """
        Tests whether the menu displays the correct info when the user is logged
        out.

        Assert that:
            * There is a "Login/Register" button
            * There is no "Profile" button
            * There is no"Logout" button
        """
        self.assertFalse(self.is_element_present(By.ID, 'profile-header-menu'))
        self.assertFalse(self.is_element_present(By.ID, 'logout-header-menu'))
        self.assertTrue(self.is_element_present(By.ID, 'login-reg-modal-btn'))

    def _login_from_modal(self, email, password):
        login_btn = self.get_element_by_id('login-reg-modal-btn')
        login_btn.click()

        login_input = self.get_element_by_id('id_login')
        pwd_input = self.get_element_by_id('id_password')
        login_btn = self.get_element_by_xpath('//input[@value="Sign In"]')

        login_input.send_keys(email)
        pwd_input.send_keys(password)
        login_btn.click()

    @override_settings(DEBUG=True)
    def test_basic_user_accounts(self):
        """
        Tests the basic user account functionality. Includes: local site 
        registration, login, profile view and change.
        """

        EMAIL = 'john@rules.com'
        PWD = 'johnisthebest'
        NAME = 'John Terry'
        PHONE = '+351960000000'


        # It's a sunny Sunday morning and John decides to check out the
        # <SITE_NAME> website and order something to drink. He visits the
        # home page and notices that there is a 'Login/Register' link at the top 
        # of the page. He clicks on the link and a from pops up whit
        # "Login"(selected) and "Register" options. He clicks on the 
        # "create an account" link, where he's asked to enter the following
        # details: name(required), email(required), password(required) and
        # phone number(optional)
        # He has to enter the password twice, in separate fields.
        home_page = self.browser.get(self.live_server_url + '/')
        log_reg_btn = self.get_element_by_id('login-reg-modal-btn')
        log_reg_btn.click()
        ## make sure modal is showoing
        modal = self.get_element_by_xpath(
            '//div[@class="modal fade login in" and @id="login-modal"]')
        
        ## make sure modal is "Login"
        modal_title = self.get_element_by_xpath('//h4[@class="modal-title"]')
        self.assertEqual(modal_title.text, 'Login with')

        reg_link = modal.find_element_by_link_text('create an account')
        reg_link.click()
        sleep(2)  # give JS time to change the title
        ## make sure modal changed to "Register"
        modal_title = self.get_element_by_xpath('//h4[@class="modal-title"]')
        self.assertEqual(modal_title.text, 'Register with')        
        
        ## For now, the phone number field will be very simple, later on
        ## make it pretty (like a flag selector for country, etc).

        # He enters the following values for each: {'name': 'John Terry',
        # 'email':'john@rules.com', 'phone':'+351960000000', 
        # 'password':'johnisthebest'}

        ## TODO: adjust element id names, with the ones generated
        name = modal.find_element_by_id('id_name')
        name.send_keys(NAME)
        
        email = modal.find_element_by_id('id_email')
        email.send_keys(EMAIL)

        phone = modal.find_element_by_id('id_phone')
        phone.send_keys(PHONE)
        
        pwd1 = modal.find_element_by_id('id_password1')
        pwd1.send_keys(PWD)

        pwd2 = modal.find_element_by_id('id_password2')
        pwd2.send_keys(PWD)

        prev_url = self.browser.current_url
        # After that, he clicks on the 'Create Account' button at the bottom.
        submit_btn = modal.find_element_by_xpath(
            '//input[@value="Create account"]')
        submit_btn.click()
        sleep(2)  # give browser time to reload the page

        # He's redirected to the page he was on before, and there is a message
        # asking him to confirm his email address.
        self.assertEqual(self.browser.current_url, prev_url)
        ## The message will be a snackbar
        self.assertIn('Registration successful, please confirm your ' 
            'email address', self.browser.page_source)
        # He notices that there is no more "Login/Register" links at the top,
        # instead, he finds two new links at the top: "Profile" and "Logout".
        self._assert_is_logged_in_menu()

        # He notices that he has recieved a new email with a link to confirm his
        # email address, he clicks on that link, after which he's taken
        # to his profile page.
        self.assertEqual(len(mail.outbox), 1, 'Registration email not sent.')
        confirmation_url = find_urls(mail.outbox[0].body)
        self.assertEqual(len(confirmation_url), 1, 'Confirmation email message'
            ' does not have the expected confirmation url.')
        self.browser.get(confirmation_url)
        mail.outbox = []  # clear the outbox
        btn = self.get_button_by_xpath('//button[@type="submit"]')
        btn.click()
        self.assertIn('/account/', self.browser.current_url)
        
        # There is a message saying that his email address has been successfully
        # confirmed and there is a "Verfified"
        # green text next to his email address on his profile page.
        self.assertIn('You have confirmed john@rules.com', 
            self.browser.page_source)
        self.assertInHTML('<span class="label label-success">Verified</span>',
            self.browser.page_source)

        ## The "unconfirmed email address" won't change much, except when he
        ## tries to proceed with the order form the cart,the user will be
        ## presented with a page asking him to confim his email address or,
        ## in case he's not logged in, to create an account.

        # He clicks on "Logout" link , which logs him out
        logout_btn = self.get_element_by_id('logout-header-menu')
        logout_btn.click()

        # He notices that is now a "Login/Register" button, the "Logout"
        # is gone and there is no sign of "Profile" button
        self._assert_is_logged_out_menu()

        ## user will be redirected to the login page after the previous logout
        ## since we want to login via modal and THERE IS AN ID clash,
        ## buggy behaviour from testig might occur
        ## TODO: fix id clash (issue #79)
        self.browser.get(self.live_server_url + '/')
        
        # He then tries to log in again using the same credetntials he used to 
        # register his account. To do that, he clicks on the "Login/Register"
        # button in the menu and inputs his credentials.
        self._login_from_modal(EMAIL, PWD)

        # He knows he's logged in, because he was notified about with a 
        # message stating that and he also notices that the "Login/Register"
        # link is gone, instead he sees "Profile" and "Logout" links.
        self._assert_is_logged_in_menu()

        # He goes to his profile, by clicking on the "Profile" link at the top
        profile_link = self.get_element_by_id('profile-header-menu') 
        profile_link.click()
        self.assertIn(reverse('profile'), self.browser.current_url)

        # where he's presented with his current profile
        # information (name,phone number, priamry email)
        prof_box = self.get_element_by_xpath('//div[@class="panel panel-info"]')
        prof_box = prof_box.get_attribute('innerHTML')
        self.assertIn(NAME, prof_box)
        self.assertIn(EMAIL, prof_box)
        self.assertIn(PHONE, prof_box)

        # he clicks on "Edit Profle" and sees that he can update his existing 
        # info
        edit_profile_link = self.browser.find_element_by_xpath(
            '//a[contains(text(), "Edit Profile")]')
        edit_profile_link.click()
        self.assertIn(reverse('edit_profile'), self.browser.current_url)

        # He notices that the "Name" box contains his current name, while
        # the Phone box his current phone number.
        # He decides to update his name to "John George Terry", 
        # leaving the other fields inact.
        new_name = "John George Terry"

        name = self.get_element_by_id('id_name')
        self.assertEquals(name.get_attribute('value'), NAME)
        
        phone = self.get_element_by_id('id_phone')
        self.assertEquals(phone.get_attribute('value'), PHONE)

        name.clear()
        name.send_keys(new_name)

        # After clicking on the "Update Profile" button, he's taken to the "Profile"
        # page (from where he's clicked on "Edit") and notices that the
        # presented name has changed.
        update_btn = self.get_button_by_xpath(
            '//button[contains(text(), "Update Profile")]')
        update_btn.click()
        self.assertIn(reverse('profile'), self.browser.current_url)

        prof_box = self.get_element_by_xpath('//div[@class="panel panel-info"]')
        prof_box = prof_box.get_attribute('innerHTML')
        self.assertNotIn(NAME, prof_box)
        self.assertIn(new_name, prof_box)

        # He clicks on "Edit Profile" once again
        edit_profile_link = self.browser.find_element_by_xpath(
            '//a[contains(text(), "Edit Profile")]')
        edit_profile_link.click()

        # This time, the "Name" box is pre-filled with his new name
        name = self.get_element_by_id('id_name')
        self.assertEquals(name.get_attribute('value'), new_name)

        # He notices that there is a "Cancel" button, so he clicks on it,
        # which takes him straight to his "Profile" page
        cancel_btn = self.browser.find_element_by_xpath(
            '//button[contains(text(), "Cancel")]')
        cancel_btn.click()
        self.assertIn(reverse('profile'), self.browser.current_url)

        # The next thing he does is clicks on "Email Settings"
        email_btn = self.get_element_by_xpath(
            '//a[contains(text(), "Email Settings")]')
        email_btn.click()

        # He decides to add a new e-mail address: 'john@terry.com'
        new_email = 'john@terry.com'
        email_field = self.get_element_by_id('id_email')
        email_field.send_keys(new_email)

        add_btn = self.browser.find_element_by_xpath(
            '//button[contains(text(), "Add Email")]')
        add_btn.click()

        # He notices that his new email address is marked as "Unverified".
        ## this is really just a minimal check, but much better than noting 
        self.assertIn("Unverified", self.browser.page_source)
        #import pdb; pdb.set_trace()

        # He also notices that there is a  message informing him that
        # a confirmation email has been sent to his new email address
        self.assertIn("Confirmation e-mail sent to {}.".format(new_email),
            self.browser.page_source)

        # He notices that he's recieved a new email, asking him to verify his
        # new email address
        self.assertEqual(len(mail.outbox), 1, 'Verification email not sent.')
        confirmation_url = find_urls(mail.outbox[0].body)
        self.assertEqual(len(confirmation_url), 1, 'Verification email message'
            ' does not have the expected url.')
        mail.outbox = []  # clear the outbox

        # He selects his new email and clicks on the "Resend Activation Email" 
        # link, after which he notices that he's recieved a new email,
        # asking him to confirm his account.

        new_mail_radio = self.get_element_by_id('email_radio_2')
        new_mail_radio.click()

        resend_btn = self.get_element_by_xpath(
            '//button[contains(text(), "Re-send Verification")]')
        resend_btn.click()

        self.assertEqual(len(mail.outbox), 1, 'Verification email not sent.')
        confirmation_url = find_urls(mail.outbox[0].body)
        self.assertEqual(len(confirmation_url), 1, 'Verification email message'
            ' does not have the expected url.')
        mail.outbox = []  # clear the outbox

        # He logs out and logs in with his newly added e-mail account.
        logout_btn = self.get_element_by_id('logout-header-menu')
        logout_btn.click()
        sleep(2)
        self._assert_is_logged_out_menu()

        self.assertIn(reverse('account_login'), self.browser.current_url,
            'Not in login url')

        # Let's login from the standalone page
        login_input = self.get_element_by_id('id_login')
        pwd_input = self.get_element_by_id('id_password')
        login_btn = self.get_element_by_xpath('//button[contains(text(),"Sign In")]')

        login_input.send_keys(new_email)
        pwd_input.send_keys(PWD)
        login_btn.click()

        self._assert_is_logged_in_menu()


        # He clicks on the email verification link and there are no
        # "Unverified" e-mails in the list anymore.
        self.browser.get(confirmation_url)
        btn = self.get_button_by_xpath('//button[@type="submit"]')
        btn.click()
        self.assertIn('/account/', self.browser.current_url)

        self.browser.get(reverse('account_email'))
        self.assertNotIn("Unverified", self.browser.page_source)

    def test_facebook_auth(self):
        # TODO
        pass
    
    def __setup_database(self):
        pass