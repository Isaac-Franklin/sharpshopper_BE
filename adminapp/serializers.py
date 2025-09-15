from rest_framework import serializers
from customeruserapp.models import *


class ShopperUserSerializer(serializers.ModelSerializer):
    # Custom fields
    accountBalance = serializers.SerializerMethodField()
    totalTransactions = serializers.SerializerMethodField()
    lastActivity = serializers.SerializerMethodField()

    class Meta:
        model = ShopperUsers
        fields = [
            "id",
            "fullname",
            "emailAddress",
            "phoneNumber",
            "created_at",
            "accountBalance",
            "totalTransactions",
            "lastActivity",
        ]

    def get_accountBalance(self, obj):
        balance_obj = UserAccountBalanceTracker.objects.filter(user=obj.user).last()
        return balance_obj.AccountBalance if balance_obj else 0

    def get_totalTransactions(self, obj):
        return NotificationActivity.objects.filter(user=obj.user).count()

    def get_lastActivity(self, obj):
        last_activity = NotificationActivity.objects.filter(user=obj.user).order_by("-created_at").first()
        from django.utils.timesince import timesince
        from django.utils.timezone import now
        return timesince(last_activity.created_at, now()) + " ago" if last_activity else "N/A"


class ErrandUserSerializer(serializers.ModelSerializer):
    # Custom fields
    ordersAssigned = serializers.SerializerMethodField()
    ordersDelivered = serializers.SerializerMethodField()
    successRate = serializers.SerializerMethodField()
    lastActivity = serializers.SerializerMethodField()

    class Meta:
        model = ErrandUsers
        fields = [
            "id",
            "fullname",
            "emailAddress",
            "phonenumber",
            "created_at",
            "ordersAssigned",
            "ordersDelivered",
            "successRate",
            "lastActivity",
        ]

    def get_ordersAssigned(self, obj):
        return OrderStatusTracking.objects.filter(errandUser=obj).count()

    def get_ordersDelivered(self, obj):
        return OrderStatusTracking.objects.filter(errandUser=obj, deliveryStatus="delivered").count()

    def get_successRate(self, obj):
        total = self.get_ordersAssigned(obj)
        delivered = self.get_ordersDelivered(obj)
        return round((delivered / total) * 100, 1) if total > 0 else 0

    def get_lastActivity(self, obj):
        last_order = OrderStatusTracking.objects.filter(errandUser=obj).order_by("-created_at").first()
        from django.utils.timesince import timesince
        from django.utils.timezone import now
        return timesince(last_order.created_at, now()) + " ago" if last_order else "N/A"
    
    
    
class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    description = serializers.CharField(source='activityTtile')
    status = serializers.CharField(source='deliveryStatus')
    date = serializers.DateTimeField(source='created_at')
    paymentMethod = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()

    class Meta:
        model = NotificationActivity
        fields = [
            'id',
            'user',
            'type',
            'amount',
            'description',
            'status',
            'date',
            'paymentMethod',
            'reference',
        ]

    def get_id(self, obj):
        # Format ID like TXN01, TXN02, etc.
        return f"TXN{obj.id:02d}"

    def get_user(self, obj):
        shopper = ShopperUsers.objects.filter(user=obj.user).first()
        if shopper:
            return shopper.fullname or obj.user.username
        errand = ErrandUsers.objects.filter(user=obj.user).first()
        if errand:
            return errand.fullname or obj.user.username
        return obj.user.username

    def get_type(self, obj):
        return "credit" if obj.transactionEffect == "Add" else "debit"

    def get_amount(self, obj):
        try:
            return float(obj.amountSpent)
        except:
            return 0.0

    def get_paymentMethod(self, obj):
        return "Wallet"

    def get_reference(self, obj):
        return f"REF{obj.id:06d}"
    
    
    
    
class DataPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPlans
        fields = "__all__"