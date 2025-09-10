from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(ProductCategories)
admin.site.register(ShoppingListModel)
admin.site.register(Products)
admin.site.register(ErrandUserAssignTrackingModel)
admin.site.register(DataSubscriptionDeliveries)
admin.site.register(RegisterAirtimePurchases)
admin.site.register(UserMeterRecordsModel)
admin.site.register(ElectricityPurchaseRecordsModel)
admin.site.register(SaveCableTVPurchases)
admin.site.register(PotentialDeposites)
admin.site.register(SuccessfullDeposites)
admin.site.register(UserAccountBalanceTracker)
admin.site.register(AvailableUserDeliveryLocation)
admin.site.register(OrderStatusTracking)
admin.site.register(NotificationActivity)

