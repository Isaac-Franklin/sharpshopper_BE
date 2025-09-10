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
from adminapp.models import ElectricityProviders
from customeruserapp.paystackViews import confirmBalanceIsEnough, decreaseAccountBalance
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


@swagger_auto_schema(
    method='post',
    request_body= VerifyMeterSerializer,
        tags=['Electricity'],
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def VerifyUserMeterNumber(request):
    try:
        url = vpassUrls.verify_mter_number_test
        serializer = VerifyMeterSerializer(data = request.data)
        if serializer.is_valid():
            billersCode = serializer.validated_data['billersCode']
            serviceID = serializer.validated_data['serviceID']
            type = serializer.validated_data['type']
            userMain = ShopperUsers.objects.get(user = request.user)
            userPhoneNumber = userMain.phoneNumber
                    
            headers = {
                'api-key': 'b22d359ce9640011d09f4f6794439f05',
                'secret-key': 'SK_6752c553bfbe0e720969d426fbc8970f379251eb76c',
                # 'public-key': 'PK_178a1e6a8652abf863183618dc1c04525a71e1c81cd'
                'Content-Type': 'application/json',
            }
            
            data = {
                'serviceID': serviceID,
                'billersCode': billersCode,
                'type': type
            }
            
            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                CustomerSetupResponse = response.json()
                print('CustomerSetupResponse')
                print(CustomerSetupResponse)
                        
                if "content" in CustomerSetupResponse:
                    print('content found')
                    
                    if CustomerSetupResponse.get('code') == "000":
                        if 'error' in CustomerSetupResponse.get('content'): 
                            print("CustomerSetupResponse.get('code') CLICKED")
                            return Response({
                                "status": status.HTTP_400_BAD_REQUEST,
                                "message": CustomerSetupResponse['content']['error'],
                            })
                        
                        # check id meter exists already
                        if UserMeterRecordsModel.objects.filter(billersCode_MeterNumber = billersCode).exists():
                            getMeter = UserMeterRecordsModel.objects.get(billersCode_MeterNumber = billersCode)
                            getMeter.delete()
                            
                        content = CustomerSetupResponse.get("content", {})
                        
                        fields = [
                            "Customer_Name", "Account_Number", "Address", "Minimum_Amount",
                            "Min_Purchase_Amount", "Customer_Arrears", "Customer_Account_Type",
                            "Can_Vend", "Meter_Type", "WrongBillersCode"
                        ]

                        data = {field: content.get(field) for field in fields if field in content}

                        UserMeterRecords = UserMeterRecordsModel(
                            user=request.user,
                            billersCode_MeterNumber=billersCode,
                            serviceID=serviceID,
                            meterType=type,
                            **data  # only passes fields that exist
                        )
                        UserMeterRecords.save()
                                                
                        return Response({
                            "status": status.HTTP_200_OK,
                            "message": 'Meter verification successfull',
                            'meterNumber': UserMeterRecords.billersCode_MeterNumber,
                            'address': UserMeterRecords.Address,
                            'userPhoneNumber': userPhoneNumber
                        })
                        
                    else:
                        return Response({
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": 'An error occured trying to verify your meter, kindly check your submission and try again',
                        })
                    
                else:
                    print("CustomerSetupResponse.get('code') NOT CLICKED")
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": CustomerSetupResponse.get('response_description', 'Unknown error')
                    })
                            
                        
                        # {'code': '000', 
                        # 'content': {'error': 'This meter is not correct or is not a valid Ikeja Electric prepaid meter. Please check and try again', 
                        # 'WrongBillersCode': True}
                        # }
                            
                            
                    # else:
                    #     print('DATA WAS NOT SAVED TO DB')
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


def generate_request_id(username):
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)
    date_str = now.strftime("%Y%m%d%H%M")
    random_str = uuid.uuid4().hex[:10]  
    # Concatenate
    request_id = f"{date_str}{username}{random_str}"
    return request_id

#

@swagger_auto_schema(
    method='post',
    request_body= PayMeterBillSerializer,
        tags=['Electricity'],
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PayElectricityBill(request):
    try:
        url = vpassUrls.meterpayment_test
        serializer = PayMeterBillSerializer(data = request.data)
        if serializer.is_valid():
            billersCode = int(serializer.validated_data['meterNumber'])
            serviceID = serializer.validated_data['powerSupplierID']
            variation_code = serializer.validated_data['meterType']
            amount = serializer.validated_data['amount']
            userMain = ShopperUsers.objects.get(user = request.user)
            phone = userMain.phoneNumber
            
            username = request.user.email.split('@')[0]
            request_id = generate_request_id(username)
            
            headers = {
                'api-key': 'b22d359ce9640011d09f4f6794439f05',
                'secret-key': 'SK_6752c553bfbe0e720969d426fbc8970f379251eb76c',
                # 'public-key': 'PK_178a1e6a8652abf863183618dc1c04525a71e1c81cd'
                'Content-Type': 'application/json',
            }
            
            data = {
                'serviceID': serviceID,
                'billersCode': billersCode,
                'request_id': request_id,
                'variation_code': variation_code,
                'amount': amount,
                'phone': phone,
            }
            
            print('data')
            print(data)
                
            # check account balance is enough for transaction
            checkAccountStatus = confirmBalanceIsEnough(request, amount)
            if checkAccountStatus == 'Success':
                pass
            else:
                return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        'message': 'Insufficient account balance to manage this transaction'
                    })
                    
            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                CustomerSetupResponse = response.json()
                print('CustomerSetupResponse')
                print(CustomerSetupResponse)
                
                if "content" in CustomerSetupResponse and 'transactions' in CustomerSetupResponse.get('content'):
                    
                    if CustomerSetupResponse['content']['transactions']['status'] != 'failed':
                        # find meter 
                        if UserMeterRecordsModel.objects.filter(billersCode_MeterNumber = billersCode).exists():
                            meter = UserMeterRecordsModel.objects.get(billersCode_MeterNumber = billersCode)
                        else:
                            meter = None
                            
                        if serviceID == 'ikeja-electric':
                            # ikeja-electric storage setup
                            if 'token' in CustomerSetupResponse:
                                # save electricity purchase details
                                raw_token = CustomerSetupResponse.get("purchased_code", "")
                                token_number = raw_token.split("Token :")[-1].strip()
                                elecricityPayment = ElectricityPurchaseRecordsModel(
                                    user = request.user,
                                    MeterRecords = meter, 
                                    meterType = variation_code, 
                                    product_name = CustomerSetupResponse["content"]["transactions"]["product_name"], 
                                    transactionId = CustomerSetupResponse["content"]["transactions"]["transactionId"], 
                                    requestId = CustomerSetupResponse["requestId"], 
                                    # purchasedToken = CustomerSetupResponse['purchased_code'], 
                                    purchasedToken=token_number,
                                    tokenAmount = CustomerSetupResponse["tokenAmount"], 
                                    amount = CustomerSetupResponse["amount"], 
                                    purchasedUnits = CustomerSetupResponse["units"], 
                                    announcement = CustomerSetupResponse["announcement"], 
                                    exchangeReference = CustomerSetupResponse["exchangeReference"],
                                )
                                elecricityPayment.save()
                                
                            elif 'token' not in CustomerSetupResponse:   
                                # save electricity purchase details
                                elecricityPayment = ElectricityPurchaseRecordsModel(
                                    user = request.user,
                                    MeterRecords = meter, 
                                    meterType = variation_code, 
                                    product_name = CustomerSetupResponse["content"]["transactions"]["product_name"], 
                                    transactionId = CustomerSetupResponse["content"]["transactions"]["transactionId"], 
                                    requestId = CustomerSetupResponse["requestId"], 
                                    customerAddress = CustomerSetupResponse["customerAddress"], 
                                    # utilityName = CustomerSetupResponse["utilityName"], 
                                    customerName = CustomerSetupResponse["customerName"], 
                                    amount = CustomerSetupResponse["amount"], 
                                    exchangeReference = CustomerSetupResponse["exchangeReference"],
                                )
                                elecricityPayment.save()
                                
                            else:
                                print('Data not save in DB for power purchase becaus token is missing in response for ikejelectric power supply')
                                
                        
                        elif serviceID == 'eko-electric':
                            
                            # eko-electric storage setup
                            if 'mainToken' in CustomerSetupResponse:
                                # save electricity purchase details
                                elecricityPayment = ElectricityPurchaseRecordsModel(
                                    user = request.user,
                                    MeterRecords = meter, 
                                    meterType = variation_code, 
                                    product_name = CustomerSetupResponse["content"]["transactions"]["product_name"], 
                                    transactionId = CustomerSetupResponse["content"]["transactions"]["transactionId"], 
                                    requestId = CustomerSetupResponse["requestId"], 
                                    purchasedToken = CustomerSetupResponse["mainToken"], 
                                    tokenAmount = CustomerSetupResponse["mainsTokenAmount"], 
                                    mainTokenTax = CustomerSetupResponse["mainTokenTax"], 
                                    amount = CustomerSetupResponse["amount"], 
                                    purchasedUnits = CustomerSetupResponse['content']['transactions']["unit_price"], 
                                    exchangeReference = CustomerSetupResponse["exchangeReference"],
                                )
                                elecricityPayment.save()
                                
                            elif 'mainToken' not in CustomerSetupResponse.get('content'):
                                # save electricity purchase details
                                elecricityPayment = ElectricityPurchaseRecordsModel(
                                    user = request.user,
                                    MeterRecords = meter, 
                                    meterType = variation_code, 
                                    product_name = CustomerSetupResponse["content"]["transactions"]["product_name"], 
                                    transactionId = CustomerSetupResponse["content"]["transactions"]["transactionId"], 
                                    requestId = CustomerSetupResponse["requestId"], 
                                    customerAddress = CustomerSetupResponse["customerAddress"], 
                                    customerName = CustomerSetupResponse["customerName"], 
                                    amount = CustomerSetupResponse["amount"], 
                                    exchangeReference = CustomerSetupResponse["exchangeReference"],
                                )
                                elecricityPayment.save()
                                
                            else:
                                print('Data not save in DB for power purchase becaus token is missing in response for eko-electric power supply')
                                
                                
                        elif serviceID == 'kano-electric':
                            
                            # eko-electric storage setup
                            if 'Token' in CustomerSetupResponse:
                                # save electricity purchase details
                                elecricityPayment = ElectricityPurchaseRecordsModel(
                                    user = request.user,
                                    MeterRecords = meter, 
                                    meterType = variation_code, 
                                    transactionId = CustomerSetupResponse["content"]["transactions"]["transactionId"], 
                                    product_name = CustomerSetupResponse["content"]["transactions"]["product_name"], 
                                    requestId = CustomerSetupResponse["requestId"], 
                                    purchasedToken = CustomerSetupResponse["Token"], 
                                    mainTokenTax = CustomerSetupResponse["Tax"], 
                                    amount = CustomerSetupResponse["amount"], 
                                    purchasedUnits = CustomerSetupResponse['Units'], 
                                )
                                elecricityPayment.save()
                                
                            elif 'Token' not in CustomerSetupResponse and variation_code == 'postpaid':
                                # save electricity purchase details
                                elecricityPayment = ElectricityPurchaseRecordsModel(
                                    user = request.user,
                                    MeterRecords = meter, 
                                    meterType = variation_code, 
                                    product_name = CustomerSetupResponse["content"]["transactions"]["product_name"], 
                                    transactionId = CustomerSetupResponse["content"]["transactions"]["transactionId"], 
                                    requestId = CustomerSetupResponse["requestId"], 
                                    customerAddress = CustomerSetupResponse["customerAddress"], 
                                    customerName = CustomerSetupResponse["customerName"], 
                                    amount = CustomerSetupResponse["amount"], 
                                    exchangeReference = CustomerSetupResponse["exchangeReference"],
                                )
                                elecricityPayment.save()
                                
                            else:
                                print('Data not save in DB for power purchase becaus token is missing in response for eko-electric power supply')
                                
                                
                    else:
                        print('DATA WAS NOT SAVED TO DB')
                    
                    
                if CustomerSetupResponse.get('code') == "000":
                            
                    # reduce amount from wallet
                    decreaseAccountBalance(request, amount)
                    
                    # save notification
                    NotificationActivity.objects.create(user = request.user, transactionEffect = 'Subtract', activityTtile = 'Electricity', deliveryStatus = 'Successfull', amountSpent = amount)
                    # 
                    
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message": "Process completed successfully",
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


@swagger_auto_schema(
    method='GET',
        tags=['Electricity'],
    )
@api_view(['GET'])
def AvailableElectricityDistributors(context):
    providers = ElectricityProviders.objects.values("id", "apiaccessname")
    return Response({
        "status": status.HTTP_200_OK,
        "message": "Electricity Providers fetched successfully",
        "data": list(providers)
    })





