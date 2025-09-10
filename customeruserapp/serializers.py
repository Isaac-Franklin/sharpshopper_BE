from enum import Enum
from typing import OrderedDict
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers
from customeruserapp.models import ProductCategories


class FetchProductCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategories
        fields = ['categoryName', 'categoryImage']



class UpdateErrandUserAssignmentSerializer(serializers.Serializer):
    errandUserID = serializers.IntegerField()



class FetchAllAvailableDataPlans(serializers.Serializer):
    networkID = serializers.IntegerField()

class FetchOrderDetailsSerilizer(serializers.Serializer):
    orderid = serializers.CharField()


class GetUserAddressSerializer(serializers.Serializer):
    count = serializers.CharField()


class TVStationServiceProviderID(serializers.Serializer):
    stationProvider = serializers.CharField()


class VerifySmartCarderializer(serializers.Serializer):
    smartCardNumber = serializers.CharField()
    cabletvProvider = serializers.CharField()


class RenewCableTVServiceSerializer(serializers.Serializer):
    smartCardNumber = serializers.CharField()
    cabletvProvider = serializers.CharField()
    amount = serializers.CharField()



class PurchaseDataSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    planID = serializers.IntegerField()
    cost = serializers.CharField()
    networkID = serializers.IntegerField()



class PurchaseMTNVTUSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    amount = serializers.IntegerField()


class PurchaseAIRTELVTUSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    amount = serializers.IntegerField()


class PurchaseGLOVTUSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    amount = serializers.IntegerField()



class AirtimeVTUTopUpSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    amount = serializers.IntegerField()
    network = serializers.CharField()



class VerifyMeterSerializer(serializers.Serializer):
    billersCode = serializers.CharField()
    serviceID = serializers.CharField()
    type = serializers.CharField()



class PayMeterBillSerializer(serializers.Serializer):
    powerSupplierID = serializers.CharField()
    meterNumber = serializers.CharField()
    meterType = serializers.CharField()
    amount = serializers.CharField()
    phone = serializers.CharField()






class UserDepositSerializer(serializers.Serializer):
    amount = serializers.CharField()
    


class AvailableUserDeliveryLocationSerializer(serializers.Serializer):
    state = serializers.CharField()
    city = serializers.CharField()
    lga = serializers.CharField()
    street = serializers.CharField()
    houseNumber = serializers.CharField()
    



class CustomerShoppingListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.productName', read_only=True)
    requester_name = serializers.CharField(source='itemRequester.fullname', read_only=True)
    requester_image = serializers.CharField(source='itemRequester.profileImage', read_only=True)


    class Meta:
        model = ShoppingListModel
        fields = [
            'id',
            # 'shoppingListID',
            'product_name',
            'requester_name',
            'requester_image',
            'deliveryLocation',
            'productPriceAtPurchase',
            'numberofitems',
            'deliveryStatus',
            'created_at',
            'edited_at'
        ]
        