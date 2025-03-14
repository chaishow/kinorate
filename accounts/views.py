from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .constants import errors, labels, requirements


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if (
            not username
            or not password
        ):
            messages.error(request, errors.EMPTY_FIELDS)

        user = authenticate(username=username,
                            password=password)

        if not user:
            messages.error(request, errors.WRONG_DATA)

        if messages.get_messages(request):
            return redirect('accounts:login')

        login(request, user)
        return redirect('collection:search_view')

    return render(request, 'accounts/login_form.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if (
            not username
            or not email
            or not password
        ):
            messages.error(request, errors.EMPTY_FIELDS)

        if (
            User.objects.filter(email=email).exists()
            or User.objects.filter(username=username).exists()
        ):
            messages.error(request, errors.ALREADY_EXISTS)

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)

        if messages.get_messages(request):
            return redirect('accounts:register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
            )
        login(request, user)

        return redirect('collection:search_view')

    return render(request, 'accounts/register_form.html', {
                  'requirements': requirements.PASSWORD_REQUIREMENTS,
                  'labels': labels.FORM_LABELS,
                  }
                  )


def logout_view(request):
    logout(request)
    return redirect('accounts:login')