from enum import Enum
from typing import OrderedDict
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopperUsers
        fields = ['fullname', 'emailAddress', 'phoneNumber', 'referrerCode', 'password']




class ErrandUserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrandUsers
        fields = ['fullname', 'emailAddress', 'phonenumber', 'password']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


