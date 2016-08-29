from ..snackbar import SnackBar
from django.contrib import messages

class MessageToSnackBarMiddleware(object):
    """
    Gets all messages and creates SnackBars for them.
    """
    def process_request(self, request):
        # TODO: write some test + don't hardcode values
        storage = messages.get_messages(request)
        for message in storage:
            SnackBar.add_data(request, ('{ message: "' + message.message + '",' 
                'timeout: 5000 }'))
