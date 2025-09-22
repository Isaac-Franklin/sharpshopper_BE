import json
from django.db import models
from django.contrib.auth.models import User
from onboardingapp.models import ErrandUsers, ShopperUsers



NETWORK_PLANS = (
    ("mtn", "MTN"),
    ("glo", "GLO"),
    ("airtel", "AIRTEL"),
    ("9mobile", "9MOBILE"),
)


DATA_PLAN_TYPE = (
    ("cooporate_gifting", "Cooporate gifting"),
    ("sme", "SME"),
    ("gifting", "Gifting"),
    ("gifting_promo", "Gifting promo"),
)


DATA_DURATION = (
    ("monthly", "Monthly"),
    ("weekly", "Weekly"),
    ("daily", "Daily"),
    ("two_days", "Two Days"),
)

class NetworkID(models.Model):
    network = models.CharField(max_length= 300,choices = NETWORK_PLANS, default = 'MTN')
    networkID = models.CharField(max_length= 10)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return f'Network: {self.network}. ID: {self.networkID}'


class DataPlans(models.Model):
    network = models.ForeignKey(NetworkID, null=True, on_delete=models.CASCADE)
    productName = models.CharField(max_length= 300, null=True, blank = True)
    planID = models.IntegerField()
    dataPlanType = models.CharField(max_length= 300,choices = DATA_PLAN_TYPE, default = 'SME')
    dataCost = models.CharField(max_length= 300, null=True, blank = True)
    dataValidity = models.CharField(max_length= 300,choices = DATA_DURATION, default = 'monthly')
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return f'network:{self.network}. product name: {self.productName}. Data plan:{self.dataPlanType}. Validity: {self.dataValidity}. Cost: {self.dataCost} PlanID: {self.planID}'



class ElectricityProviders(models.Model):
    apiaccessname = models.CharField(max_length= 300, null=True, blank = True)
    FullName = models.CharField(max_length= 300, null=True, blank = True)
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return f'apiaccessname:{self.apiaccessname}. apiaccessname: {self.apiaccessname}'



class UsersFCMTokenModel(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    userEmail = models.EmailField(null=True, blank = True)
    FCMToken = models.CharField(max_length= 50000, null=True, blank = True)
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return f'userEmail:{self.userEmail}. FCMToken: {self.FCMToken}'


