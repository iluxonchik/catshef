from django.test import TestCase, RequestFactory
from products.views import index, product_detail
from products.models import Product, Category

class CatShefBaseTestCase(TestCase):
    """
    Base test case that sets up the data that's shared by all test cases.
    """
    def setUp(self):
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        super(CatShefBaseTestCase, cls).setUpTestData()
        cls.cat1 = Category.objects.create(
            name='meat', 
            slug='meat',
            description='The meat category.', 
            parent=None)

        cls.product1 = Product.objects.create(
            name='Chicken Breast',
            slug='chicken-breast',
            description='Chicken breast. Yes, chicken breast.',
            stock=120,
            price=10,
            offer_price=5,
            available=True)

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


class ProductDetailTestCase(CatShefBaseTestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_basic(self):
        """
        Teset that the product detail view returns a 200 response, uses
        the correct template and has the correct context.
        """
        request = self.factory.get('product/chicken-breast/')

        with self.assertTemplateUsed('products/detail.html'):
            response = product_detail(request, slug='chicken-breast')
            context = response.context
            self.assertIsNotNone(context['product'], 'Product not found in '
                'context.')
            self.assertEqual(context['product'], Product.objects.get(
                slug='chicken-breast'))
            self.assertEqual(response.status_code, 200)
            page = response.content.decode()
            price_html = ('<div class="pr-single"><p class="reduced">'
                                            '<del>$10.00</del>$5.00</p></div>')
            self.assertInHTML(price_html, page)
            self.assertInHTML('<h3>Chicken Breast</h3>', page)
