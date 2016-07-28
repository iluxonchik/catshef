from django.test import TestCase, RequestFactory
from products.views import index

class CatShefBaseTestCase(TestCase):
    """
    Base test case that sets up the data that's shared by all test cases.
    """
    def setUp(self):
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        super(CatShefBaseTestCase, cls).setUpTestData()
        # TODO: setup database

class IndexViewTestCase(CatShefBaseTestCase):

    def test_index_view_basic(self):
        """
        Test that the index view returns a 200 response and uses the correct 
        template.
        """
        request = self.factory.get('/')
        response = index(request)

        with self.assertTemplateUsed('products/index.html'):
            # I was a little puzzled on how this works, so I decided to look 
            # it up. So I went to the source code and found what actually was
            # going on.
            # How this works: assertTemplateUsed returns a context manager,
            # inside that it subscribes to all "render template" signals, 
            # so every time a template is rendered, it gets notified. It stores 
            # all of the template names in a list. When the context manager's 
            # '__exit__()' is called (at the end of "with:"), first it 
            # unsubscribes from the signals and then it checks 
            # if 'products/index.html' is actually within that list of template 
            # names that have been rendered.
            response = index(request)
            self.assertEqual(response.status_code, 200)
