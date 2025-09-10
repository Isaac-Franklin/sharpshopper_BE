from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg import openapi
from django.contrib.auth import views as auth_views
# from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view
from django.conf import settings
from django.conf.urls.static import static


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="SharpShopper API",
        default_version='v0.01',
        description="SharpShopper API Documentation",
        terms_of_service="https://sharpshopper.ng/",
        contact=openapi.Contact(email="isaacfrank197@gmail.com"),
        license=openapi.License(name="Awesome License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)


urlpatterns = [
    path('adminacesspath/', admin.site.urls),
    path('onboard/', include("onboardingapp.urls")),
    path('customeruser/', include("customeruserapp.urls")),
    path('errand/', include("shopperuserapp.urls")),
    path('admin/', include("adminapp.urls")),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # jwt endpoints
    path('api', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refreshtoken', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/verifytoken', TokenVerifyView.as_view(), name='token_verify'),
]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)