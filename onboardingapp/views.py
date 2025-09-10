import csv
import json
import socket
import concurrent.futures
from smtplib import SMTPException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os
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



# Create your views here.
@swagger_auto_schema(
    method='post',
        request_body= LoginSerializer,
        tags=['onBoarding'],
        
        # openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     required=['email', 'password'],
        #     properties={
        #         'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@example.com'),
        #         'password': openapi.Schema(type=openapi.TYPE_STRING, example='strongpassword123'),
        #     },
        # ),
        responses={
            200: openapi.Response(
                description="User registered",
                examples={
                    "application/json": {
                        "message": "Login successful",
                        "Token": "jwt_token",
                        "data": {"name": "name"}
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "Email already exists"
                    }
                }
            )
        }
    )
@api_view(['POST'])
def UserLogin(request):
    # try:
    serializer = LoginSerializer(data = request.data)
    print(request.data)
    # check entry validation
    if serializer.is_valid():
        useremail = serializer.data['username']
        password = serializer.data['password']
        # check if email exist in db
        print(useremail)            
        
        if ShopperUsers.objects.filter(emailAddress = useremail).exists():
            print('user is Shopper')
            getShopper = ShopperUsers.objects.get(emailAddress = useremail)
            getShopperPassword = getShopper.password
            if not check_password(password, getShopperPassword):
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'message': 'Password is incorrect',
                    "errors": {
                        "password": "This password is not correct",
                    },
                })
            
            # check email in user model
            # check username availability
            CheckUserUsername = User.objects.get(email = useremail).username
            userAuth = authenticate(request, username = CheckUserUsername, password = password)
            
            if CheckUserUsername is None:
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'message': 'This user does not exit',
                    "errors": {
                        "email": "This user does not exit",
                    },
                })
                
            if userAuth is not None:
            
                # ✅ Get the user
                try:
                    user = User.objects.get(email=useremail)
                except User.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "User does not exist"
                    })

                # ✅ Generate JWT tokens
                token_serializer = CustomTokenObtainPairSerializer(data=request.data)
                print(request.data)
                token_serializer.is_valid(raise_exception=True)
                Token = token_serializer.validated_data
                print('Shopper LOGIN TRIGGERED')
                shopperModel = ShopperUsers.objects.get(emailAddress = useremail)
                name = shopperModel.fullname
                email = shopperModel.emailAddress
                phone = shopperModel.phoneNumber
                referralCode = shopperModel.referalCode
                print('tokens')
                print(Token)
                
                userData = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "referralCode": referralCode,
                }
                
                return Response({
                "status": status.HTTP_200_OK,
                "message": "Shopper User Login was Successful.",
                "token": Token,
                "data": userData,
                "userType": "shopper"
                })
                
            # 
                
            else:
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    "errors": {
                        "password": "Incorrect password",
                    },
                })
                
        
        # LOGIN AS ERRAND USERS
        elif ErrandUsers.objects.filter(emailAddress = useremail).exists():
            print(' user is an errand person')
            CheckUser = User.objects.get(email = useremail)
            CheckUserUsername = CheckUser.username
            userAuth = authenticate(request, username = CheckUserUsername, password = password)
            
            if CheckUserUsername is None:
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'message': 'This user does not exit',
                    "errors": {
                        "email": "This user does not exit",
                    },
                })                    
                
            if userAuth is not None:
                # redirect to code verification process

                # ✅ Generate JWT tokens
                token_serializer = CustomTokenObtainPairSerializer(data=request.data)
                print(request.data)
                token_serializer.is_valid(raise_exception=True)
                Token = token_serializer.validated_data
                print('Shopper LOGIN TRIGGERED')
                errandUsers = ErrandUsers.objects.get(emailAddress = useremail)
                name = errandUsers.fullname
                email = errandUsers.emailAddress
                phone = errandUsers.phonenumber
                print('tokens')
                print(Token)
                
                userData = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                }
                
                return Response({
                "status": status.HTTP_200_OK,
                "message": "Errand User Login was Successful.",
                "token": Token,
                "data": userData,
                "userType": "erranduser"
                })
                
            else:
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    "errors": {
                        "password": "Incorrect password",
                    },
                })
                
        else:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": "Email address does not exit",
                },
            })
    else: 
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'error': 'Your entry is invalid, kindly review and try again',
        })
        
    # except:
    #     return Response({
    #         'status':status.HTTP_400_BAD_REQUEST,
    #         "error" : "An error occured, kindly try again"
    #         })


@swagger_auto_schema(
    method='post',
        request_body= SignUpSerializer,
        tags=['onBoarding'],
        
        # openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     required=['email', 'password'],
        #     properties={
        #         'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@example.com'),
        #         'password': openapi.Schema(type=openapi.TYPE_STRING, example='strongpassword123'),
        #     },
        # ),
        responses={
            200: openapi.Response(
                description="User registered",
                examples={
                    "application/json": {
                        "message": "Login successful",
                        "Token": "jwt_token",
                        "data": {"name": "name"}
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "Email already exists"
                    }
                }
            )
        }
    )
@csrf_exempt
@api_view(['POST'])
def UserRegistration(request):
    print('UserSignUp CALLED')
    serializer = SignUpSerializer(data = request.data)
    print('request.data')
    print(request.data)
    if serializer.is_valid():
        fullname = serializer.data['fullname']
        useremailaddress = serializer.data['emailAddress']
        phone = serializer.data['phoneNumber']
        password = serializer.data['password']
        referrerCode = serializer.data['referrerCode']
        
        # generate referral code for user
        uniqueCode = get_random_string(length=14)
        userUniqueName =( serializer.data['emailAddress']).split('@')[0]
        generatedUserReferralCode = userUniqueName +"_"+uniqueCode
        
        if not serializer.data['fullname']:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'error': 'Kindly enter a full name',
            })

        if not serializer.data['emailAddress']:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": "Kindly enter an email address",
                },
            })
        
        if not serializer.data['phoneNumber']:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "phone": "Kindly enter a phone number",
                },
            })

        data = ShopperUsers.objects.filter(emailAddress = useremailaddress)
        if data:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": "A user already exist with this email.",
                },
            })
        
        UserDataCheckEmail = User.objects.filter(email=useremailaddress)
        if UserDataCheckEmail:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": "A user already exist with this email.",
                },
            })
        
        checkPhoneNumber = ShopperUsers.objects.filter(phoneNumber=phone)
        if checkPhoneNumber:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "phone": "A user already exist with this phone number.",
                },
            })

        else:
            userprofile = User.objects.create_user(username=useremailaddress, email=useremailaddress, password=password, first_name=fullname, last_name=phone)
            userprofile.save()
            
            
            cryptpassword = make_password(password)
            form = ShopperUsers(user = userprofile, fullname=fullname, emailAddress = useremailaddress, phoneNumber=phone, password=cryptpassword, referalCode = generatedUserReferralCode, referrerCode = referrerCode)
            form.save()
            
            # send activation email to user 
            # try:
            #     activateEmail(companyname, useremailaddress, generatedCompanyUniqueID)
            # except:
            #     print('Registration mail was not sent successfully')
            
            getUserusername = useremailaddress
            getUserPassword = password
                    
            tokenCreationData = {
                'username': getUserusername,
                'password': getUserPassword
            }
            
            CheckUserUsername = User.objects.get(email = useremailaddress).username
            
            token_serializer = CustomTokenObtainPairSerializer(data=tokenCreationData)
            token_serializer.is_valid(raise_exception=True)
            Token = token_serializer.validated_data
                    
            # 

            try:
                authenticate(request, username = CheckUserUsername, password = password)
                print('User auth worked fine')
                # fetch user data for response
                userModel = ShopperUsers.objects.get(emailAddress = useremailaddress)
                name = userModel.fullname
                email = userModel.emailAddress
                phone = userModel.phoneNumber
                    
                userData = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                }
                
                return Response({
                "status": status.HTTP_200_OK,
                "message": "Shopper User created was Successful.",
                "token": Token,
                "data": userData
            })
            
            except:
                print('There was a problem authenticating this user, kindly confirm your details and try again.')
        
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'error': serializer.errors,
        })


@swagger_auto_schema(
    method='post',
        request_body= ErrandUserSignUpSerializer,
        tags=['onBoarding'],
        
        # openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     required=['email', 'password'],
        #     properties={
        #         'email': openapi.Schema(type=openapi.TYPE_STRING, example='user@example.com'),
        #         'password': openapi.Schema(type=openapi.TYPE_STRING, example='strongpassword123'),
        #     },
        # ),
        responses={
            200: openapi.Response(
                description="User registered",
                examples={
                    "application/json": {
                        "message": "Login successful",
                        "Token": "jwt_token",
                        "data": {"name": "name"}
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "Email already exists"
                    }
                }
            )
        }
    )
@csrf_exempt
@api_view(['POST'])
def ErrandUserRegistration(request):
    print('ErrandUserRegistration CALLED')
    serializer = ErrandUserSignUpSerializer(data = request.data)
    print('request.data')
    print(request.data)
    if serializer.is_valid():
        fullname = serializer.data['fullname']
        useremailaddress = serializer.data['emailAddress']
        phone = serializer.data['phonenumber']
        password = serializer.data['password']
        
        # generate referral code for user
        uniqueCode = get_random_string(length=4)
        userUniqueName =( serializer.data['emailAddress']).split('@')[0]
        generatedUserReferralCode = userUniqueName +"_"+uniqueCode
        
        if not serializer.data['fullname']:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'error': 'Kindly enter a full name',
            })

        if not serializer.data['emailAddress']:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": "Kindly enter an email address",
                },
            })
        
        if not serializer.data['phonenumber']:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "phone": "Kindly enter a phone number",
                },
            })

        data = ErrandUsers.objects.filter(emailAddress = useremailaddress)
        if data:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": "A user already exist with this email.",
                },
            })
        
        UserDataCheckEmail = User.objects.filter(email=useremailaddress)
        if UserDataCheckEmail:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": "A user already exist with this email.",
                },
            })
        
        checkphonenumber = ErrandUsers.objects.filter(phonenumber=phone)
        if checkphonenumber:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "phone": "A user already exist with this phone number.",
                },
            })

        else:
            userprofile = User.objects.create_user(username=useremailaddress, email=useremailaddress, password=password, first_name=fullname, last_name=phone)
            userprofile.save()
            
            
            cryptpassword = make_password(password)
            form = ErrandUsers(user = userprofile, fullname=fullname, emailAddress = useremailaddress, phonenumber=phone, password=cryptpassword)
            form.save()
            
            # send activation email to user 
            # try:
            #     activateEmail(companyname, useremailaddress, generatedCompanyUniqueID)
            # except:
            #     print('Registration mail was not sent successfully')
            
            getUserusername = useremailaddress
            getUserPassword = password
                    
            tokenCreationData = {
                'username': getUserusername,
                'password': getUserPassword
            }
            
            CheckUserUsername = User.objects.get(email = useremailaddress).username
            
            token_serializer = CustomTokenObtainPairSerializer(data=tokenCreationData)
            token_serializer.is_valid(raise_exception=True)
            Token = token_serializer.validated_data

            # 

            try:
                authenticate(request, username = CheckUserUsername, password = password)
                print('User auth worked fine')
                # fetch user data for response
                userModel = ErrandUsers.objects.get(emailAddress = useremailaddress)
                name = userModel.fullname
                email = userModel.emailAddress
                phone = userModel.phonenumber
                    
                userData = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                }
                
                return Response({
                "status": status.HTTP_200_OK,
                "message": "Errand User created was Successful.",
                "token": Token,
                "data": userData
            })
            
            except:
                print('There was a problem authenticating this errand user, kindly confirm your details and try again.')
        
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'error': serializer.errors,
        })

