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
        user.save()
        self.instance.save()

class ProfileEditForm(forms.ModelForm):
    """
    Form for editing a Profile instance.
    """
    # NOTE: for now this is a duplicate of SignUpForm, but later on
    # some ohter custumizations will be added.
    class Meta:
        model = Profile
        fields = ['name', 'phone']
