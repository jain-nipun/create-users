from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . import forms
from . import serializers
from . import models
import json


@require_http_methods(['GET'])
def home_view(request):
    # View for Home page. Simply render the Home template.
    return render(request, 'UserAuthentication/home.html')


@require_http_methods(['GET', 'POST'])
def signup_view(request):
    # If the User is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard:dashboard_page'))

    # GET request, render the page
    if request.method == 'GET':
        return render(request, 'UserAuthentication/signup.html')

    # POST request, checks for errors and sign up
    else:
        signup_form = forms.SignupForm(request.POST)
        if signup_form.is_valid():
            signup_form.save()
            messages.add_message(request, messages.SUCCESS, 'Success! Log in to continue...')
            return HttpResponseRedirect(reverse('dashboard:signin_page'))

        else:
            errors = signup_form.errors.as_text()
            if 'username' in errors:
                errors = errors.replace('username', 'mobile')
            messages.add_message(request, messages.ERROR, errors)
            return HttpResponseRedirect(reverse('dashboard:signup_page'))


@require_http_methods(['GET', 'POST'])
def signin_view(request):
    # If the User is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard:dashboard_page'))

    if request.method == 'GET':
        return render(request, 'UserAuthentication/signin.html')

    else:
        signin_form = AuthenticationForm(request=request, data=request.POST)
        if signin_form.is_valid():
            django_login(request, signin_form.get_user())
            return HttpResponseRedirect(reverse('dashboard:dashboard_page'))

        else:
            errors = signin_form.errors.as_text()
            if 'username' in errors:
                errors = errors.replace('username', 'mobile')
            errors = errors.split('*')[2]
            messages.add_message(request, messages.ERROR, errors)
            return HttpResponseRedirect(reverse('dashboard:signin_page'))


@require_http_methods(['GET', ])
@login_required
def dashboard_view(request):
    return render(request, 'UserAuthentication/dashboard.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_notes_api(request):
    add_notes_serializer = serializers.AddNotesSerializer(data=request.data)
    add_notes_serializer.is_valid(raise_exception=True)
    add_notes_serializer.save(owner=request.user)
    return Response(data={'success': True, 'data': add_notes_serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_notes_api(request):
    my_notes_queryset = models.NoteModel.objects.filter(owner=request.user)
    my_notes_serializer = serializers.MyNotesSerializer(my_notes_queryset, many=True)
    return Response(data={'success': True, 'data': my_notes_serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_notes_api(request, id):
    can_edit = False
    try:
        note = models.NoteModel.objects.get(id=id, owner=request.user)
        can_edit = True
    except Exception:
        try:
            note = models.NoteModel.objects.get(id=id, shared=True, shared_users__user__id=request.user.id)
            can_edit = True
        except Exception:
            pass

    if can_edit:
        note.title = request.data['title']
        note.UserAuthentication = request.data['UserAuthentication']
        note.save()
        shared_users_read = request.data.getlist('shared_users_read[]')
        shared_users_write = request.data.getlist('shared_users_write[]')
        shared_users_read = list(set(shared_users_read) - set(shared_users_write))
        shared_users_write = request.data.getlist('shared_users_write[]')
        if shared_users_read or shared_users_write:
            note.shared = True
            for id in shared_users_read:
                id = int(id)
                u, _ = models.SharingModel.objects.get_or_create(user_id=id, read=True)
                note.shared_users.add(u)
            for id in shared_users_write:
                id = int(id)
                u, _ = models.SharingModel.objects.get_or_create(user_id=id, write=True)
                note.shared_users.add(u)
            note.save()
        return Response(data={'success': True}, status=status.HTTP_200_OK)
    else:
        return Response(data={'success': False, 'message': 'ACCESS_DENIED'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delete_notes_api(request, id):
    try:
        _ = models.NoteModel.objects.get(id=id, owner=request.user).delete()
        return Response(data={'success': True}, status=status.HTTP_200_OK)
    except Exception:
        Response(data={'success': False, 'message': 'ACCESS_DENIED'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_api(request):
    users_queryset = User.objects.all().exclude(id=request.user.id)
    users_serializer = serializers.UserSerializer(users_queryset, many=True)
    return Response(data={'success': True, 'data': users_serializer.data}, status=status.HTTP_200_OK)
    return Response(data={'success': True, 'data': users_serializer.data}, status=status.HTTP_200_OK)
