from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Email verification endpoints
    path('verify-email/', views.verify_email_otp, name='verify_email_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('user-info/', views.user_info_view, name='user_info'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Admin endpoints
    path('users/', views.role_based_users_view, name='role_based_users'),
]