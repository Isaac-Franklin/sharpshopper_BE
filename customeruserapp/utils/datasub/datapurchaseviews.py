import csv
import json
import socket
import concurrent.futures
from smtplib import SMTPException
import requests
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
from onboardingapp.serializers import *
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login, logout, authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, schema
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.hashers import make_password, check_password
from datetime import date, timedelta
from django.utils.crypto import get_random_string
from customeruserapp.models import *
from customeruserapp.serializers import *
from customeruserapp.utils.vpassurls import vpassUrls

# Get MTN DATA Variation Codes
@swagger_auto_schema(
    method='get',
        tags=['datapurchase'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def MTNDataVariationCodes(request):
    try:
        url = vpassUrls.mtndata
        
        headers = {
            # 'Authorization': f'Bearer {paystackSecretKey}',
            'Content-Type': 'application/json',
            'api-key': 'b22d359ce9640011d09f4f6794439f05',
            'public-key': 'PK_328ff3db4d44f00e56230c35ea56fd18a13c50f92e4'
        }
        
        # response = requests.post(url, json=data, headers=headers)
        response = requests.get(url, headers=headers)
        CustomerSetupResponse = response.json()
        print('CustomerSetupResponse')
        print(CustomerSetupResponse)
        if CustomerSetupResponse['status'] == True:
                pass
                # RegisterPaystackCustomers.objects.create(
                #     StudentID = student_admin_id,
                #     # StudentEmailAddress = CustomerSetupResponse['data']['email'],
                #     customerCode = CustomerSetupResponse['data']['customer_code'],
                #     integration = CustomerSetupResponse['data']['integration'],
                # )
                # return Response({
                #         "status":status.HTTP_200_OK,
                #         "message": "Process completed",
                #         "data": response.json(),
                #     })
    except:
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'An error occured'
        })
        
        
#  
        
# Get AIRTEL DATA Variation Codes
# @swagger_auto_schema(
#     method='get',
#         tags=['datapurchase'],
#     )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def AirtelDataSubScription(request):
#     try:
#         shopperID = ShopperUsers.objects.get(emailAddress = request.user.email).id
#         getRequestingUser = ShopperUsers.objects.get(emailAddress = request.user.email)
#         user_EmailAddress = getRequestingUser.student_email
#         user_FirstName = getRequestingUser.student_firstname
#         user_LastName = getRequestingUser.student_lastname
#         user_phone = getRequestingUser.student_phone
        
#         url = vpassUrls.mtndata
        
#         headers = {
#             # 'Authorization': f'Bearer {paystackSecretKey}',
#             'Content-Type': 'application/json',
#             'api-key': 'b22d359ce9640011d09f4f6794439f05',
#             'public-key': 'PK_328ff3db4d44f00e56230c35ea56fd18a13c50f92e4'
#         }
        
#         # data={ 
#         #     "email": user_EmailAddress,
#         #     "first_name": user_FirstName,
#         #     "last_name": user_LastName,
#         #     "phone": user_phone,
#         # }
        
#         # response = requests.post(url, json=data, headers=headers)
#         response = requests.post(url, headers=headers)
#         CustomerSetupResponse = response.json()
#         if CustomerSetupResponse['status'] == True:
#                 pass
#                 # RegisterPaystackCustomers.objects.create(
#                 #     StudentID = student_admin_id,
#                 #     # StudentEmailAddress = CustomerSetupResponse['data']['email'],
#                 #     customerCode = CustomerSetupResponse['data']['customer_code'],
#                 #     integration = CustomerSetupResponse['data']['integration'],
#                 # )
#                 # return Response({
#                 #         "status":status.HTTP_200_OK,
#                 #         "message": "Process completed",
#                 #         "data": response.json(),
#                 #     })
#     except:
#         return Response({
#             'status': status.HTTP_400_BAD_REQUEST,
#             'message': 'An error occured'
#         })
        
        
# #  
        
        
# 
