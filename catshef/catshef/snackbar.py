"""
Module containing helpers for working with Material Design Lite snackbars.
This is used to pass snackbar/toast messages to be displayed to the user.

For more info about snackbars go to: https://getmdl.io/components/index.html?#snackbar-section 
"""

from django.conf import settings

from catshef.exceptions import ArgumentError

class SnackBar(object):
    """
    Abstraction arround session that helps you with sending snackbar messages.
    Do NOT make instances of this class directly, use only the public 
    classmethods (the ones whose names do not begin with an '_').
    
    request.session[SnackBar.SESSION_KEY] stores a list of expected ata objects.

    For more info about snackbars go to: https://getmdl.io/components/index.html?#snackbar-section 
    """
    # Check out the unit tests in catshef/test_snackbar.py if you need examples
    # of usage and expected behaviour.

    def __init__(self, data=None):
        """
        Do NOT make instances of this class directly, use only the public 
        classmethods (the ones whose names do not begin with an '_').
        """
        if data:
            self.data = data if isinstance(data, list) or isinstance(data, tuple) else [data]
        else:
            raise ArgumentError('No data string provided')

    def __len__(self):
        if self.data:
            return len(self.data)
        return 0

    SESSION_KEY = getattr(settings, 'SNACKBAR_SESSION_KEY', 'catshef.snackbar')

    @classmethod
    def __is_initialized(cls, request):
        return SnackBar.SESSION_KEY in request.session

    @classmethod
    def __init_session_if_needed(cls, request):
        if not cls.__is_initialized(request):
            request.session[SnackBar.SESSION_KEY] = []

    @classmethod
    def __check_session_type(cls, request):
        """
        Make sure that the Session variable is either a list or a tuple
        """
        if not (isinstance(request.session[SnackBar.SESSION_KEY], list) or 
            isinstance(request.session[SnackBar.SESSION_KEY], tuple)):
            raise ValueError(('Value of session key {} is not a list '
            'or tuple').format(SnackBar.SESSION_KEY))

    @classmethod
    def clear(cls, request):
        if cls.__is_initialized(request):
            del request.session[SnackBar.SESSION_KEY]

    @classmethod
    def add_data(cls, request, data):
        """
        Add snackbar by providing the data object.
        """
        cls.__init_session_if_needed(request)
        cls.__check_session_type(request)

        request.session[SnackBar.SESSION_KEY].append(data)

    @classmethod
    def from_data(cls, request, data):
        return SnackBar(data=data)

    @classmethod
    def get(cls, request):
        """
        Get list of all SnackBars. This method also clears the list of snackbars 
        from session.
        """
        if not cls.__is_initialized(request):
            return []
        
        cls.__check_session_type(request)
        data_list = request.session[SnackBar.SESSION_KEY]
        cls.clear(request)
        return SnackBar.from_data(request, data=data_list)

    def get_js(self):
        """
        Get javascript for all of the snackbars stored in this intance.
        """
        js = ''
        if self.data:
            js = ('var notification = '
                'document.querySelector(".mdl-js-snackbar");')
            for d in self.data:
                js += ('var data = {};'
                'notification.MaterialSnackbar.showSnackbar(data);').format(d)
        return js
