from django.urls import path
from customeruserapp import paystackViews
from customeruserapp.utils import electricity
from customeruserapp.utils.airtime import airtimepurchasefxn
from customeruserapp.utils.cabletvalgo import cableviews
from customeruserapp.utils.datasub import datapurchaseviews
from . import views

urlpatterns = [
    path('categoryitems', views.CategoryItems, name="CategoryItems"),
    path('getproductcategories', views.GetProductCategories, name="GetProductCategories"),
    path('getproducts', views.FetchProducts, name="FetchProducts"),
    path('updatelistprices', views.UpdateListPrices, name="UpdateListPrices"),
    path('saveshoppinglist', views.SaveShoppinglist, name="SaveShoppinglist"),
    path('updatenewshoppermodel', views.SaveShopperSelectionModel, name="SaveShopperSelectionModel"),
    # path('allordersfortracking', views.FetchOrdersForTracking, name="FetchOrdersForTracking"),
    path('userdeliverylocations', views.UserDeliveryLocation, name="UserDeliveryLocation"),
    path('fetchaddress', views.FetchUserAddresses, name="FetchUserAddresses"),
    path('getorders', views.FetchOrderLists, name="FetchOrderLists"),
    path('fetchorderlist', views.FetchAnOrderList, name="FetchAnOrderList"),
    path('fetchhistory', views.FetchHistoryNotificaions, name="FetchHistoryNotificaions"),
    
    # DATA PURCHASE
    path('getdataplans', views.FetchAvailableDataPlans, name="FetchAvailableDataPlans"),
    path('bilasDatapurchase', views.BilasDataPurchase, name="BilasDataPurchase"),
    
    # Airtime purchase url here
    path('vtutopup', airtimepurchasefxn.AirtimeVTUTopUpurchase, name="AirtimeVTUTopUpurchase"),
    
    # Verify meter number
    path('verifymeter', electricity.VerifyUserMeterNumber, name="VerifyUserMeterNumber"),
    path('getdistributors', electricity.AvailableElectricityDistributors, name="AvailableElectricityDistributors"),
    path('payelectricitybill', electricity.PayElectricityBill, name="PayElectricityBill"),
    
    # purchase cable urls
    path('getdstvplans', cableviews.GetAvailableTVPlans, name="GetAvailableTVPlans"),
    path('verifysmartcard', cableviews.VerifyCableSmartNumber, name="VerifyCableSmartNumber"),
    path('subscribecabletv', cableviews.RenewCableTVService, name="RenewCableTVService"),
    
    # paystack deposte
    path('initpaystackpayment', paystackViews.UserFundAccount, name="UserFundAccount"),
    path('verifydeposit/<str:accesscode>', paystackViews.VerifyUserFundsDeposit, name="VerifyUserFundsDeposit"),
    path('fetchaccountbalance', paystackViews.FetchUserAccountBalance, name="FetchUserAccountBalance"),
    
    

]


