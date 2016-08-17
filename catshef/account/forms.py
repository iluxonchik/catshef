from django import forms
# from phonenumber_field.formfields import PhoneNumberField
from account.models import Profile

class SignUpForm(forms.ModelForm):
    """
    Custom sign up form, which creates and associates a Profile to the User.
    """
    class Meta:
        model = Profile
        fields = ['name', 'phone']

    def signup(self, request, user):
        user.profile = self.instance
