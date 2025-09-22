from django.urls import path

from customeruserapp.utils.datasub import datapurchaseviews
from . import views

urlpatterns = [
    # path('createdataplan', views.CreateDataPlan, name="CreateDataNetwork"),
    path('login', views.AdminLogin, name="AdminLogin"),
    path('dashboardstats', views.DashboardStats, name="DashboardStats"),
    path("dashboard/analytics/", views.dashboard_analytics, name="dashboard_analytics"),
    path("dashboard/activity/", views.get_recent_activity, name="get_recent_activity"),
    # path("/members", views.GetAllUsers, name="GetAllUsers"),
    path("errandmembers", views.get_errand_users, name="get_errand_users"),
    path("members", views.fetchAllAppUsers, name="fetchAllAppUsers"),
    path("getmember/<int:id>/", views.get_member, name="get_member"),
    path("createmember/", views.create_member, name="create_member"),
    path("updatemember/<int:id>/", views.update_member, name="update_member"),
    path("deletemember/<int:id>/", views.delete_member, name="delete_member"),
    path("members/stats/", views.get_member_stats, name="get_member_stats"),
    path('transactions/', views.get_all_transactions, name='transactions'),
    path("transactions/stats/", views.get_transaction_stats, name="get_transaction_stats"),
    path("orders/", views.GetOrderForAgentAdnOrderPage, name="GetOrderForAgentAdnOrderPage"),
    path("agents/", views.GetAllAgentsForAgentAndOrderPage, name="GetAllAgentsForAgentAndOrderPage"),
    path("fetchutilities/", views.FetchUtilityPurchases, name="FetchUtilityPurchases"),
    path("utilities/stats/", views.get_utility_stats_main, name="get_utility_stats_main"),
    # 
    path("utilitiesdataplans/", views.get_data_plans, name="get_data_plans"),
    path("updatedataplans/<int:id>/", views.update_data_plan, name="update_data_plan"),
    path("deletedataplans/<int:id>/", views.delete_data_plan, name="delete_data_plan"),
    path("createagents/", views.RegisterAgent, name="RegisterAgent"),
    path('savefcmtoken', views.SaveUserFCMToken, name="SaveUserFCMToken"),
    # path("editagents/", views.EditAgentProfile, name="EditAgentProfile"),
    
    # category and products
    path("getcategories/", views.FetchCategories, name="FetchCategories"),
    path("getproducts/", views.FetchProducts, name="FetchProducts"),
    path("editproduct/<int:id>/", views.editProductDetails, name="editProductDetails"),
    path("createcategory/", views.CreateCategory, name="CreateCategory"),
    path("createproduct/", views.CreateProduct, name="CreateProduct"),
    



    # path('fetchshoppingitems', views.FetchShoppingItems, name="FetchShoppingItems"),
    
    
]

