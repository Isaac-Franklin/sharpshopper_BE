from django.urls import path

from customeruserapp.utils.datasub import datapurchaseviews
from . import views

urlpatterns = [
    path('createdataplan', views.CreateDataPlan, name="CreateDataNetwork"),
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


    # path('fetchshoppingitems', views.FetchShoppingItems, name="FetchShoppingItems"),
    
    
]

