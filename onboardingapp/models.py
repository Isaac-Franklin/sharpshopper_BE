from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User



class ShopperUsers(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    fullname = models.CharField(max_length= 300, null=True, blank = True)
    emailAddress = models.EmailField(max_length= 300, null=True, blank = True)
    phoneNumber = models.CharField(max_length= 300, null=True, blank = True)
    referalCode = models.CharField(max_length= 300, null=True, blank = True)
    referrerCode = models.CharField(max_length= 300, null=True, blank = True)
    profileImage = models.ImageField(upload_to='customerUserProfileImages/', blank=True, null=True)
    password = models.CharField(max_length= 300, null=True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.user.username






class ErrandUsers(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    fullname = models.CharField(max_length= 300, null=True, blank = True)
    emailAddress = models.EmailField(max_length= 300, null=True, blank = True)
    phonenumber = models.CharField(max_length= 300, null=True, blank = True)
    password = models.CharField(max_length= 300, null=True, blank = True)
    profileImage = models.ImageField(upload_to='errandUserProfileImages/', blank=True, null=True)

    # referalCode = models.CharField(max_length= 300, null=True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edited_at', '-created_at']
        
    def __str__(self):
        return self.user.username



