from django.urls import path
from . import views

urlpatterns = [
    path('userlogin', views.UserLogin, name="UserLogin"),
    path('userreg', views.UserRegistration, name="UserRegistration"),
    path('errandreg', views.ErrandUserRegistration, name="ErrandUserRegistration"),
]


