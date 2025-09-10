import uuid
import pytz
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from customeruserapp.paystackViews import confirmBalanceIsEnough, decreaseAccountBalance
from customeruserapp.utils.bilasAuth import getBilasToken
from customeruserapp.utils.datasub.dataPurchaseFxn import PurchaseData
from customeruserapp.utils.vpassurls import CableTCSubscriptionAlgo, vpassUrls
from onboardingapp.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, schema
from customeruserapp.models import *
from customeruserapp.serializers import *
from django.utils import timezone



@swagger_auto_schema(
    method='get',
    query_serializer=TVStationServiceProviderID,
    tags=['Cable TV'],
    )
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def GetAvailableTVPlans(request):
    print(request.query_params)
    serializer = TVStationServiceProviderID(data=request.query_params)
    if serializer.is_valid():
        stationProvider = serializer.validated_data['stationProvider']
        try:
            cable_algo = CableTCSubscriptionAlgo(stationProvider)
            url = cable_algo.checkdstvplans_test
            response = requests.get(url)
            response.raise_for_status()
            CustomerSetupResponse = response.json()
            # print('data')
            if 'variations' in CustomerSetupResponse['content']:
                data = CustomerSetupResponse['content']['variations']
                
                return Response({
                    "status": status.HTTP_200_OK,
                    "message": "DSTV plans found",
                    "data": data
                })
            else:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": CustomerSetupResponse['content']['errors'],
                })
                
        except Exception as e:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "Kindly check your wifi or network connection and try again"},
            )
    else:
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "An error occured with the request, kindly refresh",
        })
        
#  


# Verify Smartcard Number
@swagger_auto_schema(
    method='POST',
    request_body=VerifySmartCarderializer,
    tags=['Cable TV'],
    )
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def VerifyCableSmartNumber(request):
    # try:
    print('request.data')
    print(request.data)
    serializer = VerifySmartCarderializer(data = request.data)
    if serializer.is_valid():
        smartCardNumber = serializer.validated_data['smartCardNumber']
        cabletvProvider = serializer.validated_data['cabletvProvider']
                
        headers = {
            'api-key': 'b22d359ce9640011d09f4f6794439f05',
            'secret-key': 'SK_6752c553bfbe0e720969d426fbc8970f379251eb76c',
            'public-key': 'PK_178a1e6a8652abf863183618dc1c04525a71e1c81cd',
            'Content-Type': 'application/json',
        }
        
        data = {
            'serviceID': cabletvProvider,
            'billersCode': smartCardNumber
        }
        
        print('data')
        print(data)
        
        try:
            cable_algo = CableTCSubscriptionAlgo(cabletvProvider)
            url = cable_algo.verifysmartcardnumber_test
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            CustomerSetupResponse = response.json()
            print('CustomerSetupResponse')
            print(CustomerSetupResponse)
            # print(CustomerSetupResponse['content']['Customer_Name'])
                
            if CustomerSetupResponse.get('code') == "000":
                    
                if 'error' in CustomerSetupResponse['content']:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST ,
                        "message": CustomerSetupResponse['content']['error'],
                    })
                        
                        
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

    # except Exception as e:
    #     return Response(
    #         {"status": status.HTTP_400_BAD_REQUEST, "message": "Kindly check your wifi or network connection and try again"},
    #         status=status.HTTP_502_BAD_GATEWAY
    #     )
        
        
# 



def generate_request_id(username):
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)

    date_str = now.strftime("%Y%m%d%H%M")

    # Generate a random alphanumeric string (UUID short)
    random_str = uuid.uuid4().hex[:10]  # take first 10 chars

    # Concatenate
    request_id = f"{date_str}{username}{random_str}"
    return request_id

# Verify Smartcard Number
@swagger_auto_schema(
    method='POST',
    request_body=RenewCableTVServiceSerializer,
    tags=['Cable TV'],
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def RenewCableTVService(request):
    try:
        print('request.data')
        print(request.data)
        serializer = RenewCableTVServiceSerializer(data = request.data)
        if serializer.is_valid():
            smartCardNumber = serializer.validated_data['smartCardNumber']
            cabletvProvider = serializer.validated_data['cabletvProvider']
            amount = serializer.validated_data['amount']
            phone = ShopperUsers.objects.get(user = request.user)
            phoneNumber = phone.phoneNumber
            
            username = request.user.email.split('@')[0]
            requestID = generate_request_id(username)
                    
            headers = {
                'api-key': 'b22d359ce9640011d09f4f6794439f05',
                'secret-key': 'SK_6752c553bfbe0e720969d426fbc8970f379251eb76c',
                'public-key': 'PK_178a1e6a8652abf863183618dc1c04525a71e1c81cd',
                'Content-Type': 'application/json',
            }
            
            data = {
                'serviceID': cabletvProvider,
                'billersCode': smartCardNumber,
                'amount': amount,
                'request_id': requestID,
                'phone': phoneNumber,
                'subscription_type': 'renew',
            }
                
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
                cable_algo = CableTCSubscriptionAlgo(cabletvProvider)
                url = cable_algo.verifysmartcardnumber_test
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                CustomerSetupResponse = response.json()
                print(CustomerSetupResponse)
                    
                if CustomerSetupResponse.get('code') == "000":
                    
                    if 'error' in CustomerSetupResponse['content']:
                        return Response({
                            "status": status.HTTP_400_BAD_REQUEST ,
                            "message": CustomerSetupResponse['content']['error'],
                        })
                        
                    else:
                        print('CustomerSetupResponse sas')
                        # save model
                        customerName = CustomerSetupResponse['content']['Customer_Name']
                        cabletvsave = SaveCableTVPurchases(user = request.user, smartcardTVorIUCNumber = smartCardNumber, product_name = cabletvProvider, customerName= customerName, requestId = requestID, amount = amount)
                        cabletvsave.save()
                        
                        # reduce amount from wallet
                        decreaseAccountBalance(request, amount)
                        
                        # save notification
                        NotificationActivity.objects.create(user = request.user, transactionEffect = 'Subtract', activityTtile = 'Cable', deliveryStatus = 'Successfull', amountSpent = amount)
                        
                        # 
                        return Response({
                            "status": status.HTTP_200_OK,
                            "message": "Process completedr",
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



