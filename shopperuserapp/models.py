import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from adminapp.models import DataPlans
from onboardingapp.models import ErrandUsers, ShopperUsers



class ErrandUserAccountBalanceTracker(models.Model):
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
        

