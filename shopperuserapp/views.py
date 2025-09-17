from django.db import models
import datetime
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q



from customeruserapp.models import ErrandUserAssignTrackingModel, ShoppingListModel
from onboardingapp.models import ErrandUsers
from collections import defaultdict

from shopperuserapp.models import ErrandUserAccountBalanceTracker
from shopperuserapp.serializer import ShoppingListSerializer


def generate_unique_code(prefix="CODE"):
    # Get current time down to microseconds
    now = datetime.datetime.now()
    time_str = now.strftime('%Y%m%d%H%M%S%f')  # e.g. '20250807115723987654'
    print(f"{prefix}-{time_str}")
    return f"{prefix}-{time_str}"



# def GenerateCodeForPurchaseListReg(request):
#     generate_unique_code(prefix='isaacfrank')



@swagger_auto_schema(
    method='get',
        tags=['shopperApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchShoppingLists(request):
    print('FetchShoppingLists CALLED')
    errand_user = ErrandUsers.objects.filter(user=request.user).first()
    print(errand_user)
    if not errand_user:
        return Response(
            {"detail": "No errand user profile found for this account."},
            status=status.HTTP_404_NOT_FOUND
            # status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch all items in one query
    items = (
        ShoppingListModel.objects
        .filter(errandUser=errand_user)
        .select_related('product', 'user', 'errandUser', 'itemRequester')
        .order_by('shoppingListID', '-created_at')
    )
    print('items')
    print(items)

    if not items.exists():
        print('no items assigned to this user')
        return Response(
        {
            "status": status.HTTP_200_OK,
            "count": 0,
            "data": [],
            "message": "No shopping list items found for this user"
        })

    # Group by shoppingListID
    grouped = defaultdict(list)
    print('grouped')
    print(grouped)
    for item in items:
        grouped[item.shoppingListID].append(ShoppingListSerializer(item).data)

    # Return grouped dict as JSON
    # print('list(grouped.keys())')
    # print(dict(grouped))
    # print(len(dict(grouped)))
    return Response(
        {
            "status": status.HTTP_200_OK,
            "count": len(grouped),
            # "data": grouped
            "data":  [{k: v} for k, v in grouped.items()]
        },
    )
    



@swagger_auto_schema(
    method='get',
        tags=['shopperApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchShoppingItems(request):
    print('FetchShoppingItems CALLED')
    errand_user = ErrandUsers.objects.filter(user=request.user).first()
    print('request.data')
    print(request.data)
    id = request.data['shoppingListID']
    print('id')
    print(id)
    print(errand_user)
    if not errand_user:
        return Response(
            {"detail": "No errand user profile found for this account."},
            status=status.HTTP_404_NOT_FOUND
            # status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch all items in one query
    items = (
        ShoppingListModel.objects
        .filter(Q(errandUser=errand_user) & Q(shoppingListID = id))
        .select_related('product', 'user', 'errandUser', 'itemRequester')
        .order_by('shoppingListID', '-created_at')
    )
    print('items')
    print(items)

    if not items.exists():
        print('no items assigned to this user')
        return Response(
        {
            "status": status.HTTP_200_OK,
            "count": 0,
            "data": [],
            "message": "No shopping list items found for this user"
        })

    # Group by shoppingListID
    grouped = defaultdict(list)
    print('grouped')
    print(grouped)
    for item in items:
        grouped[item.shoppingListID].append(ShoppingListSerializer(item).data)

    # Return grouped dict as JSON
    print('list(grouped.keys())')
    print(dict(grouped))
    print(len(dict(grouped)))
    return Response(
        {
            "status": status.HTTP_200_OK,
            "count": len(grouped),
            # "data": grouped
            "data":  [{k: v} for k, v in grouped.items()]
        },
    )
    
    
    


@swagger_auto_schema(
    method='get',
        tags=['shopperApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def ErrandUserAccountBalance(request):
    if ErrandUserAccountBalanceTracker.objects.filter(user=request.user).exists():
        getUser = ErrandUserAccountBalanceTracker.objects.filter(user=request.user).first()
        accountBalance = getUser.AccountBalance
        
        # userData = {
        #     'accountBalance': accountBalance
        # }
            
        return Response({
                "status": status.HTTP_200_OK,
                'message': 'Account balance found successfully',
                'balance': accountBalance
            })
            
    else:
        return Response({
                "status": status.HTTP_200_OK,
                'message': 'Account balance not found.',
                'balance': 0.00
            })










