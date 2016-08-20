from catshef.snackbar import SnackBar

from django.test import SimpleTestCase
from django.contrib import messages

from django.http import HttpRequest

from django.conf import settings
from importlib import import_module

class SnackBarTestCase(SimpleTestCase):

    def setUp(self):
        self.request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        self.request.session = engine.SessionStore(session_key)

    def test_snackbar_added(self):
        SnackBar.add_data(self.request, '{ message: "Message Sent", actionHandler: function(event) {}, actionText: "Undo", timeout: 10000 }')
        snackbar = SnackBar.get(self.request)
        self.assertEqual(len(snackbar), 1, 'Unexpected message count')

    def test_snackbar_retrieved(self):
        data1 = '{ message: "Message Sent", actionHandler: function(event) {}, actionText: "Undo", timeout: 10000 }'
        data2 = '{ message: "Dis gon be a toast" }'
        SnackBar.add_data(self.request, data1)
        SnackBar.add_data(self.request, data2)

        snackbar = SnackBar.get(self.request)

        self.assertEqual(len(snackbar), 2, 'Unexpected message count')

        with self.assertRaises(KeyError):
            self.request.session[SnackBar.SESSION_KEY]


    def test_clear(self):
        data1 = '{ message: "Message Sent", actionHandler: function(event) {}, actionText: "Undo", timeout: 10000 }'
        SnackBar.add_data(self.request, data1)
        SnackBar.add_data(self.request, data1)
        SnackBar.add_data(self.request, data1)
        SnackBar.add_data(self.request, data1)
        SnackBar.clear(self.request)
        self.assertEqual(len(SnackBar.get(self.request)), 0)

    def test_generated_js(self):
        self.maxDiff = None
        expected_js_1 = ('var notification = '
            'document.querySelector(".mdl-js-snackbar");'
            'var data = {'
            'message: "Message Sent",'
            'actionHandler: function(event) {},'
            'actionText: "Undo",'
            'timeout: 10000'
            '};'
            'notification.MaterialSnackbar.showSnackbar(data);')

        expected_js_2 = expected_js_1 + (
            'var data = {'
            'message: "Dis gon be a toast"'
            '};'
            'notification.MaterialSnackbar.showSnackbar(data);')

        data1 = '{message: "Message Sent",actionHandler: function(event) {},actionText: "Undo",timeout: 10000}'
        data2 = '{message: "Dis gon be a toast"}'
        SnackBar.add_data(self.request, data1)
        
        snackbar = SnackBar.get(self.request)   
        self.assertEqual(snackbar.get_js(), expected_js_1)

        SnackBar.add_data(self.request, data1)
        SnackBar.add_data(self.request, data2)

        snackbar = SnackBar.get(self.request)
        self.assertEqual(snackbar.get_js(), expected_js_2)



