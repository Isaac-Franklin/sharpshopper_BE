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
from shopperuserapp.serializer import *


def generate_unique_code(prefix="CODE"):
    # Get current time down to microseconds
    now = datetime.datetime.now()
    time_str = now.strftime('%Y%m%d%H%M%S%f')  # e.g. '20250807115723987654'
    print(f"{prefix}-{time_str}")
    return f"{prefix}-{time_str}"



# def GenerateCodeForPurchaseListReg(request):
#     generate_unique_code(prefix='isaacfrank')



# @swagger_auto_schema(
#     method='get',
#         tags=['shopperApp'],
#     )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def FetchShoppingLists(request):
#     print('FetchShoppingLists CALLED')
#     errand_user = ErrandUsers.objects.filter(user=request.user).first()
#     print(errand_user)
#     if not errand_user:
#         return Response(
#             {"detail": "No errand user profile found for this account."},
#             status=status.HTTP_404_NOT_FOUND
#             # status=status.HTTP_400_BAD_REQUEST
#         )

#     # Fetch all items in one query
#     items = (
#         ShoppingListModel.objects
#         .filter(errandUser=errand_user)
#         .select_related('product', 'user', 'errandUser', 'itemRequester')
#         .order_by('-created_at')
#     )

#     if not items.exists():
#         print('no items assigned to this user')
#         return Response(
#         {
#             "status": status.HTTP_200_OK,
#             "count": 0,
#             "data": [],
#             "message": "No shopping list items found for this user"
#         })

#     # Group by shoppingListID
#     grouped = defaultdict(list)
#     print('grouped')
#     print(grouped)
#     for item in items:
#         grouped[item.shoppingListID].append(ShoppingListSerializer(item).data)
    
#     return Response(
#         {
#             "status": status.HTTP_200_OK,
#             "count": len(grouped),
#             # "data": grouped
#             "data":  [{k: v} for k, v in grouped.items()]
#         },
#     )
    


@swagger_auto_schema(
    method='get',
    query_serializer=FetchShoppingListsSerializer,
    tags=['shopperApp'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchShoppingLists(request):
    print('request.query_params')
    print(request.query_params)
    serializer = FetchShoppingListsSerializer(data=request.query_params)
    if serializer.is_valid():
        filter_param = serializer.validated_data['filter']
    else:
        filter_param = 'all'
    errand_user = ErrandUsers.objects.filter(user=request.user).first()
    if not errand_user:
        return Response(
            {"detail": "No errand user profile found for this account."},
            status=status.HTTP_404_NOT_FOUND
        )

    # filter_param = request.query_params.get('filter', 'all').lower()

    # Base queryset
    items = ShoppingListModel.objects.filter(errandUser=errand_user)

    # Apply filter
    if filter_param == 'Delivered':
        items = items.filter(deliveryStatus='delivered')
    elif filter_param == 'Not Delivered':
        items = items.exclude(deliveryStatus='delivered')
    # else 'all' -> no extra filtering

    items = items.select_related(
        'product', 'user', 'errandUser', 'itemRequester'
    ).order_by('-created_at')

    if not items.exists():
        return Response(
            {
                "status": status.HTTP_200_OK,
                "count": 0,
                "data": [],
                "message": f"No shopping list items found for filter '{filter_param}'"
            })

    # Group by shoppingListID
    grouped = defaultdict(list)
    for item in items:
        grouped[item.shoppingListID].append(ShoppingListSerializer(item).data)

    return Response(
        {
            "status": status.HTTP_200_OK,
            "count": len(grouped),
            "data": [{k: v} for k, v in grouped.items()]
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
    print('ErrandUserAccountBalance CALLED')
    if ErrandUserAccountBalanceTracker.objects.filter(user=request.user).exists():
        getUser = ErrandUserAccountBalanceTracker.objects.filter(user=request.user).first()
        print('getUser')
        print(getUser)
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
                'balance': 0
            })




@swagger_auto_schema(
    method='put',
        request_body= MarkAsDeliveredSerializer,
        tags=['shopperApp'],
    )
@api_view(['PUT'])
@permission_classes([IsAuthenticated]) 
def MarkShoppingListAsDelivered(request):
    print('MarkAsDelivered CALLED')
    serializer = MarkAsDeliveredSerializer(data=request.data)
    print('request.data')
    print(request.data)
    if serializer.is_valid():
        shoppingListID = request.data['shoppingListID']
        
    else:
        print('serializer.errors')
        print(serializer.errors)
        return Response({
                "status": status.HTTP_404_NOT_FOUND,
                'message': 'Shopping list status update was not successful.',
                'error': serializer.errors
            })
    
    getShoppingList = ShoppingListModel.objects.filter(shoppingListID = shoppingListID)
    for list in getShoppingList:
        print('list')
        print(list)
        changeStatus = {'deliveryStatus': 'delivered'}
        # getSpecificShoppingList = ShoppingListModel.objects.get(shoppingListID = shoppingListID)
        updateserializer = UpdateShoppingListDeliveredSerializer(list, changeStatus)
        if updateserializer.is_valid():
            updateserializer.save()
        
    return Response({
            "status": status.HTTP_200_OK,
            'message': 'Shopping list status update was successful.',
        })
    
    
    # findStudentUser = User.objects.get(email = request.user.email)
    #             serializer = Update_Student_Registration_Serializer(currentUser, data = userDataToSave)
    #             if serializer.is_valid():
    #                 serializer.save()







