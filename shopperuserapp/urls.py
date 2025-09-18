from django.urls import path

from customeruserapp.utils.datasub import datapurchaseviews
from . import views

urlpatterns = [
    path('fetchshoppinglists', views.FetchShoppingLists, name="FetchShoppingLists"),
    path('fetchshoppingitems', views.FetchShoppingItems, name="FetchShoppingItems"),
    path('errandaccountbalance', views.ErrandUserAccountBalance, name="ErrandUserAccountBalance"),
    path('markaasdelivered', views.MarkShoppingListAsDelivered, name="MarkShoppingListAsDelivered"),
    
    

]


