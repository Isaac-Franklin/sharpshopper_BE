import csv
import json
import socket
import concurrent.futures
from smtplib import SMTPException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from customeruserapp.generateshoppingcode import generate_unique_code
from customeruserapp.paystackViews import confirmBalanceIsEnough, decreaseAccountBalance
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
from collections import defaultdict

from shopperuserapp.serializer import ShoppingListSerializer



# Create your views here.
def CategoryItems(request):
    pass

@swagger_auto_schema(
    method='get',
    tags=['customerApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetProductCategories(request):
    print('GetProductCategories CALLED')
    catrgoryList = []
    categories = ProductCategories.objects.filter()
    for category in categories:
        print(category)
        if category.categoryImage :
            image = image = request.build_absolute_uri(category.categoryImage.url)
        else:
            image = ''
        id = category.id
        name = category.categoryName
        image = image
        
        item = {
            'id': id,
            'name': name,
            'image': image
        }
        
        catrgoryList.append(item)
        
    return Response({
                "status": status.HTTP_200_OK,
                "dataLength": len(catrgoryList),
                "data": catrgoryList,
                "message": "Categories fetched successfully",
            }) 
        

@swagger_auto_schema(
    method='get',
        tags=['customerApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def RegisterProductCategory(request):
    pass


@swagger_auto_schema(
    method='get',
        tags=['customerApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchProducts(request):
    # Use select_related to fetch the category data in a single query
    allProducts = Products.objects.select_related('productCategory').all()
    print('allProducts')
    print(allProducts)
    # Use a dictionary to group products by their category name
    categorized_products = {}

    for product in allProducts:
        # Get the category name
        category_name = product.productCategory.categoryName
        
        # Prepare the data for a single product item
        if (product.productImage):
            image = request.build_absolute_uri(product.productImage.url),
        else:
             image = '',
            
        product_item = {
            'id': product.pk,  # Use the product's primary key
            'name': product.productName, 
            'price': product.productPrice, 
            'availabilityStatus': product.productAvailability, # Renamed to match your sample
            'image': image[0],
        }
        
        # If the category is not a key in our dictionary, create it
        if category_name not in categorized_products:
            categorized_products[category_name] = []
        
        # Append the current product to the list for its category
        categorized_products[category_name].append(product_item)

    # Now, format the dictionary into the final list of dictionaries
    allProductList = []
    for category_name, products_list in categorized_products.items():
        category_object = {
            'category': category_name,  # Renamed to match your sample
            'items': products_list
        }
        allProductList.append(category_object)
    
    return Response({
        "status": status.HTTP_200_OK,
        "dataLength": len(allProductList),
        "data": allProductList,
        "message": "Categories fetched successfully",
    })


@swagger_auto_schema(
    method='get',
        tags=['customerApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def UpdateListPrices(request):
    itemsToPurchase = []
    itemsInCart = request.data['itemsList']
    print('itemsInCart')
    print(itemsInCart)
    for itemId in itemsInCart:
        getProduct =  Products.objects.get(id = itemId['product_id'])
        getProductID = getProduct.id
        # Prepare the data for a single product item
        if (getProduct.productImage):
            image = request.build_absolute_uri(getProduct.productImage.url),
        else:
             image = 'none',
        getProductPrice =  getProduct.productPrice
        getProductName =  getProduct.productName
        getProductImage =  image,
        
        productsDetails = {
            'id': getProductID,
            'price': int(getProductPrice),
            'name': getProductName,
            'image': getProductImage,
            'quantity': 0,
        }
        
        itemsToPurchase.append(productsDetails)
        
    print(itemsToPurchase)
        
    return Response({
        "status": status.HTTP_200_OK,
        "dataLength": len(itemsToPurchase),
        "data": itemsToPurchase,
        "message": "List of items fetched successfully",
    })

# 
@swagger_auto_schema(
    method='post',
    tags=['customerApp'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def SaveShoppinglist(request):
    print('SaveShoppinglist CALLED')
    itemsInCart = request.data.get('itemsList', [])
    deliveryLocation = request.data.get('deliveryLocation', None)

    if not itemsInCart:
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "No items found in your cart."
        })

    username = request.user.email.split('@')[0]
    shoppinglistcode = generate_unique_code(prefix=username)
    getErrandPerson = UpdateShopperSelectionModel()
    itemRequester = ShopperUsers.objects.get(emailAddress=request.user.email)
    
    pickUpState = 'Lagos'
    deliveryState = deliveryLocation.split()[-1]
    deliveryCountry = 'Nigeria'
    pickUpCountry = 'Nigeria'
    
    allPrices = []
    productsToSave = []  # keep products temporarily until balance is confirmed

    # --- Step 1: Calculate total cost ---
    for itemId in itemsInCart:
        itemQuantity = itemId['quantity'] if itemId['quantity'] > 0 else 1
        getProduct = Products.objects.get(id=itemId['product_id'])
        costForItem = int(getProduct.productPrice) * int(itemQuantity)
        allPrices.append(costForItem)

        productsToSave.append({
            "product": getProduct,
            "price": getProduct.productPrice,
            "quantity": itemQuantity
        })

    totalCostOfItems = sum(allPrices)

    # --- Step 2: Check wallet balance ---
    if not UserAccountBalanceTracker.objects.filter(emailAddress=request.user.email).exists():
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "You are yet to fund your wallet, kindly deposit and try again.",
        })

    getuser = UserAccountBalanceTracker.objects.get(emailAddress=request.user.email)
    userBalance = getuser.AccountBalance

    if int(userBalance) < int(totalCostOfItems):
        naira_user_balance = f"₦{int(userBalance):,}"
        naira_total_cost = f"₦{int(totalCostOfItems):,}"

        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": (
                f"Your current account balance is {naira_user_balance}, "
                f"which is not enough to fulfil your order of {naira_total_cost}. "
                "Kindly top up your balance to continue."
            ),
        })

    # --- Step 3: Deduct balance ---
    decreaseAccountBalance(request, totalCostOfItems)
    
    NotificationActivity.objects.create(user = request.user, transactionEffect = 'Subtract', activityTtile = 'Shopped', deliveryStatus = 'Successfull', amountSpent = totalCostOfItems)

    # --- Step 4: Now save shopping list items ---
    data = getErrandPerson.data
    if data["status"] == 200:
        getErrandPersonID = data['id']
        getErrandPersonMain = ErrandUsers.objects.get(id=data['id'])
    else:
        getErrandPersonID = 10
        getErrandPersonMain = ErrandUsers.objects.get(id=10)

    for productData in productsToSave:
        ShoppingListModel.objects.create(
            user=request.user,
            product=productData["product"],
            productPriceAtPurchase=productData["price"],
            shoppingListID=shoppinglistcode,
            assignedErrandPersonID=getErrandPersonID,
            errandUser=getErrandPersonMain,
            numberofitems=productData["quantity"],
            itemRequester=itemRequester,
            deliveryLocation=deliveryLocation
        )

    # save shopping tracking details model
    OrderStatusTracking.objects.create(
        user=request.user,
        errandUser=getErrandPersonMain,
        pickUpState=pickUpState,
        pickUpCountry=pickUpCountry,
        deliveryState=deliveryState,
        deliveryCountry=deliveryCountry,
        shoppingListID=shoppinglistcode
    )

    return Response({
        "status": status.HTTP_200_OK,
        "message": "Your order request has been placed successfully.",
    })
    
# 

def ShopperSelection(request):
    assignedShoppers = ErrandUserAssignTrackingModel.objects.get()
    assignedShoppersList = assignedShoppers.assignedShoppersIDList
    # if assignedShoppersList
    
    # ErrandUsers.objects.get(id = )
    
    pass

# 
def GetAllErrandUsersList():
    print('GetAllErrandUsersList CALLED')
    allErrandUsersAvailable = []
    allErrandUsers = ErrandUsers.objects.values_list('id', flat=True)
    for user in allErrandUsers:
        allErrandUsersAvailable.append(user)
        
    return allErrandUsersAvailable
    

# 
def UpdateShopperSelectionModel():
    assignedErrander = ErrandUserAssignTrackingModel.objects.first()
    allErrandUsersAvailable = GetAllErrandUsersList()
    currentAssignErrander = assignedErrander.assignederranderIDList
    print('currentAssignErrander')
    print(currentAssignErrander)
    actualErrandUserList = ast.literal_eval(currentAssignErrander)
    print('actualErrandUserList')
    print(actualErrandUserList)
    
    if all(elem in actualErrandUserList for elem in allErrandUsersAvailable):
        print('ALL ERRAND USERS ARE ASSIGNED')
        assignUser = allErrandUsersAvailable[0]
        ErrandUserAssignTrackingModel.objects.all().delete()
        # 
        saveForm = ErrandUserAssignTrackingModel(assignederranderIDList = str([assignUser]))
        saveForm.save()
        return Response({
                "status": status.HTTP_200_OK,
                "id": assignUser,
            })

    else:
        for id in allErrandUsersAvailable:
            print('id')
            print(id)
            if id in actualErrandUserList:
                print('This errand person has been assign a task recently')
                pass
                
            elif id not in actualErrandUserList:            # 
                print('id is not in actualErrandUserList')
                # 
                actualErrandUserList.append(id)
                saveForm = ErrandUserAssignTrackingModel(assignederranderIDList = str(actualErrandUserList))
                saveForm.save()
                # 
                print(actualErrandUserList)  
                print(type(actualErrandUserList))
                # 
                return Response({
                        "status": status.HTTP_200_OK,
                        "id": id,
                    })
            

    # 

@swagger_auto_schema(
    method='get',
        # request_body= UpdateErrandUserAssignmentSerializer,
        tags=['customerApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def SaveShopperSelectionModel(request):
    if ErrandUserAssignTrackingModel.objects.first():
        response = UpdateShopperSelectionModel()
        return response
            
    else:
        response = UpdateShopperSelectionModel()
        return response
                
                

def SaveErrandModelProper():
    print('SaveErrandModelProper CALLED')
    newErrandList = []
    newErrandList.append(1)

    print('newErrandList')
    print(newErrandList)
    saveForm = ErrandUserAssignTrackingModel(assignederranderIDList = str(newErrandList))
    saveForm.save()
    
    # Check if saved by querying
    if ErrandUserAssignTrackingModel.objects.filter(pk=saveForm.pk).exists():
        return 'success'
    else:
        return 'error'
    


@swagger_auto_schema(
    method='post',
        request_body= PurchaseDataSerializer,
        tags=['customerApp'],
    )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def BilasDataPurchase(request):
    serializer = PurchaseDataSerializer(data = request.data)
    if serializer.is_valid():
        planID = serializer.data['planID']
        phoneNumber = serializer.data['phoneNumber']
        networkID = serializer.data['networkID']
        cost = serializer.data['cost']
        print("serializer.data['phoneNumber']")
        print(serializer.data['phoneNumber'])
        print(serializer.data['cost'])
        
        if DataPlans.objects.filter(id = planID).exists():
            tokeGen = getBilasToken(request)
            if tokeGen.status_code == 200:
                data = tokeGen.data 
                token = data.get("token")
                username = request.user.email.split('@')[0]
                timestamp = int(timezone.now().timestamp())
                dataRequestID = f'${username}-${timestamp}'
                
                # check account balance is enough for transaction
                checkAccountStatus = confirmBalanceIsEnough(request, cost)
                if checkAccountStatus == 'Success':
                    pass
                else:
                    return Response({
                            "status": status.HTTP_400_BAD_REQUEST,
                            'message': 'Insufficient account balance to manage this transaction'
                        })
                    
                PurchaseDataRes = PurchaseData(token, networkID, planID, dataRequestID, phoneNumber)
                if PurchaseDataRes.data["status"] == 400:
                    # error occured
                    return Response({
                            "status": status.HTTP_400_BAD_REQUEST,
                            'message': PurchaseDataRes.data["api_response"]["message"]
                        })
                    
                elif PurchaseDataRes.data["status"] == 200:
                    # charge user for transaction here
                    decreaseAccountBalance(request, cost)
                    
                    recordDataSub = DataSubscriptionDeliveries(user = request.user, dataPlanSelected = planID, phone = phoneNumber, dataDisbursmentStatus = 'Success')
                    recordDataSub.save()
                    
                    # save notification
                    NotificationActivity.objects.create(user = request.user, transactionEffect = 'Subtract', activityTtile = 'Data', deliveryStatus = 'Successfull', amountSpent = cost)
                    
                    # 
                    return Response({
                            "status": status.HTTP_200_OK,
                            'message': PurchaseDataRes.data["api_response"]["message"]
                        })
                    
                else:
                    return Response({
                            "status": status.HTTP_400_BAD_REQUEST,
                            'message': PurchaseDataRes.data["api_response"]["message"]
                        })

                # return PurchaseDataRes
            
            else:
                return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        'message': 'An error occured'
                    })
            
        else:
            return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    'message': 'Your data plan selection was incorrect.'
                })
     
    else:
        return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                'message': 'The details you submittion was incorrect.'
            })



@swagger_auto_schema(
    method='get',
    query_serializer=FetchAllAvailableDataPlans,
    tags=['customerApp'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchAvailableDataPlans(request):
    print('request.query_params')
    print(request.query_params)
    serializer = FetchAllAvailableDataPlans(data=request.query_params)
    if serializer.is_valid():
        networkID = serializer.validated_data['networkID']
        availablePlans = []

        if DataPlans.objects.filter(network__networkID=networkID).exists():
            getdataplans = DataPlans.objects.filter(network__networkID=networkID)
            for plan in getdataplans:
                planOptions = {
                    'planName': plan.productName,
                    'planID': plan.planID,
                    'planType': plan.dataPlanType,
                    'planCost': plan.dataCost,
                    'planValidity': plan.dataValidity,
                }
                availablePlans.append(planOptions)

            return Response({
                "status": status.HTTP_200_OK,
                'data': availablePlans,
                'dataPlanCount': len(availablePlans),
                'message': 'Data plans fetched successfully'
            })
        else:
            return Response({
                "status": status.HTTP_200_OK,
                'data': [],
                'dataPlanCount': 0,
                'message': 'No data plan available for now'
            })
    else:
        return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                'message': 'An error occured with the data you submitted'
            })




def FetchOrdersForTracking(request):
    userOrders = ShoppingListModel.objects.filter(user = request.user)
    

def formatWords(text: str) -> str:
    # Remove leading/trailing spaces and split into words
    words = text.strip().split()
    
    # Capitalize each word properly
    formatted_words = [word.capitalize() for word in words]
    
    # Join back into a single string
    return " ".join(formatted_words)



@swagger_auto_schema(
    method='POST',
        request_body= AvailableUserDeliveryLocationSerializer,
    tags=['customerApp'],
)
@api_view(['POST'])
def UserDeliveryLocation(request):
    serializer = AvailableUserDeliveryLocationSerializer(data = request.data)
    if serializer.is_valid():
        stateForm = serializer.data['state'] 
        cityForm = serializer.data['city'] 
        lgaForm = serializer.data['lga'] 
        streetForm = serializer.data['street'] 
        houseNumber = serializer.data['houseNumber'] 
        
        state = formatWords(stateForm)
        city = formatWords(cityForm)
        lga = formatWords(lgaForm)
        street = formatWords(streetForm)
        
        if not serializer.data['state']:
            return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Kindly enter the state where you're located",
                })
    
        
        if not serializer.data['city']:
            return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Kindly enter the city where you're located",
                })
    
        
        if not serializer.data['houseNumber']:
            return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Kindly enter the number of your residence, for easy delivery of you order",
                })
        if AvailableUserDeliveryLocation.objects.filter(user=request.user, houseNumber=serializer.data['houseNumber'],
            street=serializer.data['street'], city=serializer.data['city']).exists():
            print("True")
        else:
            print("False")
            
            
        all_matched = AvailableUserDeliveryLocation.objects.filter(user=request.user, houseNumber= houseNumber, street= street,
            city=city).exists()
        
        address ={
            'state': state,
            'city': city,
            'lga': lga,
            'street': street,
            'houseNumber': houseNumber
        }
        
        if all_matched:
            return Response({
                    "status": status.HTTP_200_OK,
                    "location": address,
                    'message': 'This address already exists.'
                })
            
        saveLocation = AvailableUserDeliveryLocation(user = request.user, lga = lga, state = state, city = city, street = street, houseNumber = houseNumber)
        saveLocation.save()
        
        address ={
            'state': state,
            'city': city,
            'lga': lga,
            'street': street,
            'houseNumber': houseNumber
        }
        
        return Response({
                "status": status.HTTP_200_OK,
                "location": address,
                'message': 'Location saved successfully'
            })
        
    else:
        return Response({
                "status": status.HTTP_200_OK,
                'message': 'An error occured saving your location, kindly try again.'
            })



@swagger_auto_schema(
    method='GET',
    query_serializer=GetUserAddressSerializer,
    tags=['customerApp'],
)
@api_view(['GET'])
def FetchUserAddresses(request):
    print('request.query_params')
    print(request.query_params)
    allAddress = []
    if AvailableUserDeliveryLocation.objects.filter(user = request.user).exists():
        serializer = GetUserAddressSerializer(data=request.query_params)
        if serializer.is_valid():
            count = serializer.validated_data['count']
            print('count')
            print(count)
            print('count')
            if count == 'one':
                userLatestSavedLocation = AvailableUserDeliveryLocation.objects.filter(user = request.user).first()
                state = userLatestSavedLocation.state
                city = userLatestSavedLocation.city
                lga = userLatestSavedLocation.lga
                street = userLatestSavedLocation.street
                houseNumber = userLatestSavedLocation.houseNumber
                
                address = {
                    'state': state,
                    'city': city,
                    'lga': lga,
                    'street': street,
                    'houseNumber': houseNumber
                }
                return Response({
                        "status": status.HTTP_200_OK,
                        "location": address,
                        'dataLength': 1,
                        'message': 'Location found '
                    })
            else: 
                allUserLatestSavedLocation = AvailableUserDeliveryLocation.objects.filter(user = request.user)
                for location in allUserLatestSavedLocation:
                    state = location.state
                    city = location.city
                    lga = location.lga,
                    street = location.street
                    houseNumber = location.houseNumber
                    
                    address ={
                        'state': state,
                        'city': city,
                        'lga': lga,
                        'street': street,
                        'houseNumber': houseNumber
                    }

                    allAddress.append(address)
                
                return Response({
                        "status": status.HTTP_200_OK,
                        "location": allAddress,
                        'dataLength': len(allAddress),
                        'message': 'Location found'
                    })
                
                
        else:
            return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    'message': 'There an error getting your location, kindly refresh to try again.'
                    })
                    
    else:
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            'dataLength': 0,
            'message': 'You have not saved any address yet'
            })


@swagger_auto_schema(
    method='get',
        tags=['customerApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchOrderLists(request):
    print('FetchShoppingLists CALLED')
    customerShopper = request.user
    print(customerShopper)
    orderPlaced = []
    fetchAllUserOrders = OrderStatusTracking.objects.filter(user = customerShopper)
    for order in fetchAllUserOrders:
        pickUpState = order.pickUpState
        pickUpCountry = order.pickUpCountry
        deliveryState = order.deliveryState
        deliveryCountry = order.deliveryCountry
        shoppingListID = order.shoppingListID
        # 
        # 
        deliveryTakeOffDate = f"{order.deliveryTakeOffTime}"
        actualPackageDeliveryDateTime =f"{ order.actualPackageDeliveryDateTime}"
        expectedDeliveryDate = f"{order.expectedDeliveryDate}"
        dateOrderWasPlaced = f"{order.created_at}"
        
        
        # --- deliveryTakeOffDate ---
        if deliveryTakeOffDate:
            try:
                readableDeliveryTakeOffTime = datetime.fromisoformat(str(deliveryTakeOffDate))
                readableDeliveryTakeOffTimeMain = readableDeliveryTakeOffTime.strftime("%H:%M")
                readableDeliveryTakeOffDateMain = readableDeliveryTakeOffTime.strftime("%d/%m/%Y")
            except ValueError:
                readableDeliveryTakeOffTimeMain = None
                readableDeliveryTakeOffDateMain = None
        else:
            readableDeliveryTakeOffTimeMain = None
            readableDeliveryTakeOffDateMain = None


        # --- actualPackageDeliveryDateTime ---
        if actualPackageDeliveryDateTime:
            try:
                readableactualPackageDeliveryDateMain = datetime.fromisoformat(str(actualPackageDeliveryDateTime))
                readableactualPackageDeliveryTime = readableactualPackageDeliveryDateMain.strftime("%H:%M")
                readableactualPackageDeliveryDate = readableactualPackageDeliveryDateMain.strftime("%d/%m/%Y")
            except ValueError:
                readableactualPackageDeliveryTime = None
                readableactualPackageDeliveryDate = None
        else:
            readableactualPackageDeliveryTime = None
            readableactualPackageDeliveryDate = None


            # --- expectedDeliveryDate ---
        if expectedDeliveryDate:
            try:
                readableexpectedDeliveryDateMain = datetime.fromisoformat(str(expectedDeliveryDate))
                readableexpectedDeliveryTime = readableexpectedDeliveryDateMain.strftime("%H:%M")
                readableexpectedDeliveryDate = readableexpectedDeliveryDateMain.strftime("%d/%m/%Y")
            except ValueError:
                readableexpectedDeliveryTime = None
                readableexpectedDeliveryDate = None
        else:
            readableexpectedDeliveryTime = None
            readableexpectedDeliveryDate = None


        # --- dateOrderWasPlaced ---
        if dateOrderWasPlaced:
            try:
                readabledateOrderWasPlacedDateMain = datetime.fromisoformat(str(dateOrderWasPlaced))
                readabledateOrderWasPlacedDateDate = readabledateOrderWasPlacedDateMain.strftime("%d/%m/%Y")
                readabledateOrderWasPlacedDateTime = readabledateOrderWasPlacedDateMain.strftime("%H:%M")
            except ValueError:
                readabledateOrderWasPlacedDateDate = None
                readabledateOrderWasPlacedDateTime = None
        else:
            readabledateOrderWasPlacedDateDate = None
            readabledateOrderWasPlacedDateTime = None
        
        
        data = {
            'pickUpState': pickUpState,
            'pickUpCountry': pickUpCountry,
            'deliveryState': deliveryState,
            'deliveryCountry': deliveryCountry,
            'shoppingListID': shoppingListID,
            'deliveryTakeOffTime': readableDeliveryTakeOffTimeMain,
            'deliveryTakeOffDay': readableDeliveryTakeOffDateMain,
            'actualPackageDeliveryTime': readableactualPackageDeliveryTime,
            'actualPackageDeliveryDate': readableactualPackageDeliveryDate,
            'expectedDeliveryDate': readableexpectedDeliveryDate,
            'expectedDeliveryTime': readableexpectedDeliveryTime,
            'dateOrderWasPlacedDate': readabledateOrderWasPlacedDateDate,
            'dateOrderWasPlacedTime': readabledateOrderWasPlacedDateTime,
        }
            
        orderPlaced.append(data)

    return Response({
        "status": status.HTTP_400_BAD_REQUEST,
        'data': orderPlaced,
        'dataCount': len(orderPlaced),
        'message': 'Orders fetched successfully'
        })




@swagger_auto_schema(
    method='get',
    query_serializer=FetchOrderDetailsSerilizer,
        tags=['customerApp'],
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchAnOrderList(request):
    print('FetchAnOrderList CALLED')
    print(request.query_params)
    serializer = FetchOrderDetailsSerilizer(data=request.query_params)
    if serializer.is_valid():
        orderList = []
        orderid = serializer.validated_data['orderid']
        print('orderid')
        print(orderid)
        allOrders = ShoppingListModel.objects.filter(shoppingListID = orderid)
        for order in allOrders:
            
            
            if order.product.productImage:
                image = image = request.build_absolute_uri(order.product.productImage.url)
            else:
                image = ''
            
            errandIUserName = order.errandUser.fullname
            productName= order.product.productName
            productImage= image
            productPrice= order.productPriceAtPurchase
            productAmount= order.numberofitems
            productDeliveryStatus= order.deliveryStatus
            dateCreated= order.created_at
        
            data = {
                "errandIUserName" : errandIUserName,
                "productName" : productName,
                "productImage" : productImage,
                "productPrice" : productPrice,
                "productAmount" : productAmount,
                "productDeliveryStatus" : productDeliveryStatus,
                "dateCreated" : dateCreated,
            }
            
            orderList.append(data)
                    
        return Response({
                "status": status.HTTP_200_OK,
                "data": orderList,
                'dataLength': len(orderList),
                'message': 'Orders found'
            })
                
                
    else:
        return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                'message': 'An error occured, kindly refresh to try again.'
                })



def FetchHistoryNotificaions(request):
    if NotificationActivity.objects.filter(user = request).exists():
        getHistory = NotificationActivity.objects.filter(user = request.user)

