from django.urls import path
from .views import RegisterAPI, MyProfileAPI, AllProfileAPI
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('profile/me/', MyProfileAPI.as_view(), name='my_profile'),
    path('profile/all/', AllProfileAPI.as_view(), name='all_profiles'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
