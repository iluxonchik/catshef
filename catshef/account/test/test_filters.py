from django import forms
from django.forms import BoundField

from django.test import SimpleTestCase

from account.templatetags.html_filters import add_class, add_placeholder

class TestForm(forms.Form):
    test = forms.CharField()
    test2 = forms.CharField(widget=forms.widgets.TextInput(attrs={
        'placeholder':'plh'
        }))

class HTMLFiltersTestCase(SimpleTestCase):
    def test_add_class(self):
        data = {'test':'This is a test string'}
        f = TestForm(data=data)
        self.assertNotIn('class="some class"', str(f['test']))
        result = add_class(f['test'], 'some class')
        self.assertTrue(type(result) is BoundField, 'Returned field has ' 
            'wrong type')
        self.assertIn('class="some class"', str(result), 'Class not added to form '
            'field.')
    
    def test_add_placeholder(self):
        data = {'test':'This is a test string'}
        f = TestForm(data=data)
        self.assertNotIn('placeholder="Test"', str(f['test']))
        result = add_placeholder(f['test'], 'Test')
        self.assertTrue(type(result) is BoundField, ('Returned field has ' 
            'wrong type'))
        self.assertIn('placeholder="Test"', str(result), 'Placeholder not added'
            ' to form field.')

    def test_original_attr_preserved(self):
        """
        Test that the existing field attrs are preserved.
        """
        data = {'test':'This is a test string', 'test2':''}
        f = TestForm(data=data)
        self.assertIn('placeholder="plh"', str(f['test2']))
        self.assertNotIn('class="much class"', str(f['test2']))
        result = add_class(f['test2'], 'much class')
        self.assertTrue(type(result) is BoundField, ('Returned field has ' 
            'wrong type'))
        self.assertIn('placeholder="plh"', str(result), 'Exisitng attrs not'
            ' preserved.')
        self.assertIn('class="much class"', str(result), 'Class not added'
            ' to form field.')

    def test_placeholder_attr_replaced(self):
        """
        Test that an exisitng placeholder is replaced.
        """
        data = {'test':'This is a test string', 'test2':''}
        f = TestForm(data=data)
        self.assertIn('placeholder="plh"', str(f['test2']))
        result = add_placeholder(f['test2'], 'new placeholder')
        self.assertTrue(type(result) is BoundField, ('Returned field has ' 
            'wrong type'))
        self.assertNotIn('plh', str(result), 'Exisitng attrs'
            ' preserved.')
        self.assertIn('placeholder="new placeholder"', str(result), 'New '
            'placeholder not added to form field.')


