import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from adminapp.models import DataPlans
from onboardingapp.models import ErrandUsers, ShopperUsers



PRODUCT_AVAILABILITY_STATUS = (
    ("In Stock", "In Stock"),
    ("Best Seller", "Best Seller"),
    ("Low Stock", "Low Stock"),
    ("Back Soon", "Back Soon"),
)

TRANSACTION_EFFECT = (
    ("Add", "Add"),
    ("Subtract", "Subtract"),
)


Airtime_Network = (
    ("mtn", "MTN"),
    ("airtel", "AIRTEL"),
    ("glo", "GLO"),
    ("9mobile", "9MOBILE"),
)


ITEM_DELIVERY_STATUS = (
    ("in_store", "In Store"),
    ("enroute", "Enroute"),
    ("delivered", "Delivered"),
    ("failed_delivery", "Failed Delivery"),
)


DATA_SUSBCRIPTION_STATUS = (
    ("success", "Success"),
    ("pending", "Pending"),
    ("delivered", "Delivered"),
    ("failed", "Failed"),
)
class ProductCategories(models.Model):
    categoryName = models.CharField(max_length= 300, null=True, blank = True)
    categoryImage = models.ImageField(upload_to='categoryimages/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.categoryName


class Products(models.Model):
    productCategory = models.ForeignKey(ProductCategories, null=True, on_delete=models.CASCADE)
    productName = models.CharField(max_length= 300, null=True, blank = True)
    productPrice = models.CharField(max_length= 300, null=True, blank = True)
    productAvailability= models.CharField(max_length= 300,choices = PRODUCT_AVAILABILITY_STATUS, default = 'In Stock')
    productImage = models.ImageField(upload_to='productimages/', blank=True, null=True )
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.productName



class ShoppingListModel(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    itemRequester = models.ForeignKey(ShopperUsers, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, null=True, on_delete=models.CASCADE)
    numberofitems = models.IntegerField(default = 1)
    errandUser = models.ForeignKey(ErrandUsers, null=True, on_delete=models.SET_NULL)
    shoppingListID = models.CharField(max_length= 300, null=True, blank = True)
    deliveryStatus= models.CharField(max_length= 300,choices = ITEM_DELIVERY_STATUS, default = 'in_store')
    deliveryLocation= models.CharField(max_length= 3000, null=True, blank = True)
    assignedErrandPersonID = models.IntegerField(null=True, blank = True)
    productPriceAtPurchase = models.CharField(max_length= 300, null=True, blank = True)
    
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.shoppingListID
    
    
    
class OrderStatusTracking(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    errandUser = models.ForeignKey(ErrandUsers, null=True, on_delete=models.SET_NULL)
    pickUpState = models.CharField(max_length= 300, null=True, blank = True)
    pickUpCountry = models.CharField(max_length= 300, null=True, blank = True)
    deliveryState = models.CharField(max_length= 300, null=True, blank = True)
    deliveryCountry = models.CharField(max_length= 300, null=True, blank = True)
    shoppingListID = models.CharField(max_length= 300, null=True, blank = True)
    
    # 
    deliveryTakeOffTime = models.DateTimeField(null=True, blank = True)
    actualPackageDeliveryDateTime = models.DateTimeField(null=True, blank = True)
    expectedDeliveryDate = models.CharField(null=True, blank = True)
    expectedDeliveryTime = models.CharField(null=True, blank = True)
    
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.shoppingListID



class ErrandUserAssignTrackingModel(models.Model):
    assignederranderIDList = models.CharField(max_length= 700, null=True, blank = True)
    
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']



class DataSubscriptionDeliveries(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    dataPlanSelected = models.ForeignKey(DataPlans, null=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length= 700, null=True, blank = True)
    dataDisbursmentStatus = models.CharField(max_length= 300,choices = DATA_SUSBCRIPTION_STATUS, default = 'failed')
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.phone



class RegisterAirtimePurchases(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    numberToRecharge = models.CharField(max_length= 700, null=True, blank = True)
    customeRequestID = models.CharField(max_length= 700, null=True, blank = True)
    transactionID = models.CharField(max_length= 700, null=True, blank = True)
    transactionStatus = models.CharField(max_length= 700, null=True, blank = True)
    network = models.CharField(max_length= 300,choices = Airtime_Network)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.numberToRecharge
    


class UserMeterRecordsModel(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    billersCode_MeterNumber = models.CharField(max_length= 700, null=True, blank = True)
    serviceID = models.CharField(max_length= 700, null=True, blank = True)
    meterType = models.CharField(max_length= 700, null=True, blank = True)
    Customer_Name = models.CharField(max_length= 700, null=True, blank = True)
    Account_Number = models.CharField(max_length= 700, null=True, blank = True)
    Address = models.CharField(max_length= 700, null=True, blank = True)
    Minimum_Amount = models.CharField(max_length= 700, null=True, blank = True)
    Min_Purchase_Amount = models.CharField(max_length= 700, null=True, blank = True)
    Customer_Arrears = models.CharField(max_length= 700, null=True, blank = True)
    Customer_Account_Type = models.CharField(max_length= 700, null=True, blank = True)
    Can_Vend = models.CharField(max_length= 700, null=True, blank = True)
    Meter_Type = models.CharField(max_length= 700, null=True, blank = True)
    WrongBillersCode = models.CharField(max_length= 700, null=True, blank = True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.Customer_Name
    


class ElectricityPurchaseRecordsModel(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    MeterRecords = models.ForeignKey(UserMeterRecordsModel, null=True, on_delete=models.CASCADE)
    product_name = models.CharField(max_length= 3000, null=True, blank = True)
    
    
    transactionId = models.CharField(max_length= 700, null=True, blank = True)
    requestId = models.CharField(max_length= 700, null=True, blank = True)
    purchasedToken = models.CharField(max_length= 700, null=True, blank = True)
    tokenAmount = models.CharField(max_length= 700, null=True, blank = True)
    amount = models.CharField(max_length= 700, null=True, blank = True)
    purchasedUnits = models.CharField(max_length= 700, null=True, blank = True)
    announcement = models.CharField(max_length= 3000, null=True, blank = True)
    exchangeReference = models.CharField(max_length= 3000, null=True, blank = True)
    mainTokenTax = models.CharField(max_length= 3000, null=True, blank = True)
    meterType = models.CharField(max_length= 3000, null=True, blank = True)
    # 
    customerAddress = models.CharField(max_length= 3000, null=True, blank = True)
    utilityName = models.CharField(max_length= 3000, null=True, blank = True)
    customerName = models.CharField(max_length= 3000, null=True, blank = True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.transactionId
    


class SaveCableTVPurchases(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    smartcardTVorIUCNumber = models.CharField(max_length= 3000, null=True, blank = True)
    product_name = models.CharField(max_length= 3000, null=True, blank = True)
    
    
    customerName = models.CharField(max_length= 700, null=True, blank = True)
    requestId = models.CharField(max_length= 700, null=True, blank = True)
    amount = models.CharField(max_length= 700, null=True, blank = True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.customerName



class PotentialDeposites(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    amount = models.CharField(max_length= 300, null=True, blank = True)
    accesscode = models.CharField(max_length= 300, null=True, blank = True)
    reference = models.CharField(max_length= 300, null=True, blank = True)
    auth_url = models.CharField(max_length= 300, null=True, blank = True)
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return f'accesscode: {self.accesscode}, reference: {self.reference}'



class SuccessfullDeposites(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    accesscode = models.CharField(max_length= 300, null=True, blank = True)
    PotentialDeposites = models.ForeignKey(PotentialDeposites, null=True, on_delete=models.CASCADE)
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    # def __str__(self):
    #     return self.accesscode
        


class UserAccountBalanceTracker(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    emailAddress = models.EmailField(max_length= 300, null=True, blank = True)
    AccountBalance = models.IntegerField(default=0)
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return f'UserEmail{self.emailAddress}. Account Balance: ₦{self.AccountBalance}'
        




class AvailableUserDeliveryLocation(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    state = models.CharField(max_length= 500, null=True, blank = True)
    lga = models.CharField(max_length= 500, null=True, blank = True)
    city = models.CharField(max_length= 500, null=True, blank = True)
    street = models.CharField(max_length= 500, null=True, blank = True)
    houseNumber = models.CharField(max_length= 300, null=True, blank = True)
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return f'Address: {self.city}.'
        


def current_month():
    return str(timezone.now().month)

class NotificationActivity(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    activityTtile = models.CharField(max_length=500, null=True, blank=True)
    deliveryStatus = models.CharField(max_length=500, null=True, blank=True)
    amountSpent = models.CharField(max_length=500, null=True, blank=True)
    transactionEffect = models.CharField(choices=TRANSACTION_EFFECT, default='Add')
    month = models.CharField(
        max_length=2,
        default=current_month,
    )
    category = models.CharField(max_length=500, null=True, blank=True, default='all')
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return f'{self.activityTtile}.'