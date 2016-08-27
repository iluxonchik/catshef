from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from account.models import Profile
from account.forms import ProfileEditForm

@login_required
def profile(request):
    return HttpResponse('')

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile successfully updated')
            return redirect(reverse('profile'))
    else:
        profile_form = ProfileEditForm(instance=profile)
    return render(request, 'account/profile/edit_profile.html', 
        {'profile_form': profile_form})


