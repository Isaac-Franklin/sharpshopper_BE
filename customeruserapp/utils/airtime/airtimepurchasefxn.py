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
from datetime import datetime
import pytz
import uuid



def generate_request_id(username):
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)

    date_str = now.strftime("%Y%m%d%H%M")

    # Generate a random alphanumeric string (UUID short)
    random_str = uuid.uuid4().hex[:10]  # take first 10 chars

    # Concatenate
    request_id = f"{date_str}{username}{random_str}"
    return request_id

# #  

@swagger_auto_schema(
    method='post',
    request_body= AirtimeVTUTopUpSerializer,
        tags=['Data Purchase'],
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AirtimeVTUTopUpurchase(request):
    try:
        url = vpassUrls.mtnvtu_test
        serializer = AirtimeVTUTopUpSerializer(data = request.data)
        if serializer.is_valid():
            phoneNumber = serializer.validated_data['phoneNumber']
            amount = serializer.validated_data['amount']
            serviceID = serializer.validated_data['network']
                    
            headers = {
                'api-key': 'b22d359ce9640011d09f4f6794439f05',
                'secret-key': 'SK_6752c553bfbe0e720969d426fbc8970f379251eb76c',
                'public-key': 'PK_178a1e6a8652abf863183618dc1c04525a71e1c81cd',
                'Content-Type': 'application/json',
            }
            
            username = request.user.email.split('@')[0]
            requestID = generate_request_id(username)
            
            data = {
                'request_id': requestID,
                'serviceID': serviceID,
                'amount': amount,
                'phone': phoneNumber
            }
            
            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                CustomerSetupResponse = response.json()
                
                if "content" in CustomerSetupResponse:
                    saveRechargeAction = RegisterAirtimePurchases(user = request.user, numberToRecharge = phoneNumber,  customeRequestID = requestID,transactionID = CustomerSetupResponse["content"]["transactions"]["transactionId"], transactionStatus = CustomerSetupResponse.get('response_description'), network = serviceID)
                    saveRechargeAction.save()
                else:
                    print('DATA WAS NOT SAVED TO DB')
                    
                    
                if CustomerSetupResponse.get('code') == "000":
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message": "Process completed",
                        "data": CustomerSetupResponse
                    })
                else:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": CustomerSetupResponse.get('response_description', 'Unknown error')
                    })
            except Exception as e:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"An error occurred: {str(e)}"
                })    
                
        else: 
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": 'An error occured while processing the submitted details, kinldy confirm your details and try again'
            })

    except Exception as e:
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "message": "Kindly check your wifi or network connection and try again"},
            status=status.HTTP_502_BAD_GATEWAY
        )
#  
