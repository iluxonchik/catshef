from django import forms

from django.test import SimpleTestCase

from account.templatetags.filters import add_attrs

class TestForm(forms.Form):
    test = forms.CharField()

class AddCssTestCase(SimpleTestCase):
    def test_css_added(self):
        data = {'test':'This is a test string'}
        f = TestForm(data=data)
        self.assertNotIn('class="some class"', str(f['test']))
        result = add_attrs(f['test'], 'some class')
        self.assertIn('class="some class"', str(result), 'Class not added to form '
            'field.')
