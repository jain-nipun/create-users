from django.contrib.auth.models import User
from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class AddNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NoteModel
        fields = ['title', 'UserAuthentication']


class SharingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.SharingModel
        fields = '__all__'


class MyNotesSerializer(serializers.ModelSerializer):
    sharing = SharingSerializer(many=True)

    class Meta:
        model = models.NoteModel
        fields = '__all__'
