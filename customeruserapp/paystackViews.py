import csv
import json
import socket
import traceback
from smtplib import SMTPException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
import requests
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from customeruserapp.generateshoppingcode import generate_unique_code
from customeruserapp.utils.bilasAuth import getBilasToken
from customeruserapp.utils.datasub.dataPurchaseFxn import PurchaseData
# from customeruserapp.utils.generateshoppingcode import generate_unique_code
from onboardingapp.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, schema
from customeruserapp.models import *
from customeruserapp.serializers import *
import ast
from django.utils import timezone
paystacSecretKey = 'sk_test_033a8913522a481065f75295a0641ba958dd54e2'


@swagger_auto_schema(
    method='POST',
    request_body=UserDepositSerializer,
    tags=['customerApp'],
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UserFundAccount(request):
    print('UserFundAccount CALLED')
    try:
        serializer = UserDepositSerializer(data = request.data)
        if serializer.is_valid():
            amount = serializer.data['amount']
            # plan = serializer.data['plan']
            # numberofdevices = serializer.data['numberofdevices']
            email = request.user.email
            
            
        url="https://api.paystack.co/transaction/initialize"
                
        headers = {
            'Authorization': f'Bearer {paystacSecretKey}',
            'Content-Type': 'application/json'
        }
        
        # amountMain = f'{amount}'
        
        data = { "email": email, 
                "amount": int(amount) * 100 
                }

        response = requests.post(url, json=data, headers=headers)
        data = response.json()
        
        res_data = response.json()
        getUserModel = User.objects.get(email = email)
        auth_url = res_data['data']['authorization_url']
        accesscode = res_data['data']['access_code']
        reference = res_data['data']['reference']
        # save prospect to db
        saveUser = PotentialDeposites(user = getUserModel, amount = amount, accesscode = accesscode, reference = reference, auth_url = auth_url)
        saveUser.save()

        return Response({
                "status": status.HTTP_200_OK,
                'message': 'Deposit request created successfully',
                'reference': reference,
                'accesscode': accesscode,
                "data": response.json(),
            })
        
        
    except Exception as e:
        print(traceback.format_exc())
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "An error occurred.",
            "details": str(e)
        })



@swagger_auto_schema(
    method='POST',
    request_body=UserDepositSerializer,
    tags=['customerApp'],
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def VerifyUserFundsDeposit(request, accesscode):
    if (PotentialDeposites.objects.filter(accesscode = accesscode).exists()):
        fetchReferencedDeposit = PotentialDeposites.objects.filter(accesscode = accesscode).first()
        referenceCode = fetchReferencedDeposit.reference
        try:
            url= f'https://api.paystack.co/transaction/verify/{referenceCode}'
                    
            headers = {
                'Authorization': f'Bearer {paystacSecretKey}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            data = response.json()
            reqstatus = data["status"]
            message = data["message"]
            
            if (reqstatus == True):
                amountToDeposite = data['data']['amount'] / 100
                formattedamountToDeposite = "{:g}".format(amountToDeposite)
                print(formattedamountToDeposite)
                
                # update account balance
                if UserAccountBalanceTracker.objects.filter(emailAddress = request.user.email).exists():
                    IncreaseAccountBalance(request, formattedamountToDeposite)
                    
                else:
                    UserAccountBalanceTrackerModel = UserAccountBalanceTracker(user = request.user, emailAddress = request.user.email, AccountBalance = formattedamountToDeposite)
                    UserAccountBalanceTrackerModel.save()
                
                # save to success db
                if PotentialDeposites.objects.filter(reference = referenceCode).exists():
                    getSubscriptionModel = PotentialDeposites.objects.filter(reference = referenceCode).first()
                    getSubscriptionModelEmail = request.user.email
                    # 
                    getUserModel = User.objects.get(email = getSubscriptionModelEmail)
                    # 
                    saveSuccessTransaction = SuccessfullDeposites(user = getUserModel, accesscode = accesscode, PotentialDeposites = getSubscriptionModel)
                    saveSuccessTransaction.save()
                    
                    return Response({
                            "status": status.HTTP_200_OK,
                            'message': message,
                            "data": response.json(),
                        })
                    
                else:
                    return Response({
                            "status": status.HTTP_400_BAD_REQUEST,
                            'message': 'There was a problem with you deposit, our support is currently rectifying this',

                    })

            else:
                return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        'message': message,
                        "data": response.json(),
                    })
                
        except Exception as e:
            print(traceback.format_exc())
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "An error occurred.",
                "details": str(e)
            })
    else:
        return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                'message': 'There was a problem with you deposit, our support is currently rectifying this',

        })



@swagger_auto_schema(
    method='GET',
    tags=['customerApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchUserAccountBalance(request):
    userEmail = request.user.email
    if UserAccountBalanceTracker.objects.filter(emailAddress = userEmail).exists():
        getUserBalance = UserAccountBalanceTracker.objects.get(emailAddress = userEmail).AccountBalance
        
        return Response({
                "status": status.HTTP_200_OK,
                'message': 'Account balance found successfully',
                'balance': getUserBalance
            })
        
    else:
        return Response({
                "status": status.HTTP_200_OK,
                'message': 'System is currently loading to display current account details.',
                'balance': 0.00
            })
        


def IncreaseAccountBalance(request, amount):
    userEmail = request.user.email
    amountToAdd = int(amount)
    if UserAccountBalanceTracker.objects.filter(emailAddress = userEmail).exists():
        getUserBalance = UserAccountBalanceTracker.objects.get(emailAddress = userEmail).AccountBalance
        updatedBalance = int((getUserBalance) + amountToAdd)
        
        # delete existing account balance model
        UserAccountBalanceTracker.objects.all().delete()
        
        # update and save updated account balance model
        UserAccountBalanceTrackerModel = UserAccountBalanceTracker(user = request.user, emailAddress = request.user.email, AccountBalance = updatedBalance)
        UserAccountBalanceTrackerModel.save()
        
        return 'Success'
        
    else:
        return 'Failed'
        
    


def decreaseAccountBalance(request, amount):
    userEmail = request.user.email
    amountToAdd = int(amount)
    if UserAccountBalanceTracker.objects.filter(emailAddress = userEmail).exists():
        getUserBalance = UserAccountBalanceTracker.objects.get(emailAddress = userEmail).AccountBalance
        print('getUserBalance')
        print(getUserBalance)
        print(amountToAdd)
        print(int((getUserBalance) - amountToAdd))
        updatedBalance = int((getUserBalance) - amountToAdd)
        
        # delete existing account balance model
        UserAccountBalanceTracker.objects.all().delete()
        
        # update and save updated account balance model
        UserAccountBalanceTrackerModel = UserAccountBalanceTracker(user = request.user, emailAddress = request.user.email, AccountBalance = updatedBalance)
        UserAccountBalanceTrackerModel.save()
        
        return 'Success'
        
    else:
        return 'Failed'
        
    



