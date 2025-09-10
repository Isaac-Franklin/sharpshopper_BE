from django.urls import path

from customeruserapp.utils.datasub import datapurchaseviews
from . import views

urlpatterns = [
    path('createdataplan', views.CreateDataPlan, name="CreateDataNetwork"),
    path('login', views.AdminLogin, name="AdminLogin"),
    # path('fetchshoppingitems', views.FetchShoppingItems, name="FetchShoppingItems"),
    
    

]


