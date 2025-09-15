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
from adminapp.dashboarddata import *
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
from django.utils import timezone
from django.db.models import Count
import calendar
from django.db.models import Sum
from django.db.models.functions import ExtractWeek, ExtractWeekDay, ExtractMonth
from datetime import date, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ShopperUsers, ErrandUsers
from .serializers import ShopperUserSerializer, ErrandUserSerializer, TransactionSerializer

from django.utils.timesince import timesince
from django.utils.timezone import now


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

        # Example: disallow specific email and password values
        if email.lower() != "sharpshopperng@gmail.com":
            return Response({
                "status": 400,
                "message": "This email is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if password != "X9v!tR7@wQ2#kLm4":
            return Response({
                "status": 400,
                "message": "This password is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)
                
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
        
        

@swagger_auto_schema(
    method='get',
        tags=['adminApp'],
    )
@api_view(['GET'])
def DashboardStats(request):
    allUsers = ShopperUsers.objects.filter()
    data = []
    allUsersCount = allUsers.count()
    userRegistrationPercentage, userRegistrationTrend = get_monthly_user_stats()
    userTrackDescription =  "Active users this month"
    
    activeUserData = {
        'title': "Total Members",
        'value': allUsersCount,
        'change': userRegistrationPercentage,
        'trend': userRegistrationTrend,
        'description': userTrackDescription,
    }
    
    data.append(activeUserData)
    
    # transaction amount and rate
    percentage_change, trend, = get_monthly_spent_stats()
    total_spent = NotificationActivity.objects.aggregate(total=Sum(Cast("amountSpent", FloatField())))["total"] or 0
    
    totalTransactionData = {
        'title': "Total Transactions",
        'value': total_spent,
        'change': percentage_change,
        'trend': trend,
        'description': 'Total transactions this month',
    }
    
    data.append(totalTransactionData)
    
    total_pending, percentage_change, trend = get_order_pending_stats()
    
    pendingDeliveryData = {
        'title': "Pending Deliveries",
        'value': total_pending,
        'change': percentage_change,
        'trend': trend,
        'description': 'Track pending deliveries',
    }
    
    data.append(pendingDeliveryData)
    
    total_utility_count, percentage_change, trend = get_utility_stats(request)
    
    utilityTransactionData = {
        'title': "Utility Purchases",
        'value': total_utility_count,
        'change': percentage_change,
        'trend': trend,
        'description': 'Utility purchased over time',
    }
    
    data.append(utilityTransactionData)
    
    return Response({
            "status": status.HTTP_200_OK,
            'data': data,
            'message': 'Dashboard stats fetched successfully'
        })
    




@swagger_auto_schema(
    method='get',
        tags=['adminApp'],
    )
@api_view(["GET"])
def dashboard_analytics(request):
    period = request.GET.get("period", "monthly").lower()
    analytics = build_global_deposit_analytics()

    # Return everything if period=all
    if period == "all":
        data = analytics
    else:
        # Safe lookup with default fallback to "monthly"
        data = analytics.get(period, analytics["monthly"])

    return Response({
        "status": status.HTTP_200_OK,
        "period": period,
        "data": analytics,
    })


@swagger_auto_schema(
    method='get',
        tags=['adminApp'],
    )
@api_view(["GET"])
def get_recent_activity(request):    
    activities = NotificationActivity.objects.all()[:10]

    data = [
        {
            "id": activity.id,
            "user": activity.user.username if activity.user else None,
            "action": activity.activityTtile,   # maps to "action" in frontend
            "time": timesince(activity.created_at, now()) + " ago",  # relative time
            "type": activity.category or "general",  # maps to "type" in frontend
        }
        for activity in activities
    ]

    return Response({
        "status": status.HTTP_200_OK,
        "data": data
    })


@swagger_auto_schema(
    method='get',
        tags=['adminApp'],
    )
@api_view(["GET"])
def GetAllUsers(request):
    shoppers = ShopperUsers.objects.select_related("user").all()

    data = []
    for shopper in shoppers:
        # Find account balance (latest record if multiple)
        balance_record = (
            UserAccountBalanceTracker.objects.filter(user=shopper.user)
            .order_by("-created_at")
            .first()
        )
        account_balance = balance_record.AccountBalance if balance_record else 0

        # Count total transactions from NotificationActivity
        total_transactions = NotificationActivity.objects.filter(
            user=shopper.user
        ).count()

        # Calculate last activity (if any)
        last_activity = (
            NotificationActivity.objects.filter(user=shopper.user)
            .order_by("-created_at")
            .first()
        )
        if last_activity:
            from django.utils.timesince import timesince

            last_activity_time = timesince(last_activity.created_at, now()) + " ago"
        else:
            last_activity_time = "N/A"

        # Append formatted user data
        data.append(
            {
                "id": shopper.id,
                "name": shopper.fullname or shopper.user.username,
                "email": shopper.emailAddress,
                "phone": shopper.phoneNumber,
                "accountBalance": account_balance,
                "joinDate": shopper.created_at.strftime("%Y-%m-%d"),
                "status": "active",  # You can extend if you have a status field
                "totalTransactions": total_transactions,
                "lastActivity": last_activity_time,
            }
        )

    return Response(
        {
            "status": status.HTTP_200_OK,
            "results": data,
        }
    )
    


@api_view(["GET"])
def get_errand_users(request):
    errand_users = ErrandUsers.objects.select_related("user").all()
    data = []

    for errand in errand_users:
        # Get all orders for this errand user
        assigned_orders = OrderStatusTracking.objects.filter(errandUser=errand)
        total_assigned = assigned_orders.count()

        # Delivered orders
        delivered_orders = assigned_orders.filter(deliveryStatus="delivered").count()

        # Success rate
        success_rate = (
            round((delivered_orders / total_assigned) * 100, 1)
            if total_assigned > 0
            else 0
        )

        # Last activity
        last_order = assigned_orders.order_by("-created_at").first()
        if last_order:
            last_activity = timesince(last_order.created_at, now()) + " ago"
        else:
            last_activity = "N/A"

        data.append(
            {
                "id": errand.id,
                "name": errand.fullname or errand.user.username,
                "email": errand.emailAddress,
                "phone": errand.phonenumber,
                "accountBalance": 0,  # (no model for now, can link if needed)
                "joinDate": errand.created_at.strftime("%Y-%m-%d"),
                "status": "active",  # static unless you have a field
                "ordersAssigned": total_assigned,
                "ordersDelivered": delivered_orders,
                "successRate": success_rate,
                "rating": 0.0,  # placeholder, no model provided
                "lastActivity": last_activity,
            }
        )

    return Response({"status": status.HTTP_200_OK, "results": data})



@api_view(["GET"])
def fetchAllAppUsers(request):
    user_type = request.GET.get('user_type', 'normal')  # default = normal

    if user_type == 'normal':
        users = ShopperUsers.objects.all()
        data = []
        for u in users:
            total_txn = NotificationActivity.objects.filter(user=u.user).count()
            balance_obj = UserAccountBalanceTracker.objects.filter(user=u.user).last()
            last_activity = NotificationActivity.objects.filter(user=u.user).order_by('-created_at').first()

            data.append({
                "id": u.id,
                "name": u.fullname,
                "email": u.emailAddress,
                "phone": u.phoneNumber,
                "accountBalance": balance_obj.AccountBalance if balance_obj else 0,
                "joinDate": u.created_at.strftime("%Y-%m-%d"),
                "status": "active",
                "totalTransactions": total_txn,
                "lastActivity": timesince(last_activity.created_at, now()) + " ago" if last_activity else "N/A",
            })

        return Response({"results": data}, status=status.HTTP_200_OK)

    elif user_type == 'errand':
        users = ErrandUsers.objects.all()
        data = []
        for u in users:
            orders = OrderStatusTracking.objects.filter(errandUser=u)
            total_assigned = orders.count()
            delivered = orders.filter(deliveryStatus="delivered").count()
            success_rate = round((delivered / total_assigned) * 100, 1) if total_assigned > 0 else 0
            last_order = orders.order_by('-created_at').first()

            data.append({
                "id": u.id,
                "name": u.fullname,
                "email": u.emailAddress,
                "phone": u.phonenumber,
                "accountBalance": 0,  # adjust if you track balances for errands
                "joinDate": u.created_at.strftime("%Y-%m-%d"),
                "status": "active",
                "ordersAssigned": total_assigned,
                "ordersDelivered": delivered,
                "successRate": success_rate,
                "rating": 0.0,
                "lastActivity": timesince(last_order.created_at, now()) + " ago" if last_order else "N/A",
            })

        return Response({"results": data}, status=status.HTTP_200_OK)

    else:
        return Response({
            "error": "Invalid user_type. Must be 'normal' or 'errand'."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(["GET"])
def get_member(request, id):
    user = get_object_or_404(ShopperUsers, pk=id)  # extend to check ErrandUsers if needed
    serializer = ShopperUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 3. Create member
@api_view(["POST"])
def create_member(request):
    serializer = ShopperUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 4. Update member
@api_view(["PUT"])
def update_member(request, id):
    user = get_object_or_404(ShopperUsers, pk=id)
    serializer = ShopperUserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Delete member
@api_view(["DELETE"])
def delete_member(request, id):
    user = get_object_or_404(ShopperUsers, pk=id)
    user.delete()
    return Response({"message": "Member deleted"}, status=status.HTTP_204_NO_CONTENT)

# 6. Member statistics
@api_view(["GET"])
def get_member_stats(request):
    stats = {
        "normal_users": ShopperUsers.objects.count(),
        "errand_users": ErrandUsers.objects.count(),
    }
    return Response(stats, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_all_transactions(request):
    transactions = NotificationActivity.objects.all()
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_transaction_stats(request):
    # Calculate total amount (credits add, debits subtract)
    total_amount = 0
    transactions = NotificationActivity.objects.all()

    for tx in transactions:
        try:
            amount = float(tx.amountSpent or 0)
        except:
            amount = 0
        if tx.transactionEffect == "Add":
            total_amount += amount
        else:
            total_amount += amount

    completed_transactions = NotificationActivity.objects.filter(deliveryStatus="successful").count()
    pending_transactions = NotificationActivity.objects.filter(deliveryStatus="failed").count()

    return Response({
        "total_amount": total_amount,
        "completed_transactions": completed_transactions,
        "pending_transactions": pending_transactions,
    }, status=status.HTTP_200_OK)
    
    

@api_view(['GET'])
def GetOrderForAgentAdnOrderPage(request):
    orders = OrderStatusTracking.objects.select_related("errandUser", "user").all()
    order_data = []

    for idx, order in enumerate(orders, start=1):
        # Get customer (ShopperUser) linked to this order via ShoppingListModel
        shopping = ShoppingListModel.objects.filter(shoppingListID=order.shoppingListID).first()
        customer_name = shopping.itemRequester.fullname if shopping and shopping.itemRequester else "Unknown Customer"
        items = [shopping.product.productName] if shopping and shopping.product else []

        order_data.append({
            "id": f"ORD{str(idx).zfill(3)}",
            "customer": customer_name,
            "agent": order.errandUser.fullname if order.errandUser else "Unassigned",
            "status": order.deliveryStatus,
            "priority": "high" if shopping and shopping.numberofitems > 5 else "medium" if shopping and shopping.numberofitems > 2 else "low",
            "amount": float(shopping.productPriceAtPurchase or 0) * shopping.numberofitems if shopping else 0,
            "address": shopping.deliveryLocation if shopping else None,
            "createdAt": order.created_at,
            "deliveredAt": order.actualPackageDeliveryDateTime,
            "items": items,
        })

    return Response({
        "data": order_data,
    }, status=status.HTTP_200_OK)




@api_view(['GET'])
def GetAllAgentsForAgentAndOrderPage(request):
    agents = ErrandUsers.objects.all()
    agent_data = []

    for agent in agents:
        assigned_orders = OrderStatusTracking.objects.filter(errandUser=agent)
        delivered_orders = assigned_orders.filter(deliveryStatus="delivered")

        total_assigned = assigned_orders.count()
        total_delivered = delivered_orders.count()
        success_rate = (total_delivered / total_assigned * 100) if total_assigned > 0 else 0

        agent_data.append({
            "id": agent.id,
            "name": agent.fullname,
            "email": agent.emailAddress,
            "phone": agent.phonenumber,
            "status": "active" if total_assigned > 0 else "inactive",
            "rating": 4.5,  # placeholder unless you have ratings
            "ordersAssigned": total_assigned,
            "ordersDelivered": total_delivered,
            "successRate": round(success_rate, 1),
            "currentOrders": assigned_orders.filter(deliveryStatus__in=["in-progress", "in_store"]).count(),
            "location": agent.user.username if agent.user else "Unknown Area",  # adjust if location exists
        })

    

    return Response({
        "data": agent_data,
    }, status=status.HTTP_200_OK)



 



@api_view(['GET'])
def FetchUtilityPurchases(request):
    UTILITY_KEYWORDS = ["Airtime", "Electricity", "Cable", "Data"]
    # Get all activities that match utility keywords
    activities = NotificationActivity.objects.filter(
        activityTtile__iregex=r'(' + '|'.join(UTILITY_KEYWORDS) + ')'
    ).order_by('-created_at')

    purchases = []
    for idx, act in enumerate(activities, start=1):
        purchases.append({
            "id": f"UTL{str(idx).zfill(3)}",  # UTL001, UTL002, ...
            "customer": act.user.get_full_name() or act.user.username,
            "utility": act.activityTtile.lower(),  # e.g. "electricity"
            "provider": "Unknown Provider",  # you can enhance later
            "amount": float(act.amountSpent or 0),
            "units": f"{act.amountSpent} units" if act.amountSpent else "N/A",
            "status": act.deliveryStatus.lower(),  # completed/pending/etc.
            "date": act.created_at.isoformat(),
            "reference": f"REF{act.id:06}",  # Unique reference
        })
    print('purchases')
    print(purchases)
    return Response({
        "status": status.HTTP_200_OK,
        "data": purchases,
    })
    
    


@api_view(['GET'])
def get_utility_stats(request):
    UTILITY_KEYWORDS = ["Airtime", "Electricity", "Cable", "Data"]
    try:
        # Filter only utility transactions
        utilities = NotificationActivity.objects.filter(
            activityTtile__iregex=r'(' + '|'.join(UTILITY_KEYWORDS) + ')'
        )

        total = utilities.count()
        successful = utilities.filter(deliveryStatus__iexact="Success").count()
        failed = utilities.filter(deliveryStatus__iexact="Failed").count()

        return Response({
            "status": 200,
            "message": "Utility stats fetched successfully",
            "data": {
                "total": total,
                "successful": successful,
                "failed": failed
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "status": 400,
            "message": "Failed to fetch utility stats",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
        


# GET all data plans
@api_view(['GET'])
def get_data_plans(request):
    try:
        plans = DataPlans.objects.all()
        result = []
        for plan in plans:
            result.append({
                "id": plan.id,
                "plan": plan.productName,
                "provider": plan.network.network if plan.network else "Unknown",
                "amount": float(plan.dataCost) if plan.dataCost else 0,
                "description": f"{plan.dataPlanType} plan",
                "validity": plan.dataValidity,
                "status": "active",  # you can extend to have a status field
                "createdAt": plan.created_at.isoformat(),
            })
        return Response({
            "status": 200,
            "message": "Data plans fetched successfully",
            "data": result
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": 400,
            "message": "Failed to fetch data plans",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# CREATE a new data plan
# CREATE a new data plan
@api_view(['POST'])
def create_data_plan(request):
    try:
        network_id = request.data.get("network")
        network = NetworkID.objects.get(id=network_id) if network_id else None

        plan = DataPlans.objects.create(
            network=network,
            productName=request.data.get("name"),
            planID=request.data.get("planID", 0),
            dataPlanType=request.data.get("description", "SME"),
            dataCost=request.data.get("amount", "0"),
            dataValidity=request.data.get("validity", "monthly"),
        )
        return Response({
            "status": 200,
            "message": "Data plan created successfully",
            "data": {
                "id": plan.id,
                "plan": plan.productName,
                "provider": plan.network.network if plan.network else "Unknown",
                "amount": float(plan.dataCost),
                "description": plan.dataPlanType,
                "validity": plan.dataValidity,
                "status": "active",
                "createdAt": plan.created_at.isoformat(),
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": 400,
            "message": "Failed to create data plan",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# UPDATE an existing data plan
@api_view(['PUT'])
def update_data_plan(request, id):
    try:
        plan = DataPlans.objects.get(id=id)

        if "name" in request.data:
            plan.productName = request.data["name"]
        if "amount" in request.data:
            plan.dataCost = request.data["amount"]
        if "description" in request.data:
            plan.dataPlanType = request.data["description"]
        if "validity" in request.data:
            plan.dataValidity = request.data["validity"]
        if "network" in request.data:
            network_id = request.data.get("network")
            plan.network = NetworkID.objects.get(id=network_id) if network_id else plan.network

        plan.save()

        return Response({
            "status": 200,
            "message": "Data plan updated successfully",
            "data": {
                "id": plan.id,
                "plan": plan.productName,
                "provider": plan.network.network if plan.network else "Unknown",
                "amount": float(plan.dataCost),
                "description": plan.dataPlanType,
                "validity": plan.dataValidity,
                "status": "active",
                "createdAt": plan.created_at.isoformat(),
            }
        }, status=status.HTTP_200_OK)

    except DataPlans.DoesNotExist:
        return Response({
            "status": 404,
            "message": "Data plan not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 400,
            "message": "Failed to update data plan",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# DELETE a data plan
@api_view(['DELETE'])
def delete_data_plan(request, id):
    try:
        plan = DataPlans.objects.get(id=id)
        plan.delete()
        return Response({
            "status": 200,
            "message": "Data plan deleted successfully"
        }, status=status.HTTP_200_OK)

    except DataPlans.DoesNotExist:
        return Response({
            "status": 404,
            "message": "Data plan not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 400,
            "message": "Failed to delete data plan",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
        

