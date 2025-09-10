import csv
import json
import socket
import concurrent.futures
from smtplib import SMTPException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os
import base64
from django.db.models import Q
from rest_framework import status
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from adminapp.serializer import *
from customeruserapp.utils.bilasAuth import getBilasToken
from customeruserapp.utils.datasub.dataPurchaseFxn import PurchaseData
# from customeruserapp.utils.generateshoppingcode import generate_unique_code
from onboardingapp.serializers import *
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login, logout, authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, schema
from drf_yasg import openapi
from django.contrib.auth.hashers import make_password, check_password
from datetime import date, timedelta
import datetime
from django.utils.crypto import get_random_string
from customeruserapp.models import *
from customeruserapp.serializers import *
import ast


# Create your views here.
@swagger_auto_schema(
    method='post',
        request_body= CreateDataPlansSerializer,
        tags=['adminApp'],
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def CreateDataPlan(request):
    serializer = CreateDataPlansSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        
    return Response({
            "status": status.HTTP_200_OK,
            # 'token': data.get("token"),
            'message': 'Request completed successfully'
        })




@swagger_auto_schema(
    method='post',
        request_body= AdminLoginSerializer,
        tags=['adminApp'],
    )
@api_view(['POST'])
def AdminLogin(request):
    serializer = AdminLoginSerializer(data = request.data)
    print(request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        print('email')
        print(email)
        print(password)
        
        data = {
            email: email,
        }
        
        return Response({
                "status": status.HTTP_200_OK,
                'user': data,
                # 'token': data.get("token"),
                'message': 'Request completed successfully'
            })
    else: 
        return Response({
                "status": status.HTTP_404_NOT_FOUND,
                # 'token': data.get("token"),
                'message': 'An error occured'
            })


