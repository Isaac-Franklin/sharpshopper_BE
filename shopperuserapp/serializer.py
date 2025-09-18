from rest_framework import serializers
from customeruserapp.models import ShoppingListModel

class ShoppingListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.productName', read_only=True)
    requester_name = serializers.CharField(source='itemRequester.fullname', read_only=True)
    requester_image = serializers.CharField(source='itemRequester.profileImage', read_only=True)


    class Meta:
        model = ShoppingListModel
        fields = [
            'id',
            'shoppingListID',
            'product_name',
            'requester_name',
            'requester_image',
            'productPriceAtPurchase',
            'numberofitems',
            'deliveryLocation',
            'deliveryStatus',
            'created_at',
            'edited_at'
        ]
        

class FetchShoppingListsSerializer(serializers.Serializer):
    filter = serializers.CharField()

class MarkAsDeliveredSerializer(serializers.Serializer):
    shoppingListID = serializers.CharField()

class UpdateShoppingListDeliveredSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingListModel
        fields = ['deliveryStatus',]