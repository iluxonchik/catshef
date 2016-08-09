from django.test import TestCase, RequestFactory
from products.views import product_related

# NOTE: This doens't seem to belong here, but to siplify things, I'm going to
# take advantage of an exisitng view that requires AJAX requests.
# I'm well aware that the decorator isn't a part of the 'products' app,
# so it's probably not the best place to test. 
# But it's better to have the test than not to have it, so let's go.
class AJAXRequiredDecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_ajax_requried_decorator(self):
        # Non-AJAX request
        request = self.factory.get('/product/related/chicken_breast/?page=1')
        response = product_related(request, 'chicken-breast')
        self.assertEqual(response.status_code, 400)

        request = self.factory.get('/product/related/chicken_breast/?page=1',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = product_related(request, 'chicken-breast')
        self.assertEqual(response.status_code, 200)
