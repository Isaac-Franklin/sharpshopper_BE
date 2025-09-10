from enum import Enum
from typing import OrderedDict
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers
from customeruserapp.models import ProductCategories


class CreateDataPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPlans
        fields = ['network', 'productName', 'dataPlanType', 'dataCost', 'dataValidity']



class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()



# class UpdateErrandUserAssignmentSerializer(serializers.Serializer):
#     errandUserID = serializers.IntegerField()


