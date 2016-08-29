from catshef.snackbar import SnackBar

from importlib import import_module

from django.contrib import messages
from django.test import TestCase, override_settings
from django.http import HttpRequest, HttpResponse
from django.conf import settings

from catshef.middleware.mtosmiddleware import MessageToSnackBarMiddleware

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages.middleware import MessageMiddleware


class MessageToSnackBarMiddlewareTestCase(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        self.request.session = engine.SessionStore(session_key)
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        self.middleware = MessageToSnackBarMiddleware()
        self.msg_middleware = MessageMiddleware()

    def test_message_converted_to_snackbar(self):
        messages.add_message(self.request, messages.INFO, '{ message: "hello" }')

        self.assertEquals(len(SnackBar.get(self.request)), 0)

        storage = messages.get_messages(self.request)
        self.assertEquals(len(storage), 1)

        self.middleware.process_request(self.request)
        self.assertEquals(len(SnackBar.get(self.request)), 1)
        
        self.msg_middleware.process_request(self.request)

        storage = messages.get_messages(self.request)

        self.assertEquals(len(storage), 0)
